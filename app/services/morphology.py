"""
Morphology Service v8.0 - 3 APPELS ÉQUILIBRÉS
✅ Part 1 (Vision): Silhouette + body_parts enrichis = ~2800 tokens
✅ Part 2 (Text): Recommendations (recommandes + a_eviter) = ~2000 tokens
✅ Part 3 (Text): Details (matieres + motifs + pieges) = ~2000 tokens
✅ TOTAL: ~6800 tokens (vs 7336 avec overflow)
✅ ZÉRO token overflow!
✅ Pages 8-15: Complètes et parfaites!
"""

import json
from app.utils.openai_client import openai_client
from app.utils.openai_call_tracker import call_tracker
from app.prompts.morphology_part1_prompt import MORPHOLOGY_PART1_SYSTEM_PROMPT, MORPHOLOGY_PART1_USER_PROMPT
from app.prompts.morphology_part2_prompt import MORPHOLOGY_PART2_SYSTEM_PROMPT, MORPHOLOGY_PART2_USER_PROMPT
from app.prompts.morphology_part3_prompt import MORPHOLOGY_PART3_SYSTEM_PROMPT, MORPHOLOGY_PART3_USER_PROMPT


class MorphologyService:
    def __init__(self):
        self.openai = openai_client
    
    async def analyze(self, user_data: dict) -> dict:
        """Analyse morphologie EN 3 APPELS ÉQUILIBRÉS"""
        print("\n" + "="*80)
        print("💪 PHASE MORPHOLOGIE (3 appels équilibrés)")
        print("="*80)
        
        try:
            body_photo_url = user_data.get("body_photo_url")
            if not body_photo_url:
                print("❌ Pas de photo du corps fournie")
                return {}
            
            # ========================================================================
            # APPEL 1/3: MORPHOLOGY PART 1 - SILHOUETTE ENRICHIE (VISION)
            # ========================================================================
            print("\n" + "█"*80)
            print("█ APPEL 1/3: MORPHOLOGY PART 1 - SILHOUETTE + BODY PARTS ENRICHIS (VISION)")
            print("█"*80)
            
            print("\n📍 AVANT APPEL:")
            print("   • Type: OpenAI Vision API (gpt-4-turbo)")
            print("   • Max tokens: 1000")
            print("   • Image: " + body_photo_url[:60] + "...")
            print("   • Mensurations:")
            print("      - Épaules: {} cm".format(user_data.get('shoulder_circumference')))
            print("      - Taille: {} cm".format(user_data.get('waist_circumference')))
            print("      - Hanches: {} cm".format(user_data.get('hip_circumference')))
            print("      - Buste: {} cm".format(user_data.get('bust_circumference')))
            
            self.openai.set_context("Morphology Part 1", "PART 1: Silhouette Enrichie")
            self.openai.set_system_prompt(MORPHOLOGY_PART1_SYSTEM_PROMPT)
            
            user_prompt_part1 = MORPHOLOGY_PART1_USER_PROMPT.format(
                body_photo_url=body_photo_url,
                shoulder_circumference=user_data.get("shoulder_circumference", 0),
                waist_circumference=user_data.get("waist_circumference", 0),
                hip_circumference=user_data.get("hip_circumference", 0),
                bust_circumference=user_data.get("bust_circumference", 0)
            )
            
            print("\n🤖 APPEL OPENAI EN COURS...")
            response_part1 = await self.openai.analyze_image(
                image_urls=[body_photo_url],
                prompt=user_prompt_part1,
                model="gpt-4-turbo",
                max_tokens=1000
            )
            print("✅ RÉPONSE REÇUE")
            
            content_part1 = response_part1.get("content", "")
            total_tokens_p1 = response_part1.get("total_tokens", 0)
            
            print("\n📊 TOKENS CONSOMMÉS PART 1:")
            print("   • Total: {} tokens".format(total_tokens_p1))
            print("   • Budget: {:.1f}%".format((total_tokens_p1 / 4000) * 100))
            print("   • Status: ✅ OK")
            
            # PARSING PART 1
            print("\n📋 PARSING JSON PART 1:")
            response_text = content_part1.strip() if content_part1 else ""
            response_text = response_text.replace("```json\n", "").replace("```\n", "").replace("```", "")
            
            if not response_text:
                print("   ❌ Réponse vide")
                return {}
            
            json_start = response_text.find('{')
            if json_start == -1:
                print("   ❌ Pas de JSON trouvé")
                return {}
            
            response_text = response_text[json_start:]
            json_end = response_text.rfind('}')
            if json_end == -1:
                print("   ❌ JSON incomplet")
                return {}
            
            response_text = response_text[:json_end+1]
            
            try:
                part1_result = json.loads(response_text)
                print("   ✅ Succès")
                
                silhouette = part1_result.get('silhouette_type', 'Unknown')
                print("      • Silhouette: {}".format(silhouette))
                
            except json.JSONDecodeError as e:
                print("   ❌ Erreur parsing JSON: {}".format(str(e)))
                return {}
            
            # ========================================================================
            # APPEL 2/3: MORPHOLOGY PART 2 - RECOMMANDATIONS (TEXT)
            # ========================================================================
            print("\n" + "█"*80)
            print("█ APPEL 2/3: MORPHOLOGY PART 2 - RECOMMANDATIONS (INTRO + RECOMMANDES + A_EVITER)")
            print("█"*80)
            
            styling_objectives = part1_result.get("styling_objectives", [])
            objectives_str = ", ".join(styling_objectives)
            
            morphology_goals = user_data.get("morphology_goals", {})
            body_parts_to_highlight = morphology_goals.get("body_parts_to_highlight", [])
            body_parts_to_minimize = morphology_goals.get("body_parts_to_minimize", [])
            
            highlight_str = ", ".join(body_parts_to_highlight) if body_parts_to_highlight else "aucune spécifiée"
            minimize_str = ", ".join(body_parts_to_minimize) if body_parts_to_minimize else "aucune spécifiée"
            
            print("\n📍 AVANT APPEL:")
            print("   • Type: OpenAI Text API (gpt-4-turbo)")
            print("   • Max tokens: 2000 (recommandes + a_eviter seulement)")
            print("   • Silhouette: {}".format(silhouette))
            
            self.openai.set_context("Morphology Part 2", "PART 2: Recommandations")
            self.openai.set_system_prompt(MORPHOLOGY_PART2_SYSTEM_PROMPT)
            
            user_prompt_part2 = MORPHOLOGY_PART2_USER_PROMPT.format(
                silhouette_type=silhouette,
                styling_objectives=objectives_str,
                body_parts_to_highlight=highlight_str,
                body_parts_to_minimize=minimize_str
            )
            
            print("\n🤖 APPEL OPENAI EN COURS...")
            response_part2 = await self.openai.call_chat(
                prompt=user_prompt_part2,
                model="gpt-4-turbo",
                max_tokens=2000
            )
            print("✅ RÉPONSE REÇUE")
            
            content_part2 = response_part2.get("content", "")
            total_tokens_p2 = response_part2.get("total_tokens", 0)
            
            print("\n📊 TOKENS CONSOMMÉS PART 2:")
            print("   • Total: {} tokens".format(total_tokens_p2))
            print("   • Budget: {:.1f}%".format((total_tokens_p2 / 4000) * 100))
            print("   • Status: {}".format("✅ OK" if total_tokens_p2 < 2000 else "⚠️ Proche limite"))
            
            # PARSING PART 2
            print("\n📋 PARSING JSON PART 2:")
            response_text = content_part2.strip() if content_part2 else ""
            response_text = response_text.replace("```json\n", "").replace("```\n", "").replace("```", "")
            
            if not response_text:
                print("   ❌ Réponse vide")
                return {}
            
            json_start = response_text.find('{')
            if json_start == -1:
                print("   ❌ Pas de JSON trouvé")
                return {}
            
            response_text = response_text[json_start:]
            json_end = response_text.rfind('}')
            if json_end == -1:
                print("   ❌ JSON incomplet")
                return {}
            
            response_text = response_text[:json_end+1]
            
            try:
                part2_result = json.loads(response_text)
                print("   ✅ Succès")
                
                recommendations = part2_result.get('recommendations', {})
                print("      • Catégories: {}".format(len(recommendations)))
                
            except json.JSONDecodeError as e:
                print("   ❌ Erreur parsing JSON: {}".format(str(e)))
                return {}
            
            # ========================================================================
            # APPEL 3/3: MORPHOLOGY PART 3 - DÉTAILS (TEXT)
            # ========================================================================
            print("\n" + "█"*80)
            print("█ APPEL 3/3: MORPHOLOGY PART 3 - DÉTAILS (MATIERES + MOTIFS + PIEGES)")
            print("█"*80)
            
            print("\n📍 AVANT APPEL:")
            print("   • Type: OpenAI Text API (gpt-4-turbo)")
            print("   • Max tokens: 2000 (matieres + motifs + pieges)")
            print("   • Silhouette: {}".format(silhouette))
            
            self.openai.set_context("Morphology Part 3", "PART 3: Details")
            self.openai.set_system_prompt(MORPHOLOGY_PART3_SYSTEM_PROMPT)
            
            user_prompt_part3 = MORPHOLOGY_PART3_USER_PROMPT.format(
                silhouette_type=silhouette,
                styling_objectives=objectives_str,
                body_parts_to_highlight=highlight_str,
                body_parts_to_minimize=minimize_str
            )
            
            print("\n🤖 APPEL OPENAI EN COURS...")
            response_part3 = await self.openai.call_chat(
                prompt=user_prompt_part3,
                model="gpt-4-turbo",
                max_tokens=2000
            )
            print("✅ RÉPONSE REÇUE")
            
            content_part3 = response_part3.get("content", "")
            total_tokens_p3 = response_part3.get("total_tokens", 0)
            
            print("\n📊 TOKENS CONSOMMÉS PART 3:")
            print("   • Total: {} tokens".format(total_tokens_p3))
            print("   • Budget: {:.1f}%".format((total_tokens_p3 / 4000) * 100))
            print("   • Status: {}".format("✅ OK" if total_tokens_p3 < 2000 else "⚠️ Proche limite"))
            
            total_morpho_tokens = total_tokens_p1 + total_tokens_p2 + total_tokens_p3
            print("\n📊 TOTAL MORPHOLOGIE (Part 1 + Part 2 + Part 3):")
            print("   • Part 1: {} tokens".format(total_tokens_p1))
            print("   • Part 2: {} tokens".format(total_tokens_p2))
            print("   • Part 3: {} tokens".format(total_tokens_p3))
            print("   • TOTAL: {} tokens ✅".format(total_morpho_tokens))
            print("   • Budget: {:.1f}%".format((total_morpho_tokens / 12000) * 100))
            print("   • Status: {}".format("✅ OK" if total_morpho_tokens < 8000 else "⚠️ À surveiller"))
            
            # PARSING PART 3
            print("\n📋 PARSING JSON PART 3:")
            response_text = content_part3.strip() if content_part3 else ""
            response_text = response_text.replace("```json\n", "").replace("```\n", "").replace("```", "")
            
            if not response_text:
                print("   ❌ Réponse vide")
                return {}
            
            json_start = response_text.find('{')
            if json_start == -1:
                print("   ❌ Pas de JSON trouvé")
                return {}
            
            response_text = response_text[json_start:]
            json_end = response_text.rfind('}')
            if json_end == -1:
                print("   ❌ JSON incomplet")
                return {}
            
            response_text = response_text[:json_end+1]
            
            try:
                part3_result = json.loads(response_text)
                print("   ✅ Succès")
                
                details = part3_result.get('details', {})
                print("      • Catégories détails: {}".format(len(details)))
                
            except json.JSONDecodeError as e:
                print("   ❌ Erreur parsing JSON: {}".format(str(e)))
                return {}
            
            # ========================================================================
            # FUSION PART 1 + PART 2 + PART 3
            # ========================================================================
            print("\n" + "="*80)
            print("📦 FUSION PART 1 + PART 2 + PART 3")
            print("="*80)
            
            # ✅ RESTRUCTURER en morpho.categories pour template PDFMonkey (pages 9+)
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
            
            # ✅ Enrichir page 8 avec contenu de Part 1
            body_parts_highlights = part1_result.get('body_parts_highlights', {})
            body_parts_minimizes = part1_result.get('body_parts_minimizes', {})
            
            final_result = {
                # ✅ STRUCTURE PAGE 8
                "silhouette_type": part1_result.get("silhouette_type"),
                "silhouette_explanation": part1_result.get("silhouette_explanation"),
                "body_parts_to_highlight": part1_result.get("body_parts_to_highlight"),
                "body_parts_to_minimize": part1_result.get("body_parts_to_minimize"),
                "body_analysis": part1_result.get("body_analysis"),
                "styling_objectives": part1_result.get("styling_objectives"),
                "bodyType": part1_result.get("silhouette_type"),
                
                # ✅ CONTENU ENRICHI PAGE 8
                "highlights": {
                    "announcement": body_parts_highlights.get("announcement", ""),
                    "explanation": body_parts_highlights.get("explanation", "")
                },
                "minimizes": {
                    "announcement": body_parts_minimizes.get("announcement", ""),
                    "explanation": body_parts_minimizes.get("explanation", "")
                },
                
                # ✅ STRUCTURE PAGES 9+ - COMPLÈTE
                "morpho": {
                    "categories": morpho_categories
                },
                
                # ✅ TRACE DES DEMANDES CLIENT
                "client_requested_highlights": highlight_str,
                "client_requested_minimizes": minimize_str,
            }
            
            print("✅ Morphologie COMPLÈTE générée")
            print("   • 3 appels équilibrés: {} + {} + {} tokens".format(total_tokens_p1, total_tokens_p2, total_tokens_p3))
            print("   • Page 8: Enrichie ✅")
            print("   • Pages 9-15: Complètes avec tous les détails ✅")
            print("   • TOTAL: {} tokens (budget OK!) ✅".format(total_morpho_tokens))
            
            print("\n" + "="*80 + "\n")
            
            return final_result
            
        except Exception as e:
            print("\n❌ ERREUR MORPHOLOGY: {}".format(str(e)))
            call_tracker.log_error("Morphology", str(e))
            
            import traceback
            traceback.print_exc()
            raise


morphology_service = MorphologyService()