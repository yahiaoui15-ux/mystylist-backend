import re
import unicodedata
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
        s = (s or "").strip().lower()
        s = s.replace("’", "'")

        # enlever accents
        s = unicodedata.normalize("NFKD", s)
        s = "".join([c for c in s if not unicodedata.combining(c)])

        # tout ce qui n'est pas alphanum -> underscore (gère espaces, tirets, etc.)
        s = re.sub(r"[^a-z0-9]+", "_", s)

        # underscores multiples
        s = re.sub(r"_+", "_", s).strip("_")
        return s

    def fetch_visuals_for_category(self, category_name: str, recommandes: list) -> list:
        out = []
        for item in recommandes or []:

            if isinstance(item, str):
                label = item.strip()
                key = self._slugify_key(label)
                out.append({
                    "cut_display": label,
                    "why": "",
                    "visual_key": key,
                    "image_url": self.get_url(key) or ""
                })
                continue

            if isinstance(item, dict):
                # ✅ support OpenAI Part2: cut_display
                label = (
                    item.get("cut_display")
                    or item.get("label")
                    or item.get("name")
                    or item.get("titre")
                    or ""
                ).strip()

                item2 = dict(item)
                if not label:
                    # on garde mais on garantit la clé
                    item2.setdefault("image_url", "")
                    out.append(item2)
                    continue

                key_source = item2.get("visual_key") or label
                key = self._slugify_key(key_source)

                item2["cut_display"] = item2.get("cut_display") or label
                item2["visual_key"] = item2.get("visual_key") or key
                item2["image_url"] = item2.get("image_url") or (self.get_url(key) or "")
                out.append(item2)
                continue

            out.append({"cut_display": str(item), "why": "", "visual_key": "", "image_url": ""})

        return out

visuals_service = VisualsService()
