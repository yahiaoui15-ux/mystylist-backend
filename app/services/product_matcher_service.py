# app/services/product_matcher_service.py
from typing import Dict, Any, List, Optional
import re
import hashlib
import os
import httpx
import unicodedata

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.utils.supabase_client import supabase
from urllib.parse import quote, urlparse




class ProductMatcherService:
    """
    Match une pièce IA vers:
    1) un produit affilié (TABLE: affiliate_products)
    2) sinon un visuel pédagogique (table `visuels`)

    v9 (Points 1 + 2):
    - PHASE 0: style-aware search via affiliate_product_enrichment
    - Image-first selection: tente jusqu'à 4 candidats pour le produit principal
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

    PRODUCT_BLACKLIST_KEYWORDS = [
        "trousse", "pochette beaute", "pochette maquillage",
        "sac voyage", "bagage", "valise", "cosmetic",
        "beauty bag", "bébé", "bebe", "enfant", "garçon", "garcon", "fille",
        "maternité", "maternite", "sport", "jogging", "pyjama", "nuisette",
    ]

    # ── Mapping styles styling → tags enrichment ──────────────────────────
    # Les tags enrichment sont les clés du classifier v6 (lowercase, sans accent).
    STYLE_LABEL_TO_ENRICHMENT_TAG: Dict[str, str] = {
        # Labels courts (style_mix dans styling)
        "Classique": "classique",
        "Chic": "chic",
        "Casual": "casual",
        "Rock": "rock",
        "Moderne": "moderne",
        "Sporty Chic": "sportswear",
        "Sportswear": "sportswear",
        "Vintage": "vintage",
        "Bohème": "boheme",
        "Boheme": "boheme",
        # Labels complets (styling._score_styles keys)
        "Style Classique / Intemporel": "classique",
        "Style Chic / Élégant": "chic",
        "Style Casual / Décontracté": "casual",
        "Style Rock": "rock",
        "Style Moderne / Contemporain": "moderne",
        "Style Sporty Chic": "sportswear",
        "Style Urbain / Streetwear": "streetwear",
        "Style Vintage": "vintage",
        "Style Bohème": "boheme",
        # Styles sans équivalent enrichment (romantique, minimaliste, etc.)
        # → pas de mapping → PHASE 0 ignorée pour eux, fallback PHASE 1
    }

    AFFILIATE_TABLE = os.getenv("AFFILIATE_TABLE", "affiliate_products")
    AFFILIATE_IMAGE_BUCKET = os.getenv("AFFILIATE_IMAGE_BUCKET", "affiliate-cache")
    AFFILIATE_PRIMARY_CATEGORY = (os.getenv("AFFILIATE_PRIMARY_CATEGORY", "Femme") or "").strip()

    HTTP_TIMEOUT = float(os.getenv("PDT_HTTP_TIMEOUT", "8.0").strip() or "8.0")
    MAX_TOKEN_LEN = int(os.getenv("PDT_MAX_TOKEN_LEN", "48").strip() or "48")

    PDT_PRODUCT_ID_RE = re.compile(r"(\d{6,})", re.IGNORECASE)
    AFFILIATE_HOST_HINTS = ("linksynergy.com", "linkshare.com", "rakuten", "awin")

    CATEGORY_TOKENS = {
        "tops": ["top", "tops", "haut", "hauts", "blouse", "chemis", "tee", "t-shirt", "pull", "maille", "sweat"],
        "bottoms": ["bas", "pantalon", "jean", "jupe", "short", "trouser", "pants", "jeans", "skirt", "shorts"],
        "dresses_playsuits": ["robe", "dress", "dresses", "combinaison", "jumpsuit", "playsuit"],
        "outerwear": ["manteau", "veste", "blouson", "trench", "coat", "jacket", "blazer"],
        "swim_lingerie": ["lingerie", "underwear", "swim", "swimwear", "maillot"],
        "shoes": ["chauss", "shoe", "shoes", "boots", "boot", "sneaker", "basket", "sandale"],
        "accessories": ["access", "accessory", "accessories", "sac", "bag", "ceinture", "belt", "bijou", "jewel"],
    }

    def __init__(self):
        self.client = supabase.get_client()

    # -------------------------
    # Public API
    # -------------------------
    def enrich_pieces(
        self,
        pieces: List[Dict[str, Any]],
        category: str,
        style_tags: Optional[List[str]] = None,   # ← nouveau, rétrocompat
    ) -> List[Dict[str, Any]]:
        out = []
        for p in pieces or []:
            if not isinstance(p, dict):
                continue
            p2 = dict(p)
            p2["match"] = self.match_piece(p2, category, style_tags=style_tags)
            m = p2.get("match") or {}
            p2["image_url"] = (m.get("image_url") or "").strip()
            p2["product_url"] = (m.get("product_url") or "").strip()
            p2["source"] = (m.get("source") or "").strip()
            out.append(p2)
        return out

    def match_piece(
        self,
        piece: Dict[str, Any],
        category: str,
        style_tags: Optional[List[str]] = None,   # ← nouveau, rétrocompat
    ) -> Dict[str, Any]:
        piece_title = (piece.get("piece_title") or "").strip()
        spec = (piece.get("spec") or "").strip()
        visual_key = (piece.get("visual_key") or "").strip()

        candidates = self._find_affiliate_products(
            piece_title=piece_title,
            spec=spec,
            category=category,
            limit=20,
            style_tags=style_tags,
        )

        # ── IMAGE-FIRST: on tente jusqu'à 4 candidats pour trouver une image ──
        valid_pool = self._pick_top_n_valid_candidates(candidates, n=4)

        try:
            print(f"🧩 MATCH [{category}] '{piece_title[:60]}' → {len(candidates)} candidats / {len(valid_pool)} retenus")
        except Exception:
            pass

        if valid_pool:
            # Cherche le premier candidat avec une image qui fonctionne
            main = None
            safe_img = ""
            remaining = []

            for idx, candidate in enumerate(valid_pool):
                raw_img = (candidate.get("image_url") or "").strip()
                img = self._ensure_cached_public_image(raw_img, candidate) if raw_img else ""
                print("🖼️ IMG raw:", raw_img)
                print("🖼️ IMG safe:", img)
                if img:
                    main = candidate
                    safe_img = img
                    remaining = valid_pool[idx + 1:]
                    break

            # Si aucun candidat avec image → on prend le premier quand même
            if main is None:
                main = valid_pool[0]
                remaining = valid_pool[1:]

            alt1 = remaining[0] if len(remaining) > 0 else None
            alt2 = remaining[1] if len(remaining) > 1 else None

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

        # 2) fallback visuel pédagogique
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

        print(f"⚠️ No visual fallback for visual_key='{visual_key}'")
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

    def match_piece_top4(self, piece: Dict[str, Any], category: str) -> List[Dict[str, Any]]:
        """
        Comme match_piece mais retourne une LISTE de 4 produits complets.
        Utilisé pour shopping_products_flat (page 12).
        """
        piece_title = (piece.get("piece_title") or "").strip()
        spec        = (piece.get("spec") or "").strip()

        candidates = self._find_affiliate_products(
            piece_title=piece_title,
            spec=spec,
            category=category,
            limit=30,
        )
        top4 = self._pick_top_n_valid_candidates(candidates, n=4)

        results = []
        for candidate in top4:
            raw_img  = (candidate.get("image_url") or "").strip()
            safe_img = self._ensure_cached_public_image(raw_img, candidate) if raw_img else ""
            results.append({
                "image_url":   safe_img,
                "product_url": (candidate.get("buy_url") or candidate.get("product_url") or "").strip(),
                "brand":       (candidate.get("brand") or "").strip(),
                "price":       str(candidate.get("price", "") or ""),
                "title":       (candidate.get("product_name") or piece_title).strip(),
            })
            status = "✅" if safe_img else "⚠️"
            print(f"   {status} TOP4 [{category}] '{piece_title[:40]}' → {(candidate.get('brand') or '')[:20]}")

        return results

    # -------------------------
    # Style helpers (Point 1)
    # -------------------------
    def _map_styles_to_enrichment_tags(self, style_labels: List[str]) -> List[str]:
        """Convertit les labels styling (ex: 'Classique') en tags enrichment (ex: 'classique')."""
        tags = []
        for label in style_labels or []:
            label = (label or "").strip()
            tag = self.STYLE_LABEL_TO_ENRICHMENT_TAG.get(label)
            if tag:
                tags.append(tag)
            else:
                # Tentative par normalisation : lowercase + strip accents
                normalized = self._strip_accents(label.lower())
                if normalized.startswith("style "):
                    normalized = normalized[6:]
                normalized = re.sub(r"[^a-z0-9]", "", normalized)
                if len(normalized) >= 3:
                    tags.append(normalized)
        return list(dict.fromkeys(tags))  # déduplique en préservant l'ordre

    def _find_affiliate_products_phase0_style(
        self,
        piece_title: str,
        style_tags: List[str],
        category: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        PHASE 0 — Style-aware: requête affiliate_product_enrichment sur style_primary,
        puis récupère les produits correspondants dans affiliate_products.
        Retourne une liste pré-filtrée par catégorie.
        """
        if not style_tags:
            return []

        enrichment_tags = self._map_styles_to_enrichment_tags(style_tags)
        if not enrichment_tags:
            return []

        select_fields = ",".join([
            "product_id", "product_name", "brand", "primary_category",
            "secondary_category", "product_url", "image_url", "buy_url",
            "price", "sale_price", "currency", "availability",
            "is_deleted", "last_seen_at",
        ])

        try:
            # 1) Récupère les product_ids dont style_primary est dans nos tags
            q_enrich = (
                self.client.table("affiliate_product_enrichment")
                .select("product_id")
                .in_("style_primary", enrichment_tags)
                .limit(200)
            )
            resp_enrich = self._execute(q_enrich)
            enrich_data = getattr(resp_enrich, "data", None) or []
            product_ids = [row["product_id"] for row in enrich_data if row.get("product_id")]

            if not product_ids:
                return []

            # 2) Récupère ces produits dans affiliate_products + filtre keyword
            kws = self._extract_keywords(piece_title, "")
            kw_safe = self._normalize_kw_for_ilike(kws[0]) if kws else ""

            # On limite à 50 product_ids pour éviter une requête trop lourde
            q_products = (
                self.client.table(self.AFFILIATE_TABLE)
                .select(select_fields)
                .eq("is_deleted", False)
                .in_("product_id", product_ids[:50])
            )
            if self.AFFILIATE_PRIMARY_CATEGORY:
                q_products = q_products.eq("primary_category", self.AFFILIATE_PRIMARY_CATEGORY)
            if len(kw_safe) >= 3:
                q_products = q_products.ilike("product_name", self._ilike_pattern(kw_safe))

            q_products = q_products.limit(40)
            resp_products = self._execute(q_products)
            data = getattr(resp_products, "data", None) or []

            # 3) Filtre catégorie
            filtered = [r for r in data if self._category_match(r, category)]
            if filtered:
                print(f"✅ PHASE0 style [{category}] tags={enrichment_tags}: {len(filtered)} produits")
            return filtered[:limit]

        except Exception as e:
            print(f"⚠️ PHASE 0 style failed: {e}")
            return []

    # -------------------------
    # Output helpers
    # -------------------------
    def _format_alt_label(self, row: Optional[Dict[str, Any]]) -> str:
        if not row:
            return ""
        brand = (row.get("brand") or "").strip()
        price = row.get("price")
        title = (row.get("product_name") or "").strip()
        p = f"{price}€" if price is not None and str(price).strip() else ""
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
        return self._pick_top_n_valid_candidates(candidates, n=3)

    def _pick_top_n_valid_candidates(self, candidates: List[Dict[str, Any]], n: int = 4) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        seen_urls   = set()
        seen_names  = set()
        seen_images = set()

        for c in candidates or []:
            if not isinstance(c, dict):
                continue

            buy_url    = (c.get("buy_url") or "").strip()
            product_id = str(c.get("product_id") or "").strip()
            raw_img    = (c.get("image_url") or "").strip()

            if not buy_url and not product_id and not raw_img:
                continue

            url_key = buy_url or product_id or raw_img
            product_name = (c.get("product_name") or "").strip().lower()[:60]
            img_base = raw_img.split("?")[0] if raw_img else ""

            if url_key in seen_urls:
                continue
            if product_name and product_name in seen_names:
                continue
            if img_base and img_base in seen_images:
                continue

            seen_urls.add(url_key)
            if product_name:
                seen_names.add(product_name)
            if img_base:
                seen_images.add(img_base)

            # Blacklist
            product_name_lower = (c.get("product_name") or "").lower()
            secondary_cat_lower = (c.get("secondary_category") or "").lower()
            combined_text = product_name_lower + " " + secondary_cat_lower
            if any(bk in combined_text for bk in self.PRODUCT_BLACKLIST_KEYWORDS):
                continue

            out.append(c)
            if len(out) >= n:
                break

        return out[:n]

    # -------------------------
    # Text helpers
    # -------------------------
    def _strip_accents(self, s: str) -> str:
        s = s or ""
        return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

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

    def _ilike_pattern(self, token: str) -> str:
        t = (token or "").strip()
        if not t:
            return ""
        t = t.replace("*", " ").strip()
        t = re.sub(r"\s{2,}", " ", t)
        return f"*{t}*"

    def _category_match(self, row: Dict[str, Any], category: str) -> bool:
        tokens = self.CATEGORY_TOKENS.get(category, [])
        if not tokens:
            return True
        sc = (row.get("secondary_category") or "").lower()
        pc = (row.get("primary_category") or "").lower()
        hay = f"{pc} {sc}"
        return any(t in hay for t in tokens)

    # -------------------------
    # Robust Supabase call (retry)
    # -------------------------
    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.6, min=0.6, max=3.0),
        retry=retry_if_exception_type(Exception),
    )
    def _execute(self, q):
        return q.execute()

    # -------------------------
    # Image cache (Supabase Storage)
    # -------------------------
    def _ensure_cached_public_image(self, image_url: str, affiliate_row: Dict[str, Any]) -> str:
        image_url = (image_url or "").strip()
        if image_url.endswith("?"):
            image_url = image_url[:-1]

        base_url = image_url.split("?", 1)[0]

        if not image_url:
            return ""

        if "supabase.co/storage/v1/object/public" in image_url:
            url = image_url.strip()
            return url[:-1] if url.endswith("?") else url

        try:
            product_id = str(affiliate_row.get("product_id") or "")
            name = str(affiliate_row.get("product_name") or "")
            key_seed = f"{product_id}|{name}|{base_url or image_url}"
            h = hashlib.sha256(key_seed.encode("utf-8")).hexdigest()[:24]

            ext = "jpg"
            low = (base_url or image_url).lower()
            if ".png" in low:
                ext = "png"
            elif ".webp" in low:
                ext = "webp"
            elif ".jpeg" in low:
                ext = "jpeg"

            object_path = f"pdt/{h}.{ext}"
            bucket = self.client.storage.from_(self.AFFILIATE_IMAGE_BUCKET)

            try:
                public = bucket.get_public_url(object_path)
                public_url = public.get("publicUrl") if isinstance(public, dict) else str(public or "")
                public_url = (public_url or "").strip()
                if public_url.endswith("?"):
                    public_url = public_url[:-1]
                if public_url:
                    r = httpx.get(
                        public_url,
                        headers={"Range": "bytes=0-0"},
                        timeout=self.HTTP_TIMEOUT,
                        follow_redirects=True,
                    )
                    if r.status_code in (200, 206):
                        return public_url
            except Exception:
                pass

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
                "Referer": "https://www.placedestendances.com/",
                "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
            }

            proxy_target = base_url or image_url
            try:
                u = urlparse(proxy_target)
                target_no_scheme = f"{u.netloc}{u.path}"
                proxy_url = f"https://images.weserv.nl/?url={quote(target_no_scheme, safe='')}"
            except Exception:
                proxy_url = f"https://images.weserv.nl/?url={quote(proxy_target, safe='')}"

            try_url = base_url or image_url
            r = httpx.get(try_url, headers=headers, timeout=20.0, follow_redirects=True)

            if r.status_code in (401, 403):
                r2 = httpx.get(proxy_url, headers={"User-Agent": headers["User-Agent"]}, timeout=20.0, follow_redirects=True)
                print("🧪 proxy status:", r2.status_code, "proxy_url:", proxy_url)
                r = r2

            if r.status_code >= 400 and try_url != image_url:
                r = httpx.get(image_url, headers=headers, timeout=20.0, follow_redirects=True)

            r.raise_for_status()

            content_type = (r.headers.get("content-type", "") or "").strip()
            data = r.content
            if not data or len(data) < 200:
                return ""

            bucket.upload(
                path=object_path,
                file=data,
                file_options={
                    "content-type": content_type or f"image/{ext}",
                    "upsert": "true",
                },
            )

            public = bucket.get_public_url(object_path)
            public_url = public.get("publicUrl") if isinstance(public, dict) else str(public or "")
            public_url = (public_url or "").strip()
            if public_url.endswith("?"):
                public_url = public_url[:-1]

            return public_url or ""

        except Exception as e:
            print(f"⚠️ Image cache failed: {e}")
            return ""

    # -------------------------
    # AFFILIATE MATCH
    # -------------------------
    def _base_query(self, select_fields: str):
        q = self.client.table(self.AFFILIATE_TABLE).select(select_fields)
        q = q.eq("is_deleted", False)
        if self.AFFILIATE_PRIMARY_CATEGORY:
            q = q.eq("primary_category", self.AFFILIATE_PRIMARY_CATEGORY)
        return q

    def _find_affiliate_products(
        self,
        piece_title: str,
        spec: str,
        category: str,
        limit: int = 20,
        style_tags: Optional[List[str]] = None,   # ← nouveau, rétrocompat
    ) -> List[Dict[str, Any]]:
        kws = self._extract_keywords(piece_title, spec)

        select_fields = ",".join([
            "product_id", "product_name", "brand", "primary_category",
            "secondary_category", "product_url", "image_url", "buy_url",
            "price", "sale_price", "currency", "availability",
            "is_deleted", "last_seen_at",
        ])

        collected: List[Dict[str, Any]] = []
        seen = set()

        def _add_rows(rows: List[Dict[str, Any]]) -> None:
            nonlocal collected, seen
            for row in rows or []:
                key = (row.get("buy_url") or "").strip() or str(row.get("product_id") or "").strip()
                if not key:
                    key = hashlib.sha256((row.get("image_url") or "").encode("utf-8")).hexdigest()[:12]
                if key in seen:
                    continue
                seen.add(key)
                collected.append(row)
                if len(collected) >= limit:
                    return

        # ────────────────────────────────────────────────────────
        # PHASE 0 — Style-aware via affiliate_product_enrichment
        # ────────────────────────────────────────────────────────
        if style_tags:
            phase0 = self._find_affiliate_products_phase0_style(
                piece_title=piece_title,
                style_tags=style_tags,
                category=category,
                limit=10,
            )
            _add_rows(phase0)

        # ────────────────────────────────────────────────────────
        # PHASE 1 — Keyword + category filter (côté Python)
        # ────────────────────────────────────────────────────────
        for kw in kws[:1]:
            if len(collected) >= limit:
                break
            kw_safe = self._normalize_kw_for_ilike(kw)
            if len(kw_safe) < 3:
                continue
            try:
                pattern = self._ilike_pattern(kw_safe)
                q = self._base_query(select_fields).ilike("product_name", pattern).limit(40)
                resp = self._execute(q)
                data = getattr(resp, "data", None) or []
                filtered = [r for r in data if self._category_match(r, category)]
                _add_rows(filtered)
                if filtered:
                    print(f"✅ KW+CAT [{category}] '{kw_safe}': {len(filtered)}")
            except Exception as e:
                print(f"⚠️ KW+CAT query failed: {e}")

        # ────────────────────────────────────────────────────────
        # PHASE 2 — Keyword sans filtre catégorie
        # ────────────────────────────────────────────────────────
        if len(collected) < 6:
            for kw in kws[:1]:
                if len(collected) >= limit:
                    break
                kw_safe = self._normalize_kw_for_ilike(kw)
                if len(kw_safe) < 3:
                    continue
                try:
                    pattern = self._ilike_pattern(kw_safe)
                    q = self._base_query(select_fields).ilike("product_name", pattern).limit(40)
                    resp = self._execute(q)
                    data = getattr(resp, "data", None) or []
                    _add_rows(data)
                    if data:
                        print(f"✅ KW [{category}] '{kw_safe}': {len(data)}")
                except Exception as e:
                    print(f"⚠️ KW query failed: {e}")

        # ────────────────────────────────────────────────────────
        # PHASE 3 — Fallback catégorie (secondary_category)
        # ────────────────────────────────────────────────────────
        def _ordered(q):
            try:
                return q.order("last_seen_at", desc=True)
            except Exception:
                return q

        if len(collected) < 10:
            for token in (self.CATEGORY_TOKENS.get(category, []) or [])[:1]:
                if len(collected) >= limit:
                    break
                t = self._normalize_kw_for_ilike(token)
                if len(t) < 3:
                    continue
                try:
                    pattern = self._ilike_pattern(t)
                    q = _ordered(self._base_query(select_fields)).ilike("secondary_category", pattern).limit(40)
                    resp = self._execute(q)
                    data = getattr(resp, "data", None) or []
                    _add_rows(data)
                    if data:
                        print(f"✅ CAT secondary [{category}] '{t}': {len(data)}")
                except Exception as e:
                    print(f"⚠️ CAT secondary query failed: {e}")

        print(f"📊 Total [{category}]: {len(collected)} produits collectés")
        return collected[:limit]

    def _extract_keywords(self, piece_title: str, spec: str) -> List[str]:
        text = f"{piece_title} {spec}".lower()
        text = re.sub(r"[^a-zàâçéèêëîïôûùüÿñæœ0-9\s-]", " ", text)
        text = re.sub(r"\s{2,}", " ", text).strip()

        stop = set([
            "a", "à", "au", "aux", "de", "des", "du", "en", "et", "ou",
            "un", "une", "avec", "pour", "la", "le", "les", "d", "l",
            "sur", "dans", "sans", "style",
            "matiere", "matières", "coton", "laine", "viscose", "soie", "bio",
        ])

        tokens = [t.strip() for t in text.split() if t.strip()]
        tokens = [t for t in tokens if t not in stop and len(t) >= 3]

        base = []
        for src in [piece_title.lower(), spec.lower()]:
            src = re.sub(r"[^a-zàâçéèêëîïôûùüÿñæœ0-9\s-]", " ", src)
            src = re.sub(r"\s{2,}", " ", src).strip()
            for t in src.split():
                if t in stop or len(t) < 3:
                    continue
                if t not in base:
                    base.append(t)

        out = base
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

            resp = self._execute(q)
            data = getattr(resp, "data", None) or []
            if data:
                return data[0]

            resp2 = self._execute(
                self.client.table("visuels")
                .select("nom_simplifie, type_vetement, coupe, url_image")
                .eq("nom_simplifie", visual_key)
                .limit(1)
            )
            data2 = getattr(resp2, "data", None) or []
            return data2[0] if data2 else None

        except Exception as e:
            print(f"⚠️ Visual fallback failed (key={visual_key}): {e}")
            return None


product_matcher_service = ProductMatcherService()