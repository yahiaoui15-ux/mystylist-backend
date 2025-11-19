import json
from app.utils.openai_client import openai_client
from app.prompts.styling_prompt import STYLING_SYSTEM_PROMPT, STYLING_USER_PROMPT

class StylingService:
    def __init__(self):
        self.openai = openai_client
    
    async def generate(self, colorimetry_result: dict, morphology_result: dict, user_data: dict) -> dict:
        """
        Génère le profil stylistique CONDENSÉ pour éviter dépassement tokens
        
        Stratégie: Extraire UNIQUEMENT les données essentielles pour OpenAI
        - Top 3-4 couleurs clés (pas toute la palette)
        - Saison colorimétrique
        - Silhouette type
        - 2-3 recommendations morpho clés (pas tout)
        
        Args:
            colorimetry_result: Résultat analyse colorimétrie
            morphology_result: Résultat analyse morphologie
            user_data: Données utilisateur (preferences, brands)
        
        Returns:
            dict avec archetypes, capsule, formules mix&match, etc.
        """
        try:
            print("👗 Génération profil stylistique (OPTIMISÉ tokens)...")
            
            # ✅ OPTIMISATION 1: Extraire TOP 3-4 couleurs clés (pas toute la palette!)
            palette = colorimetry_result.get("palette_personnalisee", [])
            top_colors = []
            for i, color in enumerate(palette[:4]):  # Top 4 seulement
                top_colors.append(f"{color.get('name', 'Couleur')}: {color.get('hex', '')}")
            palette_str = ", ".join(top_colors) if top_colors else "Palette personnalisée"
            
            print(f"   📊 Top couleurs: {palette_str}")
            
            # ✅ OPTIMISATION 2: Juste la saison (pas le guide maquillage complet!)
            season = colorimetry_result.get("saison_confirmee", "Indéterminée")
            under_tone = colorimetry_result.get("sous_ton_detecte", "")
            guide_maquillage_simple = f"Teint {under_tone}, guide complet en page 6"
            
            print(f"   🎨 Saison: {season} ({under_tone})")
            
            # ✅ OPTIMISATION 3: Silhouette + 2 recommendations clés (pas tout!)
            silhouette_type = morphology_result.get("silhouette_type", "O")
            
            # Extraire 2-3 recommendations clés seulement
            recommendations = morphology_result.get("recommendations", {})
            recommendations_simple = ""
            if isinstance(recommendations, dict):
                # Si c'est un dict avec clés comme "valoriser", "minimiser"
                valoriser = recommendations.get("valoriser", [])
                minimiser = recommendations.get("minimiser", [])
                if valoriser or minimiser:
                    val_str = ", ".join(valoriser[:2]) if valoriser else ""
                    min_str = ", ".join(minimiser[:2]) if minimiser else ""
                    recommendations_simple = f"Valoriser: {val_str}. Minimiser: {min_str}." if val_str or min_str else ""
            
            if not recommendations_simple:
                recommendations_simple = f"Silhouette {silhouette_type}: voir page 8"
            
            print(f"   👕 Morpho: {recommendations_simple}")
            
            # ✅ OPTIMISATION 4: Préférences utilisateur simples
            style_prefs = user_data.get("style_preferences", "")[:100]  # Max 100 chars
            brand_prefs_list = user_data.get("brand_preferences", [])[:3]  # Max 3 marques
            brand_prefs = ", ".join(brand_prefs_list) if brand_prefs_list else "Aucune"
            
            # Construire le prompt CONDENSÉ
            user_prompt = STYLING_USER_PROMPT.format(
                season=season,
                palette=palette_str,
                guide_maquillage=guide_maquillage_simple,
                silhouette_type=silhouette_type,
                recommendations=recommendations_simple,
                style_preferences=style_prefs or "Classique",
                brand_preferences=brand_prefs
            )
            
            print(f"\n🔤 Prompt input: ~{len(user_prompt)} chars (~1200-1500 tokens)")
            
            # Appel OpenAI Chat (avec token counting automatique)
            response = await self.openai.call_chat(
                prompt=user_prompt,
                model="gpt-4",
                max_tokens=3500  # Réduit de 4000 à 3500 (output budget)
            )
            
            # Parser la réponse JSON
            result = await self.openai.parse_json_response(response)
            
            if not result:
                print("❌ Erreur parsing JSON styling")
                return {}
            
            # Vérifier que les formules sont présentes
            formulas = result.get("mix_and_match_formulas", [])
            print(f"✅ Profil stylistique généré: {len(formulas)} formules mix&match\n")
            
            return result
            
        except Exception as e:
            print(f"❌ Erreur génération profil: {e}")
            raise

# Instance globale
styling_service = StylingService()