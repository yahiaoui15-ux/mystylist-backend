import asyncio
from app.services.colorimetry import colorimetry_service
from app.services.morphology import morphology_service
from app.services.styling import styling_service
from app.services.visuals import visuals_service
from app.services.products import products_service

class ReportGenerator:
    """Orchestre la génération complète du rapport"""
    
    async def generate_complete_report(self, user_data: dict) -> dict:
        """
        Génère le rapport complet en parallélisant les appels
        
        Timeline:
        - Colorimétrie + Morphologie: parallèle (20s max)
        - Profil Styling: dépend des 2 (15s)
        - Visuels + 5x Produits: parallèle (5s)
        Total: ~40s au lieu de 60-90s
        
        Args:
            user_data: Données utilisateur complètes
        
        Returns:
            dict avec tous les résultats
        """
        try:
            print("🚀 Début génération rapport...")
            
            # PHASE 1: Paralléliser colorimétrie + morphologie
            print("⏳ Phase 1: Analyses colorimétrie & morphologie (parallèle)...")
            colorimetry_task = colorimetry_service.analyze(user_data)
            morphology_task = morphology_service.analyze(user_data)
            
            colorimetry_result, morphology_result = await asyncio.gather(
                colorimetry_task,
                morphology_task
            )
            
            if not colorimetry_result or not morphology_result:
                print("❌ Erreur analyses IA")
                return {}
            
            # PHASE 2: Profil Styling (séquentiel, dépend des 2 autres)
            print("⏳ Phase 2: Génération profil stylistique...")
            styling_result = await styling_service.generate(
                colorimetry_result,
                morphology_result,
                user_data
            )
            
            # PHASE 3: Visuels + Produits (parallèle)
            print("⏳ Phase 3: Récupération visuels & produits (parallèle)...")
            
            # ✅ FIX: fetch_for_recommendations() est SYNCHRONE
            # Donc on la wrapper avec run_in_executor() pour la paralléliser
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
            
            print("✅ Rapport généré avec succès!")
            return report
            
        except Exception as e:
            print(f"❌ Erreur génération rapport: {e}")
            import traceback
            traceback.print_exc()
            raise

# Instance globale
report_generator = ReportGenerator()