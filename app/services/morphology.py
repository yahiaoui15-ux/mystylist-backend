"""
Morphology Service v4.1 - Syntaxe corrigée (pas de f-strings avec accolades)
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
        """Analyse morphologie EN 2 APPELS"""
        print("\n" + "="*80)
        print("💪 PHASE MORPHOLOGIE (2 appels)")
        print("="*80)
        
        try:
            body_photo_url = user_data.get("body_photo_url")
            if not body_photo_url:
                print("❌ Pas de photo du corps fournie")
                return {}
            
            # PART 1
            print("\n" + "█"*80)
            print("█ APPEL 1/2: MORPHOLOGY PART 1 - SILHOUETTE + BODY ANALYSIS")
            print("█"*80)
            
            print("\n📍 AVANT APPEL:")
            print("   • Type: OpenAI Vision API")
            print("   • Max tokens: 800")
            print("   • Image: " + body_photo_url[:60] + "...")
            print("   • Mensurations:")
            print("      - Épaules: {} cm".format(user_data.get('shoulder_circumference')))
            print("      - Taille: {} cm".format(user_data.get('waist_circumference')))
            print("      - Hanches: {} cm".format(user_data.get('hip_circumference')))
            print("      - Buste: {} cm".format(user_data.get('bust_circumference')))
            
            self.openai.set_context("Morphology Part 1", "PART 1")
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
            
            print("\n📊 TOKENS PART 1:")
            print("   • Prompt: {}".format(prompt_tokens_p1))
            print("   • Completion: {}".format(completion_tokens_p1))
            print("   • Total: {}".format(total_tokens_p1))
            print("   • Budget: {:.1f}%".format(budget_percent_p1))
            
            # Parse Part 1
            print("\n📋 PARSING JSON PART 1:")
            response_text = content_part1.strip() if content_part1 else ""
            
            if not response_text:
                print("   ❌ Réponse vide")
                return {}
            
            json_start = response_text.find('{')
            if json_start == -1:
                print("   ❌ Pas de JSON trouvé")
                return {}
            
            response_text = response_text[json_start:]
            json_end = response_text.rfind('}')
            if json_end == -1:
                print("   ❌ JSON incomplet")
                return {}
            
            response_text = response_text[:json_end+1]
            
            try:
                part1_result = json.loads(response_text)
                print("   ✅ Succès")
                silhouette = part1_result.get('silhouette_type', 'Unknown')
                print("      • Silhouette: {}".format(silhouette))
                print("      • Objectifs: {}".format(len(part1_result.get('styling_objectives', []))))
            except json.JSONDecodeError as e:
                print("   ❌ Erreur parsing: {}".format(str(e)))
                return {}
            
            # PART 2
            print("\n" + "█"*80)
            print("█ APPEL 2/2: MORPHOLOGY PART 2 - RECOMMANDATIONS")
            print("█"*80)
            
            styling_objectives = part1_result.get("styling_objectives", [])
            objectives_str = ", ".join(styling_objectives)
            
            print("\n📍 AVANT APPEL:")
            print("   • Type: OpenAI Text API")
            print("   • Max tokens: 800")
            print("   • Silhouette: {}".format(silhouette))
            print("   • Objectifs: {}".format(objectives_str))
            
            self.openai.set_context("Morphology Part 2", "PART 2")
            self.openai.set_system_prompt(MORPHOLOGY_PART2_SYSTEM_PROMPT)
            
            user_prompt_part2 = MORPHOLOGY_PART2_USER_PROMPT.format(
                silhouette_type=silhouette,
                styling_objectives=objectives_str
            )
            
            print("\n🤖 APPEL OPENAI EN COURS...")
            response_part2 = await self.openai.call_gpt4(
                prompt=user_prompt_part2,
                max_tokens=800
            )
            print("✅ RÉPONSE REÇUE")
            
            content_part2 = response_part2.get("content", "")
            prompt_tokens_p2 = response_part2.get("prompt_tokens", 0)
            completion_tokens_p2 = response_part2.get("completion_tokens", 0)
            total_tokens_p2 = response_part2.get("total_tokens", 0)
            budget_percent_p2 = (total_tokens_p2 / 4000) * 100
            
            print("\n🔍 RÉPONSE BRUTE (premiers 400 chars):")
            print("   " + content_part2[:400])
            
            print("\n📊 TOKENS PART 2:")
            print("   • Prompt: {}".format(prompt_tokens_p2))
            print("   • Completion: {}".format(completion_tokens_p2))
            print("   • Total: {}".format(total_tokens_p2))
            print("   • Budget: {:.1f}%".format(budget_percent_p2))
            
            total_morpho = total_tokens_p1 + total_tokens_p2
            total_percent = (total_morpho / 4000) * 100
            print("\n📊 TOTAL MORPHOLOGIE: {} tokens ({:.1f}%)".format(total_morpho, total_percent))
            
            # Parse Part 2
            print("\n📋 PARSING JSON PART 2:")
            response_text = content_part2.strip() if content_part2 else ""
            
            if not response_text:
                print("   ❌ Réponse vide")
                return {}
            
            json_start = response_text.find('{')
            if json_start == -1:
                print("   ❌ Pas de JSON trouvé")
                return {}
            
            response_text = response_text[json_start:]
            json_end = response_text.rfind('}')
            if json_end == -1:
                print("   ❌ JSON incomplet")
                return {}
            
            response_text = response_text[:json_end+1]
            
            try:
                part2_result = json.loads(response_text)
                print("   ✅ Succès")
            except json.JSONDecodeError as e:
                print("   ❌ Erreur parsing: {}".format(str(e)))
                return {}
            
            # MERGE
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
                "recommendations": part2_result.get("recommendations", {})
            }
            
            print("✅ Morphologie générée\n")
            return final_result
            
        except Exception as e:
            print("\n❌ ERREUR MORPHOLOGY: {}".format(str(e)))
            call_tracker.log_error("Morphology", str(e))
            raise


morphology_service = MorphologyService()