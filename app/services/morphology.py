"""
Morphology Service v5.0 - COMPLET AVEC DEMANDES CLIENT
✅ Part 1 (Vision): 800 tokens max
✅ Part 2 (Text): 3000 tokens max - AUGMENTÉ pour JSON complet
✅ NOUVEAU: Intègre body_parts_to_highlight et body_parts_to_minimize du client
✅ Logs complets par appel (like colorimetry)
"""

import json
from app.utils.openai_client import openai_client
from app.utils.openai_call_tracker import call_tracker
from app.prompts.morphology_part1_prompt import MORPHOLOGY_PART1_SYSTEM_PROMPT, MORPHOLOGY_PART1_USER_PROMPT
from app.prompts.morphology_part2_prompt import MORPHOLOGY_PART2_SYSTEM_PROMPT, MORPHOLOGY_PART2_USER_PROMPT


class MorphologyService:
    def __init__(self):
        self.openai = openai_client
    
    async def analyze(self, user_data: dict) -> dict:
        """Analyse morphologie EN 2 APPELS SÉQUENTIELS"""
        print("\n" + "="*80)
        print("💪 PHASE MORPHOLOGIE (2 appels)")
        print("="*80)
        
        try:
            body_photo_url = user_data.get("body_photo_url")
            if not body_photo_url:
                print("❌ Pas de photo du corps fournie")
                return {}
            
            # ========================================================================
            # APPEL 1/2: MORPHOLOGY PART 1 - SILHOUETTE (VISION)
            # ========================================================================
            print("\n" + "█"*80)
            print("█ APPEL 1/2: MORPHOLOGY PART 1 - SILHOUETTE + BODY ANALYSIS (VISION)")
            print("█"*80)
            
            print("\n📍 AVANT APPEL:")
            print("   • Type: OpenAI Vision API (gpt-4-turbo)")
            print("   • Max tokens: 800")
            print("   • Image: " + body_photo_url[:60] + "...")
            print("   • Mensurations:")
            print("      - Épaules: {} cm".format(user_data.get('shoulder_circumference')))
            print("      - Taille: {} cm".format(user_data.get('waist_circumference')))
            print("      - Hanches: {} cm".format(user_data.get('hip_circumference')))
            print("      - Buste: {} cm".format(user_data.get('bust_circumference')))
            
            self.openai.set_context("Morphology Part 1", "PART 1: Silhouette")
            self.openai.set_system_prompt(MORPHOLOGY_PART1_SYSTEM_PROMPT)
            
            user_prompt_part1 = MORPHOLOGY_PART1_USER_PROMPT.format(
                body_photo_url=body_photo_url,
                shoulder_circumference=user_data.get("shoulder_circumference", 0),
                waist_circumference=user_data.get("waist_circumference", 0),
                hip_circumference=user_data.get("hip_circumference", 0),
                bust_circumference=user_data.get("bust_circumference", 0)
            )
            
            print("\n🤖 APPEL OPENAI EN COURS...")
            response_part1 = await self.openai.analyze_image(
                image_urls=[body_photo_url],
                prompt=user_prompt_part1,
                model="gpt-4-turbo",
                max_tokens=800
            )
            print("✅ RÉPONSE REÇUE")
            
            content_part1 = response_part1.get("content", "")
            prompt_tokens_p1 = response_part1.get("prompt_tokens", 0)
            completion_tokens_p1 = response_part1.get("completion_tokens", 0)
            total_tokens_p1 = response_part1.get("total_tokens", 0)
            budget_percent_p1 = (total_tokens_p1 / 4000) * 100
            
            print("\n🔍 RÉPONSE BRUTE (premiers 400 chars):")
            print("   " + content_part1[:400])
            if len(content_part1) > 400:
                print("   ... [" + str(len(content_part1) - 400) + " chars supplémentaires]")
            
            print("\n📊 TOKENS CONSOMMÉS PART 1:")
            print("   • Prompt: {}".format(prompt_tokens_p1))
            print("   • Completion: {}".format(completion_tokens_p1))
            print("   • Total: {}".format(total_tokens_p1))
            print("   • Budget: {:.1f}% (vs 4000 max)".format(budget_percent_p1))
            print("   • Status: {}".format("✅ OK" if budget_percent_p1 < 100 else "⚠️ Limite" if budget_percent_p1 < 125 else "❌ DÉPASSEMENT"))
            
            # PARSING PART 1
            print("\n📋 PARSING JSON PART 1:")
            response_text = content_part1.strip() if content_part1 else ""
            
            # ✅ FIX: Strip markdown code blocks
            response_text = response_text.replace("```json\n", "").replace("```\n", "").replace("```", "")
            
            if not response_text:
                print("   ❌ Réponse vide")
                return {}
            
            json_start = response_text.find('{')
            if json_start == -1:
                print("   ❌ Pas de JSON trouvé")
                print("   Contenu: " + response_text[:200])
                return {}
            
            response_text = response_text[json_start:]
            json_end = response_text.rfind('}')
            if json_end == -1:
                print("   ❌ JSON incomplet (accolade fermante manquante)")
                return {}
            
            response_text = response_text[:json_end+1]
            
            try:
                part1_result = json.loads(response_text)
                print("   ✅ Succès")
                
                silhouette = part1_result.get('silhouette_type', 'Unknown')
                objectives = len(part1_result.get('styling_objectives', []))
                highlights = len(part1_result.get('body_parts_to_highlight', []))
                minimizes = len(part1_result.get('body_parts_to_minimize', []))
                
                print("      • Silhouette: {}".format(silhouette))
                print("      • Objectifs: {}".format(objectives))
                print("      • Parties valoriser: {}".format(highlights))
                print("      • Parties harmoniser: {}".format(minimizes))
                
                print("\n📦 RÉSULTAT PART 1 (premiers 600 chars):")
                print("   " + json.dumps(part1_result, ensure_ascii=False, indent=2)[:600] + "...")
                
            except json.JSONDecodeError as e:
                print("   ❌ Erreur parsing JSON: {}".format(str(e)))
                print("   JSON invalide: " + response_text[:300])
                return {}
            
            # ========================================================================
            # APPEL 2/2: MORPHOLOGY PART 2 - RECOMMANDATIONS (TEXT)
            # ========================================================================
            print("\n" + "█"*80)
            print("█ APPEL 2/2: MORPHOLOGY PART 2 - RECOMMANDATIONS STYLING (TEXT)")
            print("█"*80)
            
            styling_objectives = part1_result.get("styling_objectives", [])
            objectives_str = ", ".join(styling_objectives)
            
            # ✅ NOUVEAU: Récupérer les demandes spécifiques du client
            morphology_goals = user_data.get("morphology_goals", {})
            body_parts_to_highlight = morphology_goals.get("body_parts_to_highlight", [])
            body_parts_to_minimize = morphology_goals.get("body_parts_to_minimize", [])
            
            # Convertir en strings
            highlight_str = ", ".join(body_parts_to_highlight) if body_parts_to_highlight else "aucune spécifiée"
            minimize_str = ", ".join(body_parts_to_minimize) if body_parts_to_minimize else "aucune spécifiée"
            
            print("\n📍 AVANT APPEL:")
            print("   • Type: OpenAI Text API (gpt-4-turbo)")
            print("   • Max tokens: 3000 (✅ AUGMENTÉ pour JSON complet)")
            print("   • Silhouette reçue: {}".format(silhouette))
            print("   • Objectifs reçus: {}".format(objectives_str))
            print("   • À valoriser (cliente): {}".format(highlight_str))
            print("   • À minimiser (cliente): {}".format(minimize_str))
            
            self.openai.set_context("Morphology Part 2", "PART 2: Recommandations")
            self.openai.set_system_prompt(MORPHOLOGY_PART2_SYSTEM_PROMPT)
            
            # ✅ NOUVEAU: Passer les demandes du client au prompt
            user_prompt_part2 = MORPHOLOGY_PART2_USER_PROMPT.format(
                silhouette_type=silhouette,
                styling_objectives=objectives_str,
                body_parts_to_highlight=highlight_str,
                body_parts_to_minimize=minimize_str
            )
            
            print("\n🤖 APPEL OPENAI EN COURS...")
            response_part2 = await self.openai.call_chat(
                prompt=user_prompt_part2,
                model="gpt-4-turbo",
                max_tokens=3000
            )
            print("✅ RÉPONSE REÇUE")
            
            content_part2 = response_part2.get("content", "")
            prompt_tokens_p2 = response_part2.get("prompt_tokens", 0)
            completion_tokens_p2 = response_part2.get("completion_tokens", 0)
            total_tokens_p2 = response_part2.get("total_tokens", 0)
            budget_percent_p2 = (total_tokens_p2 / 4000) * 100
            
            print("\n🔍 RÉPONSE BRUTE (premiers 400 chars):")
            print("   " + content_part2[:400])
            if len(content_part2) > 400:
                print("   ... [" + str(len(content_part2) - 400) + " chars supplémentaires]")
            
            print("\n📊 TOKENS CONSOMMÉS PART 2:")
            print("   • Prompt: {}".format(prompt_tokens_p2))
            print("   • Completion: {}".format(completion_tokens_p2))
            print("   • Total: {}".format(total_tokens_p2))
            print("   • Budget: {:.1f}% (vs 4000 max)".format(budget_percent_p2))
            print("   • Status: {}".format("✅ OK" if budget_percent_p2 < 100 else "⚠️ Limite" if budget_percent_p2 < 125 else "❌ DÉPASSEMENT"))
            
            total_morpho_tokens = total_tokens_p1 + total_tokens_p2
            total_morpho_percent = (total_morpho_tokens / 4000) * 100
            print("\n📊 TOTAL MORPHOLOGIE (Part 1 + Part 2):")
            print("   • Part 1: {} tokens".format(total_tokens_p1))
            print("   • Part 2: {} tokens".format(total_tokens_p2))
            print("   • Total: {} tokens".format(total_morpho_tokens))
            print("   • Budget: {:.1f}% (vs 4000 max)".format(total_morpho_percent))
            print("   • Status: {}".format("✅ OK" if total_morpho_percent < 100 else "⚠️ Limite" if total_morpho_percent < 125 else "❌ DÉPASSEMENT"))
            
            # PARSING PART 2
            print("\n📋 PARSING JSON PART 2:")
            response_text = content_part2.strip() if content_part2 else ""
            
            # ✅ FIX: Strip markdown code blocks
            response_text = response_text.replace("```json\n", "").replace("```\n", "").replace("```", "")
            
            if not response_text:
                print("   ❌ Réponse vide")
                return {}
            
            json_start = response_text.find('{')
            if json_start == -1:
                print("   ❌ Pas de JSON trouvé")
                print("   Contenu: " + response_text[:200])
                return {}
            
            response_text = response_text[json_start:]
            json_end = response_text.rfind('}')
            if json_end == -1:
                print("   ❌ JSON incomplet (accolade fermante manquante)")
                return {}
            
            response_text = response_text[:json_end+1]
            
            try:
                part2_result = json.loads(response_text)
                print("   ✅ Succès")
                
                recommendations = part2_result.get('recommendations', {})
                categories = len(recommendations)
                
                print("      • Catégories: {}".format(categories))
                for cat in recommendations.keys():
                    a_priv = len(recommendations.get(cat, {}).get('a_privilegier', []))
                    a_eviter = len(recommendations.get(cat, {}).get('a_eviter', []))
                    print("      • {}: {} privilégier, {} éviter".format(cat, a_priv, a_eviter))
                
                print("\n📦 RÉSULTAT PART 2 (premiers 600 chars):")
                print("   " + json.dumps(part2_result, ensure_ascii=False, indent=2)[:600] + "...")
                
            except json.JSONDecodeError as e:
                print("   ❌ Erreur parsing JSON: {}".format(str(e)))
                print("   JSON invalide: " + response_text[:300])
                return {}
            
            # ========================================================================
            # FUSION PART 1 + PART 2
            # ========================================================================
            print("\n" + "="*80)
            print("📦 FUSION PART 1 + PART 2")
            print("="*80)
            
            final_result = {
                "silhouette_type": part1_result.get("silhouette_type"),
                "silhouette_explanation": part1_result.get("silhouette_explanation"),
                "body_parts_to_highlight": part1_result.get("body_parts_to_highlight"),
                "body_parts_to_minimize": part1_result.get("body_parts_to_minimize"),
                "body_analysis": part1_result.get("body_analysis"),
                "styling_objectives": part1_result.get("styling_objectives"),
                "bodyType": part1_result.get("silhouette_type"),
                "recommendations": part2_result.get("recommendations", {}),
                # ✅ NOUVEAU: Inclure les demandes du client pour traçabilité
                "client_requested_highlights": highlight_str,
                "client_requested_minimizes": minimize_str,
            }
            
            print("✅ Morphologie complète générée")
            print("   • Silhouette: {}".format(final_result['silhouette_type']))
            print("   • Catégories recommandations: {}".format(len(final_result['recommendations'])))
            print("   • Demandes client (valoriser): {}".format(highlight_str))
            print("   • Demandes client (minimiser): {}".format(minimize_str))
            print("   • Champs total: {}".format(len(final_result)))
            
            print("\n" + "="*80 + "\n")
            
            return final_result
            
        except Exception as e:
            print("\n❌ ERREUR MORPHOLOGY: {}".format(str(e)))
            call_tracker.log_error("Morphology", str(e))
            
            import traceback
            traceback.print_exc()
            raise


morphology_service = MorphologyService()