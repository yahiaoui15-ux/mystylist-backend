"""
Morphology Service v5.2 - FINAL CORRIGÉ
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
from app.prompts.morphology_part3_prompt import MORPHOLOGY_PART3_SYSTEM_PROMPT, MORPHOLOGY_PART3_USER_PROMPT


class MorphologyService:
    def __init__(self):
        self.openai = openai_client
    
    @staticmethod
    def safe_format(template: str, **kwargs) -> str:
        """Format un template en ignorant les clés manquantes - ULTRA ROBUSTE"""
        # Utiliser une classe defaultdict pour retourner vide string pour ANY missing key
        class SafeDict(dict):
            def __missing__(self, key):
                return ""  # Retourner "" pour toute clé manquante au lieu de lever KeyError
        
        safe_dict = SafeDict(kwargs)
        try:
            return template.format_map(safe_dict)
        except Exception as e:
            print(f"⚠️ Erreur format_map: {str(e)}")
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
                max_tokens=2500  # ✅ Augmenté de 800 → 2000 pour éviter la troncature
            )
            print("✅ RÉPONSE REÇUE")
            
            content_part2 = response_part2.get("content", "")
            
            print("\n📝 RÉPONSE BRUTE COMPLÈTE (Part 2) - {} chars:".format(len(content_part2)))
            print("="*80)
            print(content_part2[:1000] if len(content_part2) > 1000 else content_part2)
            print("="*80)
            
            # PARSING PART 2 - ULTRA-ROBUSTE
            print("\n🔍 PARSING JSON PART 2:")
            content_part2_clean = self.clean_json_string(content_part2)
            
            try:
                part2_result = json.loads(content_part2_clean)
                print("   ✅ Parsing réussi!")
                
            except json.JSONDecodeError:
                print("   ⚠️ JSON invalide → tentative correction OpenAI")

                try:
                    part2_result = await self.force_valid_json(
                        content_part2_clean,
                        context="Morphology Part 2"
                    )
                    print("   ✅ JSON corrigé par OpenAI")

                except Exception:
                    print("   ❌ Correction échouée → fallback")
                    part2_result = self._generate_default_recommendations(silhouette)


            # ========================================================================
            # MORPHOLOGY PART 3 - DÉTAILS DE STYLING (MATIERES + MOTIFS + PIÈGES)
            # ========================================================================
            print("\n" + "="*80)
            print("🔍 MORPHOLOGIE PART 3 - DÉTAILS DE STYLING")
            print("="*80)

            print("\n📋 AVANT APPEL:")
            print("   • Silhouette: {}".format(silhouette))
            print("   • Type: OpenAI Chat API")
            print("   • Max tokens: 1800")

            self.openai.set_context("Morphology Part 3", "PART 3: Détails Styling")
            self.openai.set_system_prompt(MORPHOLOGY_PART3_SYSTEM_PROMPT)

            # Préparer le user prompt Part 3
            styling_objectives_str = ", ".join(styling_objectives) if styling_objectives else "Optimal"
            body_parts_highlight = part1_result.get("body_parts_to_highlight", [])
            body_parts_minimize = part1_result.get("body_parts_to_minimize", [])

            highlight_str = ", ".join(body_parts_highlight) if body_parts_highlight else "Général"
            minimize_str = ", ".join(body_parts_minimize) if body_parts_minimize else "Général"

            user_prompt_part3 = self.safe_format(
                MORPHOLOGY_PART3_USER_PROMPT,
                silhouette_type=silhouette,
                styling_objectives=styling_objectives_str,
                body_parts_to_highlight=highlight_str,
                body_parts_to_minimize=minimize_str
            )

            print("\n🤖 APPEL OPENAI EN COURS...")
            response_part3 = await self.openai.call_chat(
                prompt=user_prompt_part3,
                model="gpt-4-turbo",
                max_tokens=2500  # ✅ Pour générer les 7 pièges
            )
            print("✅ RÉPONSE REÇUE")

            content_part3 = response_part3.get("content", "")

            print("\n📝 RÉPONSE BRUTE COMPLÈTE (Part 3) - {} chars:".format(len(content_part3)))
            print("="*80)
            print(content_part3[:1000] if len(content_part3) > 1000 else content_part3)
            print("="*80)

            # PARSING PART 3
            print("\n🔍 PARSING JSON PART 3:")
            content_part3_clean = self.clean_json_string(content_part3)

            try:
                part3_result = json.loads(content_part3_clean)
                print("   ✅ Parsing réussi!")
                details = part3_result.get("details", {})
                print("      • Catégories trouvées: {}".format(list(details.keys())))
                
            except json.JSONDecodeError:
                print("   ⚠️ JSON invalide → tentative correction OpenAI")

                try:
                    part3_result = await self.force_valid_json(
                        content_part3_clean,
                        context="Morphology Part 3"
                    )
                    print("   ✅ JSON corrigé par OpenAI")

                except Exception:
                    print("   ❌ Correction échouée → fallback")
                    part3_result = {"details": {}}

                # ============================
                # NORMALISATION PART 3 (ANTI-VIDE)
                # ============================
                expected_cats = ["hauts", "bas", "robes", "vestes", "maillot_lingerie", "chaussures", "accessoires"]

                # Cas 1: le modèle a renvoyé directement les catégories à la racine (au lieu de details)
                if isinstance(part3_result, dict) and "details" not in part3_result:
                    if any(k in part3_result for k in expected_cats):
                        part3_result = {"details": {k: part3_result.get(k, {}) for k in expected_cats}}

                    # Cas 2: le modèle a renvoyé un bloc générique (matieres/motifs/pieges) à la racine
                    elif any(k in part3_result for k in ["matieres", "motifs", "pieges"]):
                        generic_block = {
                            "matieres": part3_result.get("matieres", []),
                            "motifs": part3_result.get("motifs", {}),
                            "pieges": part3_result.get("pieges", [])
                        }
                        part3_result = {"details": {k: generic_block for k in expected_cats}}

                # Sécuriser la présence des clés attendues dans chaque catégorie
                if not isinstance(part3_result, dict):
                    part3_result = {"details": {}}

                if "details" not in part3_result or not isinstance(part3_result["details"], dict):
                    part3_result["details"] = {}

                for cat in expected_cats:
                    if cat not in part3_result["details"] or not isinstance(part3_result["details"][cat], dict):
                        part3_result["details"][cat] = {}
                    part3_result["details"][cat].setdefault("matieres", [])
                    part3_result["details"][cat].setdefault("motifs", {"recommandes": [], "a_eviter": []})
                    part3_result["details"][cat].setdefault("pieges", [])

                
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
            
            # VÉRIFIER SI OPENAI A DÉJÀ RETOURNÉ highlights et minimizes
            print("\n✅ VÉRIFICATION: OpenAI a-t-il fourni highlights/minimizes ?")
            openai_highlights = part1_result.get("highlights", {})
            openai_minimizes = part1_result.get("minimizes", {})
            
            has_openai_highlights = bool(openai_highlights and openai_highlights.get("announcement"))
            has_openai_minimizes = bool(openai_minimizes and openai_minimizes.get("announcement"))
            
            print(f"   • OpenAI highlights fournis: {has_openai_highlights}")
            print(f"   • OpenAI minimizes fournis: {has_openai_minimizes}")
            
            # Construire les données finales pour Page 8
            if has_openai_highlights:
                # Utiliser les données d'OpenAI directement (AVEC TIPS !)
                print("   → Utilisation des données OpenAI pour highlights")
                tips_text = ""
                if openai_highlights.get("tips"):
                    tips_text = "\n\nASPECTS À VALORISER (conseils):\n" + "\n".join([f"• {tip}" for tip in openai_highlights.get("tips", [])])
                
                highlights_data = {
                    "announcement": openai_highlights.get("announcement", ""),
                    "explanation": openai_highlights.get("explanation", ""),
                    "tips": openai_highlights.get("tips", []),
                    "full_text": f"ANNONCE: {openai_highlights.get('announcement', '')}\n\nEXPLICATION: {openai_highlights.get('explanation', '')}{tips_text}"
                }
            else:
                # Générer en interne (fallback)
                print("   → Génération interne des données pour highlights")
                highlights_data = self._format_highlights_for_page8(
                    parties=merged_highlight_parts,
                    silhouette_explanation=silhouette_explanation,
                    onboarding_parties=onboarding_highlight_parts,
                    openai_parties=openai_highlight_parts
                )
            
            if has_openai_minimizes:
                # Utiliser les données d'OpenAI directement (AVEC TIPS !)
                print("   → Utilisation des données OpenAI pour minimizes")
                tips_text = ""
                if openai_minimizes.get("tips"):
                    tips_text = "\n\nASPECTS À MINIMISER (conseils):\n" + "\n".join([f"• {tip}" for tip in openai_minimizes.get("tips", [])])
                
                minimizes_data = {
                    "announcement": openai_minimizes.get("announcement", ""),
                    "explanation": openai_minimizes.get("explanation", ""),
                    "tips": openai_minimizes.get("tips", []),
                    "full_text": f"ANNONCE: {openai_minimizes.get('announcement', '')}\n\nEXPLICATION: {openai_minimizes.get('explanation', '')}{tips_text}"
                }
            else:
                # Générer en interne (fallback)
                print("   → Génération interne des données pour minimizes")
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
            # FUSION PART 2 + PART 3 (Ajouter les matieres, motifs, pieges)
            # ========================================================================
            print("\n" + "="*80)
            print("🔗 FUSION PART 2 + PART 3")
            print("="*80)

            recommendations_part2 = part2_result.get("recommendations", {})
            details_part3 = part3_result.get("details", {})

            # Fusionner les deux pour chaque catégorie
            merged_recommendations = {}
            for category in ["hauts", "bas", "robes", "vestes", "maillot_lingerie", "chaussures", "accessoires"]:
                part2_cat = recommendations_part2.get(category, {})
                part3_cat = details_part3.get(category, {})
                
                merged = {
                    "introduction": part2_cat.get("introduction", ""),
                    "recommandes": part2_cat.get("recommandes", []),
                    "a_eviter": part2_cat.get("pieces_a_eviter", part2_cat.get("a_eviter", [])),
                    "matieres": part3_cat.get("matieres", part2_cat.get("matieres", "")),
                    "motifs": part3_cat.get("motifs", part2_cat.get("motifs", {})),
                    "pieges": part3_cat.get("pieges", []),  # ✅ Des Part 3!
                    "visuels": []
                }
                
                # ======================================================
                # FALLBACK ANTI-SECTIONS VIDES (MORPHOLOGY)
                # ======================================================

                if not merged["recommandes"]:
                    merged["recommandes"] = [
                        {
                            "cut_display": "Coupe adaptée à votre silhouette",
                            "why": "Cette coupe permet d’équilibrer les volumes et de valoriser votre morphologie."
                        }
                    ]

                if not merged["a_eviter"]:
                    merged["a_eviter"] = [
                        {
                            "cut_display": "Coupe non structurée",
                            "why": "Elle risque de déséquilibrer visuellement la silhouette."
                        }
                    ]

                if not merged["pieges"]:
                    merged["pieges"] = [
                        "Éviter les volumes excessifs qui cassent l’équilibre naturel de la silhouette."
                    ]

                # ======================================================
                # FORMATAGE TEXTE LISIBLE - MATIERES & MOTIFS (PATCH A)
                # ======================================================

                # MATIERES
                matieres = merged.get("matieres", "")
                if isinstance(matieres, list):
                    merged["matieres"] = "• " + "\n• ".join(matieres)
                elif isinstance(matieres, str) and matieres.strip():
                    merged["matieres"] = matieres.strip()
                else:
                    merged["matieres"] = "• Matières adaptées à votre silhouette."

                # MOTIFS (NORMALISATION - NE PAS CONVERTIR EN STRING)
                motifs = merged.get("motifs", {})

                # Cas 1 : format dict attendu
                if isinstance(motifs, dict):
                    rec = motifs.get("recommandes", []) or []
                    avoid = motifs.get("a_eviter", []) or []

                # Cas 2 : format liste → on l'interprète comme "recommandes"
                elif isinstance(motifs, list):
                    rec = motifs
                    avoid = []

                # Cas 3 : format inattendu
                else:
                    rec = []
                    avoid = []

                # Toujours normaliser en dict pour le template PDF
                merged["motifs"] = {
                    "recommandes": rec,
                    "a_eviter": avoid
                }

                # ======================================================
                # PATCH B — FALLBACK MOTIFS & DÉTAILS PAR CATÉGORIE
                # (uniquement si vide)
                # ======================================================
                if not merged["motifs"]["recommandes"] and not merged["motifs"]["a_eviter"]:
                    fallback_motifs = {
                        "hauts": {
                            "recommandes": ["détails verticaux", "rayures fines", "encolures structurées", "petits imprimés centrés"],
                            "a_eviter": ["rayures horizontales larges", "motifs très imposants", "imprimés sur zones à minimiser"]
                        },
                        "bas": {
                            "recommandes": ["motifs discrets", "couleurs unies", "imprimés diffus"],
                            "a_eviter": ["gros motifs sur les hanches", "contrastes forts", "imprimés trop chargés"]
                        },
                        "robes": {
                            "recommandes": ["motifs verticaux", "imprimés fluides", "détails centrés sur la taille"],
                            "a_eviter": ["motifs horizontaux", "imprimés massifs", "ruptures visuelles à la taille"]
                        },
                        "vestes": {
                            "recommandes": ["structures nettes", "lignes verticales", "détails au niveau des épaules"],
                            "a_eviter": ["poches trop larges", "détails sur les hanches", "formes informes"]
                        },
                        "maillot_lingerie": {
                            "recommandes": ["détails structurants", "matières gainantes", "jeux de découpes équilibrés"],
                            "a_eviter": ["motifs trop contrastés", "détails mal placés", "volumes excessifs"]
                        },
                        "chaussures": {
                            "recommandes": ["formes épurées", "lignes allongeantes", "détails discrets"],
                            "a_eviter": ["brides épaisses", "contrastes trop marqués", "formes trop massives"]
                        },
                        "accessoires": {
                            "recommandes": ["accessoires proportionnés", "lignes cohérentes avec la silhouette", "détails verticaux"],
                            "a_eviter": ["accessoires surdimensionnés", "accumulation excessive", "ruptures visuelles fortes"]
                        }
                    }

                    cat_fallback = fallback_motifs.get(category, {"recommandes": [], "a_eviter": []})
                    merged["motifs"] = {
                        "recommandes": cat_fallback.get("recommandes", []),
                        "a_eviter": cat_fallback.get("a_eviter", [])
                    }

                # ===========================
                # AJOUT DANS LA BOUCLE DE FUSION
                # juste AVANT merged_recommendations[category] = merged
                # ===========================

                # ======================================================
                # PATCH A — FORMATAGE MOTIFS EN BULLETS (LECTURE PDF)
                # ======================================================

                motifs = merged.get("motifs", {})

                motifs_lines = []

                if isinstance(motifs, dict):
                    rec = motifs.get("recommandes", []) or []
                    avoid = motifs.get("a_eviter", []) or []

                    if rec:
                        motifs_lines.append("• À privilégier :")
                        motifs_lines.extend([f"  – {m}" for m in rec])

                    if avoid:
                        motifs_lines.append("• À éviter :")
                        motifs_lines.extend([f"  – {m}" for m in avoid])

                merged["motifs"] = "\n".join(motifs_lines) if motifs_lines else "• Motifs adaptés à votre morphologie."

                # ======================================================
                # PATCH B — DENSIFICATION RECOMMANDATIONS / A ÉVITER
                # ======================================================

                def enrich_list(items, category, mode):
                    fallback = {
                        "hauts": {
                            "recommandes": [
                                {"cut_display": "Haut structuré", "why": "Structure le haut du corps"},
                                {"cut_display": "Détails verticaux", "why": "Allonge visuellement la silhouette"},
                            ],
                            "a_eviter": [
                                {"cut_display": "Haut trop ample", "why": "Alourdit la carrure"},
                            ],
                        },
                        "robes": {
                            "recommandes": [
                                {"cut_display": "Robe fluide structurée", "why": "Suit les lignes naturelles"},
                                {"cut_display": "Taille marquée", "why": "Rééquilibre les volumes"},
                            ],
                            "a_eviter": [
                                {"cut_display": "Robe droite rigide", "why": "Efface la silhouette"},
                            ],
                        },
                        "vestes": {
                            "recommandes": [
                                {"cut_display": "Veste cintrée", "why": "Structure le buste"},
                                {"cut_display": "Épaule définie", "why": "Renforce l’équilibre visuel"},
                            ],
                            "a_eviter": [
                                {"cut_display": "Veste informe", "why": "Manque de structure"},
                            ],
                        },
                    }

                    if len(items) >= 4:
                        return items

                    extra = fallback.get(category, {}).get(mode, [])
                    return items + extra[: max(0, 4 - len(items))]


                merged["recommandes"] = enrich_list(
                    merged["recommandes"], category, "recommandes"
                )

                merged["a_eviter"] = enrich_list(
                    merged["a_eviter"], category, "a_eviter"
                )

                merged_recommendations[category] = merged
                pieges_count = len(merged.get('pieges', []))
                print(f"   • {category}: {pieges_count} pièges")

            print("   ✅ Fusion complétée!")
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
                "recommendations": merged_recommendations,  # ✅ Avec Part 2 + Part 3!
                
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
                "recommendations": merged_recommendations,  # ✅ Avec Part 2 + Part 3!
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
        Utilise silhouette_explanation comme base pour l'explanation
        """
        announcement = ", ".join(parties) if parties else "Votre silhouette"

        # Base explanation
        explanation = silhouette_explanation or "Certaines zones peuvent être visuellement atténuées par des coupes et volumes mieux placés."

        # Enrichir avec les sources
        if onboarding_parties and openai_parties:
            explanation += (
                f"\n\nCette analyse combine vos préférences (vous aviez sélectionné: {', '.join(onboarding_parties)}) "
                f"avec nos recommandations morphologiques (nous suggérons: {', '.join(openai_parties)})."
            )
        elif onboarding_parties:
            explanation += f"\n\nVous aviez sélectionné ces zones à minimiser: {', '.join(onboarding_parties)}."
        elif openai_parties:
            explanation += f"\n\nNous recommandons de minimiser visuellement: {', '.join(openai_parties)}."

        full_text = f"""ANNONCE: {announcement}

EXPLICATION: {explanation}"""

        return {
            "announcement": announcement,
            "explanation": explanation,
            "full_text": full_text
        }


    @staticmethod
    def _repair_broken_json(json_str: str) -> str:
        """Répare les JSON partiellement cassés"""
        # Fermer les strings ouvertes
        json_str = re.sub(r'"([^"]*?)$', r'"\1"', json_str, flags=re.MULTILINE)
        
        # Ajouter accolades fermantes manquantes
        open_count = json_str.count('{')
        close_count = json_str.count('}')
        if open_count > close_count:
            json_str += '}' * (open_count - close_count)
        
        return json_str
    
    async def force_valid_json(self, raw_content: str, context: str) -> dict:
        """
        Redemande à OpenAI de corriger STRICTEMENT un JSON invalide.
        """
        repair_prompt = f"""
    Tu as généré le JSON suivant, mais il est INVALIDE.

    Corrige-le pour qu’il soit :
    - strictement valide JSON
    - sans rien ajouter
    - sans texte hors JSON

    JSON À CORRIGER :
    {raw_content}
    """

        self.openai.set_context(f"{context} - JSON FIX", "")
        self.openai.set_system_prompt(
            "Tu es un validateur JSON strict. Tu ne produis QUE du JSON valide."
        )

        response = await self.openai.call_chat(
            prompt=repair_prompt,
            model="gpt-4-turbo",
            max_tokens=2000
        )

        content = response.get("content", "").strip()
        return json.loads(content)

    def _generate_default_recommendations(self, silhouette: str) -> dict:
        """Génère des recommandations par défaut si OpenAI échoue (structure SAFE complète)"""
        print("   ✅ Génération recommandations par défaut")

        # --- Base fallback minimal mais complet, compatible template + fusion ---
        base_category = lambda label: {
            "introduction": f"Recommandations générales pour les {label}.",
            "recommandes": [
                {
                    "cut_display": "Coupe adaptée à votre silhouette",
                    "why": "Cette coupe aide à équilibrer les volumes et à structurer la silhouette."
                }
            ],
            "a_eviter": [
                {
                    "cut_display": "Coupe non structurée",
                    "why": "Elle peut déséquilibrer visuellement la silhouette et alourdir la ligne."
                }
            ]
        }

        defaults = {
            "A": {
                "hauts": {
                    "introduction": "Pour une silhouette A, l’objectif est de valoriser le haut du corps et d’apporter de la structure aux épaules.",
                    "recommandes": [
                        {"cut_display": "Haut structuré", "why": "Crée du volume au haut"},
                        {"cut_display": "Encolure V", "why": "Allonge le buste"},
                        {"cut_display": "Col rond ajusté", "why": "Met en avant les épaules"},
                        {"cut_display": "Haut échancré", "why": "Crée de la profondeur"},
                        {"cut_display": "Manches montantes", "why": "Définit les épaules"},
                        {"cut_display": "Peplum placé haut", "why": "Donne du relief au haut du corps"},
                    ],
                    "a_eviter": [
                        {"cut_display": "Haut moulant long", "why": "Accentue le contraste haut/bas"},
                        {"cut_display": "Tunique informe", "why": "Retire la structure du buste"},
                        {"cut_display": "Col bateau très large", "why": "Élargit artificiellement"},
                        {"cut_display": "Haut oversize sans taille", "why": "Perd les proportions"},
                        {"cut_display": "Manches très bouffantes", "why": "Peut surcharger le haut"},
                    ]
                },
                "bas": {
                    "introduction": "Pour une silhouette A, l’objectif est d’allonger la jambe et d’équilibrer la zone des hanches.",
                    "recommandes": [
                        {"cut_display": "Jean taille haute droit", "why": "Allonge les jambes"},
                        {"cut_display": "Pantalon droit", "why": "Équilibre les hanches"},
                        {"cut_display": "Jupe évasée", "why": "Harmonise la ligne des hanches"},
                        {"cut_display": "Pantalon flare léger", "why": "Crée une verticalité"},
                        {"cut_display": "Jupe plissée fine", "why": "Structure sans épaissir"},
                        {"cut_display": "Couleurs plus sombres en bas", "why": "Affinent visuellement"},
                    ],
                    "a_eviter": [
                        {"cut_display": "Pantalon moulant clair", "why": "Met l’accent sur les hanches"},
                        {"cut_display": "Short très court", "why": "Raccourcit la jambe"},
                        {"cut_display": "Pantalon très large", "why": "Élargit la silhouette"},
                        {"cut_display": "Jupe portefeuille épaisse", "why": "Ajoute du volume latéral"},
                        {"cut_display": "Motifs larges sur les hanches", "why": "Grossissent visuellement"},
                    ]
                },
                "robes": base_category("robes"),
                "vestes": base_category("vestes"),
                "maillot_lingerie": base_category("maillots / lingerie"),
                "chaussures": base_category("chaussures"),
                "accessoires": base_category("accessoires"),
            }
        }

        # Si silhouette inconnue → fallback sur A
        result = defaults.get(silhouette, defaults["A"])

        # Sécurité : s’assurer que toutes les catégories existent
        for category in ["hauts", "bas", "robes", "vestes", "maillot_lingerie", "chaussures", "accessoires"]:
            if category not in result:
                result[category] = base_category(category)

            # Sécurité : clés attendues
            result[category].setdefault("introduction", "")
            result[category].setdefault("recommandes", [])
            result[category].setdefault("a_eviter", [])

        return {"recommendations": result}


morphology_service = MorphologyService()