# app/services/style_visuals_selector.py
import os
from typing import List, Dict, Any
from supabase import create_client
from math import floor

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

def _allocate_counts(style_mix: List[Dict[str, Any]], total: int = 9) -> List[Dict[str, Any]]:
    """
    style_mix: [{"style":"Minimaliste","pct":70}, ...]
    Retour: [{"style":"Minimaliste","n":6}, {"style":"Romantique","n":3}]
    """
    cleaned = []
    for s in (style_mix or []):
        if not isinstance(s, dict):
            continue
        name = (s.get("style") or "").strip()
        pct = s.get("pct", 0)
        try:
            pct = float(pct)
        except Exception:
            pct = 0
        if name and pct > 0:
            cleaned.append({"style": name, "pct": pct})

    if not cleaned:
        return [{"style": "Casual", "n": total}]

    # base: floors
    base = []
    used = 0
    for item in cleaned:
        n = int(floor((item["pct"] / 100.0) * total))
        base.append({"style": item["style"], "pct": item["pct"], "n": n})
        used += n

    # distribuer le reste selon les plus grosses décimales
    remainder = total - used
    if remainder > 0:
        fracs = []
        for item in cleaned:
            raw = (item["pct"] / 100.0) * total
            fracs.append((raw - floor(raw), item["style"]))
        fracs.sort(reverse=True)  # plus grosses décimales d'abord

        # si égalité, ça reste stable (ordre)
        idx_map = {b["style"]: i for i, b in enumerate(base)}
        for _, st in fracs:
            if remainder <= 0:
                break
            base[idx_map[st]]["n"] += 1
            remainder -= 1

    # garantir au moins 1 visuel pour les styles présents si total le permet
    # (optionnel, mais utile pour éviter 0 si pct faible)
    for b in base:
        if b["n"] == 0 and total >= len(base):
            b["n"] = 1
    # re-normaliser si on a dépassé total
    while sum(b["n"] for b in base) > total:
        # enlever 1 au plus gros n
        base.sort(key=lambda x: x["n"], reverse=True)
        for b in base:
            if b["n"] > 1:
                b["n"] -= 1
                break

    # trier par pct décroissant (dominant d'abord)
    base.sort(key=lambda x: x["pct"], reverse=True)
    return [{"style": b["style"], "n": b["n"]} for b in base if b["n"] > 0]


def get_style_visuals_for_style_mix(style_mix: List[Dict[str, Any]], season: str = "all", total: int = 9) -> List[Dict[str, Any]]:
    """
    Retourne une liste de 9 visuels répartis selon les %.
    """
    plan = _allocate_counts(style_mix, total=total)

    out: List[Dict[str, Any]] = []
    for p in plan:
        n = p["n"]
        if n <= 0:
            continue
        chunk = get_style_visuals_for_style(style_label=p["style"], season=season, limit=n)
        out.extend(chunk)

    # si jamais un style manque en DB, compléter avec le dominant
    if len(out) < total:
        dominant = plan[0]["style"] if plan else "Casual"
        out.extend(get_style_visuals_for_style(style_label=dominant, season=season, limit=total - len(out)))

    return out[:total]
