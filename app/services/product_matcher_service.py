# app/services/product_matcher_service.py
from typing import Dict, Any, List, Optional
import re
import hashlib
from urllib.parse import urlparse

import httpx

from app.utils.supabase_client import supabase


class ProductMatcherService:
    """
    Match une pièce IA (piece_title/spec/visual_key) vers:
    1) un produit affilié (VIEW SQL normalisée: pdt_products)
    2) sinon un visuel pédagogique de "visuels"
    """

    VISUELS_TYPE_MAP = {
        "tops": "haut",
        "bottoms": "bas",
        "dresses_playsuits": "robe",
        "outerwear": "haut",         # ou "veste" selon ta table visuels
        "swim_lingerie": "lingerie", # ou "maillot_lingerie"
        "shoes": "chaussures",
        "accessories": "accessoire",
    }

    # Mots-clés attendus par catégorie pour éviter les matches absurdes (robe -> basket, etc.)
    AFFILIATE_KEYWORDS_BY_CATEGORY = {
        "tops": ["blouse", "chemise", "top", "pull", "gilet", "tshirt", "t-shirt", "cardigan", "maille", "tee-shirt"],
        "bottoms": ["pantalon", "jean", "jupe", "short", "legging"],
        "dresses_playsuits": ["robe", "combinaison", "salopette"],
        "outerwear": ["manteau", "veste", "blazer", "trench", "parka"],
        "swim_lingerie": ["soutien", "culotte", "lingerie", "maillot", "bikini", "brassiere", "brassière"],
        "shoes": ["bottines", "escarpins", "baskets", "sandales", "boots", "mocassins", "derbies", "ballerines"],
        "accessories": ["sac", "ceinture", "collier", "boucles", "bracelet", "foulard", "écharpe", "chapeau", "bijou"],
    }

    def __init__(self):
        self.client = supabase.get_client()
        # Bucket Supabase Storage PUBLIC dans lequel tu caches les images affiliées
        # ⚠️ Mets le nom EXACT de ton bucket public
        self.public_bucket = "public-assets"

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
        """
        Retourne un dict standard:
        {
          image_url, product_url, source, title, brand, price
        }
        """
        piece_title = (piece.get("piece_title") or "").strip()
        spec = (piece.get("spec") or "").strip()
        visual_key = (piece.get("visual_key") or "").strip()

        # 1) Try affiliate match (via view pdt_products)
        affiliate = self._find_affiliate_product(piece_title=piece_title, spec=spec, category=category)
        if affiliate:
            raw_img = affiliate.get("image_url", "") or ""
            cached_img = self._cache_image_to_supabase(raw_img) if raw_img else ""

            return {
                "image_url": cached_img or raw_img or "",
                "product_url": affiliate.get("product_url", "") or "",
                "source": "affiliate",
                "title": affiliate.get("title", "") or piece_title,
                "brand": affiliate.get("brand", "") or "",
                "price": str(affiliate.get("price", "") or ""),
            }

        # 2) Fallback visuel table "visuels"
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

        # 3) Last resort
        return {
            "image_url": "",
            "product_url": "",
            "source": "none",
            "title": piece_title,
            "brand": "",
            "price": "",
        }

    # -------------------------
    # Private: AFFILIATE MATCH (VIEW pdt_products)
    # -------------------------
    def _find_affiliate_product(self, piece_title: str, spec: str, category: str) -> Optional[Dict[str, Any]]:
        """
        Amélioré:
        - récupère jusqu'à 10 candidats
        - score les candidats (cohérence catégorie + overlap mots)
        - retourne le meilleur si score > 0
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

        # 1) keyword tries
        for kw in kws[:4]:
            try:
                resp = (
                    self.client
                    .table("pdt_products")
                    .select(select_fields)
                    .or_(f"title.ilike.%{kw}%,description_short.ilike.%{kw}%")
                    .limit(10)
                    .execute()
                )
                data = getattr(resp, "data", None) or []
                if data:
                    best = max(data, key=lambda c: self._score_candidate(piece_title, spec, c, category))
                    if self._score_candidate(piece_title, spec, best, category) > 0:
                        return best
            except Exception as e:
                print(f"⚠️ Affiliate match kw failed ({kw}): {e}")

        # 2) fallback: full title
        if piece_title:
            try:
                safe_title = piece_title.replace("%", "").strip()
                resp = (
                    self.client
                    .table("pdt_products")
                    .select(select_fields)
                    .or_(f"title.ilike.%{safe_title}%,description_short.ilike.%{safe_title}%")
                    .limit(10)
                    .execute()
                )
                data = getattr(resp, "data", None) or []
                if data:
                    best = max(data, key=lambda c: self._score_candidate(piece_title, spec, c, category))
                    if self._score_candidate(piece_title, spec, best, category) > 0:
                        return best
            except Exception as e:
                print(f"⚠️ Affiliate match title fallback failed: {e}")

        return None

    def _score_candidate(self, piece_title: str, spec: str, cand: Dict[str, Any], category: str) -> int:
        """
        Score simple mais efficace:
        + overlap keywords
        + bonus si mots-clés catégorie présents
        - forte pénalité si incohérent avec la catégorie
        """
        title = (cand.get("title") or "").lower()
        desc = (cand.get("description_short") or "").lower()
        blob = f"{title} {desc}"

        score = 0

        # overlap mots
        for w in self._extract_keywords(piece_title, spec):
            if w and w in blob:
                score += 2

        expected = self.AFFILIATE_KEYWORDS_BY_CATEGORY.get(category, [])
        if expected:
            if any(k in blob for k in expected):
                score += 8
                # bonus si le titre contient un mot “très typant”
                for k in expected[:3]:
                    if k in title:
                        score += 3
            else:
                score -= 12  # pénalité forte si hors catégorie

        return score

    def _extract_keywords(self, piece_title: str, spec: str) -> List[str]:
        """
        Ex: "Blouse fluide à col V" -> ["col v","blouse","fluide",...]
        """
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
    # Private: CACHE IMAGES (fix PDFMonkey broken images)
    # -------------------------
    def _cache_image_to_supabase(self, image_url: str) -> str:
        """
        Télécharge l'image distante (CDN) et la ré-upload dans Supabase Storage public.
        Retourne l'URL publique Supabase, sinon fallback sur l'url originale.
        """
        if not image_url:
            return ""

        h = hashlib.sha1(image_url.encode("utf-8")).hexdigest()

        ext = ".jpg"
        path = urlparse(image_url).path.lower()
        if path.endswith(".png"):
            ext = ".png"
        elif path.endswith(".webp"):
            ext = ".webp"
        elif path.endswith(".jpeg"):
            ext = ".jpeg"

        filename = f"affiliate_cache/{h}{ext}"

        try:
            r = httpx.get(
                image_url,
                timeout=20,
                follow_redirects=True,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            r.raise_for_status()

            content_type = r.headers.get("content-type", "image/jpeg")

            # Supabase python: upload + upsert
            self.client.storage.from_(self.public_bucket).upload(
                filename,
                r.content,
                {"content-type": content_type, "upsert": "true"},
            )

            public_url = self.client.storage.from_(self.public_bucket).get_public_url(filename)
            return public_url or image_url
        except Exception as e:
            print(f"⚠️ Image cache failed: {e} url={image_url}")
            return image_url

    # -------------------------
    # Private: VISUELS FALLBACK
    # -------------------------
    def _find_visual_by_key(self, visual_key: str, category: str) -> Optional[Dict[str, Any]]:
        """
        Table: public.visuels
        Colonnes:
          - nom_simplifie (text)
          - type_vetement (text)
          - coupe (text)
          - url_image (text)
        """
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

            # retry sans filtre type_vetement
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
