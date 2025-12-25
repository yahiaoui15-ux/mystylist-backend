"""
Styling Service v3.0 - CORRECT et complet
✅ Utilise call_chat() comme morphology.py
✅ Parse JSON robuste
✅ Instance styling_service exportée
"""

import json
import re
from app.utils.openai_client import openai_client
from app.utils.openai_call_tracker import call_tracker
from app.prompts.styling_prompt import STYLING_SYSTEM_PROMPT, STYLING_USER_PROMPT


class StylingService:
    def __init__(self):
        self.openai = openai_client
    
    @staticmethod
    def safe_format(template: str, **kwargs) -> str:
        """Format un template en ignorant les clés manquantes"""
        class SafeDict(dict):
            def __missing__(self, key):
                return ""
        
        safe_dict = SafeDict(kwargs)
        try:
            return template.format_map(safe_dict)
        except Exception as e:
            print(f"⚠️ Erreur format_map styling: {str(e)}")
            return template
    
    @staticmethod
    def clean_json_string(content: str) -> str:
        """Nettoie une réponse JSON"""
        content = re.sub(r'^```json\s*', '', content)
        content = re.sub(r'\s*```$', '', content)
        content = content.replace('\x00', '')
        content = re.sub(r'\\([éèêëàâäùûüôöîïœæ])', r'\1', content)
        return content
    
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
            # Extraire données du colorimetry
            palette = colorimetry_result.get("palette_personnalisee", [])
            top_colors = []
            for i, color in enumerate(palette[:4]):
                top_colors.append(f"{color.get('name', 'Couleur')}: {color.get('hex', '')}")
            palette_str = ", ".join(top_colors) if top_colors else "Palette personnalisée"
            
            season = colorimetry_result.get("saison_confirmee", "Indéterminée")
            sous_ton = colorimetry_result.get("sous_ton_detecte", "")
            
            # Extraire données de la morphologie
            silhouette_type = morphology_result.get("silhouette_type", "?")
            
            recommendations = morphology_result.get("recommendations", {})
            recommendations_simple = ""
            if isinstance(recommendations, dict):
                if "recommendations" in recommendations:
                    rec_dict = recommendations["recommendations"]
                    if isinstance(rec_dict, dict):
                        hauts = rec_dict.get("hauts", {})
                        if isinstance(hauts, dict):
                            priv = hauts.get("a_privilegier", [])
                            if isinstance(priv, list) and len(priv) > 0:
                                recommendations_simple = f"Recommandations morpho: {len(priv)} pièces identifiées"
            
            if not recommendations_simple:
                recommendations_simple = f"Silhouette {silhouette_type}"
            
            # Données utilisateur
            style_prefs = user_data.get("style_preferences", "")
            if isinstance(style_prefs, list):
                style_prefs = ", ".join(style_prefs[:3]) if style_prefs else "Classique"
            style_prefs = str(style_prefs)[:100]
            
            brand_prefs_list = user_data.get("brand_preferences", [])
            if isinstance(brand_prefs_list, list):
                brand_prefs = ", ".join(brand_prefs_list[:3]) if brand_prefs_list else "Aucune"
            else:
                brand_prefs = str(brand_prefs_list) if brand_prefs_list else "Aucune"
            
            print("\n📌 AVANT APPEL:")
            print(f"   • Type: OpenAI Chat (gpt-4)")
            print(f"   • Max tokens: 3500")
            print(f"   • Saison: {season} ({sous_ton})")
            print(f"   • Palette: {palette_str}")
            print(f"   • Silhouette: {silhouette_type}")
            
            # Configurer le contexte
            self.openai.set_context("Styling", "")
            self.openai.set_system_prompt(STYLING_SYSTEM_PROMPT)
            
            # Formater le prompt utilisateur
            user_prompt = self.safe_format(
                STYLING_USER_PROMPT,
                season=season,
                sous_ton=sous_ton,
                palette=palette_str,
                silhouette_type=silhouette_type,
                recommendations=recommendations_simple,
                style_preferences=style_prefs,
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
            
            result = {}
            try:
                content_clean = self.clean_json_string(content)
                result = json.loads(content_clean)
                print(f"   ✅ Succès (parsing direct)")
                
                formulas = result.get("mix_and_match_formulas", [])
                archetypes = result.get("archetypes", [])
                capsule = result.get("capsule_wardrobe", {})
                basics = capsule.get("basics", []) if isinstance(capsule, dict) else []
                
                print(f"      • Archetypes: {len(archetypes)}")
                print(f"      • Capsule wardrobe: {len(basics)} basics")
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
                        capsule = result.get("capsule_wardrobe", {})
                        basics = capsule.get("basics", []) if isinstance(capsule, dict) else []
                        
                        print(f"      • Archetypes: {len(archetypes)}")
                        print(f"      • Capsule wardrobe: {len(basics)} basics")
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
            import traceback
            traceback.print_exc()
            raise


# ✅ INSTANCE GLOBALE - TRÈS IMPORTANT!
styling_service = StylingService()