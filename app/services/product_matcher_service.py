from typing import Dict, Any, List, Optional
import re
import hashlib
import os
import httpx

from app.utils.supabase_client import supabase


class ProductMatcherService:
    """
    Match une pièce IA (piece_title/spec/visual_key) vers:
    1) un produit affilié (VIEW SQL normalisée: pdt_products)
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

        affiliate = self._find_affiliate_product(piece_title=piece_title, spec=spec, category=category)
        if affiliate:
            raw_img = affiliate.get("image_url", "") or ""
            safe_img = self._ensure_cached_public_image(raw_img, affiliate)

            return {
                "image_url": safe_img,
                "product_url": affiliate.get("product_url", "") or "",
                "source": "affiliate",
                "title": affiliate.get("title", "") or piece_title,
                "brand": affiliate.get("brand", "") or "",
                "price": str(affiliate.get("price", "") or ""),
            }

        visual = self._find_visual_by_key(visual_key=visual_key, category=category)
        if visual:
            return {
                "image_url": visual.get("url_image", "") or "",
                "product_url": "",
                "source": "visual",
                "title": piece_title,
                "brand": "",
                "price": "",
            }

        return {
            "image_url": "",
            "product_url": "",
            "source": "none",
            "title": piece_title,
            "brand": "",
            "price": "",
        }

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
            return image_url

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

            # 1) Si le fichier existe déjà, on renvoie l'URL publique
            try:
                public = bucket.get_public_url(object_path)
                # get_public_url renvoie une string ou dict selon versions; on normalise
                if isinstance(public, dict) and public.get("publicUrl"):
                    return public["publicUrl"]
                if isinstance(public, str) and public.strip():
                    return public
            except Exception:
                pass

            # 2) Télécharger l'image
            headers = {
                "User-Agent": "Mozilla/5.0",
                "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
            }
            r = httpx.get(image_url, headers=headers, timeout=20.0, follow_redirects=True)
            r.raise_for_status()

            content_type = r.headers.get("content-type", "")
            data = r.content
            if not data or len(data) < 200:
                return image_url

            # 3) Upload (upsert pour éviter erreurs)
            bucket.upload(
                path=object_path,
                file=data,
                file_options={
                    "content-type": content_type or f"image/{ext}",
                    "upsert": "true",
                },
            )

            public = bucket.get_public_url(object_path)
            if isinstance(public, dict) and public.get("publicUrl"):
                return public["publicUrl"]
            if isinstance(public, str) and public.strip():
                return public

            return image_url

        except Exception as e:
            print(f"⚠️ Image cache failed: {e}")
            return image_url

    # -------------------------
    # Private: AFFILIATE MATCH (VIEW pdt_products)
    # -------------------------
    def _find_affiliate_product(self, piece_title: str, spec: str, category: str) -> Optional[Dict[str, Any]]:
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

        for kw in kws[:4]:
            try:
                resp = (
                    self.client
                    .table("pdt_products")
                    .select(select_fields)
                    .or_(f"title.ilike.%{kw}%,description_short.ilike.%{kw}%")
                    .limit(1)
                    .execute()
                )
                data = getattr(resp, "data", None) or []
                if data:
                    return data[0]
            except Exception as e:
                print(f"⚠️ Affiliate match kw failed ({kw}): {e}")

        if piece_title:
            try:
                safe_title = piece_title.replace("%", "").strip()
                resp = (
                    self.client
                    .table("pdt_products")
                    .select(select_fields)
                    .or_(f"title.ilike.%{safe_title}%,description_short.ilike.%{safe_title}%")
                    .limit(1)
                    .execute()
                )
                data = getattr(resp, "data", None) or []
                if data:
                    return data[0]
            except Exception as e:
                print(f"⚠️ Affiliate match title fallback failed: {e}")

        return None

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
