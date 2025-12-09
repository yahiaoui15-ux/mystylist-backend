"""
MORPHOLOGY SERVICE v2.0 - Avec call_tracker pour logs structurés
✅ Logs clairs avant/après appel OpenAI
✅ Tracking des tokens et parsing
"""

import json
from app.utils.openai_client import openai_client
from app.utils.openai_call_tracker import call_tracker
from app.prompts.morphology_prompt import MORPHOLOGY_SYSTEM_PROMPT, MORPHOLOGY_USER_PROMPT


class MorphologyService:
    def __init__(self):
        self.openai = openai_client
    
    async def analyze(self, user_data: dict) -> dict:
        """
        Analyse la morphologie d'une cliente
        """
        try:
            print("\n" + "="*80)
            print("📊 MORPHOLOGIE: Analyses et recommandations")
            print("="*80 + "\n")
            
            # Vérifier que la photo existe
            body_photo_url = user_data.get("body_photo_url")
            if not body_photo_url:
                print("❌ Pas de photo du corps fournie")
                call_tracker.log_error("Morphology", "No body photo provided")
                return {}
            
            # Définir le contexte
            self.openai.set_context("Morphology", "")
            self.openai.set_system_prompt(MORPHOLOGY_SYSTEM_PROMPT)
            
            print(f"📸 Photo: {body_photo_url[:50]}...")
            print(f"📏 Mensurations:")
            print(f"   • Épaules: {user_data.get('shoulder_circumference')} cm")
            print(f"   • Taille: {user_data.get('waist_circumference')} cm")
            print(f"   • Hanches: {user_data.get('hip_circumference')} cm\n")
            
            # Construire le prompt
            user_prompt = MORPHOLOGY_USER_PROMPT.format(
                body_photo_url=body_photo_url,
                shoulder_circumference=user_data.get("shoulder_circumference", 0),
                waist_circumference=user_data.get("waist_circumference", 0),
                hip_circumference=user_data.get("hip_circumference", 0),
                bust_circumference=user_data.get("bust_circumference", 0)
            )
            
            print(f"🤖 Appel OpenAI Vision...")
            response = await self.openai.analyze_image(
                image_urls=[body_photo_url],
                prompt=user_prompt,
                model="gpt-4-turbo"
            )
            
            # Le call_tracker a déjà loggé via openai_client
            content = response["content"]
            
            # Parser robuste
            response_text = content.strip() if content else ""
            
            if not response_text:
                print("❌ Réponse vide reçue")
                call_tracker.log_error("Morphology", "Empty response")
                return {}
            
            # Chercher JSON
            json_start = response_text.find('{')
            if json_start == -1:
                print(f"❌ Pas de JSON trouvé")
                call_tracker.log_error("Morphology", "No JSON found in response")
                return {}
            
            response_text = response_text[json_start:]
            json_end = response_text.rfind('}')
            if json_end == -1:
                print(f"❌ JSON incomplet")
                call_tracker.log_error("Morphology", "Incomplete JSON")
                return {}
            
            response_text = response_text[:json_end+1]
            
            # Parser
            try:
                result = json.loads(response_text)
                print(f"✅ JSON parsé avec succès")
            except json.JSONDecodeError as e:
                print(f"❌ Erreur parsing JSON: {e}")
                call_tracker.log_error("Morphology", f"JSON parsing failed: {str(e)}")
                
                # Tentative correction
                if response_text.count('{') > response_text.count('}'):
                    response_text += '}'
                    try:
                        result = json.loads(response_text)
                        print(f"✅ JSON corrigé et parsé")
                    except:
                        return {}
                else:
                    return {}
            
            if not result:
                print("❌ Résultat vide après parsing")
                return {}
            
            # Log résultat
            silhouette = result.get('silhouette_type', 'Unknown')
            objectives = len(result.get('styling_objectives', []))
            tips = len(result.get('instant_tips', []))
            
            print(f"\n✅ RÉSULTAT MORPHOLOGIE:")
            print(f"   • Silhouette: {silhouette}")
            print(f"   • Objectifs: {objectives} trouvés")
            print(f"   • Conseils immédiats: {tips} trouvés")
            print("="*80 + "\n")
            
            return result
            
        except Exception as e:
            print(f"\n❌ ERREUR MORPHOLOGIE: {e}")
            call_tracker.log_error("Morphology", str(e))
            import traceback
            traceback.print_exc()
            raise


# Instance globale
morphology_service = MorphologyService()