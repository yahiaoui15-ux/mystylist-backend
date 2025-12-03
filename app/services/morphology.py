"""
MORPHOLOGY SERVICE - Analyse morphologie corporelle
Utilise OpenAI Vision pour analyser photo + mensurations
"""

import json
from app.utils.openai_client import openai_client
from app.prompts.morphology_prompt import MORPHOLOGY_SYSTEM_PROMPT, MORPHOLOGY_USER_PROMPT


class MorphologyService:
    def __init__(self):
        self.openai = openai_client
    
    async def analyze(self, user_data: dict) -> dict:
        """
        Analyse la morphologie d'une cliente.
        
        Args:
            user_data: dict avec:
                - body_photo_url: URL de la photo du corps
                - shoulder_circumference: Tour d'épaules (cm)
                - waist_circumference: Tour de taille (cm)
                - hip_circumference: Tour de hanches (cm)
        
        Returns:
            dict avec silhouette_type, recommendations pour 7 catégories, etc.
        """
        try:
            print("🔍 Analyse morphologie...")
            
            # Vérifier que la photo existe
            body_photo_url = user_data.get("body_photo_url")
            if not body_photo_url:
                print("❌ Pas de photo du corps fournie")
                return {}
            
            print(f"   📸 Photo: {body_photo_url[:50]}...")
            print(f"   📏 Épaules: {user_data.get('shoulder_circumference')} cm")
            print(f"   📏 Taille: {user_data.get('waist_circumference')} cm")
            print(f"   📏 Hanches: {user_data.get('hip_circumference')} cm")
            
            # Construire le prompt utilisateur
            user_prompt = MORPHOLOGY_USER_PROMPT.format(
                body_photo_url=body_photo_url,
                shoulder_circumference=user_data.get("shoulder_circumference", 0),
                waist_circumference=user_data.get("waist_circumference", 0),
                hip_circumference=user_data.get("hip_circumference", 0),
                bust_circumference=user_data.get("bust_circumference", 0)
            )
            
            # Appel OpenAI Vision
            print("   🤖 Envoi à OpenAI GPT-4 Vision...")
            response = await self.openai.analyze_image(
                image_urls=[body_photo_url],
                prompt=user_prompt,
                model="gpt-4-turbo"
            )
            
            response_length = len(response) if response else 0
            print(f"   ✅ Réponse reçue ({response_length} caractères)")
            
            # ✅ NETTOYAGE ROBUSTE: Extraire JSON valide
            response_text = response.strip() if response else ""
            
            if not response_text:
                print("❌ Réponse vide reçue")
                return {}
            
            # Chercher le début du JSON
            json_start = response_text.find('{')
            if json_start == -1:
                print(f"❌ Pas de '{{' trouvé dans réponse: {response_text[:100]}")
                return {}
            
            response_text = response_text[json_start:]
            print(f"   ✅ JSON trouvé à position {json_start}")
            
            # Chercher la fin du JSON
            json_end = response_text.rfind('}')
            if json_end == -1:
                print(f"❌ Pas de '}}' trouvé dans réponse nettoyée")
                return {}
            
            response_text = response_text[:json_end+1]
            print(f"   ✅ JSON extrait ({len(response_text)} caractères)")
            
            # Parser la réponse JSON
            try:
                result = json.loads(response_text)
                print(f"   ✅ JSON parsé avec succès")
            except json.JSONDecodeError as e:
                print(f"❌ Erreur parsing JSON: {e}")
                print(f"   Contexte: {response_text[:200]}...")
                
                # Tentative de correction simple: ajouter accolade manquante
                if response_text.count('{') > response_text.count('}'):
                    response_text += '}'
                    try:
                        result = json.loads(response_text)
                        print(f"   ✅ JSON corrigé et parsé")
                    except:
                        print(f"❌ Impossible de corriger le JSON")
                        return {}
                else:
                    return {}
            
            if not result:
                print("❌ Résultat vide après parsing")
                return {}
            
            silhouette = result.get('silhouette_type', 'Unknown')
            print(f"✅ Morphologie analysée: Silhouette {silhouette}")
            
            # Log résumé
            has_recommendations = 'recommendations' in result and result['recommendations']
            has_objectives = 'styling_objectives' in result and result['styling_objectives']
            has_tips = 'instant_tips' in result and result['instant_tips']
            
            print(f"   • Silhouette: {silhouette}")
            print(f"   • Objectifs: {len(result.get('styling_objectives', []))} trouvés")
            print(f"   • Recommandations: {'Oui' if has_recommendations else 'Non'}")
            print(f"   • Conseils immédiats: {len(result.get('instant_tips', []))} trouvés")
            
            return result
            
        except Exception as e:
            print(f"❌ Erreur analyse morphologie: {e}")
            import traceback
            traceback.print_exc()
            raise


# Instance globale
morphology_service = MorphologyService()