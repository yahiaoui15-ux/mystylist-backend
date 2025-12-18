"""
Morphology Service v5.2 - FINAL CORRIGÉE
✅ Accepte la vraie structure retournée par Part 1
✅ Génère highlights et minimizes EN INTERNE à partir de body_parts_to_highlight/minimize
✅ Fusionne avec onboarding morphology_goals
✅ Génère explanation et tips enrichis personnalisés
"""

import json
import re
from app.utils.openai_client import openai_client
from app.utils.openai_call_tracker import call_tracker
from app.prompts.morphology_part1_prompt import MORPHOLOGY_PART1_SYSTEM_PROMPT, MORPHOLOGY_PART1_USER_PROMPT
from app.prompts.morphology_part2_prompt import MORPHOLOGY_PART2_SYSTEM_PROMPT, MORPHOLOGY_PART2_USER_PROMPT


class MorphologyService:
    def __init__(self):
        self.openai = openai_client
    
    @staticmethod
    def safe_format(template: str, **kwargs) -> str:
        """Format un template en ignorant les clés manquantes"""
        try:
            return template.format(**kwargs)
        except KeyError as e:
            missing_key = str(e).strip("'")
            print(f"⚠️ KeyError lors du .format(): {missing_key}")
            
            format_dict = {
                "body_photo_url": kwargs.get("body_photo_url", ""),
                "shoulder_circumference": kwargs.get("shoulder_circumference", ""),
                "waist_circumference": kwargs.get("waist_circumference", ""),
                "hip_circumference": kwargs.get("hip_circumference", ""),
                "bust_circumference": kwargs.get("bust_circumference", ""),
                "silhouette_type": kwargs.get("silhouette_type", ""),
                "styling_objectives": kwargs.get("styling_objectives", ""),
            }
            
            try:
                result = template.format_map(format_dict)
                print(f"   ✅ format_map() réussi")
                return result
            except Exception as e2:
                print(f"   ❌ format_map() aussi échoué: {str(e2)}")
                return template
    
    @staticmethod
    def clean_json_string(content: str) -> str:
        """Nettoie une réponse JSON pour éviter les erreurs de parsing"""
        content = re.sub(r'^```json\s*', '', content)
        content = re.sub(r'\s*```$', '', content)
        content = content.replace('\x00', '')
        content = re.sub(r'\\([éèêëàâäùûüôöîïœæ])', r'\1', content)
        return content
    
    @staticmethod
    def merge_body_parts(onboarding_parts: list, openai_parts: list) -> list:
        """Fusionne les parties du corps en déduplicant"""
        if not openai_parts:
            openai_parts = []
        if not onboarding_parts:
            onboarding_parts = []
        
        onboarding_normalized = {part.lower().strip(): part for part in onboarding_parts}
        openai_normalized = {part.lower().strip(): part for part in openai_parts}
        
        merged = {}
        for norm, orig in onboarding_normalized.items():
            merged[norm] = orig
        for norm, orig in openai_normalized.items():
            if norm not in merged:
                merged[norm] = orig
        
        return list(merged.values())
    
    async def analyze(self, user_data: dict) -> dict:
        """Analyse morphologie EN 2 APPELS SÉQUENTIELS"""
        print("\n" + "="*80)
        print("💪 PHASE MORPHOLOGIE v5.2 (2 appels + génération highlights/minimizes)")
        print("="*80)
        
        body_photo_url = user_data.get("body_photo_url")
        if not body_photo_url:
            print("❌ Pas de photo du corps fournie")
            return {}
        
        # Récupérer les morphology_goals du onboarding
        print("\n📋 RÉCUPÉRATION MORPHOLOGY GOALS DU ONBOARDING")
        profile = user_data.get("profile", {})
        onboarding_data = profile.get("onboarding_data", {})
        morphology_goals = onboarding_data.get("morphology_goals", {})
        
        onboarding_highlight_parts = morphology_goals.get("body_parts_to_highlight", [])
        onboarding_minimize_parts = morphology_goals.get("body_parts_to_minimize", [])
        
        print(f"   • À valoriser (onboarding): {onboarding_highlight_parts}")
        print(f"   • À minimiser (onboarding): {onboarding_minimize_parts}")
        
        part1_result = {}
        part2_result = {}
        
        try:
            # ========================================================================
            # APPEL 1/2: MORPHOLOGY PART 1 - SILHOUETTE (VISION)
            # ========================================================================
            print("\n" + "█"*80)
            print("█ APPEL 1/2: MORPHOLOGY PART 1 - SILHOUETTE + BODY ANALYSIS (VISION)")
            print("█"*80)
            
            print("\n📋 AVANT APPEL:")
            print("   • Type: OpenAI Vision API (gpt-4-turbo)")
            print("   • Max tokens: 800")
            
            self.openai.set_context("Morphology Part 1", "PART 1: Silhouette")
            self.openai.set_system_prompt(MORPHOLOGY_PART1_SYSTEM_PROMPT)
            
            user_prompt_part1 = self.safe_format(
                MORPHOLOGY_PART1_USER_PROMPT,
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
                max_tokens=800
            )
            print("✅ RÉPONSE REÇUE")
            
            content_part1 = response_part1.get("content", "")
            
            print("\n📝 RÉPONSE BRUTE COMPLÈTE (Part 1) - {} chars:".format(len(content_part1)))
            print("="*80)
            print(content_part1[:1000] if len(content_part1) > 1000 else content_part1)
            print("="*80)
            
            # PARSING PART 1
            print("\n🔍 PARSING JSON PART 1:")
            content_part1_clean = self.clean_json_string(content_part1)
            
            try:
                part1_result = json.loads(content_part1_clean)
                print("   ✅ Parsing réussi!")
                print("      • Silhouette: {}".format(part1_result.get('silhouette_type', 'N/A')))
                
            except json.JSONDecodeError as e:
                print(f"   ❌ Erreur parsing JSON: {str(e)}")
                json_match = re.search(r'\{.*\}', content_part1_clean, re.DOTALL)
                if json_match:
                    try:
                        part1_result = json.loads(json_match.group())
                        print("   ✅ Extraction JSON réussie!")
                    except:
                        print("   ❌ Extraction aussi échouée")
                        part1_result = {}
                else:
                    part1_result = {}
            
            # ========================================================================
            # APPEL 2/2: MORPHOLOGY PART 2 - RECOMMANDATIONS (TEXT)
            # ========================================================================
            print("\n" + "█"*80)
            print("█ APPEL 2/2: MORPHOLOGY PART 2 - RECOMMANDATIONS STYLING (TEXT)")
            print("█"*80)
            
            if part1_result and part1_result.get("silhouette_type"):
                silhouette = part1_result.get("silhouette_type")
                styling_objectives = part1_result.get("styling_objectives", [])
            else:
                silhouette = "O"
                styling_objectives = ["Optimal"]
            
            objectives_str = ", ".join(styling_objectives) if styling_objectives else "Optimize"
            
            print("\n📋 AVANT APPEL:")
            print("   • Silhouette: {}".format(silhouette))
            
            self.openai.set_context("Morphology Part 2", "PART 2: Recommandations")
            self.openai.set_system_prompt(MORPHOLOGY_PART2_SYSTEM_PROMPT)
            
            user_prompt_part2 = self.safe_format(
                MORPHOLOGY_PART2_USER_PROMPT,
                silhouette_type=silhouette,
                styling_objectives=objectives_str
            )
            
            print("\n🤖 APPEL OPENAI EN COURS...")
            response_part2 = await self.openai.call_chat(
                prompt=user_prompt_part2,
                model="gpt-4-turbo",
                max_tokens=800
            )
            print("✅ RÉPONSE REÇUE")
            
            content_part2 = response_part2.get("content", "")
            
            print("\n📝 RÉPONSE BRUTE COMPLÈTE (Part 2) - {} chars:".format(len(content_part2)))
            print("="*80)
            print(content_part2[:1000] if len(content_part2) > 1000 else content_part2)
            print("="*80)
            
            # PARSING PART 2
            print("\n🔍 PARSING JSON PART 2:")
            content_part2_clean = self.clean_json_string(content_part2)
            
            try:
                part2_result = json.loads(content_part2_clean)
                print("   ✅ Parsing réussi!")
                
            except json.JSONDecodeError as e:
                print(f"   ❌ Erreur parsing JSON: {str(e)}")
                json_match = re.search(r'\{.*\}', content_part2_clean, re.DOTALL)
                if json_match:
                    try:
                        part2_result = json.loads(json_match.group())
                        print("   ✅ Extraction JSON réussie!")
                    except:
                        print("   ❌ Extraction aussi échouée")
                        part2_result = {}
                else:
                    part2_result = {}
            
            # ========================================================================
            # FUSION ONBOARDING + OPENAI + GÉNÉRATION HIGHLIGHTS/MINIMIZES
            # ========================================================================
            print("\n" + "="*80)
            print("🔗 FUSION ONBOARDING + OPENAI")
            print("="*80)
            
            # Part 1 retourne body_parts_to_highlight/minimize (listes simples)
            openai_highlight_parts = part1_result.get("body_parts_to_highlight", [])
            openai_minimize_parts = part1_result.get("body_parts_to_minimize", [])
            
            print("\n   OpenAI recommande:")
            print(f"   • À valoriser: {openai_highlight_parts}")
            print(f"   • À minimiser: {openai_minimize_parts}")
            
            # Fusionner les parties (déduplication)
            merged_highlight_parts = self.merge_body_parts(
                onboarding_highlight_parts,
                openai_highlight_parts
            )
            merged_minimize_parts = self.merge_body_parts(
                onboarding_minimize_parts,
                openai_minimize_parts
            )
            
            print("\n   Après fusion (union unique):")
            print(f"   • À valoriser: {merged_highlight_parts}")
            print(f"   • À minimiser: {merged_minimize_parts}")
            
            # Extraire silhouette_explanation comme explanation personnalisée
            silhouette_explanation = part1_result.get("silhouette_explanation", "")
            
            # Construire les données finales pour Page 8
            highlights_data = self._format_highlights_for_page8(
                parties=merged_highlight_parts,
                silhouette_explanation=silhouette_explanation,
                onboarding_parties=onboarding_highlight_parts,
                openai_parties=openai_highlight_parts
            )
            
            minimizes_data = self._format_minimizes_for_page8(
                parties=merged_minimize_parts,
                silhouette_explanation=silhouette_explanation,
                onboarding_parties=onboarding_minimize_parts,
                openai_parties=openai_minimize_parts
            )
            
            print("\n✅ Highlights générés:")
            print(f"   • Parties: {merged_highlight_parts}")
            
            print("\n✅ Minimizes générés:")
            print(f"   • Parties: {merged_minimize_parts}")
            
            # ========================================================================
            # RÉSULTAT FINAL
            # ========================================================================
            print("\n" + "="*80)
            print("📦 RÉSULTAT FINAL")
            print("="*80)
            
            final_result = {
                "silhouette_type": part1_result.get("silhouette_type"),
                "silhouette_explanation": part1_result.get("silhouette_explanation"),
                "body_parts_to_highlight": part1_result.get("body_parts_to_highlight", []),
                "body_parts_to_minimize": part1_result.get("body_parts_to_minimize", []),
                "body_analysis": part1_result.get("body_analysis"),
                "styling_objectives": part1_result.get("styling_objectives", []),
                "bodyType": part1_result.get("silhouette_type"),
                "recommendations": part2_result.get("recommendations", {}),
                
                # ✨ DONNÉES POUR PAGE 8 (GÉNÉRÉES EN INTERNE)
                "highlights": highlights_data,
                "minimizes": minimizes_data,
            }
            
            print("✅ Morphologie v5.2 générée avec succès!")
            print("\n" + "="*80 + "\n")
            
            return final_result
            
        except Exception as e:
            print(f"\n❌ EXCEPTION: {str(e)}")
            call_tracker.log_error("Morphology", str(e))
            
            import traceback
            traceback.print_exc()
            
            return {
                "silhouette_type": part1_result.get("silhouette_type"),
                "silhouette_explanation": part1_result.get("silhouette_explanation"),
                "body_parts_to_highlight": part1_result.get("body_parts_to_highlight", []),
                "body_parts_to_minimize": part1_result.get("body_parts_to_minimize", []),
                "body_analysis": part1_result.get("body_analysis"),
                "styling_objectives": part1_result.get("styling_objectives", []),
                "bodyType": part1_result.get("silhouette_type"),
                "recommendations": part2_result.get("recommendations", {}),
            }
    
    def _format_highlights_for_page8(self, parties: list, silhouette_explanation: str,
                                     onboarding_parties: list, openai_parties: list) -> dict:
        """
        Génère les highlights pour Page 8
        Utilise silhouette_explanation comme base pour l'explanation
        """
        announcement = ", ".join(parties) if parties else "Votre silhouette"
        
        # L'explanation de base vient de silhouette_explanation
        explanation = silhouette_explanation
        
        # Enrichir avec les sources
        if onboarding_parties and openai_parties:
            explanation += f"\n\nCette analyse combine vos préférences (vous aviez sélectionné: {', '.join(onboarding_parties)}) avec nos recommandations morphologiques (nous suggérons: {', '.join(openai_parties)})."
        elif onboarding_parties:
            explanation += f"\n\nVous aviez sélectionné ces parties à valoriser: {', '.join(onboarding_parties)}."
        elif openai_parties:
            explanation += f"\n\nNous recommandons de valoriser: {', '.join(openai_parties)}."
        
        full_text = f"""ANNONCE: {announcement}

EXPLICATION: {explanation}"""
        
        return {
            "announcement": announcement,
            "explanation": explanation,
            "full_text": full_text
        }
    
    def _format_minimizes_for_page8(self, parties: list, silhouette_explanation: str,
                                   onboarding_parties: list, openai_parties: list) -> dict:
        """
        Génère les minimizes pour Page 8
        """
        announcement = ", ".join(parties) if parties else "Votre silhouette"
        
        explanation = silhouette_explanation
        
        if onboarding_parties and openai_parties:
            explanation += f"\n\nCette analyse combine vos préférences (vous aviez sélectionné: {', '.join(onboarding_parties)}) avec nos recommandations morphologiques (nous suggérons: {', '.join(openai_parties)})."
        elif onboarding_parties:
            explanation += f"\n\nVous aviez sélectionné ces parties à harmoniser: {', '.join(onboarding_parties)}."
        elif openai_parties:
            explanation += f"\n\nNous recommandons d'harmoniser: {', '.join(openai_parties)}."
        
        full_text = f"""ANNONCE: {announcement}

EXPLICATION: {explanation}"""
        
        return {
            "announcement": announcement,
            "explanation": explanation,
            "full_text": full_text
        }


morphology_service = MorphologyService()