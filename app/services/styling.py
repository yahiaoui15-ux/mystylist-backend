"""
STYLING SERVICE v2.0 - Avec call_tracker pour logs structurés
✅ Logs clairs des appels OpenAI
✅ Tracking des tokens et parsing
"""

import json
from app.utils.openai_client import openai_client
from app.utils.openai_call_tracker import call_tracker
from app.prompts.styling_prompt import STYLING_SYSTEM_PROMPT, STYLING_USER_PROMPT


class StylingService:
    def __init__(self):
        self.openai = openai_client
    
    async def generate(
        self,
        colorimetry_result: dict,
        morphology_result: dict,
        user_data: dict
    ) -> dict:
        """
        Génère le profil stylistique avec logs clairs
        
        Args:
            colorimetry_result: Résultat colorimétrie
            morphology_result: Résultat morphologie
            user_data: Données utilisateur
        
        Returns:
            Profil stylistique complet
        """
        try:
            print("\n" + "="*80)
            print("📊 STYLING: Profil & Garde-robe capsule")
            print("="*80 + "\n")
            
            # Définir le contexte
            self.openai.set_context("Styling", "")
            self.openai.set_system_prompt(STYLING_SYSTEM_PROMPT)
            
            # Extraire les données essentielles
            palette = colorimetry_result.get("palette_personnalisee", [])
            top_colors = []
            for i, color in enumerate(palette[:4]):
                top_colors.append(f"{color.get('name', 'Couleur')}: {color.get('hex', '')}")
            palette_str = ", ".join(top_colors) if top_colors else "Palette personnalisée"
            
            season = colorimetry_result.get("saison_confirmee", "Indéterminée")
            under_tone = colorimetry_result.get("sous_ton_detecte", "")
            silhouette_type = morphology_result.get("silhouette_type", "O")
            
            print(f"🎨 Données synthétisées:")
            print(f"   • Saison: {season} ({under_tone})")
            print(f"   • Palette: {palette_str}")
            print(f"   • Silhouette: {silhouette_type}\n")
            
            # Extraire recommendations morpho
            recommendations = morphology_result.get("recommendations", {})
            recommendations_simple = ""
            if isinstance(recommendations, dict):
                valoriser = recommendations.get("valoriser", [])
                minimiser = recommendations.get("minimiser", [])
                if valoriser or minimiser:
                    val_str = ", ".join(valoriser[:2]) if valoriser else ""
                    min_str = ", ".join(minimiser[:2]) if minimiser else ""
                    recommendations_simple = f"Valoriser: {val_str}. Minimiser: {min_str}."
            
            if not recommendations_simple:
                recommendations_simple = f"Silhouette {silhouette_type}"
            
            # Préparer le prompt
            style_prefs = user_data.get("style_preferences", "")[:100]
            brand_prefs_list = user_data.get("brand_preferences", [])[:3]
            brand_prefs = ", ".join(brand_prefs_list) if brand_prefs_list else "Aucune"
            
            user_prompt = STYLING_USER_PROMPT.format(
                season=season,
                palette=palette_str,
                guide_maquillage="Voir pages colorimétrie",
                silhouette_type=silhouette_type,
                recommendations=recommendations_simple,
                style_preferences=style_prefs or "Classique",
                brand_preferences=brand_prefs
            )
            
            print(f"🤖 Appel OpenAI Chat...")
            response = await self.openai.call_chat(
                prompt=user_prompt,
                model="gpt-4",
                max_tokens=3500
            )
            
            # Le call_tracker a déjà loggé via openai_client
            content = response["content"]
            
            # Parser
            try:
                result = json.loads(content)
                print(f"✅ JSON parsé avec succès")
            except json.JSONDecodeError:
                # Extraire JSON
                try:
                    start = content.find('{')
                    end = content.rfind('}') + 1
                    if start != -1 and end > start:
                        json_str = content[start:end]
                        result = json.loads(json_str)
                        print(f"✅ JSON extrait et parsé")
                    else:
                        result = {}
                except:
                    print(f"❌ Erreur parsing JSON")
                    call_tracker.log_error("Styling", "JSON parsing failed")
                    result = {}
            
            if not result:
                print("❌ Erreur parsing JSON styling")
                return {}
            
            # Log résultat
            formulas = result.get("mix_and_match_formulas", [])
            profile = result.get("profil_mode", {})
            
            print(f"\n✅ RÉSULTAT STYLING:")
            print(f"   • Profil défini: {'Oui' if profile else 'Non'}")
            print(f"   • Formules mix&match: {len(formulas)}")
            print("="*80 + "\n")
            
            return result
            
        except Exception as e:
            print(f"\n❌ ERREUR STYLING: {e}")
            call_tracker.log_error("Styling", str(e))
            import traceback
            traceback.print_exc()
            raise


# Instance globale
styling_service = StylingService()