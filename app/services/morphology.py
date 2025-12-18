"""
Morphology Service v4.3 FIX v2 - GÉRER LE KEYERROR
✅ Catch la KeyError et ignore les clés manquantes du prompt
✅ Continue avec ce qu'on a
✅ Log ce qui manque pour debug
"""

import json
from app.utils.openai_client import openai_client
from app.utils.openai_call_tracker import call_tracker
from app.prompts.morphology_part1_prompt import MORPHOLOGY_PART1_SYSTEM_PROMPT, MORPHOLOGY_PART1_USER_PROMPT
from app.prompts.morphology_part2_prompt import MORPHOLOGY_PART2_SYSTEM_PROMPT, MORPHOLOGY_PART2_USER_PROMPT


class MorphologyService:
    def __init__(self):
        self.openai = openai_client
    
    @staticmethod
    def safe_format(template: str, **kwargs) -> str:
        """Format un template en ignorant les clés manquantes"""
        try:
            return template.format(**kwargs)
        except KeyError as e:
            missing_key = str(e).strip("'")
            print(f"⚠️ KeyError lors du .format(): {missing_key}")
            print("   Essayons avec format_map pour ignorer la clé...")
            
            # Créer un dict avec toutes les clés potentielles
            format_dict = {
                "body_photo_url": kwargs.get("body_photo_url", ""),
                "shoulder_circumference": kwargs.get("shoulder_circumference", ""),
                "waist_circumference": kwargs.get("waist_circumference", ""),
                "hip_circumference": kwargs.get("hip_circumference", ""),
                "bust_circumference": kwargs.get("bust_circumference", ""),
                "silhouette_type": kwargs.get("silhouette_type", ""),
                "styling_objectives": kwargs.get("styling_objectives", ""),
                "body_parts_to_highlight": kwargs.get("body_parts_to_highlight", ""),
                "body_parts_to_minimize": kwargs.get("body_parts_to_minimize", ""),
                "body_analysis": kwargs.get("body_analysis", ""),
            }
            
            try:
                result = template.format_map(format_dict)
                print(f"   ✅ format_map() réussi")
                return result
            except Exception as e2:
                print(f"   ❌ format_map() aussi échoué: {str(e2)}")
                return template
    
    async def analyze(self, user_data: dict) -> dict:
        """Analyse morphologie EN 2 APPELS SÉQUENTIELS"""
        print("\n" + "="*80)
        print("💪 PHASE MORPHOLOGIE v4.3 FIX v2 (2 appels)")
        print("="*80)
        
        body_photo_url = user_data.get("body_photo_url")
        if not body_photo_url:
            print("❌ Pas de photo du corps fournie")
            return {}
        
        part1_result = {}
        part2_result = {}
        
        try:
            # ========================================================================
            # APPEL 1/2: MORPHOLOGY PART 1 - SILHOUETTE (VISION)
            # ========================================================================
            print("\n" + "█"*80)
            print("█ APPEL 1/2: MORPHOLOGY PART 1 - SILHOUETTE + BODY ANALYSIS (VISION)")
            print("█"*80)
            
            print("\n📋 AVANT APPEL:")
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
            
            # 🔧 UTILISER SAFE_FORMAT
            user_prompt_part1 = self.safe_format(
                MORPHOLOGY_PART1_USER_PROMPT,
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
            
            print("\n📝 RÉPONSE BRUTE COMPLÈTE (Part 1) - {} chars total:".format(len(content_part1)))
            print("="*80)
            print(content_part1[:1000] if len(content_part1) > 1000 else content_part1)
            if len(content_part1) > 1000:
                print(f"... [{len(content_part1) - 1000} chars restants]")
            print("="*80)
            
            print("\n📊 TOKENS CONSOMMÉS PART 1:")
            print("   • Prompt: {}".format(prompt_tokens_p1))
            print("   • Completion: {}".format(completion_tokens_p1))
            print("   • Total: {}".format(total_tokens_p1))
            print("   • Budget: {:.1f}% (vs 4000 max)".format(budget_percent_p1))
            print("   • Status: {}".format("✅ OK" if budget_percent_p1 < 100 else "⚠️ Limite" if budget_percent_p1 < 125 else "❌ DÉPASSEMENT"))
            
            # PARSING PART 1
            print("\n🔍 PARSING JSON PART 1:")
            response_text = content_part1.strip() if content_part1 else ""
            
            if not response_text:
                print("   ⚠️ ERREUR: Réponse vide")
            else:
                print("   Longueur: {} chars".format(len(response_text)))
                
                json_start = response_text.find('{')
                if json_start == -1:
                    print("   ❌ Pas de JSON trouvé")
                    print("   Contenu: " + response_text[:200])
                else:
                    response_text = response_text[json_start:]
                    json_end = response_text.rfind('}')
                    if json_end == -1:
                        print("   ❌ JSON incomplet (accolade fermante manquante)")
                    else:
                        response_text = response_text[:json_end+1]
                        
                        try:
                            part1_result = json.loads(response_text)
                            print("   ✅ Parsing JSON réussi!")
                            
                            silhouette = part1_result.get('silhouette_type', 'Unknown')
                            objectives = len(part1_result.get('styling_objectives', []))
                            
                            print("      • Silhouette: {}".format(silhouette))
                            print("      • Objectifs: {}".format(objectives))
                            
                        except json.JSONDecodeError as e:
                            print("   ❌ Erreur parsing JSON: {}".format(str(e)))
                            print("   Première ligne: {}".format(response_text[:100]))
                            part1_result = {}
            
            # ========================================================================
            # APPEL 2/2: MORPHOLOGY PART 2 - RECOMMANDATIONS (TEXT)
            # ========================================================================
            print("\n" + "█"*80)
            print("█ APPEL 2/2: MORPHOLOGY PART 2 - RECOMMANDATIONS STYLING (TEXT)")
            print("█"*80)
            
            if part1_result and part1_result.get("silhouette_type"):
                silhouette = part1_result.get("silhouette_type")
                styling_objectives = part1_result.get("styling_objectives", [])
            else:
                print("   ⚠️ Part 1 vide, utilisant fallbacks")
                silhouette = "O"
                styling_objectives = ["Optimal"]
            
            objectives_str = ", ".join(styling_objectives) if styling_objectives else "Optimize"
            
            print("\n📋 AVANT APPEL:")
            print("   • Silhouette: {}".format(silhouette))
            print("   • Objectifs: {}".format(objectives_str))
            
            self.openai.set_context("Morphology Part 2", "PART 2: Recommandations")
            self.openai.set_system_prompt(MORPHOLOGY_PART2_SYSTEM_PROMPT)
            
            # 🔧 UTILISER SAFE_FORMAT
            user_prompt_part2 = self.safe_format(
                MORPHOLOGY_PART2_USER_PROMPT,
                silhouette_type=silhouette,
                styling_objectives=objectives_str
            )
            
            print("\n🤖 APPEL OPENAI EN COURS...")
            response_part2 = await self.openai.call_chat(
                prompt=user_prompt_part2,
                model="gpt-4-turbo",
                max_tokens=800
            )
            print("✅ RÉPONSE REÇUE")
            
            content_part2 = response_part2.get("content", "")
            prompt_tokens_p2 = response_part2.get("prompt_tokens", 0)
            completion_tokens_p2 = response_part2.get("completion_tokens", 0)
            total_tokens_p2 = response_part2.get("total_tokens", 0)
            budget_percent_p2 = (total_tokens_p2 / 4000) * 100
            
            print("\n📝 RÉPONSE BRUTE COMPLÈTE (Part 2) - {} chars total:".format(len(content_part2)))
            print("="*80)
            print(content_part2[:1000] if len(content_part2) > 1000 else content_part2)
            if len(content_part2) > 1000:
                print(f"... [{len(content_part2) - 1000} chars restants]")
            print("="*80)
            
            print("\n📊 TOKENS CONSOMMÉS PART 2:")
            print("   • Total: {}".format(total_tokens_p2))
            print("   • Budget: {:.1f}% (vs 4000 max)".format(budget_percent_p2))
            
            # PARSING PART 2
            print("\n🔍 PARSING JSON PART 2:")
            response_text = content_part2.strip() if content_part2 else ""
            
            if not response_text:
                print("   ⚠️ Réponse vide")
            else:
                json_start = response_text.find('{')
                if json_start == -1:
                    print("   ❌ Pas de JSON trouvé")
                else:
                    response_text = response_text[json_start:]
                    json_end = response_text.rfind('}')
                    if json_end > json_start:
                        response_text = response_text[:json_end+1]
                        
                        try:
                            part2_result = json.loads(response_text)
                            print("   ✅ Parsing JSON réussi!")
                            
                        except json.JSONDecodeError as e:
                            print("   ❌ Erreur parsing JSON: {}".format(str(e)))
                            part2_result = {}
            
            # ========================================================================
            # RÉSULTAT FINAL
            # ========================================================================
            print("\n" + "="*80)
            print("📦 RÉSULTAT FINAL")
            print("="*80)
            
            final_result = {
                "silhouette_type": part1_result.get("silhouette_type"),
                "silhouette_explanation": part1_result.get("silhouette_explanation"),
                "body_parts_to_highlight": part1_result.get("body_parts_to_highlight"),
                "body_parts_to_minimize": part1_result.get("body_parts_to_minimize"),
                "body_analysis": part1_result.get("body_analysis"),
                "styling_objectives": part1_result.get("styling_objectives"),
                "bodyType": part1_result.get("silhouette_type"),
                "recommendations": part2_result.get("recommendations", {})
            }
            
            print("✅ Résultat généré")
            print("\n" + "="*80 + "\n")
            
            return final_result
            
        except Exception as e:
            print("\n❌ EXCEPTION: {}".format(str(e)))
            call_tracker.log_error("Morphology", str(e))
            
            import traceback
            traceback.print_exc()
            
            # Retourner ce qu'on a même si erreur
            return {
                "silhouette_type": part1_result.get("silhouette_type"),
                "silhouette_explanation": part1_result.get("silhouette_explanation"),
                "body_parts_to_highlight": part1_result.get("body_parts_to_highlight"),
                "body_parts_to_minimize": part1_result.get("body_parts_to_minimize"),
                "body_analysis": part1_result.get("body_analysis"),
                "styling_objectives": part1_result.get("styling_objectives"),
                "bodyType": part1_result.get("silhouette_type"),
                "recommendations": part2_result.get("recommendations", {})
            }


morphology_service = MorphologyService()