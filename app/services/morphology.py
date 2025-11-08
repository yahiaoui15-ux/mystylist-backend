import json
from app.utils.openai_client import openai_client
from app.models.report_output import MorphologyOutput
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
            
            # Construire le prompt utilisateur
            user_prompt = MORPHOLOGY_USER_PROMPT.format(
                body_photo_url=user_data["body_photo_url"],
                shoulder_circumference=user_data.get("shoulder_circumference", 0),
                waist_circumference=user_data.get("waist_circumference", 0),
                hip_circumference=user_data.get("hip_circumference", 0),
                bust_circumference=user_data.get("bust_circumference", 0)
            )
            
            # Appel OpenAI Vision
            response = await self.openai.analyze_image(
                image_urls=[user_data["body_photo_url"]],
                prompt=user_prompt,
                model="gpt-4-turbo"
            )
            
            # Parser la réponse JSON
            result = await self.openai.parse_json_response(response)
            
            if not result:
                print("❌ Erreur parsing JSON morphologie")
                return {}
            
            print(f"✅ Morphologie analysée: {result.get('silhouette_type', 'Unknown')}")
            return result
            
        except Exception as e:
            print(f"❌ Erreur analyse morphologie: {e}")
            raise

# Instance globale
morphology_service = MorphologyService()