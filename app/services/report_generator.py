"""
REPORT GENERATOR v3.2 - Morphologie découpage 2 appels + styling params fix
✅ Morphology: Part 1 (vision) + Part 2 (text) - 600 tokens total
✅ Styling: paramètres nommés corrects
"""

import asyncio

from app.services.colorimetry import colorimetry_service
from app.services.morphology import morphology_service
from app.services.styling import styling_service
from app.services.visuals import visuals_service
from app.services.products import products_service
from app.utils.openai_call_tracker import call_tracker
from app.utils.supabase_client import supabase


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
                styling_result=styling_result
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
        styling_result: dict
    ) -> None:
        """
        Stocke le profil IA (JSON complets) dans public.user_ai_profiles.
        Upsert sur user_id = 1 seule ligne par user.
        """
        if not user_id:
            print("⚠️ user_id manquant -> skip upsert user_ai_profiles")
            return

        # champs dérivés utiles (optionnels)
        season = (colorimetry_result or {}).get("saison_confirmee")
        undertone = (colorimetry_result or {}).get("sous_ton_detecte")
        silhouette = (morphology_result or {}).get("silhouette_type")

        record = {
            "user_id": user_id,
            "colorimetry_json": colorimetry_result or {},
            "morphology_json": morphology_result or {},
            "styling_json": styling_result or {},
            "season": season,
            "undertone": undertone,
            "silhouette_type": silhouette,
        }

        client = supabase.get_client()
        client.table("user_ai_profiles").upsert(record, on_conflict="user_id").execute()
        print("✅ user_ai_profiles upsert OK")

report_generator = ReportGenerator()