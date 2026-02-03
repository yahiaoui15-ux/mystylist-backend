from typing import Dict, Any, List, Optional
import re
import hashlib
import os
import httpx
from urllib.parse import urlparse, parse_qs, unquote

from app.utils.supabase_client import supabase


class ProductMatcherService:
    """
    Match une pièce IA (piece_title/spec/visual_key) vers:
    1) un produit affilié (VIEW SQL normalisée: pdt_products)
       - récupère jusqu'à 20 candidats
       - filtre les URLs dont le murl ne ressemble pas à une page produit
       - renvoie 1 produit principal + 2 alternatives (Option A)
    2) sinon un visuel pédagogique de "visuels"
    + Cache images affiliées dans Supabase Storage pour compat PDFMonkey
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

    AFFILIATE_IMAGE_BUCKET = os.getenv("AFFILIATE_IMAGE_BUCKET", "affiliate-cache")

    # Heuristique "page produit" PlaceDesTendances :
    # on accepte si murl contient un id numérique "long" (>=6 chiffres) quelque part (ex: 9280136)
    PDT_PRODUCT_ID_RE = re.compile(r"(\d{6,})", re.IGNORECASE)

    # Optionnel: validation réseau de la page produit (réduit les "pages marque" si feed obsolète)
    # Active uniquement sur le produit principal (pour limiter coûts/latence)
    VALIDATE_MURL_NETWORK = os.getenv("PDT_VALIDATE_MURL_NETWORK", "1").strip() in ("1", "true", "True", "yes", "YES")

    # Filtre strict femmes (évite homme/enfant/unisex)
    STRICT_FEMALE_ONLY = os.getenv("PDT_STRICT_FEMALE_ONLY", "1").strip() in ("1", "true", "True", "yes", "YES")

    # Timeout réseau
    HTTP_TIMEOUT = float(os.getenv("PDT_HTTP_TIMEOUT", "8.0").strip() or "8.0")

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

        # 1) Affiliés (Option A: 3 candidats)
        candidates = self._find_affiliate_products(piece_title=piece_title, spec=spec, category=category, limit=20)
        top3 = self._pick_top3_valid_candidates(candidates, validate_network=self.VALIDATE_MURL_NETWORK)

        if top3:
            main = top3[0]
            raw_img = main.get("image_url", "") or ""
            safe_img = self._ensure_cached_public_image(raw_img, main)

            # Labels "propres" pour Option 2/3
            alt1 = top3[1] if len(top3) > 1 else None
            alt2 = top3[2] if len(top3) > 2 else None

            return {
                "image_url": safe_img,
                "product_url": main.get("product_url", "") or "",
                "source": "affiliate",
                "title": main.get("title", "") or piece_title,
                "brand": main.get("brand", "") or "",
                "price": str(main.get("price", "") or ""),

                # Option A: 2 alternatives sous forme de liens
                "alt1_url": (alt1.get("product_url") if alt1 else "") or "",
                "alt1_label": (self._format_alt_label(alt1) if alt1 else "") or "",
                "alt2_url": (alt2.get("product_url") if alt2 else "") or "",
                "alt2_label": (self._format_alt_label(alt2) if alt2 else "") or "",
            }

        # 2) Fallback visuel pédagogique
        visual = self._find_visual_by_key(visual_key=visual_key, category=category)
        if visual:
            return {
                "image_url": visual.get("url_image", "") or "",
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
    # Option A helpers
    # -------------------------
    def _format_alt_label(self, row: Optional[Dict[str, Any]]) -> str:
        if not row:
            return ""
        brand = (row.get("brand") or "").strip()
        price = row.get("price")
        title = (row.get("title") or "").strip()
        p = ""
        if price is not None and str(price).strip():
            p = f"{price}€"
        # Priorité : brand + prix, sinon title court
        if brand and p:
            return f"{brand} — {p}"
        if brand:
            return brand
        if title:
            return title[:48] + ("…" if len(title) > 48 else "")
        return "Alternative"

    def _pick_top3_valid_candidates(
        self,
        candidates: List[Dict[str, Any]],
        validate_network: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Filtre les candidats dont la destination (murl) n'a pas l'air d'une page produit.
        - Déduplique sur murl (évite les 2-3 alternatives identiques)
        - Optionnel: valide réseau UNIQUEMENT pour le candidat principal (réduit pages marque)
        Retourne au max 3.
        """
        out: List[Dict[str, Any]] = []
        seen_murl = set()

        for c in candidates or []:
            if not isinstance(c, dict):
                continue

            affiliate_url = (c.get("product_url") or "").strip()
            murl = self._extract_murl_from_affiliate_url(affiliate_url)

            if murl:
                # filtre heuristique id produit long
                if not self._looks_like_product_page(murl):
                    continue

                # dédup destination
                if murl in seen_murl:
                    continue
                seen_murl.add(murl)

            out.append(c)
            if len(out) >= 3:
                break

        # Validation réseau: uniquement sur le principal (index 0)
        if validate_network and out:
            murl0 = self._extract_murl_from_affiliate_url((out[0].get("product_url") or "").strip())
            if murl0:
                ok = self._validate_product_page_network(murl0)
                if not ok:
                    # si le principal est "mort"/redirige brand, on le retire
                    out = out[1:]

        return out[:3]

    def _extract_murl_from_affiliate_url(self, affiliate_url: str) -> str:
        """
        Extrait murl=... depuis une URL LinkSynergy.
        Retourne une URL décodée (https://www.placedestendances.com/...).
        """
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
        """
        Heuristique simple et robuste :
        - si on voit un id produit long (>=6 chiffres) dans l'URL => OK
        - sinon => probablement page marque / listing => NOK
        """
        if not murl:
            return False
        return bool(self.PDT_PRODUCT_ID_RE.search(murl))

    def _validate_product_page_network(self, murl: str) -> bool:
        """
        Valide que la page semble encore être une fiche produit (pas redirect vers marque/home).
        Stratégie:
        - HEAD murl (follow_redirects)
        - accepte si url finale contient encore un id produit long
        """
        try:
            r = httpx.head(murl, timeout=self.HTTP_TIMEOUT, follow_redirects=True, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
            })
            final_url = str(r.url) if getattr(r, "url", None) else murl
            if r.status_code >= 400:
                return False
            # final doit conserver un id produit
            return bool(self.PDT_PRODUCT_ID_RE.search(final_url))
        except Exception:
            return False

    # -------------------------
    # Image cache (Supabase Storage)
    # -------------------------
    def _ensure_cached_public_image(self, image_url: str, affiliate_row: Dict[str, Any]) -> str:
        """
        Retourne une URL publique Supabase si possible (cache),
        sinon retombe sur l'URL originale.
        """
        if not image_url:
            return ""

        # Si c'est déjà une URL Supabase Storage publique, on ne retélécharge pas
        if "supabase.co/storage/v1/object/public" in image_url:
            # defensive: retire un éventuel "?" final
            url = image_url.strip()
            return url[:-1] if url.endswith("?") else url

        try:
            product_id = str(affiliate_row.get("product_id") or "")
            title = str(affiliate_row.get("title") or "")
            key_seed = f"{product_id}|{title}|{image_url}"
            h = hashlib.sha256(key_seed.encode("utf-8")).hexdigest()[:24]

            # Choix extension basique (jpg par défaut)
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

            # 1) Si le fichier existe déjà, renvoyer l'URL publique (avec check HTTP)
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
                    # Vérifie que l'objet existe vraiment (Range bytes=0-0)
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

            # 2) Télécharger l'image (anti-hotlink: referer/origin)
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

            # 3) Upload (upsert bool)
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
    # Private: AFFILIATE MATCH (VIEW pdt_products)
    # -------------------------
    def _find_affiliate_products(self, piece_title: str, spec: str, category: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Récupère une liste de candidats (jusqu'à `limit`) via keywords,
        en évitant les doublons, puis fallback sur le titre complet.
        Applique des filtres:
        - STRICT_FEMALE_ONLY: gender='female' + product_type ilike 'Femme%'
        - filtre "univers" par category (swim/shoes/accessories) via category_secondary/product_type
        """
        kws = self._extract_keywords(piece_title, spec)

        select_fields = ",".join([
            "product_id",
            "title",
            "brand",
            "price",
            "currency",
            "image_url",
            "product_url",
            "description_short",
            "category_primary",
            "category_secondary",
            "product_type",
            "color",
            "material",
            "gender",
        ])

        collected: List[Dict[str, Any]] = []
        seen_ids = set()

        def _add_rows(rows: List[Dict[str, Any]]) -> None:
            nonlocal collected, seen_ids
            for row in rows or []:
                pid = str(row.get("product_id") or "")
                if not pid:
                    pid = hashlib.sha256((row.get("product_url") or "").encode("utf-8")).hexdigest()[:12]
                if pid in seen_ids:
                    continue
                seen_ids.add(pid)
                collected.append(row)
                if len(collected) >= limit:
                    return

        # --- contraintes par category (filtres larges mais efficaces)
        # NB: avec Supabase query builder, on reste simple: on filtre sur category_secondary/product_type
        category_filters = {
            "swim_lingerie": {
                "category_secondary_ilike": ["%Swimwear%", "%Underwear%"],
                "product_type_ilike": ["%Maillot de bain%", "%Underwear%", "%Lingerie%"],
            },
            "shoes": {
                "category_secondary_ilike": ["%Footwear%"],
                "product_type_ilike": ["%Chauss%"],
            },
            "accessories": {
                "category_secondary_ilike": ["%Accessories%"],
                "product_type_ilike": ["%Access%"],
            },
            # tops/bottoms/dresses_playsuits/outerwear : on ne met pas de filtre trop agressif ici
        }

        def _base_query():
            q = self.client.table("pdt_products").select(select_fields)

            if self.STRICT_FEMALE_ONLY:
                # évite homme/enfant/unisex
                q = q.eq("gender", "female").ilike("product_type", "Femme%")

            # filtre univers si category connue
            f = category_filters.get(category)
            if f:
                ors = []
                for pat in f.get("category_secondary_ilike", []):
                    ors.append(f"category_secondary.ilike.{pat}")
                for pat in f.get("product_type_ilike", []):
                    ors.append(f"product_type.ilike.{pat}")
                if ors:
                    q = q.or_(",".join(ors))

            return q

        # 1) Queries par mots-clés
        for kw in kws[:4]:
            if len(collected) >= limit:
                break
            try:
                q = _base_query()
                resp = (
                    q.or_(f"title.ilike.%{kw}%,description_short.ilike.%{kw}%")
                    .limit(min(20, limit))
                    .execute()
                )
                data = getattr(resp, "data", None) or []
                _add_rows(data)
            except Exception as e:
                print(f"⚠️ Affiliate match kw failed ({kw}): {e}")

        # 2) Fallback sur titre complet si besoin
        if len(collected) < 3 and piece_title:
            try:
                safe_title = piece_title.replace("%", "").strip()
                q = _base_query()
                resp = (
                    q.or_(f"title.ilike.%{safe_title}%,description_short.ilike.%{safe_title}%")
                    .limit(min(20, limit))
                    .execute()
                )
                data = getattr(resp, "data", None) or []
                _add_rows(data)
            except Exception as e:
                print(f"⚠️ Affiliate match title fallback failed: {e}")

        return collected[:limit]

    def _extract_keywords(self, piece_title: str, spec: str) -> List[str]:
        text = f"{piece_title} {spec}".lower()
        text = re.sub(r"[^a-zàâçéèêëîïôûùüÿñæœ0-9\s-]", " ", text)
        text = re.sub(r"\s{2,}", " ", text).strip()

        stop = set([
            "a", "à", "au", "aux", "de", "des", "du", "en", "et", "ou", "un", "une", "avec", "pour",
            "la", "le", "les", "d", "l", "sur", "dans", "sans", "style", "matiere", "matières",
            "coton", "laine", "viscose", "soie",
        ])

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
                self.client
                .table("visuels")
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
                self.client
                .table("visuels")
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
