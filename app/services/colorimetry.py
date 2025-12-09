"""
Colorimetry Service v8.2 - Avec call_tracker pour logs structurés
✅ 3 appels optimisés avec tracking clair
✅ Chaque partie (Part 1, 2, 3) loggée séparément
✅ Résumé final par section
"""

import json
import re
from app.utils.openai_client import openai_client
from app.utils.openai_call_tracker import call_tracker
from app.prompts.colorimetry_part1_prompt import COLORIMETRY_PART1_SYSTEM_PROMPT, COLORIMETRY_PART1_USER_PROMPT
from app.prompts.colorimetry_part2_prompt import (
    COLORIMETRY_PART2_SYSTEM_PROMPT,
    COLORIMETRY_PART2_USER_PROMPT_TEMPLATE,
    FALLBACK_PALETTE_AND_ASSOCIATIONS
)
from app.prompts.colorimetry_part3_prompt import COLORIMETRY_PART3_SYSTEM_PROMPT, COLORIMETRY_PART3_USER_PROMPT_TEMPLATE
from app.services.robust_json_parser import RobustJSONParser


class ColorimetryService:
    def __init__(self):
        self.openai = openai_client
    
    async def analyze(self, user_data: dict) -> dict:
        """
        Analyse colorimétrie en 3 appels OpenAI
        Part 1: Saison + Analyses détaillées
        Part 2: Palette + Couleurs génériques + Associations
        Part 3: Notes compatibilité + Maquillage
        """
        try:
            print("\n🎨 ANALYSE COLORIMETRIE (3 APPELS)")
            
            face_photo_url = user_data.get("face_photo_url")
            if not face_photo_url:
                print("❌ Pas de photo de visage fournie")
                return {}
            
            # ═══════════════════════════════════════════════════════════
            # PART 1: SAISON + ANALYSES
            # ═══════════════════════════════════════════════════════════
            print("\n" + "="*80)
            print("📊 PART 1: Saison + Analyses détaillées")
            print("="*80 + "\n")
            
            # Définir le contexte pour le tracking
            self.openai.set_context("Colorimetry", "Part 1")
            self.openai.set_system_prompt(COLORIMETRY_PART1_SYSTEM_PROMPT)
            
            user_prompt_part1 = COLORIMETRY_PART1_USER_PROMPT.format(
                face_photo_url=face_photo_url,
                eye_color=user_data.get("eye_color", "Non spécifié"),
                hair_color=user_data.get("hair_color", "Non spécifié"),
                age=str(user_data.get("age", 0))
            )
            
            print(f"🤖 Appel OpenAI Vision...")
            response_part1 = await self.openai.analyze_image(
                image_urls=[face_photo_url],
                prompt=user_prompt_part1,
                model="gpt-4-turbo",
                max_tokens=1200
            )
            
            # Le call_tracker a déjà loggé via openai_client
            # Mais on peut ajouter le résultat du parsing
            content_part1 = response_part1["content"]
            
            # Parser
            result_part1 = RobustJSONParser.parse_json_with_fallback(content_part1)
            
            if not result_part1:
                print("❌ Erreur parsing Part 1")
                call_tracker.log_error("Colorimetry", "Part 1 parsing failed")
                return {}
            
            saison = result_part1.get("saison_confirmee", "Indéterminée")
            sous_ton = result_part1.get("sous_ton_detecte", "neutre")
            analyses = len(result_part1.get("analyse_colorimetrique_detaillee", {}))
            
            print(f"\n✅ RÉSULTAT Part 1:")
            print(f"   • Saison: {saison}")
            print(f"   • Sous-ton: {sous_ton}")
            print(f"   • Analyses: {analyses} champs\n")
            
            # ═══════════════════════════════════════════════════════════
            # PART 2: PALETTE + ASSOCIATIONS
            # ═══════════════════════════════════════════════════════════
            print("="*80)
            print("📊 PART 2: Palette + Associations")
            print("="*80 + "\n")
            
            self.openai.set_context("Colorimetry", "Part 2")
            self.openai.set_system_prompt(COLORIMETRY_PART2_SYSTEM_PROMPT)
            
            user_prompt_part2 = COLORIMETRY_PART2_USER_PROMPT_TEMPLATE.format(
                SAISON=saison,
                SOUS_TON=sous_ton,
                EYE_COLOR=result_part1.get("eye_color", user_data.get("eye_color")),
                HAIR_COLOR=result_part1.get("hair_color", user_data.get("hair_color"))
            )
            
            print(f"🤖 Appel OpenAI Chat...")
            response_part2 = await self.openai.call_chat(
                prompt=user_prompt_part2,
                model="gpt-4",
                max_tokens=1400
            )
            
            content_part2 = response_part2["content"]
            
            # Parser avec cleanup
            content_part2_cleaned = self._fix_json_for_parsing(content_part2)
            result_part2 = RobustJSONParser.parse_json_with_fallback(content_part2_cleaned)
            
            # Vérifier palette
            palette = result_part2.get("palette_personnalisee", []) if result_part2 else []
            associations = result_part2.get("associations_gagnantes", []) if result_part2 else []
            all_colors = result_part2.get("allColorsWithNotes", []) if result_part2 else []
            
            using_fallback = False
            if not palette or len(palette) == 0:
                print("⚠️ Palette vide, utilisation FALLBACK")
                result_part2 = FALLBACK_PALETTE_AND_ASSOCIATIONS.copy()
                palette = result_part2.get("palette_personnalisee", [])
                associations = result_part2.get("associations_gagnantes", [])
                all_colors = result_part2.get("allColorsWithNotes", [])
                using_fallback = True
            
            fallback_label = " (FALLBACK)" if using_fallback else ""
            print(f"\n✅ RÉSULTAT Part 2{fallback_label}:")
            print(f"   • Palette: {len(palette)} couleurs")
            print(f"   • AllColorsWithNotes: {len(all_colors)} couleurs")
            print(f"   • Associations: {len(associations)} occasions\n")
            
            # ═══════════════════════════════════════════════════════════
            # PART 3: MAQUILLAGE + VERNIS
            # ═══════════════════════════════════════════════════════════
            print("="*80)
            print("📊 PART 3: Maquillage + Vernis")
            print("="*80 + "\n")
            
            self.openai.set_context("Colorimetry", "Part 3")
            self.openai.set_system_prompt(COLORIMETRY_PART3_SYSTEM_PROMPT)
            
            unwanted_colors = user_data.get("unwanted_colors", [])
            unwanted_str = ", ".join(unwanted_colors) if unwanted_colors else "Aucune"
            
            user_prompt_part3 = COLORIMETRY_PART3_USER_PROMPT_TEMPLATE.format(
                SAISON=saison,
                SOUS_TON=sous_ton,
                UNWANTED_COLORS=unwanted_str
            )
            
            print(f"🤖 Appel OpenAI Chat...")
            response_part3 = await self.openai.call_chat(
                prompt=user_prompt_part3,
                model="gpt-4",
                max_tokens=1400
            )
            
            content_part3 = response_part3["content"]
            
            # Parser
            content_part3_cleaned = self._fix_json_for_parsing(content_part3)
            result_part3 = RobustJSONParser.parse_json_with_fallback(content_part3_cleaned)
            
            if not result_part3:
                print("⚠️ Erreur Part 3, utilisant fallback vide")
                result_part3 = {}
            else:
                unwanted = result_part3.get("unwanted_colors", [])
                makeup = result_part3.get("guide_maquillage", {})
                nails = result_part3.get("nailColors", [])
                print(f"\n✅ RÉSULTAT Part 3:")
                print(f"   • Couleurs refusées: {len(unwanted)}")
                print(f"   • Guide maquillage: {len(makeup)} champs")
                print(f"   • Vernis: {len(nails)} couleurs\n")
            
            # ═══════════════════════════════════════════════════════════
            # FUSION ET RÉSUMÉ
            # ═══════════════════════════════════════════════════════════
            result = {
                # Part 1
                "saison_confirmee": result_part1.get("saison_confirmee", "Indéterminée"),
                "sous_ton_detecte": result_part1.get("sous_ton_detecte", "neutre"),
                "justification_saison": result_part1.get("justification_saison", ""),
                "eye_color": result_part1.get("eye_color", user_data.get("eye_color")),
                "hair_color": result_part1.get("hair_color", user_data.get("hair_color")),
                "analyse_colorimetrique_detaillee": result_part1.get("analyse_colorimetrique_detaillee", {}),
                
                # Part 2
                "palette_personnalisee": palette,
                "allColorsWithNotes": all_colors,
                "associations_gagnantes": associations,
                
                # Part 3
                "notes_compatibilite": result_part3.get("notes_compatibilite", {}),
                "unwanted_colors": result_part3.get("unwanted_colors", []),
                "guide_maquillage": result_part3.get("guide_maquillage", {}),
                "nailColors": result_part3.get("nailColors", [])
            }
            
            # Fallback analyse
            if not result.get("analyse_colorimetrique_detaillee"):
                result["analyse_colorimetrique_detaillee"] = self._create_default_analyse(
                    result.get("saison_confirmee", "Automne"),
                    user_data
                )
            
            print("="*80)
            print("✅ RÉSUMÉ COLORIMETRIE:")
            print(f"   • Saison: {result.get('saison_confirmee')}")
            print(f"   • Palette: {len(result.get('palette_personnalisee', []))} couleurs")
            print(f"   • Associations: {len(result.get('associations_gagnantes', []))}")
            print(f"   • Maquillage: {len(result.get('guide_maquillage', {}))} champs")
            print("="*80 + "\n")
            
            return result
            
        except Exception as e:
            print(f"\n❌ ERREUR COLORIMETRIE: {e}")
            call_tracker.log_error("Colorimetry", str(e))
            import traceback
            traceback.print_exc()
            raise
    
    def _fix_json_for_parsing(self, text: str) -> str:
        """Nettoie le JSON avant parsing"""
        if not text:
            return text
        
        # Supprimer caractères de contrôle
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)
        
        # Remplacer \' par ' (invalide en JSON)
        text = text.replace("\\'", "'")
        
        # Fixer les escapes invalides
        def fix_invalid_escapes(match):
            char = match.group(1)
            if char in '"\\bfnrt/':
                return match.group(0)
            if char == 'u':
                return match.group(0)
            return char
        
        text = re.sub(r'\\([^"\\bfnrtu/])', fix_invalid_escapes, text)
        
        return text
    
    def _create_default_analyse(self, saison: str, user_data: dict) -> dict:
        """Fallback analyse"""
        return {
            "temperature": "chaud" if saison in ["Automne", "Printemps"] else "froid",
            "valeur": "medium",
            "intensite": "medium",
            "contraste_naturel": "moyen",
            "description_teint": f"Votre teint s'harmonise avec la saison {saison}.",
            "description_yeux": f"Vos yeux {user_data.get('eye_color', 'de couleur variée')} enrichissent votre profil.",
            "description_cheveux": f"Vos cheveux {user_data.get('hair_color', 'de teinte naturelle')} complètent votre palette.",
            "harmonie_globale": f"Harmonie typique de la saison {saison}.",
            "bloc_emotionnel": f"Votre {saison} apporte luminosité et confiance.",
            "impact_visuel": {
                "effet_couleurs_chaudes": "Illuminent votre teint naturellement.",
                "effet_couleurs_froides": "Créent moins d'harmonie.",
                "pourquoi": "Votre sous-ton réagit favorablement à votre saison."
            }
        }


# Instance globale
colorimetry_service = ColorimetryService()