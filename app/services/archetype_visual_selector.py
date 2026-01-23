from typing import Dict, List, Optional
import re

from app.utils.supabase_client import supabase  # ton wrapper


TARGET_COUNTS = {
    "silhouette": 3,
    "situation": 3,
    "detail": 2,
    "ambiance": 1,
}

TYPE_ORDER = ["silhouette", "situation", "detail", "ambiance"]


def _clean_url(url: str) -> str:
    # tes URLs finissent parfois par "?" -> certains renderers n'aiment pas
    return (url or "").rstrip("?").strip()


def _auto_label_from_url(url: str) -> str:
    """
    Fabrique un label à partir du filename.
    Ex: situation__p1__04__guerriere-metro-mouvement.webp -> "Metro mouvement"
    """
    filename = url.split("/")[-1].split("?")[0]
    filename = re.sub(r"\.(webp|png|jpg|jpeg)$", "", filename, flags=re.I)

    parts = filename.split("__")
    raw = parts[3] if len(parts) >= 4 else filename  # ex: guerriere-metro-mouvement

    raw = re.sub(r"^(guerriere|reine|romantique|sage|mystique|visionnaire)-", "", raw, flags=re.I)
    label = raw.replace("-", " ").strip()
    if not label:
        return "—"
    return label[0].upper() + label[1:]


def _fetch_rows_for_archetype(client, archetype: str) -> List[dict]:
    return (
        client.table("archetype_visuals")
        .select("archetype, visual_type, image_url, priority, sort_order, is_fallback, is_active")
        .eq("archetype", archetype)
        .eq("is_active", True)
        .order("priority", desc=True)
        .order("sort_order", desc=False)
        .execute()
        .data
    ) or []


def _fetch_rows_global(client) -> List[dict]:
    return (
        client.table("archetype_visuals")
        .select("archetype, visual_type, image_url, priority, sort_order, is_fallback, is_active")
        .eq("is_active", True)
        .order("priority", desc=True)
        .order("sort_order", desc=False)
        .execute()
        .data
    ) or []


def get_style_visuals_for_archetype(
    archetype: str,
    fallback_archetype: Optional[str] = None,
) -> List[Dict[str, str]]:
    """
    Retourne EXACTEMENT 9 items:
    3 silhouettes, 3 situations, 2 details, 1 ambiance.
    Si manque: complète avec d'autres visuels du même archétype.
    Si toujours manque: fallback_archetype (optionnel) puis global actifs.
    """
    client = supabase.get_client()
    if client is None:
        return []

    rows = _fetch_rows_for_archetype(client, archetype)

    if not rows and fallback_archetype:
        rows = _fetch_rows_for_archetype(client, fallback_archetype)

    if not rows:
        rows = _fetch_rows_global(client)

    # Grouping par type
    by_type: Dict[str, List[dict]] = {t: [] for t in TYPE_ORDER}
    for r in rows:
        vt = (r.get("visual_type") or "").strip().lower()
        url = r.get("image_url")
        if vt in by_type and url:
            by_type[vt].append(r)

    chosen: List[Dict[str, str]] = []
    used_urls = set()
    selected_by_type = {t: 0 for t in TYPE_ORDER}

    # 1) Respect quotas
    for t in TYPE_ORDER:
        for r in by_type[t]:
            if selected_by_type[t] >= TARGET_COUNTS[t]:
                break
            url = _clean_url(r.get("image_url", ""))
            if not url or url in used_urls:
                continue
            chosen.append({"url": url, "label": _auto_label_from_url(url)})
            used_urls.add(url)
            selected_by_type[t] += 1

    # 2) Compléter jusqu’à 9
    if len(chosen) < 9:
        for t in TYPE_ORDER:
            for r in by_type[t]:
                if len(chosen) >= 9:
                    break
                url = _clean_url(r.get("image_url", ""))
                if not url or url in used_urls:
                    continue
                chosen.append({"url": url, "label": _auto_label_from_url(url)})
                used_urls.add(url)

    return chosen[:9]
