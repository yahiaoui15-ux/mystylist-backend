"""
Style Pieces Selector v1.1
Sélectionne 10 pièces phares depuis style_piece_visuals
en fonction du profil stylistique et morphologique de la cliente.

Aucun appel OpenAI — scoring pur + commentaires template enrichis.
v1.1: commentaires plus personnalisés, référencent le mix de styles client,
      formules variées par pièce pour éviter la répétition.
"""

import json
import re
from typing import Any, Dict, List, Tuple

from app.utils.supabase_client import supabase


STYLE_LABEL_TO_TAG: Dict[str, str] = {
    "Style Classique / Intemporel": "classique",
    "Style Chic / Élégant": "chic",
    "Style Minimaliste": "minimaliste",
    "Style Casual / Décontracté": "casual",
    "Style Bohème": "boheme",
    "Style Romantique": "romantique",
    "Style Rock": "rock",
    "Style Vintage": "vintage",
    "Style Moderne / Contemporain": "moderne",
    "Style Sporty Chic": "sportswear",
    "Style Urbain / Streetwear": "sportswear",
    "Style Féminin Moderne": "moderne",
    "Style Naturel / Authentique": "boheme",
    "Style Artistique / Créatif": "rock",
    "Style Glamour": "chic",
    "Style Preppy": "classique",
    "Style Ethnique": "boheme",
    "Style Sexy Assumé": "moderne",
    "Classique": "classique",
    "Chic": "chic",
    "Minimaliste": "minimaliste",
    "Casual": "casual",
    "Bohème": "boheme",
    "Boheme": "boheme",
    "Romantique": "romantique",
    "Rock": "rock",
    "Vintage": "vintage",
    "Moderne": "moderne",
    "Sporty Chic": "sportswear",
    "Sportswear": "sportswear",
    "classique": "classique",
    "chic": "chic",
    "minimaliste": "minimaliste",
    "casual": "casual",
    "boheme": "boheme",
    "romantique": "romantique",
    "rock": "rock",
    "vintage": "vintage",
    "moderne": "moderne",
    "sportswear": "sportswear",
}

CATEGORY_TARGETS: Dict[str, int] = {
    "top":       2,
    "bottom":    2,
    "dress":     1,
    "outerwear": 1,
    "shoe":      2,
    "accessory": 2,
}

SCORE_STYLE_PRIMARY   = 30
SCORE_STYLE_SECONDARY = 15
SCORE_STYLE_TERTIARY  = 5
SCORE_MORPHO_MATCH    = 25
SCORE_FLATTERS_ZONE   = 8
SCORE_MINIMIZES_ZONE  = 8
SCORE_CONTEXT_TAG     = 4
SCORE_BASE_PRIORITY   = 0.10

STYLE_DISPLAY_LABELS: Dict[str, str] = {
    "minimaliste": "minimaliste",
    "chic":        "chic",
    "classique":   "classique",
    "moderne":     "moderne",
    "casual":      "casual",
    "boheme":      "bohème",
    "romantique":  "romantique",
    "rock":        "rock",
    "vintage":     "vintage",
    "sportswear":  "sporty chic",
}

MESSAGE_DISPLAY_LABELS: Dict[str, str] = {
    "pratique":    "pratique au quotidien",
    "sobre":       "sobre et épurée",
    "style":       "stylée sans effort",
    "feminin":     "féminine et affirmée",
    "raffine":     "raffinée",
    "moderne":     "moderne et actuelle",
    "decontracte": "décontractée avec allure",
    "classe":      "classe et soignée",
    "intemporel":  "intemporelle",
    "rebelle":     "rebelle et affirmée",
    "structure":   "structurée",
    "souple":      "souple et fluide",
    "equilibre":   "équilibrée",
    "fort":        "avec caractère",
    "doux":        "avec douceur",
    "libre":       "libre et naturelle",
    "urbain":      "urbaine et actuelle",
    "assure":      "assurée",
    "mode":        "dans l'air du temps",
    "retro":       "rétro chic",
    "naturel":     "naturelle",
    "detail":      "soignée dans les détails",
    "elegant":     "élégante",
    "polyvalent":  "polyvalente",
}

SITUATION_TO_CONTEXT: Dict[str, List[str]] = {
    "work":      ["travail", "city"],
    "events":    ["occasion", "city"],
    "weekends":  ["weekend", "quotidien"],
    "dating":    ["dating", "occasion"],
    "travel":    ["vacances", "weekend"],
    "family":    ["quotidien", "weekend"],
    "social":    ["city", "occasion"],
    "student":   ["quotidien", "city"],
    "remote":    ["quotidien"],
}

# Effets trop génériques pour les accessoires → ne pas afficher
GENERIC_EFFECTS = {"complete le look", "complète le look", "complete the look"}


