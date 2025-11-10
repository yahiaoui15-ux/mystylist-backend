"""
PDF Data Mapper - VERSION CORRIGÉE ET ROBUSTE
Accepte à la fois des listes et des dicts pour chaque section
Avec logs détaillés pour diagnostic
"""

from typing import Dict, Any, Optional, Union
from datetime import datetime


class PDFDataMapper:
    """
    Mappe les données du rapport généré au format PDFMonkey
    VERSION CORRIGÉE: Gère les données manquantes et logs détaillés
    """
    
    @staticmethod
    def _ensure_dict(value: Any, default: dict = None) -> dict:
        """
        Convertit une liste ou n'importe quoi en dict
        Si c'est une liste, retourne {}
        Si c'est un dict, retourne le dict
        Sinon retourne {}
        """
        if value is None:
            return default or {}
        if isinstance(value, dict):
            return value
        # Si c'est une liste ou autre, retourner {}
        return default or {}
    
    @staticmethod
    def _ensure_list(value: Any, default: list = None) -> list:
        """
        Convertit n'importe quoi en liste
        Si c'est déjà une liste, retourne la liste
        Sinon retourne []
        """
        if value is None:
            return default or []
        if isinstance(value, list):
            return value
        # Si c'est autre chose, retourner []
        return default or []
    
    @staticmethod
    def prepare_liquid_variables(report_data: dict, user_data: dict) -> dict:
        """
        Prépare les variables Liquid pour le template PDFMonkey
        VERSION CORRIGÉE: Utilise first_name et last_name correctement
        
        🔧 CORRECTION: user_data doit avoir first_name et last_name
        """
        
        print("\n✅ prepare_liquid_variables (CORRECTED VERSION)")
        print(f"📌 user_data keys: {list(user_data.keys())[:10]}...")
        
        # Extraire les sections - peut être liste ou dict
        colorimetry = PDFDataMapper._ensure_dict(report_data.get("colorimetry"))
        morphology = PDFDataMapper._ensure_dict(report_data.get("morphology"))
        styling = PDFDataMapper._ensure_dict(report_data.get("styling"))
        products = PDFDataMapper._ensure_dict(report_data.get("products"))
        visuals = PDFDataMapper._ensure_dict(report_data.get("visuals"))
        
        print(f"   colorimetry: {type(report_data.get('colorimetry')).__name__} → dict ✓")
        print(f"   morphology: {type(report_data.get('morphology')).__name__} → dict ✓")
        print(f"   styling: {type(report_data.get('styling')).__name__} → dict ✓")
        print(f"   products: {type(report_data.get('products')).__name__} → dict ✓")
        print(f"   visuals: {type(report_data.get('visuals')).__name__} → dict ✓")
        
        # Helper pour récupérer les produits d'une catégorie
        def get_products_for_category(category_name: str, products_dict: dict) -> list:
            """Récupère les produits d'une catégorie de manière sûre"""
            try:
                # products_dict est maintenant garanti être un dict
                category_data = products_dict.get(category_name, {})
                
                # category_data peut être dict ou liste
                if isinstance(category_data, dict):
                    products_list = category_data.get("products", [])
                    products_list = PDFDataMapper._ensure_list(products_list)
                    return products_list[:5]
                elif isinstance(category_data, list):
                    # Si c'est directement une liste, retourner les 5 premiers
                    return category_data[:5]
                else:
                    return []
            except Exception as e:
                print(f"   ⚠️ {category_name}: {e}")
                return []
        
        # 🔧 CORRECTION: Récupérer correctement first_name et last_name
        first_name = ""
        last_name = ""
        
        if isinstance(user_data, dict):
            # ✅ Essayer d'abord les champs directs (from corrected main.py)
            first_name = user_data.get("first_name", "")
            last_name = user_data.get("last_name", "")
            
            # 🔧 Fallback: parser user_name si champs séparés n'existent pas
            if not first_name and not last_name:
                user_name = user_data.get("user_name", "Client")
                parts = user_name.split(" ", 1)
                first_name = parts[0] if len(parts) > 0 else "Client"
                last_name = parts[1] if len(parts) > 1 else ""
        
        print(f"   👤 user_data name: first_name='{first_name}', last_name='{last_name}'")
        
        # Préparer les variables au format Liquid
        variables = {
            # Section 1: Intro
            "client_first_name": first_name if first_name else "Client",  # ← CORRIGÉ
            "client_last_name": last_name,  # ← CORRIGÉ
            "generation_date": datetime.now().strftime("%d %B %Y"),
            
            # Section 2: Colorimétrie
            "colorimetry_season": colorimetry.get("season", ""),
            "colorimetry_explanation": colorimetry.get("season_explanation", ""),
            "palette_colors": PDFDataMapper._ensure_list(colorimetry.get("palette_personnalisee")),
            
            # Section 3: Morphologie
            "body_type": morphology.get("silhouette_type", ""),
            "body_explanation": morphology.get("silhouette_explanation", ""),
            
            # Section 4: Styling
            "style_archetypes": PDFDataMapper._ensure_list(styling.get("style_archetypes")),
            "capsule_pieces": PDFDataMapper._ensure_list(styling.get("capsule_wardrobe")),
            
            # Section 5: Mix & Match
            "formulas": PDFDataMapper._ensure_list(styling.get("mix_and_match_formulas")),
            
            # Section 6: Shopping (utiliser la fonction helper)
            "products_tops": get_products_for_category("hauts", products),
            "products_bottoms": get_products_for_category("bas", products),
            "products_dresses": get_products_for_category("robes", products),
            
            # Section 7: Advice
            "final_advice": styling.get("shopping_guide", ""),
        }
        
        print(f"   ✅ Variables Liquid préparées: {len(variables)} champs")
        print(f"      - client_first_name: '{variables['client_first_name']}'")  # ← LOG POUR VÉRIFIER
        print(f"      - client_last_name: '{variables['client_last_name']}'")   # ← LOG POUR VÉRIFIER
        
        return variables
    
    @staticmethod
    def map_report_to_pdfmonkey(report_data: dict, user_data: dict) -> dict:
        """Transforme un rapport généré en payload PDFMonkey"""
        
        print("\n🔧 map_report_to_pdfmonkey")
        
        colorimetry = PDFDataMapper._ensure_dict(report_data.get("colorimetry"))
        morphology = PDFDataMapper._ensure_dict(report_data.get("morphology"))
        styling = PDFDataMapper._ensure_dict(report_data.get("styling"))
        products = PDFDataMapper._ensure_dict(report_data.get("products"))
        
        # 🔧 CORRECTION: Récupérer first_name et last_name correctement
        first_name = user_data.get("first_name", "Client") if isinstance(user_data, dict) else "Client"
        last_name = user_data.get("last_name", "") if isinstance(user_data, dict) else ""
        
        payload = {
            "data": {
                "client_first_name": first_name,  # ← CORRIGÉ
                "client_last_name": last_name,    # ← CORRIGÉ
                "client_name": f"{first_name} {last_name}".strip(),
                "client_email": user_data.get("user_email", "") if isinstance(user_data, dict) else "",
                "generation_date": datetime.now().strftime("%d/%m/%Y"),
                "season": colorimetry.get("season", ""),
                "silhouette_type": morphology.get("silhouette_type", ""),
            }
        }
        
        print(f"   client_first_name: {payload['data']['client_first_name']}")  # ← LOG
        print(f"   client_last_name: {payload['data']['client_last_name']}")    # ← LOG
        
        return payload
    
    @staticmethod
    def validate_mapping(payload: dict) -> bool:
        """Valide que le mapping est complet"""
        required_fields = [
            "data.client_first_name",  # ← AJOUTÉ
            "data.client_last_name",   # ← AJOUTÉ
            "data.client_name",
            "data.season",
            "data.silhouette_type"
        ]
        
        for field in required_fields:
            parts = field.split(".")
            current = payload
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    print(f"⚠️ Champ manquant: {field}")
                    return False
        
        print(f"✅ Validation: tous les champs requis sont présents")
        return True


# Instance globale à exporter
pdf_mapper = PDFDataMapper()