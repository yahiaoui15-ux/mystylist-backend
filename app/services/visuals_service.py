from functools import lru_cache
from typing import Dict, Optional
from app.utils.supabase_client import supabase
from typing import List, Any

class VisualsService:
    """
    Fournit les URLs des visuels fallback depuis la table Supabase `visuels`.
    Mapping: visuels.nom_simplifie -> visuels.url_image
    """

    @lru_cache(maxsize=1)
    def _load_map(self) -> Dict[str, str]:
        client = supabase.get_client()
        resp = client.table("visuels").select("nom_simplifie,url_image").execute()
        data = resp.data or []
        out: Dict[str, str] = {}
        for row in data:
            k = self._slugify_key(row.get("nom_simplifie") or "")
            v = (row.get("url_image") or "").strip()
            if k and v:
                out[k] = v
        return out

    def get_url(self, visual_key: str) -> Optional[str]:
        if not visual_key:
            return None
        vk = self._slugify_key(visual_key)
        return self._load_map().get(vk)



    def _slugify_key(self, s: str) -> str:
        """
        Normalisation légère pour matcher nom_simplifie.
        Adapte si tes clés Supabase ont une convention différente.
        """
        s = (s or "").strip().lower()
        s = s.replace("’", "'")
        # espaces -> underscore
        s = "_".join(s.split())
        return s

    def fetch_visuals_for_category(self, category_name: str, recommandes: list) -> list:
        """
        Enrichit les items recommandés avec image_url depuis Supabase `visuels`.
        - recommandes: liste de strings ou dicts
        Retourne une liste de dicts homogène.
        """
        out = []
        for item in recommandes or []:
            if isinstance(item, str):
                label = item.strip()
                key = self._slugify_key(label)
                out.append({
                    "label": label,
                    "image_url": self.get_url(key)
                })
            elif isinstance(item, dict):
                label = (item.get("label") or item.get("name") or item.get("titre") or "").strip()
                if not label:
                    # si pas de label, on garde l'item tel quel
                    out.append(item)
                    continue
                key = self._slugify_key(item.get("visual_key") or label)
                item2 = dict(item)
                item2["label"] = label
                item2["image_url"] = item2.get("image_url") or self.get_url(key)
                out.append(item2)
            else:
                out.append({"label": str(item), "image_url": None})
        return out

visuals_service = VisualsService()
