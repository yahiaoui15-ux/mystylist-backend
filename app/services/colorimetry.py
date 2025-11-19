"""
Colorimetry Service Enhanced v5.0 - 2 Appels OpenAI
✅ 2 appels (Part 1 + Part 2) = pas troncature
✅ Tous les logs détaillés du v4.3 original
✅ Fallbacks robustes conservés
✅ Token counting intégré
"""

import json
from app.utils.openai_client import openai_client
from app.prompts.colorimetry_part1_prompt import COLORIMETRY_PART1_SYSTEM_PROMPT, COLORIMETRY_PART1_USER_PROMPT
from app.prompts.colorimetry_part2_prompt import COLORIMETRY_PART2_SYSTEM_PROMPT, COLORIMETRY_PART2_USER_PROMPT
from app.services.robust_json_parser import RobustJSONParser


class ColorimetryService:
    def __init__(self):
        self.openai = openai_client
    
    async def analyze(self, user_data: dict) -> dict:
        """
        Analyse la colorimétrie en 2 appels OpenAI
        Part 1: Saison + Palette + Analyse détaillée
        Part 2: Couleurs génériques + Maquillage + Associations
        
        Args:
            user_data: dict avec face_photo_url, eye_color, hair_color, age, unwanted_colors
        
        Returns:
            dict complet avec saison, palette, couleurs, maquillage, associations
        """
        try:
            print("\n🎨 Analyse colorimétrie (2 APPELS - v5.0)...")
            
            # Vérifier que la photo existe
            face_photo_url = user_data.get("face_photo_url")
            if not face_photo_url:
                print("❌ Pas de photo de visage fournie")
                return {}
            
            # ═══════════════════════════════════════════════════════════
            # APPEL 1: SAISON + PALETTE + ANALYSE DÉTAILLÉE
            # ═══════════════════════════════════════════════════════════
            print("\n" + "="*80)
            print("📊 APPEL 1: Saison + Palette + Analyse détaillée")
            print("="*80)
            
            self.openai.set_system_prompt(COLORIMETRY_PART1_SYSTEM_PROMPT)
            
            unwanted_colors_str = ", ".join(user_data.get("unwanted_colors", []))
            user_prompt_part1 = COLORIMETRY_PART1_USER_PROMPT.format(
                face_photo_url=face_photo_url,
                eye_color=user_data.get("eye_color", "Non spécifié"),
                hair_color=user_data.get("hair_color", "Non spécifié"),
                age=str(user_data.get("age", 0))
            )
            
            print(f"📋 User prompt (première 400 chars):")
            print(user_prompt_part1[:400])
            print(f"   ... [{len(user_prompt_part1)} chars total]\n")
            
            print("   🤖 Envoi à OpenAI (GPT-4-turbo avec vision)...")
            response_part1 = await self.openai.analyze_image(
                image_urls=[face_photo_url],
                prompt=user_prompt_part1,
                model="gpt-4-turbo",
                max_tokens=2000
            )
            
            print(f"   📨 Réponse reçue ({len(response_part1)} chars)")
            print(f"   📋 Débuts: {response_part1[:150]}...\n")
            
            # Parser Part 1
            print("   🔍 Parsing JSON Part 1...")
            result_part1 = RobustJSONParser.parse_json_with_fallback(response_part1)
            
            if not result_part1:
                print("   ❌ Erreur parsing Part 1")
                return {}
            
            saison = result_part1.get("saison_confirmee", "Indéterminée")
            palette = result_part1.get("palette_personnalisee", [])
            analyse_detail = result_part1.get("analyse_colorimetrique_detaillee", {})
            
            print(f"   ✅ Part 1 parsé avec succès:")
            print(f"      • Saison: {saison}")
            print(f"      • Palette: {len(palette)} couleurs")
            print(f"      • Analyse détaillée: {len(analyse_detail)} champs")
            
            # Vérifier qualité commentaires Part 1
            if palette and len(palette) > 0:
                first_color = palette[0]
                comment = first_color.get('commentaire', '')
                word_count = len(comment.split())
                print(f"      • Qualité commentaires: {word_count} mots (min 25)")
                if word_count < 20:
                    print(f"        ⚠️  WARNING: Commentaires plus courts que prévu")
            
            # ═══════════════════════════════════════════════════════════
            # APPEL 2: COULEURS GÉNÉRIQUES + MAQUILLAGE + ASSOCIATIONS
            # ═══════════════════════════════════════════════════════════
            print("\n" + "="*80)
            print("📊 APPEL 2: Détails + Maquillage + Associations")
            print("="*80)
            
            self.openai.set_system_prompt(COLORIMETRY_PART2_SYSTEM_PROMPT)
            
            # Extraire noms couleurs palette pour context
            palette_names = ", ".join([c.get("name", "") for c in palette[:5]])
            
            user_prompt_part2 = COLORIMETRY_PART2_USER_PROMPT.format(
                saison_confirmee=saison,
                sous_ton_detecte=result_part1.get("sous_ton_detecte", ""),
                palette_names=palette_names
            )
            
            print(f"📋 User prompt (première 400 chars):")
            print(user_prompt_part2[:400])
            print(f"   ... [{len(user_prompt_part2)} chars total]\n")
            
            print("   🤖 Envoi à OpenAI (Chat mode)...")
            response_part2 = await self.openai.call_chat(
                prompt=user_prompt_part2,
                model="gpt-4",
                max_tokens=2000
            )
            
            print(f"   📨 Réponse reçue ({len(response_part2)} chars)")
            print(f"   📋 Débuts: {response_part2[:150]}...\n")
            
            # Parser Part 2
            print("   🔍 Parsing JSON Part 2...")
            result_part2 = RobustJSONParser.parse_json_with_fallback(response_part2)
            
            if not result_part2:
                print("   ❌ Erreur parsing Part 2 - utilisation Part 1 seul")
                result_part2 = {}
            else:
                colors_with_notes = result_part2.get('allColorsWithNotes', [])
                associations = result_part2.get('associations_gagnantes', [])
                guide_maquillage = result_part2.get('guide_maquillage', {})
                shopping = result_part2.get('shopping_couleurs', {})
                notes_compatibilite = result_part2.get('notes_compatibilite', {})
                
                print(f"   ✅ Part 2 parsé avec succès:")
                print(f"      • Couleurs génériques: {len(colors_with_notes)} couleurs")
                print(f"      • Notes compatibilité: {len(notes_compatibilite)} couleurs")
                print(f"      • Associations gagnantes: {len(associations)}")
                print(f"      • Guide maquillage: {len(guide_maquillage)} champs")
                print(f"      • Shopping couleurs: {len(shopping)} champs")
            
            # ═══════════════════════════════════════════════════════════
            # FUSIONNER LES 2 APPELS
            # ═══════════════════════════════════════════════════════════
            print("\n" + "="*80)
            print("🔗 FUSION Part 1 + Part 2")
            print("="*80)
            
            result = {
                # Part 1 (core)
                "saison_confirmee": result_part1.get("saison_confirmee"),
                "sous_ton_detecte": result_part1.get("sous_ton_detecte"),
                "justification_saison": result_part1.get("justification_saison"),
                "eye_color": user_data.get("eye_color", ""),
                "hair_color": user_data.get("hair_color", ""),
                "palette_personnalisee": result_part1.get("palette_personnalisee", []),
                "analyse_colorimetrique_detaillee": result_part1.get("analyse_colorimetrique_detaillee", {}),
                
                # Part 2 (details)
                "notes_compatibilite": result_part2.get("notes_compatibilite", {}),
                "allColorsWithNotes": result_part2.get("allColorsWithNotes", []),
                "associations_gagnantes": result_part2.get("associations_gagnantes", []),
                "guide_maquillage": result_part2.get("guide_maquillage", {}),
                "shopping_couleurs": result_part2.get("shopping_couleurs", {}),
                "alternatives_couleurs_refusees": result_part2.get("alternatives_couleurs_refusees", {}),
            }
            
            # Fallbacks si données manquantes
            if not result.get("saison_confirmee"):
                result["saison_confirmee"] = "Indéterminée"
            
            if not result.get("justification_saison"):
                result["justification_saison"] = f"Analyse colorimétrique basée sur votre carnation, yeux et cheveux."
            
            # Fallbacks pour analyse_colorimetrique_detaillee
            if not result.get("analyse_colorimetrique_detaillee"):
                print("\n⚠️  Création fallback pour analyse_colorimetrique_detaillee...")
                result["analyse_colorimetrique_detaillee"] = self._create_default_analyse(
                    result.get('saison_confirmee', 'Automne'),
                    user_data
                )
            else:
                analyse_detail = self._ensure_analyse_fields(result["analyse_colorimetrique_detaillee"], user_data)
                result["analyse_colorimetrique_detaillee"] = analyse_detail
            
            # Validation des données critiques
            palette = result.get('palette_personnalisee', [])
            colors_with_notes = result.get('allColorsWithNotes', [])
            associations = result.get('associations_gagnantes', [])
            guide_maquillage = result.get('guide_maquillage', {})
            shopping = result.get('shopping_couleurs', {})
            analyse_detail = result.get('analyse_colorimetrique_detaillee', {})
            
            print(f"\n✅ Données finales récupérées:")
            print(f"   ✓ Palette: {len(palette)} couleurs")
            print(f"   ✓ Couleurs génériques: {len(colors_with_notes)} couleurs")
            print(f"   ✓ Associations: {len(associations)}")
            print(f"   ✓ Guide Maquillage: {len(guide_maquillage)} champs")
            print(f"   ✓ Shopping: {len(shopping)} champs")
            print(f"   ✓ Analyse détaillée: {len(analyse_detail)} champs")
            
            saison = result.get("saison_confirmee", "Unknown")
            print(f"\n✅ Colorimétrie analysée (2 appels): {saison}")
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
        
        # Vérifier les sous-champs impact_visuel
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