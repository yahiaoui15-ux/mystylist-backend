"""
Colorimetry Service v9.2 - FIXE avec analyze_image()
✅ Utilise analyze_image() pour les appels Vision avec images
✅ Placeholders en MAJUSCULES: {FACE_PHOTO}, {EYE_COLOR}, {HAIR_COLOR}, {AGE}
✅ Chaque appel OpenAI = bloc isolé avec Before/During/After clair
✅ Part 1: Vision avec image
✅ Part 2 & 3: Chat texte pur
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
        Part 1: Saison + Analyses détaillées (avec image)
        Part 2: Palette + Couleurs génériques + Associations (texte)
        Part 3: Notes compatibilité + Maquillage + Couleurs refusées (texte)
        """
        try:
            print("\n" + "="*80)
            print("🎨 ANALYSE COLORIMETRIE - 3 APPELS SEQUENTIELS")
            print("="*80)
            
            # ✅ FIX: Chercher photo en snake_case OU camelCase
            face_photo_url = user_data.get("face_photo_url")
            if not face_photo_url:
                face_photo_url = user_data.get("facePhotoUrl")  # camelCase fallback
            
            if not face_photo_url:
                print("❌ Pas de photo de visage fournie")
                return {}
            
            # ✅ FIX: Chercher eye_color et hair_color aussi en camelCase
            eye_color = user_data.get("eye_color") or user_data.get("eyeColor")
            hair_color = user_data.get("hair_color") or user_data.get("hairColor")
            
            # ═══════════════════════════════════════════════════════════
            # PART 1: SAISON + ANALYSES
            # ═══════════════════════════════════════════════════════════
            result_part1 = await self._call_part1(user_data, face_photo_url, eye_color, hair_color)
            if not result_part1:
                return {}
            
            saison = result_part1.get("saison_confirmee", "Indéterminée")
            sous_ton = result_part1.get("sous_ton_detecte", "neutre")
            
            # ═══════════════════════════════════════════════════════════
            # PART 2: PALETTE + ASSOCIATIONS + COULEURS GÉNÉRIQUES
            # ═══════════════════════════════════════════════════════════
            result_part2 = await self._call_part2(
                saison, 
                sous_ton,
                result_part1.get("eye_color", eye_color),
                result_part1.get("hair_color", hair_color)
            )
            if not result_part2:
                result_part2 = FALLBACK_PART2_DATA.copy()
            
            palette = result_part2.get("palette_personnalisee", [])
            associations = result_part2.get("associations_gagnantes", [])
            generiques = result_part2.get("couleurs_generiques", [])
            all_colors_raw = result_part2.get("allColorsWithNotes", [])
            
            # ═══════════════════════════════════════════════════════════
            # PART 3: MAQUILLAGE + VERNIS + COULEURS REFUSÉES
            # ═══════════════════════════════════════════════════════════
            unwanted_colors = user_data.get("unwanted_colors", [])
            result_part3 = await self._call_part3(saison, sous_ton, unwanted_colors)
            if not result_part3:
                result_part3 = {}
            
            # ═══════════════════════════════════════════════════════════
            # ✅ FIX: Construire allColorsWithNotes complète
            # ═══════════════════════════════════════════════════════════
            all_colors_with_notes = self._build_all_colors_with_notes(
                palette,
                all_colors_raw,
                result_part3.get("unwanted_colors", [])
            )
            
            # ═══════════════════════════════════════════════════════════
            # ✅ FIX: Créer structure "makeup" pour PDFMonkey (Page 7)
            # ═══════════════════════════════════════════════════════════
            makeup_structure = self._build_makeup_structure(result_part3)
            
            # ═══════════════════════════════════════════════════════════
            # ✅ FIX: Extraire couleurs à manier avec prudence (Page 5)
            # ═══════════════════════════════════════════════════════════
            couleurs_prudence = self._extract_colors_by_note_range(all_colors_with_notes, 4, 6)
            
            # ═══════════════════════════════════════════════════════════
            # ✅ FIX: Extraire couleurs à éviter (Page 5)
            # ═══════════════════════════════════════════════════════════
            couleurs_eviter = self._extract_colors_by_note_range(all_colors_with_notes, 0, 3)
            
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
                "eye_color": result_part1.get("eye_color", eye_color),
                "hair_color": result_part1.get("hair_color", hair_color),
                "analyse_colorimetrique_detaillee": result_part1.get("analyse_colorimetrique_detaillee", {}),
                
                # ✅ PAGE 3: Palette personnalisée (10 couleurs, 8-10/10)
                "palette_personnalisee": palette,
                
                # ✅ PAGE 4: Couleurs génériques (Bleu, Rouge, Jaune, etc. 7-10/10)
                "couleurs_generiques": generiques,
                
                # ✅ PAGE 5: Couleurs à manier avec prudence (4-6/10)
                "couleurs_prudence": couleurs_prudence,
                
                # ✅ PAGE 5: Couleurs à éviter (<4/10)
                "couleurs_eviter": couleurs_eviter,
                
                # Toutes les couleurs avec notes (pour debug/reference)
                "allColorsWithNotes": all_colors_with_notes,
                
                # Associations de couleurs
                "associations_gagnantes": associations,
                
                # Notes de compatibilité complètes
                "notes_compatibilite": result_part3.get("notes_compatibilite", {}),
                
                # Couleurs refusées brutes
                "unwanted_colors": result_part3.get("unwanted_colors", []),
                
                # ✅ PAGE 7: Guide maquillage structuré
                "guide_maquillage": result_part3.get("guide_maquillage", {}),
                
                # ✅ PAGE 7: Structure makeup mappée pour PDFMonkey
                "makeup": makeup_structure,
                
                # Couleurs vernis ongles
                "nailColors": result_part3.get("nailColors", [])
            }
            
            print(f"   • Saison: {result.get('saison_confirmee')}")
            print(f"   • Palette personnalisée: {len(result.get('palette_personnalisee', []))} couleurs (8-10/10)")
            print(f"   • Couleurs génériques: {len(result.get('couleurs_generiques', []))} couleurs (7-10/10)")
            print(f"   • Couleurs prudence: {len(result.get('couleurs_prudence', []))} couleurs (4-6/10)")
            print(f"   • Couleurs à éviter: {len(result.get('couleurs_eviter', []))} couleurs (<4/10)")
            print(f"   • Associations: {len(result.get('associations_gagnantes', []))} occasions")
            print(f"   • Vernis ongles: {len(result.get('nailColors', []))} couleurs")
            print(f"   • Guide maquillage: {len(result.get('guide_maquillage', {}))} champs")
            print("="*80 + "\n")
            
            return result
            
        except Exception as e:
            print(f"\n❌ ERREUR COLORIMETRIE: {e}")
            call_tracker.log_error("Colorimetry", str(e))
            import traceback
            traceback.print_exc()
            raise
    
    def _build_all_colors_with_notes(self, palette: list, all_colors_raw: list, unwanted: list) -> list:
        """✅ Construit allColorsWithNotes depuis palette + alternatives + refusées"""
        colors_dict = {}
        
        # Ajouter palette (priorité haute)
        for color in palette:
            display_name = color.get("displayName", color.get("name", ""))
            if display_name and display_name not in colors_dict:
                colors_dict[display_name] = color
        
        # Ajouter alternatives (priorité moyenne)
        for color in all_colors_raw:
            display_name = color.get("displayName", color.get("name", ""))
            if display_name and display_name not in colors_dict:
                colors_dict[display_name] = color
        
        # Ajouter couleurs refusées (priorité basse)
        for color in unwanted:
            display_name = color.get("displayName", color.get("name", ""))
            if display_name and display_name not in colors_dict:
                colors_dict[display_name] = color
        
        # Convertir en liste et trier par note décroissante
        all_colors = list(colors_dict.values())
        all_colors.sort(key=lambda x: x.get("note", 5), reverse=True)
        
        print(f"\n   ✅ allColorsWithNotes construite: {len(all_colors)} couleurs uniques")
        return all_colors
    
    def _extract_colors_by_note_range(self, all_colors: list, min_note: int, max_note: int) -> list:
        """✅ Extrait les couleurs dans une plage de notes donnée"""
        filtered = [
            color for color in all_colors
            if min_note <= color.get("note", 5) <= max_note
        ]
        filtered.sort(key=lambda x: x.get("note", 5), reverse=True)
        return filtered
    
    def _build_makeup_structure(self, result_part3: dict) -> dict:
        """✅ Construit structure makeup pour PDFMonkey (Page 7)"""
        guide = result_part3.get("guide_maquillage", {})
        
        makeup = {
            "foundation": guide.get("teint", {}),
            "eyes": guide.get("yeux", {}),
            "lips": guide.get("levres", {}),
            "nails": guide.get("ongles", {})
        }
        
        print(f"\n   ✅ Makeup structure créée:")
        print(f"      • Foundation: {len(makeup['foundation'])} champs" if makeup['foundation'] else "      • Foundation: vide")
        print(f"      • Eyes: {len(makeup['eyes'])} champs" if makeup['eyes'] else "      • Eyes: vide")
        print(f"      • Lips: {len(makeup['lips'])} champs" if makeup['lips'] else "      • Lips: vide")
        print(f"      • Nails: {len(makeup['nails'])} champs" if makeup['nails'] else "      • Nails: vide")
        
        return makeup
    
    async def _call_part1(self, user_data: dict, face_photo_url: str, eye_color: str = None, hair_color: str = None) -> dict:
        """PART 1 - Vision avec image"""
        print("\n" + "="*80)
        print("📋 APPEL 1/3: COLORIMETRY PART 1 - SAISON + ANALYSES")
        print("="*80)
        
        try:
            print("\n📌 AVANT APPEL:")
            print(f"   • Type: OpenAI Vision (gpt-4-turbo)")
            print(f"   • Max tokens: 1000")
            print(f"   • Image: {face_photo_url[:60]}...")
            
            self.openai.set_context("Colorimetry", "Part 1")
            self.openai.set_system_prompt(COLORIMETRY_PART1_SYSTEM_PROMPT)
            
            # ✅ FIX: Placeholders en MAJUSCULES + AGE ajouté
            user_prompt = COLORIMETRY_PART1_USER_PROMPT.format(
                FACE_PHOTO=face_photo_url,
                EYE_COLOR=eye_color or user_data.get("eye_color", "indéterminé"),
                HAIR_COLOR=hair_color or user_data.get("hair_color", "indéterminé"),
                AGE=user_data.get("age", "indéterminé")
            )
            
            print(f"\n🤖 APPEL OPENAI EN COURS...")
            # ✅ FIX: Utiliser analyze_image() au lieu de call_chat() avec has_image
            response = await self.openai.analyze_image(
                image_urls=[face_photo_url],
                prompt=user_prompt,
                model="gpt-4-turbo",
                max_tokens=1000
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
                print(f"      • Saison: {result.get('saison_confirmee', 'N/A')}")
                print(f"      • Sous-ton: {result.get('sous_ton_detecte', 'N/A')}")
            else:
                print(f"   ⚠️  Erreur parsing")
                result = {}
            
            print("\n" + "="*80 + "\n")
            return result
            
        except Exception as e:
            print(f"\n❌ ERREUR PART 1: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    async def _call_part2(self, saison: str, sous_ton: str, eye_color: str, hair_color: str) -> dict:
        """PART 2 - Texte pur"""
        print("\n" + "="*80)
        print("📋 APPEL 2/3: COLORIMETRY PART 2 - PALETTE + COULEURS GÉNÉRIQUES + ASSOCIATIONS")
        print("="*80)
        
        try:
            print("\n📌 AVANT APPEL:")
            print(f"   • Type: OpenAI Chat (gpt-4-turbo)")
            print(f"   • Max tokens: 1200")
            print(f"   • Input data: saison={saison}, sous_ton={sous_ton}")
            
            self.openai.set_context("Colorimetry", "Part 2")
            self.openai.set_system_prompt(COLORIMETRY_PART2_SYSTEM_PROMPT)
            
            user_prompt = COLORIMETRY_PART2_USER_PROMPT_TEMPLATE.format(
                SAISON=saison,
                SOUS_TON=sous_ton,
                EYE_COLOR=eye_color or "indéterminé",
                HAIR_COLOR=hair_color or "indéterminé"
            )
            
            print(f"\n🤖 APPEL OPENAI EN COURS...")
            response = await self.openai.call_chat(
                prompt=user_prompt,
                model="gpt-4-turbo",
                max_tokens=1500
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
            
            content = response.get("content", "")
            print(f"\n📝 RÉPONSE BRUTE (premiers 400 chars):")
            print(f"   {content[:400]}...")
            
            print(f"\n🔍 PARSING JSON (avec retry + fallback robuste):")
            
            parser = ColorimetryJSONParser()
            content_cleaned = parser.clean_gpt_response(content)
            result = parser.parse_json_safely(content_cleaned, max_retries=3)
            
            if result and parser.validate_part2_structure(result):
                palette = result.get("palette_personnalisee", [])
                generiques = result.get("couleurs_generiques", [])
                associations = result.get("associations_gagnantes", [])
                print(f"   ✅ Succès (parsing robuste)")
                print(f"      • Palette personnalisée: {len(palette)} couleurs")
                print(f"      • Couleurs génériques: {len(generiques)} couleurs")
                print(f"      • Associations: {len(associations)} occasions")
            else:
                print(f"   ⚠️  Parsing échoué → FALLBACK")
                result = FALLBACK_PART2_DATA.copy()
            
            print("\n" + "="*80 + "\n")
            return result
            
        except Exception as e:
            print(f"\n❌ ERREUR PART 2: {e}")
            import traceback
            traceback.print_exc()
            return FALLBACK_PART2_DATA.copy()
    
    async def _call_part3(self, saison: str, sous_ton: str, unwanted_colors: list) -> dict:
        """PART 3 - Texte pur"""
        print("\n" + "="*80)
        print("📋 APPEL 3/3: COLORIMETRY PART 3 - MAQUILLAGE + VERNIS + COULEURS REFUSÉES")
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
                max_tokens=1800
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
            
            content = response.get("content", "")
            print(f"\n📝 RÉPONSE BRUTE (premiers 400 chars):")
            print(f"   {content[:400]}...")
            
            print(f"\n🔍 PARSING JSON:")
            content_cleaned = self._fix_json_for_parsing(content)
            result = RobustJSONParser.parse_json_with_fallback(content_cleaned)
            
            if result:
                print(f"   ✅ Succès")
                print(f"      • Vernis ongles: {len(result.get('nailColors', []))} couleurs")
                print(f"      • Guide maquillage: {len(result.get('guide_maquillage', {}))} champs")
                print(f"      • Couleurs refusées: {len(result.get('unwanted_colors', []))} couleurs")
            else:
                print(f"   ⚠️  Erreur parsing")
                result = {}
            
            print("\n" + "="*80 + "\n")
            return result
            
        except Exception as e:
            print(f"\n❌ ERREUR PART 3: {e}")
            import traceback
            traceback.print_exc()
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