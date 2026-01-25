# app/services/style_visuals_selector.py
import os
from typing import List, Dict, Any
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()

# ✅ fallback: si pas de SERVICE_ROLE en prod, on tente SUPABASE_KEY / SUPABASE_ANON_KEY
SUPABASE_KEY = (
    os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    or os.getenv("SUPABASE_KEY", "").strip()
    or os.getenv("SUPABASE_ANON_KEY", "").strip()
)

# ⚠️ dans ta table, la "catégorie" est stockée dans la colonne `label`
# et elle est en slug (boheme, casual, etc.)
_STYLE_SLUG_MAP = {
    "minimaliste": "minimaliste",
    "style minimaliste": "minimaliste",
    "classique": "classique",
    "style classique / intemporel": "classique",
    "chic": "chic",
    "style chic / élégant": "chic",
    "casual": "casual",
    "style casual / décontracté": "casual",
    "moderne": "moderne",
    "style moderne / contemporain": "moderne",
    "romantique": "romantique",
    "style romantique": "romantique",
    "boheme": "boheme",
    "bohème": "boheme",
    "style bohème": "boheme",
    "style boheme": "boheme",
    "sportswear": "sportswear",
    "style sporty chic": "sportswear",
    "rock": "rock",
    "style rock": "rock",
    "vintage": "vintage",
    "style vintage": "vintage",
    "streetwear": "casual",
    "style urbain / streetwear": "casual",
}

def normalize_style_for_db(style_label: str) -> str:
    s = (style_label or "").strip().lower()
    if not s:
        return "casual"

    if s in _STYLE_SLUG_MAP:
        return _STYLE_SLUG_MAP[s]

    # heuristiques
    if "streetwear" in s or "urbain" in s:
        return "casual"
    if "sport" in s:
        return "sportswear"
    if "class" in s or "intemp" in s:
        return "classique"
    if "chic" in s or "élég" in s or "eleg" in s:
        return "chic"
    if "minim" in s:
        return "minimaliste"
    if "roman" in s:
        return "romantique"
    if "boh" in s:
        return "boheme"
    if "vint" in s:
        return "vintage"
    if "rock" in s:
        return "rock"
    if "modern" in s or "contemp" in s:
        return "moderne"
    if "casual" in s or "décontract" in s or "decontract" in s:
        return "casual"
    return "casual"

def _client():
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError("SUPABASE_URL / SUPABASE_KEY manquants (SERVICE_ROLE_KEY ou ANON_KEY)")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def get_style_visuals_for_style(style_label: str, season: str = "all", limit: int = 9) -> List[Dict[str, Any]]:
    """
    Retourne [{url,label}, ...] ordonné par slot.
    Table: public.style_images(season, slot, label, image_url)
    - `label` = slug de style (boheme, casual, ...)
    """
    style_slug = normalize_style_for_db(style_label)

    sb = _client()
    res = (
        sb.table("style_images")
        .select("slot,label,image_url,season")
        .eq("season", season)
        .eq("label", style_slug)           # ✅ filtre sur la bonne colonne
        .order("slot", desc=False)
        .limit(limit)
        .execute()
    )

    rows = res.data or []
    out: List[Dict[str, Any]] = []

    for r in rows:
        url = (r.get("image_url") or "").strip()
        # caption optionnel: tu peux mettre un libellé plus friendly si tu veux
        caption = (r.get("label") or "").strip()
        out.append({"url": url, "label": caption})

    return out
