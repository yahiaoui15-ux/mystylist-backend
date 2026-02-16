# app/services/product_matcher_service.py
from typing import Dict, Any, List, Optional, Tuple
import re
import hashlib
import os
import unicodedata
from urllib.parse import urlparse

import httpx

from app.utils.supabase_client import supabase


class ProductMatcherService:
    """
    Match une pièce IA (piece_title/spec/visual_key) vers:
    1) un produit affilié (TABLE: affiliate_products)
       - récupère jusqu'à `limit` candidats
       - renvoie 1 produit principal + 2 alternatives
    2) sinon un visuel pédagogique (table `visuels`)
    + Cache images affiliées dans Supabase Storage (bucket public) pour compat PDFMonkey

    ✅ FIX v7 (stable + rapide):
    - Interroge DIRECTEMENT `affiliate_products` + filtre `is_deleted=false`
    - Requêtes PostgREST simples (1 seul ilike par call), filtrage catégorie côté Python
    - Catégories alignées avec tes valeurs FR/EN (Vêtements~~Robe / Clothing~~Dresses / Footwear~~Sneakers...)
    - Cache image NON BLOQUANT (timeouts courts + limite taille + cache mémoire request)
    """

    VISUELS_TYPE_MAP = {
        "tops": "haut",
        "bottoms": "bas",
        "dresses_playsuits": "robe",
        "outerwear": "haut",
        "swim_lingerie": "lingerie",
        "shoes": "chaussures",
        "accessories": "accessoire",
    }

    # Table source
    AFFILIATE_TABLE = os.getenv("AFFILIATE_TABLE", "affiliate_products")

    # Bucket public (doit être PUBLIC pour PDFMonkey)
    AFFILIATE_IMAGE_BUCKET = os.getenv("AFFILIATE_IMAGE_BUCKET", "affiliate-cache")

    # Timeouts (évite worker timeout)
    HTTP_CONNECT_TIMEOUT = float(os.getenv("PDT_HTTP_CONNECT_TIMEOUT", "3.0"))
    HTTP_READ_TIMEOUT = float(os.getenv("PDT_HTTP_READ_TIMEOUT", "6.0"))
    HTTP_TOTAL_TIMEOUT = float(os.getenv("PDT_HTTP_TOTAL_TIMEOUT", "8.0"))

    # Taille max d’image acceptée (en bytes) pour éviter de télécharger des monstres
    MAX_IMAGE_BYTES = int(os.getenv("PDT_MAX_IMAGE_BYTES", str(1_800_000)))  # ~1.8MB

    # Sécurité tokens envoyés à PostgREST
    MAX_TOKEN_LEN = int(os.getenv("PDT_MAX_TOKEN_LEN", "48").strip() or "48")

    # Liens d'affiliation "fiables" (tracking)
    AFFILIATE_HOST_HINTS = ("linksynergy.com", "linkshare.com", "rakuten", "awin")

    # Tokens réels observés dans tes secondary_category (FR/EN)
    CATEGORY_TOKENS = {
        "tops": [
            # FR
            "vêtements~~pull", "vetements~~pull",
            "vêtements~~chemise", "vetements~~chemise",
            "vêtements~~tee-shirt", "vetements~~tee-shirt",
            "vêtements~~t-shirt", "vetements~~t-shirt",
            "vêtements~~top", "vetements~~top",
            "vêtements~~top & blouse", "vetements~~top & blouse",
            "vêtements~~gilet", "vetements~~gilet",
            "vêtements~~maille", "vetements~~maille",
            # EN
            "clothing~~tops", "clothing~~top", "clothing~~shirts", "clothing~~blouses",
            "clothing~~knitwear", "clothing~~sweaters",
        ],
        "bottoms": [
            "vêtements~~pantalon", "vetements~~pantalon",
            "vêtements~~jean", "vetements~~jean",
            "vêtements~~jupe", "vetements~~jupe",
            "vêtements~~short", "vetements~~short",
            "clothing~~trousers", "clothing~~pants", "clothing~~jeans", "clothing~~skirts", "clothing~~shorts",
        ],
        "dresses_playsuits": [
            "vêtements~~robe", "vetements~~robe",
            "clothing~~dresses", "clothing~~dress",
            "clothing~~playsuits", "clothing~~jumpsuits",
        ],
        "outerwear": [
            "vêtements~~manteau", "vetements~~manteau",
            "vêtements~~veste", "vetements~~veste",
            "vêtements~~veste & blouson", "vetements~~veste & blouson",
            "clothing~~outerwear", "clothing~~coats", "clothing~~jackets", "clothing~~blazers", "clothing~~trench",
        ],
        "swim_lingerie": [
            "vêtements~~underwear", "vetements~~underwear",
            "vêtements~~lingerie", "vetements~~lingerie",
            "vêtements~~maillot", "vetements~~maillot",
            "clothing~~underwear", "clothing~~lingerie", "clothing~~swimwear",
        ],
        "shoes": [
            "footwear~~sneakers", "footwear~~boots", "footwear~~sandals",
            "footwear~~shoes",
            "chaussures~~baskets", "chaussures~~chaussures",
            "chaussures", "footwear",
        ],
        "accessories": [
            "accessories", "apparel & accessories",
            "luggage & bags",
            "sac", "bag", "ceinture", "belt", "bijou", "jewellery", "jewelry",
        ],
    }

    def __init__(self):
        self.client = supabase.get_client()
        # cache mémoire (évite de retélécharger la même image 10x sur un même rapport)
        self._image_cache: Dict[str, str] = {}

    # -------------------------
    # Public API
    # -------------------------
    def enrich_pieces(self, pieces: List[Dict[str, Any]], category: str) -> List[Dict[str, Any]]:
        out = []
        for p in pieces or []:
            if not isinstance(p, dict):
                continue
            p2 = dict(p)
            p2["match"] = self.match_piece(p2, category)
            out.append(p2)
        return out

    def match_piece(self, piece: Dict[str, Any], category: str) -> Dict[str, Any]:
        piece_title = (piece.get("piece_title") or "").strip()
        spec = (piece.get("spec") or "").strip()
        visual_key = (piece.get("visual_key") or "").strip()

        candidates = self._find_affiliate_products(
            piece_title=piece_title,
            spec=spec,
            category=category,
            limit=20,
        )
        top3 = self._pick_top3_valid_candidates(candidates)

        try:
            print(f"🧩 MATCH [{category}] '{piece_title[:60]}' → {len(candidates)} candidats / {len(top3)} retenus")
        except Exception:
            pass

        if top3:
            main = top3[0]
            raw_img = (main.get("image_url") or "").strip()
            safe_img = self._ensure_cached_public_image(raw_img, main) if raw_img else ""

            alt1 = top3[1] if len(top3) > 1 else None
            alt2 = top3[2] if len(top3) > 2 else None

            return {
                "image_url": safe_img,
                "product_url": (main.get("buy_url") or main.get("product_url") or "").strip(),
                "source": "affiliate",
                "title": (main.get("product_name") or piece_title).strip(),
                "brand": (main.get("brand") or "").strip(),
                "price": str(main.get("price", "") or ""),
                "alt1_url": ((alt1 or {}).get("buy_url") or (alt1 or {}).get("product_url") or "").strip(),
                "alt1_label": self._format_alt_label(alt1) if alt1 else "",
                "alt2_url": ((alt2 or {}).get("buy_url") or (alt2 or {}).get("product_url") or "").strip(),
                "alt2_label": self._format_alt_label(alt2) if alt2 else "",
            }

        # Fallback visuel pédagogique
        visual = self._find_visual_by_key(visual_key=visual_key, category=category)
        if visual:
            return {
                "image_url": (visual.get("url_image") or "").strip(),
                "product_url": "",
                "source": "visual",
                "title": piece_title,
                "brand": "",
                "price": "",
                "alt1_url": "",
                "alt1_label": "",
                "alt2_url": "",
                "alt2_label": "",
            }

        return {
            "image_url": "",
            "product_url": "",
            "source": "none",
            "title": piece_title,
            "brand": "",
            "price": "",
            "alt1_url": "",
            "alt1_label": "",
            "alt2_url": "",
            "alt2_label": "",
        }

    # -------------------------
    # Output helpers
    # -------------------------
    def _format_alt_label(self, row: Optional[Dict[str, Any]]) -> str:
        if not row:
            return ""
        brand = (row.get("brand") or "").strip()
        price = row.get("price")
        title = (row.get("product_name") or "").strip()
        p = ""
        if price is not None and str(price).strip():
            p = f"{price}€"
        if brand and p:
            return f"{brand} — {p}"
        if brand:
            return brand
        if title:
            return title[:48] + ("…" if len(title) > 48 else "")
        return "Alternative"

    # -------------------------
    # Candidate selection / dedupe
    # -------------------------
    def _pick_top3_valid_candidates(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        seen = set()

        for c in candidates or []:
            if not isinstance(c, dict):
                continue
            buy_url = (c.get("buy_url") or "").strip()
            product_id = str(c.get("product_id") or "").strip()
            image_url = (c.get("image_url") or "").strip()
            if not buy_url and not product_id and not image_url:
                continue
            key = buy_url or product_id or image_url
            if key in seen:
                continue
            seen.add(key)
            out.append(c)
            if len(out) >= 3:
                break

        return out[:3]

    def _is_affiliate_tracking_url(self, url: str) -> bool:
        if not url:
            return False
        try:
            host = (urlparse(url).netloc or "").lower()
            return any(h in host for h in self.AFFILIATE_HOST_HINTS)
        except Exception:
            return False

    # -------------------------
    # Text helpers
    # -------------------------
    def _strip_accents(self, s: str) -> str:
        s = s or ""
        return "".join(
            c for c in unicodedata.normalize("NFD", s)
            if unicodedata.category(c) != "Mn"
        )

    def _normalize_for_match(self, s: str) -> str:
        s = self._strip_accents((s or "").lower())
        s = re.sub(r"\s{2,}", " ", s).strip()
        return s

    def _normalize_kw_for_ilike(self, kw: str) -> str:
        kw = (kw or "").strip().lower()
        if not kw:
            return ""
        kw = self._strip_accents(kw)
        kw = re.sub(r"[^a-z0-9\-\s]", " ", kw)
        kw = re.sub(r"\s{2,}", " ", kw).strip()
        parts = kw.split()[:2]
        kw = " ".join(parts)
        if len(kw) > self.MAX_TOKEN_LEN:
            kw = kw[: self.MAX_TOKEN_LEN]
        return kw

    def _category_match(self, row: Dict[str, Any], category: str) -> bool:
        tokens = self.CATEGORY_TOKENS.get(category, [])
        if not tokens:
            return True
        sc = self._normalize_for_match(row.get("secondary_category") or "")
        pc = self._normalize_for_match(row.get("primary_category") or "")
        hay = f"{pc} {sc}"
        for t in tokens:
            tt = self._normalize_for_match(t)
            if tt and tt in hay:
                return True
        return False

    # -------------------------
    # Image cache (Supabase Storage)
    # -------------------------
    def _ensure_cached_public_image(self, image_url: str, affiliate_row: Dict[str, Any]) -> str:
        if not image_url:
            return ""

        # Cache mémoire (évite x10 downloads dans un même rapport)
        if image_url in self._image_cache:
            return self._image_cache[image_url]

        # Déjà un public supabase
        if "supabase.co/storage/v1/object/public" in image_url:
            url = image_url.strip()
            out = url[:-1] if url.endswith("?") else url
            self._image_cache[image_url] = out
            return out

        try:
            product_id = str(affiliate_row.get("product_id") or "")
            name = str(affiliate_row.get("product_name") or "")
            key_seed = f"{product_id}|{name}|{image_url}"
            h = hashlib.sha256(key_seed.encode("utf-8")).hexdigest()[:24]

            # extension la plus probable (on forcera content-type si besoin)
            ext = "jpg"
            low = image_url.lower()
            if ".png" in low:
                ext = "png"
            elif ".webp" in low:
                ext = "webp"
            elif ".jpeg" in low:
                ext = "jpeg"

            object_path = f"pdt/{h}.{ext}"
            bucket = self.client.storage.from_(self.AFFILIATE_IMAGE_BUCKET)

            # URL publique (même si l’objet n’existe pas encore)
            public = bucket.get_public_url(object_path)
            public_url = public.get("publicUrl") if isinstance(public, dict) else str(public or "")
            public_url = (public_url or "").strip()
            if public_url.endswith("?"):
                public_url = public_url[:-1]

            timeout = httpx.Timeout(
                connect=self.HTTP_CONNECT_TIMEOUT,
                read=self.HTTP_READ_TIMEOUT,
                write=self.HTTP_READ_TIMEOUT,
                pool=self.HTTP_CONNECT_TIMEOUT,
            )

            # 1) Test rapide si déjà présent
            if public_url:
                try:
                    r0 = httpx.get(
                        public_url,
                        headers={"Range": "bytes=0-0"},
                        timeout=timeout,
                        follow_redirects=True,
                    )
                    if r0.status_code in (200, 206):
                        self._image_cache[image_url] = public_url
                        return public_url
                except Exception:
                    pass

            # 2) Télécharger depuis CDN (anti-hotlink)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
                "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
                "Referer": "https://www.placedestendances.com/",
                "Origin": "https://www.placedestendances.com",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
            }

            with httpx.Client(timeout=timeout, follow_redirects=True) as client:
                r = client.get(image_url, headers=headers)
                r.raise_for_status()

                # garde-fou taille
                data = r.content or b""
                if not data or len(data) < 200:
                    self._image_cache[image_url] = image_url
                    return image_url
                if len(data) > self.MAX_IMAGE_BYTES:
                    # trop gros -> on n’upload pas (mais on ne crash pas)
                    self._image_cache[image_url] = image_url
                    return image_url

                content_type = (r.headers.get("content-type", "") or "").split(";")[0].strip()
                if not content_type.startswith("image/"):
                    content_type = f"image/{ext}"

            # 3) Upload (upsert)
            try:
                bucket.upload(
                    path=object_path,
                    file=data,
                    file_options={"content-type": content_type, "upsert": True},
                )
            except Exception as e:
                # si upload rate, on retombe sur original
                print(f"⚠️ Storage upload failed: {e}")
                self._image_cache[image_url] = image_url
                return image_url

            # 4) Reprendre l’URL publique
            public2 = bucket.get_public_url(object_path)
            public_url2 = public2.get("publicUrl") if isinstance(public2, dict) else str(public2 or "")
            public_url2 = (public_url2 or "").strip()
            if public_url2.endswith("?"):
                public_url2 = public_url2[:-1]

            out = public_url2 or image_url
            self._image_cache[image_url] = out
            return out

        except Exception as e:
            print(f"⚠️ Image cache failed: {e}")
            self._image_cache[image_url] = image_url
            return image_url

    # -------------------------
    # AFFILIATE MATCH (TABLE affiliate_products)
    # -------------------------
    def _find_affiliate_products(self, piece_title: str, spec: str, category: str, limit: int = 20) -> List[Dict[str, Any]]:
        kws = self._extract_keywords(piece_title, spec)

        # On sélectionne le strict nécessaire (plus rapide)
        select_fields = ",".join([
            "product_id",
            "product_name",
            "brand",
            "primary_category",
            "secondary_category",
            "product_url",
            "image_url",
            "buy_url",
            "price",
            "sale_price",
            "currency",
            "availability",
            "is_deleted",
            "last_seen_at",
        ])

        collected: List[Dict[str, Any]] = []
        seen = set()

        def _add_rows(rows: List[Dict[str, Any]]) -> None:
            nonlocal collected, seen
            for row in rows or []:
                key = (row.get("buy_url") or "").strip() or str(row.get("product_id") or "").strip() or (row.get("image_url") or "").strip()
                if not key:
                    continue
                if key in seen:
                    continue
                seen.add(key)
                collected.append(row)
                if len(collected) >= limit:
                    return

        def _base_query():
            q = self.client.table(self.AFFILIATE_TABLE).select(select_fields).eq("is_deleted", False)
            # priorise last_seen_at si dispo
            try:
                q = q.order("last_seen_at", desc=True)
            except Exception:
                pass
            return q

        # PHASE 1: kw + filtre catégorie en Python
        for kw in kws[:3]:
            if len(collected) >= limit:
                break
            kw_safe = self._normalize_kw_for_ilike(kw)
            if len(kw_safe) < 3:
                continue
            try:
                q = _base_query().ilike("product_name", f"%{kw_safe}%").limit(60)
                resp = q.execute()
                data = getattr(resp, "data", None) or []
                filtered = [r for r in data if self._category_match(r, category)]
                _add_rows(filtered)
            except Exception as e:
                print(f"⚠️ KW+CAT query failed: {e}")

        # PHASE 2: kw sans catégorie
        if len(collected) < 6:
            for kw in kws[:3]:
                if len(collected) >= limit:
                    break
                kw_safe = self._normalize_kw_for_ilike(kw)
                if len(kw_safe) < 3:
                    continue
                try:
                    q = _base_query().ilike("product_name", f"%{kw_safe}%").limit(60)
                    resp = q.execute()
                    data = getattr(resp, "data", None) or []
                    _add_rows(data)
                except Exception as e:
                    print(f"⚠️ KW query failed: {e}")

        # PHASE 3: fallback catégorie (secondary_category)
        if len(collected) < 10:
            tokens = self.CATEGORY_TOKENS.get(category, []) or []
            # on essaie 2 tokens max
            for t0 in tokens[:2]:
                if len(collected) >= limit:
                    break
                t = self._normalize_kw_for_ilike(t0)
                if len(t) < 3:
                    continue
                try:
                    q = _base_query().ilike("secondary_category", f"%{t}%").limit(60)
                    resp = q.execute()
                    data = getattr(resp, "data", None) or []
                    _add_rows(data)
                except Exception as e:
                    print(f"⚠️ CAT secondary query failed: {e}")

        # PHASE 4: fallback primary_category
        if len(collected) < 10:
            tokens = self.CATEGORY_TOKENS.get(category, []) or []
            for t0 in tokens[:2]:
                if len(collected) >= limit:
                    break
                t = self._normalize_kw_for_ilike(t0)
                if len(t) < 3:
                    continue
                try:
                    q = _base_query().ilike("primary_category", f"%{t}%").limit(60)
                    resp = q.execute()
                    data = getattr(resp, "data", None) or []
                    _add_rows(data)
                except Exception as e:
                    print(f"⚠️ CAT primary query failed: {e}")

        return collected[:limit]

    def _extract_keywords(self, piece_title: str, spec: str) -> List[str]:
        text = f"{piece_title} {spec}".lower()
        text = re.sub(r"[^a-zàâçéèêëîïôûùüÿñæœ0-9\s-]", " ", text)
        text = re.sub(r"\s{2,}", " ", text).strip()

        stop = {
            "a", "à", "au", "aux", "de", "des", "du", "en", "et", "ou",
            "un", "une", "avec", "pour", "la", "le", "les", "d", "l",
            "sur", "dans", "sans", "style",
            "matiere", "matières", "coton", "laine", "viscose", "soie",
            # très fréquents inutiles
            "femme", "homme", "taille", "noir", "blanc",
        }

        tokens = [t.strip() for t in text.split() if t.strip()]
        tokens = [t for t in tokens if t not in stop and len(t) >= 3]

        # patterns utiles
        joined = " ".join(tokens)
        patterns = []
        if "col v" in joined or ("col" in tokens and "v" in tokens):
            patterns.append("col v")
        if "taille haute" in joined:
            patterns.append("taille haute")
        if "bootcut" in joined:
            patterns.append("bootcut")

        base = []
        for src in [piece_title.lower(), spec.lower()]:
            src = re.sub(r"[^a-zàâçéèêëîïôûùüÿñæœ0-9\s-]", " ", src)
            src = re.sub(r"\s{2,}", " ", src).strip()
            for t in src.split():
                if t in stop or len(t) < 3:
                    continue
                if t not in base:
                    base.append(t)

        out = patterns + base
        seen = set()
        final = []
        for x in out:
            k = x.strip().lower()
            if k and k not in seen:
                seen.add(k)
                final.append(k)
        return final[:8]

    # -------------------------
    # VISUELS FALLBACK
    # -------------------------
    def _find_visual_by_key(self, visual_key: str, category: str) -> Optional[Dict[str, Any]]:
        if not visual_key:
            return None
        try:
            q = (
                self.client.table("visuels")
                .select("nom_simplifie, type_vetement, coupe, url_image")
                .eq("nom_simplifie", visual_key)
                .limit(1)
            )
            expected_type = self.VISUELS_TYPE_MAP.get(category)
            if expected_type:
                q = q.eq("type_vetement", expected_type)

            resp = q.execute()
            data = getattr(resp, "data", None) or []
            if data:
                return data[0]

            # fallback sans type_vetement
            resp2 = (
                self.client.table("visuels")
                .select("nom_simplifie, type_vetement, coupe, url_image")
                .eq("nom_simplifie", visual_key)
                .limit(1)
                .execute()
            )
            data2 = getattr(resp2, "data", None) or []
            return data2[0] if data2 else None
        except Exception as e:
            print(f"⚠️ Visual fallback failed (key={visual_key}): {e}")
            return None


product_matcher_service = ProductMatcherService()
