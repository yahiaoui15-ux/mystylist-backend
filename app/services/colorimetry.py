import json
from app.utils.openai_client import openai_client
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
            
            # ✅ AJOUTER les données utilisateur manquantes
            result["eye_color"] = user_data.get("eye_color", "")
            result["hair_color"] = user_data.get("hair_color", "")
            
            # Fallback saison si absente
            if not result.get("saison_confirmee"):
                result["saison_confirmee"] = "Indéterminée"
            
            # Fallback justification
            if not result.get("justification_saison"):
                result["justification_saison"] = f"Votre carnation et traits correspondent à la saison {result.get('saison_confirmee', 'indéterminée')}."
            
            saison = result.get("saison_confirmee", "Unknown")
            print(f"✅ Colorimétrie analysée: {saison}")
            print(f"   ✓ Yeux: {result.get('eye_color')}")
            print(f"   ✓ Cheveux: {result.get('hair_color')}")
            print(f"   ✓ Palette: {len(result.get('palette_personnalisee', []))} couleurs")
            
            return result
            
        except Exception as e:
            print(f"❌ Erreur analyse colorimétrie: {e}")
            import traceback
            traceback.print_exc()
            raise

# Instance globale
colorimetry_service = ColorimetryService()