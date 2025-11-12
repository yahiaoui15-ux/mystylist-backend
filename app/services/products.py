from app.utils.supabase_client import supabase

class ProductsService:
    def __init__(self):
        self.supabase = supabase
    
    async def fetch_recommendations(self, category: str, colorimetry_result: dict, morphology_result: dict) -> list:
        """
        Récupère produits filtrés par colorimétrie + morphologie
        
        Args:
            category: Catégorie (hauts, bas, robes, chaussures, vestes)
            colorimetry_result: Résultat colorimétrie (saison, palette)
            morphology_result: Résultat morphologie (silhouette_type)
        
        Returns:
            list de 10-20 produits recommandés
        """
        try:
            print(f"🛍️  Récupération produits {category}...")
            
            # Récupérer les produits de la catégorie - UTILISER supabase.query()
            response = self.supabase.query(
                "Products place des tendances",
                select_fields="*",
                filters={
                    "category/primary": category
                }
            )
            
            products = response.data if response.data else []
            
            if not products:
                print(f"⚠️  Aucun produit trouvé pour {category}")
                return []
            
            # Filtrer par colorimétrie (saison)
            season = colorimetry_result.get("season", "")
            silhouette = morphology_result.get("silhouette_type", "")
            
            filtered_products = []
            for product in products[:20]:  # Limiter à 20 produits
                # Vérifier si le produit correspond à la saison (optionnel si pas de tag)
                # Pour l'instant, on prend les premiers produits
                filtered_products.append({
                    "name": product.get("_name", ""),
                    "brand": product.get("brand", ""),
                    "price": product.get("price/retail", 0),
                    "url": product.get("URL/product/0", ""),
                    "image_url": product.get("URL/productImage", ""),
                    "category": product.get("category/primary", category)
                })
            
            print(f"✅ {len(filtered_products)} produits pour {category}")
            return filtered_products
            
        except Exception as e:
            print(f"❌ Erreur récupération produits {category}: {e}")
            return []

# Instance globale
products_service = ProductsService()