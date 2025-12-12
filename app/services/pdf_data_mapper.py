"""
PDF Data Mapper v5.1 - CORRIGÉ SNAKE_CASE
✅ Garde logique complète ancien (466 lignes)
✅ CORRIGÉ: Utilise snake_case pour correspondre au template PDFMonkey
✅ Ajoute displayName generation (backend, 0 tokens OpenAI)
✅ Ajoute unwanted_colors mapping + traitement
✅ COLOR_HEX_MAP global: 40+ couleurs
✅ COLOR_NAME_MAP: reverse mapping
✅ Associations enrichies avec color_details + displayName
✅ analyse_colorimetrique_detaillee INCLUSE avec impact_visuel (snake_case)
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json
from app.services.visuals import visuals_service

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
        "rouge_chaud": "Rouge Chaud",
        "olive": "Olive",
        "brique": "Brique",
        "ocre": "Ocre",
        "rouille": "Rouille",
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
        return color_name.replace("_", " ").title()
    
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
            # Gérer les deux formats possibles: "colors" ou "color_hex"
            hex_codes = assoc.get("color_hex", assoc.get("colors", []))
            color_names = assoc.get("colors", [])
            color_details = []
            
            # Si color_hex existe, l'utiliser
            if assoc.get("color_hex"):
                for i, hex_code in enumerate(hex_codes):
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
                    
                    # Ultra-fallback: utiliser le nom de la liste colors si dispo
                    if not found:
                        name = color_names[i] if i < len(color_names) else hex_code
                        found = {
                            "name": name,
                            "displayName": PDFDataMapper.generate_display_name(name),
                            "hex": hex_code,
                        }
                    
                    color_details.append(found)
            else:
                # Sinon, utiliser les noms de couleurs
                for name in color_names:
                    hex_code = PDFDataMapper.COLOR_NAME_MAP.get(name.lower(), "#808080")
                    found = {
                        "name": name,
                        "displayName": PDFDataMapper.generate_display_name(name),
                        "hex": hex_code,
                    }
                    color_details.append(found)
            
            enriched_assoc = {
                **assoc,
                "combo": hex_codes if assoc.get("color_hex") else color_names,
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
        """Prépare variables Liquid pour PDFMonkey - SNAKE_CASE pour template"""
        
        colorimetry_raw = PDFDataMapper._safe_dict(report_data.get("colorimetry", {}))
        morphology_raw = PDFDataMapper._safe_dict(report_data.get("morphology", {}))
        styling_raw = PDFDataMapper._safe_dict(report_data.get("styling", {}))
        
        # ✅ Page 8 & Pages 9-15
        morphology_page1 = PDFDataMapper._transform_morphology_service_data(morphology_raw, user_data)
        morpho_categories = PDFDataMapper._generate_morphology_categories(morphology_raw, user_data)

        # ════════════════════════════════════════════════════════════
        # COLORIMETRY - Enrichir displayName + unwanted_colors
        # ════════════════════════════════════════════════════════════
        palette = PDFDataMapper._safe_list(colorimetry_raw.get("palette_personnalisee", []))
        palette = PDFDataMapper.enrich_with_display_names(palette)
        
        notes_compatibilite = PDFDataMapper._safe_dict(colorimetry_raw.get("notes_compatibilite", {}))
        
        # ✅ IMPORTANT: Récupérer allColorsWithNotes depuis colorimetry_raw SI présent (FALLBACK)
        all_colors_with_notes = PDFDataMapper._safe_list(colorimetry_raw.get("allColorsWithNotes", []))
        if not all_colors_with_notes:
            # Sinon construire depuis notes_compatibilite
            all_colors_with_notes = PDFDataMapper._build_all_colors_with_notes(notes_compatibilite)
        # Enrichir avec displayName
        all_colors_with_notes = PDFDataMapper.enrich_with_display_names(all_colors_with_notes)
        
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
        
        # ✅ FIX: Transform nailColors
        # Chercher d'abord dans guide_maquillage.vernis_a_ongles, sinon à la racine colorimetry.nailColors
        raw_nail_colors = PDFDataMapper._safe_list(guide_maquillage_raw.get("vernis_a_ongles", []))
        if not raw_nail_colors:
            # Fallback: chercher à la racine de colorimetry
            raw_nail_colors = PDFDataMapper._safe_list(colorimetry_raw.get("nailColors", []))
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
        # ANALYSE COLORIMETRIQUE - GARDER SNAKE_CASE pour template!
        # ════════════════════════════════════════════════════════════
        analyse_raw = PDFDataMapper._safe_dict(colorimetry_raw.get("analyse_colorimetrique_detaillee", {}))
        impact_visuel_raw = PDFDataMapper._safe_dict(analyse_raw.get("impact_visuel", {}))
        
        # ✅ GARDER snake_case pour correspondre au template PDFMonkey
        analyse_snake = {
            "temperature": analyse_raw.get("temperature", ""),
            "valeur": analyse_raw.get("valeur", ""),
            "intensite": analyse_raw.get("intensite", ""),
            "contraste_naturel": analyse_raw.get("contraste_naturel", analyse_raw.get("contrasteNaturel", "")),
            "justification_saison": colorimetry_raw.get("justification_saison", analyse_raw.get("justification_saison", "")),
            "description_teint": analyse_raw.get("description_teint", analyse_raw.get("descriptionTeint", "")),
            "description_yeux": analyse_raw.get("description_yeux", analyse_raw.get("descriptionYeux", "")),
            "description_cheveux": analyse_raw.get("description_cheveux", analyse_raw.get("descriptionCheveux", "")),
            "harmonie_globale": analyse_raw.get("harmonie_globale", analyse_raw.get("harmonieGlobale", "")),
            "bloc_emotionnel": analyse_raw.get("bloc_emotionnel", analyse_raw.get("blocEmotionnel", "")),
            "impact_visuel": {
                "effet_couleurs_chaudes": impact_visuel_raw.get("effet_couleurs_chaudes", impact_visuel_raw.get("effetCouleursChaudes", "")),
                "effet_couleurs_froides": impact_visuel_raw.get("effet_couleurs_froides", impact_visuel_raw.get("effetCouleursFroides", "")),
                "pourquoi": impact_visuel_raw.get("pourquoi", ""),
            }
        }
        
        # ════════════════════════════════════════════════════════════
        # MORPHOLOGY
        # ════════════════════════════════════════════════════════════
        hauts_visuals = PDFDataMapper._safe_list(morphology_raw.get("hauts_visuals", []))
        
        priorite_1 = PDFDataMapper._safe_list(shopping_raw.get("priorite_1", []))
        priorite_2 = PDFDataMapper._safe_list(shopping_raw.get("priorite_2", []))
        eviter = PDFDataMapper._safe_list(shopping_raw.get("eviter_absolument", []))
        
        # ════════════════════════════════════════════════════════════
        # CONSTRUIRE STRUCTURE LIQUID - ✅ SNAKE_CASE pour template!
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
            
            # ✅ CORRIGÉ: Utiliser snake_case pour correspondre au template PDFMonkey
            "colorimetry": {
                # ✅ snake_case pour template
                "saison_confirmee": colorimetry_raw.get("saison_confirmee", ""),
                "sous_ton_detecte": colorimetry_raw.get("sous_ton_detecte", ""),
                "eye_color": colorimetry_raw.get("eye_color", user_data.get("eye_color", "")),
                "hair_color": colorimetry_raw.get("hair_color", user_data.get("hair_color", "")),
                
                # ✅ snake_case pour template
                "palette_personnalisee": palette,
                "notes_compatibilite": notes_compatibilite,
                "allColorsWithNotes": all_colors_with_notes,  # Celui-ci est camelCase dans le template
                "unwanted_colors": unwanted_colors,
                "alternatives_couleurs": alternatives,
                "associations_gagnantes": associations,
                "analyse_colorimetrique_detaillee": analyse_snake,
                
                # ✅ Aussi garder pour récap page 20
                "season": colorimetry_raw.get("saison_confirmee", ""),
                "topColors": ", ".join([c.get("displayName", c.get("name", "")) for c in palette[:4]]) if palette else "",
            },
            
            "makeup": makeup_mapping,
            
            "shopping": {
                "priorite1": priorite_1,
                "priorite2": priorite_2,
                "eviterAbsolument": eviter,
            },
            
             "morphology_page1": morphology_page1,
            
            # ✅ Pour récap page 20
            "morphology": {
                "bodyType": morphology_raw.get("silhouette_type", ""),
                "objectiveShort": morphology_raw.get("objective_comment", "")[:50] + "..." if morphology_raw.get("objective_comment") else "",
            },
            
            "morpho": {
                "categories": morpho_categories,
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
                "totalPieces": len(PDFDataMapper._safe_list(styling_raw.get("capsule_basics", []))) + len(PDFDataMapper._safe_list(styling_raw.get("capsule_statement_pieces", []))),
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
        
        print(f"✅ Mapper v5.1 (snake_case) complet:")
        print(f"   ✓ Palette: {len(palette)} + displayName")
        print(f"   ✓ AllColorsWithNotes: {len(all_colors_with_notes)} couleurs")
        print(f"   ✓ Associations: {len(associations)} enrichies")
        print(f"   ✓ Unwanted colors: {len(unwanted_colors)} traitées")
        print(f"   ✓ Ongles: {len(nail_colors_transformed)} détaillés")
        print(f"   ✓ Analyse: snake_case + impact_visuel")
        
        return liquid_data
    
    @staticmethod
    def _transform_morphology_service_data(morphology_raw: dict, user_data: dict) -> dict:
        """Transforme morphology_service.analyze() en morphology_page1"""
        silhouette_type = morphology_raw.get("silhouette_type", "")
        silhouette_explanation = morphology_raw.get("silhouette_explanation", "")
        styling_objectives = PDFDataMapper._safe_list(morphology_raw.get("styling_objectives", []))
        recommendations = PDFDataMapper._safe_dict(morphology_raw.get("recommendations", {}))
        instant_tips = PDFDataMapper._safe_list(morphology_raw.get("instant_tips", []))
        
        hauts_recos = PDFDataMapper._safe_dict(recommendations.get("hauts", {}))
        a_privilegier = PDFDataMapper._safe_list(hauts_recos.get("a_privilegier", []))
        a_eviter = PDFDataMapper._safe_list(hauts_recos.get("a_eviter", []))
        
        highlights = []
        for item in a_privilegier[:3]:
            cut_display = item.get("cut_display", item.get("cut", ""))
            why = item.get("why", "")
            if cut_display:
                highlights.append(f"{cut_display}: {why}" if why else cut_display)
        
        minimizes = []
        for item in a_eviter[:3]:
            cut = item.get("cut", item.get("cut_display", ""))
            why = item.get("why", "")
            if cut:
                minimizes.append(f"{cut}: {why}" if why else cut)
        
        waist = user_data.get("waist_circumference", 0) or 0
        shoulders = user_data.get("shoulder_circumference", 0) or 0
        hips = user_data.get("hip_circumference", 0) or 0
        
        waist_hip_ratio = round(waist / hips, 2) if hips > 0 else ""
        waist_shoulder_ratio = round(waist / shoulders, 2) if shoulders > 0 else ""
        
        return {
            "bodyType": silhouette_type,
            "coherence": silhouette_explanation,
            "ratios": {
                "waistToHips": str(waist_hip_ratio),
                "waistToShoulders": str(waist_shoulder_ratio),
            },
            "measures": {
                "shoulders": shoulders,
                "waist": waist,
                "hips": hips,
                "heightCm": user_data.get("height", ""),
                "weightKg": user_data.get("weight", ""),
            },
            "comment": " ".join(styling_objectives[:1]) if styling_objectives else "",
            "goals": styling_objectives if styling_objectives else ["Créer de la verticalité"],
            "highlights": highlights if highlights else ["Vos atouts naturels"],
            "minimizes": minimizes if minimizes else ["Créer une transition fluide"],
            "instantTips": instant_tips if instant_tips else ["Explorez les coupes qui vous flattent"],
            "photos": {"body": user_data.get("body_photo_url", "")},
        }

    @staticmethod
    def _generate_morphology_categories(morphology_raw: dict, user_data: dict) -> dict:
        """
        Génère données pour Pages 9-15 (7 catégories vestimentaires)
        Contenu adapté à la silhouette détectée
        ✅ ENRICHI: Chaque recommandation inclut visual_url et visual_key
        ✅ DEBUG: Affiche si les visuels sont chargés
        """
        
        silhouette_type = morphology_raw.get("silhouette_type", "O")
        styling_objectives = PDFDataMapper._safe_list(morphology_raw.get("styling_objectives", []))
        body_parts_to_highlight = PDFDataMapper._safe_list(morphology_raw.get("body_parts_to_highlight", []))
        
        if silhouette_type == "O":
            # ✅ Structure de base (COMPLÈTE - voir fichiers précédents)
            categories_data = {
                "hauts": {
                    "introduction": f"Pour votre silhouette {silhouette_type}, les hauts doivent créer de la verticalité et époucer légèrement. Privilégiez les encolures en V et les matières fluides.",
                    "recommandes": [
                        {"name": "Encolure en V", "why": "Allonge le cou et crée une verticalité immédiate"},
                        {"name": "Manches raglan ou kimono", "why": "Harmonise les épaules et allonge le buste"},
                        {"name": "Coupes ceinturées", "why": "Marque la taille et crée de la définition"},
                        {"name": "Matières fluides (soie, coton léger)", "why": "Épousent sans serrer, créent de la fluidité"},
                        {"name": "Rayures verticales", "why": "Allongent et structurent visuellement"},
                        {"name": "Couches et superpositions", "why": "Créent de la profondeur et du relief"},
                    ],
                    "a_eviter": [
                        {"name": "Col roulé très serré", "why": "Écrase le cou et raccourcit le buste"},
                        {"name": "Polos stretch très ajustés", "why": "Accentuent le volume au centre"},
                        {"name": "Volumes excessifs au buste", "why": "Ajoutent de la masse là où il faut minimiser"},
                        {"name": "Matières rigides (denim épais)", "why": "Figent la silhouette et manquent de fluidité"},
                        {"name": "Rayures horizontales larges", "why": "Élargissent visuellement la silhouette"},
                    ],
                    "matieres": "Privilégier les matières fluides (soie, coton peigné, lin mélangé, jersey fin) qui épousent sans serrer. Les mailles structurantes de bonne qualité créent une belle verticalité. Éviter le denim rigide, la toile épaisse et les tissus qui marquent trop.",
                    "motifs": {
                        "recommandes": "Rayures verticales, losanges verticaux, petits motifs discrets, dégradés, détails au niveau de l'encolure ou des épaules",
                        "a_eviter": "Rayures horizontales, gros motifs répétitifs, pois, carreaux, imprimés trop volumineux au centre"
                    },
                    "pieges": [
                        "Ourlets qui coupent la silhouette à la mauvaise hauteur (casser la verticalité)",
                        "Encolures asymétriques qui perturbent l'équilibre",
                        "Nœuds ou fronces au niveau du buste qui accentuent",
                        "Bandes stretch trop visibles qui marquent",
                        "Matières brillantes au mauvais endroit (à éviter au centre)",
                        "Coutures épaisses qui cassent les lignes",
                        "Ceintures trop larges qui écrasent plutôt que définissent"
                    ],
                    "visuels": []
                },
                "bas": {
                    "introduction": f"Pour votre silhouette {silhouette_type}, les bas doivent allonger les jambes et créer une transition fluide. Privilégiez les tailles hautes et les coupes qui épousent légèrement.",
                    "recommandes": [
                        {"name": "Tailles hautes", "why": "Allongent les jambes et structurent la silhouette"},
                        {"name": "Coupes droites ou évasées", "why": "Épousent légèrement sans serrer, allongent les proportions"},
                        {"name": "Jupes crayon ou portefeuille", "why": "Marquent la taille et créent de la définition"},
                        {"name": "Longueurs midi ou cheville", "why": "Allongent les jambes et créent une fluidité"},
                        {"name": "Rayures verticales", "why": "Créent une illusion d'optique d'allongement"},
                        {"name": "Matières fluides (soie, coton léger)", "why": "Bougent naturellement et flattent les formes"},
                    ],
                    "a_eviter": [
                        {"name": "Tailles basses", "why": "Raccourcissent les jambes et élargissent visuellement"},
                        {"name": "Baggy ou sursize au niveau des hanches", "why": "Ajoutent du volume là où il faut harmoniser"},
                        {"name": "Coupes moulantes excessives", "why": "Accentuent chaque détail du corps"},
                        {"name": "Ceintures très larges", "why": "Écrasent et figent la taille"},
                        {"name": "Rayures horizontales", "why": "Élargissent visuellement les jambes"},
                    ],
                    "matieres": "Privilégier les matières fluides et élastiques (coton stretch, lin mélangé, jersey) qui épousent légèrement. Éviter le denim trop rigide. Les matières mats valorisent plus que les brillants.",
                    "motifs": {
                        "recommandes": "Rayures verticales, motifs discrets, petits imprimés, dégradés unis, placement horizontal au niveau des chevilles",
                        "a_eviter": "Rayures horizontales, gros motifs répétitifs, pois, carreaux volumineux, imprimés trop clairs qui élargissent"
                    },
                    "pieges": [
                        "Longueur qui coupe la jambe à la mauvaise hauteur",
                        "Ourlets trop courts qui cassent les proportions",
                        "Poches trop voluminuses qui élargissent les hanches",
                        "Ceintures trop serrées qui marquent",
                        "Zip ou fermetures mal placées qui accentuent",
                        "Matières trop épaisses au niveau des hanches",
                        "Braguette ou surpiqûres qui accentuent"
                    ],
                    "visuels": []
                },
                "robes": {
                    "introduction": f"Pour votre silhouette {silhouette_type}, les robes doivent époucer légèrement et marquer la taille. Privilégiez les coupes portefeuille et les ceintures qui définissent.",
                    "recommandes": [
                        {"name": "Robes portefeuille", "why": "Marquent la taille et s'adaptent à tous les types de silhouette"},
                        {"name": "Ceintures intégrées ou accessoires", "why": "Définissent la taille et créent des proportions équilibrées"},
                        {"name": "Longueurs midi à cheville", "why": "Allongent et créent une fluidité élégante"},
                        {"name": "Encolures en V ou cache-cœur", "why": "Allongent le buste et le cou"},
                        {"name": "Matières fluides", "why": "Bougent naturellement et flattent la silhouette"},
                        {"name": "Robes cache-cœur", "why": "Marquent la taille et valorisent le buste"},
                    ],
                    "a_eviter": [
                        {"name": "Robes trop amples", "why": "Ajoutent du volume et épaississent"},
                        {"name": "Ceintures trop larges non intégrées", "why": "Peuvent écraser plutôt que définir"},
                        {"name": "Coupes droites sans définition", "why": "N'épousent pas assez et aplatissent"},
                        {"name": "Longueurs courtes", "why": "Raccourcissent les jambes et perturbent l'équilibre"},
                        {"name": "Col roulé très serré", "why": "Écrase le cou et le buste"},
                    ],
                    "matieres": "Privilégier les matières fluides structurantes (soie, crêpe, coton peigné) qui épousent sans serrer. Éviter les matières trop rigides qui ne flattent pas les courbes.",
                    "motifs": {
                        "recommandes": "Rayures verticales, motifs discrets, petits imprimés géométriques, dégradés, détails au niveau de la taille",
                        "a_eviter": "Rayures horizontales, gros motifs centrés au buste, pois volumineux, carreaux qui élargissent"
                    },
                    "pieges": [
                        "Ourlet qui coupe la jambe à la mauvaise hauteur",
                        "Trop de volume au buste",
                        "Ceintures mal positionnées",
                        "Matières brillantes qui soulignent les zones à harmoniser",
                        "Fermetures éclair ou détails qui accentuent",
                        "Encolures trop hautes",
                        "Longueurs qui figent plutôt que de créer de la fluidité"
                    ],
                    "visuels": []
                },
                "vestes": {
                    "introduction": f"Pour votre silhouette {silhouette_type}, les vestes doivent structurer et créer de la verticalité. Privilégiez les coupes ajustées avec une ceinture ou des détails qui définissent.",
                    "recommandes": [
                        {"name": "Vestes cintrées", "why": "Marquent la taille et créent une définition immédiate"},
                        {"name": "Ceintures intégrées", "why": "Structurent sans ajouter de volume"},
                        {"name": "Longueurs qui arrivent à la taille ou légèrement plus bas", "why": "Allongent et définissent les proportions"},
                        {"name": "Épaulettes subtiles", "why": "Harmonisent les épaules sans surcharger"},
                        {"name": "Manteaux fluides", "why": "Bougent naturellement et créent de l'élégance"},
                        {"name": "Coutures verticales", "why": "Créent des lignes qui allongent"},
                    ],
                    "a_eviter": [
                        {"name": "Vestes trop amples", "why": "Ajoutent du volume et épaississent"},
                        {"name": "Longueurs qui arrivent aux hanches", "why": "Accentuent le volume et raccourcissent"},
                        {"name": "Ceintures très larges", "why": "Peuvent écraser plutôt que définir"},
                        {"name": "Épaulettes excessives", "why": "Élargissent les épaules"},
                        {"name": "Matières trop rigides", "why": "Figent la silhouette"},
                    ],
                    "matieres": "Privilégier les matières semi-rigides (laine, lin, coton structurant) qui tiennent bien. Les matières fluides avec doublure créent une belle ligne. Éviter les matières trop épaisses.",
                    "motifs": {
                        "recommandes": "Rayures verticales subtiles, motifs discrets, uni de qualité, petits carreaux fins",
                        "a_eviter": "Rayures horizontales, gros carreaux, motifs volumineux, imprimés qui élargissent"
                    },
                    "pieges": [
                        "Longueur qui coupe mal le corps",
                        "Fermeture ou boutonnage mal aligné",
                        "Poches trop voluminuses qui élargissent les hanches",
                        "Ceintures mal positionnées",
                        "Épaulettes trop marquées",
                        "Doublure qui montre et ajoute du volume",
                        "Coutures asymétriques"
                    ],
                    "visuels": []
                },
                "maillot_lingerie": {
                    "introduction": f"Pour votre silhouette {silhouette_type}, confort et confiance sont essentiels. Choisissez des coupes et soutiens adaptés qui vous mettent en valeur.",
                    "recommandes": [
                        {"name": "Soutiens-gorge structurants avec maintien", "why": "Créent une belle forme et du confort"},
                        {"name": "Maillots de bain avec motifs au niveau du buste", "why": "Valorisent et créent du relief"},
                        {"name": "Ceintures gaines douces", "why": "Lissent légèrement sans comprimer"},
                        {"name": "Matières stretch confortables", "why": "Épousent naturellement et confortablement"},
                        {"name": "Coupes cache-cœur", "why": "Flattent et créent de la féminité"},
                        {"name": "Lanières verticales", "why": "Créent une illusion d'allongement"},
                    ],
                    "a_eviter": [
                        {"name": "Soutiens-gorge trop serrés", "why": "Créent de l'inconfort et des marques"},
                        {"name": "Matières rigides", "why": "Ne s'adaptent pas à votre corps"},
                        {"name": "Maillots de bain trop amples", "why": "Ajoutent du volume"},
                        {"name": "Coutures mal placées", "why": "Peuvent marquer ou créer des gonflements"},
                    ],
                    "matieres": "Privilégier les matières stretch de qualité (coton bio, microfibre, nylon). Les doublures douces et les ceintures gaines discrètes offrent confort et confiance.",
                    "motifs": {
                        "recommandes": "Rayures verticales, petits motifs, dégradés, uni de qualité, motifs au niveau du buste",
                        "a_eviter": "Rayures horizontales, gros motifs au centre, couleurs trop claires au niveau du buste"
                    },
                    "pieges": [
                        "Soutiens-gorge mal calibrés",
                        "Matières qui glissent ou se déplacent",
                        "Coutures épaisses qui marquent",
                        "Doublures insuffisantes",
                        "Élastiques trop serrés",
                        "Gaines qui compriment excessivement",
                        "Motifs mal placés"
                    ],
                    "visuels": []
                },
                "chaussures": {
                    "introduction": f"Pour votre silhouette {silhouette_type}, les chaussures affinent ou élargissent. Choisissez les formes qui allongent et créent de l'élégance.",
                    "recommandes": [
                        {"name": "Chaussures à talon fin", "why": "Affinent la cheville et allongent les jambes"},
                        {"name": "Escarpins pointus", "why": "Créent une ligne allongée et élégante"},
                        {"name": "Bottines à talon", "why": "Allongent les jambes et structurent"},
                        {"name": "Chaussures aux teintes proches de la peau", "why": "Allongent visuellement les jambes"},
                        {"name": "Chaussures avec détails verticaux", "why": "Créent une ligne qui affine"},
                        {"name": "Matières nobles (cuir, daim)", "why": "Créent une ligne nette et reflet la lumière"},
                    ],
                    "a_eviter": [
                        {"name": "Chaussures plates et larges", "why": "Raccourcissent les jambes"},
                        {"name": "Bottines trop molles", "why": "Élargissent les chevilles"},
                        {"name": "Chaussures arrondies trop larges", "why": "Épaississent les pieds"},
                        {"name": "Sandales très échancrées", "why": "Peuvent raccourcir la jambe"},
                        {"name": "Matières molles qui s'affaissent", "why": "Déforment et perdent leur allure"},
                    ],
                    "matieres": "Privilégier les matières nobles (cuir, daim, matières brillantes) qui reflètent la lumière et créent une ligne nette. Éviter les matières molles qui s'affaissent.",
                    "motifs": {
                        "recommandes": "Couleurs unies, finitions brillantes, matières qui reflètent la lumière",
                        "a_eviter": "Matières trop épaisses, couleurs très contrastées, surcharges de détails"
                    },
                    "pieges": [
                        "Talons trop bas ou nuls",
                        "Largeur mal adaptée à vos pieds",
                        "Hauteur de tige qui coupe mal la jambe",
                        "Matières qui se déforment",
                        "Couleurs qui tranchent trop",
                        "Semelles visibles mal alignées",
                        "Détails qui élargissent"
                    ],
                    "visuels": []
                },
                "accessoires": {
                    "introduction": f"Pour votre silhouette {silhouette_type}, les accessoires finissent la tenue avec élégance. Privilégiez les pièces qui créent de la verticalité et de la proportion.",
                    "recommandes": [
                        {"name": "Ceintures fines ou moyennes", "why": "Définissent la taille sans ajouter de volume"},
                        {"name": "Sacs de taille moyenne", "why": "Créent de l'équilibre sans ajouter du poids visuel"},
                        {"name": "Bijoux verticaux (colliers longs, créoles)", "why": "Allongent le cou et le buste"},
                        {"name": "Foulards (port long)", "why": "Créent de la verticalité et de la fluidité"},
                        {"name": "Capes légères", "why": "Créent des lignes épurées et élégantes"},
                        {"name": "Accessoires discrets de qualité", "why": "Valorisent sans surcharger"},
                    ],
                    "a_eviter": [
                        {"name": "Ceintures très larges", "why": "Écrasent plutôt que définissent"},
                        {"name": "Sacs trop volumineux", "why": "Ajoutent du poids visuel"},
                        {"name": "Bijoux trop lourds ou trop gros", "why": "Écrasent le haut du corps"},
                        {"name": "Foulards port court ou dense", "why": "Élargissent le cou"},
                        {"name": "Surcharge d'accessoires", "why": "Perturbent l'équilibre"},
                    ],
                    "matieres": "Privilégier les matières nobles (cuir, soie, matières brillantes) qui reflètent l'élégance. Les finitions douces et les textures qualitatives créent un effet raffiné.",
                    "motifs": {
                        "recommandes": "Motifs discrets, couleurs uni de qualité, rayures verticales subtiles, géométries fines",
                        "a_eviter": "Motifs volumineux, couleurs trop criardes, surcharges de détails, motifs qui élargissent"
                    },
                    "pieges": [
                        "Ceintures mal positionnées",
                        "Sacs qui pèsent trop lourd d'un côté",
                        "Bijoux mal proportionnés",
                        "Foulards qui rétrécissent",
                        "Accessoires de mauvaise qualité",
                        "Surcharge d'accessoires",
                        "Matières brillantes mal placées"
                    ],
                    "visuels": []
                },
            }
            
            # ✅ ENRICHIR CHAQUE CATÉGORIE AVEC LES VISUELS
            print("\n🎨 ════════════════════════════════════════════════════════════════")
            print("🎨 ENRICHISSEMENT VISUELS - DÉBUT")
            print("🎨 ════════════════════════════════════════════════════════════════")
            
            for category_name, category_data in categories_data.items():
                print(f"\n📍 Catégorie: {category_name}")
                
                # Enrichir recommandations avec visuels
                enriched_recommandes = visuals_service.fetch_visuals_for_category(
                    category_name,
                    category_data.get("recommandes", [])
                )
                category_data["recommandes"] = enriched_recommandes
                
                # ✅ DEBUG: AFFICHER LES VISUELS ENRICHIS (RECOMMANDÉS)
                print(f"   ✅ Recommandées enrichies: {len(enriched_recommandes)} items")
                for i, item in enumerate(enriched_recommandes[:2]):
                    visual_url = item.get("visual_url", "VIDE")
                    visual_key = item.get("visual_key", "N/A")
                    url_status = "✅" if visual_url else "❌"
                    print(f"      {url_status} Item {i}: '{item.get('name')}' → visual_url: {visual_url[:50] if visual_url else 'VIDE'}... | key: {visual_key}")
                
                # Enrichir aussi les à éviter
                enriched_a_eviter = visuals_service.fetch_visuals_for_category(
                    category_name,
                    category_data.get("a_eviter", [])
                )
                category_data["a_eviter"] = enriched_a_eviter
                
                # ✅ DEBUG: AFFICHER LES VISUELS ENRICHIS (À ÉVITER)
                print(f"   ⚠️ À éviter enrichies: {len(enriched_a_eviter)} items")
                for i, item in enumerate(enriched_a_eviter[:2]):
                    visual_url = item.get("visual_url", "VIDE")
                    visual_key = item.get("visual_key", "N/A")
                    url_status = "✅" if visual_url else "❌"
                    print(f"      {url_status} Item {i}: '{item.get('name')}' → visual_url: {visual_url[:50] if visual_url else 'VIDE'}... | key: {visual_key}")
            
            print("\n🎨 ════════════════════════════════════════════════════════════════")
            print("🎨 ENRICHISSEMENT VISUELS - FIN ✅")
            print("🎨 ════════════════════════════════════════════════════════════════\n")
            
            return categories_data
        
        # Pour les autres silhouettes (reste du code identique...)
        else:
            generic_structure = {
                "introduction": f"Pour votre silhouette {silhouette_type}, adaptez vos pièces à votre morphologie unique.",
                "recommandes": [
                    {"name": "Pièce 1", "why": "Adapté à votre silhouette", "visual_url": "", "visual_key": ""},
                    {"name": "Pièce 2", "why": "Valorise vos atouts", "visual_url": "", "visual_key": ""},
                    {"name": "Pièce 3", "why": "Crée l'harmonie", "visual_url": "", "visual_key": ""},
                    {"name": "Pièce 4", "why": "Affine votre silhouette", "visual_url": "", "visual_key": ""},
                    {"name": "Pièce 5", "why": "Crée de la fluidité", "visual_url": "", "visual_key": ""},
                    {"name": "Pièce 6", "why": "Personnalise votre look", "visual_url": "", "visual_key": ""},
                ],
                "a_eviter": [
                    {"name": "À éviter 1", "why": "Peut élargir", "visual_url": "", "visual_key": ""},
                    {"name": "À éviter 2", "why": "Manque de fluidité", "visual_url": "", "visual_key": ""},
                    {"name": "À éviter 3", "why": "Peut écaser", "visual_url": "", "visual_key": ""},
                    {"name": "À éviter 4", "why": "Crée un déséquilibre", "visual_url": "", "visual_key": ""},
                    {"name": "À éviter 5", "why": "Peut marquer", "visual_url": "", "visual_key": ""},
                ],
                "matieres": "Privilégiez les matières de qualité qui épousent votre silhouette sans contrainte. Choisissez des tissus nobles et fluides.",
                "motifs": {
                    "recommandes": "Motifs discrets, rayures verticales, petits imprimés, dégradés",
                    "a_eviter": "Gros motifs, rayures horizontales, imprimés trop clairs"
                },
                "pieges": [
                    "Mal évaluer votre taille réelle",
                    "Choisir des longueurs qui coupent mal",
                    "Surcharger avec des accessoires",
                    "Négliger la qualité des matières",
                    "Créer un déséquilibre visuel",
                    "Forcer des coupes inadaptées",
                    "Ignorer votre morphologie"
                ],
                "visuels": []
            }
            
            return {
                "hauts": {**generic_structure, "introduction": f"Pour votre silhouette {silhouette_type}, les hauts doivent valoriser vos atouts."},
                "bas": {**generic_structure, "introduction": f"Pour votre silhouette {silhouette_type}, les bas doivent allonger et harmoniser."},
                "robes": {**generic_structure, "introduction": f"Pour votre silhouette {silhouette_type}, les robes doivent créer une belle proportion."},
                "vestes": {**generic_structure, "introduction": f"Pour votre silhouette {silhouette_type}, les vestes doivent structurer et élégancer."},
                "maillot_lingerie": {**generic_structure, "introduction": f"Pour votre silhouette {silhouette_type}, confort et confiance sont primordiaux."},
                "chaussures": {**generic_structure, "introduction": f"Pour votre silhouette {silhouette_type}, les chaussures complètent votre look."},
                "accessoires": {**generic_structure, "introduction": f"Pour votre silhouette {silhouette_type}, les accessoires finissent avec élégance."},
            }

    @staticmethod
    def map_report_to_pdfmonkey(report_data: dict, user_data: dict) -> dict:
        """Wrapper compatibilité"""
        return {
            "data": PDFDataMapper.prepare_liquid_variables(report_data, user_data)
        }


pdf_mapper = PDFDataMapper()