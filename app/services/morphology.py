import json
from app.utils.openai_client import openai_client
from app.prompts.morphology_prompt import MORPHOLOGY_SYSTEM_PROMPT, MORPHOLOGY_USER_PROMPT

class MorphologyService:
    def __init__(self):
        self.openai = openai_client
    
    async def analyze(self, user_data: dict) -> dict:
        """
        Analyse la morphologie d'une cliente
        
        Args:
            user_data: dict avec body_photo_url, measurements (shoulder, waist, hip, bust)
        
        Returns:
            dict avec silhouette_type, recommendations, etc.
        """
        try:
            print("📏 Analyse morphologie...")
            
            # Vérifier que la photo existe
            body_photo_url = user_data.get("body_photo_url")
            if not body_photo_url:
                print("❌ Pas de photo du corps fournie")
                return {}
            
            # Construire le prompt utilisateur
            user_prompt = MORPHOLOGY_USER_PROMPT.format(
                body_photo_url=body_photo_url,
                shoulder_circumference=user_data.get("shoulder_circumference", 0),
                waist_circumference=user_data.get("waist_circumference", 0),
                hip_circumference=user_data.get("hip_circumference", 0),
                bust_circumference=user_data.get("bust_circumference", 0)
            )
            
            # Appel OpenAI Vision
            print("   📤 Envoi à OpenAI...")
            response = await self.openai.analyze_image(
                image_urls=[body_photo_url],
                prompt=user_prompt,
                model="gpt-4-turbo"
            )
            
            print(f"   📨 Réponse reçue ({len(response)} chars)")
            
            # ✅ NETTOYAGE ROBUSTE: Extraire JSON valide
            response_text = response.strip()
            
            # Chercher le début du JSON
            json_start = response_text.find('{')
            if json_start == -1:
                print(f"❌ Pas de {{ trouvé dans réponse: {response_text[:100]}")
                return {}
            
            response_text = response_text[json_start:]
            
            # Chercher la fin du JSON
            json_end = response_text.rfind('}')
            if json_end == -1:
                print(f"❌ Pas de }} trouvé dans réponse nettoyée")
                return {}
            
            response_text = response_text[:json_end+1]
            
            print(f"   ✓ JSON extrait ({len(response_text)} chars)")
            print(f"   📋 Débuts: {response_text[:80]}...")
            
            # Parser la réponse JSON
            try:
                result = json.loads(response_text)
                print(f"   ✅ JSON parsé avec succès")
            except json.JSONDecodeError as e:
                print(f"❌ Erreur parsing JSON: {e}")
                print(f"   Contenu: {response_text[:200]}")
                return {}
            
            if not result:
                print("❌ Résultat vide après parsing")
                return {}
            
            print(f"✅ Morphologie analysée: {result.get('silhouette_type', 'Unknown')}")
            return result
            
        except Exception as e:
            print(f"❌ Erreur analyse morphologie: {e}")
            import traceback
            traceback.print_exc()
            raise

# Instance globale
morphology_service = MorphologyService()