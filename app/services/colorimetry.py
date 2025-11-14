import json
from app.utils.openai_client import openai_client
from app.prompts.colorimetry_prompt import COLORIMETRY_SYSTEM_PROMPT, COLORIMETRY_USER_PROMPT
from app.services.robust_json_parser import RobustJSONParser  # ← MODIFIÉ


class ColorimetryService:
    def __init__(self):
        self.openai = openai_client
    
    async def analyze(self, user_data: dict) -> dict:
        """
        Analyse la colorimétrie d'une cliente
        
        Args:
            user_data: dict avec face_photo_url, eye_color, hair_color, age, unwanted_colors
        
        Returns:
            dict avec saison_confirmee, palette_personnalisee, guide_maquillage, etc.
        """
        try:
            print("🎨 Analyse colorimétrie...")
            
            # Vérifier que la photo existe
            face_photo_url = user_data.get("face_photo_url")
            if not face_photo_url:
                print("❌ Pas de photo de visage fournie")
                return {}
            
            # Construire le prompt utilisateur
            unwanted_colors_str = ", ".join(user_data.get("unwanted_colors", []))
            user_prompt = COLORIMETRY_USER_PROMPT.format(
                face_photo_url=face_photo_url,
                eye_color=user_data.get("eye_color", "Non spécifié"),
                hair_color=user_data.get("hair_color", "Non spécifié"),
                age=user_data.get("age", 0),
                unwanted_colors=unwanted_colors_str or "Aucune"
            )
            
            # Appel OpenAI Vision
            print("   📤 Envoi à OpenAI...")
            response = await self.openai.analyze_image(
                image_urls=[face_photo_url],
                prompt=user_prompt,
                model="gpt-4-turbo"
            )
            print(f"   📨 Réponse reçue ({len(response)} chars)")
            print(f"   📋 Débuts: {response[:100]}...")
            
            # ✅ MODIFIÉ: Utiliser le parser robuste (remplace clean_json_response)
            result = RobustJSONParser.parse_json_with_fallback(response)
            
            if not result:
                print("❌ Impossible de parser la réponse JSON")
                return {}
            
            # ✅ Valider que les données colorimétrie sont présentes
            palette = result.get('palette_personnalisee', [])
            colors_with_notes = result.get('allColorsWithNotes', [])
            associations = result.get('associationsGagnantes', [])
            
            print(f"   ✓ Palette: {len(palette)} couleurs")
            print(f"   ✓ All Colors: {len(colors_with_notes)} couleurs")
            print(f"   ✓ Associations: {len(associations)} associations")
            
            if not palette and not colors_with_notes:
                print("⚠️ ATTENTION: Pas de couleurs dans la réponse GPT!")
                print(f"   Clés disponibles: {list(result.keys())}")
            
            # ✅ AJOUTER les données utilisateur manquantes
            result["eye_color"] = user_data.get("eye_color", "")
            result["hair_color"] = user_data.get("hair_color", "")
            
            # Fallback saison si absente
            if not result.get("saison_confirmee"):
                result["saison_confirmee"] = "Indéterminée"
                print(f"⚠️ Saison manquante, utilisation fallback")
            
            # Fallback justification
            if not result.get("justification_saison"):
                result["justification_saison"] = f"Votre carnation et traits correspondent à la saison {result.get('saison_confirmee', 'indéterminée')}."
            
            saison = result.get("saison_confirmee", "Unknown")
            print(f"✅ Colorimétrie analysée: {saison}")
            print(f"   ✓ Yeux: {result.get('eye_color')}")
            print(f"   ✓ Cheveux: {result.get('hair_color')}")
            print(f"   ✓ Palette personnalisée: {len(palette)} couleurs")
            print(f"   ✓ Guide Maquillage: {bool(result.get('guide_maquillage'))}")
            
            return result
            
        except Exception as e:
            print(f"❌ Erreur analyse colorimétrie: {e}")
            import traceback
            traceback.print_exc()
            raise


# Instance globale
colorimetry_service = ColorimetryService()