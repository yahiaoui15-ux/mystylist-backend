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

    # MAPPING KEYWORD → nom_simplifie (basé sur vraies données Supabase)
    # Table visuels : 36 images disponibles
    # ═══════════════════════════════════════════════════════════════
    MORPHO_MVP_KEYWORD_MAP = {
 
        # ── HAUTS ────────────────────────────────────────────────────────────
        "haut": [
            # ── Col en V ──
            (["pull ajuste col v", "pull col en v", "pull col v", "pull en v"], "pull_ajuste_col_v"),
            (["top col v ajuste", "col v ajuste"], "top_col_v_ajuste"),
            (["top col v", "top col en v", "col en v", "encolure en v",
              "decollete en v", "encolure v"], "top_col_v"),
            (["blouse col en v", "blouse col v", "encolure en v blouse"], "encolure_en_v"),
            # ── Col en U ──  ← NOUVEAU
            (["tshirt en u", "t-shirt en u", "tee en u", "top en u",
            "encolure en u", "col en u", "encolure u",
            "blouse en u", "top encolure u", "col u",
            "pull en u", "pull u", "pull col u"], "top_encolure_u"),
            # ── Cache-cœur ──
            (["top col cache coeur", "top cache coeur col"], "top_col_cache_coeur"),
            (["cache-coeur", "cache coeur", "cachecoeur", "top cache coeur",
              "blouse cache coeur"], "top_cache_coeur"),
            (["wrap top", "haut wrap", "top portefeuille", "wrap"], "top_cache_coeur"),


            # ── Col bateau / bardot ──
            (["top col bateau brillant"], "top_col_bateau_brillant"),
            (["top col bateau", "col bateau top"], "top_col_bateau"),
            (["encolure bateau", "col bateau", "bateau"], "encolure_bateau"),
            (["tshirt col bardot", "t-shirt bardot", "bardot"], "tshirt_col_bardot"),
            # ── Col carré ──
            (["top col carre", "col carre top"], "top_col_carre"),
            (["encolure carree", "col carre"], "encolure_carree"),
            # ── Épaules froncées / épaulettes ──
            (["chemise epaules froncees", "epaules froncees"], "chemise_epaules_froncees"),
            (["tshirt fronce epaules", "t-shirt fronce epaules", "fronce aux epaules"], "tshirt_fronce_epaules"),  # NOUVEAU
            (["top manches courtes epaulettes", "epaulettes manches courtes"], "top_manches_courtes_a_epaulettes"),
            (["top epaulettes", "top a epaulettes"], "top_a_epaulettes"),
            (["epaulettes", "epaulette", "epaule structur"], "haut_epaulettes"),
            # ── Manches bouffantes ──
            (["blouse imprimee manches bouffantes"], "blouse_imprimee_manches_bouffantes"),
            (["top manches longues bouffantes", "manches longues bouffantes"], "top_manches_longues_bouffantes"),
            (["top cintre manches courtes bouffantes", "cintre manches bouffantes"], "top_cintre_manches_courtes_bouffantes"),
            (["manches bouffantes", "bouffantes", "bouffant"], "manches_bouffantes"),
            # ── Raglan ──  ← NOUVEAU
            (["top raglan", "raglan"], "top_raglan"),
            # ── Chauve-souris ──
            (["pull manches chauve souris"], "pull_manches_chauve_souris"),
            (["chauve-souris", "chauve souris"], "manches_chauve_souris"),
            # ── Peplum ──
            (["top peplum oversize", "peplum oversize"], "top_peplum_oversize"),
            (["top denim peplum", "peplum denim"], "top_denim_peplum"),
            (["top peplum", "peplum leger", "top peplum leger", "peplum"], "top_peplum"),
            # ── Drapé ──  ← NOUVEAU
            (["top drape", "top drapé", "top drapee", "haut drape"], "top_drape"),
            (["tshirt drape", "t-shirt drape", "tshirt drapé"], "tshirt_drape_col_rond"),
            # ── Taille froncée ──  ← NOUVEAU
            (["tshirt taille froncee", "t-shirt taille froncee", "taille froncee"], "tshirt_taille_froncee"),
            # ── Tunique ──  ← NOUVEAU
            (["tunique ample", "tunique chiffon", "tunique fluide",
            "tunique longue", "tunique"], "tunique_sombre"),
            (["tunique ceinturee", "tunique ceinturée"], "tunique_ceinturee"),
            (["tunique boutonnee", "tunique boutonnée"], "tunique_boutonee_unie"),
            # ── Encolure américaine ──  ← NOUVEAU
            (["encolure americaine", "dos nu", "dos nageur"], "top_encolure_americaine"),
            # ── Cintrés ──
            (["haut cintre"], "haut_cintre"),
            (["top cintre manches courtes", "top cintre"], "top_cintre"),
            # ── Chemises / blouses ──
            (["chemise cintree", "chemisier cintre"], "chemise_cintree"),
            (["chemise droite fluide imprimee", "chemise fluide imprimee"], "chemise_droite_fluide_imprimee"),
            (["chemise droite fluide", "chemisier fluide", "chemise fluide",
              "chemisier", "blouse fluide"], "chemise_droite_fluide"),
            (["chemise oversize rayee"], "chemise_oversize_rayee"),
            (["chemise oversize souple", "chemise oversize"], "chemise_oversize_souple"),
            (["blouse droite satinee", "blouse droite", "blouse satinee"], "blouse_droite_satinee"),
            (["blouse"], "blouse_droite_satinee"),
            # ── Rayures horizontales ──
            (["rayures horizontales", "haut rayures horizontales", "top rayures"], "haut_rayures_horizontales"),
            # ── Top fluide générique ──
            (["top col rond fluide"], "top_col_rond_fluide"),
            (["top fluide", "haut fluide"], "top_fluide"),
            (["fluide"], "chemise_droite_fluide"),
            # ── Bénitier ──
            (["col benitier", "benitier"], "top_sans_manches_col_benitier"),
            (["col benitier", "benitier", "sans manches col benitier"], "top_sans_manches_col_benitier"),
            (["pull col benitier", "pull benitier"], "top_sans_manches_col_benitier"),
            (["pull col"], "pull_col_roul"),
            (["pull en maille", "pull maille", "pull"], "pull_col_roul"),
            # ── Pull / col roulé ──
            (["pull col roule", "pull col roul"], "pull_col_roule"),
            (["pull col"], "pull_col_roul"),
            (["pull en maille", "pull maille", "pull"], "pull_col_roul"),
            # ── Cardigan ──
            (["cardigan", "gilet en maille", "gilet laine"], "cardigan_laine"),
            # ── Débardeur ──
            (["top debardeur long"], "top_debardeur_long"),
            (["debardeur long", "debardeur"], "debardeur_long"),
            # ── Col montant ──
            (["col montant creme"], "top_col_montant_creme"),
            (["col montant"], "top_col_montant"),
            # ── Col tailleur ──
            (["col tailleur"], "top_col_tailleur"),
            # ── Sweat ──
            (["sweat"], "pull_col_roul"),
        ],
 
        # ── BAS ───────────────────────────────────────────────────────────────
        "bas": [
            # ── Jupes ──
            (["jupe crayon taille haute", "jupe crayon"], "jupe_crayon"),
            (["jupe droite taille haute"], "jupe_droite_taille_haute"),  # NOUVEAU
            (["jupe droite classique", "jupe droite enfilable"], "jupe_droite_classique_enfilable"),  # NOUVEAU
            (["jupe droite"], "jupe_droite_taille_haute"),
            (["jupe midi portefeuille", "jupe portefeuille midi"], "jupe_midi_portefeuille"),
            (["jupe froncee", "jupe froncée", "jupe volantee"], "jupe_froncee"),  # NOUVEAU
            (["jupe trapeze", "trapeze", "jupe A-line"], "jupe_trapeze"),
            (["jupe patineuse", "patineuse"], "jupe_patineuse"),
            (["jupe longue fluide", "jupe maxi", "jupe longue"], "jupe portefeuille midi"),
            (["jupe plissee", "jupe plissée"], "jupe_patineuse"),
            (["jupe longue fluide", "jupe maxi", "jupe longue"], "jupe portefeuille midi"),
            (["jupe midi evasee", "jupe midi évasée", "jupe evasee", "jupe évasée",
              "jupe evase", "jupe trapeze midi"], "jupe_trapeze"),
            # ── Pantalons larges ──
            (["pantalon palazzo fluide beige"], "pantalon_palazzo_fluide_beige"),
            (["pantalon palazzo fluide"], "pantalon_palazzo_fluide_beige"),
            (["palazzo", "pantalon palazzo"], "pantalon_palazzo"),
            (["pantalon large fluide", "large fluide"], "pantalon_large_fluide"),
            (["pantalon evase", "pantalon évasé", "evase", "evasee"], "pantalon_evase"),  # NOUVEAU
            (["flare"], "pantalon_flare"),
            (["bootcut"], "pantalon_bootcut"),
            (["carotte", "pantalon carotte"], "pantalon_carotte"),
            # ── Jeans ──
            (["jean droit taille haute"], "jean_droit_taille_haute"),
            (["jean mom", "mom jean"], "jean_mom"),  # NOUVEAU
            (["jean skinny gris", "skinny gris"], "jean_skinny_gris"),  # NOUVEAU
            (["jean slim", "skinny", "slim"], "jean_slim"),
            (["jean taille mi haute"], "jean_taille_mi_haute"),
            (["jean large", "jean boyfriend", "boyfriend"], "jean_droit_taille_haute"),
            (["jean"], "jean_droit_taille_haute"),
            # ── Legging ──
            (["legging cuir", "legging sculptant"], "legging_cuir_sculptant"),  # NOUVEAU
            (["legging"], "legging_cuir_sculptant"),
            # ── Bermuda / short ──
            (["bermuda cargo"], "bermuda_cargo_ceinture"),  # NOUVEAU
            (["bermuda taille haute", "bermuda"], "bermuda_taille_haute"),  # NOUVEAU
            (["short"], "short_taille_haute"),
            # ── Pantalons droits ──
            (["pantalon taille haute droit"], "pantalon_taille_haute_droit"),
            (["pantalon taille haute"], "pantalon_taille_haute"),
            (["pantalon droit", "droit", "chino", "cigarette"], "pantalon_droit"),
        ],
 
        # ── ROBES ────────────────────────────────────────────────────────────
        "robe": [
            (["robe portefeuille"], "robe_portefeuille"),
            (["robe empire"], "robe_empire"),
            (["robe patineuse"], "robe_patineuse"),
            (["robe bustier"], "robe_bustier"),
            (["robe chemise denim"], "robe_chemise_denim"),
            (["robe chemise"], "robe_chemise"),
            (["robe drapee", "robe drapée", "robe asymetrique"], "robe_drapee"),  # NOUVEAU
            (["robe courte fluide"], "robe_courte_fluide"),  # NOUVEAU
            (["robe courte cache coeur ceinturee"], "robe_courte_cache_coeur_ceinturee"),
            (["robe courte cintree ceinturee"], "robe_courte_cintree_ceinturee"),
            (["robe fourreau", "fourreau"], "robe_fourreau"),
            (["robe longue legere bretelles", "longue bretelles"], "robe_longue_legere_bretelles"),  # NOUVEAU
            (["robe longue ceinturee motif", "longue ceinturee motif"], "robe_longue_ceinturee_motif_leopoard"),
            (["robe longue fluide fleurs", "longue fluide fleurs"], "robe_longue_fluide_fleurs"),
            (["robe midi ceinturee velours"], "robe_midi_ceinturee_velours"),
            (["robe midi oversize"], "robe_midi_oversize"),
            (["robe midi plissee", "midi plissee"], "robe_midi_plissee"),
            (["robe moulante col v"], "robe_moulante_col_v"),
            (["robe moulante", "moulante"], "robe_moulante_col_rond"),
            (["robe a line", "a-line", "a line", "robe evase"], "robe_a_line"),
            (["robe droite", "droite"], "robe_droite"),
            (["tunique sombre", "tunique longue sombre"], "tunique_sombre"),  # NOUVEAU
            # ── Combinaisons ──  ← NOUVEAU
            (["combinaison pantalon droite", "combinaison pantalon"], "combinaison_pantalon_droite"),
            (["combinaison jambes plissee", "combinaison plissee"], "combinaison_jambes_plissee"),
            (["combinaison fluide manches courtes", "combinaison fluide"], "combinaison_fluide_manches_courtes"),
            (["combinaison dentelle col v", "combinaison dentelle"], "combinaison_dentelle_col_v"),
            (["combinaison jean bretelles", "combinaison jean"], "combinaison_jean_bretelles"),
            (["combi short cache coeur", "combi short"], "combi_short_cache_coeur"),
            (["combinaison", "combi"], "combinaison_pantalon_droite"),
        ],
 
        # ── VESTES ───────────────────────────────────────────────────────────
        "veste": [
            (["blazer cintre", "veste cintree", "veste cintre"], "blazer_cintre"),
            (["blazer structure", "blazer structuré"], "blazer_structure"),  # NOUVEAU
            (["veste structuree", "veste structurée"], "veste_structuree"),  # NOUVEAU
            (["veste ceinturee rayures cachemire"], "veste_ceinturee_rayures_cachemire"),
            (["veste ceinturee", "ceinturee"], "veste_ceinturee"),
            (["veste blazer droite noire"], "veste_blazer_droite_noire"),
            (["veste blazer droite", "blazer droit"], "veste_blazer_droite"),
            (["veste perfecto", "perfecto"], "veste_perfecto_cuir"),
            (["veste courte", "courte"], "veste_courte"),
            (["veste longue", "longue"], "veste_longue"),
            (["veste mi longue", "trench mi long"], "veste_mi_longue"),
            (["veste oversize", "veste oversized", "oversized"], "veste_oversize"),
            (["blouson boutonne tweed", "blouson tweed", "tweed"], "blouson_boutonne_tweed"),  # NOUVEAU
            (["blouson court motard", "perfecto court", "motard"], "blouson_court_motard_simili"),  # NOUVEAU
            (["blouson court zippe", "blouson zippe"], "blouson_court_zippe_capuche_velours"),  # NOUVEAU
            (["blouson sherpa", "sherpa trucker", "trucker"], "blouson_sherpa_trucker"),  # NOUVEAU
            (["doudoune court capuche", "doudoune courte fourrure"], "doudoune_court_capuche_fourrure"),  # NOUVEAU
            (["doudoune courte", "doudoune court"], "doudoune_courte_pressionnee"),  # NOUVEAU
            (["doudoune longue capuche", "doudoune longue"], "doudoune_longue_capuche"),  # NOUVEAU
            (["doudoune"], "doudoune_courte_pressionnee"),
            (["veste matelassee", "veste matelassée"], "veste_matelassee_courte_imprimee"),  # NOUVEAU
            (["cardigan long", "gilet long"], "gilet_long"),
            (["blazer"], "blazer_cintre"),
            (["trench"], "veste_mi_longue"),
        ],
 
        # ── MANTEAUX ─────────────────────────────────────────────────────────
        "manteau": [
            (["duffle coat capuche"], "duffle_coat_capuche"),
            (["duffle coat", "duffle"], "duffle_coat"),
            (["manteau ceinture"], "manteau_ceinture"),
            (["manteau droit"], "manteau_droit"),
            (["manteau trapeze"], "manteau_trapeze"),
            (["trench court ceinture", "trench court"], "trench_court_ceinture"),
            (["trench long ceinture", "trench long", "trench"], "trench_long_ceinture_uni"),
            (["manteau"], "manteau_droit"),
        ],
 
        # ── CHAUSSURES ───────────────────────────────────────────────────────
        "chaussure": [
            (["escarpins pointus cuir"], "escarpins_pointus_cuir"),
            (["escarpins pointus"], "escarpins_pointus"),
            (["escarpins brides vernis", "escarpins brides"], "escarpins_brides_vernis_cuir"),
            (["escarpins bout carre"], "escarpins_bout_carree"),
            (["escarpins kitten heel cuir"], "escarpins_kitten_heel_cuir"),
            (["kitten heel", "kitten"], "escarpins_kitten_heel"),
            (["escarpins talon bloc"], "escarpins_talons_bloc"),
            (["escarpins ouverts arriere"], "escarpins_ouverts_arriere"),
            (["escarpins talon moyen", "escarpins talons", "escarpins",
              "talon haut", "talons hauts", "talon aiguille"], "escarpins_pointus"),
            (["sandales brides chevilles minimalistes"], "sandales_brides_chevilles_minimalistes_talons"),
            (["sandales fines talons dorees"], "sandales_fines_talons_dorees"),
            (["sandales talons fins"], "sandales_talons_fins"),
            (["sandales lannieres", "sandales lanieres", "nu-pieds lanieres"], "sandales_lannieres_montantes"),
            (["sandales compensees"], "sandales_compensees"),
            (["sandales talon plateforme", "sandales plateforme"], "sandales_talon_plateforme_daim"),
            (["sandales plates"], "sandales_plates_cuir"),
            (["sandales talons", "sandales talon"], "sandales_fines_talons_dorees"),
            (["sandales", "nu-pieds"], "sandales_fines_talons_dorees"),
            (["bottines western"], "bottines_western_bouts_pointus"),
            (["bottines talon fin velours"], "bottines_talon_fin_velours"),
            (["bottines talon large"], "bottines_talon_large"),
            (["bottines", "bottine"], "bottines_talon_fin_velours"),
            (["bottes hautes cuir velours", "bottes hautes"], "bottes_hautes_cuir_velours"),
            (["bottes talons cuir", "bottes talons", "bottes a talons"], "bottes_talons_cuir"),
            (["bottes mollets larges"], "bottes_mollets_larges"),
            (["bottes plates cuir", "bottes plates"], "bottes_cuir_plates"),
            (["bottes", "boots"], "bottes_talons_cuir"),
            (["ballerines plates"], "ballerines_plates"),  # NOUVEAU
            (["ballerines pointues cuir"], "ballerines_pointues_cuir"),
            (["ballerines"], "ballerines_daim_classiques"),
            (["mocassins chunky"], "mocassins_chunky"),
            (["mocassins", "mocassin", "loafer"], "mocassins"),
            (["mules ouvertes talons", "mules talons"], "mules_ouvertes_talons"),
            (["mules plates cuir", "mules"], "mules_plates_cuir"),
            (["espadrilles coton compensees", "espadrilles compensees"], "espadrilles_coton_compensees"),
            (["espadrilles cuir talon", "espadrilles talon"], "espadrilles_cuir_talon"),
            (["espadrilles"], "espadrilles_rayees_plates"),
            (["sneakers massives"], "sneakers_massives"),
            (["sneakers montantes compensees"], "sneakers_montantes_compensees_beige"),
            (["sneakers", "basket"], "sneakers_fines_minimalistes"),
            (["derbies", "derby", "richelieu"], "derbies_feminines"),
            (["talons fins", "chaussures talons fins"], "sandales_fines_talons_dorees"),
            (["chaussures plates", "plates"], "ballerines_daim_classiques"),
        ],
 
        # ── ACCESSOIRES ──────────────────────────────────────────────────────
        "accessoire": [
            # Sacs ──
            (["sac cabas habille", "cabas habille"], "sac_cabas_habille"),  # NOUVEAU
            (["sac cabas"], "sac_cabas_grand_noir"),
            (["sac hobo cuir", "sac hobo", "hobo"], "sac_hobo_cuir"),  # NOUVEAU
            (["sac baguette cuir", "sac baguette", "baguette"], "sac_baguette_cuir"),  # NOUVEAU
            (["sac structure noir cuir", "sac structure"], "sac_structure_noir_cuir"),  # NOUVEAU
            (["sac rigide"], "sac_rigide"),
            (["sac demi lune", "demi lune"], "sac_demi_lune_petit_format_cuir"),
            (["sac porte croise", "porte croise"], "sac_porte_croise"),
            (["sac bandouliere cuir"], "sac_bandouliere_cuir"),  # NOUVEAU
            (["sac bandouliere", "sac croise", "crossbody"], "sac_bandouliere_souple_petit_format"),
            (["sac porte epaules structure"], "sac_porte_epaules_structure"),  # NOUVEAU
            (["sac porte epaule", "sac epaule"], "sac_porte_epaule"),
            (["sac porte main"], "sac_porte_main"),
            (["shopper small cuir mouton", "shopper cuir", "shopper"], "shopper_small_cuir_mouton"),  # NOUVEAU
            (["sac a main", "sac main"], "sac_a_main_moyen_cuir_souple"),
            (["pochette chaine", "pochette detachable"], "pochette_chaine_detachable"),  # NOUVEAU
            (["pochette soiree", "pochette argent"], "pochette_soiree_argent"),  # NOUVEAU
            (["pochette", "clutch"], "pochette_chaine_detachable"),  # NOUVEAU
            (["sac raphia", "pochette raphia"], "sac_pochette_raphia"),  # NOUVEAU
            (["sac a dos brode", "petit sac a dos"], "petit_sac_a_dos_brode"),  # NOUVEAU
            (["sac a dos", "dos"], "petit_sac_a_dos_brode"),
            (["sac volumineux", "grand sac"], "sac_cabas_habille"),
            (["sac"], "sac_a_main_moyen_cuir_souple"),
            # Ceintures ──
            (["ceinture corset"], "ceinture_corset"),
            (["ceinture tres fine"], "ceinture_tres_fine"),
            (["ceinture fine"], "ceinture_fine"),
            (["ceinture taille haute boucle ardillon"], "ceinture_taille_haute_boucle_ardillon"),
            (["ceinture taille haute"], "ceinture_taille_haute"),
            (["ceinture large boucle"], "ceinture_large_boucle"),
            (["ceinture large"], "ceinture_large"),
            (["ceinture rigide"], "ceinture_rigide"),
            (["ceinture moyenne"], "ceinture_moyenne"),
            (["ceinture chaine"], "ceinture_chaine"),
            (["ceinture obi"], "ceinture_obi"),
            (["ceinture cuir tressee", "ceinture tressee"], "ceinture_cuir_tressee"),
            (["ceinture taille basse"], "ceinture_taille_basse"),
            (["ceinture"], "ceinture_fine"),
            # Bijoux ──
            (["sautoir", "collier long", "long collier"], "sautoir_etain_dore"),
            (["collier multi rang"], "collier_multi_rang"),
            (["collier mi long", "collier moyen"], "collier_mi_long"),
            (["collier ras du cou", "ras du cou", "choker"], "collier_ras_du_cou"),
            (["chaine maille", "chaine doree"], "chaine_maille_torsadee_laiton_dore"),
            (["pendentif"], "pendentif_pierre_naturelle"),
            (["collier"], "collier_mi_long"),
            (["creoles", "boucles creoles"], "boucles_d_oreilles_creoles"),
            (["boucles pendantes", "boucles longues"], "boucles_d_oreilles_pendantes"),
            (["boucles clips"], "boucles_d_oreilles_clips"),
            (["boucles oreilles"], "boucles_d_oreilles_pendantes"),
            (["manchette"], "manchette"),
            (["bracelet jonc"], "bracelet_jonc"),
            (["bracelet maille"], "bracelet_maille"),
            (["bracelet"], "bracelet_souple"),
            # Foulards / chapeaux ──
            (["foulard long", "foulard vertical"], "foulard_long_vertical"),
            (["foulard"], "foulard_noue_cou"),
            (["chapeau paille", "capelline"], "chapeau_paille_capelline"),  # NOUVEAU
            (["chapeau tresse", "chapeau"], "chapeau_tresse"),  # NOUVEAU
        ],
 
        # ── LINGERIE ─────────────────────────────────────────────────────────
        "lingerie": [
            (["push-up", "push up", "soutien gorge push up"], "push_up"),
            (["balconnet", "soutien gorge balconnet"], "balconnet"),
            (["bralette"], "bralette"),
            (["bustier lingerie"], "bustier"),
            (["soutien gorge emboitant", "emboitant", "minimiseur armatures", "minimiseur"], "soutien_gorge_emboitant"),
            (["soutien gorge triangle", "triangle"], "soutien_gorge_triangle"),
            (["soutien gorge tshirt", "soutien tshirt", "shorty taille haute"], "soutien_tshirt"),
            (["body gainant", "body"], "body_gainant"),
            (["culotte basse", "taille basse culotte"], "culotte_basse"),
            (["culotte echancree", "echancree"], "culotte_echancree"),
            (["culotte haute", "culotte taille haute"], "culotte_haute"),
            (["string", "tanga"], "string_tanga"),
        ],
 
        # ── MAILLOTS DE BAIN ─────────────────────────────────────────────────
        "Maillot de bain": [
            (["une piece gainant", "gainant maillot"], "une_piece_gainant"),
            (["une piece decollete"], "une_piece_decollete"),
            (["une piece asymetrique"], "une_piece_asymetrique"),
            (["une piece classique", "une piece"], "une_piece_classique"),
            (["maillot decoupes laterales", "decoupes laterales"], "maillot_decoupes_laterales"),  # NOUVEAU
            (["maillot push up", "push up bain"], "maillot_push_up"),
            (["maillot soutien armature", "armature bain"], "maillot_soutien_armature"),
            (["maillot taille haute", "taille haute bain"], "maillot_taille_haute"),
            (["maillot echancre", "echancre bain"], "maillot_echancre"),
            (["maillot triangle", "triangle bain"], "maillot_triangle"),
            (["maillot bandeau", "bandeau bain"], "maillot_bandeau"),
            (["tankini"], "tankini"),
            (["trikini"], "trikini"),
            (["shorty bain"], "shorty_bain"),
            (["shorty"], "shorty"),
            (["bas echancre"], "bas_echancre"),
            (["bas taille haute bain", "bas taille haute"], "bas_taille_haute"),
        ],
    }

    # Visuels lingerie et maillots de bain par silhouette pour la page 10
    LINGERIE_MAILLOT_BY_SILHOUETTE = {
        "A": {
            "lingerie": [
                ("push_up",       "Push-up / balconnet",   "Structure le haut, équilibre les hanches larges."),
                ("culotte_haute", "Culotte taille haute",  "Lisse et affine les hanches visuellement."),
                ("body_gainant",  "Body gainant",          "Ligne continue sous les vêtements."),
            ],
            "maillots": [
                ("une_piece_decollete", "Une pièce décolleté V",   "Dirige le regard vers le haut."),
                ("maillot_bandeau",     "Haut bandeau à volants",  "Élargit visuellement les épaules."),
                ("tankini",             "Tankini taille haute",    "Camouffle le bas, valorise le haut."),
            ],
            "lingerie_eviter":  "Culottes taille basse — accentuent la largeur des hanches.",
            "maillots_eviter":  "Bikini bas à nœuds latéraux — élargissent les hanches.",
        },
        "V": {
            "lingerie": [
                ("bralette",              "Bralette",             "Légère, sans volume aux épaules."),
                ("culotte_echancree",     "Culotte échancrée",    "Attire l'œil vers le bas pour rééquilibrer."),
                ("soutien_gorge_triangle","Triangle",             "Doux et adapté aux épaules larges."),
            ],
            "maillots": [
                ("maillot_triangle",  "Bikini triangle",      "Ajoute du volume et de l'équilibre en bas."),
                ("bas_taille_haute",  "Bas taille haute",     "Attire l'attention vers le bas."),
                ("tankini",           "Tankini haut sobre",   "Dirige l'attention vers le bas."),
            ],
            "lingerie_eviter":  "Bustiers rigides — élargissent encore les épaules.",
            "maillots_eviter":  "Hauts de bikini à épaulettes — accentuent la largeur.",
        },
        "O": {
            "lingerie": [
                ("minimiseur_avec_armatures",  "Minimiseur armatures",    "Soutient et structure la silhouette."),
                ("culotte_haute",   "Shorty taille haute",     "Confort et maintien optimal au quotidien."),
                ("body_gainant",    "Body gainant ventre plat","Affine la taille sous les vêtements."),
            ],
            "maillots": [
                ("une_piece_gainant",   "Une pièce gainant",          "Galbe et affine la taille."),
                ("maillot_decoupes_laterales", "Maillot découpes latérales", "Effet amincissant et élancé."),
                ("tankini",             "Tankini col en V",           "Allonge le buste, verticalité."),
            ],
            "lingerie_eviter":  "Lingerie inadaptée à la poitrine — crée des bourrelets.",
            "maillots_eviter":  "Bikini deux pièces très court — marque la taille.",
        },
        "X": {
            "lingerie": [
                ("balconnet",     "Balconnet",         "Met en valeur le décolleté naturel."),
                ("culotte_haute", "Culotte taille haute","Valorise la taille naturelle."),
                ("bustier",       "Bustier",           "Accentue le galbe naturel de la silhouette."),
            ],
            "maillots": [
                ("maillot_echancre",   "Une pièce échancré",   "Met en avant les courbes."),
                ("bas_taille_haute",   "Bikini taille haute",  "Accentue la taille et les formes."),
                ("une_piece_classique","Bikini à nœuds",       "Sublime les courbes naturelles."),
            ],
            "lingerie_eviter":  "Sous-vêtements trop visibles sous les vêtements structurés.",
            "maillots_eviter":  "Maillots droits sans forme — cachent votre atout naturel.",
        },
        "H": {
            "lingerie": [
                ("push_up",          "Push-up rembourré",      "Crée des courbes sur le haut."),
                ("culotte_echancree", "Culotte à volants",     "Ajoute du galbe aux hanches."),
                ("bralette",         "Bralette avec détails",  "Définit le buste sans rigidité."),
            ],
            "maillots": [
                ("maillot_push_up",  "Maillot push-up",        "Crée des courbes sur le haut."),
                ("une_piece_gainant","Une pièce effet peplum", "Crée l'illusion d'une taille."),
                ("maillot_bandeau",  "Bandeau + bas à nœuds",  "Définit les courbes."),
            ],
            "lingerie_eviter":  "Maillots une pièce très droits — accentuent le manque de courbes.",
            "maillots_eviter":  "Bikini très minimaliste — n'apporte pas de définition.",
        },
    }

    # Fallback par catégorie si aucun match — garantit qu'aucun carré vide n'apparaît
    MORPHO_MVP_FALLBACK = {
        "haut":          "top_fluide",
        "bas":           "pantalon_droit",
        "robe":          "robe_droite",
        "veste":         "blazer_cintre",
        "manteau":       "manteau_droit",
        "chaussure":     "escarpins_pointus",
        "accessoire":    "sac_a_main_moyen_cuir_souple",
        "lingerie":      "soutien_gorge_emboitant",
        "Maillot de bain": "une_piece_classique",
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
    def _find_visual_key_for_piece(name: str, supabase_category: str, allow_fallback: bool = True) -> str:
        """Retourne le nom_simplifie Supabase correspondant au nom de pièce.
        Si allow_fallback=False, retourne "" si aucun match réel (sans activer le fallback).
        """
        if not name:
            return ""
        name_norm = PDFDataMapper._normalize_for_matching(name)
        for keywords, visual_key in PDFDataMapper.MORPHO_MVP_KEYWORD_MAP.get(supabase_category, []):
            if any(kw in name_norm for kw in keywords):
                return visual_key
 
        if not allow_fallback:
            return ""
 
        # Fallback uniquement si allow_fallback=True
        fallback_key = PDFDataMapper.MORPHO_MVP_FALLBACK.get(supabase_category, "")
        if fallback_key:
            print(f"   📦 FALLBACK [{supabase_category}] '{name[:40]}' → key='{fallback_key}'")
            return fallback_key
        return ""
 
    @staticmethod
    def _enrich_mvp_essentials_with_visuals(essentials: dict) -> dict:
        """
        Enrichit chaque item de morphology_mvp.essentials avec visual_url
        depuis la table Supabase visuels via keyword matching sur le nom.
 
        Mapping catégories MVP → catégories Supabase :
          tops              → haut
          bottoms           → bas
          dresses           → robe             (NOUVEAU v6)
          jackets           → veste, manteau   (NOUVEAU v6)
          dresses_jackets   → robe, veste      (rétrocompat v5)
          shoes_accessories → chaussure, accessoire
        """
        CATEGORY_MAP = {
            "tops":               ["haut"],
            "bottoms":            ["bas"],
            "dresses":            ["robe"],                    # ← NOUVEAU
            "jackets":            ["veste", "manteau"],        # ← NOUVEAU
            "dresses_jackets":    ["robe", "veste"],           # rétrocompat
            "shoes_accessories":  ["chaussure", "accessoire"],
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
 
                # Passe 1 : chercher un vrai match sans fallback sur toutes les catégories
                visual_key = ""
                for supabase_cat in supabase_cats:
                    visual_key = PDFDataMapper._find_visual_key_for_piece(
                        name, supabase_cat, allow_fallback=False
                    )
                    if visual_key:
                        break
 
                # Passe 2 : si toujours rien, accepter le fallback de la première catégorie
                if not visual_key:
                    visual_key = PDFDataMapper._find_visual_key_for_piece(
                        name, supabase_cats[0], allow_fallback=True
                    )
 
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
    def _guess_supabase_cats_for_piece(name: str) -> list:
        """Devine la(les) catégorie(s) Supabase pour un nom de pièce.
        Priorité : veste > manteau > robe > bas > chaussure > accessoire > haut
        """
        n = PDFDataMapper._normalize_for_matching(name)
 
        # Vestes — AVANT robes pour attraper blazer/veste cintré/fluide
        if any(k in n for k in ["blazer", "veste", "blouson", "perfecto",
                                  "doudoune", "gilet", "cardigan long"]):
            return ["veste"]
 
        # Manteaux
        if any(k in n for k in ["manteau", "trench", "duffle"]):
            return ["manteau", "veste"]
 
        # Robes et combinaisons
        if any(k in n for k in ["robe", "combinaison", "combi"]):
            return ["robe"]
 
        # Bas
        if any(k in n for k in ["jupe", "pantalon", "jean", "legging",
                                  "short", "palazzo", "bermuda"]):
            return ["bas"]
 
        # Chaussures — word boundary pour "talon"
        words = n.split()
        shoe_kw = ["escarpin", "botte", "bottine", "sandale", "chaussure",
                   "sneaker", "ballerine", "mocassin", "mule", "derby", "espadrille"]
        if any(k in n for k in shoe_kw) or "talon" in words or "talons" in words:
            return ["chaussure"]
 
        # Accessoires
        if any(k in n for k in ["ceinture", "collier", "sac", "foulard",
                                  "bracelet", "boucle", "sautoir", "pendentif",
                                  "pochette", "chapeau", "manchette"]):
            return ["accessoire"]
 
        # Maillots / lingerie
        if any(k in n for k in ["maillot", "bikini", "tankini"]):
            return ["Maillot de bain"]
        if any(k in n for k in ["soutien", "culotte", "bralette", "bustier", "body"]):
            return ["lingerie"]
 
        return ["haut"]
 
 
    @staticmethod
    def _enrich_outfit_formulas_with_visuals(outfit_formulas: list) -> list:
        """
        Transforme chaque formula.pieces de list[str] en list[dict]:
          {"name": str, "visual_key": str, "visual_url": str}
        Permet d'afficher les visuels illustratifs dans la page 10.
        """
        enriched_formulas = []
 
        for formula in outfit_formulas:
            if not isinstance(formula, dict):
                continue
 
            pieces_raw = PDFDataMapper._safe_list(formula.get("pieces", []))
            enriched_pieces = []
 
            for piece in pieces_raw:
                if not isinstance(piece, str):
                    # Déjà enrichi (dict) — on le garde tel quel
                    if isinstance(piece, dict):
                        enriched_pieces.append(piece)
                    continue
 
                name = piece.strip()
                visual_key = ""
                visual_url = ""
 
                # Deviner la catégorie Supabase depuis le nom
                cats = PDFDataMapper._guess_supabase_cats_for_piece(name)
                for cat in cats:
                    visual_key = PDFDataMapper._find_visual_key_for_piece(name, cat)
                    if visual_key:
                        break
 
                if visual_key:
                    try:
                        visual_url = visuals_service.get_url(visual_key) or ""
                    except Exception as e:
                        print(f"⚠️  formula visual get_url('{visual_key}'): {e}")
 
                enriched_pieces.append({
                    "name": name,
                    "visual_key": visual_key,
                    "visual_url": visual_url,
                })
 
                status = "✅" if visual_url else ("🔑" if visual_key else "⚠️ ")
                print(f"   {status} FORMULA '{formula.get('occasion','')}' '{name}' → '{visual_key}'")
 
            enriched_formulas.append({**formula, "pieces": enriched_pieces})
 
        return enriched_formulas

    @staticmethod
    def _guess_product_category_for_priority(name: str) -> str:
        """
        Devine la catégorie product_matcher_service pour une priorité shopping.
        Catégories valides: tops, bottoms, dresses_playsuits, outerwear, shoes, accessories
        """
        n = PDFDataMapper._normalize_for_matching(name)
        shoe_keywords = ["escarpin", "botte", "bottine", "sandale", "chaussure",
                         "sneaker", "ballerine", "mocassin", "mule", "derby", "espadrille"]
        # "talon" vérifié séparément avec word boundary pour éviter "pantalons"
        words = n.split()
        if any(k in n for k in shoe_keywords) or "talon" in words or "talons" in words:
            return "shoes"
 
        if any(k in n for k in ["sac", "ceinture", "collier", "bracelet", "foulard",
                                  "bijou", "accessoire", "boucle", "sautoir", "pendentif"]):
            return "accessories"
        if any(k in n for k in ["robe", "combinaison", "jumpsuit"]):
            return "dresses_playsuits"
        if any(k in n for k in ["veste", "blazer", "manteau", "trench", "trenchcoat"]):
            return "outerwear"
        if any(k in n for k in ["pantalon", "jupe", "jean", "short", "palazzo"]):
            return "bottoms"
        return "tops"

    @staticmethod
    def _enrich_shopping_priorities_with_products(shopping_priorities: list) -> list:
        """
        Pour chaque priorité shopping, retourne 4 produits complets via match_piece_top4.
        Chaque item: {name, category, visual_key, products: list[4 dicts]}
        """
        VISUAL_CATS = {
            "tops":              ["haut"],
            "bottoms":           ["bas"],
            "dresses_playsuits": ["robe"],
            "outerwear":         ["veste"],
            "shoes":             ["chaussure"],
            "accessories":       ["accessoire"],
        }
 
        enriched = []
        for priority in shopping_priorities:
            if not isinstance(priority, str) or not priority.strip():
                continue
 
            name         = priority.strip()
            product_cat  = PDFDataMapper._guess_product_category_for_priority(name)
            supabase_cats = VISUAL_CATS.get(product_cat, ["haut"])
 
            visual_key = ""
            for vcat in supabase_cats:
                visual_key = PDFDataMapper._find_visual_key_for_piece(name, vcat)
                if visual_key:
                    break
 
            piece = {"piece_title": name, "spec": "", "visual_key": visual_key}
 
            try:
                products = product_matcher_service.match_piece_top4(piece, product_cat)
            except Exception as e:
                print(f"⚠️ match_piece_top4 failed for '{name}': {e}")
                products = []
 
            enriched.append({
                "name":       name,
                "category":   product_cat,
                "visual_key": visual_key,
                "products":   products,
            })
 
            print(f"   🛍️ PRIORITY '{name[:50]}' → {product_cat}: {len(products)} produits")
 
        return enriched
 
    @staticmethod
    def _build_lingerie_maillot_page10(silhouette_type: str) -> dict:
        """
        Construit les visuels lingerie et maillots pour la page 10.
        Retourne: {lingerie: [...], maillots: [...], lingerie_eviter: str, maillots_eviter: str}
        """
        sil_data = PDFDataMapper.LINGERIE_MAILLOT_BY_SILHOUETTE.get(
            silhouette_type,
            PDFDataMapper.LINGERIE_MAILLOT_BY_SILHOUETTE.get("O", {})
        )
 
        def _enrich_items(items, supabase_type):
            enriched = []
            for nom_simplifie, label, why in items:
                visual_url = ""
                try:
                    raw_url = visuals_service.get_url(nom_simplifie) or ""
                    # PDFMonkey ne peut pas charger les CDN externes qui bloquent le hotlinking.
                    # On ne garde que les URLs Supabase qui fonctionnent sans restriction.
                    if raw_url and "supabase.co" in raw_url:
                        visual_url = raw_url
                    elif raw_url:
                        print(f"   ⚠️ URL externe ignorée pour '{nom_simplifie}': {raw_url[:60]}...")
                except Exception as e:
                    print(f"⚠️ visuals_service.get_url('{nom_simplifie}'): {e}")
 
                enriched.append({
                    "key":        nom_simplifie,
                    "label":      label,
                    "why":        why,
                    "visual_url": visual_url,
                })
                status = "✅" if visual_url else "⚠️ (emoji fallback)"
                print(f"   {status} PAGE10 [{supabase_type}] '{nom_simplifie}' → url={'yes' if visual_url else 'no'}")
            return enriched
 
        return {
            "lingerie":         _enrich_items(sil_data.get("lingerie", []),  "lingerie"),
            "maillots":         _enrich_items(sil_data.get("maillots", []),  "maillots"),
            "lingerie_eviter":  sil_data.get("lingerie_eviter", ""),
            "maillots_eviter":  sil_data.get("maillots_eviter", ""),
        }
 
 

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

        # Extraction des style_tags pour le matching affilié (Point 1 - style-aware)
        _style_mix = (styling_raw.get("page17") or {}).get("style_mix") or []
        _style_tags_matching = [
            s.get("style", "").strip()
            for s in _style_mix
            if isinstance(s, dict) and s.get("style")
        ]
        print(f"🎨 Style tags pour matching affilié: {_style_tags_matching}")

        # Page 18 - enrich affiliate matches
        for k in ["tops", "bottoms", "dresses_playsuits", "outerwear"]:
            items = styling_raw["page18"]["categories"].get(k, [])

            # 1) match affilié
            items = product_matcher_service.enrich_pieces(items, k, style_tags=_style_tags_matching)

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
            items = product_matcher_service.enrich_pieces(items, k, style_tags=_style_tags_matching)
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
        
        # ✅ Enrichissement visuels pédagogiques MVP morphologie
        print("\n🎨 Enrichissement visuels MVP morphologie...")
        essentials_raw = PDFDataMapper._safe_dict(morphology_mvp.get("essentials", {}))
        essentials_enriched = PDFDataMapper._enrich_mvp_essentials_with_visuals(essentials_raw)

        # Séparer dresses et jackets depuis essentials pour la page 9 v10
        essentials_dresses  = essentials_enriched.get("dresses", [])
        essentials_jackets  = essentials_enriched.get("jackets", [])
        # Rétrocompat : si GPT retourne encore dresses_jackets (vieux rapport)
        if not essentials_dresses and not essentials_jackets:
            dj = essentials_enriched.get("dresses_jackets", [])
            essentials_dresses  = [i for i in dj if PDFDataMapper._is_dress(i)]
            essentials_jackets  = [i for i in dj if not PDFDataMapper._is_dress(i)]
 

        # ✅ Enrichissement formules de tenues avec visuels
        print("\n🎨 Enrichissement formules de tenues...")
        outfit_formulas_raw = PDFDataMapper._safe_list(morphology_mvp.get("outfit_formulas", []))
        outfit_formulas_enriched = PDFDataMapper._enrich_outfit_formulas_with_visuals(outfit_formulas_raw)

        # ✅ Visuels lingerie + maillots page 10
        silhouette_type_for_p10 = morphology_raw.get("silhouette_type", "O") or "O"
        print(f"\n👙 Construction visuels lingerie/maillots page 10 (silhouette={silhouette_type_for_p10})...")
        lingerie_maillot_p10 = PDFDataMapper._build_lingerie_maillot_page10(silhouette_type_for_p10)

        # ✅ Enrichissement priorités shopping avec produits affiliés
        print("\n🛍️ Enrichissement priorités shopping morphologie...")
        shopping_priorities_raw = PDFDataMapper._safe_list(morphology_mvp.get("shopping_priorities", []))
        shopping_priorities_enriched = PDFDataMapper._enrich_shopping_priorities_with_products(shopping_priorities_raw)

        # ✅ Extraction avoid_by_category (items à éviter par catégorie, pour page 9)
        # ✅ avoid_by_category — shoes et accessories séparés (v5)
        avoid_by_category_raw = PDFDataMapper._safe_dict(morphology_mvp.get("avoid_by_category", {}))
        avoid_by_category = {
            "tops":              PDFDataMapper._safe_list(avoid_by_category_raw.get("tops", [])),
            "bottoms":           PDFDataMapper._safe_list(avoid_by_category_raw.get("bottoms", [])),
            "dresses_jackets":   PDFDataMapper._safe_list(avoid_by_category_raw.get("dresses_jackets", [])),
            "shoes":             PDFDataMapper._safe_list(avoid_by_category_raw.get("shoes", [])),
            "accessories":       PDFDataMapper._safe_list(avoid_by_category_raw.get("accessories", [])),
            # rétrocompat : ancienne clé shoes_accessories si nouveau prompt pas encore déployé
            "shoes_accessories": PDFDataMapper._safe_list(
                avoid_by_category_raw.get("shoes_accessories", [])
                or avoid_by_category_raw.get("shoes", [])
            ),
        }

        # ✅ Flatten shopping products pour page 12 (4 produits × 5 priorités = 20 max)
        shopping_products_flat = []
        for sp_item in shopping_priorities_enriched:
            priority_name = sp_item.get("name", "")
            for product in sp_item.get("products", []):
                if product.get("product_url"):
                    shopping_products_flat.append({
                        "priority_name": priority_name,
                        "image_url":     product.get("image_url", ""),
                        "product_url":   product.get("product_url", ""),
                        "brand":         product.get("brand", ""),
                        "price":         product.get("price", ""),
                        "title":         product.get("title", priority_name),
                    })
 
 
 
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
                "essentials":                 essentials_enriched,
                "essentials_dresses":  essentials_dresses,
                "essentials_jackets":  essentials_jackets,
                "avoid":                      PDFDataMapper._safe_list(morphology_mvp.get("avoid", [])),
                "avoid_by_category":              avoid_by_category,
                "outfit_formulas":            outfit_formulas_enriched,
                "shopping_priorities":        PDFDataMapper._safe_list(morphology_mvp.get("shopping_priorities", [])),
                "shopping_priorities_enriched": shopping_priorities_enriched,
                "shopping_products_flat":       shopping_products_flat,
                "style_notes": PDFDataMapper._safe_dict(morphology_mvp.get("style_notes", {
                    "matieres_recommandees": [],
                    "motifs_recommandes":    [],
                    "matieres_eviter":       [],
                    "motifs_eviter":         [],
                })),
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
            "lingerie_page10":        lingerie_maillot_p10["lingerie"],
            "maillots_page10":        lingerie_maillot_p10["maillots"],
            "lingerie_eviter_page10": lingerie_maillot_p10["lingerie_eviter"],
            "maillots_eviter_page10": lingerie_maillot_p10["maillots_eviter"],
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
    def _is_dress(item: dict) -> bool:
        """True si l'item ressemble à une robe/combinaison plutôt qu'une veste."""
        name = PDFDataMapper._normalize_for_matching(item.get("name", ""))
        return any(k in name for k in ["robe", "combinaison", "combi", "jumpsuit"])


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