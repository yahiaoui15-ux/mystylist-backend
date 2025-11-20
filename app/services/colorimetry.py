"""
Colorimetry Service Enhanced v7.0 - 3 APPELS OPTIMISÉS
✅ Part 1: Saison + Analyses détaillées (50+ mots)
✅ Part 2: Palette + Couleurs génériques + Associations
✅ Part 3: Notes compatibilité + Unwanted colors + Maquillage + Vernis
"""

import json
from app.utils.openai_client import openai_client
from app.prompts.colorimetry_part1_prompt import COLORIMETRY_PART1_SYSTEM_PROMPT, COLORIMETRY_PART1_USER_PROMPT
from app.prompts.colorimetry_part2_prompt import COLORIMETRY_PART2_SYSTEM_PROMPT, COLORIMETRY_PART2_USER_PROMPT_TEMPLATE
from app.prompts.colorimetry_part3_prompt import COLORIMETRY_PART3_SYSTEM_PROMPT, COLORIMETRY_PART3_USER_PROMPT_TEMPLATE
from app.services.robust_json_parser import RobustJSONParser


class ColorimetryService:
    def __init__(self):
        self.openai = openai_client
    
    async def analyze(self, user_data: dict) -> dict:
        """
        Analyse colorimétrie en 3 appels OpenAI optimisés pour tokens.
        Part 1: Saison + Analyses détaillées
        Part 2: Palette 12 + Couleurs génériques + Associations
        Part 3: Notes compatibilité + Unwanted colors + Maquillage
        """
        try:
            print("\n🎨 Analyse colorimétrie (3 APPELS - v7.0)...")
            
            face_photo_url = user_data.get("face_photo_url")
            if not face_photo_url:
                print("❌ Pas de photo de visage fournie")
                return {}
            
            # ═══════════════════════════════════════════════════════════
            # APPEL 1: SAISON + ANALYSES DÉTAILLÉES
            # ═══════════════════════════════════════════════════════════
            print("\n" + "="*80)
            print("📊 APPEL 1: Saison + Analyses détaillées (50+ mots)")
            print("="*80)
            
            self.openai.set_system_prompt(COLORIMETRY_PART1_SYSTEM_PROMPT)
            
            user_prompt_part1 = COLORIMETRY_PART1_USER_PROMPT.format(
                face_photo_url=face_photo_url,
                eye_color=user_data.get("eye_color", "Non spécifié"),
                hair_color=user_data.get("hair_color", "Non spécifié"),
                age=str(user_data.get("age", 0))
            )
            
            print(f"📋 User prompt (première 300 chars): {user_prompt_part1[:300]}...")
            print("   🤖 Envoi à OpenAI (gpt-4-turbo avec vision)...")
            
            response_part1 = await self.openai.analyze_image(
                image_urls=[face_photo_url],
                prompt=user_prompt_part1,
                model="gpt-4-turbo",
                max_tokens=1200
            )
            
            print(f"   📨 Réponse reçue ({len(response_part1)} chars)")
            print("   🔴 RÉPONSE BRUTE PART 1 (premiers 300 chars):")
            print(response_part1[:300])
            
            print("   🔍 Parsing JSON Part 1...")
            result_part1 = RobustJSONParser.parse_json_with_fallback(response_part1)
            
            if not result_part1:
                print("   ❌ Erreur parsing Part 1")
                return {}
            
            saison = result_part1.get("saison_confirmee", "Indéterminée")
            sous_ton = result_part1.get("sous_ton_detecte", "neutre")
            eye_color = result_part1.get("eye_color", user_data.get("eye_color"))
            hair_color = result_part1.get("hair_color", user_data.get("hair_color"))
            analyse_detail = result_part1.get("analyse_colorimetrique_detaillee", {})
            
            print(f"   ✅ Part 1 parsé:")
            print(f"      • Saison: {saison}")
            print(f"      • Sous-ton: {sous_ton}")
            print(f"      • Analyses détaillées: {len(analyse_detail)} champs")
            
            # ═══════════════════════════════════════════════════════════
            # APPEL 2: PALETTE + COULEURS GÉNÉRIQUES + ASSOCIATIONS
            # ═══════════════════════════════════════════════════════════
            print("\n" + "="*80)
            print("📊 APPEL 2: Palette + Couleurs génériques + Associations")
            print("="*80)
            
            self.openai.set_system_prompt(COLORIMETRY_PART2_SYSTEM_PROMPT)
            
            user_prompt_part2 = COLORIMETRY_PART2_USER_PROMPT_TEMPLATE.format(
                SAISON=saison,
                SOUS_TON=sous_ton,
                EYE_COLOR=eye_color,
                HAIR_COLOR=hair_color
            )
            
            print(f"📋 User prompt (première 300 chars): {user_prompt_part2[:300]}...")
            print("   🤖 Envoi à OpenAI (gpt-4 chat)...")
            
            response_part2 = await self.openai.call_chat(
                prompt=user_prompt_part2,
                model="gpt-4",
                max_tokens=1400
            )
            
            print(f"   📨 Réponse reçue ({len(response_part2)} chars)")
            print("   🔴 RÉPONSE BRUTE PART 2 (premiers 300 chars):")
            print(response_part2[:300])
            
            print("   🔍 Parsing JSON Part 2...")
            response_part2_cleaned = response_part2.replace('\r', ' ').replace('\x00', '')
            result_part2 = RobustJSONParser.parse_json_with_fallback(response_part2_cleaned)
            
            if not result_part2:
                print("   ⚠️ Erreur Part 2, utilisant fallback")
                result_part2 = {}
            else:
                palette = result_part2.get("palette_personnalisee", [])
                associations = result_part2.get("associations_gagnantes", [])
                print(f"   ✅ Part 2 parsé:")
                print(f"      • Palette: {len(palette)} couleurs")
                print(f"      • Associations: {len(associations)} occasions")
            
            # ═══════════════════════════════════════════════════════════
            # APPEL 3: NOTES COMPATIBILITÉ + UNWANTED + MAQUILLAGE
            # ═══════════════════════════════════════════════════════════
            print("\n" + "="*80)
            print("📊 APPEL 3: Compatibilité + Unwanted colors + Maquillage")
            print("="*80)
            
            self.openai.set_system_prompt(COLORIMETRY_PART3_SYSTEM_PROMPT)
            
            unwanted_colors = user_data.get("unwanted_colors", [])
            unwanted_str = ", ".join(unwanted_colors) if unwanted_colors else "Aucune"
            
            user_prompt_part3 = COLORIMETRY_PART3_USER_PROMPT_TEMPLATE.format(
                SAISON=saison,
                SOUS_TON=sous_ton,
                UNWANTED_COLORS=unwanted_str
            )
            
            print(f"📋 User prompt (première 300 chars): {user_prompt_part3[:300]}...")
            print(f"   Couleurs refusées: {unwanted_str}")
            print("   🤖 Envoi à OpenAI (gpt-4 chat)...")
            
            response_part3 = await self.openai.call_chat(
                prompt=user_prompt_part3,
                model="gpt-4",
                max_tokens=1400
            )
            
            print(f"   📨 Réponse reçue ({len(response_part3)} chars)")
            print("   🔴 RÉPONSE BRUTE PART 3 (premiers 300 chars):")
            print(response_part3[:300])
            
            print("   🔍 Parsing JSON Part 3...")
            response_part3_cleaned = response_part3.replace('\r', ' ').replace('\x00', '')
            result_part3 = RobustJSONParser.parse_json_with_fallback(response_part3_cleaned)
            
            if not result_part3:
                print("   ⚠️ Erreur Part 3, utilisant fallback")
                result_part3 = {}
            else:
                unwanted = result_part3.get("unwanted_colors", [])
                makeup = result_part3.get("guide_maquillage", {})
                nails = result_part3.get("nailColors", [])
                print(f"   ✅ Part 3 parsé:")
                print(f"      • Couleurs refusées traitées: {len(unwanted)}")
                print(f"      • Guide maquillage: {len(makeup)} champs")
                print(f"      • Vernis: {len(nails)} couleurs")
            
            # ═══════════════════════════════════════════════════════════
            # FUSION 3 APPELS
            # ═══════════════════════════════════════════════════════════
            print("\n" + "="*80)
            print("🔗 FUSION Part 1 + Part 2 + Part 3")
            print("="*80)
            
            result = {
                # Part 1
                "saison_confirmee": result_part1.get("saison_confirmee", "Indéterminée"),
                "sous_ton_detecte": result_part1.get("sous_ton_detecte", "neutre"),
                "eye_color": eye_color,
                "hair_color": hair_color,
                "analyse_colorimetrique_detaillee": result_part1.get("analyse_colorimetrique_detaillee", {}),
                
                # Part 2
                "palette_personnalisee": result_part2.get("palette_personnalisee", []),
                "allColorsWithNotes": result_part2.get("allColorsWithNotes", []),
                "associations_gagnantes": result_part2.get("associations_gagnantes", []),
                
                # Part 3
                "notes_compatibilite": result_part3.get("notes_compatibilite", {}),
                "unwanted_colors": result_part3.get("unwanted_colors", []),
                "guide_maquillage": result_part3.get("guide_maquillage", {}),
                "nailColors": result_part3.get("nailColors", [])
            }
            
            # Fallbacks
            if not result.get("palette_personnalisee") and result_part2:
                palette = result_part2.get("palette_personnalisee", [])
                result["palette_personnalisee"] = palette
                print(f"   ✅ Palette consolidée: {len(palette)} couleurs")
            
            if not result.get("analyse_colorimetrique_detaillee"):
                result["analyse_colorimetrique_detaillee"] = self._create_default_analyse(
                    result.get("saison_confirmee", "Automne"),
                    user_data
                )
            
            print(f"\n✅ RÉSUMÉ FINAL:")
            print(f"   • Saison: {result.get('saison_confirmee')}")
            print(f"   • Palette: {len(result.get('palette_personnalisee', []))} couleurs")
            print(f"   • Couleurs génériques: {len(result.get('allColorsWithNotes', []))}")
            print(f"   • Associations: {len(result.get('associations_gagnantes', []))}")
            print(f"   • Couleurs refusées analysées: {len(result.get('unwanted_colors', []))}")
            print(f"   • Guide maquillage: {len(result.get('guide_maquillage', {}))} champs\n")
            
            return result
            
        except Exception as e:
            print(f"\n❌ Erreur analyse colorimétrie: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _create_default_analyse(self, saison: str, user_data: dict) -> dict:
        """Fallback analyse si OpenAI échoue"""
        return {
            "temperature": "chaud" if saison in ["Automne", "Printemps"] else "froid",
            "valeur": "médium",
            "intensite": "médium",
            "contraste_naturel": "moyen",
            "description_teint": f"Votre teint s'harmonise naturellement avec la saison {saison}.",
            "description_yeux": f"Vos yeux {user_data.get('eye_color', 'de couleur variée')} enrichissent votre profil colorimétrique.",
            "description_cheveux": f"Vos cheveux {user_data.get('hair_color', 'de teinte naturelle')} complètent votre palette {saison}.",
            "harmonie_globale": f"Tous vos éléments créent une harmonie cohérente typique de la saison {saison}.",
            "bloc_emotionnel": f"Votre {saison} apporte luminosité et confiance à votre apparence naturelle.",
            "impact_visuel": {
                "effet_couleurs_chaudes": "Illuminent votre teint naturellement.",
                "effet_couleurs_froides": "Créent moins d'harmonie avec votre sous-ton.",
                "pourquoi": "Votre sous-ton naturel réagit favorablement aux couleurs alignées à votre saison."
            }
        }


# Instance globale
colorimetry_service = ColorimetryService()