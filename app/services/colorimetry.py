import json
from app.utils.openai_client import openai_client
from app.prompts.colorimetry_prompt import COLORIMETRY_SYSTEM_PROMPT, COLORIMETRY_USER_PROMPT
from app.services.robust_json_parser import RobustJSONParser


class ColorimetryService:
    def __init__(self):
        self.openai = openai_client
    
    async def analyze(self, user_data: dict) -> dict:
        """
        Analyse la colorimétrie d'une cliente
        
        Args:
            user_data: dict avec face_photo_url, eye_color, hair_color, age, unwanted_colors
        
        Returns:
            dict avec saison_confirmee, palette_personnalisee, guide_maquillage, 
            analyse_colorimetrique_detaillee, etc.
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
            # ✅ CHANGÉ: Utilise GPT-4o mini (128k tokens) au lieu de GPT-4 Turbo (4k tokens)
            print("   🔤 Envoi à OpenAI (GPT-4o mini)...")
            response = await self.openai.analyze_image(
                image_urls=[face_photo_url],
                prompt=user_prompt,
                model="gpt-4o-mini",  # ✅ CHANGÉ: GPT-4o mini (meilleur prix/perf)
                max_tokens=4500  # ✅ Peut utiliser 4500 sans problème (limite: 128,000)
            )
            print(f"   🎨 Réponse reçue ({len(response)} chars)")
            print(f"   📋 Débuts: {response[:100]}...")
            
            # ✅ Parser robuste
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
            
            # ✅ Fallbacks pour analyse_colorimetrique_detaillee
            analyse_detail = result.get("analyse_colorimetrique_detaillee", {})
            if not analyse_detail:
                print("⚠️ analyse_colorimetrique_detaillee manquante, création fallback")
                result["analyse_colorimetrique_detaillee"] = {
                    "temperature": "neutre",
                    "valeur": "médium",
                    "intensite": "médium",
                    "contraste_naturel": "moyen",
                    "description_teint": "Votre teint présente des caractéristiques qui s'harmonisent avec votre saison colorimétrique.",
                    "description_yeux": "Vos yeux contribuent à l'harmonie générale de votre palette colorimétrique.",
                    "description_cheveux": "Vos cheveux complètent naturellement votre profil colorimétrique.",
                    "harmonie_globale": "Tous les éléments de votre profil colorimétrique s'harmonisent ensemble.",
                    "bloc_emotionnel": f"La saison {result.get('saison_confirmee', 'de votre profil')} vous convient et apportera de la lumière à votre apparence.",
                    "impact_visuel": {
                        "effet_couleurs_chaudes": "Les couleurs de votre palette illuminent votre teint naturel.",
                        "effet_couleurs_froides": "Les couleurs contraires à votre palette créent un contraste moins flatteur.",
                        "pourquoi": "Votre undertone naturel s'harmonise mieux avec certaines teintes qu'avec d'autres."
                    }
                }
            else:
                # Fallbacks pour les sous-clés manquantes
                if not analyse_detail.get("temperature"):
                    analyse_detail["temperature"] = "neutre"
                if not analyse_detail.get("valeur"):
                    analyse_detail["valeur"] = "médium"
                if not analyse_detail.get("intensite"):
                    analyse_detail["intensite"] = "médium"
                if not analyse_detail.get("contraste_naturel"):
                    analyse_detail["contraste_naturel"] = "moyen"
                if not analyse_detail.get("description_teint"):
                    analyse_detail["description_teint"] = "Votre teint présente des caractéristiques harmonieuses."
                if not analyse_detail.get("description_yeux"):
                    analyse_detail["description_yeux"] = "Vos yeux contribuent à votre palette."
                if not analyse_detail.get("description_cheveux"):
                    analyse_detail["description_cheveux"] = "Vos cheveux complètent votre profil."
                if not analyse_detail.get("harmonie_globale"):
                    analyse_detail["harmonie_globale"] = "Tous les éléments s'harmonisent."
                if not analyse_detail.get("bloc_emotionnel"):
                    analyse_detail["bloc_emotionnel"] = "Votre profil colorimétrique vous apportera luminosité et confiance."
                
                # Fallbacks pour impact_visuel
                if not analyse_detail.get("impact_visuel"):
                    analyse_detail["impact_visuel"] = {}
                impact = analyse_detail["impact_visuel"]
                if not impact.get("effet_couleurs_chaudes"):
                    impact["effet_couleurs_chaudes"] = "Les couleurs de votre palette illuminent votre teint."
                if not impact.get("effet_couleurs_froides"):
                    impact["effet_couleurs_froides"] = "Les couleurs contraires créent un contraste moins flatteur."
                if not impact.get("pourquoi"):
                    impact["pourquoi"] = "Votre undertone naturel s'harmonise mieux avec certaines teintes."
                
                result["analyse_colorimetrique_detaillee"] = analyse_detail
            
            saison = result.get("saison_confirmee", "Unknown")
            print(f"✅ Colorimétrie analysée: {saison}")
            print(f"   ✓ Yeux: {result.get('eye_color')}")
            print(f"   ✓ Cheveux: {result.get('hair_color')}")
            print(f"   ✓ Palette personnalisée: {len(palette)} couleurs")
            print(f"   ✓ Guide Maquillage: {bool(result.get('guide_maquillage'))}")
            print(f"   ✓ Analyse détaillée: {bool(result.get('analyse_colorimetrique_detaillee'))}")
            
            return result
            
        except Exception as e:
            print(f"❌ Erreur analyse colorimétrie: {e}")
            import traceback
            traceback.print_exc()
            raise


# Instance globale
colorimetry_service = ColorimetryService()