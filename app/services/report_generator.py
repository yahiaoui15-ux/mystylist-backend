"""
REPORT GENERATOR v3.0 - Appels SÉQUENTIELS (pas parallèles)
✅ Colorimetry → Morphology → Styling (dans cet ordre)
✅ Aucun mélange de logs entre les sections
"""

import asyncio
from app.services.colorimetry import colorimetry_service
from app.services.morphology import morphology_service
from app.services.styling import styling_service
from app.services.visuals import visuals_service
from app.services.products import products_service
from app.utils.openai_call_tracker import call_tracker


class ReportGenerator:
    """Orchestre la génération complète du rapport - SÉQUENTIELLE"""
    
    async def generate_complete_report(self, user_data: dict) -> dict:
        """
        Génère le rapport complet - APPELS SÉQUENTIELS pour logs cloisonnés
        """
        try:
            print("\n" + "="*80)
            print("🚀 GÉNÉRATION RAPPORT COMPLET - APPELS SÉQUENTIELS")
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
            
            # PHASE 2: MORPHOLOGY (1 appel)
            print("\n" + "█"*80)
            print("█ PHASE 2: MORPHOLOGY (1 appel)")
            print("█"*80)
            
            morphology_result = await morphology_service.analyze(user_data)
            
            if not morphology_result:
                print("\n⚠️ Erreur morphology - continuation avec données vides")
                morphology_result = {}
            
            # PHASE 3: STYLING (1 appel)
            print("\n" + "█"*80)
            print("█ PHASE 3: STYLING (1 appel)")
            print("█"*80)
            
            styling_result = await styling_service.generate(
                colorimetry_result,
                morphology_result,
                user_data
            )
            
            if not styling_result:
                print("\n⚠️ Erreur styling - continuation avec données vides")
                styling_result = {}
            
            # PHASE 4: VISUALS + PRODUCTS (parallèle - pas d'appels OpenAI)
            print("\n" + "█"*80)
            print("█ PHASE 4: VISUALS + PRODUCTS (parallèle - pas d'appels OpenAI)")
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
            
            # RÉSUMÉ FINAL
            call_tracker.print_summary()
            
            return report
            
        except Exception as e:
            print(f"\n❌ ERREUR GÉNÉRATION RAPPORT: {e}")
            call_tracker.log_error("ReportGenerator", str(e))
            call_tracker.print_summary()
            
            import traceback
            traceback.print_exc()
            raise


report_generator = ReportGenerator()