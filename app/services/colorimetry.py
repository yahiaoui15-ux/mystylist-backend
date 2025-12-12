"""
Colorimetry Service v9.0 - Logging STRUCTURÉ et CLOISONNÉ par appel
✅ Chaque appel OpenAI = bloc isolé avec Before/During/After clair
✅ Aucun mélange de réponses brutes entre les sections
✅ Ordre logique: Avant → Appel → Tokens → Réponse brute → Parsing
✅ Format cohérent pour tous les appels (Part 1, 2, 3)
"""

import json
import re
from datetime import datetime
from app.utils.openai_client import openai_client
from app.utils.openai_call_tracker import call_tracker
from app.prompts.colorimetry_part1_prompt import COLORIMETRY_PART1_SYSTEM_PROMPT, COLORIMETRY_PART1_USER_PROMPT
from app.prompts.colorimetry_part2_prompt import (
    COLORIMETRY_PART2_SYSTEM_PROMPT,
    COLORIMETRY_PART2_USER_PROMPT_TEMPLATE,
    FALLBACK_PART2_DATA
)
from app.prompts.colorimetry_part3_prompt import COLORIMETRY_PART3_SYSTEM_PROMPT, COLORIMETRY_PART3_USER_PROMPT_TEMPLATE
from app.services.robust_json_parser import RobustJSONParser
from app.services.colorimetry_parsing_utilities import ColorimetryJSONParser


