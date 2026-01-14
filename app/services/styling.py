"""
Styling Service v4.0 - Compatible prompt premium + personnalité
✅ Support placeholders avec points {a.b.c}
✅ JSON parsing robuste + réparation
✅ Normalisation du schéma V2 (stylistic_identity, capsule, outfits, plan…)
✅ Instance styling_service exportée
"""

import json
import re
from typing import Any, Dict, List, Tuple

from app.utils.openai_client import openai_client
from app.utils.openai_call_tracker import call_tracker
from app.prompts.styling_prompt import STYLING_SYSTEM_PROMPT, STYLING_USER_PROMPT


class StylingService:
    def __init__(self):
        self.openai = openai_client

    # ---------------------------------------------------------------------
    # Helpers: JSON cleaning / formatting / safe getters
    # ---------------------------------------------------------------------
    @staticmethod
    def clean_json_string(content: str) -> str:
        """Nettoie une réponse JSON (code fences, null bytes, etc.)"""
        content = re.sub(r'^```json\s*', '', content.strip())
        content = re.sub(r'^\s*```', '', content.strip())
        content = re.sub(r'\s*```$', '', content.strip())
        content = content.replace('\x00', '')
        return content.strip()

    def _join_list(self, x, maxn=6):
        if isinstance(x, list):
            return ", ".join([str(i) for i in x if str(i).strip()][:maxn])
        return ""

    # ---------------------------------------------------------------------
    # Helpers: normalization / safe text
    # ---------------------------------------------------------------------
    def _lower_list(self, xs) -> List[str]:
        if not isinstance(xs, list):
            return []
        return [str(x).strip().lower() for x in xs if str(x).strip()]

    def _ensure_min_words(self, text: str, min_words: int) -> bool:
        return isinstance(text, str) and len(text.split()) >= min_words

    def _one_line(self, text: str) -> str:
        if not isinstance(text, str):
            return ""
        t = text.replace("\n", " ").replace("\r", " ").replace("\t", " ")
        # normalisation guillemets typographiques
        t = (
            t.replace("’", "'")
            .replace("“", '"')
            .replace("”", '"')
            .replace("«", '"')
            .replace("»", '"')
        )
        t = re.sub(r"\s{2,}", " ", t).strip()
        return t

    def _labelize_traits(self, ids: List[str]) -> List[str]:
        # IDs exacts -> labels UI
        mapping = {
            "creative": "Créative",
            "discrete": "Discrète",
            "dynamic": "Dynamique",
            "ambitious": "Ambitieuse",
            "sensitive": "Sensible",
            "bold": "Audacieuse",
            "romantic": "Romantique",
            "practical": "Pratique",
            "extroverted": "Extravertie",
            "reserved": "Réservée",
            "natural": "Naturelle",
            "refined": "Raffinée",
        }
        out = []
        for x in ids or []:
            k = str(x).strip().lower()
            out.append(mapping.get(k, str(x)))
        return out

    def _labelize_messages(self, ids: List[str]) -> List[str]:
        mapping = {
            "natural": "se sentir naturelle et alignée",
            "respect": "inspirer le respect et la crédibilité",
            "creativity": "exprimer sa créativité et son originalité",
            "feminine": "se sentir séduisante et féminine",
            "silhouette": "mettre en valeur sa silhouette",
            "elegance": "se démarquer avec élégance",
            "discrete_style": "rester discrète mais stylée",
        }
        out = []
        for x in ids or []:
            k = str(x).strip().lower()
            out.append(mapping.get(k, str(x)))
        return out

    def _labelize_situations(self, ids: List[str]) -> List[str]:
        mapping = {
            "work": "travail / bureau",
            "events": "soirées / événements",
            "weekends": "week-ends / loisirs",
            "dating": "rendez-vous / dating",
            "travel": "voyages",
            "family": "vie de famille",
            "social": "réseaux sociaux / influence",
            "student": "étudiante",
            "remote": "télétravail / maison",
        }
        out = []
        for x in ids or []:
            k = str(x).strip().lower()
            out.append(mapping.get(k, str(x)))
        return out

    # ---------------------------------------------------------------------
    # 1) Archetypes scoring (IDs exacts)
    # ---------------------------------------------------------------------
    def _score_archetypes(self, personality_data: Dict[str, Any]) -> Dict[str, int]:
        traits = self._lower_list((personality_data or {}).get("selected_personality", []))
        msgs = self._lower_list((personality_data or {}).get("selected_message", []))
        ctx = self._lower_list((personality_data or {}).get("selected_situations", []))

        scores = {
            "Reine / Leader": 0,
            "Guerrière / Chasseresse": 0,
            "Romantique / Amante": 0,
            "Sage / Mystique": 0,
            "Visionnaire / Créative": 0,
        }

        # Traits -> archetypes
        if "ambitious" in traits: scores["Reine / Leader"] += 3; scores["Guerrière / Chasseresse"] += 1
        if "bold" in traits: scores["Guerrière / Chasseresse"] += 3; scores["Reine / Leader"] += 1
        if "romantic" in traits: scores["Romantique / Amante"] += 4
        if "dynamic" in traits: scores["Guerrière / Chasseresse"] += 2
        if "refined" in traits: scores["Reine / Leader"] += 2; scores["Sage / Mystique"] += 1
        if "discrete" in traits: scores["Sage / Mystique"] += 2; scores["Reine / Leader"] += 1
        if "practical" in traits: scores["Sage / Mystique"] += 2
        if "reserved" in traits: scores["Sage / Mystique"] += 2
        if "natural" in traits: scores["Sage / Mystique"] += 2
        if "sensitive" in traits: scores["Romantique / Amante"] += 2; scores["Sage / Mystique"] += 1
        if "creative" in traits: scores["Visionnaire / Créative"] += 4
        if "extroverted" in traits: scores["Guerrière / Chasseresse"] += 1; scores["Visionnaire / Créative"] += 1

        # Messages -> archetypes
        if "respect" in msgs: scores["Reine / Leader"] += 4; scores["Sage / Mystique"] += 1
        if "feminine" in msgs: scores["Romantique / Amante"] += 3; scores["Reine / Leader"] += 1
        if "elegance" in msgs: scores["Reine / Leader"] += 3; scores["Visionnaire / Créative"] += 1
        if "discrete_style" in msgs: scores["Sage / Mystique"] += 3; scores["Reine / Leader"] += 1
        if "natural" in msgs: scores["Sage / Mystique"] += 3
        if "creativity" in msgs: scores["Visionnaire / Créative"] += 4
        if "silhouette" in msgs: scores["Reine / Leader"] += 1; scores["Guerrière / Chasseresse"] += 1

        # Situations -> archetypes
        if "work" in ctx or "student" in ctx: scores["Reine / Leader"] += 2; scores["Sage / Mystique"] += 1
        if "events" in ctx or "dating" in ctx: scores["Romantique / Amante"] += 2; scores["Reine / Leader"] += 1
        if "remote" in ctx: scores["Sage / Mystique"] += 2
        if "weekends" in ctx or "travel" in ctx: scores["Sage / Mystique"] += 1; scores["Guerrière / Chasseresse"] += 1
        if "social" in ctx: scores["Visionnaire / Créative"] += 2; scores["Reine / Leader"] += 1
        if "family" in ctx: scores["Sage / Mystique"] += 2

        return scores

    def _top_archetypes(self, scores: Dict[str, int]) -> Tuple[List[str], List[str]]:
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        nonzero = [a for a, s in ranked if s > 0]

        main = nonzero[:2] if nonzero else ["Sage / Mystique"]
        secondary = nonzero[2:3]  # optional 1 secondary
        return main, secondary

    # ---------------------------------------------------------------------
    # 2) Styles scoring (IDs exacts + refus couleurs/motifs + marques)
    # ---------------------------------------------------------------------
    def _score_styles(
        self,
        style_preferences: List[str],
        brand_preferences: Dict[str, Any],
        color_preferences: Dict[str, Any],
        pattern_preferences: Dict[str, Any],
        archetypes_main: List[str],
        archetypes_secondary: List[str],
    ) -> Dict[str, int]:

        sp = self._lower_list(style_preferences)
        brands = self._lower_list((brand_preferences or {}).get("selected_brands", [])) + self._lower_list((brand_preferences or {}).get("custom_brands", []))
        disliked_colors = self._lower_list((color_preferences or {}).get("disliked_colors", []))
        disliked_patterns = self._lower_list((pattern_preferences or {}).get("disliked_patterns", []))

        # Styles "produit" (liste)
        stylescore = {
            "Style Classique / Intemporel": 0,
            "Style Chic / Élégant": 0,
            "Style Minimaliste": 0,
            "Style Casual / Décontracté": 0,
            "Style Bohème": 0,
            "Style Romantique": 0,
            "Style Glamour": 0,
            "Style Rock": 0,
            "Style Urbain / Streetwear": 0,
            "Style Sporty Chic": 0,
            "Style Preppy": 0,
            "Style Vintage": 0,
            "Style Moderne / Contemporain": 0,
            "Style Artistique / Créatif": 0,
            "Style Ethnique": 0,
            "Style Féminin Moderne": 0,
            "Style Sexy Assumé": 0,
            "Style Naturel / Authentique": 0,
        }

        # Archetypes -> styles (principal)
        for a in archetypes_main:
            if "Reine" in a:
                stylescore["Style Chic / Élégant"] += 4
                stylescore["Style Classique / Intemporel"] += 3
                stylescore["Style Minimaliste"] += 2
                stylescore["Style Féminin Moderne"] += 3
            if "Guerrière" in a:
                stylescore["Style Sporty Chic"] += 5
                stylescore["Style Urbain / Streetwear"] += 4
                stylescore["Style Moderne / Contemporain"] += 2
                stylescore["Style Casual / Décontracté"] += 2
            if "Romantique" in a:
                stylescore["Style Romantique"] += 5
                stylescore["Style Féminin Moderne"] += 3
                stylescore["Style Bohème"] += 1
            if "Sage" in a:
                stylescore["Style Minimaliste"] += 3
                stylescore["Style Naturel / Authentique"] += 4
                stylescore["Style Casual / Décontracté"] += 2
                stylescore["Style Classique / Intemporel"] += 1
            if "Visionnaire" in a:
                stylescore["Style Artistique / Créatif"] += 5
                stylescore["Style Moderne / Contemporain"] += 3
                stylescore["Style Vintage"] += 2
                stylescore["Style Ethnique"] += 1

        # Archetype secondaire = poids plus faible
        for a in archetypes_secondary:
            if "Reine" in a:
                stylescore["Style Chic / Élégant"] += 1
                stylescore["Style Féminin Moderne"] += 1
            if "Guerrière" in a:
                stylescore["Style Sporty Chic"] += 1
                stylescore["Style Urbain / Streetwear"] += 1
            if "Romantique" in a:
                stylescore["Style Romantique"] += 1
                stylescore["Style Féminin Moderne"] += 1
            if "Sage" in a:
                stylescore["Style Minimaliste"] += 1
                stylescore["Style Naturel / Authentique"] += 1
            if "Visionnaire" in a:
                stylescore["Style Artistique / Créatif"] += 1
                stylescore["Style Vintage"] += 1

        # Style déclaré onboarding (IDs de tes cards)
        # Tes styles possible: casual, chic, boheme, minimaliste, romantique, rock, vintage, sportswear, classique, moderne
        if "sportswear" in sp:
            stylescore["Style Sporty Chic"] += 7
            stylescore["Style Urbain / Streetwear"] += 4
            stylescore["Style Casual / Décontracté"] += 3
        if "romantique" in sp:
            stylescore["Style Romantique"] += 6
            stylescore["Style Féminin Moderne"] += 2
        if "minimaliste" in sp:
            stylescore["Style Minimaliste"] += 6
        if "chic" in sp:
            stylescore["Style Chic / Élégant"] += 6
        if "classique" in sp:
            stylescore["Style Classique / Intemporel"] += 6
        if "moderne" in sp:
            stylescore["Style Moderne / Contemporain"] += 6
        if "casual" in sp:
            stylescore["Style Casual / Décontracté"] += 5
        if "bohème" in sp or "boheme" in sp:
            stylescore["Style Bohème"] += 6
        if "rock" in sp:
            stylescore["Style Rock"] += 6
        if "vintage" in sp:
            stylescore["Style Vintage"] += 6

        # Marques : règle simple (tu pourras enrichir plus tard)
        # H&M etc -> urbain/casual/féminin moderne/sporty chic
        if any(b in ["h&m", "hm"] for b in brands):
            stylescore["Style Féminin Moderne"] += 3
            stylescore["Style Casual / Décontracté"] += 2
            stylescore["Style Urbain / Streetwear"] += 2
            stylescore["Style Sporty Chic"] += 2

        # Rejets couleurs / motifs
        if "argenté" in disliked_colors or "argente" in disliked_colors:
            stylescore["Style Glamour"] -= 2
            stylescore["Style Sexy Assumé"] -= 2
            stylescore["Style Rock"] -= 1
            stylescore["Style Minimaliste"] += 1
            stylescore["Style Chic / Élégant"] += 1

        # motifs animaux forts (léopard, zèbre, animaliers)
        if any("léopard" in p or "leopard" in p for p in disliked_patterns) or any("zèbre" in p or "zebre" in p for p in disliked_patterns) or any("animalier" in p for p in disliked_patterns):
            stylescore["Style Rock"] -= 2
            stylescore["Style Glamour"] -= 2
            stylescore["Style Sexy Assumé"] -= 2
            stylescore["Style Minimaliste"] += 1
            stylescore["Style Féminin Moderne"] += 1
            stylescore["Style Romantique"] += 1

        # Empêcher scores négatifs
        for k in list(stylescore.keys()):
            stylescore[k] = max(0, int(stylescore[k]))

        return stylescore

    def _pick_top_styles_with_percentages(self, stylescore: Dict[str, int], max_styles: int = 3) -> List[Dict[str, Any]]:
        ranked = sorted(stylescore.items(), key=lambda x: x[1], reverse=True)
        top = [r for r in ranked if r[1] > 0][:max_styles]
        if not top:
            top = [("Style Féminin Moderne", 1), ("Style Sporty Chic", 1), ("Style Minimaliste", 1)]

        total = sum([s for _, s in top]) or 1
        out = [{"style": st, "pct": int(round((sc / total) * 100))} for st, sc in top]
        diff = 100 - sum(x["pct"] for x in out)
        out[0]["pct"] += diff
        return out

    # ---------------------------------------------------------------------
    # 3) Génération des 3 paragraphes (150+ mots, parse-safe)
    # ---------------------------------------------------------------------
    def _dynamic_personality_translation_v2(self, prompt_data: Dict[str, Any], archetypes_main: List[str], archetypes_secondary: List[str]) -> str:
        pers = prompt_data.get("personality_data", {}) or {}
        traits_ids = pers.get("selected_personality", []) or []
        msgs_ids = pers.get("selected_message", []) or []
        ctx_ids = pers.get("selected_situations", []) or []

        traits_lbl = ", ".join(self._labelize_traits(traits_ids)[:4]) if traits_ids else "—"
        msgs_lbl = ", ".join(self._labelize_messages(msgs_ids)[:4]) if msgs_ids else "—"
        ctx_lbl = ", ".join(self._labelize_situations(ctx_ids)[:4]) if ctx_ids else "—"

        brands_list = (prompt_data.get("brand_preferences", {}) or {}).get("selected_brands", []) or []
        brands = ", ".join(brands_list[:4]) if isinstance(brands_list, list) and brands_list else "vos marques habituelles"

        disliked_colors = self._join_list((prompt_data.get("color_preferences", {}) or {}).get("disliked_colors", []), 4) or "—"
        disliked_patterns = self._join_list((prompt_data.get("pattern_preferences", {}) or {}).get("disliked_patterns", []), 4) or "—"

        age = (prompt_data.get("personal_info", {}) or {}).get("age", "")
        hi = self._join_list((prompt_data.get("morphology_goals", {}) or {}).get("body_parts_to_highlight", []), 3) or "vos atouts"
        mi = self._join_list((prompt_data.get("morphology_goals", {}) or {}).get("body_parts_to_minimize", []), 3) or "vos zones à adoucir"

        main = " et ".join(archetypes_main[:2])
        sec = archetypes_secondary[0] if archetypes_secondary else ""

        text = (
            f"À partir de vos réponses, l’IA identifie une signature de personnalité portée par {main}"
            f"{f', avec une nuance {sec}' if sec else ''}. Cela se voit dans vos adjectifs ({traits_lbl}) et dans les messages que vous "
            f"voulez faire passer ({msgs_lbl}) : vous cherchez à être perçue comme féminine, mais avec une présence nette et crédible, "
            f"ce qui demande un équilibre très précis entre douceur et affirmation. Vos situations clés ({ctx_lbl}) indiquent un quotidien "
            f"où vous devez être bien habillée sans y passer trop de temps : vous avez besoin de repères simples et d’une cohérence immédiate, "
            f"en particulier quand vous alternez des moments détente et des moments où l’image compte. Le fait que vous citiez {brands} "
            f"montre que vous aimez des pièces accessibles et modernes, mais que votre attente n’est pas de “faire de la mode” : votre besoin "
            f"principal est de vous sentir sûre de vous, alignée, et lisible. Vos refus (couleurs : {disliked_colors}, motifs : {disliked_patterns}) "
            f"sont aussi une information forte : vous n’avez pas envie de codes trop ostentatoires ni d’effets trop marqués, vous préférez une féminité "
            f"maîtrisée. Enfin, vos objectifs morphologiques (mettre en valeur {hi}, minimiser {mi}) servent de boussole : on construira votre style pour "
            f"que vos tenues travaillent pour vous, avec des détails placés au bon endroit et une silhouette harmonieuse, sans jamais vous déguiser."
        )
        return self._one_line(text)

    def _dynamic_style_positioning_v2(
        self,
        prompt_data: Dict[str, Any],
        archetypes_main: List[str],
        styles_top: List[Dict[str, Any]],
    ) -> str:
        pers = prompt_data.get("personality_data", {}) or {}
        ctx_lbl = ", ".join(self._labelize_situations(pers.get("selected_situations", []) or [])[:4]) or "votre quotidien"
        msgs_lbl = ", ".join(self._labelize_messages(pers.get("selected_message", []) or [])[:4]) or "vos intentions"
        brands_list = (prompt_data.get("brand_preferences", {}) or {}).get("selected_brands", []) or []
        brands = ", ".join(brands_list[:4]) if isinstance(brands_list, list) and brands_list else "vos marques habituelles"

        style_names = [x["style"] for x in styles_top]
        style_pct = ", ".join([f'{x["style"]} — {x["pct"]}%' for x in styles_top])

        disliked_colors = self._join_list((prompt_data.get("color_preferences", {}) or {}).get("disliked_colors", []), 4) or "—"
        disliked_patterns = self._join_list((prompt_data.get("pattern_preferences", {}) or {}).get("disliked_patterns", []), 4) or "—"

        main = " et ".join(archetypes_main[:2])

        text = (
            f"Votre style dominant se structure autour de {', '.join(style_names[:-1]) + ' et ' + style_names[-1] if len(style_names) > 1 else style_names[0]}. "
            f"La répartition estimée est la suivante : {style_pct}. Cette combinaison est cohérente avec votre personnalité ({main}) et avec vos usages réels ({ctx_lbl}). "
            f"Concrètement, votre base doit rester confortable et mobile, parce que vous vivez des contextes où vous voulez être à l’aise sans perdre en présence ; "
            f"c’est ce qui justifie la composante Sporty Chic / Casual si elle est présente. En parallèle, votre message ({msgs_lbl}) impose une tenue qui reste maîtrisée : "
            f"des lignes propres, des coupes qui structurent, et un rendu soigné, même dans un look simple. Vos références de marque ({brands}) indiquent aussi une affinité "
            f"pour des pièces modernes et faciles à trouver, ce qui est un avantage pour construire une garde-robe cohérente. Enfin, vos refus (couleurs : {disliked_colors}, "
            f"motifs : {disliked_patterns}) orientent clairement vers un style plus élégant et plus net : on évitera les effets trop brillants ou trop agressifs, et on privilégiera "
            f"des détails féminins plus subtils, qui renforcent votre image sans la caricaturer."
        )
        return self._one_line(text)

    def _dynamic_what_defines_style_v2(
        self,
        prompt_data: Dict[str, Any],
        styles_top: List[Dict[str, Any]],
    ) -> str:
        pers = prompt_data.get("personality_data", {}) or {}
        ctx_lbl = ", ".join(self._labelize_situations(pers.get("selected_situations", []) or [])[:4]) or "votre quotidien"

        hi = self._join_list((prompt_data.get("morphology_goals", {}) or {}).get("body_parts_to_highlight", []), 3) or "vos atouts"
        mi = self._join_list((prompt_data.get("morphology_goals", {}) or {}).get("body_parts_to_minimize", []), 3) or "vos zones à adoucir"

        disliked_colors = self._join_list((prompt_data.get("color_preferences", {}) or {}).get("disliked_colors", []), 4) or "—"
        disliked_patterns = self._join_list((prompt_data.get("pattern_preferences", {}) or {}).get("disliked_patterns", []), 4) or "—"

        # Définition des styles (courte mais actionnable, intégrée au texte)
        style_defs = {
            "Style Sporty Chic": "un vestiaire confortable mais soigné, avec des pièces simples, des matières agréables, et une silhouette nette",
            "Style Urbain / Streetwear": "des coupes modernes, parfois un peu oversize ou structurées, et une attitude plus affirmée",
            "Style Casual / Décontracté": "des basiques faciles à associer, avec un rendu propre et des détails qui font la différence",
            "Style Féminin Moderne": "une féminité actuelle, des lignes épurées, des détails délicats sans excès, et une allure maîtrisée",
            "Style Romantique": "des matières plus souples, des touches délicates, des formes qui adoucissent sans faire “too much”",
            "Style Minimaliste": "peu d’effets, des coupes nettes, des harmonies calmes, et une impression de qualité par la simplicité",
            "Style Chic / Élégant": "des lignes structurées, des finitions propres, et une tenue qui renvoie immédiatement une image soignée",
            "Style Classique / Intemporel": "des pièces simples mais bien coupées, durables, et faciles à porter longtemps",
            "Style Naturel / Authentique": "des matières naturelles, un confort évident, une allure douce et vraie",
            "Style Moderne / Contemporain": "une silhouette actuelle, des proportions maîtrisées, et des pièces qui donnent un twist moderne",
        }

        picked = [x["style"] for x in styles_top]
        defs = []
        for st in picked:
            if st in style_defs:
                defs.append(f"{st.replace('Style ', '')} : {style_defs[st]}")
        defs_str = " ; ".join(defs) if defs else "une combinaison équilibrée entre confort, structure et féminité"

        text = (
            f"Votre style personnalisé va orienter vos tenues vers une silhouette à la fois lisible et facile à vivre, adaptée à vos contextes ({ctx_lbl}). "
            f"Les styles qui composent votre ADN se traduisent concrètement ainsi : {defs_str}. Dans la pratique, cela veut dire que nous allons privilégier des hauts "
            f"qui mettent en valeur {hi} (encolures travaillées, manches intéressantes, détails près du visage ou des épaules) et des bas qui harmonisent {mi} "
            f"(coupes plus fluides, longueurs plus équilibrées, lignes verticales et volumes maîtrisés). Votre style doit aussi respecter vos limites : vous avez indiqué "
            f"ne pas aimer {disliked_colors} et éviter {disliked_patterns}, donc nous allons construire une féminité moderne, sans brillance excessive et sans imprimés agressifs. "
            f"L’impact attendu sur vos tenues est très clair : des looks plus cohérents, plus flatteurs, et surtout plus simples à reproduire. Vous aurez des formules fiables "
            f"(par exemple un haut plus travaillé et féminin + un bas plus sobre et allongeant + une paire de chaussures propre et actuelle), ce qui vous permettra de garder "
            f"le confort nécessaire tout en renvoyant l’image de respect et de féminité que vous recherchez."
        )
        return self._one_line(text)


    def _dynamic_personality_translation(self, prompt_data: Dict[str, Any]) -> str:
        traits = self._join_list(prompt_data.get("personality_data", {}).get("selected_personality", []), 4)
        msgs = self._join_list(prompt_data.get("personality_data", {}).get("selected_message", []), 4)
        ctx = self._join_list(prompt_data.get("personality_data", {}).get("selected_situations", []), 4)

        styles = prompt_data.get("style_preferences", "")
        brands_list = prompt_data.get("brand_preferences", {}).get("selected_brands", [])
        brands = ", ".join(brands_list[:4]) if isinstance(brands_list, list) and brands_list else "vos marques habituelles"

        disliked_colors = self._join_list(prompt_data.get("color_preferences", {}).get("disliked_colors", []), 4)
        disliked_patterns = self._join_list(prompt_data.get("pattern_preferences", {}).get("disliked_patterns", []), 4)

        season = prompt_data.get("season", "")
        sil = prompt_data.get("silhouette_type", "")

        hi = self._join_list(prompt_data.get("morphology_goals", {}).get("body_parts_to_highlight", []), 3)
        mi = self._join_list(prompt_data.get("morphology_goals", {}).get("body_parts_to_minimize", []), 3)

        # On construit un texte "riche" mais en une seule string (parse-safe)
        text = (
            f"D’après vos réponses, vous avez une personnalité {traits} et vous cherchez à faire passer des messages "
            f"très clairs par vos tenues : {msgs}. Vos contextes de vie ({ctx}) vous demandent donc un style qui soit à la fois "
            f"simple à porter, cohérent et immédiatement lisible : vous ne voulez pas “réfléchir 20 minutes” devant le dressing, "
            f"mais vous souhaitez que la tenue produise l’effet attendu. Le fait que vous ayez cité {brands} et que vous ayez "
            f"indiqué une préférence de style ({styles}) montre que vous aimez quand c’est accessible et pratique, mais vous avez "
            f"besoin d’un niveau de finition supérieur dans l’allure pour exprimer {msgs}. "
            f"Nous allons aussi respecter vos limites : couleurs à éviter ({disliked_colors}) et motifs à éviter ({disliked_patterns}), "
            f"pour que vous vous sentiez sûre de vous sans vous forcer. Enfin, votre colorimétrie ({season}) et votre silhouette ({sil}) "
            f"seront des repères concrets : nous mettrons en avant {hi} et nous adoucirons {mi} grâce aux coupes, aux volumes et aux "
            f"contrastes bien placés. L’objectif est que vous vous reconnaissiez dans votre style, et que chaque tenue renforce votre image "
            f"avec naturel et intention."
        )

        return text

    @staticmethod
    def _resolve_path(data: Dict[str, Any], path: str) -> Any:
        """
        Résout un chemin type 'personality_data.selected_personality'
        dans un dict python.
        """
        cur: Any = data
        for part in path.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                return ""
        return cur

    @classmethod
    def safe_format(cls, template: str, data: Dict[str, Any]) -> str:
        """
        Remplace les placeholders {a.b.c} en résolvant les chemins dans `data`.
        On n'utilise pas format_map car il ne supporte pas les clés avec points.
        """
        def repl(match: re.Match) -> str:
            key = match.group(1).strip()
            val = cls._resolve_path(data, key)
            # Eviter les objets non sérialisables dans le prompt
            if isinstance(val, (dict, list)):
                try:
                    return json.dumps(val, ensure_ascii=False)
                except Exception:
                    return str(val)
            return str(val) if val is not None else ""

        # { ... } placeholders
        return re.sub(r"\{([^{}]+)\}", repl, template)

    @staticmethod
    def _ensure_str(x: Any, default: str = "") -> str:
        return x if isinstance(x, str) else default

    @staticmethod
    def _ensure_list(x: Any, default: List[Any] = None) -> List[Any]:
        if default is None:
            default = []
        return x if isinstance(x, list) else default

    @staticmethod
    def _ensure_dict(x: Any, default: Dict[str, Any] = None) -> Dict[str, Any]:
        if default is None:
            default = {}
        return x if isinstance(x, dict) else default

    # ---------------------------------------------------------------------
    # JSON repair (optional)
    # ---------------------------------------------------------------------
    async def force_valid_json(self, raw_content: str) -> dict:
        """
        Demande au modèle de renvoyer STRICTEMENT un JSON valide.
        """
        repair_prompt = f"""
Corrige le JSON suivant pour qu’il soit STRICTEMENT valide.
- AUCUN texte hors JSON
- AUCUN commentaire
- guillemets doubles uniquement
- aucune virgule finale

JSON À CORRIGER :
{raw_content}
""".strip()

        self.openai.set_context("Styling - JSON FIX", "")
        self.openai.set_system_prompt("Tu es un validateur JSON strict. Tu produis uniquement du JSON valide.")

        response = await self.openai.call_chat(
            prompt=repair_prompt,
            model="gpt-4",
            max_tokens=2000
        )

        content = response.get("content", "").strip()
        content_clean = self.clean_json_string(content)
        return json.loads(content_clean)

    # ---------------------------------------------------------------------
    # Main
    # ---------------------------------------------------------------------
    async def generate(self, colorimetry_result: dict, morphology_result: dict, user_data: dict) -> dict:
        """
        Génère le profil stylistique (1 appel OpenAI chat) selon schéma V2
        """
        print("\n" + "=" * 80)
        print("📋 APPEL STYLING: PROFIL STYLISTIQUE PREMIUM (V2)")
        print("=" * 80)

        try:
            # -------------------------
            # 1) Build flat data view for prompt placeholders
            # -------------------------
            palette = colorimetry_result.get("palette_personnalisee", []) or []
            top_colors = []
            for color in palette[:4]:
                if isinstance(color, dict):
                    top_colors.append(f"{color.get('name', 'Couleur')}: {color.get('hex', '')}")
            palette_str = ", ".join(top_colors) if top_colors else "Palette personnalisée"

            season = colorimetry_result.get("saison_confirmee", "Indéterminée")
            sous_ton = colorimetry_result.get("sous_ton_detecte", "")

            silhouette_type = morphology_result.get("silhouette_type", "?")
            recommendations = morphology_result.get("recommendations", {})
            # On laisse plutôt un résumé court mais utile
            recommendations_simple = f"Silhouette {silhouette_type}"
            if isinstance(recommendations, dict):
                recommendations_simple = json.dumps(recommendations, ensure_ascii=False)[:1200]

            # user_data extractions (onboarding)
            style_preferences = user_data.get("style_preferences", [])
            style_preferences = style_preferences if isinstance(style_preferences, list) else [str(style_preferences)]

            brand_preferences = user_data.get("brand_preferences", {}) or {}
            selected_brands = brand_preferences.get("selected_brands", []) if isinstance(brand_preferences, dict) else []
            custom_brands = brand_preferences.get("custom_brands", []) if isinstance(brand_preferences, dict) else []
            all_brands = []
            if isinstance(selected_brands, list):
                all_brands.extend(selected_brands)
            if isinstance(custom_brands, list):
                all_brands.extend(custom_brands)
            all_brands = [b for b in all_brands if isinstance(b, str) and b.strip()]
            brand_preferences_str = ", ".join(all_brands[:8]) if all_brands else "Aucune"

            color_preferences = user_data.get("color_preferences", {}) or {}
            disliked_colors = color_preferences.get("disliked_colors", []) if isinstance(color_preferences, dict) else []
            pattern_preferences = user_data.get("pattern_preferences", {}) or {}
            disliked_patterns = pattern_preferences.get("disliked_patterns", []) if isinstance(pattern_preferences, dict) else []

            personality_data = user_data.get("personality_data", {}) or {}
            morphology_goals = user_data.get("morphology_goals", {}) or {}
            personal_info = user_data.get("personal_info", {}) or {}    
            style_preferences_raw = style_preferences  # ici style_preferences est déjà ta liste issue de user_data

            print("DEBUG styling.py loaded from:", __file__)
            print("DEBUG has personal_info:", "personal_info" in locals())
            print("DEBUG personal_info value:", personal_info)

            prompt_data = {
                "season": season,
                "sous_ton": sous_ton,
                "palette": palette_str,
                "silhouette_type": silhouette_type,
                "recommendations": recommendations_simple,
                "personal_info": personal_info,
                "style_preferences_raw": style_preferences_raw,

                # champs "plats" (OK)
                "style_preferences": ", ".join(style_preferences[:6]) if style_preferences else "Non précisé",

                # ✅ IMPORTANT : ici il faut le dict complet, pas une string
                "brand_preferences": brand_preferences,

                # Full nested dicts for dotted placeholders
                "personality_data": personality_data,
                "color_preferences": color_preferences,
                "pattern_preferences": pattern_preferences,
                "morphology_goals": morphology_goals,
            }

            print("\n📌 AVANT APPEL:")
            print(f"   • Model: gpt-4")
            print(f"   • Saison: {season} ({sous_ton})")
            print(f"   • Palette: {palette_str}")
            print(f"   • Silhouette: {silhouette_type}")
            print(f"   • Styles: {', '.join(style_preferences[:6]) if style_preferences else 'Non précisé'}")
            print(f"   • Marques: {brand_preferences_str}")

            # -------------------------
            # 2) Call OpenAI
            # -------------------------
            self.openai.set_context("Styling", "")
            self.openai.set_system_prompt(STYLING_SYSTEM_PROMPT)

            user_prompt = self.safe_format(STYLING_USER_PROMPT, prompt_data)

            response = await self.openai.call_chat(
                prompt=user_prompt,
                model="gpt-4",
                max_tokens=3500
            )

            content = (response.get("content", "") or "").strip()
            print("\n📝 RÉPONSE BRUTE (premiers 400 chars):")
            print(f"   {content[:400]}...")

            # -------------------------
            # 3) Parse JSON robust
            # -------------------------
            result: Dict[str, Any] = {}
            try:
                content_clean = self.clean_json_string(content)
                result = json.loads(content_clean)
                print("   ✅ Parsing direct OK")
            except json.JSONDecodeError as e:
                print(f"   ❌ JSON invalide (styling): {e}")
                # Repair attempt
                try:
                    fixed = await self.force_valid_json(content)
                    if isinstance(fixed, dict):
                        result = fixed
                        print("   ✅ JSON réparé via OpenAI (Styling - JSON FIX)")
                except Exception as repair_err:
                    print(f"   ⚠️ Réparation JSON impossible: {repair_err}")
                    result = {}

                # raw extraction fallback
                if not result:
                    try:
                        start = content.find("{")
                        end = content.rfind("}") + 1
                        if start != -1 and end > start:
                            json_str = content[start:end]
                            result = json.loads(json_str)
                            print("   ✅ Extraction JSON brute OK")
                    except Exception as e2:
                        print(f"   ❌ Extraction brute KO: {e2}")
                        result = {}

            # -------------------------
            # 4) Normalize schema V2 + fallback safe
            # -------------------------
            result = self._normalize_styling_schema_v2(result, prompt_data)

            # Quick stats for logs
            sig_kw = self._ensure_list(result.get("stylistic_identity", {}).get("signature_keywords", []))
            hero = self._ensure_list(result.get("capsule_wardrobe", {}).get("hero_pieces", []))
            outfits_daily = self._ensure_list(result.get("signature_outfits", {}).get("everyday", []))
            print("\n📌 RÉSUMÉ:")
            print(f"   • Signature keywords: {len(sig_kw)}")
            print(f"   • Hero pieces: {len(hero)}")
            print(f"   • Everyday outfits: {len(outfits_daily)}")

            print("\n" + "=" * 80 + "\n")
            return result

        except Exception as e:
            print(f"\n❌ ERREUR STYLING: {e}")
            call_tracker.log_error("Styling", str(e))
            import traceback
            traceback.print_exc()
            raise

    # ---------------------------------------------------------------------
    # Schema normalization
    # ---------------------------------------------------------------------
    def _normalize_styling_schema_v2(self, result: Dict[str, Any], prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assure que toutes les clés du schéma V2 existent + types corrects.
        Ajoute des fallbacks premium si manquants.
        """
        if not isinstance(result, dict):
            result = {}

        # --- Top level sections
        result["stylistic_identity"] = self._ensure_dict(result.get("stylistic_identity"), {})
        result["psycho_stylistic_profile"] = self._ensure_dict(result.get("psycho_stylistic_profile"), {})
        result["contextual_style_logic"] = self._ensure_dict(result.get("contextual_style_logic"), {})
        result["style_dna"] = self._ensure_dict(result.get("style_dna"), {})
        result["style_within_constraints"] = self._ensure_dict(result.get("style_within_constraints"), {})
        result["capsule_wardrobe"] = self._ensure_dict(result.get("capsule_wardrobe"), {})
        result["mix_and_match_rules"] = self._ensure_dict(result.get("mix_and_match_rules"), {})
        result["signature_outfits"] = self._ensure_dict(result.get("signature_outfits"), {})
        result["style_evolution_plan"] = self._ensure_dict(result.get("style_evolution_plan"), {})

        # --- stylistic_identity
        si = result["stylistic_identity"]

        # Calculs: archetypes + styles (basés sur tes IDs)
        personality_data = prompt_data.get("personality_data", {}) or {}
        ar_scores = self._score_archetypes(personality_data)
        ar_main, ar_secondary = self._top_archetypes(ar_scores)

        stylescore = self._score_styles(
            style_preferences=prompt_data.get("style_preferences_raw", []),
            brand_preferences=prompt_data.get("brand_preferences", {}) or {},
            color_preferences=prompt_data.get("color_preferences", {}) or {},
            pattern_preferences=prompt_data.get("pattern_preferences", {}) or {},
            archetypes_main=ar_main,
            archetypes_secondary=ar_secondary,
        )
        styles_top = self._pick_top_styles_with_percentages(stylescore, max_styles=3)

        # 1) style_statement (court mais personnalisé)
        ss = self._ensure_str(si.get("style_statement"), "")
        if not ss:
            # phrase courte qui reprend le top style et l'intention
            main_style = styles_top[0]["style"].replace("Style ", "")
            si["style_statement"] = self._one_line(
                f"Je construis un style {main_style.lower()}, féminin et maîtrisé, qui reste confortable mais renvoie une image structurée et crédible."
            )
        else:
            si["style_statement"] = self._one_line(ss)

        # 2) personality_translation : 150+ mots, archétypes + justifications
        pt = self._ensure_str(si.get("personality_translation"), "")
        if not self._ensure_min_words(pt, 150):
            generated = self._dynamic_personality_translation_v2(prompt_data, ar_main, ar_secondary)
            # fallback si encore trop court
            if not self._ensure_min_words(generated, 150):
                generated = generated + " L’objectif est de vous donner des repères concrets, cohérents avec votre personnalité, vos contraintes et votre quotidien, afin que vous puissiez vous habiller plus vite, avec plus de confiance, et obtenir un rendu féminin et crédible sans effort."
            si["personality_translation"] = self._one_line(generated)
        else:
            si["personality_translation"] = self._one_line(pt)


        # 3) style_positioning : 150+ mots, styles + justifications
        sp = self._ensure_str(si.get("style_positioning"), "")
        if not self._ensure_min_words(sp, 150):
            si["style_positioning"] = self._dynamic_style_positioning_v2(prompt_data, ar_main, styles_top)
        else:
            si["style_positioning"] = self._one_line(sp)

        # 4) signature_keywords : format "Style — XX%"
        sk = si.get("signature_keywords")
        if not isinstance(sk, list) or len(sk) < 2:
            si["signature_keywords"] = [f'{x["style"].replace("Style ", "")} — {x["pct"]}%' for x in styles_top]
        else:
            # normaliser en strings
            si["signature_keywords"] = [self._one_line(str(x)) for x in sk if str(x).strip()]

        # --- psycho_stylistic_profile (traits UI labels)
        pp = result["psycho_stylistic_profile"]
        traits_ids = (personality_data.get("selected_personality") or [])
        traits_labels = self._labelize_traits(traits_ids)
        pp["core_personality_traits"] = traits_labels[:5] if traits_labels else self._ensure_list(pp.get("core_personality_traits"), [])

        # how_they_express_in_style (optionnel : laisser modèle ou fallback)
        pp_ht = self._ensure_str(pp.get("how_they_express_in_style"), "")
        if not pp_ht:
            pp["how_they_express_in_style"] = self._one_line(
                "Votre style s’exprime par un équilibre entre présence et douceur : des pièces confortables mais nettes, avec un détail féminin maîtrisé (encolure, manche, texture) qui signe la tenue."
            )
        else:
            pp["how_they_express_in_style"] = self._one_line(pp_ht)

        # balance_between_comfort_and_elegance (optionnel)
        pp_bal = self._ensure_str(pp.get("balance_between_comfort_and_elegance"), "")
        if not pp_bal:
            pp["balance_between_comfort_and_elegance"] = self._one_line(
                "Votre équilibre idéal : une base confortable et mobile au quotidien, mais toujours structurée par une coupe nette et une finition soignée, pour rester crédible et féminine sans effort."
            )
        else:
            pp["balance_between_comfort_and_elegance"] = self._one_line(pp_bal)

        # --- style_dna
        dna = result["style_dna"]

        wd = self._ensure_str(dna.get("what_defines_the_style"), "")
        if not self._ensure_min_words(wd, 150):
            dna["what_defines_the_style"] = self._dynamic_what_defines_style_v2(prompt_data, styles_top)
        else:
            dna["what_defines_the_style"] = self._one_line(wd)


        # --- constraints
        sc = result["style_within_constraints"]
        sc["morphology_guidelines"] = self._ensure_str(sc.get("morphology_guidelines"),
            "Valoriser le haut du corps (encolures, détails, structure d’épaules) et alléger visuellement le bas (lignes simples, teintes plus sobres).")
        sc["color_logic"] = self._ensure_str(sc.get("color_logic"),
            f"Rester dans votre harmonie {prompt_data.get('season','')} : tons chauds et riches près du visage, éviter les teintes trop froides.")
        sc["how_constraints_refine_the_style"] = self._ensure_str(sc.get("how_constraints_refine_the_style"),
            "Les contraintes deviennent votre force : elles guident vers un style cohérent, flatteur et facile à décliner.")

        # --- capsule
        cap = result["capsule_wardrobe"]
        cap["essentials"] = self._ensure_list(cap.get("essentials"), [
            "pantalon taille haute droit",
            "top uni de qualité (col V / col bateau)",
            "veste structurée courte",
            "robe ceinturée midi",
            "jupe évasée sobre"
        ])
        cap["hero_pieces"] = self._ensure_list(cap.get("hero_pieces"), [
            "blazer cintré couleur chaude",
            "chemise avec détail féminin discret",
            "robe patineuse élégante"
        ])
        cap["why_this_capsule_works"] = self._ensure_str(cap.get("why_this_capsule_works"),
            "Peu de pièces, mais très combinables : elles respectent votre silhouette, votre colorimétrie et votre besoin d’élégance naturelle.")

        # --- mix_and_match_rules
        mm = result["mix_and_match_rules"]
        mm["silhouette_balance"] = self._ensure_str(mm.get("silhouette_balance"),
            "Haut plus travaillé + bas plus sobre. Jouer sur la structure en haut et la simplicité en bas.")
        mm["color_associations"] = self._ensure_str(mm.get("color_associations"),
            "Base neutre chaude (écru, camel, kaki) + accent (brique, terracotta, bordeaux) + métal chaud (doré/cuivre).")
        mm["outfit_formulas"] = self._ensure_list(mm.get("outfit_formulas"), [
            "Top clair structuré + pantalon taille haute foncé + veste courte",
            "Robe ceinturée midi + chaussures élancées + bijou lumineux",
            "Jean droit + chemise féminine + blazer cintré"
        ])

        # --- signature_outfits
        so = result["signature_outfits"]
        so["everyday"] = self._ensure_list(so.get("everyday"), [
            "Jean droit foncé + top col V + veste courte + baskets compensées",
            "Jupe évasée sobre + blouse à détails + bottines"
        ])
        so["academic_or_professional"] = self._ensure_list(so.get("academic_or_professional"), [
            "Pantalon taille haute + top uni + blazer cintré + escarpins pointus",
            "Robe midi ceinturée + manteau structuré + accessoires minimalistes"
        ])
        so["events"] = self._ensure_list(so.get("events"), [
            "Robe élégante (brique/bordeaux) + sandales à lanières + bijoux dorés",
            "Ensemble ton sur ton chaud + pochette + escarpins"
        ])

        # --- plan
        plan = result["style_evolution_plan"]
        plan["week_1_focus"] = self._ensure_str(plan.get("week_1_focus"),
            "Clarifier vos bases : identifier les 10 pièces les plus portées et celles qui ne vous servent plus.")
        plan["week_2_focus"] = self._ensure_str(plan.get("week_2_focus"),
            "Structurer la silhouette : intégrer 2 pièces “structure haut” (blazer, top travaillé, encolure).")
        plan["week_3_focus"] = self._ensure_str(plan.get("week_3_focus"),
            "Harmoniser la palette : ajouter 2 couleurs signatures compatibles saison et faciles à associer.")
        plan["week_4_focus"] = self._ensure_str(plan.get("week_4_focus"),
            "Finaliser votre signature : 2 looks complets prêts pour événements + accessoires cohérents.")

        return result


# ✅ INSTANCE GLOBALE
styling_service = StylingService()
