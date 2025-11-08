import json
from app.utils.openai_client import openai_client
from app.prompts.styling_prompt import STYLING_SYSTEM_PROMPT, STYLING_USER_PROMPT

class StylingService:
    def __init__(self):
        self.openai = openai_client
    
    async def generate(self, colorimetry_result: dict, morphology_result: dict, user_data: dict) -> dict:
        """
        Génère le profil stylistique complet
        
        Args:
            colorimetry_result: Résultat analyse colorimétrie
            morphology_result: Résultat analyse morphologie
            user_data: Données utilisateur (preferences, brands)
        
        Returns:
            dict avec archetypes, capsule, formules mix&match, etc.
        """
        try:
            print("👗 Génération profil stylistique...")
            
            # Formatter les données pour le prompt
            palette_str = ", ".join([c.get("displayName", c.get("name", "")) for c in colorimetry_result.get("palette_personnalisee", [])])
            guide_maquillage_str = str(colorimetry_result.get("guide_maquillage", {}))
            recommendations_str = str(morphology_result.get("recommendations", {}))
            style_prefs = user_data.get("style_preferences", "Non spécifié")
            brand_prefs = ", ".join(user_data.get("brand_preferences", []))
            
            # Construire le prompt utilisateur
            user_prompt = STYLING_USER_PROMPT.format(
                season=colorimetry_result.get("season", "Indéterminée"),
                palette=palette_str,
                guide_maquillage=guide_maquillage_str,
                silhouette_type=morphology_result.get("silhouette_type", "Indéterminée"),
                recommendations=recommendations_str,
                style_preferences=style_prefs,
                brand_preferences=brand_prefs or "Aucune"
            )
            
            # Appel OpenAI Chat (pas vision, juste texte)
            response = await self.openai.call_chat(
                prompt=user_prompt,
                model="gpt-4"
            )
            
            # Parser la réponse JSON
            result = await self.openai.parse_json_response(response)
            
            if not result:
                print("❌ Erreur parsing JSON styling")
                return {}
            
            # Vérifier que les 10 formules sont complètes
            formulas = result.get("mix_and_match_formulas", [])
            print(f"✅ Profil stylistique généré: {len(formulas)} formules mix&match")
            
            return result
            
        except Exception as e:
            print(f"❌ Erreur génération profil: {e}")
            raise

# Instance globale
styling_service = StylingService()