class ColorimetryService:
    def __init__(self):
        self.openai = openai_client
    
    async def analyze(self, user_data: dict) -> dict:
        """
        Analyse colorimétrie en 3 appels OpenAI - LOGS STRUCTURÉS
        Part 1: Saison + Analyses détaillées
        Part 2: Palette + Couleurs génériques + Associations
        Part 3: Notes compatibilité + Maquillage
        """
        try:
            print("\n" + "="*80)
            print("🎨 ANALYSE COLORIMETRIE - 3 APPELS SEQUENTIELS")
            print("="*80)
            
            face_photo_url = user_data.get("face_photo_url")
            if not face_photo_url:
                print("❌ Pas de photo de visage fournie")
                return {}
            
            # ═══════════════════════════════════════════════════════════
            # PART 1: SAISON + ANALYSES
            # ═══════════════════════════════════════════════════════════
            result_part1 = await self._call_part1(user_data, face_photo_url)
            if not result_part1:
                return {}
            
            saison = result_part1.get("saison_confirmee", "Indéterminée")
            sous_ton = result_part1.get("sous_ton_detecte", "neutre")
            
            # ═══════════════════════════════════════════════════════════
            # PART 2: PALETTE + ASSOCIATIONS
            # ═══════════════════════════════════════════════════════════
            result_part2 = await self._call_part2(
                saison, 
                sous_ton,
                result_part1.get("eye_color", user_data.get("eye_color")),
                result_part1.get("hair_color", user_data.get("hair_color"))
            )
            if not result_part2:
                result_part2 = FALLBACK_PART2_DATA.copy()
            
            palette = result_part2.get("palette_personnalisee", [])
            associations = result_part2.get("associations_gagnantes", [])
            all_colors = result_part2.get("allColorsWithNotes", [])
            
            # ═══════════════════════════════════════════════════════════
            # PART 3: MAQUILLAGE + VERNIS
            # ═══════════════════════════════════════════════════════════
            unwanted_colors = user_data.get("unwanted_colors", [])
            result_part3 = await self._call_part3(saison, sous_ton, unwanted_colors)
            if not result_part3:
                result_part3 = {}
            
            # ═══════════════════════════════════════════════════════════
            # FUSION FINALE
            # ═══════════════════════════════════════════════════════════
            print("\n" + "="*80)
            print("✅ RÉSUMÉ COLORIMETRIE COMPLÈTE")
            print("="*80)
            
            result = {
                "saison_confirmee": result_part1.get("saison_confirmee", "Indéterminée"),
                "sous_ton_detecte": result_part1.get("sous_ton_detecte", "neutre"),
                "justification_saison": result_part1.get("justification_saison", ""),
                "eye_color": result_part1.get("eye_color", user_data.get("eye_color")),
                "hair_color": result_part1.get("hair_color", user_data.get("hair_color")),
                "analyse_colorimetrique_detaillee": result_part1.get("analyse_colorimetrique_detaillee", {}),
                "palette_personnalisee": palette,
                "allColorsWithNotes": all_colors,
                "associations_gagnantes": associations,
                "notes_compatibilite": result_part3.get("notes_compatibilite", {}),
                "unwanted_colors": result_part3.get("unwanted_colors", []),
                "guide_maquillage": result_part3.get("guide_maquillage", {}),
                "nailColors": result_part3.get("nailColors", [])
            }
            
            print(f"   • Saison: {result.get('saison_confirmee')}")
            print(f"   • Palette: {len(result.get('palette_personnalisee', []))} couleurs")
            print(f"   • AllColors: {len(result.get('allColorsWithNotes', []))} couleurs")
            print(f"   • Associations: {len(result.get('associations_gagnantes', []))} occasions")
            print(f"   • Guide maquillage: {len(result.get('guide_maquillage', {}))} champs")
            print("="*80 + "\n")
            
            return result
            
        except Exception as e:
            print(f"\n❌ ERREUR COLORIMETRIE: {e}")
            call_tracker.log_error("Colorimetry", str(e))
            import traceback
            traceback.print_exc()
            raise
    
    async def _call_part1(self, user_data: dict, face_photo_url: str) -> dict:
        """PART 1 - Logging cloisonné"""
        print("\n" + "="*80)
        print("📋 APPEL 1/3: COLORIMETRY PART 1 - SAISON + ANALYSES")
        print("="*80)
        
        try:
            print("\n📌 AVANT APPEL:")
            print(f"   • Type: OpenAI Vision API (gpt-4-turbo)")
            print(f"   • Max tokens: 1200")
            print(f"   • Image: {face_photo_url[:50]}...")
            print(f"   • Input data: eye={user_data.get('eye_color')}, hair={user_data.get('hair_color')}, age={user_data.get('age')}")
            
            self.openai.set_context("Colorimetry", "Part 1")
            self.openai.set_system_prompt(COLORIMETRY_PART1_SYSTEM_PROMPT)
            
            user_prompt = COLORIMETRY_PART1_USER_PROMPT.format(
                face_photo_url=face_photo_url,
                eye_color=user_data.get("eye_color", "Non spécifié"),
                hair_color=user_data.get("hair_color", "Non spécifié"),
                age=str(user_data.get("age", 0))
            )
            
            print(f"\n🤖 APPEL OPENAI EN COURS...")
            response = await self.openai.analyze_image(
                image_urls=[face_photo_url],
                prompt=user_prompt,
                model="gpt-4-turbo",
                max_tokens=1200
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
            result = RobustJSONParser.parse_json_with_fallback(content)
            
            if result:
                print(f"   ✅ Succès")
                print(f"      • Saison: {result.get('saison_confirmee', '?')}")
                print(f"      • Sous-ton: {result.get('sous_ton_detecte', '?')}")
                print(f"      • Champs principaux: {len(result)}")
            else:
                print(f"   ❌ Erreur parsing JSON")
                return {}
            
            print("\n" + "="*80 + "\n")
            return result
            
        except Exception as e:
            print(f"\n❌ ERREUR PART 1: {e}")
            return {}
    
    async def _call_part2(self, saison: str, sous_ton: str, eye_color: str, hair_color: str) -> dict:
        """PART 2 - Logging cloisonné avec parsing robuste (v10.0 OPTIMISÉ)"""
        print("\n" + "="*80)
        print("📋 APPEL 2/3: COLORIMETRY PART 2 - PALETTE + ASSOCIATIONS (OPTIMISÉ)")
        print("="*80)
        
        try:
            print("\n📌 AVANT APPEL:")
            print(f"   • Type: OpenAI Chat (gpt-4-turbo)")
            print(f"   • Max tokens: 1200 (réduit de 40% pour moins d'erreurs)")
            print(f"   • Input data: saison={saison}, sous_ton={sous_ton}")
            print(f"   • Stratégie: FRANÇAIS UNIQUEMENT + 15 objets JSON")
            
            self.openai.set_context("Colorimetry", "Part 2")
            self.openai.set_system_prompt(COLORIMETRY_PART2_SYSTEM_PROMPT)
            
            user_prompt = COLORIMETRY_PART2_USER_PROMPT_TEMPLATE.format(
                SAISON=saison,
                SOUS_TON=sous_ton,
                EYE_COLOR=eye_color,
                HAIR_COLOR=hair_color
            )
            
            print(f"\n🤖 APPEL OPENAI EN COURS...")
            response = await self.openai.call_chat(
                prompt=user_prompt,
                model="gpt-4-turbo",
                max_tokens=1200
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
            
            print(f"\n🔍 PARSING JSON (avec retry + fallback robuste):")
            
            # Utiliser le parser robuste amélioré
            parser = ColorimetryJSONParser()
            
            # 1. Nettoyer la réponse
            content_cleaned = parser.clean_gpt_response(content)
            
            # 2. Parser avec retry
            result = parser.parse_json_safely(content_cleaned, max_retries=3)
            
            # 3. Valider structure
            if result and parser.validate_part2_structure(result):
                palette = result.get("palette_personnalisee", [])
                associations = result.get("associations_gagnantes", [])
                print(f"   ✅ Succès (parsing robuste)")
                print(f"      • Palette: {len(palette)} couleurs")
                print(f"      • Associations: {len(associations)} occasions")
            else:
                print(f"   ⚠️  Parsing échoué ou structure invalide → FALLBACK")
                result = FALLBACK_PART2_DATA.copy()
                print(f"      • Palette fallback: {len(result.get('palette_personnalisee', []))} couleurs")
                print(f"      • Associations fallback: {len(result.get('associations_gagnantes', []))} occasions")
            
            print("\n" + "="*80 + "\n")
            return result
            
        except Exception as e:
            print(f"\n❌ ERREUR PART 2: {e}")
            print(f"   ⚠️  FALLBACK utilisé")
            import traceback
            traceback.print_exc()
            return FALLBACK_PART2_DATA.copy()
    
    async def _call_part3(self, saison: str, sous_ton: str, unwanted_colors: list) -> dict:
        """PART 3 - Logging cloisonné"""
        print("\n" + "="*80)
        print("📋 APPEL 3/3: COLORIMETRY PART 3 - MAQUILLAGE + VERNIS")
        print("="*80)
        
        try:
            unwanted_str = ", ".join(unwanted_colors) if unwanted_colors else "Aucune"
            
            print("\n📌 AVANT APPEL:")
            print(f"   • Type: OpenAI Chat (gpt-4)")
            print(f"   • Max tokens: 1400")
            print(f"   • Couleurs refusées: {unwanted_str}")
            
            self.openai.set_context("Colorimetry", "Part 3")
            self.openai.set_system_prompt(COLORIMETRY_PART3_SYSTEM_PROMPT)
            
            user_prompt = COLORIMETRY_PART3_USER_PROMPT_TEMPLATE.format(
                SAISON=saison,
                SOUS_TON=sous_ton,
                UNWANTED_COLORS=unwanted_str
            )
            
            print(f"\n🤖 APPEL OPENAI EN COURS...")
            response = await self.openai.call_chat(
                prompt=user_prompt,
                model="gpt-4",
                max_tokens=1400
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
            content_cleaned = self._fix_json_for_parsing(content)
            result = RobustJSONParser.parse_json_with_fallback(content_cleaned)
            
            if result:
                print(f"   ✅ Succès")
                print(f"      • Notes compatibilité: {len(result.get('notes_compatibilite', {}))} couleurs")
                print(f"      • Guide maquillage: {len(result.get('guide_maquillage', {}))} champs")
                print(f"      • Vernis: {len(result.get('nailColors', []))} couleurs")
            else:
                print(f"   ⚠️  Erreur parsing - résultat vide")
                result = {}
            
            print("\n" + "="*80 + "\n")
            return result
            
        except Exception as e:
            print(f"\n❌ ERREUR PART 3: {e}")
            return {}
    
    def _fix_json_for_parsing(self, text: str) -> str:
        """Nettoie le JSON avant parsing"""
        if not text:
            return text
        
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)
        text = text.replace("\\'", "'")
        
        def fix_invalid_escapes(match):
            char = match.group(1)
            if char in '"\\bfnrt/':
                return match.group(0)
            if char == 'u':
                return match.group(0)
            return char
        
        text = re.sub(r'\\([^"\\bfnrtu/])', fix_invalid_escapes, text)
        return text


colorimetry_service = ColorimetryService()