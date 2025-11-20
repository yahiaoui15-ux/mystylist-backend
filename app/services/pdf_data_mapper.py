"""
PDF Data Mapper v5.0 - COMPLET & FUSIONNÉ
✅ Garde logique complète ancien (466 lignes)
✅ Ajoute displayName generation (backend, 0 tokens OpenAI)
✅ Ajoute unwanted_colors mapping + traitement
✅ COLOR_HEX_MAP global: 40+ couleurs
✅ COLOR_NAME_MAP: reverse mapping
✅ Associations enrichies avec color_details + displayName
✅ analyseColorimetriqueDetaillee INCLUSE avec impactVisuel
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json


class PDFDataMapper:
    """Mappe les données du rapport générés au format PDFMonkey (structure Liquid)"""
    
    # ✅ DISPLAY NAMES: Conversion name → displayName (accent-safe, backend only)
    DISPLAY_NAMES = {
        "rose_pale": "Rose Pâle",
        "rose_fuchsia": "Rose Fuchsia",
        "rose_corail": "Rose Corail",
        "peche": "Pêche",
        "terre_sienne": "Terre de Sienne",
        "ocre_jaune": "Ocre Jaune",
        "olive_drab": "Olive Drab",
        "brique_rouge": "Brique Rouge",
        "gris_taupe": "Gris Taupe",
        "vert_fonce": "Vert Foncé",
        "bleu_marine": "Bleu Marine",
        "cuivre": "Cuivre",
        "bronze": "Bronze",
        "chocolat": "Chocolat",
        "moutarde": "Moutarde",
        "camel": "Camel",
        "kaki": "Kaki",
        "bordeaux": "Bordeaux",
        "terracotta": "Terracotta",
    }
    
    # ✅ COLOR_HEX_MAP GLOBAL - 40+ couleurs (palette + associations + fallback)
    COLOR_HEX_MAP = {
        # PALETTE AUTOMNE
        "#E1AD01": {"name": "moutarde", "displayName": "Moutarde"},
        "#B87333": {"name": "cuivre", "displayName": "Cuivre"},
        "#808000": {"name": "olive", "displayName": "Olive"},
        "#E2725B": {"name": "terracotta", "displayName": "Terracotta"},
        "#C19A6B": {"name": "camel", "displayName": "Camel"},
        "#7B3F00": {"name": "chocolat", "displayName": "Chocolat"},
        "#6D071A": {"name": "bordeaux", "displayName": "Bordeaux"},
        "#C3B091": {"name": "kaki", "displayName": "Kaki"},
        "#CC7722": {"name": "ocre", "displayName": "Ocre"},
        "#CD7F32": {"name": "bronze", "displayName": "Bronze"},
        "#B7410E": {"name": "rouille", "displayName": "Rouille"},
        "#CB4154": {"name": "brique", "displayName": "Brique"},
        
        # COULEURS GÉNÉRIQUES
        "#FF0000": {"name": "rouge", "displayName": "Rouge"},
        "#0000FF": {"name": "bleu", "displayName": "Bleu"},
        "#FFFF00": {"name": "jaune", "displayName": "Jaune"},
        "#008000": {"name": "vert", "displayName": "Vert"},
        "#FFA500": {"name": "orange", "displayName": "Orange"},
        "#800080": {"name": "violet", "displayName": "Violet"},
        "#FFFFFF": {"name": "blanc", "displayName": "Blanc"},
        "#000000": {"name": "noir", "displayName": "Noir"},
        "#808080": {"name": "gris", "displayName": "Gris"},
        "#F5F5DC": {"name": "beige", "displayName": "Beige"},
        "#8B4513": {"name": "marron", "displayName": "Marron"},
        
        # ROSES & CORAIL
        "#FFB6C1": {"name": "rose_pale", "displayName": "Rose Pâle"},
        "#FF1493": {"name": "rose_fuchsia", "displayName": "Rose Fuchsia"},
        "#FF7F50": {"name": "rose_corail", "displayName": "Rose Corail"},
        
        # MARINES & AUTRES
        "#000080": {"name": "marine", "displayName": "Marine"},
        "#800020": {"name": "bordeaux", "displayName": "Bordeaux"},
        "#40E0D0": {"name": "turquoise", "displayName": "Turquoise"},
        
        # MOINS COURANTS
        "#D4AF76": {"name": "doré_clair", "displayName": "Doré Clair"},
        "#8B8589": {"name": "gris_taupe", "displayName": "Gris Taupe"},
        "#228B22": {"name": "vert_fonce", "displayName": "Vert Foncé"},
        "#2F4F4F": {"name": "ardoise_foncee", "displayName": "Ardoise Foncée"},
        "#D4A574": {"name": "tan_chaud", "displayName": "Tan Chaud"},
        "#A0522D": {"name": "sienne", "displayName": "Sienne"},
        "#708090": {"name": "ardoise", "displayName": "Ardoise"},
        "#CD853F": {"name": "perou", "displayName": "Pérou"},
        "#DEB887": {"name": "burlywood", "displayName": "Burlywood"},
        "#F4A460": {"name": "orange_sable", "displayName": "Orange Sablé"},
    }
    
    # ✅ REVERSE MAPPING: name → hex (pour chercher par nom)
    COLOR_NAME_MAP = {
        color_info["name"]: hex_code
        for hex_code, color_info in COLOR_HEX_MAP.items()
    }
    
    @staticmethod
    def generate_display_name(color_name: str) -> str:
        """Génère displayName depuis name OpenAI"""
        if not color_name:
            return ""
        
        # Vérifier mapping custom
        if color_name.lower() in PDFDataMapper.DISPLAY_NAMES:
            return PDFDataMapper.DISPLAY_NAMES[color_name.lower()]
        
        # Sinon: capitaliser simple
        return color_name.title()
    
    @staticmethod
    def enrich_with_display_names(items: List[dict]) -> List[dict]:
        """Ajoute displayName à une liste de couleurs"""
        for item in items:
            if "name" in item and "displayName" not in item:
                item["displayName"] = PDFDataMapper.generate_display_name(item["name"])
        return items
    
    @staticmethod
    def _safe_dict(value: Any, default: dict = None) -> dict:
        """Convertit une valeur en dict"""
        if isinstance(value, dict):
            return value
        return default or {}
    
    @staticmethod
    def _safe_list(value: Any, default: list = None) -> list:
        """Convertit une valeur en liste"""
        if isinstance(value, list):
            return value
        return default or []
    
    @staticmethod
    def _convert_snake_to_camel(obj: Any) -> Any:
        """Convertit clés snake_case en camelCase récursivement"""
        if not isinstance(obj, dict):
            return obj
        
        def to_camel(snake_str):
            components = snake_str.split('_')
            return components[0] + ''.join(x.title() for x in components[1:])
        
        converted = {}
        for key, value in obj.items():
            camel_key = to_camel(key)
            if isinstance(value, dict):
                converted[camel_key] = PDFDataMapper._convert_snake_to_camel(value)
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                converted[camel_key] = [
                    PDFDataMapper._convert_snake_to_camel(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                converted[camel_key] = value
        
        return converted
    
    @staticmethod
    def _build_all_colors_with_notes(notes_compatibilite: dict) -> list:
        """Transforme notesCompatibilite (dict) en allColorsWithNotes (list)"""
        all_colors = []
        
        for color_name, color_data in notes_compatibilite.items():
            if isinstance(color_data, dict):
                try:
                    note = int(color_data.get("note", 0)) if isinstance(color_data.get("note"), str) else color_data.get("note", 0)
                    
                    # Chercher hex code
                    hex_code = PDFDataMapper.COLOR_NAME_MAP.get(color_name)
                    if not hex_code:
                        hex_code = "#808080"  # Fallback gris
                    
                    color_obj = {
                        "name": color_name,
                        "displayName": PDFDataMapper.generate_display_name(color_name),
                        "note": note,
                        "commentaire": color_data.get("commentaire", ""),
                        "hex": hex_code,
                    }
                    all_colors.append(color_obj)
                except Exception as e:
                    print(f"⚠️ Erreur parsing couleur {color_name}: {e}")
                    continue
        
        # Trier par note décroissante
        all_colors.sort(key=lambda x: x["note"], reverse=True)
        return all_colors
    
    @staticmethod
    def _enrich_associations_with_colors(associations: list, palette: list) -> list:
        """Enrichit associations avec color_details + displayName"""
        enriched = []
        
        for assoc in associations:
            hex_codes = assoc.get("colors", [])
            color_details = []
            
            for hex_code in hex_codes:
                # Chercher dans palette
                found = None
                for color in palette:
                    if color.get("hex") == hex_code:
                        found = {
                            "name": color.get("name", ""),
                            "displayName": color.get("displayName", PDFDataMapper.generate_display_name(color.get("name", ""))),
                            "hex": hex_code,
                        }
                        break
                
                # Fallback COLOR_HEX_MAP
                if not found and hex_code in PDFDataMapper.COLOR_HEX_MAP:
                    color_info = PDFDataMapper.COLOR_HEX_MAP[hex_code]
                    found = {
                        "name": color_info.get("name", ""),
                        "displayName": color_info.get("displayName", ""),
                        "hex": hex_code,
                    }
                
                # Ultra-fallback
                if not found:
                    found = {
                        "name": hex_code,
                        "displayName": hex_code,
                        "hex": hex_code,
                    }
                
                color_details.append(found)
            
            enriched_assoc = {
                **assoc,
                "combo": hex_codes,
                "color_details": color_details,
            }
            enriched.append(enriched_assoc)
        
        return enriched
    
    @staticmethod
    def _transform_nail_colors(nail_colors_hex: list, palette: list) -> list:
        """Transforme hex codes d'ongles en objets avec noms + displayName"""
        transformed = []
        
        for hex_code in nail_colors_hex:
            # Chercher dans palette
            found = None
            for color in palette:
                if color.get("hex") == hex_code:
                    found = {
                        "name": color.get("name", ""),
                        "displayName": color.get("displayName", ""),
                        "hex": hex_code,
                    }
                    break
            
            # Fallback COLOR_HEX_MAP
            if not found and hex_code in PDFDataMapper.COLOR_HEX_MAP:
                color_info = PDFDataMapper.COLOR_HEX_MAP[hex_code]
                found = {
                    "name": color_info.get("name", ""),
                    "displayName": color_info.get("displayName", ""),
                    "hex": hex_code,
                }
            
            # Ultra-fallback
            if not found:
                found = {
                    "name": hex_code,
                    "displayName": hex_code,
                    "hex": hex_code,
                }
            
            transformed.append(found)
        
        return transformed
    
    @staticmethod
    def prepare_liquid_variables(report_data: dict, user_data: dict) -> dict:
        """Prépare variables Liquid pour PDFMonkey"""
        
        colorimetry_raw = PDFDataMapper._safe_dict(report_data.get("colorimetry", {}))
        morphology_raw = PDFDataMapper._safe_dict(report_data.get("morphology", {}))
        styling_raw = PDFDataMapper._safe_dict(report_data.get("styling", {}))
        
        # ════════════════════════════════════════════════════════════
        # COLORIMETRY - Enrichir displayName + unwanted_colors
        # ════════════════════════════════════════════════════════════
        palette = PDFDataMapper._safe_list(colorimetry_raw.get("palette_personnalisee", []))
        palette = PDFDataMapper.enrich_with_display_names(palette)
        
        notes_compatibilite = PDFDataMapper._safe_dict(colorimetry_raw.get("notes_compatibilite", {}))
        all_colors_with_notes = PDFDataMapper._build_all_colors_with_notes(notes_compatibilite)
        
        associations = PDFDataMapper._safe_list(colorimetry_raw.get("associations_gagnantes", []))
        associations = PDFDataMapper._enrich_associations_with_colors(associations, palette)
        
        # ✅ NOUVEAU: Unwanted colors
        unwanted_colors = PDFDataMapper._safe_list(colorimetry_raw.get("unwanted_colors", []))
        unwanted_colors = PDFDataMapper.enrich_with_display_names(unwanted_colors)
        
        alternatives = PDFDataMapper._safe_dict(colorimetry_raw.get("alternatives_couleurs_refusees", {}))
        
        # ════════════════════════════════════════════════════════════
        # MAKEUP - Depuis colorimetry.guide_maquillage
        # ════════════════════════════════════════════════════════════
        guide_maquillage_raw = PDFDataMapper._safe_dict(colorimetry_raw.get("guide_maquillage", {}))
        shopping_raw = PDFDataMapper._safe_dict(colorimetry_raw.get("shopping_couleurs", {}))
        
        # Transform nailColors
        raw_nail_colors = PDFDataMapper._safe_list(guide_maquillage_raw.get("vernis_a_ongles", []))
        nail_colors_transformed = PDFDataMapper._transform_nail_colors(raw_nail_colors, palette)
        
        # Map keys exactes attendues par template
        makeup_mapping = {
            "foundation": guide_maquillage_raw.get("teint", ""),
            "blush": guide_maquillage_raw.get("blush", ""),
            "bronzer": guide_maquillage_raw.get("bronzer", ""),
            "highlighter": guide_maquillage_raw.get("highlighter", ""),
            "eyeshadows": guide_maquillage_raw.get("eyeshadows", ""),
            "eyeliner": guide_maquillage_raw.get("eyeliner", ""),
            "mascara": guide_maquillage_raw.get("mascara", ""),
            "brows": guide_maquillage_raw.get("brows", ""),
            "lipsNatural": guide_maquillage_raw.get("lipsNatural", ""),
            "lipsDay": guide_maquillage_raw.get("lipsDay", ""),
            "lipsEvening": guide_maquillage_raw.get("lipsEvening", ""),
            "lipsAvoid": guide_maquillage_raw.get("lipsAvoid", ""),
            "nailColors": nail_colors_transformed,
        }
        
        # ════════════════════════════════════════════════════════════
        # ANALYSE COLORIMETRIQUE (snake_case → camelCase)
        # ════════════════════════════════════════════════════════════
        analyse_raw = PDFDataMapper._safe_dict(colorimetry_raw.get("analyse_colorimetrique_detaillee", {}))
        analyse_camel = PDFDataMapper._convert_snake_to_camel(analyse_raw)
        impact_visuel_raw = PDFDataMapper._safe_dict(analyse_raw.get("impact_visuel", {}))
        analyse_camel["impactVisuel"] = PDFDataMapper._convert_snake_to_camel(impact_visuel_raw)
        
        # ════════════════════════════════════════════════════════════
        # MORPHOLOGY
        # ════════════════════════════════════════════════════════════
        hauts_visuals = PDFDataMapper._safe_list(morphology_raw.get("hauts_visuals", []))
        
        priorite_1 = PDFDataMapper._safe_list(shopping_raw.get("priorite_1", []))
        priorite_2 = PDFDataMapper._safe_list(shopping_raw.get("priorite_2", []))
        eviter = PDFDataMapper._safe_list(shopping_raw.get("eviter_absolument", []))
        
        # ════════════════════════════════════════════════════════════
        # CONSTRUIRE STRUCTURE LIQUID
        # ════════════════════════════════════════════════════════════
        
        liquid_data = {
            "user": {
                "firstName": user_data.get("first_name", ""),
                "lastName": user_data.get("last_name", ""),
                "age": user_data.get("age", ""),
                "height": user_data.get("height", ""),
                "weight": user_data.get("weight", ""),
                "facePhotoUrl": user_data.get("face_photo_url", ""),
                "bodyPhotoUrl": user_data.get("body_photo_url", ""),
            },
            
            "colorimetry": {
                "season": colorimetry_raw.get("saison_confirmee", ""),
                "soustonDetecte": colorimetry_raw.get("sous_ton_detecte", ""),
                "seasonJustification": colorimetry_raw.get("justification_saison", ""),
                "eyeColor": colorimetry_raw.get("eye_color", ""),
                "hairColor": colorimetry_raw.get("hair_color", ""),
                "palettePersonnalisee": palette,
                "notesCompatibilite": notes_compatibilite,
                "allColorsWithNotes": all_colors_with_notes,
                "unwantedColors": unwanted_colors,  # ✅ NOUVEAU
                "alternativesCouleurs": alternatives,
                "associationsGagnantes": associations,
                "analyseColorimetriqueDetaillee": analyse_camel,
            },
            
            "makeup": makeup_mapping,
            
            "shopping": {
                "priorite1": priorite_1,
                "priorite2": priorite_2,
                "eviterAbsolument": eviter,
            },
            
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
            
            "morpho": {
                "recos": {
                    "hauts": morphology_raw.get("hauts_recommendations", ""),
                },
                "visuels": {
                    "hauts": hauts_visuals,
                },
            },
            
            "style": {
                "archetypes": PDFDataMapper._safe_list(styling_raw.get("style_archetypes", [])),
                "primaryArchetype": PDFDataMapper._safe_list(styling_raw.get("style_archetypes", []))[0] if styling_raw.get("style_archetypes") else {},
                "essenceShort": styling_raw.get("style_essence", ""),
            },
            
            "capsule": {
                "basics": PDFDataMapper._safe_list(styling_raw.get("capsule_basics", [])),
                "statement": PDFDataMapper._safe_list(styling_raw.get("capsule_statement_pieces", [])),
                "totalBudget": styling_raw.get("capsule_total_budget", 0),
            },
            
            "outfits": PDFDataMapper._safe_list(styling_raw.get("mix_and_match_outfits", [])),
            "brands": PDFDataMapper._safe_list(styling_raw.get("shopping_brands", [])),
            "occasions": PDFDataMapper._safe_list(styling_raw.get("special_occasions", [])),
            
            "nextSteps": {
                "weeklyChecklist": [
                    "Imprimez ou enregistrez ce rapport sur votre téléphone",
                    "Prenez un café avec cette palette - testez les couleurs en personne",
                    "Explorez les marques recommandées et créez votre liste de souhaits",
                    "Essayez au moins une pièce phare cette semaine",
                    "Prenez des photos de vos meilleures tenues et notez ce qui marche",
                ]
            },
            
            "currentDate": datetime.now().strftime("%d %b %Y"),
        }
        
        print(f"✅ Mapper v5.0 complet:")
        print(f"   ✓ Palette: {len(palette)} + displayName")
        print(f"   ✓ Associations: {len(associations)} enrichies")
        print(f"   ✓ Unwanted colors: {len(unwanted_colors)} traitées")
        print(f"   ✓ Ongles: {len(nail_colors_transformed)} détaillés")
        print(f"   ✓ Analyse: camelCase + impactVisuel")
        
        return liquid_data
    
    @staticmethod
    def map_report_to_pdfmonkey(report_data: dict, user_data: dict) -> dict:
        """Wrapper compatibilité"""
        return {
            "data": PDFDataMapper.prepare_liquid_variables(report_data, user_data)
        }


pdf_mapper = PDFDataMapper()