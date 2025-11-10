"""
PDF Data Mapper - VERSION CORRIGÉE
Mappe les données du rapport à la STRUCTURE EXACTE attendue par le template Liquid
✅ Structure imbriquée comme le template l'attend
✅ Gestion robuste des cas manquants
✅ Logs détaillés pour debug
"""

from typing import Dict, Any, Optional
from datetime import datetime
import json


class PDFDataMapper:
    """
    Mappe les données du rapport généré au format PDFMonkey (structure Liquid)
    """
    
    @staticmethod
    def _safe_dict(value: Any, default: dict = None) -> dict:
        """Convertit une valeur en dict de manière sûre"""
        if isinstance(value, dict):
            return value
        return default or {}
    
    @staticmethod
    def _safe_list(value: Any, default: list = None) -> list:
        """Convertit une valeur en liste de manière sûre"""
        if isinstance(value, list):
            return value
        return default or []
    
    @staticmethod
    def prepare_liquid_variables(report_data: dict, user_data: dict) -> dict:
        """
        ✅ FONCTION PRINCIPALE - Prépare les variables Liquid pour le template PDFMonkey
        
        Retourne une structure EXACTEMENT comme le template l'attend:
        - {{ user.firstName }} au lieu de {{ client_first_name }}
        - {{ colorimetry.season }} au lieu de {{ colorimetry_season }}
        - etc.
        
        Args:
            report_data: Les données générées par OpenAI
            user_data: Les données utilisateur (peut avoir first_name ou user_name)
        
        Returns:
            dict: Structure Liquid imbriquée comme le template l'attend
        """
        
        print("\n" + "="*70)
        print("🔧 PDF DATA MAPPER - PREPARE_LIQUID_VARIABLES")
        print("="*70)
        
        # Assurer que les sections sont des dicts
        colorimetry_raw = PDFDataMapper._safe_dict(report_data.get("colorimetry"))
        morphology_raw = PDFDataMapper._safe_dict(report_data.get("morphology"))
        styling_raw = PDFDataMapper._safe_dict(report_data.get("styling"))
        products_raw = PDFDataMapper._safe_dict(report_data.get("products"))
        makeup_raw = PDFDataMapper._safe_dict(report_data.get("makeup"))
        
        user_data = PDFDataMapper._safe_dict(user_data)
        
        print(f"\n📦 Données reçues:")
        print(f"   ✓ user_data: {len(user_data)} champs")
        print(f"   ✓ colorimetry: {len(colorimetry_raw)} champs")
        print(f"   ✓ morphology: {len(morphology_raw)} champs")
        print(f"   ✓ styling: {len(styling_raw)} champs")
        
        # ================================================================
        # EXTRAIRE ET PARSER LES DONNÉES
        # ================================================================
        
        # SECTION USER
        print(f"\n👤 Mapping user:")
        first_name = user_data.get("first_name", "")
        last_name = user_data.get("last_name", "")
        
        # Fallback: parser user_name si first_name/last_name n'existent pas
        if not first_name and not last_name:
            user_name = user_data.get("user_name", "Client")
            parts = user_name.split(" ", 1)
            first_name = parts[0] if len(parts) > 0 else "Client"
            last_name = parts[1] if len(parts) > 1 else ""
        
        print(f"   ✓ firstName: {first_name}")
        print(f"   ✓ lastName: {last_name}")
        
        # SECTION COLORIMETRY
        print(f"\n🎨 Mapping colorimetry:")
        palette = PDFDataMapper._safe_list(colorimetry_raw.get("palette_personnalisee"))
        all_colors = PDFDataMapper._safe_list(colorimetry_raw.get("all_colors_with_notes"))
        associations = PDFDataMapper._safe_list(colorimetry_raw.get("associations_gagnantes"))
        print(f"   ✓ palette: {len(palette)} couleurs")
        print(f"   ✓ all_colors: {len(all_colors)} couleurs")
        print(f"   ✓ associations: {len(associations)}")
        
        # SECTION MAKEUP
        print(f"\n💄 Mapping makeup:")
        nail_colors = PDFDataMapper._safe_list(makeup_raw.get("nail_colors", []))
        print(f"   ✓ nail_colors: {len(nail_colors)}")
        
        # SECTION MORPHOLOGY
        print(f"\n👗 Mapping morphology:")
        hauts_visuals = PDFDataMapper._safe_list(morphology_raw.get("hauts_visuals", []))
        print(f"   ✓ hauts_visuals: {len(hauts_visuals)} images")
        
        # ================================================================
        # CONSTRUIRE LA STRUCTURE LIQUID EXACTE
        # ================================================================
        
        liquid_data = {
            # ✅ SECTION: USER (structure imbriquée)
            "user": {
                "firstName": first_name,
                "lastName": last_name,
                "age": user_data.get("age", ""),
                "height": user_data.get("height", ""),
                "weight": user_data.get("weight", ""),
                "facePhotoUrl": user_data.get("face_photo_url", ""),
                "bodyPhotoUrl": user_data.get("body_photo_url", ""),
            },
            
            # ✅ SECTION: COLORIMETRY (structure imbriquée)
            "colorimetry": {
                "season": colorimetry_raw.get("season", ""),
                "seasonJustification": colorimetry_raw.get("season_justification", ""),
                "eyeColor": colorimetry_raw.get("eye_color", ""),
                "hairColor": colorimetry_raw.get("hair_color", ""),
                "palettePersonnalisee": palette,
                "allColorsWithNotes": all_colors,
                "associationsGagnantes": associations,
            },
            
            # ✅ SECTION: MAKEUP (structure imbriquée)
            "makeup": {
                "foundation": makeup_raw.get("foundation", ""),
                "blush": makeup_raw.get("blush", ""),
                "bronzer": makeup_raw.get("bronzer", ""),
                "highlighter": makeup_raw.get("highlighter", ""),
                "eyeshadows": makeup_raw.get("eyeshadows", ""),
                "eyeliner": makeup_raw.get("eyeliner", ""),
                "mascara": makeup_raw.get("mascara", ""),
                "brows": makeup_raw.get("brows", ""),
                "lipsNatural": makeup_raw.get("lips_natural", ""),
                "lipsDay": makeup_raw.get("lips_day", ""),
                "lipsEvening": makeup_raw.get("lips_evening", ""),
                "lipsAvoid": makeup_raw.get("lips_avoid", ""),
                "nailColors": nail_colors,
            },
            
            # ✅ SECTION: MORPHOLOGY_PAGE1
            "morphology_page1": {
                "bodyType": morphology_raw.get("silhouette_type", ""),
                "coherence": morphology_raw.get("silhouette_coherence", ""),
                "ratios": {
                    "waistToHips": morphology_raw.get("ratio_waist_hips", ""),
                    "waistToShoulders": morphology_raw.get("ratio_waist_shoulders", ""),
                },
                "measures": {
                    "shoulders": morphology_raw.get("measure_shoulders", ""),
                    "waist": morphology_raw.get("measure_waist", ""),
                    "hips": morphology_raw.get("measure_hips", ""),
                    "heightCm": user_data.get("height", ""),
                    "weightKg": user_data.get("weight", ""),
                },
                "comment": morphology_raw.get("objective_comment", ""),
                "goals": PDFDataMapper._safe_list(morphology_raw.get("styling_goals", [])),
                "highlights": PDFDataMapper._safe_list(morphology_raw.get("highlights", [])),
                "minimizes": PDFDataMapper._safe_list(morphology_raw.get("minimizes", [])),
                "instantTips": PDFDataMapper._safe_list(morphology_raw.get("instant_tips", [])),
                "photos": {
                    "body": user_data.get("body_photo_url", ""),
                },
            },
            
            # ✅ SECTION: MORPHO (Recommandations)
            "morpho": {
                "recos": {
                    "hauts": morphology_raw.get("hauts_recommendations", ""),
                },
                "visuels": {
                    "hauts": hauts_visuals,
                },
            },
            
            # ✅ SECTION: STYLE
            "style": {
                "archetypes": PDFDataMapper._safe_list(styling_raw.get("style_archetypes", [])),
                "primaryArchetype": PDFDataMapper._safe_list(styling_raw.get("style_archetypes", []))[0] if styling_raw.get("style_archetypes") else {},
                "essenceShort": styling_raw.get("style_essence", ""),
            },
            
            # ✅ SECTION: CAPSULE
            "capsule": {
                "basics": PDFDataMapper._safe_list(styling_raw.get("capsule_basics", [])),
                "statement": PDFDataMapper._safe_list(styling_raw.get("capsule_statement_pieces", [])),
                "totalBudget": styling_raw.get("capsule_total_budget", 0),
            },
            
            # ✅ SECTION: OUTFITS
            "outfits": PDFDataMapper._safe_list(styling_raw.get("mix_and_match_outfits", [])),
            
            # ✅ SECTION: BRANDS & OCCASIONS
            "brands": PDFDataMapper._safe_list(styling_raw.get("shopping_brands", [])),
            "occasions": PDFDataMapper._safe_list(styling_raw.get("special_occasions", [])),
            
            # ✅ SECTION: NEXT STEPS
            "nextSteps": {
                "weeklyChecklist": [
                    "Imprimez ou enregistrez ce rapport sur votre téléphone",
                    "Prenez un café avec cette palette - testez les couleurs en personne",
                    "Explorez les marques recommandées et créez votre liste de souhaits",
                    "Essayez au moins une pièce phare cette semaine",
                    "Prenez des photos de vos meilleures tenues et notez ce qui marche",
                ]
            },
            
            # ✅ METADATA
            "currentDate": datetime.now().strftime("%d %b %Y"),
        }
        
        print(f"\n✅ Structure Liquid complète assemblée:")
        for key in list(liquid_data.keys())[:5]:
            val = liquid_data[key]
            if isinstance(val, (dict, list)):
                print(f"   ✓ {key}: {type(val).__name__}")
            else:
                print(f"   ✓ {key}: {val}")
        print(f"   ... et {len(liquid_data)-5} autres sections")
        
        return liquid_data
    
    @staticmethod
    def map_report_to_pdfmonkey(report_data: dict, user_data: dict) -> dict:
        """
        ⚠️  DEPRECATED: Ancienne fonction - garder pour compatibilité
        Utiliser prepare_liquid_variables() à la place
        """
        print("⚠️  map_report_to_pdfmonkey() est dépréciée - utiliser prepare_liquid_variables()")
        return {
            "data": PDFDataMapper.prepare_liquid_variables(report_data, user_data)
        }


# Instance globale à exporter
pdf_mapper = PDFDataMapper()