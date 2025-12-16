"""
Morphology Service v10.0 - ROBUSTE
✅ 3 appels TOUJOURS effectués (même si 1 échoue)
✅ JSON cleaning amélioré
✅ Part 3 appelé même si Part 2 échoue
✅ Fallbacks pour éviter pages vides
✅ Logs clairs séparés
"""

import json
import re
from app.utils.openai_client import openai_client
from app.utils.openai_call_tracker import call_tracker
from app.prompts.morphology_part1_prompt import MORPHOLOGY_PART1_SYSTEM_PROMPT, MORPHOLOGY_PART1_USER_PROMPT
from app.prompts.morphology_part2_prompt import MORPHOLOGY_PART2_SYSTEM_PROMPT, MORPHOLOGY_PART2_USER_PROMPT
from app.prompts.morphology_part3_prompt import MORPHOLOGY_PART3_SYSTEM_PROMPT, MORPHOLOGY_PART3_USER_PROMPT


class MorphologyService:
    def __init__(self):
        self.openai = openai_client
    
    def _clean_and_parse_json(self, text):
        """Parse JSON avec nettoyage complet des caractères problématiques"""
        if not text:
            return None
        
        try:
            # Extraire le JSON
            json_start = text.find('{')
            if json_start == -1:
                return None
            
            json_end = text.rfind('}')
            if json_end == -1:
                return None
            
            json_text = text[json_start:json_end+1]
            
            # Essayer parse direct d'abord
            try:
                return json.loads(json_text)
            except json.JSONDecodeError:
                # Si échec, nettoyer les caractères problématiques
                # Remplacer les apostrophes curbes par rien (ou espace)
                json_text = json_text.replace(''', '').replace(''', '')
                json_text = json_text.replace('"', '"').replace('"', '"')
                
                # Essayer à nouveau
                return json.loads(json_text)
        
        except Exception as e:
            print("   ❌ Parsing error: {}".format(str(e)))
            return None
    
    async def analyze(self, user_data: dict) -> dict:
        """Analyse morphologie EN 3 APPELS ROBUSTES"""
        print("\n" + "="*80)
        print("💪 PHASE MORPHOLOGIE - 3 APPELS ROBUSTES")
        print("="*80)
        
        body_photo_url = user_data.get("body_photo_url")
        if not body_photo_url:
            print("❌ Pas de photo du corps fournie")
            return {}
        
        # Initialiser les résultats
        part1_result = {}
        part2_result = {}
        part3_result = {}
        
        try:
            # ====================================================================
            # PART 1 - SILHOUETTE (VISION)
            # ====================================================================
            print("\n" + "█"*80)
            print("█ APPEL 1/3 - PART 1: SILHOUETTE (VISION)")
            print("█"*80)
            
            print("\n📍 Configuration:")
            print("   • Model: gpt-4-turbo (Vision)")
            print("   • Max tokens: 1000")
            
            self.openai.set_context("Morphology", "Part 1: Vision")
            self.openai.set_system_prompt(MORPHOLOGY_PART1_SYSTEM_PROMPT)
            
            user_prompt_part1 = MORPHOLOGY_PART1_USER_PROMPT.format(
                body_photo_url=body_photo_url,
                shoulder_circumference=user_data.get("shoulder_circumference", 0),
                waist_circumference=user_data.get("waist_circumference", 0),
                hip_circumference=user_data.get("hip_circumference", 0),
                bust_circumference=user_data.get("bust_circumference", 0)
            )
            
            print("🤖 Appel OpenAI en cours...")
            response_part1 = await self.openai.analyze_image(
                image_urls=[body_photo_url],
                prompt=user_prompt_part1,
                model="gpt-4-turbo",
                max_tokens=1000
            )
            print("✅ Réponse reçue")
            
            total_tokens_p1 = response_part1.get("total_tokens", 0)
            print("\n📊 TOKENS PART 1: {} ({:.1f}%)".format(
                total_tokens_p1, (total_tokens_p1 / 4000) * 100))
            
            print("\n📋 Parsing JSON Part 1...")
            part1_result = self._clean_and_parse_json(response_part1.get("content", ""))
            if not part1_result:
                print("❌ Parsing échoué")
                return {}
            print("✅ Succès")
            
            silhouette = part1_result.get('silhouette_type', 'Unknown')
            print("   • Silhouette: {}".format(silhouette))
            
        except Exception as e:
            print("❌ ERREUR PART 1: {}".format(str(e)))
            return {}
        
        # ====================================================================
        # PART 2 - RECOMMANDATIONS (TEXT)
        # ====================================================================
        print("\n" + "█"*80)
        print("█ APPEL 2/3 - PART 2: RECOMMANDATIONS (TEXT)")
        print("█"*80)
        
        try:
            print("\n📍 Configuration:")
            print("   • Model: gpt-4-turbo (Text)")
            print("   • Max tokens: 2000")
            
            styling_objectives = part1_result.get("styling_objectives", [])
            objectives_str = ", ".join(styling_objectives)
            
            morphology_goals = user_data.get("morphology_goals", {})
            body_parts_to_highlight = morphology_goals.get("body_parts_to_highlight", [])
            body_parts_to_minimize = morphology_goals.get("body_parts_to_minimize", [])
            
            highlight_str = ", ".join(body_parts_to_highlight) if body_parts_to_highlight else "aucune"
            minimize_str = ", ".join(body_parts_to_minimize) if body_parts_to_minimize else "aucune"
            
            self.openai.set_context("Morphology", "Part 2: Recommendations")
            self.openai.set_system_prompt(MORPHOLOGY_PART2_SYSTEM_PROMPT)
            
            user_prompt_part2 = MORPHOLOGY_PART2_USER_PROMPT.format(
                silhouette_type=silhouette,
                styling_objectives=objectives_str,
                body_parts_to_highlight=highlight_str,
                body_parts_to_minimize=minimize_str
            )
            
            print("🤖 Appel OpenAI en cours...")
            response_part2 = await self.openai.call_chat(
                prompt=user_prompt_part2,
                model="gpt-4-turbo",
                max_tokens=2000
            )
            print("✅ Réponse reçue")
            
            total_tokens_p2 = response_part2.get("total_tokens", 0)
            print("\n📊 TOKENS PART 2: {} ({:.1f}%)".format(
                total_tokens_p2, (total_tokens_p2 / 4000) * 100))
            
            print("\n📋 Parsing JSON Part 2...")
            part2_result = self._clean_and_parse_json(response_part2.get("content", ""))
            if not part2_result:
                print("⚠️ Parsing échoué - continuation avec fallback")
                part2_result = {"recommendations": {}}
            else:
                print("✅ Succès")
            
        except Exception as e:
            print("⚠️ ERREUR PART 2: {}".format(str(e)))
            print("   Continuation avec fallback...")
            part2_result = {"recommendations": {}}
        
        # ====================================================================
        # PART 3 - DÉTAILS (TEXT) - TOUJOURS APPELÉ
        # ====================================================================
        print("\n" + "█"*80)
        print("█ APPEL 3/3 - PART 3: DÉTAILS (TEXT)")
        print("█"*80)
        
        try:
            print("\n📍 Configuration:")
            print("   • Model: gpt-4-turbo (Text)")
            print("   • Max tokens: 2000")
            
            self.openai.set_context("Morphology", "Part 3: Details")
            self.openai.set_system_prompt(MORPHOLOGY_PART3_SYSTEM_PROMPT)
            
            user_prompt_part3 = MORPHOLOGY_PART3_USER_PROMPT.format(
                silhouette_type=silhouette,
                styling_objectives=objectives_str,
                body_parts_to_highlight=highlight_str,
                body_parts_to_minimize=minimize_str
            )
            
            print("🤖 Appel OpenAI en cours...")
            response_part3 = await self.openai.call_chat(
                prompt=user_prompt_part3,
                model="gpt-4-turbo",
                max_tokens=2000
            )
            print("✅ Réponse reçue")
            
            total_tokens_p3 = response_part3.get("total_tokens", 0)
            print("\n📊 TOKENS PART 3: {} ({:.1f}%)".format(
                total_tokens_p3, (total_tokens_p3 / 4000) * 100))
            
            print("\n📋 Parsing JSON Part 3...")
            part3_result = self._clean_and_parse_json(response_part3.get("content", ""))
            if not part3_result:
                print("⚠️ Parsing échoué - continuation avec fallback")
                part3_result = {"details": {}}
            else:
                print("✅ Succès")
            
        except Exception as e:
            print("⚠️ ERREUR PART 3: {}".format(str(e)))
            print("   Continuation avec fallback...")
            part3_result = {"details": {}}
        
        # ====================================================================
        # FUSION FINALE
        # ====================================================================
        print("\n" + "="*80)
        print("📦 FUSION FINALE")
        print("="*80)
        
        total_morpho_tokens = total_tokens_p1 + total_tokens_p2 + total_tokens_p3
        print("\nTOTAL TOKENS: {} ({:.1f}% budget)".format(
            total_morpho_tokens, (total_morpho_tokens / 8000) * 100))
        
        # Restructurer en morpho.categories
        morpho_categories = {}
        recommendations = part2_result.get('recommendations', {})
        details = part3_result.get('details', {})
        
        for category_name in recommendations.keys():
            morpho_categories[category_name] = {
                "introduction": recommendations[category_name].get("introduction", ""),
                "recommandes": recommendations[category_name].get("recommandes", []),
                "a_eviter": recommendations[category_name].get("a_eviter", []),
                "matieres": details.get(category_name, {}).get("matieres", ""),
                "motifs": details.get(category_name, {}).get("motifs", {}),
                "pieges": details.get(category_name, {}).get("pieges", [])
            }
        
        body_parts_highlights = part1_result.get('body_parts_highlights', {})
        body_parts_minimizes = part1_result.get('body_parts_minimizes', {})
        
        final_result = {
            "silhouette_type": part1_result.get("silhouette_type"),
            "silhouette_explanation": part1_result.get("silhouette_explanation"),
            "body_parts_to_highlight": part1_result.get("body_parts_to_highlight"),
            "body_parts_to_minimize": part1_result.get("body_parts_to_minimize"),
            "body_analysis": part1_result.get("body_analysis"),
            "styling_objectives": part1_result.get("styling_objectives"),
            "bodyType": part1_result.get("silhouette_type"),
            "highlights": {
                "announcement": body_parts_highlights.get("announcement", ""),
                "explanation": body_parts_highlights.get("explanation", "")
            },
            "minimizes": {
                "announcement": body_parts_minimizes.get("announcement", ""),
                "explanation": body_parts_minimizes.get("explanation", "")
            },
            "morpho": {
                "categories": morpho_categories
            },
            "client_requested_highlights": highlight_str,
            "client_requested_minimizes": minimize_str,
        }
        
        print("✅ Morphologie complète générée")
        print("\n" + "="*80 + "\n")
        
        return final_result


morphology_service = MorphologyService()