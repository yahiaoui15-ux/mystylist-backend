"""
REPORT GENERATOR v2.0 - Avec résumé final call_tracker
✅ Affiche le résumé de TOUS les appels OpenAI à la fin
"""

import asyncio
from app.services.colorimetry import colorimetry_service
from app.services.morphology import morphology_service
from app.services.styling import styling_service
from app.services.visuals import visuals_service
from app.services.products import products_service
from app.utils.openai_call_tracker import call_tracker


class ReportGenerator:
    """Orchestre la génération complète du rapport avec tracking"""
    
    async def generate_complete_report(self, user_data: dict) -> dict:
        """
        Génère le rapport complet avec résumé final des appels OpenAI
        
        Timeline:
        - Colorimétrie + Morphologie: parallèle (20s max)
        - Profil Styling: dépend des 2 (15s)
        - Visuels + Produits: parallèle (5s)
        Total: ~40s
        
        Args:
            user_data: Données utilisateur complètes
        
        Returns:
            dict avec tous les résultats
        """
        try:
            print("\n🚀 GÉNÉRATION RAPPORT COMPLET")
            print("="*80 + "\n")
            
            # PHASE 1: Paralléliser colorimétrie + morphologie
            print("⏳ PHASE 1: Analyses colorimétrie & morphologie (parallèle)...\n")
            colorimetry_task = colorimetry_service.analyze(user_data)
            morphology_task = morphology_service.analyze(user_data)
            
            colorimetry_result, morphology_result = await asyncio.gather(
                colorimetry_task,
                morphology_task
            )
            
            if not colorimetry_result or not morphology_result:
                print("❌ Erreur analyses IA")
                call_tracker.print_summary()
                return {}
            
            # PHASE 2: Profil Styling
            print("\n⏳ PHASE 2: Génération profil stylistique...\n")
            styling_result = await styling_service.generate(
                colorimetry_result,
                morphology_result,
                user_data
            )
            
            # PHASE 3: Visuels + Produits
            print("\n⏳ PHASE 3: Récupération visuels & produits (parallèle)...\n")
            
            # ✅ FIX: fetch_for_recommendations() est SYNCHRONE
            loop = asyncio.get_event_loop()
            
            visuals_task = loop.run_in_executor(
                None,
                visuals_service.fetch_for_recommendations,
                morphology_result
            )
            
            # Tâches produits pour 5 catégories
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
            
            # Assembler le rapport final
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
            
            print("\n✅ Rapport généré avec succès!")
            
            # ✅ AFFICHER LE RÉSUMÉ FINAL DE TOUS LES APPELS
            call_tracker.print_summary()
            
            return report
            
        except Exception as e:
            print(f"\n❌ ERREUR GÉNÉRATION RAPPORT: {e}")
            call_tracker.log_error("ReportGenerator", str(e))
            
            # Afficher quand même le résumé des appels effectués avant l'erreur
            call_tracker.print_summary()
            
            import traceback
            traceback.print_exc()
            raise


# Instance globale
report_generator = ReportGenerator()