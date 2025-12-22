"""
Styling Service v3.0 - Logging STRUCTURÉ et CLOISONNÉ
✅ Bloc isolé: Before → Call → Tokens → Response → Parsing
"""

import json
from datetime import datetime
from app.utils.openai_client import openai_client
from app.utils.openai_call_tracker import call_tracker
from app.prompts.styling_prompt import STYLING_SYSTEM_PROMPT, STYLING_USER_PROMPT
from app.services.robust_json_parser import RobustJSONParser


class StylingService:
    def __init__(self):
        self.openai = openai_client
    
    async def generate(
        self,
        colorimetry_result: dict,
        morphology_result: dict,
        user_data: dict
    ) -> dict:
        """Génère le profil stylistique - 1 APPEL OPENAI CHAT"""
        print("\n" + "="*80)
        print("📋 APPEL STYLING: PROFIL STYLISTIQUE + GARDE-ROBE CAPSULE")
        print("="*80)
        
        try:
            palette = colorimetry_result.get("palette_personnalisee", [])
            top_colors = []
            for i, color in enumerate(palette[:4]):
                top_colors.append(f"{color.get('name', 'Couleur')}: {color.get('hex', '')}")
            palette_str = ", ".join(top_colors) if top_colors else "Palette personnalisée"
            
            season = colorimetry_result.get("saison_confirmee", "Indéterminée")
            under_tone = colorimetry_result.get("sous_ton_detecte", "")
            silhouette_type = morphology_result.get("silhouette_type", "?")
            
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
            
            print("\n📌 AVANT APPEL:")
            print(f"   • Type: OpenAI Chat (gpt-4)")
            print(f"   • Max tokens: 3500")
            print(f"   • Saison: {season} ({under_tone})")
            print(f"   • Palette: {palette_str}")
            print(f"   • Silhouette: {silhouette_type}")
            
            self.openai.set_context("Styling", "")
            self.openai.set_system_prompt(STYLING_SYSTEM_PROMPT)
            
            style_prefs = user_data.get("style_preferences", "")[:100]
            brand_prefs_list = user_data.get("brand_preferences", [])[:3]
            brand_prefs = ", ".join(brand_prefs_list) if brand_prefs_list else "Aucune"
            
            user_prompt = STYLING_USER_PROMPT.format(
                season=season,
                sous_ton=under_tone, 
                palette=palette_str,
                guide_maquillage="Voir pages colorimétrie",
                silhouette_type=silhouette_type,
                recommendations=recommendations_simple,
                style_preferences=style_prefs or "Classique",
                brand_preferences=brand_prefs
            )
            
            print(f"\n🤖 APPEL OPENAI EN COURS...")
            response = await self.openai.call_chat(
                prompt=user_prompt,
                model="gpt-4",
                max_tokens=3500
            )
            print(f"✅ RÉPONSE REÇUE")
            
            prompt_tokens = response.get("prompt_tokens", 0)
            completion_tokens = response.get("completion_tokens", 0)
            total_tokens = response.get("total_tokens", 0)
            budget_percent = (total_tokens / 4000) * 100
            
            print(f"\n📊 TOKENS CONSOMMÉS:")
            print(f"   • Prompt: {prompt_tokens}")
            print(f"   • Completion: {completion_tokens}")
            print(f"   • Total: {total_tokens}")
            print(f"   • Budget: {budget_percent:.1f}% (vs 4000 max)")
            print(f"   • Status: {'⚠️ DÉPASSEMENT!' if budget_percent > 100 else '⚠️ Approche limite' if budget_percent > 90 else '✅ OK'}")
            
            content = response.get("content", "")
            print(f"\n📝 RÉPONSE BRUTE (premiers 400 chars):")
            print(f"   {content[:400]}...")
            
            print(f"\n🔍 PARSING JSON:")
            
            try:
                result = json.loads(content)
                print(f"   ✅ Succès (parsing direct)")
                
                formulas = result.get("mix_and_match_formulas", [])
                archetypes = result.get("archetypes", [])
                capsule = result.get("capsule_wardrobe", [])
                
                print(f"      • Archetypes: {len(archetypes)}")
                print(f"      • Capsule wardrobe: {len(capsule)} pièces")
                print(f"      • Mix & match formulas: {len(formulas)}")
                
            except json.JSONDecodeError:
                try:
                    start = content.find('{')
                    end = content.rfind('}') + 1
                    if start != -1 and end > start:
                        json_str = content[start:end]
                        result = json.loads(json_str)
                        print(f"   ✅ Succès (extraction JSON)")
                        
                        formulas = result.get("mix_and_match_formulas", [])
                        archetypes = result.get("archetypes", [])
                        capsule = result.get("capsule_wardrobe", [])
                        
                        print(f"      • Archetypes: {len(archetypes)}")
                        print(f"      • Capsule wardrobe: {len(capsule)} pièces")
                        print(f"      • Mix & match formulas: {len(formulas)}")
                    else:
                        print(f"   ❌ Pas de JSON trouvé")
                        result = {}
                except Exception as e:
                    print(f"   ❌ Erreur parsing JSON: {e}")
                    result = {}
            
            print("\n" + "="*80 + "\n")
            return result
            
        except Exception as e:
            print(f"\n❌ ERREUR STYLING: {e}")
            call_tracker.log_error("Styling", str(e))
            raise


styling_service = StylingService()