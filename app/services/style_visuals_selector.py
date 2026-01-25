# app/services/style_visuals_selector.py
import os
from typing import List, Dict, Any

from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()

_BUCKET_PUBLIC_BASE = os.getenv("STYLE_IMAGES_PUBLIC_BASE_URL", "").strip()
# optionnel : si vide, on utilisera directement image_url depuis la table

_STYLE_MAP = {
    "style minimaliste": "Minimaliste",
    "style classique / intemporel": "Classique",
    "style chic / élégant": "Chic",
    "style casual / décontracté": "Casual",
    "style moderne / contemporain": "Moderne",
    "style romantique": "Romantique",
    "style bohème": "Bohème",
    "style boheme": "Bohème",
    "style sporty chic": "Sportswear",
    "style rock": "Rock",
    "style vintage": "Vintage",
    "style urbain / streetwear": "Casual",  # ✅ confirmé
}

def normalize_style_for_db(style_label: str) -> str:
    s = (style_label or "").strip().lower()
    if not s:
        return "Casual"
    # match exact map
    if s in _STYLE_MAP:
        return _STYLE_MAP[s]
    # fallback heuristique
    if "streetwear" in s or "urbain" in s:
        return "Casual"
    if "sport" in s:
        return "Sportswear"
    if "class" in s or "intemp" in s:
        return "Classique"
    if "chic" in s or "élég" in s or "eleg" in s:
        return "Chic"
    if "minim" in s:
        return "Minimaliste"
    if "roman" in s:
        return "Romantique"
    if "boh" in s:
        return "Bohème"
    if "vint" in s:
        return "Vintage"
    if "rock" in s:
        return "Rock"
    if "modern" in s or "contemp" in s:
        return "Moderne"
    if "casual" in s or "décontract" in s or "decontract" in s:
        return "Casual"
    return "Casual"

def _client():
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise RuntimeError("SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY manquants")
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def get_style_visuals_for_style(style_label: str, season: str = "all", limit: int = 9) -> List[Dict[str, Any]]:
    """
    Retourne [{url,label}, ...] ordonné par slot.
    """
    style_db = normalize_style_for_db(style_label)

    sb = _client()
    res = (
        sb.table("style_images")
        .select("slot,label,image_url,style,season")
        .eq("season", season)
        .ilike("style", style_db)   # tolère casse
        .order("slot", desc=False)
        .limit(limit)
        .execute()
    )

    rows = res.data or []
    out = []
    for r in rows:
        url = r.get("image_url") or ""
        label = r.get("label") or ""
        # si tu veux reconstruire l'URL depuis un base public, tu peux :
        # if _BUCKET_PUBLIC_BASE and not url:
        #     url = f"{_BUCKET_PUBLIC_BASE}/{style_db.lower()}/{season}/slot-{int(r.get('slot')):02d}"
        out.append({"url": url, "label": label})

    return out
