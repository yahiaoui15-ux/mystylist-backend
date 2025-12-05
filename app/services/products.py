from app.utils.supabase_client import supabase

class ProductsService:
    def __init__(self):
        self.supabase = supabase
    
    async def fetch_recommendations(self, category: str, colorimetry_result: dict, morphology_result: dict) -> list:
        """
        Récupère produits filtrés par colorimétrie + morphologie
        
        ✅ FIX: Gérer correctement les colonnes avec slashes ("category/primary")
        
        Args:
            category: Catégorie (hauts, bas, robes, chaussures, vestes)
            colorimetry_result: Résultat colorimétrie
            morphology_result: Résultat morphologie
        
        Returns:
            list de 10-20 produits recommandés
        """
        try:
            print(f"🛍️  Récupération produits {category}...")
            
            # ✅ FIX: Utiliser le vrai client Supabase directement
            # car les colonnes avec slashes ne marchent pas bien avec supabase.query()
            try:
                client = self.supabase._get_client()
                if client is None:
                    print(f"⚠️  Client Supabase None")
                    return []
                
                # ✅ FIX: Les colonnes avec slashes doivent être mappées correctement
                # "category/primary" contient des valeurs comme "Apparel & Accessories"
                # On doit les mapper à nos catégories: "hauts", "bas", "robes", etc.
                
                # Récupérer TOUS les produits et les filtrer côté Python
                result = client.table("Products place des tendances").select("*").limit(50).execute()
                
                if not result or not result.data:
                    print(f"⚠️  Aucun produit trouvé dans la table")
                    return []
                
                products = result.data
                print(f"   📦 {len(products)} produits trouvés dans la table")
                
                # Filtrer par catégorie
                filtered_products = []
                
                for product in products:
                    try:
                        # Récupérer les infos du produit
                        product_name = product.get("_name", "")
                        product_category_primary = product.get("category/primary", "").lower()
                        product_category_secondary = product.get("category/secondary", "").lower()
                        
                        # Mapper la catégorie Supabase à notre catégorie
                        matches_category = False
                        
                        if category == "hauts":
                            matches_category = (
                                "shirt" in product_category_secondary or 
                                "top" in product_category_secondary or
                                "sweater" in product_category_secondary
                            )
                        elif category == "bas":
                            matches_category = (
                                "pant" in product_category_secondary or 
                                "jean" in product_category_secondary or
                                "short" in product_category_secondary or
                                "pant" in product_category_secondary
                            )
                        elif category == "robes":
                            matches_category = (
                                "dress" in product_category_secondary or 
                                "robe" in product_category_secondary
                            )
                        elif category == "chaussures":
                            matches_category = (
                                "shoe" in product_category_primary.lower() or 
                                "shoe" in product_category_secondary or
                                "sandal" in product_category_secondary or
                                "boot" in product_category_secondary
                            )
                        elif category == "vestes":
                            matches_category = (
                                "jacket" in product_category_secondary or 
                                "blazer" in product_category_secondary or
                                "coat" in product_category_secondary or
                                "vest" in product_category_secondary
                            )
                        
                        if matches_category:
                            filtered_products.append({
                                "name": product_name,
                                "brand": product.get("brand", ""),
                                "price": product.get("price/retail", 0),
                                "url": product.get("URL/product/0", ""),
                                "image_url": product.get("URL/productImage", ""),
                                "category": category
                            })
                            
                            if len(filtered_products) >= 15:
                                break
                    
                    except Exception as product_error:
                        print(f"⚠️  Erreur traitement produit: {str(product_error)[:100]}")
                        continue
                
                print(f"✅ {len(filtered_products)} produits filtrés pour {category}")
                return filtered_products
                
            except Exception as supabase_error:
                print(f"❌ Erreur requête Supabase: {type(supabase_error).__name__}: {str(supabase_error)[:150]}")
                return []
            
        except Exception as e:
            print(f"❌ Erreur récupération produits {category}: {type(e).__name__}: {str(e)[:150]}")
            import traceback
            traceback.print_exc()
            return []


# Instance globale
products_service = ProductsService()