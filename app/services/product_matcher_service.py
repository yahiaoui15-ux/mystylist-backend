# app/services/product_matcher_service.py
from typing import Dict, Any, List, Optional
import re
import hashlib
import os
import httpx
import unicodedata

from urllib.parse import urlparse, parse_qs, unquote

from app.utils.supabase_client import supabase


class ProductMatcherService:
    """
    Match une pièce IA (piece_title/spec/visual_key) vers:
    1) un produit affilié (VIEW SQL: active_affiliate_products)  ✅ (aligné avec tes colonnes réelles)
       - récupère jusqu'à 20 candidats
       - renvoie 1 produit principal + 2 alternatives
    2) sinon un visuel pédagogique (table `visuels`)
    + Cache images affiliées dans Supabase Storage (bucket public) pour compat PDFMonkey

    ✅ Correctifs clés:
    - Utilise product_name / keywords / primary_category / secondary_category / buy_url (colonnes réelles)
    - Ne dépend PAS de colonnes inexistantes (title, description_short, product_type, color, material, gender)
    - Déduplication robuste sur buy_url + product_id + image_url
    - Validation réseau désactivée par défaut (HEAD souvent bloqué)
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

    # Bucket public pour cache images affiliées
    AFFILIATE_IMAGE_BUCKET = os.getenv("AFFILIATE_IMAGE_BUCKET", "affiliate-cache")

    # Optionnel: validation réseau d'une page "murl" si présent (désactivée par défaut)
    VALIDATE_MURL_NETWORK = os.getenv("PDT_VALIDATE_MURL_NETWORK", "0").strip() in (
        "1",
        "true",
        "True",
        "yes",
        "YES",
    )

    # Timeout réseau
    HTTP_TIMEOUT = float(os.getenv("PDT_HTTP_TIMEOUT", "8.0").strip() or "8.0")

    # Sécurité: limite la taille des tokens envoyés à PostgREST
    MAX_TOKEN_LEN = int(os.getenv("PDT_MAX_TOKEN_LEN", "48").strip() or "48")

    # Heuristique "page produit" : id long (>=6 chiffres) dans URL
    PDT_PRODUCT_ID_RE = re.compile(r"(\d{6,})", re.IGNORECASE)

    # Liens d'affiliation "fiables" (tracking)
    AFFILIATE_HOST_HINTS = ("linksynergy.com", "linkshare.com", "rakuten", "awin")

    def __init__(self):
        self.client = supabase.get_client()

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
            piece_title=piece_title, spec=spec, category=category, limit=20
        )
        top3 = self._pick_top3_valid_candidates(
            candidates, validate_network=self.VALIDATE_MURL_NETWORK
        )

        # Log simple (utile pour Railway)
        try:
            print(
                f"🧩 MATCH [{category}] '{piece_title[:60]}' → "
                f"{len(candidates)} candidats / {len(top3)} retenus"
            )
        except Exception:
            pass

        if top3:
            main = top3[0]
            raw_img = (main.get("image_url") or "").strip()
            safe_img = self._ensure_cached_public_image(raw_img, main) if raw_img else ""

            alt1 = top3[1] if len(top3) > 1 else None
            alt2 = top3[2] if len(top3) > 2 else None

            # IMPORTANT: dans tes données réelles, le lien tracké est buy_url.
            # On renvoie product_url = buy_url pour que tes clics restent attribués.
            return {
                "image_url": safe_img,
                "product_url": (main.get("buy_url") or "").strip(),
                "source": "affiliate",
                "title": (main.get("product_name") or piece_title).strip(),
                "brand": (main.get("brand") or "").strip(),
                "price": str(main.get("price", "") or ""),
                "alt1_url": ((alt1 or {}).get("buy_url") or "").strip(),
                "alt1_label": self._format_alt_label(alt1) if alt1 else "",
                "alt2_url": ((alt2 or {}).get("buy_url") or "").strip(),
                "alt2_label": self._format_alt_label(alt2) if alt2 else "",
            }

        # 2) Fallback visuel pédagogique
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

        # 3) Rien
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
    def _pick_top3_valid_candidates(
        self,
        candidates: List[Dict[str, Any]],
        validate_network: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        ✅ Version tracking-safe:
        - utilise buy_url (tracking)
        - déduplique sur buy_url puis product_id puis image_url
        - accepte un lien d'affiliation comme "valide" par défaut
        - validation réseau optionnelle uniquement si murl=... présent
        """
        out: List[Dict[str, Any]] = []
        seen = set()

        for c in candidates or []:
            if not isinstance(c, dict):
                continue

            buy_url = (c.get("buy_url") or "").strip()
            product_id = (c.get("product_id") or "").strip()
            image_url = (c.get("image_url") or "").strip()

            if not buy_url and not product_id and not image_url:
                continue

            key = buy_url or product_id or image_url
            if key in seen:
                continue
            seen.add(key)

            # Si tracking -> ok direct
            if buy_url and self._is_affiliate_tracking_url(buy_url):
                out.append(c)
                if len(out) >= 3:
                    break
                continue

            # Sinon, si murl=... on peut heuristiquement checker
            murl = self._extract_murl_from_affiliate_url(buy_url)
            if murl:
                if not self._looks_like_product_page(murl):
                    continue
                out.append(c)
                if len(out) >= 3:
                    break
                continue

            # Sinon on accepte (meilleur que "vide")
            out.append(c)
            if len(out) >= 3:
                break

        # Validation réseau optionnelle
        if validate_network and out:
            try:
                murl0 = self._extract_murl_from_affiliate_url((out[0].get("buy_url") or "").strip())
                if murl0:
                    ok = self._validate_product_page_network(murl0)
                    if not ok:
                        out = out[1:]
            except Exception:
                pass

        return out[:3]

    def _is_affiliate_tracking_url(self, url: str) -> bool:
        if not url:
            return False
        try:
            host = (urlparse(url).netloc or "").lower()
            return any(h in host for h in self.AFFILIATE_HOST_HINTS)
        except Exception:
            return False

    def _extract_murl_from_affiliate_url(self, affiliate_url: str) -> str:
        """Extrait murl=... depuis une URL (quand présent)."""
        if not affiliate_url:
            return ""
        try:
            u = urlparse(affiliate_url)
            qs = parse_qs(u.query)
            m = qs.get("murl")
            if not m:
                return ""
            return unquote(m[0] or "").strip()
        except Exception:
            return ""

    def _looks_like_product_page(self, murl: str) -> bool:
        """Heuristique: id produit long (>=6 chiffres) dans l'URL => OK."""
        if not murl:
            return False
        return bool(self.PDT_PRODUCT_ID_RE.search(murl))

    def _validate_product_page_network(self, murl: str) -> bool:
        """
        Valide que la page semble encore être une fiche produit (pas redirect vers marque/home).
        - HEAD murl (follow_redirects)
        - accepte si url finale contient encore un id produit long
        """
        try:
            r = httpx.head(
                murl,
                timeout=self.HTTP_TIMEOUT,
                follow_redirects=True,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
                },
            )
            final_url = str(r.url) if getattr(r, "url", None) else murl
            if r.status_code >= 400:
                return False
            return bool(self.PDT_PRODUCT_ID_RE.search(final_url))
        except Exception:
            return False

    # -------------------------
    # Safety helpers for PostgREST
    # -------------------------
    def _strip_accents(self, s: str) -> str:
        s = s or ""
        return "".join(
            c for c in unicodedata.normalize("NFD", s)
            if unicodedata.category(c) != "Mn"
        )

    def _normalize_kw_for_ilike(self, kw: str) -> str:
        """
        Token safe pour PostgREST ilike:
        - pas d'accents
        - pas d'espaces (on garde UNIQUEMENT le 1er mot)
        - alnum + tiret seulement
        """
        kw = (kw or "").strip().lower()
        if not kw:
            return ""
        kw = self._strip_accents(kw)
        kw = kw.replace("’", "'")
        kw = kw.split()[0]
        kw = re.sub(r"[^a-z0-9\-]", "", kw)
        if len(kw) > self.MAX_TOKEN_LEN:
            kw = kw[: self.MAX_TOKEN_LEN]
        return kw

    # -------------------------
    # Image cache (Supabase Storage)
    # -------------------------
    def _ensure_cached_public_image(self, image_url: str, affiliate_row: Dict[str, Any]) -> str:
        """
        Retourne une URL publique Supabase Storage si possible (cache),
        sinon retombe sur l'URL originale.
        """
        if not image_url:
            return ""

        # Déjà une URL publique Supabase Storage
        if "supabase.co/storage/v1/object/public" in image_url:
            url = image_url.strip()
            return url[:-1] if url.endswith("?") else url

        try:
            product_id = str(affiliate_row.get("product_id") or "")
            name = str(affiliate_row.get("product_name") or "")
            key_seed = f"{product_id}|{name}|{image_url}"
            h = hashlib.sha256(key_seed.encode("utf-8")).hexdigest()[:24]

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

            # 1) Si existe déjà
            try:
                public = bucket.get_public_url(object_path)
                public_url = ""
                if isinstance(public, dict) and public.get("publicUrl"):
                    public_url = public["publicUrl"]
                elif isinstance(public, str) and public.strip():
                    public_url = public

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

            # 2) Télécharger l'image (anti-hotlink)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
                "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
                "Referer": "https://www.placedestendances.com/",
                "Origin": "https://www.placedestendances.com",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
            }
            r = httpx.get(image_url, headers=headers, timeout=20.0, follow_redirects=True)
            r.raise_for_status()

            content_type = (r.headers.get("content-type", "") or "").strip()
            data = r.content
            if not data or len(data) < 200:
                return image_url

            # 3) Upload (upsert)
            bucket.upload(
                path=object_path,
                file=data,
                file_options={
                    "content-type": content_type or f"image/{ext}",
                    "upsert": True,
                },
            )

            # 4) URL publique
            public = bucket.get_public_url(object_path)
            public_url = ""
            if isinstance(public, dict) and public.get("publicUrl"):
                public_url = public["publicUrl"]
            elif isinstance(public, str) and public.strip():
                public_url = public

            public_url = (public_url or "").strip()
            if public_url.endswith("?"):
                public_url = public_url[:-1]

            return public_url or image_url

        except Exception as e:
            print(f"⚠️ Image cache failed: {e}")
            return image_url

    # -------------------------
    # Private: AFFILIATE MATCH (VIEW active_affiliate_products)
    # -------------------------
    def _find_affiliate_products(
        self, piece_title: str, spec: str, category: str, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Récupère des candidats via keywords + fallback.
        ✅ Aligné sur active_affiliate_products:
        - product_name (texte principal)
        - keywords (fallback texte)
        - primary_category / secondary_category (filtres)
        - buy_url (lien tracké)
        """
        kws = self._extract_keywords(piece_title, spec)

        select_fields = ",".join(
            [
                "merchant_id",
                "sid",
                "product_id",
                "sku",
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
                "keywords",
                "is_deleted",
                "last_seen_at",
                "updated_at",
            ]
        )

        collected: List[Dict[str, Any]] = []
        seen = set()

        def _add_rows(rows: List[Dict[str, Any]]) -> None:
            nonlocal collected, seen
            for row in rows or []:
                # clé de dédup: buy_url puis product_id
                key = (row.get("buy_url") or "").strip() or (row.get("product_id") or "").strip()
                if not key:
                    key = hashlib.sha256((row.get("image_url") or "").encode("utf-8")).hexdigest()[:12]
                if key in seen:
                    continue
                seen.add(key)
                collected.append(row)
                if len(collected) >= limit:
                    return

        # Catégories: on reste simple (colonne réelle: secondary_category / primary_category)
        category_filters = {
            "tops": ["top", "tops", "maille", "knitwear", "blouse", "chemise", "pull"],
            "bottoms": ["bottom", "bottoms", "pantal", "jean", "jupe", "short"],
            "dresses_playsuits": ["dress", "dresses", "robe", "combi"],
            "outerwear": ["outerwear", "veste", "manteau", "blazer", "trench"],
            "swim_lingerie": ["swim", "swimwear", "underwear", "lingerie", "maillot"],
            "shoes": ["footwear", "chauss", "shoe", "shoes", "bott", "sandale", "basket"],
            "accessories": ["accessor", "accessories", "sac", "bag", "ceinture", "bijou"],
        }

        def _base_query():
            # active_affiliate_products = is_deleted = false déjà dans la vue, mais on peut garder safe
            q = self.client.table("active_affiliate_products").select(select_fields)

            # Filtre catégorie (OR sur primary + secondary)
            pats = category_filters.get(category, [])
            if pats:
                ors = []
                for p in pats[:8]:
                    tok = self._normalize_kw_for_ilike(p)
                    if not tok:
                        continue
                    ors.append(f"secondary_category.ilike.%{tok}%")
                    ors.append(f"primary_category.ilike.%{tok}%")
                if ors:
                    q = q.or_(",".join(ors))
            return q

        def _query_kw(q, kw_token: str):
            """
            1) product_name only
            2) product_name OR keywords
            """
            try:
                resp = q.ilike("product_name", f"%{kw_token}%").limit(min(20, limit)).execute()
                return getattr(resp, "data", None) or []
            except Exception as e:
                print(f"⚠️ product_name-only failed (kw={kw_token!r}) : {e}")

            try:
                resp = (
                    q.or_(f"product_name.ilike.%{kw_token}%,keywords.ilike.%{kw_token}%")
                    .limit(min(20, limit))
                    .execute()
                )
                return getattr(resp, "data", None) or []
            except Exception as e:
                print(f"⚠️ product_name+keywords failed (kw={kw_token!r}) : {e}")
                return []

        # 1) Queries par mots-clés
        for kw in kws[:4]:
            if len(collected) >= limit:
                break

            kw2 = self._normalize_kw_for_ilike(kw)
            if len(kw2) < 3:
                continue

            try:
                q = _base_query()
                data = _query_kw(q, kw2)
                _add_rows(data)
            except Exception as e:
                print(f"⚠️ Affiliate match kw failed ({kw2}): {e}")

        # 2) Fallback sur titre complet si besoin
        if len(collected) < 3 and piece_title:
            safe_title = self._normalize_kw_for_ilike(piece_title)
            if safe_title:
                try:
                    q = _base_query()
                    data = _query_kw(q, safe_title)
                    _add_rows(data)
                except Exception as e:
                    print(f"⚠️ Affiliate match title fallback failed ({safe_title}): {e}")

        return collected[:limit]

    def _extract_keywords(self, piece_title: str, spec: str) -> List[str]:
        text = f"{piece_title} {spec}".lower()
        text = re.sub(r"[^a-zàâçéèêëîïôûùüÿñæœ0-9\s-]", " ", text)
        text = re.sub(r"\s{2,}", " ", text).strip()

        stop = set(
            [
                "a", "à", "au", "aux", "de", "des", "du", "en", "et", "ou",
                "un", "une", "avec", "pour", "la", "le", "les", "d", "l",
                "sur", "dans", "sans", "style",
                "matiere", "matières", "coton", "laine", "viscose", "soie",
            ]
        )

        tokens = [t.strip() for t in text.split() if t.strip()]
        tokens = [t for t in tokens if t not in stop and len(t) >= 3]

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
    # Private: VISUELS FALLBACK
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