class StylePiecesSelector:

    def __init__(self):
        self.client = supabase.get_client()

    # ─────────────────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _parse_jsonb(value: Any) -> List[str]:
        if isinstance(value, list):
            return [str(v).strip().lower() for v in value if v]
        if isinstance(value, str) and value.strip():
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return [str(v).strip().lower() for v in parsed if v]
            except Exception:
                pass
        return []

    @staticmethod
    def _normalize(s: str) -> str:
        s = (s or "").strip().lower()
        for fr, en in [
            ('é','e'),('è','e'),('ê','e'),('ë','e'),
            ('à','a'),('â','a'),('î','i'),('ï','i'),
            ('ô','o'),('û','u'),('ù','u'),('ü','u'),('ç','c'),
        ]:
            s = s.replace(fr, en)
        return s

    @staticmethod
    def _zones_overlap(client_zones: List[str], piece_zones: List[str]) -> List[str]:
        matches = []
        for cz in client_zones:
            cz_norm = StylePiecesSelector._normalize(cz)
            for pz in piece_zones:
                pz_norm = StylePiecesSelector._normalize(pz)
                if cz_norm in pz_norm or pz_norm in cz_norm:
                    if cz not in matches:
                        matches.append(cz)
                    break
        return matches

    @staticmethod
    def _map_style_mix_to_tags(style_mix: List[Dict[str, Any]]) -> List[Tuple[str, int]]:
        result = []
        for item in style_mix or []:
            if not isinstance(item, dict):
                continue
            label = (item.get("style") or "").strip()
            pct = int(item.get("pct") or 0)
            if pct <= 0:
                continue
            tag = STYLE_LABEL_TO_TAG.get(label)
            if not tag:
                norm = StylePiecesSelector._normalize(label)
                norm = re.sub(r"^style\s+", "", norm)
                norm = re.sub(r"\s*/.*$", "", norm).strip()
                tag = norm if norm else None
            if tag:
                result.append((tag, pct))
        return result

    @staticmethod
    def _map_situations_to_context_tags(situations: List[str]) -> List[str]:
        tags: List[str] = []
        for s in situations or []:
            for t in SITUATION_TO_CONTEXT.get(str(s).lower(), []):
                if t not in tags:
                    tags.append(t)
        return tags

    # ─────────────────────────────────────────────────────────────────────────
    # Fetch
    # ─────────────────────────────────────────────────────────────────────────

    def _fetch_candidates(self, style_tags_with_pct: List[Tuple[str, int]]) -> List[Dict[str, Any]]:
        primary_tags = [t for t, _ in style_tags_with_pct] if style_tags_with_pct else []
        SELECT = (
            "id, title, image_url, category, piece_type, "
            "style_primary, style_secondary, style_tertiary, "
            "silhouette_types, flatters_zones, minimizes_zones, "
            "silhouette_effect, context_tags, message_tags, "
            "personality_tags, base_priority"
        )

        if primary_tags:
            try:
                resp = (
                    self.client.table("style_piece_visuals")
                    .select(SELECT)
                    .eq("is_active", True)
                    .in_("style_primary", primary_tags)
                    .limit(250)
                    .execute()
                )
                data = getattr(resp, "data", None) or []
                print(f"✅ [StylePiecesSelector] {len(data)} candidats primaires")

                if len(data) >= 20:
                    return data

                resp2 = (
                    self.client.table("style_piece_visuals")
                    .select(SELECT)
                    .eq("is_active", True)
                    .in_("style_secondary", primary_tags)
                    .limit(250)
                    .execute()
                )
                data2 = getattr(resp2, "data", None) or []
                ids_seen = {r["id"] for r in data}
                for r in data2:
                    if r["id"] not in ids_seen:
                        data.append(r)
                        ids_seen.add(r["id"])

                print(f"   ↩ Après secondary: {len(data)} candidats")
                if len(data) >= 10:
                    return data

            except Exception as e:
                print(f"⚠️ [StylePiecesSelector] Fetch style_primary failed: {e}")

        try:
            resp = (
                self.client.table("style_piece_visuals")
                .select(SELECT)
                .eq("is_active", True)
                .limit(250)
                .execute()
            )
            data = getattr(resp, "data", None) or []
            print(f"   ↩ Fallback all: {len(data)} pièces")
            return data
        except Exception as e:
            print(f"⚠️ [StylePiecesSelector] Fallback failed: {e}")
            return []

    # ─────────────────────────────────────────────────────────────────────────
    # Scoring
    # ─────────────────────────────────────────────────────────────────────────

    def _score_piece(
        self,
        piece: Dict[str, Any],
        style_tags_with_pct: List[Tuple[str, int]],
        silhouette_type: str,
        highlight_zones: List[str],
        minimize_zones: List[str],
        context_tags: List[str],
    ) -> float:
        score = 0.0
        sp = self._normalize(piece.get("style_primary") or "")
        ss = self._normalize(piece.get("style_secondary") or "")
        st = self._normalize(piece.get("style_tertiary") or "")

        for tag, pct in style_tags_with_pct:
            tn = self._normalize(tag)
            w  = pct / 100.0
            if sp == tn:   score += SCORE_STYLE_PRIMARY   * w
            elif ss == tn: score += SCORE_STYLE_SECONDARY * w
            elif st == tn: score += SCORE_STYLE_TERTIARY  * w

        sil_types = self._parse_jsonb(piece.get("silhouette_types"))
        if silhouette_type and any(s.upper() == silhouette_type.upper() for s in sil_types):
            score += SCORE_MORPHO_MATCH

        flatters  = self._parse_jsonb(piece.get("flatters_zones"))
        minimizes = self._parse_jsonb(piece.get("minimizes_zones"))
        score += len(self._zones_overlap(highlight_zones, flatters))  * SCORE_FLATTERS_ZONE
        score += len(self._zones_overlap(minimize_zones, minimizes))  * SCORE_MINIMIZES_ZONE

        piece_ctx = self._parse_jsonb(piece.get("context_tags"))
        for ctx in context_tags:
            if any(self._normalize(ctx) == self._normalize(pc) for pc in piece_ctx):
                score += SCORE_CONTEXT_TAG

        score += float(piece.get("base_priority") or 0) * SCORE_BASE_PRIORITY
        return score

    # ─────────────────────────────────────────────────────────────────────────
    # Sélection diversifiée
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _select_diverse_top10(
        scored: List[Tuple[float, Dict[str, Any]]],
    ) -> List[Tuple[float, Dict[str, Any]]]:
        sorted_pieces = sorted(scored, key=lambda x: x[0], reverse=True)
        counts   = {cat: 0 for cat in CATEGORY_TARGETS}
        selected = []
        overflow = []

        for s, p in sorted_pieces:
            cat    = (p.get("category") or "").strip().lower()
            target = CATEGORY_TARGETS.get(cat, 0)
            if counts.get(cat, 0) < target:
                selected.append((s, p))
                counts[cat] = counts.get(cat, 0) + 1
            else:
                overflow.append((s, p))
            if len(selected) == 10:
                break

        for item in overflow:
            if len(selected) >= 10:
                break
            selected.append(item)

        return selected[:10]

    # ─────────────────────────────────────────────────────────────────────────
    # Génération du commentaire v1.1
    # ─────────────────────────────────────────────────────────────────────────

    def _generate_comment(
        self,
        piece: Dict[str, Any],
        highlight_zones: List[str],
        minimize_zones: List[str],
        style_tags_with_pct: List[Tuple[str, int]],
    ) -> str:
        sp_norm           = self._normalize(piece.get("style_primary") or "")
        silhouette_effect = (piece.get("silhouette_effect") or "").strip()
        flatters          = self._parse_jsonb(piece.get("flatters_zones"))
        minimizes_piece   = self._parse_jsonb(piece.get("minimizes_zones"))
        message_tags      = self._parse_jsonb(piece.get("message_tags"))

        # Déterminisme de variante pour éviter la répétition visuelle
        piece_id = piece.get("id") or ""
        h = sum(ord(c) for c in piece_id[:8]) if piece_id else 0

        parts: List[str] = []

        # ── Partie 1 : ancrage dans le profil stylistique de la cliente ───
        top = style_tags_with_pct[:2]

        if len(top) >= 2:
            s1_tag, _ = top[0]
            s2_tag, _ = top[1]
            s1 = STYLE_DISPLAY_LABELS.get(self._normalize(s1_tag), s1_tag)
            s2 = STYLE_DISPLAY_LABELS.get(self._normalize(s2_tag), s2_tag)

            if sp_norm == self._normalize(s1_tag):
                tpls = [
                    f"Incarne le cœur de votre style {s1}, avec la touche {s2} qui vous définit.",
                    f"Ancrage direct dans votre ADN {s1} — l'équilibre parfait avec votre côté {s2}.",
                    f"Pièce signature de votre profil {s1}, en résonance avec votre nuance {s2}.",
                    f"Au centre de votre style {s1} — complète naturellement votre facette {s2}.",
                ]
            elif sp_norm == self._normalize(s2_tag):
                tpls = [
                    f"Exprime votre facette {s2} qui enrichit et équilibre votre base {s1}.",
                    f"Apporte la nuance {s2} essentielle à votre style {s1}.",
                    f"La touche {s2} qui donne du relief à votre garde-robe {s1}.",
                ]
            else:
                tpls = [
                    f"Pont naturel entre votre style {s1} et votre touche {s2}.",
                    f"S'intègre dans votre univers {s1}/{s2} avec cohérence.",
                ]

        elif len(top) == 1:
            s1_tag, _ = top[0]
            s1 = STYLE_DISPLAY_LABELS.get(self._normalize(s1_tag), s1_tag)
            tpls = [
                f"Pièce signature de votre style {s1}.",
                f"Incarne l'ADN {s1} qui vous correspond.",
                f"Essentielle à votre garde-robe {s1}.",
            ]
        else:
            tpls = ["Pièce clé de votre garde-robe personnalisée."]

        parts.append(tpls[h % len(tpls)])

        # ── Partie 2 : effet silhouette (si non générique) ────────────────
        if silhouette_effect and len(silhouette_effect) > 5:
            effect_norm = self._normalize(silhouette_effect)
            if effect_norm not in GENERIC_EFFECTS:
                e = silhouette_effect.strip()
                e = e[0].upper() + e[1:]
                if not e.endswith("."):
                    e += "."
                parts.append(e)

        # ── Partie 3 : zones ou message ───────────────────────────────────
        flatters_match  = self._zones_overlap(highlight_zones, flatters)
        minimizes_match = self._zones_overlap(minimize_zones, minimizes_piece)

        if flatters_match:
            z = " et ".join(flatters_match[:2])
            zone_tpls = [
                f"Valorise votre {z}.",
                f"Met en avant votre {z}.",
                f"Souligne votre {z}.",
            ]
            parts.append(zone_tpls[h % len(zone_tpls)])
        elif minimizes_match:
            z = " et ".join(minimizes_match[:2])
            min_tpls = [
                f"Affine visuellement {z}.",
                f"Atténue discrètement {z}.",
                f"Equilibre la silhouette au niveau {z}.",
            ]
            parts.append(min_tpls[h % len(min_tpls)])
        elif message_tags:
            labels = [MESSAGE_DISPLAY_LABELS.get(m) for m in message_tags[:3] if MESSAGE_DISPLAY_LABELS.get(m)]
            if labels:
                parts.append(f"L'allure : {' et '.join(labels[:2])}.")

        return " ".join(parts)

    # ─────────────────────────────────────────────────────────────────────────
    # Point d'entrée principal
    # ─────────────────────────────────────────────────────────────────────────

    def select_10_pieces(
        self,
        style_mix: List[Dict[str, Any]],
        silhouette_type: str,
        body_parts_to_highlight: List[str],
        body_parts_to_minimize: List[str],
        selected_situations: List[str],
    ) -> List[Dict[str, Any]]:
        print("\n" + "=" * 64)
        print("🎨 STYLE PIECES SELECTOR v1.1")
        print(f"   style_mix       : {style_mix}")
        print(f"   silhouette_type : {silhouette_type}")
        print(f"   highlight       : {body_parts_to_highlight}")
        print(f"   minimize        : {body_parts_to_minimize}")
        print(f"   situations      : {selected_situations}")

        style_tags   = self._map_style_mix_to_tags(style_mix)
        context_tags = self._map_situations_to_context_tags(selected_situations)
        h_zones      = [z.strip() for z in (body_parts_to_highlight or []) if z]
        m_zones      = [z.strip() for z in (body_parts_to_minimize  or []) if z]

        print(f"   style_tags      : {style_tags}")
        print(f"   context_tags    : {context_tags}")

        candidates = self._fetch_candidates(style_tags)
        if not candidates:
            print("⚠️ Aucun candidat")
            return []

        scored = [
            (self._score_piece(p, style_tags, silhouette_type, h_zones, m_zones, context_tags), p)
            for p in candidates
        ]

        top5 = sorted(scored, key=lambda x: x[0], reverse=True)[:5]
        print("   Top 5:")
        for s, p in top5:
            print(f"     [{s:.1f}] {p.get('title')} ({p.get('category')}/{p.get('style_primary')})")

        selected       = self._select_diverse_top10(scored)
        score_by_id    = {p.get("id"): s for s, p in scored}

        result = []
        for s, piece in selected:
            comment = self._generate_comment(piece, h_zones, m_zones, style_tags)
            result.append({
                "id":                piece.get("id", ""),
                "title":             piece.get("title", ""),
                "image_url":         piece.get("image_url", ""),
                "category":          piece.get("category", ""),
                "piece_type":        piece.get("piece_type", ""),
                "style_primary":     piece.get("style_primary", ""),
                "silhouette_effect": piece.get("silhouette_effect", ""),
                "comment":           comment,
                "score":             round(score_by_id.get(piece.get("id"), s), 1),
            })

        print(f"\n✅ {len(result)} pièces sélectionnées:")
        for r in result:
            print(f"   [{r['score']:.1f}] {r['title']} | {r['comment'][:80]}...")
        print("=" * 64 + "\n")

        return result


style_pieces_selector = StylePiecesSelector()