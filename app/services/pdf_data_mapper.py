"""
PDF Data Mapper - VERSION 3 AMÉLIORÉE
✅ Guide_maquillage extrait depuis colorimetry (pas niveau racine)
✅ Mapping des clés Liquid EXACT: teint→foundation, yeux→eyeshadows, lipsNude→lipsNatural
✅ Associations: enrichies avec color_details (noms des couleurs)
✅ Shopping_couleurs extrait depuis colorimetry
✅ nailColors: transformés de hex codes à [{hex, name}, ...]
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json


class PDFDataMapper:
    """
    Mappe les données du rapport généré au format PDFMonkey (structure Liquid)
    """
    
    # Mapping des noms de couleurs français → hex codes
    COLOR_HEX_MAP = {
        "rouge": "#FF0000",
        "bleu": "#0000FF",
        "jaune": "#FFFF00",
        "vert": "#008000",
        "orange": "#FFA500",
        "violet": "#800080",
        "blanc": "#FFFFFF",
        "noir": "#000000",
        "gris": "#808080",
        "beige": "#F5F5DC",
        "marron": "#8B4513",
        "rose_pale": "#FFB6C1",
        "rose_fuchsia": "#FF1493",
        "rose_corail": "#FF7F50",
        "camel": "#C19A6B",
        "marine": "#000080",
        "bordeaux": "#800020",
        "kaki": "#C3B091",
        "turquoise": "#40E0D0",
    }
    
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
    def _build_all_colors_with_notes(notes_compatibilite: dict) -> list:
        """
        Transforme notesCompatibilite (dict) en allColorsWithNotes (list)
        avec hex codes pour chaque couleur
        """
        all_colors = []
        
        for color_name, color_data in notes_compatibilite.items():
            if isinstance(color_data, dict):
                try:
                    note = int(color_data.get("note", 0)) if isinstance(color_data.get("note"), str) else color_data.get("note", 0)
                except (ValueError, TypeError):
                    note = 0
                
                hex_code = PDFDataMapper.COLOR_HEX_MAP.get(color_name, "#CCCCCC")
                
                all_colors.append({
                    "name": color_name,
                    "note": note,
                    "commentaire": color_data.get("commentaire", ""),
                    "hex": hex_code
                })
        
        all_colors.sort(key=lambda x: x["note"], reverse=True)
        return all_colors
    
    @staticmethod
    def _create_hex_to_color_map(palette: list) -> Dict[str, Dict[str, str]]:
        """
        Crée un mapping hex → {name, displayName} depuis palette_personnalisee
        
        Exemple:
        {
            "#C19A6B": {"name": "camel", "displayName": "Camel"},
            "#E2725B": {"name": "terracotta", "displayName": "Terracotta"},
            ...
        }
        """
        hex_map = {}
        for color in palette:
            if isinstance(color, dict) and "hex" in color:
                hex_code = color["hex"].upper()
                hex_map[hex_code] = {
                    "name": color.get("name", ""),
                    "displayName": color.get("displayName", ""),
                    "hex": hex_code
                }
        
        print(f"\n   🔍 Hex→Name mapping créé: {len(hex_map)} couleurs")
        return hex_map
    
    @staticmethod
    def _enrich_associations_with_color_names(associations: list, palette: list) -> list:
        """
        Enrichit les associations avec color_details (noms des couleurs)
        
        INPUT:
        [
            {
                "occasion": "professionnel",
                "colors": ["#C19A6B", "#E2725B", "#000080"],
                "effet": "Élégance autorité"
            }
        ]
        
        OUTPUT:
        [
            {
                "occasion": "professionnel",
                "colors": ["#C19A6B", "#E2725B", "#000080"],
                "combo": ["#C19A6B", "#E2725B", "#000080"],
                "color_details": [
                    {"hex": "#C19A6B", "name": "camel", "displayName": "Camel"},
                    {"hex": "#E2725B", "name": "terracotta", "displayName": "Terracotta"},
                    ...
                ],
                "effet": "Élégance autorité"
            }
        ]
        """
        
        # Créer le mapping hex → {name, displayName}
        hex_map = PDFDataMapper._create_hex_to_color_map(palette)
        
        enriched_associations = []
        
        for assoc in associations:
            if not isinstance(assoc, dict):
                enriched_associations.append(assoc)
                continue
            
            # Récupérer les couleurs (key "colors" d'OpenAI)
            colors_list = assoc.get("colors", [])
            
            # Enrichir avec les noms
            color_details = []
            for hex_code in colors_list:
                # Normaliser le hex code (uppercase)
                hex_upper = hex_code.upper() if isinstance(hex_code, str) else ""
                
                # Chercher dans le mapping
                if hex_upper in hex_map:
                    color_details.append(hex_map[hex_upper])
                else:
                    # Fallback: créer une entrée minimale
                    color_details.append({
                        "hex": hex_code,
                        "name": "couleur",
                        "displayName": "Couleur"
                    })
            
            # Construire l'association enrichie
            enriched_assoc = {
                **assoc,
                "combo": colors_list,  # Garder combo pour compatibilité
                "color_details": color_details  # Ajouter les détails avec noms
            }
            
            enriched_associations.append(enriched_assoc)
        
        print(f"   ✅ {len(enriched_associations)} associations enrichies avec color_details")
        return enriched_associations
    
    @staticmethod
    def _transform_nail_colors(nail_hex_list: list, palette: list) -> list:
        """
        Transforme les codes hex des ongles en [{hex, name, displayName}, ...]
        
        INPUT: ["#E1AD01", "#7B3F00", "#CC7722", "#6D071A", "#CD7F32"]
        OUTPUT: [
            {"hex": "#E1AD01", "name": "moutarde", "displayName": "Moutarde"},
            {"hex": "#7B3F00", "name": "chocolat", "displayName": "Chocolat"},
            ...
        ]
        """
        
        if not nail_hex_list:
            return []
        
        # Créer le mapping hex → {name, displayName}
        hex_map = PDFDataMapper._create_hex_to_color_map(palette)
        
        nail_colors_detailed = []
        
        for hex_code in nail_hex_list:
            hex_upper = hex_code.upper() if isinstance(hex_code, str) else ""
            
            if hex_upper in hex_map:
                nail_colors_detailed.append(hex_map[hex_upper])
            else:
                # Fallback
                nail_colors_detailed.append({
                    "hex": hex_code,
                    "name": "couleur",
                    "displayName": "Couleur"
                })
        
        print(f"   ✅ {len(nail_colors_detailed)} couleurs d'ongles transformées")
        return nail_colors_detailed
    
    @staticmethod
    def prepare_liquid_variables(report_data: dict, user_data: dict) -> dict:
        """
        ✅ FONCTION PRINCIPALE - Prépare les variables Liquid pour le template PDFMonkey
        
        CORRECTIONS APPORTÉES:
        1. guide_maquillage extrait depuis colorimetry (pas niveau racine)
        2. Mapping exact des clés Liquid pour le makeup
        3. Associations: enrichies avec color_details (noms des couleurs) ✨
        4. Shopping_couleurs extrait depuis colorimetry
        5. nailColors: transformés de hex codes à [{hex, name}, ...] ✨
        """
        
        print("\n" + "="*70)
        print("🔧 PDF DATA MAPPER - PREPARE_LIQUID_VARIABLES (v3)")
        print("="*70)
        
        # ✅ CORRECTION: Extraire depuis colorimetry_raw
        colorimetry_raw = PDFDataMapper._safe_dict(report_data.get("colorimetry"))
        morphology_raw = PDFDataMapper._safe_dict(report_data.get("morphology"))
        styling_raw = PDFDataMapper._safe_dict(report_data.get("styling"))
        products_raw = PDFDataMapper._safe_dict(report_data.get("products"))
        
        # ✅ CORRECTION: guide_maquillage et shopping_couleurs DANS colorimetry_raw
        guide_maquillage_raw = PDFDataMapper._safe_dict(colorimetry_raw.get("guide_maquillage", {}))
        shopping_raw = PDFDataMapper._safe_dict(colorimetry_raw.get("shopping_couleurs", {}))
        
        user_data = PDFDataMapper._safe_dict(user_data)
        
        print(f"\n📦 Données reçues:")
        print(f"   ✓ user_data: {len(user_data)} champs")
        print(f"   ✓ colorimetry: {len(colorimetry_raw)} champs")
        print(f"   ✓ guide_maquillage: {len(guide_maquillage_raw)} champs")
        print(f"   ✓ shopping_couleurs: {len(shopping_raw)} champs")
        
        # ================================================================
        # SECTION USER
        # ================================================================
        print(f"\n👤 Mapping user:")
        first_name = user_data.get("first_name", "")
        last_name = user_data.get("last_name", "")
        
        if not first_name and not last_name:
            user_name = user_data.get("user_name", "Client")
            parts = user_name.split(" ", 1)
            first_name = parts[0] if len(parts) > 0 else "Client"
            last_name = parts[1] if len(parts) > 1 else ""
        
        print(f"   ✓ firstName: {first_name}")
        print(f"   ✓ lastName: {last_name}")
        
        # ================================================================
        # SECTION COLORIMETRY
        # ================================================================
        print(f"\n🎨 Mapping colorimetry:")
        palette = PDFDataMapper._safe_list(colorimetry_raw.get("palette_personnalisee"))
        notes_compatibilite = PDFDataMapper._safe_dict(colorimetry_raw.get("notes_compatibilite"))
        
        # ✅ NEW: Enrichir les associations avec les noms des couleurs
        print(f"\n✨ Enrichissement des associations:")
        raw_associations = PDFDataMapper._safe_list(colorimetry_raw.get("associations_gagnantes"))
        associations = PDFDataMapper._enrich_associations_with_color_names(raw_associations, palette)
        
        alternatives = PDFDataMapper._safe_dict(colorimetry_raw.get("alternatives_couleurs_refusees"))
        
        all_colors_with_notes = PDFDataMapper._build_all_colors_with_notes(notes_compatibilite)
        
        print(f"   ✓ palette: {len(palette)} couleurs")
        print(f"   ✓ notes_compatibilite: {len(notes_compatibilite)} couleurs")
        print(f"   ✓ allColorsWithNotes: {len(all_colors_with_notes)} couleurs")
        print(f"   ✓ associations: {len(associations)}")
        print(f"   ✓ alternatives: {len(alternatives)}")
        
        # ================================================================
        # SECTION MAKEUP
        # ================================================================
        print(f"\n💄 Mapping makeup (CLÉS CORRIGÉES):")
        
        # ✅ NEW: Transformer nailColors de hex codes à [{hex, name}, ...]
        raw_nail_colors = PDFDataMapper._safe_list(guide_maquillage_raw.get("vernis_a_ongles", []))
        print(f"\n💅 Transformation ongles:")
        nail_colors_transformed = PDFDataMapper._transform_nail_colors(raw_nail_colors, palette)
        
        # ✅ CORRECTION: Mapper les clés EXACTES attendues par le template
        makeup_mapping = {
            "foundation": guide_maquillage_raw.get("teint", ""),        # ← teint → foundation
            "blush": guide_maquillage_raw.get("blush", ""),
            "bronzer": guide_maquillage_raw.get("bronzer", ""),
            "highlighter": guide_maquillage_raw.get("highlighter", ""),
            "eyeshadows": guide_maquillage_raw.get("yeux", ""),         # ← yeux → eyeshadows
            "eyeliner": guide_maquillage_raw.get("eyeliner", ""),
            "mascara": guide_maquillage_raw.get("mascara", ""),
            "brows": guide_maquillage_raw.get("brows", ""),
            "lipsNatural": guide_maquillage_raw.get("lipsNude", ""),    # ← lipsNude → lipsNatural
            "lipsDay": guide_maquillage_raw.get("lipsDay", ""),
            "lipsEvening": guide_maquillage_raw.get("lipsEvening", ""),
            "lipsAvoid": guide_maquillage_raw.get("lipsAvoid", ""),
            "nailColors": nail_colors_transformed,  # ✨ Maintenant des [{hex, name}, ...]
        }
        print(f"   ✓ foundation: {bool(makeup_mapping['foundation'])}")
        print(f"   ✓ eyeshadows: {bool(makeup_mapping['eyeshadows'])}")
        print(f"   ✓ lipsNatural: {bool(makeup_mapping['lipsNatural'])}")
        print(f"   ✓ nailColors: {len(makeup_mapping['nailColors'])} (transformés)")
        
        # ================================================================
        # SECTION SHOPPING
        # ================================================================
        print(f"\n🛍️  Mapping shopping_couleurs:")
        priorite_1 = PDFDataMapper._safe_list(shopping_raw.get("priorite_1"))
        priorite_2 = PDFDataMapper._safe_list(shopping_raw.get("priorite_2"))
        eviter = PDFDataMapper._safe_list(shopping_raw.get("eviter_absolument"))
        print(f"   ✓ priorite_1: {len(priorite_1)}")
        print(f"   ✓ priorite_2: {len(priorite_2)}")
        print(f"   ✓ eviter_absolument: {len(eviter)}")
        
        # ================================================================
        # SECTION MORPHOLOGY
        # ================================================================
        print(f"\n👗 Mapping morphology:")
        hauts_visuals = PDFDataMapper._safe_list(morphology_raw.get("hauts_visuals", []))
        print(f"   ✓ hauts_visuals: {len(hauts_visuals)} images")
        
        # ================================================================
        # CONSTRUIRE LA STRUCTURE LIQUID EXACTE
        # ================================================================
        
        liquid_data = {
            # ✅ SECTION: USER
            "user": {
                "firstName": first_name,
                "lastName": last_name,
                "age": user_data.get("age", ""),
                "height": user_data.get("height", ""),
                "weight": user_data.get("weight", ""),
                "facePhotoUrl": user_data.get("face_photo_url", ""),
                "bodyPhotoUrl": user_data.get("body_photo_url", ""),
            },
            
            # ✅ SECTION: COLORIMETRY
            "colorimetry": {
                "season": colorimetry_raw.get("saison_confirmee", ""),
                "soustonDetecte": colorimetry_raw.get("sous_ton_detecte", ""),
                "seasonJustification": colorimetry_raw.get("justification_saison", ""),
                "eyeColor": colorimetry_raw.get("eye_color", ""),
                "hairColor": colorimetry_raw.get("hair_color", ""),
                "palettePersonnalisee": palette,
                "notesCompatibilite": notes_compatibilite,
                "allColorsWithNotes": all_colors_with_notes,
                "alternativesCouleurs": alternatives,
                "associationsGagnantes": associations,  # ✨ Enrichies avec color_details
            },
            
            # ✅ SECTION: MAKEUP (CLÉS CORRIGÉES)
            "makeup": makeup_mapping,
            
            # ✅ SECTION: SHOPPING COULEURS
            "shopping": {
                "priorite1": priorite_1,
                "priorite2": priorite_2,
                "eviterAbsolument": eviter,
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
            
            # ✅ SECTION: MORPHO
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
        
        print(f"\n✅ Structure Liquid assemblée (v3 AMÉLIORÉE)")
        print(f"   ✓ Associations enrichies: {len(associations)} avec color_details")
        print(f"   ✓ Ongles transformés: {len(nail_colors_transformed)} couleurs détaillées")
        
        return liquid_data
    
    @staticmethod
    def map_report_to_pdfmonkey(report_data: dict, user_data: dict) -> dict:
        """Wrapper pour compatibilité"""
        return {
            "data": PDFDataMapper.prepare_liquid_variables(report_data, user_data)
        }


# Instance globale
pdf_mapper = PDFDataMapper()