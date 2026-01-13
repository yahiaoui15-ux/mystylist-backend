"""
Styling Service v4.0 - Compatible prompt premium + personnalité
✅ Support placeholders avec points {a.b.c}
✅ JSON parsing robuste + réparation
✅ Normalisation du schéma V2 (stylistic_identity, capsule, outfits, plan…)
✅ Instance styling_service exportée
"""

import json
import re
from typing import Any, Dict, List

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

            prompt_data = {
                "season": season,
                "sous_ton": sous_ton,
                "palette": palette_str,
                "silhouette_type": silhouette_type,
                "recommendations": recommendations_simple,

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
        si["style_positioning"] = self._ensure_str(si.get("style_positioning"),
            "Une élégance naturelle, structurée et facile à vivre, pensée pour votre quotidien réel.")
        si["personality_translation"] = self._ensure_str(si.get("personality_translation"),
            "Votre style doit refléter une féminité maîtrisée : naturelle, raffinée, avec une touche romantique subtile.")
        si["signature_keywords"] = self._ensure_list(si.get("signature_keywords"),
            ["élégance naturelle", "silhouette structurée", "minimal chic", "féminité subtile", "raffinement simple"])
        si["style_statement"] = self._ensure_str(si.get("style_statement"),
            "Je privilégie des pièces épurées et bien coupées, avec des détails féminins discrets, pour une allure soignée sans effort.")

        # --- psycho_stylistic_profile
        pp = result["psycho_stylistic_profile"]
        pp["core_personality_traits"] = self._ensure_list(pp.get("core_personality_traits"), ["romantique", "naturelle", "raffinée"])
        pp["how_they_express_in_style"] = self._ensure_str(pp.get("how_they_express_in_style"),
            "Des matières agréables, des lignes lisibles, et un détail délicat (encolure, bouton, bijou) qui signe la tenue.")
        pp["balance_between_comfort_and_elegance"] = self._ensure_str(pp.get("balance_between_comfort_and_elegance"),
            "Votre équilibre idéal : confort au toucher + structure visuelle. Une tenue simple, mais jamais négligée.")

        # --- contextual_style_logic
        cs = result["contextual_style_logic"]
        cs["daily_life"] = self._ensure_str(cs.get("daily_life"),
            "Priorité à des tenues rapides à composer, confortables, mais structurées : bases neutres + une pièce qui élève la silhouette.")
        cs["family_and_social"] = self._ensure_str(cs.get("family_and_social"),
            "Miser sur une féminité accessible : robes fluides structurées, ensembles ton sur ton, accessoires harmonisés.")
        cs["events_and_special_occasions"] = self._ensure_str(cs.get("events_and_special_occasions"),
            "Élégance affirmée : matières plus nobles, lignes verticales, détail lumineux (métal chaud, texture satinée).")

        # --- style_dna
        dna = result["style_dna"]
        dna["core_styles"] = self._ensure_list(dna.get("core_styles"), ["classique", "minimaliste"])
        dna["secondary_styles"] = self._ensure_list(dna.get("secondary_styles"), ["romantique discret", "décontracté chic"])
        dna["what_defines_the_style"] = self._ensure_str(dna.get("what_defines_the_style"),
            "Des coupes nettes, des matières qualitatives, une palette harmonieuse, et des détails féminins subtils.")
        dna["what_is_consciously_avoided"] = self._ensure_str(dna.get("what_is_consciously_avoided"),
            "Éviter les imprimés animaliers et les contrastes agressifs. Préférer l’élégance douce à l’effet “too much”.")

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
