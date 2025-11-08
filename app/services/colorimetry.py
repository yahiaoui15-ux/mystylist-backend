import json
from app.utils.openai_client import openai_client
from app.models.report_output import ColorimetryOutput
from app.prompts.colorimetry_prompt import COLORIMETRY_SYSTEM_PROMPT, COLORIMETRY_USER_PROMPT

class ColorimetryService:
    def __init__(self):
        self.openai = openai_client
    
    async def analyze(self, user_data: dict) -> dict:
        """
        Analyse la colorimétrie d'une cliente
        
        Args:
            user_data: dict avec face_photo_url, eye_color, hair_color, age, unwanted_colors
        
        Returns:
            dict avec season, palette, guide_maquillage, etc.
        """
        try:
            print("🎨 Analyse colorimétrie...")
            
            # Construire le prompt utilisateur
            unwanted_colors_str = ", ".join(user_data.get("unwanted_colors", []))
            user_prompt = COLORIMETRY_USER_PROMPT.format(
                face_photo_url=user_data["face_photo_url"],
                eye_color=user_data.get("eye_color", "Non spécifié"),
                hair_color=user_data.get("hair_color", "Non spécifié"),
                age=user_data.get("age", 0),
                unwanted_colors=unwanted_colors_str or "Aucune"
            )
            
            # Appel OpenAI Vision
            response = await self.openai.analyze_image(
                image_urls=[user_data["face_photo_url"]],
                prompt=user_prompt,
                model="gpt-4-turbo"
            )
            
            # Parser la réponse JSON
            result = await self.openai.parse_json_response(response)
            
            if not result:
                print("❌ Erreur parsing JSON colorimétrie")
                return {}
            
            print(f"✅ Colorimétrie analysée: {result.get('season', 'Unknown')}")
            return result
            
        except Exception as e:
            print(f"❌ Erreur analyse colorimétrie: {e}")
            raise

# Instance globale
colorimetry_service = ColorimetryService()