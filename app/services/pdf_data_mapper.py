"""
PDF Data Mapper - Transforme le rapport généré en payload PDFMonkey
"""

from typing import Dict, Any, Optional
from datetime import datetime


class PDFDataMapper:
    """
    Mappe les données du rapport généré au format PDFMonkey
    Transforme la structure interne en variables Liquid pour le template
    """
    
    @staticmethod
    def map_report_to_pdfmonkey(report_data: dict, user_data: dict) -> dict:
        """
        Transforme un rapport généré en payload PDFMonkey
        
        Args:
            report_data: Rapport généré par report_generator
            user_data: Données utilisateur (email, nom, measurements, etc.)
        
        Returns:
            dict: Payload prêt pour l'API PDFMonkey
        """
        
        # Extraire les sections du rapport
        colorimetry = report_data.get("colorimetry", {})
        morphology = report_data.get("morphology", {})
        styling = report_data.get("styling", {})
        visuals = report_data.get("visuals", {})
        products = report_data.get("products", {})
        
        # Mapper les données pour le template PDFMonkey
        payload = {
            "data": {
                # Données utilisateur
                "client_name": user_data.get("first_name", "Client"),
                "client_email": user_data.get("email", ""),
                "generation_date": datetime.now().strftime("%d/%m/%Y"),
                
                # Colorimétrie
                "season": colorimetry.get("season", ""),
                "season_explanation": colorimetry.get("season_explanation", ""),
                "color_palette": colorimetry.get("palette_personnalisee", []),
                "all_colors_evaluation": colorimetry.get("all_colors_evaluation", {}),
                "makeup_guide": colorimetry.get("guide_maquillage", {}),
                
                # Morphologie
                "silhouette_type": morphology.get("silhouette_type", ""),
                "silhouette_explanation": morphology.get("silhouette_explanation", ""),
                "body_analysis": morphology.get("body_analysis", {}),
                "styling_objectives": morphology.get("styling_objectives", []),
                "recommendations": morphology.get("recommendations", {}),
                
                # Styling
                "style_archetypes": styling.get("style_archetypes", []),
                "capsule_wardrobe": styling.get("capsule_wardrobe", []),
                "mix_and_match_formulas": styling.get("mix_and_match_formulas", []),
                "shopping_guide": styling.get("shopping_guide", ""),
                "occasions_styling": styling.get("occasions_styling", []),
                
                # Visuels
                "morphology_visuals": visuals.get("morphology_examples", {}),
                
                # Produits recommandés par catégorie
                "top_recommendations": products.get("hauts", {}).get("products", [])[:5],
                "bottom_recommendations": products.get("bas", {}).get("products", [])[:5],
                "dress_recommendations": products.get("robes", {}).get("products", [])[:5],
                "shoe_recommendations": products.get("chaussures", {}).get("products", [])[:5],
                "jacket_recommendations": products.get("vestes", {}).get("products", [])[:5],
            }
        }
        
        return payload
    
    @staticmethod
    def prepare_liquid_variables(report_data: dict, user_data: dict) -> dict:
        """
        Prépare les variables Liquid pour le template PDFMonkey
        Format compatible avec le template existant
        
        Args:
            report_data: Rapport complet
            user_data: Données utilisateur
        
        Returns:
            dict: Variables Liquid
        """
        
        colorimetry = report_data.get("colorimetry", {})
        morphology = report_data.get("morphology", {})
        styling = report_data.get("styling", {})
        products = report_data.get("products", {})
        
        # Préparer les variables au format Liquid
        variables = {
            # Section 1: Intro
            "client_first_name": user_data.get("first_name", ""),
            "client_last_name": user_data.get("last_name", ""),
            "generation_date": datetime.now().strftime("%d %B %Y"),
            
            # Section 2: Colorimétrie
            "colorimetry_season": colorimetry.get("season", ""),
            "colorimetry_explanation": colorimetry.get("season_explanation", ""),
            "palette_colors": colorimetry.get("palette_personnalisee", []),
            
            # Section 3: Morphologie
            "body_type": morphology.get("silhouette_type", ""),
            "body_explanation": morphology.get("silhouette_explanation", ""),
            
            # Section 4: Styling
            "style_archetypes": styling.get("style_archetypes", []),
            "capsule_pieces": styling.get("capsule_wardrobe", []),
            
            # Section 5: Mix & Match
            "formulas": styling.get("mix_and_match_formulas", []),
            
            # Section 6: Shopping
            "products_tops": products.get("hauts", {}).get("products", []),
            "products_bottoms": products.get("bas", {}).get("products", []),
            "products_dresses": products.get("robes", {}).get("products", []),
            
            # Section 7: Advice
            "final_advice": styling.get("shopping_guide", ""),
        }
        
        return variables
    
    @staticmethod
    def validate_mapping(payload: dict) -> bool:
        """
        Valide que le mapping est complet
        
        Args:
            payload: Payload à valider
        
        Returns:
            bool: True si valide
        """
        
        required_fields = [
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
        
        return True


# Instance globale à exporter
pdf_mapper = PDFDataMapper()