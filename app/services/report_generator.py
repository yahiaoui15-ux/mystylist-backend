"""
REPORT GENERATOR v3.2 - Morphologie découpage 2 appels + styling params fix
✅ Morphology: Part 1 (vision) + Part 2 (text) - 600 tokens total
✅ Styling: paramètres nommés corrects
"""

import asyncio
import re



from app.services.colorimetry import colorimetry_service
from app.services.morphology import morphology_service
from app.services.styling import styling_service
from app.services.visuals import visuals_service
from app.services.products import products_service
from app.utils.openai_call_tracker import call_tracker
from app.utils.supabase_client import supabase
from typing import Any

class ReportGenerator:
    """Orchestre génération rapport - SÉQUENTIELLE"""
    
    async def generate_complete_report(self, user_data: dict) -> dict:
        """Génère rapport complet"""
        try:
            print("\n" + "="*80)
            print("🚀 GÉNÉRATION RAPPORT COMPLET")
            print("="*80)
            
            # PHASE 1: COLORIMETRY (3 appels)
            print("\n" + "█"*80)
            print("█ PHASE 1: COLORIMETRY (3 appels)")
            print("█"*80)
            
            colorimetry_result = await colorimetry_service.analyze(user_data)
            
            if not colorimetry_result:
                print("\n❌ Erreur colorimetry - arrêt")
                call_tracker.print_summary()
                return {}
            
            # PHASE 2: MORPHOLOGY (2 appels)
            print("\n" + "█"*80)
            print("█ PHASE 2: MORPHOLOGY (2 appels - Part 1 vision + Part 2 text)")
            print("█"*80)
            
            morphology_result = await morphology_service.analyze(user_data)
            
            if not morphology_result:
                print("\n⚠️ Erreur morphology - continuation avec données vides")
                morphology_result = {}
            
            # PHASE 3: STYLING (1 appel)
            print("\n" + "█"*80)
            print("█ PHASE 3: STYLING (1 appel)")
            print("█"*80)
            
            # ✅ FIX: Passer les dictionnaires complets (signature correcte)
            styling_result = await styling_service.generate(
                colorimetry_result=colorimetry_result,
                morphology_result=morphology_result,
                user_data=user_data
            )
            
            if not styling_result:
                print("\n⚠️ Erreur styling - continuation avec données vides")
                styling_result = {}
            
            # ✅ STOCKAGE PROFIL IA (DB)
            self._upsert_user_ai_profile(
                user_id=user_data.get("user_id"),
                colorimetry_result=colorimetry_result,
                morphology_result=morphology_result,
                styling_result=styling_result,
                user_data=user_data,
            )
            
            # PHASE 4: VISUALS + PRODUCTS (parallèle)
            print("\n" + "█"*80)
            print("█ PHASE 4: VISUALS + PRODUCTS (parallèle)")
            print("█"*80)
            
            loop = asyncio.get_event_loop()
            
            visuals_task = loop.run_in_executor(
                None,
                visuals_service.fetch_for_recommendations,
                morphology_result
            )
            
            products_tasks = [
                products_service.fetch_recommendations("hauts", colorimetry_result, morphology_result),
                products_service.fetch_recommendations("bas", colorimetry_result, morphology_result),
                products_service.fetch_recommendations("robes", colorimetry_result, morphology_result),
                products_service.fetch_recommendations("chaussures", colorimetry_result, morphology_result),
                products_service.fetch_recommendations("vestes", colorimetry_result, morphology_result),
            ]
            
            visuals, hauts, bas, robes, chaussures, vestes = await asyncio.gather(
                visuals_task,
                *products_tasks
            )
            
            print("✅ Visuals et produits récupérés\n")
            
            # ASSEMBLAGE FINAL
            report = {
                "user_name": user_data.get("user_name", ""),
                "user_email": user_data.get("user_email", ""),
                "colorimetry": colorimetry_result,
                "morphology": morphology_result,
                "styling": styling_result,
                "visuals": visuals,
                "products": {
                    "hauts": hauts,
                    "bas": bas,
                    "robes": robes,
                    "chaussures": chaussures,
                    "vestes": vestes
                }
            }
            
            print("✅ Rapport généré avec succès!")
            
            call_tracker.print_summary()
            
            return report
            
        except Exception as e:
            print(f"\n❌ ERREUR GÉNÉRATION RAPPORT: {e}")
            call_tracker.log_error("ReportGenerator", str(e))
            call_tracker.print_summary()
            
            import traceback
            traceback.print_exc()
            raise

    def _upsert_user_ai_profile(
            self,
            user_id: str,
            colorimetry_result: dict,
            morphology_result: dict,
            styling_result: dict,
            user_data: dict | None = None,
        ) -> None:
            """
            Stocke le profil IA + champs dérivés dans public.user_ai_profiles.
            Objectif: Edge Function = filtres rapides sans reparsing lourd des JSON.
            """

            if not user_id:
                print("⚠️ user_id manquant -> skip upsert user_ai_profiles")
                return

            color = colorimetry_result or {}
            morph = morphology_result or {}
            style = styling_result or {}

            # ---------------------------
            # Helpers robustes
            # ---------------------------
            def _norm_list(x: Any) -> list:
                return x if isinstance(x, list) else []

            def _norm_str(x: Any) -> str:
                return x.strip() if isinstance(x, str) else ""

            def _uniq(items: list[str]) -> list[str]:
                out, seen = [], set()
                for it in items:
                    it = _norm_str(it)
                    if not it:
                        continue
                    key = it.lower()
                    if key in seen:
                        continue
                    seen.add(key)
                    out.append(it)
                return out

            def _extract_color_names(color_list: Any) -> list[str]:
                """
                Listes type: [{"name":"terracotta","displayName":"Terracotta",...}, {"displayName":"gris",...}]
                """
                names = []
                for c in _norm_list(color_list):
                    if isinstance(c, dict):
                        n = c.get("displayName") or c.get("name")
                        n = _norm_str(n)
                        if n:
                            names.append(n)
                    elif isinstance(c, str):
                        n = _norm_str(c)
                        if n:
                            names.append(n)
                return _uniq(names)

            def _extract_strong_terms(html: Any) -> list[str]:
                """
                Extrait les termes entre <strong>...</strong> depuis tes champs HTML (matieres/motifs).
                """
                s = _norm_str(html)
                if not s:
                    return []
                # le HTML dans ton payload est échappé \u003cstrong\u003e : mais côté Python tu reçois souvent déjà "<strong>"
                # On gère les 2.
                s = s.replace("\\u003c", "<").replace("\\u003e", ">")
                terms = re.findall(r"<strong>\s*([^<]+?)\s*</strong>", s, flags=re.IGNORECASE)
                return _uniq([t for t in terms])

            def _extract_morpho_cuts(morpho_categories: dict) -> tuple[list[str], list[str], list[str], list[str]]:
                """
                Retourne:
                cuts_recommended, cuts_avoid, materials_recommended, pattern_recommended
                """
                cuts_rec, cuts_avoid = [], []
                mats_rec, pats_rec = [], []
                pats_avoid = []

                if not isinstance(morpho_categories, dict):
                    return [], [], [], []

                for _, cat in morpho_categories.items():
                    if not isinstance(cat, dict):
                        continue

                    # Cuts recommandées / à éviter
                    for item in _norm_list(cat.get("recommandes")):
                        if isinstance(item, dict):
                            cuts_rec.append(item.get("cut_display") or item.get("visual_key") or "")
                        elif isinstance(item, str):
                            cuts_rec.append(item)

                    for item in _norm_list(cat.get("a_eviter")):
                        if isinstance(item, dict):
                            cuts_avoid.append(item.get("cut_display") or item.get("visual_key") or "")
                        elif isinstance(item, str):
                            cuts_avoid.append(item)

                    # Matières (HTML) -> termes <strong>
                    mats_rec.extend(_extract_strong_terms(cat.get("matieres")))

                    # Motifs (HTML) -> termes <strong>
                    motifs = cat.get("motifs") or {}
                    if isinstance(motifs, dict):
                        pats_rec.extend(_extract_strong_terms(motifs.get("recommandes")))
                        pats_avoid.extend(_extract_strong_terms(motifs.get("a_eviter")))

                # On fusionne pats_avoid dans pattern_avoid plus bas (avec onboarding)
                return _uniq(cuts_rec), _uniq(cuts_avoid), _uniq(mats_rec), _uniq(pats_rec + pats_avoid)

            def _extract_style_keywords(style_obj: dict) -> list[str]:
                """
                Basé sur payload:
                styling.page17.style_mix = [{style:"Minimaliste", pct:50}, ...]
                + éventuellement texte pillars
                """
                kws = []

                page17 = (style_obj.get("page17") or {}) if isinstance(style_obj, dict) else {}
                style_mix = _norm_list(page17.get("style_mix"))
                for s in style_mix:
                    if isinstance(s, dict):
                        kws.append(s.get("style") or "")

                # fallback: si un "style_name" existe
                kws.append(page17.get("style_name") or "")

                # Ajoute quelques signaux depuis les "pillars" si présents
                for p in _norm_list(page17.get("pillars")):
                    if isinstance(p, str):
                        # très light: ne pas stocker phrases entières, juste un tag si ça match
                        low = p.lower()
                        if "animal" in low:
                            kws.append("Anti-animalier")
                        if "minimal" in low:
                            kws.append("Minimaliste")
                        if "romant" in low:
                            kws.append("Romantique")
                        if "classiq" in low:
                            kws.append("Classique")

                return _uniq([k for k in kws if _norm_str(k)])

            def _extract_preferred_brands_from_text(style_obj: dict) -> list[str]:
                """
                Ton texte mentionne souvent les marques favorites (ex: Uniqlo, H&M).
                On tente une extraction simple depuis constraints_text / why_this_style_text.
                """
                brands = []
                page17 = (style_obj.get("page17") or {}) if isinstance(style_obj, dict) else {}
                blob = " ".join([
                    _norm_str(page17.get("constraints_text")),
                    _norm_str(page17.get("why_this_style_text")),
                ]).lower()

                # Heuristiques simples (tu peux compléter)
                if "uniqlo" in blob:
                    brands.append("Uniqlo")
                if "h&m" in blob or "h\\u0026m" in blob or "h&m," in blob:
                    brands.append("H&M")

                return _uniq(brands)

            # ---------------------------
            # 1) Couleurs (best / ok / avoid / keywords)
            # ---------------------------
            colors_best = _extract_color_names(color.get("palette_personnalisee"))
            # "ok" = couleurs prudence + génériques (selon ton payload)
            colors_ok = _extract_color_names(color.get("couleurs_prudence")) + _extract_color_names(color.get("couleurs_generiques"))
            colors_ok = _uniq(colors_ok)

            # avoid = couleurs_eviter + unwanted_colors (payload)
            colors_avoid = _extract_color_names(color.get("couleurs_eviter")) + _extract_color_names(color.get("unwanted_colors"))
            colors_avoid = _uniq(colors_avoid)

            # color_keywords = union best/ok (utile pour recherche simple)
            color_keywords = _uniq(colors_best + colors_ok)

            # ---------------------------
            # 2) Morphologie: cuts + matières + motifs
            # ---------------------------
            morpho_categories = (((morph.get("morpho") or {}).get("categories")) if isinstance(morph.get("morpho"), dict) else None)
            if morpho_categories is None:
                # parfois c'est directement morph["categories"]
                morpho_categories = morph.get("categories")

            cuts_recommended, cuts_avoid, materials_recommended, pattern_from_morpho = _extract_morpho_cuts(morpho_categories if isinstance(morpho_categories, dict) else {})

            # ---------------------------
            # 3) Onboarding: brands / pattern_avoid / style_keywords
            # ---------------------------
            preferred_brands = []
            pattern_avoid = []
            style_keywords = []

            onboarding = {}
            if user_data:
                onboarding = ((user_data.get("profile") or {}).get("onboarding_data") or {})

            # Adapte ces clés EXACTES à ton schéma onboarding
            preferred_brands = onboarding.get("preferred_brands") or onboarding.get("brands") or []
            pattern_avoid = onboarding.get("pattern_avoid") or onboarding.get("disliked_patterns") or []
            style_keywords = onboarding.get("style_preferences") or onboarding.get("styles") or []

            preferred_brands = preferred_brands if isinstance(preferred_brands, list) else []
            pattern_avoid = pattern_avoid if isinstance(pattern_avoid, list) else []
            style_keywords = style_keywords if isinstance(style_keywords, list) else []

            # Ajoute les signaux issus du style IA (page17)
            style_keywords = _uniq(style_keywords + _extract_style_keywords(style.get("styling") or style))
            # Ajoute les marques trouvées dans le texte IA si onboarding incomplet
            preferred_brands = _uniq(preferred_brands + _extract_preferred_brands_from_text(style.get("styling") or style))
            # Ajoute motifs/éviter issus morpho (et éventuellement “imprimés animaliers” depuis IA)
            pattern_avoid = _uniq(pattern_avoid + pattern_from_morpho)

            # ---------------------------
            # 4) Champs “filtres” de base
            # ---------------------------
            color_season = color.get("saison_confirmee") or color.get("season")
            undertone = color.get("sous_ton_detecte")
            silhouette_type = (
                (morph.get("silhouette_type"))
                or (morph.get("bodyType"))
                or ((morph.get("morphology") or {}).get("bodyType") if isinstance(morph.get("morphology"), dict) else None)
            )

            # ---------------------------
            # Record final (colonne EXACTES)
            # ---------------------------
            record = {
                "user_id": user_id,

                # JSON sources de vérité
                "colorimetry_json": color,
                "morphology_json": morph,
                "style_json": style,

                # Filtres
                "color_season": color_season,
                "undertone": undertone,
                "silhouette_type": silhouette_type,

                # ✅ Champs nécessaires Edge Function
                "colors_best": colors_best,               # text[] ou jsonb selon ta table
                "colors_ok": colors_ok,
                "colors_avoid": colors_avoid,
                "color_keywords": color_keywords,

                "cuts_recommended": cuts_recommended,
                "cuts_avoid": cuts_avoid,

                # motifs/matières: ta table mentionne pattern_avoid; si tu as "materials_*", ajoute
                "pattern_avoid": pattern_avoid,
                "style_keywords": style_keywords,
                "preferred_brands": preferred_brands,

                # si tu as une colonne matières (recommandé pour filtrage)
                # "materials_recommended": materials_recommended,

                "source_version": "report_generator_v3.2_profiles_v1",
            }

            client = supabase.get_client()
            client.table("user_ai_profiles").upsert(record, on_conflict="user_id").execute()
            print("✅ user_ai_profiles upsert OK (with derived columns)")

report_generator = ReportGenerator()