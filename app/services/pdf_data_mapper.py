"""
PDF Data Mapper - VERSION ULTRA-SAFE avec logging détaillé
Identifie exactement où se produit l'erreur 'list has no attribute get'
"""

from typing import Dict, Any, Optional
from datetime import datetime
import json


class PDFDataMapper:
    """
    Mappe les données du rapport généré au format PDFMonkey
    VERSION ULTRA-SAFE: Logs détaillés pour debug
    """
    
    @staticmethod
    def prepare_liquid_variables(report_data: dict, user_data: dict) -> dict:
        """
        Prépare les variables Liquid pour le template PDFMonkey
        FORMAT ULTRA-SÛRE avec logging détaillé
        """
        
        print("\n" + "="*80)
        print("🔍 DEBUG - prepare_liquid_variables START")
        print("="*80)
        
        # 1. Vérifier le type de report_data
        print(f"✓ Step 1: Vérifier report_data")
        print(f"  Type: {type(report_data)}")
        if not isinstance(report_data, dict):
            print(f"  ❌ ERREUR: report_data n'est pas un dict!")
            return {}
        print(f"  Keys: {list(report_data.keys())}")
        
        # 2. Extraire et vérifier colorimetry
        print(f"\n✓ Step 2: Extraire colorimetry")
        try:
            colorimetry = report_data.get("colorimetry", {})
            print(f"  Type: {type(colorimetry)}")
            if not isinstance(colorimetry, dict):
                print(f"  ⚠️  ATTENTION: colorimetry est un {type(colorimetry)}, pas dict!")
                colorimetry = {}
            else:
                print(f"  ✓ Keys: {list(colorimetry.keys())[:5]}")
        except Exception as e:
            print(f"  ❌ ERREUR dans colorimetry: {e}")
            colorimetry = {}
        
        # 3. Extraire et vérifier morphology
        print(f"\n✓ Step 3: Extraire morphology")
        try:
            morphology = report_data.get("morphology", {})
            print(f"  Type: {type(morphology)}")
            if not isinstance(morphology, dict):
                print(f"  ⚠️  ATTENTION: morphology est un {type(morphology)}, pas dict!")
                morphology = {}
            else:
                print(f"  ✓ Keys: {list(morphology.keys())[:5]}")
        except Exception as e:
            print(f"  ❌ ERREUR dans morphology: {e}")
            morphology = {}
        
        # 4. Extraire et vérifier styling
        print(f"\n✓ Step 4: Extraire styling")
        try:
            styling = report_data.get("styling", {})
            print(f"  Type: {type(styling)}")
            if not isinstance(styling, dict):
                print(f"  ⚠️  ATTENTION: styling est un {type(styling)}, pas dict!")
                styling = {}
            else:
                print(f"  ✓ Keys: {list(styling.keys())[:5]}")
        except Exception as e:
            print(f"  ❌ ERREUR dans styling: {e}")
            styling = {}
        
        # 5. Extraire et vérifier products
        print(f"\n✓ Step 5: Extraire products")
        try:
            products = report_data.get("products", {})
            print(f"  Type: {type(products)}")
            if not isinstance(products, dict):
                print(f"  ⚠️  ATTENTION: products est un {type(products)}, pas dict!")
                print(f"  Contenu: {products}")
                products = {}
            else:
                print(f"  ✓ Keys: {list(products.keys())}")
                # Vérifier la structure de chaque catégorie
                for category in ["hauts", "bas", "robes"]:
                    if category in products:
                        cat_data = products[category]
                        print(f"    - {category}: {type(cat_data)}")
                        if isinstance(cat_data, dict):
                            print(f"      Keys: {list(cat_data.keys())}")
                            if "products" in cat_data:
                                print(f"      products type: {type(cat_data['products'])}")
                        else:
                            print(f"      ⚠️  {category} n'est pas un dict!")
        except Exception as e:
            print(f"  ❌ ERREUR dans products: {e}")
            products = {}
        
        # 6. Helper pour récupérer les produits
        print(f"\n✓ Step 6: Helper get_products_for_category")
        
        def get_products_for_category(category_name: str, products_dict: dict) -> list:
            """Récupère les produits avec logging détaillé"""
            print(f"    → get_products_for_category('{category_name}')")
            try:
                if not isinstance(products_dict, dict):
                    print(f"      ⚠️  products_dict n'est pas un dict: {type(products_dict)}")
                    return []
                
                category_data = products_dict.get(category_name, {})
                print(f"      category_data type: {type(category_data)}")
                
                if not isinstance(category_data, dict):
                    print(f"      ⚠️  category_data n'est pas un dict!")
                    return []
                
                products_list = category_data.get("products", [])
                print(f"      products_list type: {type(products_list)}")
                
                if not isinstance(products_list, list):
                    print(f"      ⚠️  products_list n'est pas une list!")
                    return []
                
                print(f"      ✓ Retourne {len(products_list)} produits")
                return products_list[:5]
            except Exception as e:
                print(f"      ❌ ERREUR: {e}")
                return []
        
        # 7. Préparer les variables
        print(f"\n✓ Step 7: Préparer les variables Liquid")
        try:
            variables = {
                "client_first_name": user_data.get("first_name", "") if isinstance(user_data, dict) else "",
                "client_last_name": user_data.get("last_name", "") if isinstance(user_data, dict) else "",
                "generation_date": datetime.now().strftime("%d %B %Y"),
                
                "colorimetry_season": colorimetry.get("season", "") if isinstance(colorimetry, dict) else "",
                "colorimetry_explanation": colorimetry.get("season_explanation", "") if isinstance(colorimetry, dict) else "",
                "palette_colors": colorimetry.get("palette_personnalisee", []) if isinstance(colorimetry, dict) else [],
                
                "body_type": morphology.get("silhouette_type", "") if isinstance(morphology, dict) else "",
                "body_explanation": morphology.get("silhouette_explanation", "") if isinstance(morphology, dict) else "",
                
                "style_archetypes": styling.get("style_archetypes", []) if isinstance(styling, dict) else [],
                "capsule_pieces": styling.get("capsule_wardrobe", []) if isinstance(styling, dict) else [],
                
                "formulas": styling.get("mix_and_match_formulas", []) if isinstance(styling, dict) else [],
                
                "products_tops": get_products_for_category("hauts", products),
                "products_bottoms": get_products_for_category("bas", products),
                "products_dresses": get_products_for_category("robes", products),
                
                "final_advice": styling.get("shopping_guide", "") if isinstance(styling, dict) else "",
            }
            
            print(f"  ✓ Variables préparées: {len(variables)} champs")
            print("="*80)
            print("✅ prepare_liquid_variables SUCCESS\n")
            return variables
            
        except Exception as e:
            print(f"  ❌ ERREUR dans création des variables: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    @staticmethod
    def map_report_to_pdfmonkey(report_data: dict, user_data: dict) -> dict:
        """Transforme un rapport généré en payload PDFMonkey"""
        return {
            "data": {
                "client_name": user_data.get("first_name", "Client"),
                "client_email": user_data.get("email", ""),
                "generation_date": datetime.now().strftime("%d/%m/%Y"),
            }
        }


# Instance globale à exporter
pdf_mapper = PDFDataMapper()