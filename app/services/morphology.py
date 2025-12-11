"""
Morphology Service v4.1 - Logs DÉTAILLÉS + DÉCORRÉLÉS (Part 1 vs Part 2)
✅ Format identique à colorimetry
✅ Affiche contenu brut, tokens breakdown, parsing résultats complets
"""

import json
from app.utils.openai_client import openai_client
from app.utils.openai_call_tracker import call_tracker
from app.prompts.morphology_part1_prompt import MORPHOLOGY_PART1_SYSTEM_PROMPT, MORPHOLOGY_PART1_USER_PROMPT
from app.prompts.morphology_part2_prompt import MORPHOLOGY_PART2_SYSTEM_PROMPT, MORPHOLOGY_PART2_USER_PROMPT


class MorphologyService:
    def __init__(self):
        self.openai = openai_client
    
    async def analyze(self, user_data: dict) -> dict:
        """Analyse morphologie EN 2 APPELS SÉQUENTIELS - LOGS COMPLETS"""
        print("\n" + "="*80)
        print("💪 PHASE MORPHOLOGIE (2 appels)")
        print("="*80)
        
        try:
            body_photo_url = user_data.get("body_photo_url")
            if not body_photo_url:
                print("❌ Pas de photo du corps fournie")
                return {}
            
            # ========================================================================
            # APPEL 1/2: MORPHOLOGY PART 1 - SILHOUETTE + BODY ANALYSIS (VISION)
            # ========================================================================
            print("\n" + "█"*80)
            print("█ APPEL 1/2: MORPHOLOGY PART 1 - SILHOUETTE + BODY ANALYSIS")
            print("█"*80)
            
            print("\n📍 AVANT APPEL:")
            print(f"   • Type: OpenAI Vision API (gpt-4-turbo)")
            print(f"   • Max tokens: 800")
            print(f"   • Image: {body_photo_url[:60]}...")
            print(f"   • Mensurations:")
            print(f"      - Épaules: {user_data.get('shoulder_circumference')} cm")
            print(f"      - Taille: {user_data.get('waist_circumference')} cm")
            print(f"      - Hanches: {user_data.get('hip_circumference')} cm")
            print(f"      - Buste: {user_data.get('bust_circumference')} cm")
            
            self.openai.set_context("Morphology Part 1", "PART 1: Silhouette + Body Analysis")
            self.openai.set_system_prompt(MORPHOLOGY_PART1_SYSTEM_PROMPT)
            
            user_prompt_part1 = MORPHOLOGY_PART1_USER_PROMPT.format(
                body_photo_url=body_photo_url,
                shoulder_circumference=user_data.get("shoulder_circumference", 0),
                waist_circumference=user_data.get("waist_circumference", 0),
                hip_circumference=user_data.get("hip_circumference", 0),
                bust_circumference=user_data.get("bust_circumference", 0)
            )
            
            print(f"\n🤖 APPEL OPENAI EN COURS...")
            response_part1 = await self.openai.analyze_image(
                image_urls=[body_photo_url],
                prompt=user_prompt_part1,
                model="gpt-4-turbo",
                max_tokens=800
            )
            print(f"✅ RÉPONSE REÇUE")
            
            content_part1 = response_part1.get("content", "")
            prompt_tokens_p1 = response_part1.get("prompt_tokens", 0)
            completion_tokens_p1 = response_part1.get("completion_tokens", 0)
            total_tokens_p1 = response_part1.get("total_tokens", 0)
            budget_percent_p1 = (total_tokens_p1 / 4000) * 100
            
            print(f"\n🔍 RÉPONSE BRUTE (premiers 400 chars):")
            print(f"   {content_part1[:400]}")
            if len(content_part1) > 400:
                print(f"   ... [{len(content_part1) - 400} chars supplémentaires]")
            
            print(f"\n📊 TOKENS CONSOMMÉS PART 1:")
            print(f"   • Prompt: {prompt_tokens_p1}")
            print(f"   • Completion: {completion_tokens_p1}")
            print(f"   • Total: {total_tokens_p1}")
            print(f"   • Budget: {budget_percent_p1:.1f}% (vs 4000 max)")
            print(f"   • Status: {'✅ OK' if budget_percent_p1 < 100 else '⚠️ Approche limite' if budget_percent_p1 < 125 else '❌ DÉPASSEMENT!'}")
            
            # PARSING PART 1
            print(f"\n📋 PARSING JSON PART 1:")
            response_text = content_part1.strip() if content_part1 else ""
            
            if not response_text:
                print(f"   ❌ Réponse vide")
                return {}
            
            json_start = response_text.find('{')
            if json_start == -1:
                print(f"   ❌ Pas de JSON trouvé")
                print(f"   Contenu: {response_text[:200]}")
                return {}
            
            response_text = response_text[json_start:]
            json_end = response_text.rfind('}')
            if json_end == -1:
                print(f"   ❌ JSON incomplet (accolade fermante manquante)")
                return {}
            
            response_text = response_text[:json_end+1]
            
            try:
                part1_result = json.loads(response_text)
                print(f"   ✅ Succès")
                
                silhouette = part1_result.get('silhouette_type', 'Unknown')
                objectives = len(part1_result.get('styling_objectives', []))
                highlights = len(part1_result.get('body_parts_to_highlight', []))
                minimizes = len(part1_result.get('body_parts_to_minimize', []))
                
                print(f"      • Silhouette: {silhouette}")
                print(f"      • Objectifs de styling: {objectives}")
                print(f"      • Parties à valoriser: {highlights}")
                print(f"      • Parties à harmoniser: {minimizes}")
                
                print(f"\n📦 RÉSULTAT PART 1 COMPLET:")
                print(f"   {json.dumps(part1_result, ensure_ascii=False, indent=2)[:500]}...")
                
            except json.JSONDecodeError as e:
                print(f"   ❌ Erreur parsing JSON: {e}")
                print(f"   JSON invalide: {response_text[:300]}...")
                
                # Tentative correction
                if response_text.count('{') > response_text.count('}'):
                    print(f"   🔧 Tentative correction (ajout }) ...")
                    response_text += '}'
                    try:
                        part1_result = json.loads(response_text)
                        print(f"   ✅ Succès après correction")
                    except:
                        print(f"   ❌ Correction échouée")
                        return {}
                else:
                    print(f"   Impossible de corriger")
                    return {}
            
            # ========================================================================
            # APPEL 2/2: MORPHOLOGY PART 2 - RECOMMANDATIONS STYLING (TEXT)
            # ========================================================================
            print("\n" + "█"*80)
            print("█ APPEL 2/2: MORPHOLOGY PART 2 - RECOMMANDATIONS STYLING")
            print("█"*80)
            
            styling_objectives = part1_result.get("styling_objectives", [])
            objectives_str = ", ".join(styling_objectives)
            
            print(f"\n📍 AVANT APPEL:")
            print(f"   • Type: OpenAI Text API (gpt-4-turbo)")
            print(f"   • Max tokens: 800")
            print(f"   • Silhouette reçue: {silhouette}")
            print(f"   • Objectifs reçus: {objectives_str}")
            
            self.openai.set_context("Morphology Part 2", "PART 2: Recommandations Styling")
            self.openai.set_system_prompt(MORPHOLOGY_PART2_SYSTEM_PROMPT)
            
            user_prompt_part2 = MORPHOLOGY_PART2_USER_PROMPT.format(
                silhouette_type=silhouette,
                styling_objectives=objectives_str
            )
            
            print(f"\n🤖 APPEL OPENAI EN COURS...")
            response_part2 = await self.openai.call_gpt4(
                prompt=user_prompt_part2,
                max_tokens=800
            )
            print(f"✅ RÉPONSE REÇUE")
            
            content_part2 = response_part2.get("content", "")
            prompt_tokens_p2 = response_part2.get("prompt_tokens", 0)
            completion_tokens_p2 = response_part2.get("completion_tokens", 0)
            total_tokens_p2 = response_part2.get("total_tokens", 0)
            budget_percent_p2 = (total_tokens_p2 / 4000) * 100
            
            print(f"\n🔍 RÉPONSE BRUTE (premiers 400 chars):")
            print(f"   {content_part2[:400]}")
            if len(content_part2) > 400:
                print(f"   ... [{len(content_part2) - 400} chars supplémentaires]")
            
            print(f"\n📊 TOKENS CONSOMMÉS PART 2:")
            print(f"   • Prompt: {prompt_tokens_p2}")
            print(f"   • Completion: {completion_tokens_p2}")
            print(f"   • Total: {total_tokens_p2}")
            print(f"   • Budget: {budget_percent_p2:.1f}% (vs 4000 max)")
            print(f"   • Status: {'✅ OK' if budget_percent_p2 < 100 else '⚠️ Approche limite' if budget_percent_p2 < 125 else '❌ DÉPASSEMENT!'}")
            
            total_morpho_tokens = total_tokens_p1 + total_tokens_p2
            total_morpho_percent = (total_morpho_tokens / 4000) * 100
            print(f"\n📊 TOTAL MORPHOLOGIE (Part 1 + Part 2):")
            print(f"   • Part 1: {total_tokens_p1} tokens")
            print(f"   • Part 2: {total_tokens_p2} tokens")
            print(f"   • Total: {total_morpho_tokens} tokens")
            print(f"   • Budget: {total_morpho_percent:.1f}% (vs 4000 max)")
            print(f"   • Status: {'✅ OK' if total_morpho_percent < 100 else '⚠️ Approche limite' if total_morpho_percent < 125 else '❌ DÉPASSEMENT!'}")
            
            # PARSING PART 2
            print(f"\n📋 PARSING JSON PART 2:")
            response_text = content_part2.strip() if content_part2 else ""
            
            if not response_text:
                print(f"   ❌ Réponse vide")
                return {}
            
            json_start = response_text.find('{')
            if json_start == -1:
                print(f"   ❌ Pas de JSON trouvé")
                print(f"   Contenu: {response_text[:200]}")
                return {}
            
            response_text = response_text[json_start:]
            json_end = response_text.rfind('}')
            if json_end == -1:
                print(f"   ❌ JSON incomplet (accolade fermante manquante)")
                return {}
            
            response_text = response_text[:json_end+1]
            
            try:
                part2_result = json.loads(response_text)
                print(f"   ✅ Succès")
                
                recommendations = part2_result.get('recommendations', {})
                categories = len(recommendations)
                
                print(f"      • Catégories: {categories}")
                for cat in recommendations.keys():
                    a_priv = len(recommendations.get(cat, {}).get('a_privilegier', []))
                    a_eviter = len(recommendations.get(cat, {}).get('a_eviter', []))
                    print(f"      • {cat}: {a_priv} à privilégier, {a_eviter} à éviter")
                
                print(f"\n📦 RÉSULTAT PART 2 COMPLET (premiers 600 chars):")
                print(f"   {json.dumps(part2_result, ensure_ascii=False, indent=2)[:600]}...")
                
            except json.JSONDecodeError as e:
                print(f"   ❌ Erreur parsing JSON: {e}")
                print(f"   JSON invalide: {response_text[:300]}...")
                
                # Tentative correction
                if response_text.count('{') > response_text.count('}'):
                    print(f"   🔧 Tentative correction (ajout }) ...")
                    response_text += '}'
                    try:
                        part2_result = json.loads(response_text)
                        print(f"   ✅ Succès après correction")
                    except:
                        print(f"   ❌ Correction échouée")
                        return {}
                else:
                    print(f"   Impossible de corriger")
                    return {}
            
            # ========================================================================
            # FUSION PART 1 + PART 2
            # ========================================================================
            print("\n" + "="*80)
            print("📦 FUSION PART 1 + PART 2")
            print("="*80)
            
            final_result = {
                "silhouette_type": part1_result.get("silhouette_type"),
                "silhouette_explanation": part1_result.get("silhouette_explanation"),
                "body_parts_to_highlight": part1_result.get("body_parts_to_highlight"),
                "body_parts_to_minimize": part1_result.get("body_parts_to_minimize"),
                "body_analysis": part1_result.get("body_analysis"),
                "styling_objectives": part1_result.get("styling_objectives"),
                "bodyType": part1_result.get("silhouette_type"),  # Pour report_generator
                "recommendations": part2_result.get("recommendations", {})
            }
            
            print(f"✅ Morphologie complète générée")
            print(f"   • Silhouette: {final_result['silhouette_type']}")
            print(f"   • Recommandations catégories: {len(final_result['recommendations'])}")
            print(f"   • Champs total: {len(final_result)}")
            
            print("\n" + "="*80 + "\n")
            
            return final_result
            
        except Exception as e:
            print(f"\n❌ ERREUR MORPHOLOGY: {e}")
            call_tracker.log_error("Morphology", str(e))
            
            import traceback
            traceback.print_exc()
            raise


morphology_service = MorphologyService()