from app.utils.supabase_client import supabase

class VisualsService:
    def __init__(self):
        self.supabase = supabase
    
    async def fetch_for_recommendations(self, morphology_result: dict) -> dict:
        """
        Récupère les visuels pédagogiques pour chaque recommandation morpho
        
        Args:
            morphology_result: Résultat analyse morphologie avec recommandations
        
        Returns:
            dict avec visuels organisés par catégorie
        """
        try:
            print("🖼️  Récupération visuels pédagogiques...")
            
            visuals_by_category = {}
            recommendations = morphology_result.get("recommendations", {})
            
            # Catégories à traiter
            categories = ["hauts", "bas", "robes", "vestes", "maillots", "accessoires"]
            
            for category in categories:
                if category not in recommendations:
                    continue
                
                visuals_by_category[category] = {
                    "a_privilegier": [],
                    "a_eviter": []
                }
                
                # Traiter les visuels à privilégier
                for rec in recommendations[category].get("a_privilegier", []):
                    cut_key = rec.get("cut")
                    if cut_key:
                        visual = await self._get_visual(category, cut_key)
                        if visual:
                            visuals_by_category[category]["a_privilegier"].append({
                                **rec,
                                "image_url": visual.get("image_url"),
                                "visual_id": visual.get("id")
                            })
                
                # Traiter les visuels à éviter
                for rec in recommendations[category].get("a_eviter", []):
                    cut_key = rec.get("cut")
                    if cut_key:
                        visual = await self._get_visual(category, cut_key)
                        if visual:
                            visuals_by_category[category]["a_eviter"].append({
                                **rec,
                                "image_url": visual.get("image_url")
                            })
            
            print(f"✅ Visuels récupérés: {len(visuals_by_category)} catégories")
            return visuals_by_category
            
        except Exception as e:
            print(f"❌ Erreur récupération visuels: {e}")
            return {}
    
    async def _get_visual(self, category: str, cut_key: str) -> dict:
        """Récupère un visuel spécifique"""
        try:
            result = await self.supabase.query_table(
                "visuels",
                filters={
                    "category": category,
                    "cut_key": cut_key
                }
            )
            
            if result and len(result) > 0:
                return result[0]
            return None
            
        except Exception as e:
            print(f"⚠️  Visuel non trouvé {category}/{cut_key}: {e}")
            return None

# Instance globale
visuals_service = VisualsService()