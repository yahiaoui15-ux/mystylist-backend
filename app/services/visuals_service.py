from functools import lru_cache
from typing import Dict, Optional
from app.utils.supabase_client import supabase


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
            k = (row.get("nom_simplifie") or "").strip()
            v = (row.get("url_image") or "").strip()
            if k and v:
                out[k] = v
        return out

    def get_url(self, visual_key: str) -> Optional[str]:
        if not visual_key:
            return None
        vk = visual_key.strip()
        return self._load_map().get(vk)


visuals_service = VisualsService()
