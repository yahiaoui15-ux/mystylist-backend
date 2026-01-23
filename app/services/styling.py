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
from app.prompts.styling_prompt_part1 import STYLING_PART1_SYSTEM_PROMPT, STYLING_PART1_USER_PROMPT
from app.prompts.styling_prompt_part2 import STYLING_PART2_SYSTEM_PROMPT, STYLING_PART2_USER_PROMPT
from app.prompts.styling_prompt_part3 import STYLING_PART3_SYSTEM_PROMPT, STYLING_PART3_USER_PROMPT



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

    def _as_dict(self, x) -> Dict[str, Any]:
        if isinstance(x, dict):
            return x
        if isinstance(x, str) and x.strip():
            try:
                return json.loads(x)
            except Exception:
                return {}
        return {}

    def _as_list(self, x) -> List[Any]:
        if isinstance(x, list):
            return x
        if isinstance(x, str) and x.strip():
            try:
                v = json.loads(x)
                return v if isinstance(v, list) else [x]
            except Exception:
                return [x]
        return []

    def _as_int_str(self, x) -> str:
        if x is None:
            return ""
        if isinstance(x, (int, float)):
            return str(int(x)) if isinstance(x, float) and x.is_integer() else str(x)
        return str(x)



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
    def _is_part2_complete(self, d: Dict[str, Any]) -> bool:
        try:
            p18 = (d.get("page18") or {}).get("categories") or {}
            p19 = (d.get("page19") or {}).get("categories") or {}
            ok = (
                isinstance(p18.get("tops"), list) and len(p18["tops"]) == 3 and
                isinstance(p18.get("bottoms"), list) and len(p18["bottoms"]) == 3 and
                isinstance(p18.get("dresses_playsuits"), list) and len(p18["dresses_playsuits"]) == 3 and
                isinstance(p18.get("outerwear"), list) and len(p18["outerwear"]) == 3 and
                isinstance(p19.get("swim_lingerie"), list) and len(p19["swim_lingerie"]) == 3 and
                isinstance(p19.get("shoes"), list) and len(p19["shoes"]) == 3 and
                isinstance(p19.get("accessories"), list) and len(p19["accessories"]) == 3
            )
            return bool(ok)
        except Exception:
            return False

    def _is_part3_complete(self, d: Dict[str, Any]) -> bool:
        try:
            p20 = d.get("page20") or {}
            formulas = p20.get("formulas") or []
            if not (isinstance(formulas, list) and len(formulas) == 3):
                return False

            p24 = d.get("page24") or {}
            if not (isinstance(p24.get("actions"), list) and len(p24["actions"]) == 3):
                return False
            if not (isinstance(p24.get("pre_outing_checklist"), list) and 6 <= len(p24["pre_outing_checklist"]) <= 10):
                return False

            p2123 = d.get("pages21_23") or {}
            for fk in ["formula_1", "formula_2", "formula_3"]:
                fobj = p2123.get(fk) or {}
                for ctx in ["professional", "weekend", "evening"]:
                    cobj = fobj.get(ctx) or {}
                    slots = cobj.get("product_slots") or []
                    if not (isinstance(slots, list) and 4 <= len(slots) <= 6):
                        return False
            return True
        except Exception:
            return False

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
        Génère le profil stylistique (3 appels OpenAI chat) selon schéma V2
        """
        print("\n" + "=" * 80)
        print("📋 APPEL STYLING: PROFIL STYLISTIQUE PREMIUM (V3)")
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

            # --- Normalisation robuste user_data / onboarding_data ---
            ud = user_data if isinstance(user_data, dict) else {}
            profile = ud.get("profile") or {}
            onb = self._as_dict(
                ud.get("onboarding_data")
                or profile.get("onboarding_data")
                or {}
)


            # =========================
            # DEBUG PATCH 1: INPUT user_data + onboarding_data (masked)
            # =========================
            def _mask(x: Any) -> Any:
                if not isinstance(x, dict):
                    return x
                y = dict(x)
                if "personal_info" in y and isinstance(y["personal_info"], dict):
                    pi = dict(y["personal_info"])
                    for k in ["first_name", "last_name", "postal_code"]:
                        if k in pi and pi[k]:
                            pi[k] = "***"
                    y["personal_info"] = pi
                return y

            print("DEBUG user_data type:", type(user_data).__name__)
            print("DEBUG user_data top keys:", list(ud.keys())[:30])
            print("DEBUG profile keys:", list((profile or {}).keys())[:30])

            src = (
                "ud.onboarding_data" if ud.get("onboarding_data") else
                "profile.onboarding_data" if (profile or {}).get("onboarding_data") else
                "NONE"
            )
            print("DEBUG onboarding_data source:", src)
            print("DEBUG onboarding_data parsed keys:", list(onb.keys())[:30])

            print("DEBUG ud snapshot (masked):", json.dumps(_mask({
                "style_preferences": ud.get("style_preferences") or onb.get("style_preferences"),
                "personality_data": ud.get("personality_data") or onb.get("personality_data"),
                "brand_preferences": ud.get("brand_preferences") or onb.get("brand_preferences"),
                "color_preferences": ud.get("color_preferences") or onb.get("color_preferences"),
                "pattern_preferences": ud.get("pattern_preferences") or onb.get("pattern_preferences"),
                "morphology_goals": ud.get("morphology_goals") or onb.get("morphology_goals"),
                "personal_info": ud.get("personal_info") or onb.get("personal_info"),
                "measurements": ud.get("measurements") or onb.get("measurements"),
                "eye_color": ud.get("eye_color") or onb.get("eye_color"),
                "hair_color": ud.get("hair_color") or onb.get("hair_color"),
                "onboarding_data_ud": ud.get("onboarding_data"),
                "onboarding_data_profile": (profile or {}).get("onboarding_data"),
            }), ensure_ascii=False)[:1200])


            def pick(key, default):
                v = ud.get(key, None)
                if v in [None, "", [], {}]:
                    v = onb.get(key, None)
                return default if v is None else v

            # Récupération brute
            personality_data    = pick("personality_data", {})
            morphology_goals    = pick("morphology_goals", {})
            personal_info       = pick("personal_info", {})
            measurements        = pick("measurements", {})
            eye_color           = pick("eye_color", "")
            hair_color          = pick("hair_color", "")
            style_preferences   = pick("style_preferences", [])
            brand_preferences   = pick("brand_preferences", {})
            color_preferences   = pick("color_preferences", {})
            pattern_preferences = pick("pattern_preferences", {})

            # ✅ Parsing robustes (gère dict/list en JSON string)
            personality_data    = self._as_dict(personality_data)
            morphology_goals    = self._as_dict(morphology_goals)
            personal_info       = self._as_dict(personal_info)
            measurements        = self._as_dict(measurements)
            brand_preferences   = self._as_dict(brand_preferences)
            color_preferences   = self._as_dict(color_preferences)
            pattern_preferences = self._as_dict(pattern_preferences)
            style_preferences   = self._as_list(style_preferences)

            # =========================
            # DEBUG PATCH 2: RESOLVED values (post-pick, post-parse)
            # =========================
            print("DEBUG resolved (post-pick, post-parse):")
            print(" - style_preferences:", style_preferences)
            print(" - personality_data:", personality_data)
            print(" - brand_preferences:", brand_preferences)
            print(" - color_preferences:", color_preferences)
            print(" - pattern_preferences:", pattern_preferences)
            print(" - morphology_goals:", morphology_goals)

            print("DEBUG counts:",
                  "traits", len((personality_data or {}).get("selected_personality", []) or []),
                  "msgs", len((personality_data or {}).get("selected_message", []) or []),
                  "ctx", len((personality_data or {}).get("selected_situations", []) or []),
                  "styles", len(style_preferences) if isinstance(style_preferences, list) else 0,
                  "brands",
                  len(((brand_preferences or {}).get("selected_brands", []) or [])) + len(((brand_preferences or {}).get("custom_brands", []) or [])))

            # ✅ fallback flattened si jamais personal_info/measurements vides
            if not personal_info:
                personal_info = {
                    "age": ud.get("age", ud.get("user_age", "")),
                    "height": ud.get("height", ud.get("user_height", "")),
                    "weight": ud.get("weight", ud.get("user_weight", "")),
                }
            if not measurements:
                measurements = {
                    "clothing_size": ud.get("clothing_size", ud.get("clothingSize", "")),
                    "number_size": ud.get("number_size", ""),
                    "hip_circumference": ud.get("hip_circumference", ""),
                    "waist_circumference": ud.get("waist_circumference", ""),
                    "shoulder_circumference": ud.get("shoulder_circumference", ""),
                }

            # ✅ Cast valeurs en string
            personal_info = {
                "age": self._as_int_str(personal_info.get("age", "")),
                "height": self._as_int_str(personal_info.get("height", "")),
                "weight": self._as_int_str(personal_info.get("weight", "")),
            }
            measurements = {
                "clothing_size": self._as_int_str(measurements.get("clothing_size", "")),
                "number_size": self._as_int_str(measurements.get("number_size", "")),
                "hip_circumference": self._as_int_str(measurements.get("hip_circumference", "")),
                "waist_circumference": self._as_int_str(measurements.get("waist_circumference", "")),
                "shoulder_circumference": self._as_int_str(measurements.get("shoulder_circumference", "")),
            }

            # ✅ brands_list + brand_preferences_str
            brands_list = []
            sb = brand_preferences.get("selected_brands", []) or []
            cb = brand_preferences.get("custom_brands", []) or []
            if isinstance(sb, list): brands_list += [b for b in sb if isinstance(b, str) and b.strip()]
            if isinstance(cb, list): brands_list += [b for b in cb if isinstance(b, str) and b.strip()]
            brand_preferences_str = ", ".join(brands_list[:8]) if brands_list else "Aucune"

            print("DEBUG types:",
                "personality_data", type(personality_data).__name__,
                "style_preferences", type(style_preferences).__name__,
                "brand_preferences", type(brand_preferences).__name__)

            print("DEBUG onboarding presence:",
                "traits", len((personality_data or {}).get("selected_personality", []) or []),
                "msgs", len((personality_data or {}).get("selected_message", []) or []),
                "ctx", len((personality_data or {}).get("selected_situations", []) or []),
                "styles", len(style_preferences) if isinstance(style_preferences, list) else 0)

            # ✅ Construire prompt_data APRES parsing
            prompt_data = {
                "season": season,
                "sous_ton": sous_ton,
                "palette": palette_str,
                "silhouette_type": silhouette_type,
                "recommendations": recommendations_simple,

                "personal_info": personal_info,
                "measurements": measurements,
                "eye_color": eye_color,
                "hair_color": hair_color,

                "style_preferences": style_preferences,
                "style_preferences_str": ", ".join([str(s) for s in style_preferences[:6]]) if style_preferences else "",

                "brand_preferences": brand_preferences,
                "personality_data": personality_data,
                "color_preferences": color_preferences,
                "pattern_preferences": pattern_preferences,
                "morphology_goals": morphology_goals,
            }

            # types sûrs
            style_preferences = style_preferences if isinstance(style_preferences, list) else [str(style_preferences)] if style_preferences else []
            brand_preferences = brand_preferences if isinstance(brand_preferences, dict) else {}
            color_preferences = color_preferences if isinstance(color_preferences, dict) else {}
            pattern_preferences = pattern_preferences if isinstance(pattern_preferences, dict) else {}
            personality_data = personality_data if isinstance(personality_data, dict) else {}
            morphology_goals = morphology_goals if isinstance(morphology_goals, dict) else {}

            style_preferences_raw = style_preferences  # ici style_preferences est déjà ta liste issue de user_data

            print("DEBUG styling.py loaded from:", __file__)
            print("DEBUG has personal_info:", "personal_info" in locals())
            print("DEBUG personal_info value:", personal_info)
            print("DEBUG onboarding presence:",
                  "traits", len((personality_data or {}).get("selected_personality", []) or []),
                  "msgs", len((personality_data or {}).get("selected_message", []) or []),
                  "ctx", len((personality_data or {}).get("selected_situations", []) or []),
                  "styles", len(style_preferences) if isinstance(style_preferences, list) else 0)

            print("DEBUG types:",
                "personality_data", type(personality_data).__name__,
                "style_preferences", type(style_preferences).__name__,
                "brand_preferences", type(brand_preferences).__name__)

            print("\n📌 AVANT APPEL:")
            print(f"   • Model: gpt-4")
            print(f"   • Saison: {season} ({sous_ton})")
            print(f"   • Palette: {palette_str}")
            print(f"   • Silhouette: {silhouette_type}")
            print(f"   • Styles: {', '.join(style_preferences[:6]) if style_preferences else 'Non précisé'}")
            print(f"   • Marques: {brand_preferences_str}")

            # -------------------------
            # 2) Call OpenAI (3 parts)
            # -------------------------

            async def _call_part(
                name: str,
                system_prompt: str,
                user_prompt_template: str,
                max_tokens: int
            ) -> Dict[str, Any]:

                def _pick_tokens() -> int:
                    # On donne plus de marge aux parties longues
                    if name == "PART2":
                        return max(max_tokens, 3200)
                    if name == "PART3":
                        return max(max_tokens, 3400)
                    return max_tokens

                def _extract_json_object(text: str) -> Dict[str, Any]:
                    if not isinstance(text, str):
                        return {}
                    t = self.clean_json_string(text)
                    # parse direct
                    try:
                        obj = json.loads(t)
                        return obj if isinstance(obj, dict) else {}
                    except Exception:
                        pass
                    # fallback extraction
                    try:
                        start = t.find("{")
                        end = t.rfind("}") + 1
                        if start != -1 and end > start:
                            obj = json.loads(t[start:end])
                            return obj if isinstance(obj, dict) else {}
                    except Exception:
                        pass
                    return {}

                async def _single_call(extra_guard: str = "", tokens_override: int = None) -> Dict[str, Any]:
                    self.openai.set_context(f"Styling {name}", "")
                    self.openai.set_system_prompt(system_prompt)

                    user_prompt = self.safe_format(user_prompt_template, prompt_data)
                    
                    # =========================
                    # DEBUG PATCH 3: prompt_data summary actually sent
                    # =========================
                    print(f"DEBUG {name} prompt_data summary:",
                          json.dumps({
                              "style_preferences": prompt_data.get("style_preferences"),
                              "personality_data": prompt_data.get("personality_data"),
                              "brand_preferences": prompt_data.get("brand_preferences"),
                              "color_preferences": prompt_data.get("color_preferences"),
                              "pattern_preferences": prompt_data.get("pattern_preferences"),
                              "morphology_goals": prompt_data.get("morphology_goals"),
                              "season": prompt_data.get("season"),
                              "silhouette_type": prompt_data.get("silhouette_type"),
                          }, ensure_ascii=False)[:1200])

                    # Guard en tête (évite d’être “ignoré” en fin de prompt)
                    if extra_guard:
                        user_prompt = extra_guard.strip() + "\n\n" + user_prompt

                    resp = await self.openai.call_chat(
                        prompt=user_prompt,
                        model="gpt-4",
                        max_tokens=tokens_override or _pick_tokens(),
                    )

                    content = (resp.get("content", "") or "").strip()
                    return _extract_json_object(content)

                # ---------------------------------------------------------
                # 1) Essai standard
                # ---------------------------------------------------------
                out = await _single_call()

                # ---------------------------------------------------------
                # 2) Retry si incomplet (PART2 / PART3)
                # ---------------------------------------------------------
                if name == "PART2" and not self._is_part2_complete(out):
                    guard = (
                        "IMPORTANT — JSON COMPLET OBLIGATOIRE.\n"
                        "- Tu dois remplir TOUTES les catégories avec EXACTEMENT 3 items.\n"
                        "- Si tu manques de place, raccourcis UNIQUEMENT les textes (spec/why/tips/promo), "
                        "mais NE LAISSE JAMAIS un tableau vide.\n"
                        "- Interdiction de supprimer des clés, interdiction de renvoyer du texte hors JSON.\n"
                        "- Si tu es proche de la limite, fais des phrases plus courtes, mais garde la quantité.\n"
                    )
                    out2 = await _single_call(extra_guard=guard, tokens_override=3600)
                    if self._is_part2_complete(out2):
                        out = out2

                if name == "PART3" and not self._is_part3_complete(out):
                    guard = (
                        "IMPORTANT — JSON COMPLET OBLIGATOIRE.\n"
                        "- page20.formulas = EXACTEMENT 3 items.\n"
                        "- Chaque product_slots = 4 à 6 items (page20 + pages21_23).\n"
                        "- page24.actions = EXACTEMENT 3.\n"
                        "- page24.pre_outing_checklist = 6 à 10.\n"
                        "- Si tu manques de place, raccourcis UNIQUEMENT les textes (explanations/benefits), "
                        "mais ne réduis pas la quantité d'items.\n"
                        "- Interdiction de supprimer des clés, interdiction de renvoyer du texte hors JSON.\n"
                    )
                    out2 = await _single_call(extra_guard=guard, tokens_override=3800)
                    if self._is_part3_complete(out2):
                        out = out2

                return out

            part1 = await _call_part("PART1", STYLING_PART1_SYSTEM_PROMPT, STYLING_PART1_USER_PROMPT, max_tokens=2200)
            part2 = await _call_part("PART2", STYLING_PART2_SYSTEM_PROMPT, STYLING_PART2_USER_PROMPT, max_tokens=3000)
            part3 = await _call_part("PART3", STYLING_PART3_SYSTEM_PROMPT, STYLING_PART3_USER_PROMPT, max_tokens=3200)
            
            # ✅ DEBUG COUNTS AVANT MERGE (pour confirmer que PART2/PART3 ne sont pas vides)
            def _len_safe(x):
                return len(x) if isinstance(x, list) else 0

            p18 = (part2.get("page18", {}).get("categories", {}) if isinstance(part2, dict) else {})
            p19 = (part2.get("page19", {}).get("categories", {}) if isinstance(part2, dict) else {})
            p20 = (part3.get("page20", {}) if isinstance(part3, dict) else {})
            fml = (p20.get("formulas") if isinstance(p20.get("formulas"), list) else [])

            print("DEBUG PART2 counts:",
                "tops", _len_safe(p18.get("tops")),
                "bottoms", _len_safe(p18.get("bottoms")),
                "dresses_playsuits", _len_safe(p18.get("dresses_playsuits")),
                "outerwear", _len_safe(p18.get("outerwear")),
                "swim_lingerie", _len_safe(p19.get("swim_lingerie")),
                "shoes", _len_safe(p19.get("shoes")),
                "accessories", _len_safe(p19.get("accessories")))

            print("DEBUG PART3 counts:",
                "page20.formulas", _len_safe(fml),
                "p24.actions", _len_safe((part3.get("page24", {}) or {}).get("actions")),
                "p24.checklist", _len_safe((part3.get("page24", {}) or {}).get("pre_outing_checklist")))

            # Merge (attention: ne pas écraser les clés)
            result: Dict[str, Any] = {}
            if isinstance(part1, dict):
                result.update(part1)
            if isinstance(part2, dict):
                result.update(part2)
            if isinstance(part3, dict):
                result.update(part3)

            # -------------------------
            # 3) Normalize schema V3 (pages 16–24)
            # -------------------------
            result = self._normalize_styling_schema_v3(result)

            print("DEBUG onboarding_data type:", type(ud.get("onboarding_data")).__name__)
            print("DEBUG onboarding_data parsed keys:", list(onb.keys())[:10])

            print("\n📌 RÉSUMÉ (V3):")
            print("   • page16 keys:", list((result.get("page16") or {}).keys())[:8])
            print("   • page17 keys:", list((result.get("page17") or {}).keys())[:8])
            print("   • page18 categories:", list((((result.get("page18") or {}).get("categories")) or {}).keys()))
            print("   • page20 formulas:", len(((result.get("page20") or {}).get("formulas")) or []))
            print("   • pages21_23 formula_1:", list(((result.get("pages21_23") or {}).get("formula_1") or {}).keys()))

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
    def _normalize_styling_schema_v3(self, result: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(result, dict):
            result = {}

        # Sections attendues par le template (TOUJOURS d'abord)
        result["page16"] = self._ensure_dict(result.get("page16"), {})
        result["page17"] = self._ensure_dict(result.get("page17"), {})
        result["page18"] = self._ensure_dict(result.get("page18"), {})
        result["page19"] = self._ensure_dict(result.get("page19"), {})
        result["page20"] = self._ensure_dict(result.get("page20"), {})
        result["pages21_23"] = self._ensure_dict(result.get("pages21_23"), {})
        result["page24"] = self._ensure_dict(result.get("page24"), {})

        # BACKWARD/DUAL SCHEMA SUPPORT (page16): map new nested blocks -> flat keys
        p16 = result.get("page16") or {}
        if isinstance(p16, dict):
            ab = p16.get("archetype_block") or {}
            if isinstance(ab, dict):
                if not p16.get("archetype_text"):
                    p16["archetype_text"] = self._one_line(self._ensure_str(ab.get("text"), ""))
                if not isinstance(p16.get("dominant_traits"), list):
                    p16["dominant_traits"] = self._ensure_list(ab.get("traits_dominants_detectes"), [])

            sgb = p16.get("style_goals_block") or {}
            if isinstance(sgb, dict):
                if not p16.get("objectifs_emotionnels_text"):
                    p16["objectifs_emotionnels_text"] = self._one_line(self._ensure_str(sgb.get("emotional_goals"), ""))
                if not p16.get("objectifs_pratiques_text"):
                    p16["objectifs_pratiques_text"] = self._one_line(self._ensure_str(sgb.get("practical_goals"), ""))
                if not p16.get("objectifs_morphologiques_text"):
                    p16["objectifs_morphologiques_text"] = self._one_line(self._ensure_str(sgb.get("morphology_goals"), ""))

            spb = p16.get("style_preferences_block") or {}
            if isinstance(spb, dict) and not p16.get("preferences_style_text"):
                p16["preferences_style_text"] = self._one_line(self._ensure_str(spb.get("text"), ""))

            if not p16.get("boussole_text"):
                p16["boussole_text"] = self._one_line(self._ensure_str(p16.get("compass_sentence"), ""))

            # Ensure lists exist
            p16["dominant_traits"] = self._ensure_list(p16.get("dominant_traits"), [])

            result["page16"] = p16

        # page18/page19 categories structure
        for pkey in ["page18", "page19"]:
            p = result[pkey]
            p["headline"] = self._one_line(self._ensure_str(p.get("headline"), ""))

            cats = self._ensure_dict(p.get("categories"), {})
            p["categories"] = cats

        # Ensure page18 categories keys
        p18 = result["page18"]["categories"]
        p18.setdefault("tops", [])
        p18.setdefault("bottoms", [])
        p18.setdefault("dresses_playsuits", [])
        p18.setdefault("outerwear", [])

        # Ensure page19 categories keys
        p19 = result["page19"]["categories"]
        p19.setdefault("swim_lingerie", [])
        p19.setdefault("shoes", [])
        p19.setdefault("accessories", [])

        # Normalize items shape (piece_title/spec)
        def _norm_piece_list(items):
            items = items if isinstance(items, list) else []
            out = []
            for it in items:
                if isinstance(it, dict):
                    out.append({
                        "piece_title": self._one_line(self._ensure_str(it.get("piece_title"), "")),
                        "spec": self._one_line(self._ensure_str(it.get("spec"), "")),
                        "recommended_colors": self._ensure_list(it.get("recommended_colors"), []),
                        "recommended_patterns": self._ensure_list(it.get("recommended_patterns"), []),
                        "accessories_pairing": self._one_line(self._ensure_str(it.get("accessories_pairing"), "")),
                        "why_for_you": self._one_line(self._ensure_str(it.get("why_for_you"), "")),
                    })
            return out


        for k in ["tops", "bottoms", "dresses_playsuits", "outerwear"]:
            result["page18"]["categories"][k] = _norm_piece_list(result["page18"]["categories"].get(k))

        for k in ["swim_lingerie", "shoes", "accessories"]:
            result["page19"]["categories"][k] = _norm_piece_list(result["page19"]["categories"].get(k))

        # page19 tips block
        result["page19"]["tips_block"] = self._one_line(self._ensure_str(result["page19"].get("tips_block"), ""))

        # page20 formulas
        p20 = result["page20"]
        p20["intro"] = self._one_line(self._ensure_str(p20.get("intro"), ""))
        formulas = p20.get("formulas")
        formulas = formulas if isinstance(formulas, list) else []
        norm_formulas = []
        for f in formulas:
            if not isinstance(f, dict):
                continue
            ps = f.get("product_slots")
            ps = ps if isinstance(ps, list) else []
            norm_slots = []
            for s in ps:
                if isinstance(s, dict):
                    norm_slots.append({
                        "slot_type": self._one_line(self._ensure_str(s.get("slot_type"), "")),
                        "slot_description": self._one_line(self._ensure_str(s.get("slot_description"), "")),
                        "preferred_colors": self._ensure_list(s.get("preferred_colors"), []),
                        "avoid": self._ensure_list(s.get("avoid"), []),
                    })
            norm_formulas.append({
                "formula_name": self._one_line(self._ensure_str(f.get("formula_name"), "")),
                "formula_explanation": self._one_line(self._ensure_str(f.get("formula_explanation"), "")),
                "benefit_to_you": self._one_line(self._ensure_str(f.get("benefit_to_you"), "")),
                "finishing_touches": self._one_line(self._ensure_str(f.get("finishing_touches"), "")),
                "mannequin_outfit_brief": self._one_line(self._ensure_str(f.get("mannequin_outfit_brief"), "")),
                "product_slots": norm_slots,
            })
        p20["formulas"] = norm_formulas

        # pages21_23
        p2123 = result["pages21_23"]
        for fk in ["formula_1", "formula_2", "formula_3"]:
            fobj = self._ensure_dict(p2123.get(fk), {})
            p2123[fk] = fobj
            for ctx in ["professional", "weekend", "evening"]:
                cobj = self._ensure_dict(fobj.get(ctx), {})
                fobj[ctx] = cobj
                cobj["explanation"] = self._one_line(self._ensure_str(cobj.get("explanation"), ""))
                cobj["mannequin_outfit_brief"] = self._one_line(self._ensure_str(cobj.get("mannequin_outfit_brief"), ""))
                slots = cobj.get("product_slots")
                slots = slots if isinstance(slots, list) else []
                norm_slots = []
                for s in slots:
                    if isinstance(s, dict):
                        norm_slots.append({
                            "slot_type": self._one_line(self._ensure_str(s.get("slot_type"), "")),
                            "slot_description": self._one_line(self._ensure_str(s.get("slot_description"), "")),
                            "preferred_colors": self._ensure_list(s.get("preferred_colors"), []),
                            "avoid": self._ensure_list(s.get("avoid"), []),
                        })
                cobj["product_slots"] = norm_slots

        # page24
        p24 = result["page24"]
        p24["actions"] = self._ensure_list(p24.get("actions"), [])
        p24["pre_outing_checklist"] = self._ensure_list(p24.get("pre_outing_checklist"), [])
        p24["wardrobe_advice"] = self._one_line(self._ensure_str(p24.get("wardrobe_advice"), ""))
        p24["platform_tips_my_stylist"] = self._one_line(self._ensure_str(p24.get("platform_tips_my_stylist"), ""))

        return result



# ✅ INSTANCE GLOBALE
styling_service = StylingService()
