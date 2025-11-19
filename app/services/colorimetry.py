"""
Colorimetry Service Enhanced v4.3
✅ Utilise le prompt enrichi avec commentaires 20-25 mots
✅ Intègre le token counting
✅ Backward compatible - peut remplacer colorimetry.py directement
✅ Fallbacks robustes
"""

import json
from app.utils.openai_client import openai_client
from app.prompts.colorimetry_prompt import (
    COLORIMETRY_SYSTEM_PROMPT,
    COLORIMETRY_USER_PROMPT
)
from app.services.robust_json_parser import RobustJSONParser


class ColorimetryService:
    def __init__(self):
        self.openai = openai_client
    
    async def analyze(self, user_data: dict) -> dict:
        """
        Analyse la colorimétrie d'une cliente avec prompt enrichi
        
        Args:
            user_data: dict avec face_photo_url, eye_color, hair_color, age, unwanted_colors
        
        Returns:
            dict avec saison_confirmee, palette_personnalisee, commentaires enrichis, etc.
        """
        try:
            print("\n🎨 Analyse colorimétrie (ENRICHIE v4.3)...")
            
            # Vérifier que la photo existe
            face_photo_url = user_data.get("face_photo_url")
            if not face_photo_url:
                print("❌ Pas de photo de visage fournie")
                return {}
            
            # ✅ NOUVEAU: Stocker le system prompt pour token counting
            self.openai.set_system_prompt(COLORIMETRY_SYSTEM_PROMPT)
            
            # Construire le prompt utilisateur avec données réelles
            unwanted_colors_str = ", ".join(user_data.get("unwanted_colors", []))
            user_prompt = COLORIMETRY_USER_PROMPT.replace(
                "{face_photo_url}", face_photo_url
            ).replace(
                "{eye_color}", user_data.get("eye_color", "Non spécifié")
            ).replace(
                "{hair_color}", user_data.get("hair_color", "Non spécifié")
            ).replace(
                "{age}", str(user_data.get("age", 0))
            ).replace(
                "{unwanted_colors}", unwanted_colors_str or "Aucune"
            )
            
            # Log prompts (première 500 chars)
            print("\n" + "="*80)
            print("📋 PROMPT ENVOYÉ À OPENAI:")
            print("="*80)
            print(f"System prompt (première 300 chars):")
            print(COLORIMETRY_SYSTEM_PROMPT[:300])
            print(f"\n... [{len(COLORIMETRY_SYSTEM_PROMPT)} chars total]\n")
            
            print(f"User prompt (première 400 chars):")
            print(user_prompt[:400])
            print(f"\n... [{len(user_prompt)} chars total]")
            print("="*80 + "\n")
            
            # Appel OpenAI Vision avec token counting intégré
            print("   🤖 Envoi à OpenAI (GPT-4-turbo avec vision)...")
            response = await self.openai.analyze_image(
                image_urls=[face_photo_url],
                prompt=user_prompt,
                model="gpt-4-turbo",
                max_tokens=4000
            )
            
            # Log réponse
            print("\n" + "="*80)
            print("📋 RÉPONSE COMPLÈTE D'OPENAI:")
            print("="*80)
            print(response)
            print("="*80)
            print(f"Longueur réponse: {len(response)} chars\n")
            
            print(f"   🎨 Réponse reçue ({len(response)} chars)")
            print(f"   📋 Débuts: {response[:150]}...")
            
            # Parser robuste
            print("\n📋 PARSING JSON:")
            print(f"   Avant: Type={type(response)}, Longueur={len(response)}")
            
            result = RobustJSONParser.parse_json_with_fallback(response)
            
            print(f"   Après: Type={type(result)}, Clés={list(result.keys()) if result else 'NONE'}")
            
            if not result:
                print("❌ Impossible de parser la réponse JSON")
                return {}
            
            # Validation des données critiques
            palette = result.get('palette_personnalisee', [])
            colors_with_notes = result.get('allColorsWithNotes', [])
            associations = result.get('associationsGagnantes', [])
            guide_maquillage = result.get('guide_maquillage', {})
            shopping = result.get('shopping_couleurs', {})
            analyse_detail = result.get('analyse_colorimetrique_detaillee', {})
            
            print(f"\n✅ Données récupérées:")
            print(f"   ✓ Palette: {len(palette)} couleurs")
            print(f"   ✓ All Colors: {len(colors_with_notes)} couleurs")
            print(f"   ✓ Associations: {len(associations)}")
            print(f"   ✓ Guide Maquillage: {len(guide_maquillage)} champs")
            print(f"   ✓ Shopping: {len(shopping)} champs")
            print(f"   ✓ Analyse détaillée: {len(analyse_detail)} champs")
            
            # Vérification commentaires enrichis
            if palette and len(palette) > 0:
                first_color = palette[0]
                comment = first_color.get('commentaire', '')
                word_count = len(comment.split())
                print(f"\n📊 Vérification qualité commentaires:")
                print(f"   Premier commentaire: {word_count} mots")
                if word_count < 15:
                    print(f"   ⚠️  WARNING: Commentaires encore trop courts!")
                elif word_count >= 20:
                    print(f"   ✅ Bon: Commentaires assez longs (>= 20 mots)")
            
            # ✅ AJOUTER données utilisateur
            result["eye_color"] = user_data.get("eye_color", "")
            result["hair_color"] = user_data.get("hair_color", "")
            
            # Fallbacks si données manquantes
            if not result.get("saison_confirmee"):
                result["saison_confirmee"] = "Indéterminée"
            
            if not result.get("justification_saison"):
                result["justification_saison"] = f"Analyse colorimétrique complète basée sur votre carnation, yeux et cheveux."
            
            # Fallbacks pour analyse_colorimetrique_detaillee
            if not analyse_detail:
                print("\n⚠️  Création fallback pour analyse_colorimetrique_detaillee...")
                result["analyse_colorimetrique_detaillee"] = self._create_default_analyse(
                    result.get('saison_confirmee', 'Automne'),
                    user_data
                )
            else:
                # Compléter clés manquantes
                analyse_detail = self._ensure_analyse_fields(analyse_detail, user_data)
                result["analyse_colorimetrique_detaillee"] = analyse_detail
            
            saison = result.get("saison_confirmee", "Unknown")
            print(f"\n✅ Colorimétrie analysée: {saison}")
            print(f"   ✓ Yeux: {result.get('eye_color')}")
            print(f"   ✓ Cheveux: {result.get('hair_color')}")
            print(f"   ✓ Palette: {len(palette)} couleurs")
            print(f"   ✓ Guide Maquillage: {bool(guide_maquillage)}")
            print(f"   ✓ Analyse détaillée: {bool(result.get('analyse_colorimetrique_detaillee'))}\n")
            
            return result
            
        except Exception as e:
            print(f"\n❌ Erreur analyse colorimétrie: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _create_default_analyse(self, saison: str, user_data: dict) -> dict:
        """Crée une structure d'analyse par défaut si OpenAI ne la génère pas"""
        return {
            "temperature": "neutre",
            "valeur": "médium",
            "intensite": "médium",
            "contraste_naturel": "moyen",
            "description_teint": f"Votre teint présente des caractéristiques harmonieuses typiques de la saison {saison}.",
            "description_yeux": f"Vos yeux {user_data.get('eye_color', 'de couleur variée')} contribuent à l'harmonie de votre profil colorimétrique.",
            "description_cheveux": f"Vos cheveux {user_data.get('hair_color', 'de teinte naturelle')} complètent parfaitement votre palette saisonnière.",
            "harmonie_globale": "Tous les éléments de votre profil colorimétrique s'harmonisent ensemble de manière naturelle.",
            "bloc_emotionnel": f"Votre profil colorimétrique {saison} apporte luminosité et confiance à votre apparence naturelle.",
            "impact_visuel": {
                "effet_couleurs_chaudes": "Les couleurs de votre palette illuminent votre teint de manière naturelle et flatteuse.",
                "effet_couleurs_froides": "Les couleurs en dehors de votre palette créent un contraste moins harmonieux.",
                "pourquoi": "Votre sous-ton naturel s'harmonise mieux avec certaines teintes colorées qu'avec d'autres."
            }
        }
    
    def _ensure_analyse_fields(self, analyse: dict, user_data: dict) -> dict:
        """Remplit les champs manquants dans analyse_colorimetrique_detaillee"""
        defaults = self._create_default_analyse("Automne", user_data)
        
        for key in defaults.keys():
            if not analyse.get(key):
                analyse[key] = defaults[key]
        
        # Vérifier les sous-champs
        if not analyse.get("impact_visuel"):
            analyse["impact_visuel"] = defaults["impact_visuel"]
        else:
            impact = analyse["impact_visuel"]
            for key in defaults["impact_visuel"].keys():
                if not impact.get(key):
                    impact[key] = defaults["impact_visuel"][key]
        
        return analyse


# Instance globale
colorimetry_service = ColorimetryService()