"""
Style Pieces Selector v1.0
Sélectionne 10 pièces phares depuis style_piece_visuals
en fonction du profil stylistique et morphologique de la cliente.

Aucun appel OpenAI — scoring pur + commentaires template.
"""

import json
import re
from typing import Any, Dict, List, Optional, Tuple

from app.utils.supabase_client import supabase


# ─────────────────────────────────────────────────────────────────────────────
# Mapping labels styling (styling_service) → style_primary (style_piece_visuals)
# ─────────────────────────────────────────────────────────────────────────────
STYLE_LABEL_TO_TAG: Dict[str, str] = {
    # Labels complets (styling._score_styles keys)
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
    # Labels courts (parfois présents dans style_mix)
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
    # Valeurs déjà normalisées (fallback direct)
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

# Distribution cible des 10 pièces par catégorie (category dans style_piece_visuals)
CATEGORY_TARGETS: Dict[str, int] = {
    "top":       2,
    "bottom":    2,
    "dress":     1,
    "outerwear": 1,
    "shoe":      2,
    "accessory": 2,
}

# Poids de scoring
SCORE_STYLE_PRIMARY   = 30   # style_primary == tag client (pondéré par pct)
SCORE_STYLE_SECONDARY = 15   # style_secondary == tag client
SCORE_STYLE_TERTIARY  = 5    # style_tertiary == tag client
SCORE_MORPHO_MATCH    = 25   # silhouette_type de la cliente dans silhouette_types de la pièce
SCORE_FLATTERS_ZONE   = 8    # par zone flatters_zones qui recoupe les zones à valoriser
SCORE_MINIMIZES_ZONE  = 8    # par zone minimizes_zones qui recoupe les zones à minimiser
SCORE_CONTEXT_TAG     = 4    # par context_tag qui recoupe les situations de la cliente
SCORE_BASE_PRIORITY   = 0.10 # base_priority × 0.10 (max ~10 pts pour base_priority=100)

# Labels lisibles pour les commentaires
STYLE_DISPLAY_LABELS: Dict[str, str] = {
    "minimaliste": "minimaliste",
    "chic":        "chic et élégant",
    "classique":   "classique et intemporel",
    "moderne":     "moderne et contemporain",
    "casual":      "casual et décontracté",
    "boheme":      "bohème et naturel",
    "romantique":  "romantique",
    "rock":        "rock et affirmé",
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

# Mapping situations onboarding → context_tags style_piece_visuals
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


class StylePiecesSelector:
    """
    Sélectionne les 10 meilleures pièces depuis style_piece_visuals
    pour le profil d'une cliente donnée.
    """

    def __init__(self):
        self.client = supabase.get_client()

    # ─────────────────────────────────────────────────────────────────────────
    # Helpers statiques
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _parse_jsonb(value: Any) -> List[str]:
        """Parse un champ jsonb Supabase (liste ou string JSON)."""
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
        """Lowercase + suppression accents pour comparaison robuste."""
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
        """
        Retourne les zones client qui ont un recouvrement avec les zones de la pièce.
        Matching souple : sous-chaîne bidirectionnelle après normalisation.
        """
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
        """
        Convertit style_mix=[{style: "Style Classique / Intemporel", pct: 55}, ...]
        en [(tag_normalisé, pct), ...] pour le scoring.
        """
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
                # Tentative normalisée : strip "Style " + accents
                norm = StylePiecesSelector._normalize(label)
                norm = re.sub(r"^style\s+", "", norm)
                norm = re.sub(r"\s*/.*$", "", norm).strip()
                tag = norm if norm else None

            if tag:
                result.append((tag, pct))

        return result

    @staticmethod
    def _map_situations_to_context_tags(situations: List[str]) -> List[str]:
        """Convertit les IDs de situations onboarding en context_tags CSV."""
        tags: List[str] = []
        for s in situations or []:
            for t in SITUATION_TO_CONTEXT.get(str(s).lower(), []):
                if t not in tags:
                    tags.append(t)
        return tags

    # ─────────────────────────────────────────────────────────────────────────
    # Fetch depuis Supabase
    # ─────────────────────────────────────────────────────────────────────────

    def _fetch_candidates(
        self,
        style_tags_with_pct: List[Tuple[str, int]],
    ) -> List[Dict[str, Any]]:
        """
        Récupère les pièces actives filtrées par style_primary des tags client.
        Fallback sur toutes les pièces actives si résultats insuffisants (< 20).
        """
        primary_tags = [t for t, _ in style_tags_with_pct] if style_tags_with_pct else []

        # Essai 1 : filtre sur style_primary
        if primary_tags:
            try:
                resp = (
                    self.client.table("style_piece_visuals")
                    .select(
                        "id, title, image_url, category, piece_type, "
                        "style_primary, style_secondary, style_tertiary, "
                        "silhouette_types, flatters_zones, minimizes_zones, "
                        "silhouette_effect, context_tags, message_tags, "
                        "personality_tags, base_priority"
                    )
                    .eq("is_active", True)
                    .in_("style_primary", primary_tags)
                    .limit(250)
                    .execute()
                )
                data = getattr(resp, "data", None) or []
                print(f"✅ [StylePiecesSelector] {len(data)} candidats (style_primary in {primary_tags})")

                if len(data) >= 20:
                    return data

                print(f"   ↩ Trop peu ({len(data)}) — ajout style_secondary...")

                # Essai 2 : aussi style_secondary pour élargir
                resp2 = (
                    self.client.table("style_piece_visuals")
                    .select(
                        "id, title, image_url, category, piece_type, "
                        "style_primary, style_secondary, style_tertiary, "
                        "silhouette_types, flatters_zones, minimizes_zones, "
                        "silhouette_effect, context_tags, message_tags, "
                        "personality_tags, base_priority"
                    )
                    .eq("is_active", True)
                    .in_("style_secondary", primary_tags)
                    .limit(250)
                    .execute()
                )
                data2 = getattr(resp2, "data", None) or []

                # Déduplique
                ids_seen = {r["id"] for r in data}
                for r in data2:
                    if r["id"] not in ids_seen:
                        data.append(r)
                        ids_seen.add(r["id"])

                print(f"   ↩ Après ajout secondary: {len(data)} candidats")

                if len(data) >= 10:
                    return data

            except Exception as e:
                print(f"⚠️ [StylePiecesSelector] Fetch style_primary failed: {e}")

        # Fallback final : toutes pièces actives
        print(f"   ↩ Fallback: toutes pièces actives")
        try:
            resp = (
                self.client.table("style_piece_visuals")
                .select(
                    "id, title, image_url, category, piece_type, "
                    "style_primary, style_secondary, style_tertiary, "
                    "silhouette_types, flatters_zones, minimizes_zones, "
                    "silhouette_effect, context_tags, message_tags, "
                    "personality_tags, base_priority"
                )
                .eq("is_active", True)
                .limit(250)
                .execute()
            )
            data = getattr(resp, "data", None) or []
            print(f"   ↩ Fallback: {len(data)} pièces actives récupérées")
            return data
        except Exception as e:
            print(f"⚠️ [StylePiecesSelector] Fallback fetch failed: {e}")
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

        # ── Style scoring (pondéré par %) ─────────────────────────────────
        sp_norm = self._normalize(piece.get("style_primary") or "")
        ss_norm = self._normalize(piece.get("style_secondary") or "")
        st_norm = self._normalize(piece.get("style_tertiary") or "")

        for tag, pct in style_tags_with_pct:
            tag_norm = self._normalize(tag)
            weight = pct / 100.0
            if sp_norm == tag_norm:
                score += SCORE_STYLE_PRIMARY * weight
            elif ss_norm == tag_norm:
                score += SCORE_STYLE_SECONDARY * weight
            elif st_norm == tag_norm:
                score += SCORE_STYLE_TERTIARY * weight

        # ── Morpho scoring ────────────────────────────────────────────────
        sil_types = self._parse_jsonb(piece.get("silhouette_types"))
        sil_upper = silhouette_type.upper() if silhouette_type else ""
        if sil_upper and any(s.upper() == sil_upper for s in sil_types):
            score += SCORE_MORPHO_MATCH

        # ── Zones valorisées ──────────────────────────────────────────────
        flatters = self._parse_jsonb(piece.get("flatters_zones"))
        matches_flatters = self._zones_overlap(highlight_zones, flatters)
        score += len(matches_flatters) * SCORE_FLATTERS_ZONE

        # ── Zones minimisées ──────────────────────────────────────────────
        minimizes = self._parse_jsonb(piece.get("minimizes_zones"))
        matches_minimizes = self._zones_overlap(minimize_zones, minimizes)
        score += len(matches_minimizes) * SCORE_MINIMIZES_ZONE

        # ── Contextes ─────────────────────────────────────────────────────
        piece_contexts = self._parse_jsonb(piece.get("context_tags"))
        for ctx in context_tags:
            ctx_norm = self._normalize(ctx)
            if any(ctx_norm == self._normalize(pc) for pc in piece_contexts):
                score += SCORE_CONTEXT_TAG

        # ── Priorité de base ──────────────────────────────────────────────
        score += float(piece.get("base_priority") or 0) * SCORE_BASE_PRIORITY

        return score

    # ─────────────────────────────────────────────────────────────────────────
    # Sélection diversifiée (respect distribution cible)
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _select_diverse_top10(
        scored_pieces: List[Tuple[float, Dict[str, Any]]],
    ) -> List[Tuple[float, Dict[str, Any]]]:
        """
        Sélectionne 10 pièces en respectant CATEGORY_TARGETS.
        Les pièces surreprésentées sont mises en attente et ajoutées si besoin.
        """
        sorted_pieces = sorted(scored_pieces, key=lambda x: x[0], reverse=True)
        category_counts: Dict[str, int] = {cat: 0 for cat in CATEGORY_TARGETS}
        selected: List[Tuple[float, Dict[str, Any]]] = []
        overflow: List[Tuple[float, Dict[str, Any]]] = []

        for score, piece in sorted_pieces:
            cat = (piece.get("category") or "").strip().lower()
            target = CATEGORY_TARGETS.get(cat, 0)
            current = category_counts.get(cat, 0)

            if current < target:
                selected.append((score, piece))
                category_counts[cat] = current + 1
            else:
                overflow.append((score, piece))

            if len(selected) == 10:
                break

        # Compléter avec les meilleurs surreprésentés si < 10
        if len(selected) < 10:
            for item in overflow:
                if len(selected) >= 10:
                    break
                selected.append(item)

        return selected[:10]

    # ─────────────────────────────────────────────────────────────────────────
    # Génération du commentaire stylistique (template, pas d'OpenAI)
    # ─────────────────────────────────────────────────────────────────────────

    def _generate_comment(
        self,
        piece: Dict[str, Any],
        highlight_zones: List[str],
        minimize_zones: List[str],
        style_tags_with_pct: List[Tuple[str, int]],
    ) -> str:
        """
        Génère un commentaire personnalisé à 2-3 phrases:
        1. Ancrage stylistique
        2. Effet silhouette de la pièce
        3. Adéquation morphologique (zones)
        """
        style_primary = self._normalize(piece.get("style_primary") or "")
        silhouette_effect = (piece.get("silhouette_effect") or "").strip()
        flatters = self._parse_jsonb(piece.get("flatters_zones"))
        minimizes_zones_piece = self._parse_jsonb(piece.get("minimizes_zones"))
        message_tags = self._parse_jsonb(piece.get("message_tags"))

        parts: List[str] = []

        # ── Partie 1 : ancrage stylistique ───────────────────────────────
        style_label = STYLE_DISPLAY_LABELS.get(style_primary, style_primary or "votre style")
        parts.append(f"Pièce clé de votre ADN {style_label}.")

        # ── Partie 2 : effet silhouette ───────────────────────────────────
        if silhouette_effect and len(silhouette_effect.strip()) > 5:
            effect = silhouette_effect.strip()
            effect = effect[0].upper() + effect[1:]
            if not effect.endswith("."):
                effect += "."
            parts.append(effect)

        # ── Partie 3a : zones valorisées ─────────────────────────────────
        flatters_match = self._zones_overlap(highlight_zones, flatters)
        if flatters_match:
            zones_str = " et ".join(flatters_match[:2])
            parts.append(f"Valorise votre {zones_str}.")

        # ── Partie 3b : zones minimisées ─────────────────────────────────
        minimizes_match = self._zones_overlap(minimize_zones, minimizes_zones_piece)
        if minimizes_match and not flatters_match:
            zones_str = " et ".join(minimizes_match[:2])
            parts.append(f"Atténue visuellement {zones_str}.")

        # ── Fallback si peu de contenu : message_tags ─────────────────────
        if len(parts) < 3 and message_tags:
            msg_labels = [
                MESSAGE_DISPLAY_LABELS.get(m, None)
                for m in message_tags[:3]
                if MESSAGE_DISPLAY_LABELS.get(m)
            ]
            if msg_labels:
                parts.append(f"L'allure : {' et '.join(msg_labels[:2])}.")

        return " ".join(parts) if parts else f"Une pièce essentielle pour votre style {style_label}."

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
        """
        Retourne une liste de 10 pièces phares avec commentaire personnalisé.

        Chaque dict retourné contient :
          - title          : nom de la pièce
          - image_url      : URL Supabase (chargeable directement par PDFMonkey)
          - category       : top / bottom / dress / outerwear / shoe / accessory
          - piece_type     : type précis
          - style_primary  : style dominant de la pièce
          - comment        : commentaire stylistique personnalisé (2-3 phrases)
          - score          : score de pertinence (debug)
        """
        print("\n" + "=" * 64)
        print("🎨 STYLE PIECES SELECTOR — Sélection 10 pièces phares")
        print(f"   style_mix       : {style_mix}")
        print(f"   silhouette_type : {silhouette_type}")
        print(f"   highlight_zones : {body_parts_to_highlight}")
        print(f"   minimize_zones  : {body_parts_to_minimize}")
        print(f"   situations      : {selected_situations}")

        # 1) Mapper les styles
        style_tags_with_pct = self._map_style_mix_to_tags(style_mix)
        print(f"   style_tags      : {style_tags_with_pct}")

        # 2) Mapper les situations en context_tags
        context_tags = self._map_situations_to_context_tags(selected_situations)
        print(f"   context_tags    : {context_tags}")

        # 3) Normaliser les zones (conserve la valeur originale pour l'affichage)
        highlight_zones = [z.strip() for z in (body_parts_to_highlight or []) if z]
        minimize_zones  = [z.strip() for z in (body_parts_to_minimize or []) if z]

        # 4) Fetch candidats depuis Supabase
        candidates = self._fetch_candidates(style_tags_with_pct)
        if not candidates:
            print("⚠️ [StylePiecesSelector] Aucun candidat — liste vide retournée")
            return []

        # 5) Scorer chaque pièce
        scored: List[Tuple[float, Dict[str, Any]]] = []
        for piece in candidates:
            s = self._score_piece(
                piece=piece,
                style_tags_with_pct=style_tags_with_pct,
                silhouette_type=silhouette_type,
                highlight_zones=highlight_zones,
                minimize_zones=minimize_zones,
                context_tags=context_tags,
            )
            scored.append((s, piece))

        # Log top 5 pour debug
        top5 = sorted(scored, key=lambda x: x[0], reverse=True)[:5]
        print(f"   Top 5 scores:")
        for s, p in top5:
            print(f"     [{s:.1f}] {p.get('title')} ({p.get('category')}/{p.get('style_primary')})")

        # 6) Sélection diversifiée
        selected = self._select_diverse_top10(scored)

        # Index score par id pour lookup rapide
        score_by_id: Dict[str, float] = {p.get("id"): s for s, p in scored}

        # 7) Enrichir avec commentaire
        result: List[Dict[str, Any]] = []
        for s, piece in selected:
            comment = self._generate_comment(
                piece=piece,
                highlight_zones=highlight_zones,
                minimize_zones=minimize_zones,
                style_tags_with_pct=style_tags_with_pct,
            )
            result.append({
                "id":               piece.get("id", ""),
                "title":            piece.get("title", ""),
                "image_url":        piece.get("image_url", ""),
                "category":         piece.get("category", ""),
                "piece_type":       piece.get("piece_type", ""),
                "style_primary":    piece.get("style_primary", ""),
                "silhouette_effect": piece.get("silhouette_effect", ""),
                "comment":          comment,
                "score":            round(score_by_id.get(piece.get("id"), s), 1),
            })

        print(f"\n✅ {len(result)} pièces finales sélectionnées")
        for r in result:
            print(f"   [{r['score']:.1f}] {r['title']} ({r['category']}) — img={'✓' if r['image_url'] else '✗'}")
        print("=" * 64 + "\n")

        return result


# Instance globale (pattern utilisé partout dans le projet)
style_pieces_selector = StylePiecesSelector()