"""
Morphology Service v3.0 - Logging STRUCTURÉ et CLOISONNÉ
✅ Bloc isolé: Before → Call → Tokens → Response → Parsing
"""

import json
from datetime import datetime
from app.utils.openai_client import openai_client
from app.utils.openai_call_tracker import call_tracker
from app.prompts.morphology_prompt import MORPHOLOGY_SYSTEM_PROMPT, MORPHOLOGY_USER_PROMPT


class MorphologyService:
    def __init__(self):
        self.openai = openai_client
    
    async def analyze(self, user_data: dict) -> dict:
        """Analyse morphologie - 1 APPEL OPENAI VISION"""
        print("\n" + "="*80)
        print("📋 APPEL MORPHOLOGY: ANALYSE SILHOUETTE + RECOMMANDATIONS")
        print("="*80)
        
        try:
            body_photo_url = user_data.get("body_photo_url")
            if not body_photo_url:
                print("❌ Pas de photo du corps fournie")
                return {}
            
            print("\n📌 AVANT APPEL:")
            print(f"   • Type: OpenAI Vision API (gpt-4-turbo)")
            print(f"   • Max tokens: 2000")
            print(f"   • Image: {body_photo_url[:50]}...")
            print(f"   • Mensurations:")
            print(f"      - Épaules: {user_data.get('shoulder_circumference')} cm")
            print(f"      - Taille: {user_data.get('waist_circumference')} cm")
            print(f"      - Hanches: {user_data.get('hip_circumference')} cm")
            
            self.openai.set_context("Morphology", "")
            self.openai.set_system_prompt(MORPHOLOGY_SYSTEM_PROMPT)
            
            user_prompt = MORPHOLOGY_USER_PROMPT.format(
                body_photo_url=body_photo_url,
                shoulder_circumference=user_data.get("shoulder_circumference", 0),
                waist_circumference=user_data.get("waist_circumference", 0),
                hip_circumference=user_data.get("hip_circumference", 0),
                bust_circumference=user_data.get("bust_circumference", 0)
            )
            
            print(f"\n🤖 APPEL OPENAI EN COURS...")
            response = await self.openai.analyze_image(
                image_urls=[body_photo_url],
                prompt=user_prompt,
                model="gpt-4-turbo",
                max_tokens=2000
            )
            print(f"✅ RÉPONSE REÇUE")
            
            prompt_tokens = response.get("prompt_tokens", 0)
            completion_tokens = response.get("completion_tokens", 0)
            total_tokens = response.get("total_tokens", 0)
            budget_percent = (total_tokens / 4000) * 100
            
            print(f"\n📊 TOKENS CONSOMMÉS:")
            print(f"   • Prompt: {prompt_tokens}")
            print(f"   • Completion: {completion_tokens}")
            print(f"   • Total: {total_tokens}")
            print(f"   • Budget: {budget_percent:.1f}% (vs 4000 max)")
            print(f"   • Status: {'⚠️ DÉPASSEMENT!' if budget_percent > 100 else '⚠️ Approche limite' if budget_percent > 90 else '✅ OK'}")
            
            content = response.get("content", "")
            print(f"\n📝 RÉPONSE BRUTE (premiers 400 chars):")
            print(f"   {content[:400]}...")
            
            print(f"\n🔍 PARSING JSON:")
            
            response_text = content.strip() if content else ""
            if not response_text:
                print(f"   ❌ Réponse vide")
                return {}
            
            json_start = response_text.find('{')
            if json_start == -1:
                print(f"   ❌ Pas de JSON trouvé")
                return {}
            
            response_text = response_text[json_start:]
            json_end = response_text.rfind('}')
            if json_end == -1:
                print(f"   ❌ JSON incomplet")
                return {}
            
            response_text = response_text[:json_end+1]
            
            try:
                result = json.loads(response_text)
                print(f"   ✅ Succès")
                
                silhouette = result.get('silhouette_type', 'Unknown')
                objectives = len(result.get('styling_objectives', []))
                tips = len(result.get('instant_tips', []))
                
                print(f"      • Silhouette: {silhouette}")
                print(f"      • Objectifs: {objectives}")
                print(f"      • Conseils immédiat: {tips}")
                
            except json.JSONDecodeError as e:
                print(f"   ❌ Erreur parsing JSON: {e}")
                if response_text.count('{') > response_text.count('}'):
                    response_text += '}'
                    try:
                        result = json.loads(response_text)
                        print(f"   ✅ Succès (après correction)")
                    except:
                        return {}
                else:
                    return {}
            
            print("\n" + "="*80 + "\n")
            return result
            
        except Exception as e:
            print(f"\n❌ ERREUR MORPHOLOGY: {e}")
            call_tracker.log_error("Morphology", str(e))
            raise


morphology_service = MorphologyService()