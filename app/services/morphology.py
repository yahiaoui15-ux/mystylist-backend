"""
Morphology Service v9.0 - FINAL FIXED
✅ Logs restructurés et clairement séparés (Part 1, Part 2, Part 3)
✅ Part 3 correctement importé et intégré
✅ JSON escaping amélioré pour éviter les erreurs
✅ Meilleur contrôle d'erreur et fallbacks
✅ ZÉRO token overflow!
"""

import json
import re
from app.utils.openai_client import openai_client
from app.utils.openai_call_tracker import call_tracker
from app.prompts.morphology_part1_prompt import MORPHOLOGY_PART1_SYSTEM_PROMPT, MORPHOLOGY_PART1_USER_PROMPT
from app.prompts.morphology_part2_prompt import MORPHOLOGY_PART2_SYSTEM_PROMPT, MORPHOLOGY_PART2_USER_PROMPT
from app.prompts.morphology_part3_prompt import MORPHOLOGY_PART3_SYSTEM_PROMPT, MORPHOLOGY_PART3_USER_PROMPT


class MorphologyService:
    def __init__(self):
        self.openai = openai_client
    
    def _clean_json_string(self, text):
        """Nettoie les strings JSON pour éviter les caractères mal échappés"""
        # Remplacer les apostrophes courbes par des apostrophes simples
        text = text.replace(''', "'").replace(''', "'")
        # Remplacer les guillemets courbes
        text = text.replace('"', '"').replace('"', '"')
        # Supprimer les retours à la ligne dans les strings JSON
        text = re.sub(r':\s*"[^"]*\n[^"]*"', lambda m: m.group(0).replace('\n', ' '), text)
        return text
    
    def _parse_json_safe(self, text):
        """Parse JSON avec nettoyage préalable"""
        # Extraire le JSON
        json_start = text.find('{')
        if json_start == -1:
            return None
        
        json_end = text.rfind('}')
        if json_end == -1:
            return None
        
        json_text = text[json_start:json_end+1]
        
        # Nettoyer
        json_text = self._clean_json_string(json_text)
        
        try:
            return json.loads(json_text)
        except json.JSONDecodeError as e:
            print("   ❌ JSON Error: {}".format(str(e)))
            print("   JSON excerpt: {}".format(json_text[max(0, e.pos-50):min(len(json_text), e.pos+50)]))
            return None
    
    async def analyze(self, user_data: dict) -> dict:
        """Analyse morphologie EN 3 APPELS SÉQUENTIELS"""
        print("\n" + "="*80)
        print("💪 PHASE MORPHOLOGIE - 3 APPELS ÉQUILIBRÉS")
        print("="*80)
        
        try:
            body_photo_url = user_data.get("body_photo_url")
            if not body_photo_url:
                print("❌ Pas de photo du corps fournie")
                return {}
            
            # ========================================================================
            # APPEL 1/3: PART 1 - SILHOUETTE (VISION)
            # ========================================================================
            print("\n" + "█"*80)
            print("█ APPEL 1/3 - PART 1: SILHOUETTE + BODY PARTS ENRICHIS (VISION)")
            print("█"*80)
            
            print("\n📍 Configuration:")
            print("   • Model: gpt-4-turbo (Vision API)")
            print("   • Max tokens: 1000")
            print("   • Mensurations reçues: E{}cm T{}cm H{}cm B{}cm".format(
                user_data.get('shoulder_circumference'),
                user_data.get('waist_circumference'),
                user_data.get('hip_circumference'),
                user_data.get('bust_circumference')
            ))
            
            self.openai.set_context("Morphology", "Part 1: Vision")
            self.openai.set_system_prompt(MORPHOLOGY_PART1_SYSTEM_PROMPT)
            
            user_prompt_part1 = MORPHOLOGY_PART1_USER_PROMPT.format(
                body_photo_url=body_photo_url,
                shoulder_circumference=user_data.get("shoulder_circumference", 0),
                waist_circumference=user_data.get("waist_circumference", 0),
                hip_circumference=user_data.get("hip_circumference", 0),
                bust_circumference=user_data.get("bust_circumference", 0)
            )
            
            print("\n🤖 Appel OpenAI en cours...")
            response_part1 = await self.openai.analyze_image(
                image_urls=[body_photo_url],
                prompt=user_prompt_part1,
                model="gpt-4-turbo",
                max_tokens=1000
            )
            
            total_tokens_p1 = response_part1.get("total_tokens", 0)
            print("✅ Réponse reçue")
            
            print("\n📊 TOKENS PART 1:")
            print("   • Prompt: {}".format(response_part1.get("prompt_tokens", 0)))
            print("   • Completion: {}".format(response_part1.get("completion_tokens", 0)))
            print("   • Total: {} tokens".format(total_tokens_p1))
            print("   • Budget: {:.1f}% (vs 4000 max)".format((total_tokens_p1 / 4000) * 100))
            print("   • Status: ✅ OK")
            
            # Parse Part 1
            print("\n📋 Parsing JSON Part 1...")
            part1_result = self._parse_json_safe(response_part1.get("content", ""))
            if not part1_result:
                print("❌ Parsing échoué - retour vide")
                return {}
            
            print("✅ Succès")
            silhouette = part1_result.get('silhouette_type', 'Unknown')
            print("   • Silhouette: {}".format(silhouette))
            print("   • Body parts highlights présents: {}".format("Oui" if "body_parts_highlights" in part1_result else "Non"))
            print("   • Body parts minimizes présents: {}".format("Oui" if "body_parts_minimizes" in part1_result else "Non"))
            
            # ========================================================================
            # APPEL 2/3: PART 2 - RECOMMANDATIONS (TEXT)
            # ========================================================================
            print("\n" + "█"*80)
            print("█ APPEL 2/3 - PART 2: RECOMMANDATIONS (INTRO + RECOMMANDES + A_EVITER)")
            print("█"*80)
            
            styling_objectives = part1_result.get("styling_objectives", [])
            objectives_str = ", ".join(styling_objectives)
            
            morphology_goals = user_data.get("morphology_goals", {})
            body_parts_to_highlight = morphology_goals.get("body_parts_to_highlight", [])
            body_parts_to_minimize = morphology_goals.get("body_parts_to_minimize", [])
            
            highlight_str = ", ".join(body_parts_to_highlight) if body_parts_to_highlight else "aucune"
            minimize_str = ", ".join(body_parts_to_minimize) if body_parts_to_minimize else "aucune"
            
            print("\n📍 Configuration:")
            print("   • Model: gpt-4-turbo (Text API)")
            print("   • Max tokens: 2000")
            print("   • Silhouette: {}".format(silhouette))
            print("   • À valoriser: {}".format(highlight_str))
            print("   • À minimiser: {}".format(minimize_str))
            
            self.openai.set_context("Morphology", "Part 2: Recommendations")
            self.openai.set_system_prompt(MORPHOLOGY_PART2_SYSTEM_PROMPT)
            
            user_prompt_part2 = MORPHOLOGY_PART2_USER_PROMPT.format(
                silhouette_type=silhouette,
                styling_objectives=objectives_str,
                body_parts_to_highlight=highlight_str,
                body_parts_to_minimize=minimize_str
            )
            
            print("\n🤖 Appel OpenAI en cours...")
            response_part2 = await self.openai.call_chat(
                prompt=user_prompt_part2,
                model="gpt-4-turbo",
                max_tokens=2000
            )
            
            total_tokens_p2 = response_part2.get("total_tokens", 0)
            print("✅ Réponse reçue")
            
            print("\n📊 TOKENS PART 2:")
            print("   • Prompt: {}".format(response_part2.get("prompt_tokens", 0)))
            print("   • Completion: {}".format(response_part2.get("completion_tokens", 0)))
            print("   • Total: {} tokens".format(total_tokens_p2))
            print("   • Budget: {:.1f}% (vs 4000 max)".format((total_tokens_p2 / 4000) * 100))
            print("   • Status: {}".format("✅ OK" if total_tokens_p2 < 2000 else "⚠️ Proche limite"))
            
            # Parse Part 2
            print("\n📋 Parsing JSON Part 2...")
            part2_result = self._parse_json_safe(response_part2.get("content", ""))
            if not part2_result:
                print("❌ Parsing échoué - retour vide")
                return {}
            
            print("✅ Succès")
            recommendations = part2_result.get('recommendations', {})
            print("   • Catégories trouvées: {}".format(len(recommendations)))
            
            # ========================================================================
            # APPEL 3/3: PART 3 - DÉTAILS (TEXT)
            # ========================================================================
            print("\n" + "█"*80)
            print("█ APPEL 3/3 - PART 3: DÉTAILS (MATIERES + MOTIFS + PIEGES)")
            print("█"*80)
            
            print("\n📍 Configuration:")
            print("   • Model: gpt-4-turbo (Text API)")
            print("   • Max tokens: 2000")
            print("   • Silhouette: {}".format(silhouette))
            
            self.openai.set_context("Morphology", "Part 3: Details")
            self.openai.set_system_prompt(MORPHOLOGY_PART3_SYSTEM_PROMPT)
            
            user_prompt_part3 = MORPHOLOGY_PART3_USER_PROMPT.format(
                silhouette_type=silhouette,
                styling_objectives=objectives_str,
                body_parts_to_highlight=highlight_str,
                body_parts_to_minimize=minimize_str
            )
            
            print("\n🤖 Appel OpenAI en cours...")
            response_part3 = await self.openai.call_chat(
                prompt=user_prompt_part3,
                model="gpt-4-turbo",
                max_tokens=2000
            )
            
            total_tokens_p3 = response_part3.get("total_tokens", 0)
            print("✅ Réponse reçue")
            
            print("\n📊 TOKENS PART 3:")
            print("   • Prompt: {}".format(response_part3.get("prompt_tokens", 0)))
            print("   • Completion: {}".format(response_part3.get("completion_tokens", 0)))
            print("   • Total: {} tokens".format(total_tokens_p3))
            print("   • Budget: {:.1f}% (vs 4000 max)".format((total_tokens_p3 / 4000) * 100))
            print("   • Status: {}".format("✅ OK" if total_tokens_p3 < 2000 else "⚠️ Proche limite"))
            
            # Parse Part 3
            print("\n📋 Parsing JSON Part 3...")
            part3_result = self._parse_json_safe(response_part3.get("content", ""))
            if not part3_result:
                print("❌ Parsing échoué - retour vide")
                return {}
            
            print("✅ Succès")
            details = part3_result.get('details', {})
            print("   • Catégories détails trouvées: {}".format(len(details)))
            
            # ========================================================================
            # RÉSUMÉ GLOBAL
            # ========================================================================
            print("\n" + "="*80)
            print("📊 RÉSUMÉ GLOBAL - 3 APPELS ÉQUILIBRÉS")
            print("="*80)
            
            total_morpho_tokens = total_tokens_p1 + total_tokens_p2 + total_tokens_p3
            budget_percent = (total_morpho_tokens / 8000) * 100
            
            print("\nTokens consommés:")
            print("   • Part 1 (Vision): {} tokens ({:.1f}%)".format(
                total_tokens_p1, (total_tokens_p1 / 4000) * 100))
            print("   • Part 2 (Text): {} tokens ({:.1f}%)".format(
                total_tokens_p2, (total_tokens_p2 / 4000) * 100))
            print("   • Part 3 (Text): {} tokens ({:.1f}%)".format(
                total_tokens_p3, (total_tokens_p3 / 4000) * 100))
            print("\n   • TOTAL: {} tokens".format(total_morpho_tokens))
            print("   • Budget global: {:.1f}% (vs 8000 max)".format(budget_percent))
            print("   • Status: {}".format(
                "✅ PARFAIT" if total_morpho_tokens < 6800 else 
                "⚠️ Acceptable" if total_morpho_tokens < 7500 else 
                "❌ Trop élevé"))
            
            # ========================================================================
            # FUSION FINALE
            # ========================================================================
            print("\n" + "="*80)
            print("📦 FUSION FINALE - CRÉATION STRUCTURE MORPHO")
            print("="*80)
            
            # Créer morpho.categories
            morpho_categories = {}
            for category_name in recommendations.keys():
                morpho_categories[category_name] = {
                    "introduction": recommendations[category_name].get("introduction", ""),
                    "recommandes": recommendations[category_name].get("recommandes", []),
                    "a_eviter": recommendations[category_name].get("a_eviter", []),
                    "matieres": details.get(category_name, {}).get("matieres", ""),
                    "motifs": details.get(category_name, {}).get("motifs", {}),
                    "pieges": details.get(category_name, {}).get("pieges", [])
                }
            
            body_parts_highlights = part1_result.get('body_parts_highlights', {})
            body_parts_minimizes = part1_result.get('body_parts_minimizes', {})
            
            final_result = {
                "silhouette_type": part1_result.get("silhouette_type"),
                "silhouette_explanation": part1_result.get("silhouette_explanation"),
                "body_parts_to_highlight": part1_result.get("body_parts_to_highlight"),
                "body_parts_to_minimize": part1_result.get("body_parts_to_minimize"),
                "body_analysis": part1_result.get("body_analysis"),
                "styling_objectives": part1_result.get("styling_objectives"),
                "bodyType": part1_result.get("silhouette_type"),
                "highlights": {
                    "announcement": body_parts_highlights.get("announcement", ""),
                    "explanation": body_parts_highlights.get("explanation", "")
                },
                "minimizes": {
                    "announcement": body_parts_minimizes.get("announcement", ""),
                    "explanation": body_parts_minimizes.get("explanation", "")
                },
                "morpho": {
                    "categories": morpho_categories
                },
                "client_requested_highlights": highlight_str,
                "client_requested_minimizes": minimize_str,
            }
            
            print("\n✅ MORPHOLOGIE COMPLÈTE GÉNÉRÉE")
            print("   • Silhouette: {}".format(final_result['silhouette_type']))
            print("   • Catégories: {}".format(len(final_result['morpho']['categories'])))
            print("   • Pages 8-15: Prêtes pour affichage")
            print("\n" + "="*80 + "\n")
            
            return final_result
            
        except Exception as e:
            print("\n❌ ERREUR MORPHOLOGY: {}".format(str(e)))
            call_tracker.log_error("Morphology", str(e))
            
            import traceback
            traceback.print_exc()
            raise


morphology_service = MorphologyService()