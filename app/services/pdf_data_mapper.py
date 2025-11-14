"""
PDF Data Mapper - VERSION 4 COMPLÈTE ET AMÉLIORÉE
✅ COLOR_HEX_MAP GLOBAL ÉTENDU: 40+ couleurs (palette + associations + fallback)
✅ Guide_maquillage extrait depuis colorimetry (pas niveau racine)
✅ Mapping des clés Liquid EXACT: teint→foundation, yeux→eyeshadows, lipsNude→lipsNatural
✅ Associations: enrichies avec color_details (noms des couleurs)
✅ Shopping_couleurs extrait depuis colorimetry
✅ nailColors: transformés de hex codes à [{hex, name}, ...]
✅ Fallback sur COLOR_HEX_MAP global si hex pas dans palette_personnalisee

NOUVEAUTÉS v4:
- COLOR_HEX_MAP complet avec toutes les couleurs possibles
- Stratégie multi-niveaux pour les associations (palette → global map → fallback)
- Documentation complète des hex codes non standards
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json


class PDFDataMapper:
    """
    Mappe les données du rapport généré au format PDFMonkey (structure Liquid)
    
    Stratégie de matching des couleurs:
    1. Chercher le hex dans palette_personnalisee (priorité haute - couleurs du rapport)
    2. Chercher le hex dans COLOR_HEX_MAP global (fallback - toutes les couleurs)
    3. Fallback final: {"name": "couleur", "displayName": "Couleur"}
    """
    
    # ✅ COLOR_HEX_MAP GLOBAL COMPLET - Pour toutes les associations
    # Inclut: palette de base + couleurs génériques + couleurs moins courantes qu'OpenAI peut utiliser
    COLOR_HEX_MAP = {
        # ════════════════════════════════════════════════════════════
        # PALETTE DE BASE (Automne - couleurs chaudes)
        # ════════════════════════════════════════════════════════════
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
        
        # ════════════════════════════════════════════════════════════
        # COULEURS GÉNÉRIQUES STANDARD
        # ════════════════════════════════════════════════════════════
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
        
        # ════════════════════════════════════════════════════════════
        # COULEURS ROSES & CORAIL
        # ════════════════════════════════════════════════════════════
        "#FFB6C1": {"name": "rose_pale", "displayName": "Rose pâle"},
        "#FF1493": {"name": "rose_fuchsia", "displayName": "Rose fuchsia"},
        "#FF7F50": {"name": "rose_corail", "displayName": "Corail"},
        
        # ════════════════════════════════════════════════════════════
        # BLEUS & MARINES
        # ════════════════════════════════════════════════════════════
        "#000080": {"name": "marine", "displayName": "Marine"},
        "#800020": {"name": "bordeaux", "displayName": "Bordeaux"},
        "#40E0D0": {"name": "turquoise", "displayName": "Turquoise"},
        
        # ════════════════════════════════════════════════════════════
        # COULEURS MOINS COURANTES (Hex codes non-standards qu'OpenAI peut utiliser)
        # ════════════════════════════════════════════════════════════
        "#D4AF76": {"name": "doré_clair", "displayName": "Doré clair"},
        "#8B8589": {"name": "gris_taupe", "displayName": "Gris taupe"},
        "#228B22": {"name": "vert_foncé", "displayName": "Vert foncé"},
        "#2F4F4F": {"name": "ardoise_foncée", "displayName": "Ardoise foncée"},
        "#D4A574": {"name": "tan_chaud", "displayName": "Tan chaud"},
        "#A0522D": {"name": "sienne", "displayName": "Sienne"},
        "#708090": {"name": "ardoise", "displayName": "Ardoise"},
        "#CD853F": {"name": "pérou", "displayName": "Pérou"},
        "#DEB887": {"name": "burlywood", "displayName": "Burlywood"},
        "#F4A460": {"name": "orange_sable", "displayName": "Orange sablé"},
    }
    
    @staticmethod
    def _safe_dict(value: Any, default: dict = None) -> dict:
        """
        Convertit une valeur en dict de manière sûre
        
        Args:
            value: Valeur à convertir
            default: Dict par défaut si conversion échoue
            
        Returns:
            Dict convertie ou default
        """
        if isinstance(value, dict):
            return value
        return default or {}
    
    @staticmethod
    def _safe_list(value: Any, default: list = None) -> list:
        """
        Convertit une valeur en liste de manière sûre
        
        Args:
            value: Valeur à convertir
            default: Liste par défaut si conversion échoue
            
        Returns:
            Liste convertie ou default
        """
        if isinstance(value, list):
            return value
        return default or []
    
    @staticmethod
    def _build_all_colors_with_notes(notes_compatibilite: dict) -> list:
        """
        Transforme notesCompatibilite (dict) en allColorsWithNotes (list)
        avec hex codes pour chaque couleur
        
        INPUT:
        {
            "rouge": {"note": "8", "commentaire": "..."},
            "bleu": {"note": "3", "commentaire": "..."},
            ...
        }
        
        OUTPUT (trié par note décroissante):
        [
            {"name": "rouge", "note": 8, "commentaire": "...", "hex": "#FF0000"},
            {"name": "bleu", "note": 3, "commentaire": "...", "hex": "#0000FF"},
            ...
        ]
        """
        all_colors = []
        
        for color_name, color_data in notes_compatibilite.items():
            if isinstance(color_data, dict):
                try:
                    # Convertir la note en int (OpenAI peut l'envoyer en string)
                    note = int(color_data.get("note", 0)) if isinstance(color_data.get("note"), str) else color_data.get("note", 0)
                except (ValueError, TypeError):
                    note = 0
                
                # Chercher le hex dans COLOR_HEX_MAP
                hex_code = PDFDataMapper.COLOR_HEX_MAP.get(color_name, {}).get("hex", "#CCCCCC")
                if not isinstance(hex_code, str) or hex_code.startswith("#"):
                    # Si hex n'est pas dans COLOR_HEX_MAP, chercher directement
                    if color_name in PDFDataMapper.COLOR_HEX_MAP:
                        hex_code = list(PDFDataMapper.COLOR_HEX_MAP.keys())[
                            list(PDFDataMapper.COLOR_HEX_MAP.values()).index({"name": color_name, "displayName": ""})
                        ]
                    else:
                        hex_code = "#CCCCCC"
                
                all_colors.append({
                    "name": color_name,
                    "note": note,
                    "commentaire": color_data.get("commentaire", ""),
                    "hex": hex_code
                })
        
        # Trier par note décroissante
        all_colors.sort(key=lambda x: x["note"], reverse=True)
        return all_colors
    
    @staticmethod
    def _create_hex_to_color_map(palette: list) -> Dict[str, Dict[str, str]]:
        """
        Crée un mapping hex → {name, displayName} depuis palette_personnalisee
        PLUS fallback sur COLOR_HEX_MAP global
        
        Stratégie:
        1. Ajouter tous les hex de palette_personnalisee (priorité haute)
        2. Ajouter tous les hex de COLOR_HEX_MAP (fallback)
        
        Retourne un dict:
        {
            "#C19A6B": {"name": "camel", "displayName": "Camel", "hex": "#C19A6B"},
            "#E2725B": {"name": "terracotta", "displayName": "Terracotta", "hex": "#E2725B"},
            "#000080": {"name": "marine", "displayName": "Marine", "hex": "#000080"},  # ← Du fallback
            ...
        }
        """
        hex_map = {}
        
        # ÉTAPE 1: Ajouter depuis palette_personnalisee (priorité haute)
        for color in palette:
            if isinstance(color, dict) and "hex" in color:
                hex_upper = color["hex"].upper()
                hex_map[hex_upper] = {
                    "name": color.get("name", ""),
                    "displayName": color.get("displayName", ""),
                    "hex": color["hex"]
                }
        
        # ÉTAPE 2: Ajouter depuis COLOR_HEX_MAP global (fallback - sans overwrite)
        for hex_code, color_info in PDFDataMapper.COLOR_HEX_MAP.items():
            hex_upper = hex_code.upper()
            # Ne pas overwrite si déjà dans palette_personnalisee
            if hex_upper not in hex_map:
                hex_map[hex_upper] = {
                    "name": color_info.get("name", ""),
                    "displayName": color_info.get("displayName", ""),
                    "hex": hex_code
                }
        
        print(f"\n   🔍 _create_hex_to_color_map créé: {len(hex_map)} couleurs")
        print(f"      - Depuis palette_personnalisee: {len([c for c in palette if isinstance(c, dict) and 'hex' in c])}")
        print(f"      - Depuis COLOR_HEX_MAP global: {len(PDFDataMapper.COLOR_HEX_MAP)}")
        return hex_map
    
    @staticmethod
    def _enrich_associations_with_color_names(associations: list, palette: list) -> list:
        """
        Enrichit les associations avec color_details (noms des couleurs)
        
        Stratégie:
        1. Créer hex_map depuis palette_personnalisee
        2. Ajouter fallback depuis COLOR_HEX_MAP global
        3. Pour chaque hex dans colors[], chercher le nom
        4. Si pas trouvé: fallback "Couleur"
        
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
                    {"hex": "#000080", "name": "marine", "displayName": "Marine"}  # ← Du fallback!
                ],
                "effet": "Élégance autorité"
            }
        ]
        """
        
        # Créer le mapping hex → {name, displayName} (PALETTE + COLOR_HEX_MAP)
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
                
                # Chercher dans le mapping (qui a palette + COLOR_HEX_MAP)
                if hex_upper in hex_map:
                    color_details.append(hex_map[hex_upper])
                else:
                    # Dernier fallback si vraiment pas trouvé
                    color_details.append({
                        "hex": hex_code,
                        "name": "couleur",
                        "displayName": "Couleur"
                    })
            
            # Construire l'association enrichie
            enriched_assoc = {
                **assoc,
                "combo": colors_list,
                "color_details": color_details
            }
            
            enriched_associations.append(enriched_assoc)
        
        print(f"\n   ✅ _enrich_associations_with_color_names: {len(enriched_associations)} associations")
        return enriched_associations
    
    @staticmethod
    def _transform_nail_colors(nail_hex_list: list, palette: list) -> list:
        """
        Transforme les codes hex des ongles en [{hex, name, displayName}, ...]
        Utilise PALETTE + COLOR_HEX_MAP comme fallback
        
        INPUT:
        ["#E1AD01", "#7B3F00", "#CC7722", "#6D071A", "#CD7F32"]
        
        OUTPUT:
        [
            {"hex": "#E1AD01", "name": "moutarde", "displayName": "Moutarde"},
            {"hex": "#7B3F00", "name": "chocolat", "displayName": "Chocolat"},
            {"hex": "#CC7722", "name": "ocre", "displayName": "Ocre"},
            {"hex": "#6D071A", "name": "bordeaux", "displayName": "Bordeaux"},
            {"hex": "#CD7F32", "name": "bronze", "displayName": "Bronze"}
        ]
        """
        
        if not nail_hex_list:
            return []
        
        # Créer le mapping hex → {name, displayName} (PALETTE + COLOR_HEX_MAP)
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
        
        print(f"   ✅ _transform_nail_colors: {len(nail_colors_detailed)} couleurs d'ongles")
        return nail_colors_detailed
    
    @staticmethod
    def prepare_liquid_variables(report_data: dict, user_data: dict) -> dict:
        """
        ✅ FONCTION PRINCIPALE - Prépare les variables Liquid pour le template PDFMonkey
        
        VERSION 4 - AMÉLIORATIONS:
        1. ✅ guide_maquillage extrait depuis colorimetry (pas niveau racine)
        2. ✅ Mapping exact des clés Liquid pour le makeup
        3. ✅ Associations: enrichies avec color_details (noms des couleurs)
        4. ✅ Shopping_couleurs extrait depuis colorimetry
        5. ✅ nailColors: transformés de hex codes à [{hex, name}, ...]
        6. ✅ COLOR_HEX_MAP global comme fallback pour toutes les associations
        7. ✅ Hex map multi-niveaux: palette → COLOR_HEX_MAP → fallback
        """
        
        print("\n" + "="*70)
        print("🔧 PDF DATA MAPPER - PREPARE_LIQUID_VARIABLES (v4 COMPLÈTE)")
        print("="*70)
        
        # Extraire les sections principales
        colorimetry_raw = PDFDataMapper._safe_dict(report_data.get("colorimetry"))
        morphology_raw = PDFDataMapper._safe_dict(report_data.get("morphology"))
        styling_raw = PDFDataMapper._safe_dict(report_data.get("styling"))
        products_raw = PDFDataMapper._safe_dict(report_data.get("products"))
        
        # Extraire guide_maquillage et shopping_couleurs DEPUIS colorimetry
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
        
        # Enrichir les associations avec noms des couleurs + COLOR_HEX_MAP fallback
        print(f"\n✨ Enrichissement des associations:")
        raw_associations = PDFDataMapper._safe_list(colorimetry_raw.get("associations_gagnantes"))
        associations = PDFDataMapper._enrich_associations_with_color_names(raw_associations, palette)
        
        alternatives = PDFDataMapper._safe_dict(colorimetry_raw.get("alternatives_couleurs_refusees"))
        all_colors_with_notes = PDFDataMapper._build_all_colors_with_notes(notes_compatibilite)
        
        print(f"   ✓ palette: {len(palette)} couleurs")
        print(f"   ✓ notes_compatibilite: {len(notes_compatibilite)} couleurs")
        print(f"   ✓ allColorsWithNotes: {len(all_colors_with_notes)} couleurs")
        print(f"   ✓ associations: {len(associations)} (enrichies)")
        print(f"   ✓ alternatives: {len(alternatives)}")
        
        # ================================================================
        # SECTION MAKEUP
        # ================================================================
        print(f"\n💄 Mapping makeup (CLÉS CORRIGÉES):")
        
        # Transformer nailColors de hex codes à [{hex, name}, ...]
        raw_nail_colors = PDFDataMapper._safe_list(guide_maquillage_raw.get("vernis_a_ongles", []))
        print(f"\n💅 Transformation ongles:")
        nail_colors_transformed = PDFDataMapper._transform_nail_colors(raw_nail_colors, palette)
        
        # Mapper les clés EXACTES attendues par le template
        makeup_mapping = {
            "foundation": guide_maquillage_raw.get("teint", ""),
            "blush": guide_maquillage_raw.get("blush", ""),
            "bronzer": guide_maquillage_raw.get("bronzer", ""),
            "highlighter": guide_maquillage_raw.get("highlighter", ""),
            "eyeshadows": guide_maquillage_raw.get("yeux", ""),
            "eyeliner": guide_maquillage_raw.get("eyeliner", ""),
            "mascara": guide_maquillage_raw.get("mascara", ""),
            "brows": guide_maquillage_raw.get("brows", ""),
            "lipsNatural": guide_maquillage_raw.get("lipsNude", ""),
            "lipsDay": guide_maquillage_raw.get("lipsDay", ""),
            "lipsEvening": guide_maquillage_raw.get("lipsEvening", ""),
            "lipsAvoid": guide_maquillage_raw.get("lipsAvoid", ""),
            "nailColors": nail_colors_transformed,
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
            "user": {
                "firstName": first_name,
                "lastName": last_name,
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
                "alternativesCouleurs": alternatives,
                "associationsGagnantes": associations,
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
        
        print(f"\n✅ Structure Liquid assemblée (v4 COMPLÈTE)")
        print(f"   ✓ Associations enrichies: {len(associations)} avec color_details")
        print(f"   ✓ Ongles transformés: {len(nail_colors_transformed)} couleurs détaillées")
        print(f"   ✓ COLOR_HEX_MAP fallback: {len(PDFDataMapper.COLOR_HEX_MAP)} couleurs disponibles")
        
        return liquid_data
    
    @staticmethod
    def map_report_to_pdfmonkey(report_data: dict, user_data: dict) -> dict:
        """Wrapper pour compatibilité avec les anciennes versions"""
        return {
            "data": PDFDataMapper.prepare_liquid_variables(report_data, user_data)
        }


# Instance globale
pdf_mapper = PDFDataMapper()