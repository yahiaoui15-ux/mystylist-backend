from typing import Dict, Any, List, Optional
import re

from app.supabase_client import supabase



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
            return {
                "image_url": affiliate.get("image_url", "") or "",
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
        Heuristique simple:
        - extrait 2-8 mots clés de piece_title/spec
        - tente plusieurs requêtes Supabase sur la VIEW "pdt_products":
            a) title ilike %kw% OR description_short ilike %kw%
            b) fallback: title ilike %piece_title%
        - retourne 1 best match
        """
        kws = self._extract_keywords(piece_title, spec)

        # Champs de la VIEW pdt_products
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
                    .limit(1)
                    .execute()
                )
                data = getattr(resp, "data", None) or []
                if data:
                    return data[0]
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
