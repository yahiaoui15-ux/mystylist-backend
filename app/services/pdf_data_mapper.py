"""
PDF Data Mapper v5.2 - COMPLET AVEC FIX PAGES 9-15
✅ Garde logique complète (895 lignes)
✅ FIX SCALPEL ligne 558-795: Utilise les VRAIES recommendations OpenAI
✅ Plus de contenu hardcodé "Pièce 1, Pièce 2"
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json
from app.services.visuals import visuals_service

class PDFDataMapper:
    """Mappe les données du rapport générés au format PDFMonkey (structure Liquid)"""
    
    # DISPLAY NAMES
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
    
    # COLOR_HEX_MAP GLOBAL
    COLOR_HEX_MAP = {
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
        "#FFB6C1": {"name": "rose_pale", "displayName": "Rose Pâle"},
        "#FF1493": {"name": "rose_fuchsia", "displayName": "Rose Fuchsia"},
        "#FF7F50": {"name": "rose_corail", "displayName": "Rose Corail"},
        "#000080": {"name": "marine", "displayName": "Marine"},
        "#800020": {"name": "bordeaux", "displayName": "Bordeaux"},
        "#40E0D0": {"name": "turquoise", "displayName": "Turquoise"},
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
    
    COLOR_NAME_MAP = {
        color_info["name"]: hex_code
        for hex_code, color_info in COLOR_HEX_MAP.items()
    }
    
    @staticmethod
    def generate_display_name(color_name: str) -> str:
        """Génère displayName depuis name"""
        if not color_name:
            return ""
        if color_name.lower() in PDFDataMapper.DISPLAY_NAMES:
            return PDFDataMapper.DISPLAY_NAMES[color_name.lower()]
        return color_name.replace("_", " ").title()
    
    @staticmethod
    def enrich_with_display_names(items: List[dict]) -> List[dict]:
        """Ajoute displayName à une liste"""
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
        """Transforme notes_compatibilite en allColorsWithNotes"""
        all_colors = []
        
        for color_name, color_data in notes_compatibilite.items():
            if isinstance(color_data, dict):
                try:
                    note = int(color_data.get("note", 0)) if isinstance(color_data.get("note"), str) else color_data.get("note", 0)
                    hex_code = PDFDataMapper.COLOR_NAME_MAP.get(color_name, "#808080")
                    
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
        
        all_colors.sort(key=lambda x: x["note"], reverse=True)
        return all_colors
    
    @staticmethod
    def _enrich_associations_with_colors(associations: list, palette: list) -> list:
        """Enrichit associations avec color_details"""
        enriched = []
        
        for assoc in associations:
            hex_codes = assoc.get("color_hex", assoc.get("colors", []))
            color_names = assoc.get("colors", [])
            color_details = []
            
            if assoc.get("color_hex"):
                for i, hex_code in enumerate(hex_codes):
                    found = None
                    for color in palette:
                        if color.get("hex") == hex_code:
                            found = {
                                "name": color.get("name", ""),
                                "displayName": color.get("displayName", PDFDataMapper.generate_display_name(color.get("name", ""))),
                                "hex": hex_code,
                            }
                            break
                    
                    if not found and hex_code in PDFDataMapper.COLOR_HEX_MAP:
                        color_info = PDFDataMapper.COLOR_HEX_MAP[hex_code]
                        found = {
                            "name": color_info.get("name", ""),
                            "displayName": color_info.get("displayName", ""),
                            "hex": hex_code,
                        }
                    
                    if not found:
                        name = color_names[i] if i < len(color_names) else hex_code
                        found = {
                            "name": name,
                            "displayName": PDFDataMapper.generate_display_name(name),
                            "hex": hex_code,
                        }
                    
                    color_details.append(found)
            else:
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
        """Transforme nail colors en objets complets"""
        transformed = []
        
        for item in nail_colors_hex:
            if isinstance(item, dict):
                hex_code = item.get("hex", "")
                original_display_name = item.get("displayName", "")
            else:
                hex_code = item
                original_display_name = ""
            
            if not hex_code:
                continue
                
            found = None
            for color in palette:
                if color.get("hex") == hex_code:
                    found = {
                        "name": color.get("name", ""),
                        "displayName": color.get("displayName", original_display_name),
                        "hex": hex_code,
                    }
                    break
            
            if not found and hex_code in PDFDataMapper.COLOR_HEX_MAP:
                color_info = PDFDataMapper.COLOR_HEX_MAP[hex_code]
                found = {
                    "name": color_info.get("name", ""),
                    "displayName": color_info.get("displayName", original_display_name),
                    "hex": hex_code,
                }
            
            if not found:
                found = {
                    "name": original_display_name or hex_code,
                    "displayName": original_display_name or hex_code,
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
        
        # Page 8 & Pages 9-15
        morphology_page1 = PDFDataMapper._transform_morphology_service_data(morphology_raw, user_data)
        morpho_categories = PDFDataMapper._generate_morphology_categories(morphology_raw, user_data)

        # COLORIMETRY
        palette = PDFDataMapper._safe_list(colorimetry_raw.get("palette_personnalisee", []))
        palette = PDFDataMapper.enrich_with_display_names(palette)
        palette = sorted(palette, key=lambda x: x.get("note", 0), reverse=True)
        
        notes_compatibilite = PDFDataMapper._safe_dict(colorimetry_raw.get("notes_compatibilite", {}))
        all_colors_with_notes = PDFDataMapper._build_all_colors_with_notes(notes_compatibilite)
        all_colors_with_notes = PDFDataMapper.enrich_with_display_names(all_colors_with_notes)
        
        associations = PDFDataMapper._safe_list(colorimetry_raw.get("associations_gagnantes", []))
        associations = PDFDataMapper._enrich_associations_with_colors(associations, palette)
        
        unwanted_colors = PDFDataMapper._safe_list(colorimetry_raw.get("unwanted_colors", []))
        unwanted_colors = PDFDataMapper.enrich_with_display_names(unwanted_colors)
        
        alternatives = PDFDataMapper._safe_dict(colorimetry_raw.get("alternatives_couleurs_refusees", {}))
        
        # MAKEUP
        guide_maquillage_raw = PDFDataMapper._safe_dict(colorimetry_raw.get("guide_maquillage", {}))
        shopping_raw = PDFDataMapper._safe_dict(colorimetry_raw.get("shopping_couleurs", {}))
        
        raw_nail_colors = PDFDataMapper._safe_list(colorimetry_raw.get("nailColors", []))
        nail_colors_transformed = PDFDataMapper._transform_nail_colors(raw_nail_colors, palette)
        
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
        
        # ANALYSE COLORIMETRIQUE
        analyse_raw = PDFDataMapper._safe_dict(colorimetry_raw.get("analyse_colorimetrique_detaillee", {}))
        impact_visuel_raw = PDFDataMapper._safe_dict(analyse_raw.get("impact_visuel", {}))
        
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
        
        hauts_visuals = PDFDataMapper._safe_list(morphology_raw.get("hauts_visuals", []))
        priorite_1 = PDFDataMapper._safe_list(shopping_raw.get("priorite_1", []))
        priorite_2 = PDFDataMapper._safe_list(shopping_raw.get("priorite_2", []))
        eviter = PDFDataMapper._safe_list(shopping_raw.get("eviter_absolument", []))
        
        liquid_data = {
            "user": {
                "firstName": user_data.get("first_name", ""),
                "lastName": user_data.get("last_name", ""),
                "age": user_data.get("age", ""),
                "height": user_data.get("height", ""),
                "weight": user_data.get("weight", ""),
                "facePhotoUrl": user_data.get("face_photo_url", ""),
                "bodyPhotoUrl": user_data.get("body_photo_url", ""),
                "clothingSize": user_data.get("clothing_size", ""),
            },
            
            "colorimetry": {
                "saison_confirmee": colorimetry_raw.get("saison_confirmee", ""),
                "sous_ton_detecte": colorimetry_raw.get("sous_ton_detecte", ""),
                "eye_color": colorimetry_raw.get("eye_color", user_data.get("eye_color", "")),
                "hair_color": colorimetry_raw.get("hair_color", user_data.get("hair_color", "")),
                "palette_personnalisee": palette,
                "notes_compatibilite": notes_compatibilite,
                "allColorsWithNotes": all_colors_with_notes,
                "unwanted_colors": unwanted_colors,
                "alternatives_couleurs": alternatives,
                "associations_gagnantes": associations,
                "analyse_colorimetrique_detaillee": analyse_snake,
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
            
            "morphology": {
                "bodyType": morphology_raw.get("silhouette_type", ""),
                "objectiveShort": morphology_raw.get("objective_comment", "")[:50] + "..." if morphology_raw.get("objective_comment") else "",
            },
            
            "morpho": {
                "categories": morpho_categories,
            },
            
            "morphology_highlights": morphology_raw.get("highlights", {
                "announcement": "",
                "explanation": ""
            }),
            "morphology_minimizes": morphology_raw.get("minimizes", {
                "announcement": "",
                "explanation": ""
            }),
            
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
        
        print(f"\n✅ Mapper v5.2 (avec vraies recommendations):")
        print(f"   ✓ Palette: {len(palette)} couleurs")
        print(f"   ✓ AllColorsWithNotes: {len(all_colors_with_notes)} couleurs")
        print(f"   ✓ Associations: {len(associations)} enrichies")
        print(f"   ✓ Morpho categories: {list(morpho_categories.keys())}")
        
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
        ✅ v5.2 FIXED: Utilise les VRAIES recommendations d'OpenAI Part 2
        Récupère hauts, bas, robes, vestes, etc. depuis morphology_raw.get("recommendations")
        """
        
        silhouette_type = morphology_raw.get("silhouette_type", "O")
        
        # ✅ NOUVEAU: Récupérer les VRAIES recommendations d'OpenAI Part 2
        openai_recommendations = PDFDataMapper._safe_dict(morphology_raw.get("recommendations", {}))
        
        print("\n" + "="*80)
        print("📊 UTILISATION RECOMMENDATIONS OPENAI PART 2")
        print("="*80)
        print(f"   • Silhouette: {silhouette_type}")
        print(f"   • OpenAI recommendations trouvées: {list(openai_recommendations.keys())}")
        
        categories_data = {}
        category_names = ["hauts", "bas", "robes", "vestes", "maillot_lingerie", "chaussures", "accessoires"]
        
        for category_name in category_names:
            # Récupérer depuis OpenAI s'il existe
            openai_cat_data = openai_recommendations.get(category_name, {})
            
            # ✅ Créer la structure pour le template
            categories_data[category_name] = {
                "introduction": openai_cat_data.get("introduction", f"Pour votre silhouette {silhouette_type}, découvrez les pièces recommandées."),
                "recommandes": PDFDataMapper._safe_list(openai_cat_data.get("recommandes", openai_cat_data.get("a_privilegier", []))),
                "a_eviter": PDFDataMapper._safe_list(openai_cat_data.get("a_eviter", [])),
                "matieres": openai_cat_data.get("matieres", "Privilégier les matières de qualité."),
                "motifs": openai_cat_data.get("motifs", {
                    "recommandes": "Motifs discrets, rayures verticales, petits imprimés, dégradés",
                    "a_eviter": "Gros motifs, rayures horizontales, imprimés trop clairs"
                }),
                "pieges": PDFDataMapper._safe_list(openai_cat_data.get("pieges", [])),
                "visuels": []
            }
            
            # ✅ Enrichir avec visuels si disponibles
            recommandes = categories_data[category_name]["recommandes"]
            a_eviter = categories_data[category_name]["a_eviter"]
            
            if recommandes:
                print(f"\n   📌 {category_name}:")
                print(f"      • {len(recommandes)} recommandés à enrichir")
                enriched_recommandes = visuals_service.fetch_visuals_for_category(category_name, recommandes)
                categories_data[category_name]["recommandes"] = enriched_recommandes
            
            if a_eviter:
                print(f"      • {len(a_eviter)} à éviter à enrichir")
                enriched_a_eviter = visuals_service.fetch_visuals_for_category(category_name, a_eviter)
                categories_data[category_name]["a_eviter"] = enriched_a_eviter
        
        print("\n" + "="*80)
        print("✅ Morpho categories construites depuis OpenAI Part 2")
        print("="*80 + "\n")
        
        return categories_data

    @staticmethod
    def map_report_to_pdfmonkey(report_data: dict, user_data: dict) -> dict:
        """Wrapper compatibilité"""
        return {
            "data": PDFDataMapper.prepare_liquid_variables(report_data, user_data)
        }


pdf_mapper = PDFDataMapper()