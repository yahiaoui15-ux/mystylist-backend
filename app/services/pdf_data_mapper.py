"""
PDF Data Mapper v5.3 - CORRIGÉ COMPLET
✅ Pages 4, 5, 7 fixes
✅ Utilise couleurs_generiques, couleurs_prudence, couleurs_eviter (déjà calculées par colorimetry)
✅ Utilise makeup au lieu de guide_maquillage
✅ Crée structure shopping vide
✅ Morphologie: Pages 9-15 avec vraies recommendations
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json
from app.services.archetype_visual_selector import get_style_visuals_for_archetype
from app.services.style_visuals_selector import get_style_visuals_for_style, get_style_visuals_for_style_mix
import os
import csv
from app.services.product_matcher_service import product_matcher_service
from app.services.visuals_service import visuals_service

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

    _VISUALS_INDEX = None  # cache

    @classmethod
    def _load_visuals_index(cls) -> dict:
        """
        Charge la bibliothèque visuelle depuis CSV et indexe par nom_simplifie (visual_key).
        Attend au minimum les colonnes: nom_simplifie, url_image
        """
        if cls._VISUALS_INDEX is not None:
            return cls._VISUALS_INDEX

        # 1) Chemin via env (recommandé)
        csv_path = os.getenv("STYLE_VISUALS_CSV_PATH", "").strip()

        # 2) Fallback: essaie un chemin local si tu poses le CSV dans /data ou /app/assets
        fallback_paths = [
            csv_path,
            "data/visuels_rows.csv",
            "app/assets/visuels_rows.csv",
            "/mnt/data/visuels_rows (6).csv",  # utile en dev/local notebook
        ]
        csv_path = next((p for p in fallback_paths if p and os.path.exists(p)), "")

        index = {}
        if not csv_path:
            cls._VISUALS_INDEX = index
            return index

        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    key = (row.get("nom_simplifie") or "").strip().lower()
                    url = (row.get("url_image") or "").strip()
                    if key and url and key not in index:
                        index[key] = url

        except Exception as e:
            print(f"⚠️ Erreur chargement visuels CSV: {e}")
            index = {}

        cls._VISUALS_INDEX = index
        return index

    @classmethod
    def _visual_url_from_key(cls, visual_key: str) -> str:
        if not visual_key:
            return ""
        idx = cls._load_visuals_index()
        return idx.get(str(visual_key).strip().lower(), "")

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
        """Enrichit associations avec color_details (priorité à color_details déjà fourni)"""
        enriched = []

        for assoc in associations:
            # 1) Si le service a déjà injecté color_details (Solution 1 DB), on le respecte
            existing_details = assoc.get("color_details")
            if isinstance(existing_details, list) and len(existing_details) > 0:
                transformed = {
                    "occasion": assoc.get("occasion", ""),
                    "description": assoc.get("description", ""),
                    "colors": assoc.get("colors", []),
                    "color_hex": assoc.get("color_hex", []),
                    "color_details": existing_details,
                    "image_url": assoc.get("image_url"),
                    "image_filename": assoc.get("image_filename"),
                }
                enriched.append(transformed)
                continue

            # 2) Fallback: ancienne logique (hex->palette)
            hex_codes = assoc.get("color_hex", [])
            color_names = assoc.get("colors", [])
            color_details = []

            if isinstance(hex_codes, list) and hex_codes:
                for hex_code in hex_codes:
                    found = None
                    for color in palette:
                        if color.get("hex") == hex_code:
                            found = {
                                "name": color.get("name", ""),
                                "displayName": color.get("displayName", ""),
                                "hex": hex_code,
                            }
                            break
                    if found:
                        color_details.append(found)

            transformed = {
                "occasion": assoc.get("occasion", ""),
                "description": assoc.get("description", ""),
                "colors": color_names,
                "color_hex": hex_codes,
                "color_details": color_details,
                "image_url": assoc.get("image_url"),
                "image_filename": assoc.get("image_filename"),
            }
            enriched.append(transformed)

        return enriched

    @staticmethod
    def _transform_nail_colors(nail_colors: list, palette: list) -> list:
        """Transforme nail colors avec enrichissement"""
        transformed = []
        
        for nail_color in nail_colors:
            if isinstance(nail_color, dict):
                hex_code = nail_color.get("hex", nail_color.get("color_hex", "#FF69B4"))
                
                found = None
                for color in palette:
                    if color.get("hex") == hex_code:
                        found = color
                        break
                
                if not found:
                    found = {
                        "name": nail_color.get("name", "Couleur"),
                        "displayName": nail_color.get("displayName", PDFDataMapper.generate_display_name(nail_color.get("name", "Couleur"))),
                        "hex": hex_code,
                    }
                
                transformed.append(found)
        
        return transformed

# ═══════════════════════════════════════════════════════════════
    # MAPPING KEYWORD → nom_simplifie (basé sur vraies données Supabase)
    # Table visuels : 36 images disponibles
    # ═══════════════════════════════════════════════════════════════
    MORPHO_MVP_KEYWORD_MAP = {
        "haut": [
            (["col en v", "col v", "encolure en v", "decollete en v", "cache-coeur", "cache coeur", "blouse", "chemisier"], "encolure_en_v"),
            (["encolure bateau", "col bateau"], "encolure_bateau"),
            (["encolure carree", "col carre", "col carré"], "encolure_carree"),
            (["manches bouffantes", "bouffantes", "bouffant"], "manches_bouffantes"),
            (["chauve-souris", "chauve souris", "chauve_souris"], "manches_chauve_souris"),
            (["top fluide", "blouse fluide", "chemise fluide"], "top_fluide"),
            (["fluide"], "top_fluide"),
            (["col roule", "col roul", "col roulé"], "pull_col_roul"),
            (["pull", "sweat"], "pull_col_roul"),
            (["epaulettes", "epaulette", "epaule structuree", "epaule structure"], "haut_epaulettes"),
            (["peplum", "cintree", "cintre"], "haut_cintre"),
            (["gilet"], "gilet_long"),
            (["debardeur"], "debardeur_long"),
        ],
        "bas": [
            (["jupe crayon", "crayon taille haute", "crayon"], "jupe_crayon"),
            (["jupe trapeze", "trapeze"], "jupe_trapeze"),
            (["jupe patineuse", "patineuse"], "jupe_patineuse"),
            (["palazzo", "evase", "evasee", "large", "ample"], "pantalon_flare"),
            (["flare"], "pantalon_flare"),
            (["bootcut"], "pantalon_bootcut"),
            (["droit taille", "droit", "chino", "cigarette"], "pantalon_droit"),
            (["slim", "skinny"], "jean_slim"),
            (["carotte"], "pantalon_carotte"),
            (["short"], "short_taille_haute"),
            (["jean"], "jean_slim"),
        ],
        "robe": [
            (["portefeuille"], "robe_portefeuille"),
            (["empire"], "robe_empire"),
            (["patineuse"], "robe_patineuse"),
            (["bustier"], "robe_bustier"),
            (["chemise"], "robe_chemise"),
            (["droite"], "robe_droite"),
        ],
        "veste": [
            (["blazer", "cintree", "cintre"], "blazer_cintre"),
            (["courte"], "veste_courte"),
            (["trench", "mi-long", "mi long", "long"], "veste_mi_longue"),
            (["oversized", "oversize"], "veste_oversized"),
        ],
        "accessoire": [
            (["ceinture fine"], "ceinture_fine"),
            (["ceinture large"], "ceinture_large"),
            (["ceinture moyenne"], "ceinture_moyenne"),
            (["ceinture obi"], "ceinture_obi"),
            (["ceinture tressee", "ceinture tress", "ceinture tressée"], "ceinture_tressee"),
            (["ceinture"], "ceinture_fine"),   # fallback générique
        ],
    }

    @staticmethod
    def _normalize_for_matching(s: str) -> str:
        """Supprime accents + met en minuscule pour matching robuste."""
        s = s.lower()
        for fr, en in [('é','e'),('è','e'),('ê','e'),('ë','e'),('à','a'),('â','a'),
                       ('î','i'),('ï','i'),('ô','o'),('û','u'),('ù','u'),('ü','u'),('ç','c')]:
            s = s.replace(fr, en)
        return s

    @staticmethod
    def _find_visual_key_for_piece(name: str, supabase_category: str) -> str:
        """Retourne le nom_simplifie Supabase correspondant au nom de pièce, ou '' si aucun match."""
        if not name:
            return ""
        name_norm = PDFDataMapper._normalize_for_matching(name)
        for keywords, visual_key in PDFDataMapper.MORPHO_MVP_KEYWORD_MAP.get(supabase_category, []):
            if any(kw in name_norm for kw in keywords):
                return visual_key
        return ""

    @staticmethod
    def _enrich_mvp_essentials_with_visuals(essentials: dict) -> dict:
        """
        Enrichit chaque item de morphology_mvp.essentials avec visual_url
        depuis la table Supabase visuels via keyword matching sur le nom.

        Mapping catégories MVP → catégories Supabase :
          tops             → haut
          bottoms          → bas
          dresses_jackets  → robe puis veste (fallback)
          shoes_accessories→ accessoire
        """
        CATEGORY_MAP = {
            "tops":              ["haut"],
            "bottoms":           ["bas"],
            "dresses_jackets":   ["robe", "veste"],   # essaie robe d'abord, puis veste
            "shoes_accessories": ["accessoire"],
        }

        enriched = {}

        for mvp_cat, supabase_cats in CATEGORY_MAP.items():
            items = PDFDataMapper._safe_list(essentials.get(mvp_cat, []))
            enriched_items = []

            for item in items:
                if not isinstance(item, dict):
                    continue

                name = item.get("name", "")
                visual_key = ""

                # Tente chaque catégorie Supabase dans l'ordre
                for supabase_cat in supabase_cats:
                    visual_key = PDFDataMapper._find_visual_key_for_piece(name, supabase_cat)
                    if visual_key:
                        break

                # Récupère l'URL via visuals_service
                visual_url = ""
                if visual_key:
                    try:
                        visual_url = visuals_service.get_url(visual_key) or ""
                    except Exception as e:
                        print(f"⚠️ visuals_service.get_url('{visual_key}'): {e}")

                enriched_item = {**item, "visual_key": visual_key, "visual_url": visual_url}
                enriched_items.append(enriched_item)

                status = "✅" if visual_url else "⚠️ NO IMG"
                print(f"   {status} MVP [{mvp_cat}] '{name}' → key='{visual_key}'")

            enriched[mvp_cat] = enriched_items

        return enriched

    @staticmethod
    def prepare_liquid_variables(report_data: dict, user_data: dict) -> dict:
        """Prépare variables Liquid pour PDFMonkey - VERSION CORRIGÉE"""
        
        colorimetry_raw = PDFDataMapper._safe_dict(report_data.get("colorimetry", {}))
        morphology_raw = PDFDataMapper._safe_dict(report_data.get("morphology", {}))
        morphology_mvp = PDFDataMapper._safe_dict(morphology_raw.get("morphology_mvp", {}))
        # ✅ Styling = schéma V3 (source of truth)
        styling_raw = PDFDataMapper._safe_dict(report_data.get("styling", {}))

        # ✅ Safety defaults V3 pour Liquid (évite erreurs sur .size / for-loops)
        # IMPORTANT: on FORCE les sous-blocs à être des dicts, même si la source contient None/str/etc.

        # --- page16 / page17 safety defaults (évite placeholders "—" inutiles)
        styling_raw["page16"] = PDFDataMapper._safe_dict(styling_raw.get("page16", {}))
        styling_raw["page17"] = PDFDataMapper._safe_dict(styling_raw.get("page17", {}))

        styling_raw["page17"].setdefault("style_name", "")
        styling_raw["page17"].setdefault("style_mix", [])
        styling_raw["page17"].setdefault("style_explained_text", "")
        styling_raw["page17"].setdefault("wardrobe_impact_text", "")
        styling_raw["page17"].setdefault("style_tagline", "")
        styling_raw["page17"].setdefault("constraints_text", "")

        # --- page18.categories.*
        styling_raw["page18"] = PDFDataMapper._safe_dict(styling_raw.get("page18", {}))
        styling_raw["page18"]["categories"] = PDFDataMapper._safe_dict(styling_raw["page18"].get("categories", {}))
        styling_raw["page18"]["categories"].setdefault("tops", [])
        styling_raw["page18"]["categories"].setdefault("bottoms", [])
        styling_raw["page18"]["categories"].setdefault("dresses_playsuits", [])
        styling_raw["page18"]["categories"].setdefault("outerwear", [])

        # --- page19.categories.*
        styling_raw["page19"] = PDFDataMapper._safe_dict(styling_raw.get("page19", {}))
        styling_raw["page19"]["categories"] = PDFDataMapper._safe_dict(styling_raw["page19"].get("categories", {}))
        styling_raw["page19"]["categories"].setdefault("swim_lingerie", [])
        styling_raw["page19"]["categories"].setdefault("shoes", [])
        styling_raw["page19"]["categories"].setdefault("accessories", [])

        # ---------------------------------------------------------------------
        # STYLING VISUALS + PRODUCT MATCH (PAGES 18-19)
        # ---------------------------------------------------------------------
 


        def _apply_fallback_visuals(items: list) -> list:
            """
            Ajoute item.image_url (fallback pédagogique) si:
            - pas de match affilié (ou match.image_url vide)
            - et visual_key présent
            """
            out = []
            for it in items if isinstance(items, list) else []:
                if not isinstance(it, dict):
                    continue

                # Normalise
                it.setdefault("image_url", "")
                vk = (it.get("visual_key") or "").strip()

                # Si un match affilié existe, on laisse le HTML afficher match.image_url en priorité
                match = it.get("match") if isinstance(it.get("match"), dict) else None
                match_img = (match.get("image_url") if match else "") or ""

                # Si pas d'image affiliée, on met fallback visuel pédagogique via table `visuels`
                if not match_img and not it["image_url"] and vk:
                    # 1) tentative directe
                    fb = visuals_service.get_url(vk)

                    # 2) tentative normalisée (au cas où la DB a "jupe_evasee" vs "jupe_évasée")
                    if not fb:
                        vk2 = (vk or "").strip().lower()
                        vk2 = vk2.replace("é", "e").replace("è", "e").replace("ê", "e").replace("ë", "e")
                        vk2 = vk2.replace("à", "a").replace("â", "a")
                        vk2 = vk2.replace("î", "i").replace("ï", "i")
                        vk2 = vk2.replace("ô", "o")
                        vk2 = vk2.replace("ù", "u").replace("û", "u").replace("ü", "u")
                        fb = visuals_service.get_url(vk2)

                    if fb:
                        it["image_url"] = fb
                    else:
                        print(f"⚠️ No visual fallback for visual_key={vk!r}")


                out.append(it)
            return out


        # Page 18 - enrich affiliate matches
        for k in ["tops", "bottoms", "dresses_playsuits", "outerwear"]:
            items = styling_raw["page18"]["categories"].get(k, [])

            # 1) match affilié
            items = product_matcher_service.enrich_pieces(items, k)

            # 🔴 DEBUG TEMPORAIRE – À NE FAIRE QUE POUR tops
            if k == "tops" and items:
                import json
                print("\n🧪 DEBUG PAGE18 / TOPS (APRÈS enrich_pieces)")
                print(json.dumps(items[0], ensure_ascii=False, indent=2))

            # 2) fallback pédagogique si pas de match
            items = _apply_fallback_visuals(items)

            # 🔴 DEBUG TEMPORAIRE – APRÈS fallback
            if k == "tops" and items:
                import json
                print("\n🧪 DEBUG PAGE18 / TOPS (APRÈS fallback)")
                print(json.dumps(items[0], ensure_ascii=False, indent=2))

            styling_raw["page18"]["categories"][k] = items

        # Page 19 - enrich affiliate matches
        for k in ["swim_lingerie", "shoes", "accessories"]:
            items = styling_raw["page19"]["categories"].get(k, [])
            # 1) match affilié
            items = product_matcher_service.enrich_pieces(items, k)
            # 2) fallback pédagogique si pas de match
            items = _apply_fallback_visuals(items)
            styling_raw["page19"]["categories"][k] = items


        
        # Page 8 + nouvelle section morphologie MVP
        morphology_page1 = PDFDataMapper._transform_morphology_service_data(morphology_raw, user_data)

        # ═══════════════════════════════════════════════════════════
        # COLORIMETRY - CORRECTION COMPLÈTE PAGES 4, 5, 7
        # ═══════════════════════════════════════════════════════════
        
        # ✅ PAGE 3: Palette personnalisée (10 couleurs top 8-10/10)
        palette = PDFDataMapper._safe_list(colorimetry_raw.get("palette_personnalisee", []))
        palette = PDFDataMapper.enrich_with_display_names(palette)
        palette = sorted(palette, key=lambda x: x.get("note", 0), reverse=True)
        
        # ✅ PAGE 4: Couleurs génériques (Bleu, Rouge, Jaune, etc. - 7-10/10)
        # CORRECTION: Utiliser directement couleurs_generiques calculées par colorimetry
        couleurs_generiques = PDFDataMapper._safe_list(colorimetry_raw.get("couleurs_generiques", []))
        couleurs_generiques = PDFDataMapper.enrich_with_display_names(couleurs_generiques)
        
        # ✅ PAGE 5: Couleurs à manier avec prudence (4-6/10)
        # CORRECTION: Utiliser directement couleurs_prudence calculées par colorimetry
        couleurs_prudence = PDFDataMapper._safe_list(colorimetry_raw.get("couleurs_prudence", []))
        couleurs_prudence = PDFDataMapper.enrich_with_display_names(couleurs_prudence)
        
        # ✅ PAGE 5: Couleurs à éviter (<4/10)
        # CORRECTION: Utiliser directement couleurs_eviter calculées par colorimetry
        couleurs_eviter = PDFDataMapper._safe_list(colorimetry_raw.get("couleurs_eviter", []))
        couleurs_eviter = PDFDataMapper.enrich_with_display_names(couleurs_eviter)
        
        # ✅ FALLBACK: notes_compatibilite + allColorsWithNotes (pour référence)
        notes_compatibilite = PDFDataMapper._safe_dict(colorimetry_raw.get("notes_compatibilite", {}))
        all_colors_with_notes = PDFDataMapper._build_all_colors_with_notes(notes_compatibilite)
        all_colors_with_notes = PDFDataMapper.enrich_with_display_names(all_colors_with_notes)
        
        # ✅ PAGE 6: Associations de couleurs (occasions)
        associations = PDFDataMapper._safe_list(colorimetry_raw.get("associations_gagnantes", []))
        associations = PDFDataMapper._enrich_associations_with_colors(associations, palette)
        
        # Couleurs refusées
        unwanted_colors = PDFDataMapper._safe_list(colorimetry_raw.get("unwanted_colors", []))
        unwanted_colors = PDFDataMapper.enrich_with_display_names(unwanted_colors)
        
        alternatives = PDFDataMapper._safe_dict(colorimetry_raw.get("alternatives_couleurs_refusees", {}))
        
        # ═══════════════════════════════════════════════════════════
        # MAKEUP - CORRECTION PAGE 7
        # ═══════════════════════════════════════════════════════════
        # ✅ CORRIGÉ: Utiliser la structure makeup que colorimetry construit activement
        makeup_raw = PDFDataMapper._safe_dict(colorimetry_raw.get("makeup", {}))
        
        raw_nail_colors = PDFDataMapper._safe_list(colorimetry_raw.get("nailColors", []))
        nail_colors_transformed = PDFDataMapper._transform_nail_colors(raw_nail_colors, palette)
        
        makeup_mapping = {
            "foundation": makeup_raw.get("foundation", ""),
            "blush": makeup_raw.get("blush", ""),
            "bronzer": makeup_raw.get("bronzer", ""),
            "highlighter": makeup_raw.get("highlighter", ""),
            "eyeshadows": makeup_raw.get("eyeshadows", ""),
            "eyeliner": makeup_raw.get("eyeliner", ""),
            "mascara": makeup_raw.get("mascara", ""),
            "brows": makeup_raw.get("brows", ""),
            "lipsNatural": makeup_raw.get("lipsNatural", ""),
            "lipsDay": makeup_raw.get("lipsDay", ""),
            "lipsEvening": makeup_raw.get("lipsEvening", ""),
            "lipsAvoid": makeup_raw.get("lipsAvoid", ""),
            "nailColors": nail_colors_transformed,
        }
        
        # ✅ NOUVEAU: Shopping structure (vide car non fourni par colorimetry)
        shopping = {
            "priorite1": [],
            "priorite2": [],
            "eviterAbsolument": [],
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
                "effet_couleurs_froides": impact_visuel_raw.get("effet_couleurs_froides", impact_visuel_raw.get("effetCouleursFreides", "")),
            }
        }
        # ✅ Enrichissement visuels pédagogiques pour morphologie MVP
        print("\n🎨 Enrichissement visuels MVP morphologie...")
        essentials_raw = PDFDataMapper._safe_dict(morphology_mvp.get("essentials", {}))
        essentials_enriched = PDFDataMapper._enrich_mvp_essentials_with_visuals(essentials_raw)
        
        # BUILD LIQUID DATA
        liquid_data = {
            "user": {
                "firstName": user_data.get("user_name", "").split()[0] if user_data.get("user_name") else "",
                "lastName": user_data.get("user_name", "").split()[-1] if user_data.get("user_name") else "",
                "fullName": user_data.get("user_name", ""),
                "email": user_data.get("user_email", ""),
                "age": user_data.get("age", ""),
                "height": user_data.get("height", ""),
                "clothingSize": user_data.get("clothing_size", ""),
                "facePhotoUrl": user_data.get("face_photo_url", ""),  # ✅ Photo visage Page 2
            },
            
            "colorimetry": {
                "saison_confirmee": colorimetry_raw.get("saison_confirmee", ""),
                "sous_ton_detecte": colorimetry_raw.get("sous_ton_detecte", ""),
                "eye_color": colorimetry_raw.get("eye_color", user_data.get("eye_color", "")),
                "hair_color": colorimetry_raw.get("hair_color", user_data.get("hair_color", "")),
                
                # ✅ PAGE 3: Palette personnalisée (10 couleurs)
                "palette_personnalisee": palette,
                
                # ✅ PAGE 4: Couleurs génériques
                "couleurs_generiques": couleurs_generiques,
                
                # ✅ PAGE 5: Couleurs à manier avec prudence
                "couleurs_prudence": couleurs_prudence,
                
                # ✅ PAGE 5: Couleurs à éviter
                "couleurs_eviter": couleurs_eviter,
                
                "notes_compatibilite": notes_compatibilite,
                "allColorsWithNotes": all_colors_with_notes,
                "unwanted_colors": unwanted_colors,
                "alternatives_couleurs": alternatives,
                
                # ✅ PAGE 6: Associations de couleurs
                "associations_gagnantes": associations,
                
                "analyse_colorimetrique_detaillee": analyse_snake,
                "season": colorimetry_raw.get("saison_confirmee", ""),
                "topColors": ", ".join([c.get("displayName", c.get("name", "")) for c in palette[:4]]) if palette else "",
            },
            
            # ✅ PAGE 7: Makeup
            "makeup": makeup_mapping,
            
            # Shopping (structure vide mais présente)
            "shopping": shopping,
            
            # ✅ PAGE 8: Morphology page 1
            "morphology_page1": morphology_page1,
            
            "morphology": {
                "bodyType": morphology_raw.get("silhouette_type", ""),
                "objectiveShort": morphology_raw.get("objective_comment", "")[:50] + "..." if morphology_raw.get("objective_comment") else "",
            },
            
            # ✅ PAGES 9-15: Morpho categories
           
            "morphology_mvp": {
                "essentials": essentials_enriched,
                "avoid": PDFDataMapper._safe_list(morphology_mvp.get("avoid", [])),
                "outfit_formulas": PDFDataMapper._safe_list(morphology_mvp.get("outfit_formulas", [])),
                "shopping_priorities": PDFDataMapper._safe_list(morphology_mvp.get("shopping_priorities", [])),
            },
            
            "morphology_highlights": morphology_raw.get("highlights", {
                "announcement": "",
                "explanation": ""
            }),
            
            "morphology_minimizes": morphology_raw.get("minimizes", {  # ✅ AJOUTÉ - Parties à minimiser Page 8
                "announcement": "",
                "explanation": "",
                "tips": []
            }),
            
            "styling": {
                # ✅ NOUVEAU : Styling V3 (pages 16 → 24)
                "page16": PDFDataMapper._safe_dict(styling_raw.get("page16", {})),
                "page17": PDFDataMapper._safe_dict(styling_raw.get("page17", {})),
                "page18": PDFDataMapper._safe_dict(styling_raw.get("page18", {})),
                "page19": PDFDataMapper._safe_dict(styling_raw.get("page19", {})),
                "page20": PDFDataMapper._safe_dict(styling_raw.get("page20", {})),
                "pages21_23": PDFDataMapper._safe_dict(styling_raw.get("pages21_23", {})),
                "page24": PDFDataMapper._safe_dict(styling_raw.get("page24", {})),
            },

            "styling_products": {
                "enabled": False,
                "selection": {
                    "everyday": [],
                    "academic_or_professional": [],
                    "events": [],
                    "capsule_essentials": [],
                    "capsule_hero_pieces": [],
                }
            },

            "currentDate": datetime.now().strftime("%d %b %Y"),
        }
        
        print(f"\n✅ Mapper v5.3 (CORRIGÉ - Pages 4, 5, 7):")
        print(f"   ✓ Palette: {len(palette)} couleurs")
        print(f"   ✓ Couleurs génériques: {len(couleurs_generiques)} couleurs")
        print(f"   ✓ Couleurs prudence: {len(couleurs_prudence)} couleurs")
        print(f"   ✓ Couleurs à éviter: {len(couleurs_eviter)} couleurs")
        print(f"   ✓ Associations: {len(associations)} enrichies")
        print(f"   ✓ Makeup: {sum(1 for v in makeup_mapping.values() if v)} champs remplis")
        print(f"   ✓ Morphology MVP essentials: {list(PDFDataMapper._safe_dict(morphology_mvp.get('essentials', {})).keys())}")
        print(f"   ✓ Morphology MVP avoid: {len(PDFDataMapper._safe_list(morphology_mvp.get('avoid', [])))} items")
        print(f"   ✓ Morphology MVP formulas: {len(PDFDataMapper._safe_list(morphology_mvp.get('outfit_formulas', [])))} items")

        # ---------------------------------------------------------------------
        # PAGE 16 - UNIVERS VISUEL (style_visuals) - EXACTEMENT 9 VISUELS
        # ---------------------------------------------------------------------
        try:
            page16 = PDFDataMapper._safe_dict(styling_raw.get("page16", {}))
            archetype = (page16.get("archetype_title") or "").strip()

            # Si pas d'archetype_title, on laisse vide (le template affichera les placeholders)
            if archetype:
                style_visuals = get_style_visuals_for_archetype(archetype=archetype)
            else:
                style_visuals = []

            # Variable attendue par ton HTML page 16: {% if style_visuals ... %}
            liquid_data["style_visuals"] = style_visuals

            print(f"   ✓ style_visuals: {len(style_visuals)} items (archétype='{archetype}')")

        except Exception as e:
            print(f"⚠️  Erreur style_visuals: {e}")
            liquid_data["style_visuals"] = []

        # ---------------------------------------------------------------------
        # PAGE 17 - VISUELS DE STYLE (style_visuals_page17) - 9 VISUELS
        # ---------------------------------------------------------------------
        try:
            page17 = PDFDataMapper._safe_dict(styling_raw.get("page17", {}))

            def _norm(s: str) -> str:
                if not s:
                    return ""
                s = str(s).strip().lower()
                s = s.replace("&", "and")
                s = " ".join(s.split())
                return s

            style_name = (page17.get("style_name") or "").strip()
            sm = page17.get("style_mix") or []

            top_style = ""
            if isinstance(sm, list) and len(sm) > 0 and isinstance(sm[0], dict):
                top_style = (sm[0].get("style") or "").strip()

            # -------- LOGS AVANT --------
            print("\n🧩 PAGE17 VISUALS DEBUG (BEFORE SELECTOR)")
            print(f"   • page17.style_name = {style_name!r}")
            print(f"   • page17.style_mix  = {sm!r}")
            print(f"   • extracted top_style = {top_style!r}")

            candidates = []
            if style_name:
                candidates.append(style_name)   # ex: "Romantisme Minimaliste"
            if top_style:
                candidates.append(top_style)    # ex: "Minimaliste"

            seen = set()
            candidates = [c for c in candidates if c and not (_norm(c) in seen or seen.add(_norm(c)))]

            print(f"   • candidates = {candidates!r}")

            style_visuals_page17 = []
            chosen = ""

            for cand in candidates:
                chosen = cand
                print(f"\n   ▶ trying style_label={cand!r}")
                style_mix = page17.get("style_mix") or []
                style_visuals_page17 = get_style_visuals_for_style_mix(style_mix=style_mix, season="all", total=9)


                print(f"     • selector returned: {len(style_visuals_page17)} items")
                if style_visuals_page17 and isinstance(style_visuals_page17[0], dict):
                    print(f"     • first item keys: {list(style_visuals_page17[0].keys())}")
                    print(f"     • first url: {style_visuals_page17[0].get('url')}")

                if style_visuals_page17:
                    break

            cleaned = []
            for v in style_visuals_page17:
                if isinstance(v, dict):
                    url = (v.get("url") or "").strip()
                    label = (v.get("label") or v.get("title") or "").strip()
                    if url.endswith("?"):
                        url = url[:-1]
                    if url:
                        cleaned.append({"url": url, "label": label})

            liquid_data["style_visuals_page17"] = cleaned

            # -------- LOGS APRÈS --------
            print("\n🧩 PAGE17 VISUALS DEBUG (AFTER CLEAN)")
            print(f"   ✓ chosen='{chosen}'")
            print(f"   ✓ cleaned count={len(cleaned)}")
            if cleaned:
                print(f"   ✓ first cleaned url={cleaned[0]['url']}")

            print("\n🔎 LIQUID ROOT KEYS CHECK")
            print("   • has style_visuals_page17:", "style_visuals_page17" in liquid_data)
            print("   • style_visuals_page17 len:", len(liquid_data.get('style_visuals_page17', [])))

        except Exception as e:
            print(f"⚠️  Erreur style_visuals_page17: {e}")
            liquid_data["style_visuals_page17"] = []


        return liquid_data

    @staticmethod
    def _transform_morphology_service_data(morphology_raw: dict, user_data: dict) -> dict:
        """Transforme morphology_service.analyze() en données page 8."""
        silhouette_type = morphology_raw.get("silhouette_type", "")
        silhouette_explanation = morphology_raw.get("silhouette_explanation", "")
        styling_objectives = PDFDataMapper._safe_list(morphology_raw.get("styling_objectives", []))

        waist = user_data.get("waist_circumference", 0) or 0
        shoulders = user_data.get("shoulder_circumference", 0) or 0
        hips = user_data.get("hip_circumference", 0) or 0

        hips_float = float(hips) if hips else 0
        shoulders_float = float(shoulders) if shoulders else 0
        waist_float = float(waist) if waist else 0

        waist_hip_ratio = round(waist_float / hips_float, 2) if hips_float > 0 else ""
        waist_shoulder_ratio = round(waist_float / shoulders_float, 2) if shoulders_float > 0 else ""

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
            "goals": styling_objectives if styling_objectives else ["Créer une silhouette harmonieuse"],
            "photos": {
                "body": user_data.get("body_photo_url", "")
            },
        }

    @staticmethod
    def _generate_morphology_categories(morphology_raw: dict, user_data: dict) -> dict:
        """
        ✅ v5.3 FIXED: Utilise les VRAIES recommendations d'OpenAI Part 2
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
        
        # Remplace intégralement le bloc "for category_name in category_names:" dans
        # PDFDataMapper._generate_morphology_categories() (fichier pdf_data_mapper.py)
        # par ce bloc-ci, SANS aucune ligne de diff.

        for category_name in category_names:
            # Récupérer depuis OpenAI s'il existe (safe)
            openai_cat_data = PDFDataMapper._safe_dict(openai_recommendations.get(category_name, {}))

            # ------------------------------------------------------------------
            # NORMALISATION ULTRA-ROBUSTE (types + clés alternatives)
            # ------------------------------------------------------------------
            def _list_to_html(items):
                """Convertit liste(str|dict) -> HTML léger (compatible | raw)."""
                if not items:
                    return ""
                out = []
                for x in items:
                    if isinstance(x, str):
                        out.append(x.strip())
                    elif isinstance(x, dict):
                        # tolérance: {"title": "...", "text": "..."} ou {"label": "..."}
                        title = (x.get("title") or x.get("label") or x.get("name") or "").strip()
                        text = (x.get("text") or x.get("why") or x.get("desc") or "").strip()
                        if title and text:
                            out.append(f"<strong>{title}</strong> : {text}")
                        elif title:
                            out.append(f"<strong>{title}</strong>")
                        elif text:
                            out.append(text)
                # rendu simple (PDF friendly)
                return "<br>".join([s for s in out if s])

            # Recommandés / À éviter : accepter plusieurs noms de clés selon versions
            recommandes_raw = (
                openai_cat_data.get("recommandes")
                or openai_cat_data.get("a_privilegier")
                or openai_cat_data.get("pieces_recommandees")
                or []
            )
            a_eviter_raw = (
                openai_cat_data.get("a_eviter")
                or openai_cat_data.get("pieces_a_eviter")
                or []
            )

            # Matières : peut arriver en str OU list => on force str HTML
            matieres_raw = openai_cat_data.get("matieres", "")
            if isinstance(matieres_raw, list):
                matieres_str = _list_to_html(matieres_raw)
            elif isinstance(matieres_raw, dict):
                # rare: dict de listes/strings
                matieres_str = _list_to_html(matieres_raw.get("items") or []) or str(matieres_raw)
            else:
                matieres_str = str(matieres_raw or "")

            if not matieres_str.strip():
                matieres_str = "Privilégier les matières de qualité."

            # Motifs : peut être dict(str), dict(list), list, str => on force dict(str,str)
            motifs_raw = openai_cat_data.get("motifs", {})
            motifs_obj = {"recommandes": "", "a_eviter": ""}

            if isinstance(motifs_raw, dict):
                rec = motifs_raw.get("recommandes", motifs_raw.get("a_privilegier", ""))
                avoid = motifs_raw.get("a_eviter", "")
                if isinstance(rec, list):
                    motifs_obj["recommandes"] = _list_to_html(rec)
                else:
                    motifs_obj["recommandes"] = str(rec or "")
                if isinstance(avoid, list):
                    motifs_obj["a_eviter"] = _list_to_html(avoid)
                else:
                    motifs_obj["a_eviter"] = str(avoid or "")
            elif isinstance(motifs_raw, list):
                # si on reçoit une liste unique, on la met côté "recommandes"
                motifs_obj["recommandes"] = _list_to_html(motifs_raw)
                motifs_obj["a_eviter"] = ""
            else:
                # string brute
                motifs_obj["recommandes"] = str(motifs_raw or "")
                motifs_obj["a_eviter"] = ""

            if not motifs_obj["recommandes"].strip():
                motifs_obj["recommandes"] = "Motifs discrets, rayures verticales, petits imprimés, dégradés"
            if not motifs_obj["a_eviter"].strip():
                motifs_obj["a_eviter"] = "Gros motifs, rayures horizontales, imprimés trop clairs"

            # Pièges : normaliser list
            pieges_list = PDFDataMapper._safe_list(
                openai_cat_data.get("pieges", openai_cat_data.get("traps", []))
            )

            # Introduction
            intro = openai_cat_data.get(
                "introduction",
                f"Pour votre silhouette {silhouette_type}, découvrez les pièces recommandées."
            )

            # ✅ Créer la structure pour le template (types garantis)
            categories_data[category_name] = {
                "introduction": str(intro or ""),
                "recommandes": PDFDataMapper._safe_list(recommandes_raw),
                "a_eviter": PDFDataMapper._safe_list(a_eviter_raw),
                "matieres": matieres_str,
                "motifs": motifs_obj,
                "pieges": pieges_list,
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

            if enriched_recommandes:
                            print(f"🧪 VISUALS CHECK [{category_name}] first:", {
                                "cut_display": enriched_recommandes[0].get("cut_display"),
                                "visual_key": enriched_recommandes[0].get("visual_key"),
                                "image_url": (enriched_recommandes[0].get("image_url") or "")[:80],
                            })

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