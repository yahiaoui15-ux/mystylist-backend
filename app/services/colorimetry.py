"""
Colorimetry Service v9.3 - FIX affichage couleurs DB + robustesse noms attachés
✅ Utilise analyze_image() pour les appels Vision avec images
✅ Placeholders en MAJUSCULES: {FACE_PHOTO}, {EYE_COLOR}, {HAIR_COLOR}, {AGE}
✅ Chaque appel OpenAI = bloc isolé avec Before/During/After clair
✅ Part 1: Vision avec image
✅ Part 2 & 3: Chat texte pur
✅ FIX: couleurs DB parfois "attachées" (ex: bleuglacier, blanccasse) -> affichage humain ("Bleu Glacier", "Blanc Cassé")
✅ FIX: assoc.colors + assoc.color_details.displayName forcés depuis la DB (Solution 1) avec pretty names
"""

import json
import re
from datetime import datetime
from app.utils.openai_client import openai_client
from app.utils.openai_call_tracker import call_tracker
from app.prompts.colorimetry_part1_prompt import (
    COLORIMETRY_PART1_SYSTEM_PROMPT,
    COLORIMETRY_PART1_USER_PROMPT,
)
from app.prompts.colorimetry_part2_prompt import (
    COLORIMETRY_PART2_SYSTEM_PROMPT,
    COLORIMETRY_PART2_USER_PROMPT_TEMPLATE,
    get_fallback_part2,
)
from app.prompts.colorimetry_part3_prompt import (
    COLORIMETRY_PART3_SYSTEM_PROMPT,
    COLORIMETRY_PART3_USER_PROMPT_TEMPLATE,
)
from app.services.robust_json_parser import RobustJSONParser
from app.services.colorimetry_parsing_utilities import ColorimetryJSONParser
from app.services.color_image_matcher import ColorImageMatcher
from app.services.image_thumbnailer import ImageThumbnailer


class ColorimetryService:
    def __init__(self):
        self.openai = openai_client

    # ---------------------------------------------------------------------
    # Pretty display helpers (DB slugs sometimes concatenated: bleuglacier...)
    # ---------------------------------------------------------------------
    _DISPLAY_EXCEPTIONS = {
        "blanccasse": "Blanc Cassé",
        "bleunuitestival": "Bleu Nuit Estival",
        "orvieilli": "Or Vieilli",
        "orclair": "Or Clair",
        "nudechaud": "Nude Chaud",
        "nudedore": "Nude Doré",
        "turquoiseprofond": "Turquoise Profond",
        "denimclair": "Denim Clair",
        "olivefonce": "Olive Foncé",
        "taupeclair": "Taupe Clair",
        "taupefroid": "Taupe Froid",
        "pruneclaire": "Prune Claire",
        "prunedouce": "Prune Douce",
        "violetfonce": "Violet Foncé",
        "jaunepale": "Jaune Pâle",
        "jaunedoux": "Jaune Doux",
        "coraildoux": "Corail Doux",
        "terrecuite": "Terre Cuite",
        "rougerubis": "Rouge Rubis",
        "rosefroid": "Rose Froid",
        "rosefuchsia": "Rose Fuchsia",
        "rosenude": "Rose Nude",
        "rosepastel": "Rose Pastel",
        "rosepoudre": "Rose Poudre",
        "rosevieux": "Rose Vieux",
        "bleuacier": "Bleu Acier",
        "bleuardoise": "Bleu Ardoise",
        "bleuazur": "Bleu Azur",
        "bleuceladon": "Bleu Céladon",
        "bleuciel": "Bleu Ciel",
        "bleuelectrique": "Bleu Électrique",
        "bleuglacier": "Bleu Glacier",
        "bleunuit": "Bleu Nuit",
        "bleupastel": "Bleu Pastel",
        "bleupoudre": "Bleu Poudre",
        "bleuroi": "Bleu Roi",
        "grisacier": "Gris Acier",
        "grisargent": "Gris Argent",
        "grisclair": "Gris Clair",
        "grisfonce": "Gris Foncé",
        "grisperle": "Gris Perle",
        "vertamande": "Vert Amande",
        "vertdeau": "Vert d’Eau",
        "verteau": "Vert d’Eau",
        "vertdoux": "Vert Doux",
        "vertemeraude": "Vert Émeraude",
        "vertmousse": "Vert Mousse",
        "vertpistache": "Vert Pistache",
        "vertpomme": "Vert Pomme",
        "vertsauge": "Vert Sauge",
        "champagne": "Champagne",
        "vanille": "Vanille",
        "lavande": "Lavande",
        "fuchsia": "Fuchsia",
        "emeraude": "Émeraude",
        "framboise": "Framboise",
        "cannelle": "Cannelle",
        "rouille": "Rouille",
        "camelclair": "Camel Clair",
    }

    _BASE_PREFIXES = [
        "turquoise",
        "anthracite",
        "chocolat",
        "bordeaux",
        "terracotta",
        "denim",
        "blanc",
        "bleu",
        "gris",
        "rose",
        "vert",
        "jaune",
        "orange",
        "rouge",
        "camel",
        "taupe",
        "nude",
        "olive",
        "prune",
        "violet",
        "corail",
        "ivoire",
        "ecru",
        "creme",
        "sable",
        "or",
        "cuivre",
        "bronze",
        "argent",
        "ambre",
    ]

    _QUALIFIERS = [
        "electrique",
        "estival",
        "glacier",
        "ardoise",
        "celadon",
        "poudre",
        "pastel",
        "profond",
        "vieilli",
        "clair",
        "fonce",
        "pale",
        "doux",
        "casse",
        "nuit",
        "acier",
        "argent",
        "azur",
        "ciel",
        "roi",
        "dore",
    ]

    _QUALIFIER_DISPLAY = {
        "electrique": "Électrique",
        "fonce": "Foncé",
        "pale": "Pâle",
        "casse": "Cassé",
        "dore": "Doré",
    }

    # ---------------------------------------------------------------------
    # HEX helpers (DB is truth for pastilles too)
    # ---------------------------------------------------------------------
    _COLOR_HEX_BY_TOKEN = {
        # neutres
        "noir": "#000000",
        "blanc": "#FFFFFF",
        "ivoire": "#FFFFF0",
        "ecru": "#F5F5DC",
        "creme": "#FFFDD0",
        "sable": "#D9CAB3",

        # chauds / bruns
        "camel": "#C19A6B",
        "chocolat": "#7B3F00",
        "cuivre": "#B87333",
        "bronze": "#CD7F32",
        "or": "#D4AF37",
        "orvieilli": "#B08D57",

        # oranges / rouges
        "terracotta": "#E2725B",
        "terrecuite": "#E2725B",
        "rouille": "#B7410E",
        "bordeaux": "#800020",
        "brique": "#CB4154",

        # verts
        "olive": "#808000",
        "olivefonce": "#556B2F",
        "vertmousse": "#8A9A5B",
        "vertsauge": "#708238",
        "vertdoux": "#A3B18A",
        "vertdeau": "#40E0D0",
        "verteau": "#40E0D0",
        "kaki": "#C3B091",

        # bleus
        "denim": "#3B4F5A",
        "denimclair": "#6E7F8D",
        "marine": "#000080",
        "bleu": "#0000FF",
        "bleunuit": "#0B1D39",
        "bleuglacier": "#BFD7EA",
        "bleuciel": "#87CEEB",
        "bleupoudre": "#B0C4DE",
        "bleuardoise": "#708090",
        "bleuacier": "#4682B4",
        "bleuelectrique": "#0077FF",

        # gris
        "gris": "#808080",
        "grisclair": "#D3D3D3",
        "grisfonce": "#4F4F4F",
        "grisargent": "#C0C0C0",
        "grisperle": "#D9D9D9",
        "grisacier": "#708090",
        "anthracite": "#2F4F4F",

        # violets / prune
        "violet": "#800080",
        "violetfonce": "#4B0082",
        "prune": "#6D071A",
        "prunedouce": "#7D4E57",

        # jaunes
        "moutarde": "#E1AD01",
        "jaunepale": "#FFF2A6",
        "jaunedoux": "#F7D36A",
        "ocre": "#CC7722",
    }

    @classmethod
    def _norm_db_token(cls, token: str) -> str:
        """Normalise un token DB pour matcher les slugs 'attachés' / underscore."""
        if not token:
            return ""
        t = str(token).strip().lower()
        t = t.replace("-", "_").replace(" ", "_")
        # on supprime _ pour matcher aussi les attachés (olive_fonce == olivefonce)
        t = t.replace("_", "")
        return t

    @classmethod
    def _hex_from_db_token(cls, token: str) -> str:
        k = cls._norm_db_token(token)
        if not k:
            return "#DDDDDD"
        # match direct
        if k in cls._COLOR_HEX_BY_TOKEN:
            return cls._COLOR_HEX_BY_TOKEN[k]
        # match via clés normalisées (au cas où dict contient underscores dans le futur)
        for kk, hx in cls._COLOR_HEX_BY_TOKEN.items():
            if cls._norm_db_token(kk) == k:
                return hx
        return "#DDDDDD"

    @classmethod
    def _pretty_color_from_db_token(cls, token: str) -> str:
        """
        Rend lisible une couleur DB:
        - underscore: "bleu_glacier" -> "Bleu Glacier"
        - attachée: "bleuglacier" -> "Bleu Glacier"
        - exceptions: "blanccasse" -> "Blanc Cassé"
        """
        if not token:
            return ""
        t = str(token).strip().lower()
        t = t.replace("-", "_").replace(" ", "_")

        # direct exception
        if t in cls._DISPLAY_EXCEPTIONS:
            return cls._DISPLAY_EXCEPTIONS[t]

        # underscore -> title-case simple
        if "_" in t:
            parts = [p for p in t.split("_") if p]
            out = []
            for p in parts:
                out.append(cls._QUALIFIER_DISPLAY.get(p, p.capitalize()))
            # cas spécial "d'eau" si on reçoit vert_deau / vert_eau, géré en exceptions
            return " ".join(out).strip()

        # attaché -> tentative split (prefix + qualifiers)
        # 1) trouve le meilleur prefix
        prefix = ""
        for pfx in sorted(cls._BASE_PREFIXES, key=len, reverse=True):
            if t.startswith(pfx) and len(t) > len(pfx):
                prefix = pfx
                rest = t[len(pfx):]
                break
        if not prefix:
            return t.capitalize()

        # 2) découpe rest en qualifiers en chaîne (greedy)
        parts = [prefix]
        rest = rest or ""
        while rest:
            matched = None
            for q in sorted(cls._QUALIFIERS, key=len, reverse=True):
                if rest.startswith(q):
                    matched = q
                    break
            if matched:
                parts.append(matched)
                rest = rest[len(matched):]
            else:
                # fallback: ce qu'il reste
                parts.append(rest)
                break

        # 3) format
        out = []
        for p in parts:
            out.append(cls._QUALIFIER_DISPLAY.get(p, p.capitalize()))
        return " ".join([x for x in out if x]).strip()

    async def analyze(self, user_data: dict) -> dict:
        """
        Analyse colorimétrie en 3 appels OpenAI - LOGS STRUCTURÉS
        Part 1: Saison + Analyses détaillées (avec image)
        Part 2: Palette + Couleurs génériques + Associations (texte)
        Part 3: Notes compatibilité + Maquillage + Couleurs refusées (texte)
        """
        try:
            print("\n" + "=" * 80)
            print("🎨 ANALYSE COLORIMETRIE - 3 APPELS SEQUENTIELS")
            print("=" * 80)

            # ✅ FIX: Chercher photo en snake_case OU camelCase
            face_photo_url = user_data.get("face_photo_url")
            if not face_photo_url:
                face_photo_url = user_data.get("facePhotoUrl")  # camelCase fallback

            if not face_photo_url:
                print("❌ Pas de photo de visage fournie")
                return {}

            # ✅ FIX: Chercher eye_color et hair_color aussi en camelCase
            eye_color = user_data.get("eye_color") or user_data.get("eyeColor")
            hair_color = user_data.get("hair_color") or user_data.get("hairColor")

            # ═══════════════════════════════════════════════════════════
            # PART 1: SAISON + ANALYSES
            # ═══════════════════════════════════════════════════════════
            result_part1 = await self._call_part1(user_data, face_photo_url, eye_color, hair_color)
            if not isinstance(result_part1, dict) or result_part1.get("_parse_error"):
                print("⚠️ Colorimétrie Part 1 invalide → mode dégradé")

                result_part1 = {
                    "saison_confirmee": "Indéterminée",
                    "sous_ton_detecte": "neutre",
                    "justification_saison": "",
                    "analyse_colorimetrique_detaillee": {},
                }

            saison = result_part1.get("saison_confirmee", "Indéterminée")
            sous_ton = result_part1.get("sous_ton_detecte", "neutre")

            # ═══════════════════════════════════════════════════════════
            # PART 2: PALETTE + ASSOCIATIONS + COULEURS GÉNÉRIQUES
            # ═══════════════════════════════════════════════════════════
            result_part2 = await self._call_part2(
                saison,
                sous_ton,
                result_part1.get("eye_color", eye_color),
                result_part1.get("hair_color", hair_color),
            )
            if not result_part2:
                result_part2 = get_fallback_part2(saison)

            palette = result_part2.get("palette_personnalisee", [])
            associations = result_part2.get("associations_gagnantes", [])

            # ✅ AJOUT: Ajouter les images à chaque association (Solution 1 - DB is truth)
            associations = self._add_images_to_associations(
                associations,
                result_part1.get("saison_confirmee", "Printemps"),
            )

            generiques = result_part2.get("couleurs_generiques", [])
            all_colors_raw = result_part2.get("allColorsWithNotes", [])

            # ═══════════════════════════════════════════════════════════
            # PART 3: MAQUILLAGE + VERNIS + COULEURS REFUSÉES
            # ═══════════════════════════════════════════════════════════
            unwanted_colors = user_data.get("unwanted_colors", [])
            result_part3 = await self._call_part3(saison, sous_ton, unwanted_colors)
            if not result_part3:
                result_part3 = {}

            # ═══════════════════════════════════════════════════════════
            # ✅ FIX: Construire allColorsWithNotes complète
            # ═══════════════════════════════════════════════════════════
            all_colors_with_notes = self._build_all_colors_with_notes(
                palette,
                all_colors_raw,
                result_part3.get("unwanted_colors", []),
            )

            # ═══════════════════════════════════════════════════════════
            # ✅ FIX: Créer structure "makeup" pour PDFMonkey (Page 7)
            # ═══════════════════════════════════════════════════════════
            makeup_structure = self._build_makeup_structure(result_part3)

            # ═══════════════════════════════════════════════════════════
            # ✅ FIX: Extraire couleurs à manier avec prudence (Page 5)
            # ═══════════════════════════════════════════════════════════
            couleurs_prudence = self._extract_colors_by_note_range(all_colors_with_notes, 4, 6)

            # ═══════════════════════════════════════════════════════════
            # ✅ FIX: Extraire couleurs à éviter (Page 5)
            # ═══════════════════════════════════════════════════════════
            couleurs_eviter = self._extract_colors_by_note_range(all_colors_with_notes, 0, 3)

            # ═══════════════════════════════════════════════════════════
            # FUSION FINALE
            # ═══════════════════════════════════════════════════════════
            print("\n" + "=" * 80)
            print("✅ RÉSUMÉ COLORIMETRIE COMPLÈTE")
            print("=" * 80)

            result = {
                "saison_confirmee": result_part1.get("saison_confirmee", "Indéterminée"),
                "sous_ton_detecte": result_part1.get("sous_ton_detecte", "neutre"),
                "justification_saison": result_part1.get("justification_saison", ""),
                "eye_color": result_part1.get("eye_color", eye_color),
                "hair_color": result_part1.get("hair_color", hair_color),
                "analyse_colorimetrique_detaillee": result_part1.get("analyse_colorimetrique_detaillee", {}),

                # ✅ PAGE 3: Palette personnalisée (10 couleurs, 8-10/10)
                "palette_personnalisee": palette,

                # ✅ PAGE 4: Couleurs génériques (Bleu, Rouge, Jaune, etc. 7-10/10)
                "couleurs_generiques": generiques,

                # ✅ PAGE 5: Couleurs à manier avec prudence (4-6/10)
                "couleurs_prudence": couleurs_prudence,

                # ✅ PAGE 5: Couleurs à éviter (<4/10)
                "couleurs_eviter": couleurs_eviter,

                # Toutes les couleurs avec notes (pour debug/reference)
                "allColorsWithNotes": all_colors_with_notes,

                # Associations de couleurs
                "associations_gagnantes": associations,

                # Notes de compatibilité complètes
                "notes_compatibilite": result_part3.get("notes_compatibilite", {}),

                # Couleurs refusées brutes
                "unwanted_colors": result_part3.get("unwanted_colors", []),

                # ✅ PAGE 7: Guide maquillage structuré
                "guide_maquillage": result_part3.get("guide_maquillage", {}),

                # ✅ PAGE 7: Structure makeup mappée pour PDFMonkey
                "makeup": makeup_structure,

                # Couleurs vernis ongles
                "nailColors": result_part3.get("nailColors", []),
            }

            print(f"   • Saison: {result.get('saison_confirmee')}")
            print(f"   • Palette personnalisée: {len(result.get('palette_personnalisee', []))} couleurs (8-10/10)")
            print(f"   • Couleurs génériques: {len(result.get('couleurs_generiques', []))} couleurs (7-10/10)")
            print(f"   • Couleurs prudence: {len(result.get('couleurs_prudence', []))} couleurs (4-6/10)")
            print(f"   • Couleurs à éviter: {len(result.get('couleurs_eviter', []))} couleurs (<4/10)")
            print(f"   • Associations: {len(result.get('associations_gagnantes', []))} occasions")
            print(f"   • Vernis ongles: {len(result.get('nailColors', []))} couleurs")
            print(f"   • Guide maquillage: {len(result.get('guide_maquillage', {}))} champs")
            print("=" * 80 + "\n")

            # DEBUG: Vérifier que les images sont dans le JSON retourné
            print(f"\n🔍 DEBUG FINAL - Associations avec images:")
            for assoc in result.get("associations_gagnantes", []):
                print(f"   {assoc.get('occasion')}: image_url = {assoc.get('image_url')}")
            return result

        except Exception as e:
            print(f"\n❌ ERREUR COLORIMETRIE: {e}")
            call_tracker.log_error("Colorimetry", str(e))
            import traceback
            traceback.print_exc()
            raise

    def _build_all_colors_with_notes(self, palette: list, all_colors_raw: list, unwanted: list) -> list:
        """✅ Construit allColorsWithNotes depuis palette + alternatives + refusées"""
        colors_dict = {}

        # Ajouter palette (priorité haute)
        for color in palette:
            display_name = color.get("displayName", color.get("name", ""))
            if display_name and display_name not in colors_dict:
                colors_dict[display_name] = color

        # Ajouter alternatives (priorité moyenne)
        for color in all_colors_raw:
            display_name = color.get("displayName", color.get("name", ""))
            if display_name and display_name not in colors_dict:
                colors_dict[display_name] = color

        # Ajouter couleurs refusées (priorité basse)
        for color in unwanted:
            display_name = color.get("displayName", color.get("name", ""))
            if display_name and display_name not in colors_dict:
                colors_dict[display_name] = color

        # Convertir en liste et trier par note décroissante
        all_colors = list(colors_dict.values())
        all_colors.sort(key=lambda x: x.get("note", 5), reverse=True)

        print(f"\n   ✅ allColorsWithNotes construite: {len(all_colors)} couleurs uniques")
        return all_colors

    def _extract_colors_by_note_range(self, all_colors: list, min_note: int, max_note: int) -> list:
        """✅ Extrait les couleurs dans une plage de notes donnée"""
        filtered = [
            color for color in all_colors
            if min_note <= color.get("note", 5) <= max_note
        ]
        filtered.sort(key=lambda x: x.get("note", 5), reverse=True)
        return filtered

    def _add_images_to_associations(self, associations: list, saison: str) -> list:
        """
        Ajoute image + force les couleurs affichées = couleurs DB (Solution 1).
        ✅ FIX: affichage humain même si DB a des slugs attachés (bleuglacier, blanccasse...)
        """
        if not associations:
            return []

        print(f"\n   🖼️  Ajout des images aux associations (Solution 1 - DB is truth):")
        out = []

        for assoc in associations:
            context = assoc.get("occasion", "")

            image_data = ColorImageMatcher.get_image_for_context(
                season=saison,
                context=context,
            )

            assoc["image_url"] = image_data.get("url") if image_data.get("found") else None
            assoc["image_filename"] = image_data.get("filename")

            # ✅ Forcer les couleurs affichées à celles du visuel choisi (DB is truth)
            db_colors_raw = [c for c in (image_data.get("colors_db") or []) if c]
            db_colors_raw = db_colors_raw[:3]

            if image_data.get("found") and len(db_colors_raw) >= 2:
                # 1) afficher des noms "humains"
                assoc["colors"] = [self._pretty_color_from_db_token(c) for c in db_colors_raw]

                # 2) construire color_details (hex + displayName)
                # ✅ FIX pastilles: HEX doivent suivre la DB (pas GPT)
                assoc["color_hex"] = [self._hex_from_db_token(c) for c in db_colors_raw]

                assoc["color_details"] = [
                    {
                        "hex": self._hex_from_db_token(c),
                        "displayName": self._pretty_color_from_db_token(c),
                        "name": self._norm_db_token(c),  # stable même si attaché
                    }
                    for c in db_colors_raw
                ]
                # (optionnel) debug/trace
                assoc["colors_db"] = db_colors_raw

                print(f"      ✅ {context}: {db_colors_raw} -> {assoc.get('image_filename')}")
            else:
                print(f"      ⚠️  {context}: pas d'image trouvée")

            out.append(assoc)

        return out

    def _build_makeup_structure(self, result_part3: dict) -> dict:
        """✅ Construit structure makeup pour PDFMonkey (Page 7)"""
        guide = result_part3.get("guide_maquillage", {})

        # ✅ CORRIGÉ: Utiliser les VRAIES clés générées par Part 3
        makeup = {
            "foundation": guide.get("teint", ""),
            "blush": guide.get("blush", ""),
            "bronzer": guide.get("bronzer", ""),
            "highlighter": guide.get("highlighter", ""),
            "eyeshadows": guide.get("eyeshadows", ""),
            "eyeliner": guide.get("eyeliner", ""),
            "mascara": guide.get("mascara", ""),
            "brows": guide.get("brows", ""),
            "lipsNatural": guide.get("lipsNatural", ""),
            "lipsDay": guide.get("lipsDay", ""),
            "lipsEvening": guide.get("lipsEvening", ""),
            "lipsAvoid": guide.get("lipsAvoid", ""),
        }

        print(f"\n   ✅ Makeup structure créée:")
        filled = sum(1 for v in makeup.values() if v)
        print(f"      • Champs remplis: {filled}/12")
        print(f"      • Foundation: {'✅' if makeup['foundation'] else '❌'}")
        print(f"      • Blush: {'✅' if makeup['blush'] else '❌'}")
        print(f"      • Bronzer: {'✅' if makeup['bronzer'] else '❌'}")
        print(f"      • Eyeliner: {'✅' if makeup['eyeliner'] else '❌'}")
        print(f"      • Lips (Naturel): {'✅' if makeup['lipsNatural'] else '❌'}")
        print(f"      • Lips (Jour): {'✅' if makeup['lipsDay'] else '❌'}")
        print(f"      • Lips (Soirée): {'✅' if makeup['lipsEvening'] else '❌'}")

        return makeup

    async def _call_part1(self, user_data: dict, face_photo_url: str, eye_color: str = None, hair_color: str = None) -> dict:
        """PART 1 - Vision avec image"""
        print("\n" + "=" * 80)
        print("📋 APPEL 1/3: COLORIMETRY PART 1 - SAISON + ANALYSES")
        print("=" * 80)

        try:
            print("\n📌 AVANT APPEL:")
            print(f"   • Type: OpenAI Vision (gpt-4-turbo)")
            print(f"   • Max tokens: 1000")
            print(f"   • Image: {face_photo_url[:60]}...")

            self.openai.set_context("Colorimetry", "Part 1")
            self.openai.set_system_prompt(COLORIMETRY_PART1_SYSTEM_PROMPT)

            # ✅ FIX: Placeholders en MAJUSCULES + AGE ajouté
            user_prompt = COLORIMETRY_PART1_USER_PROMPT.format(
                EYE_COLOR=eye_color or user_data.get("eye_color", "indéterminé"),
                HAIR_COLOR=hair_color or user_data.get("hair_color", "indéterminé"),
                AGE=user_data.get("age", "indéterminé"),
            )

            print(f"\n🤖 APPEL OPENAI EN COURS...")
            print("DEBUG system_prompt chars:", len(COLORIMETRY_PART1_SYSTEM_PROMPT or ""))
            print("DEBUG user_prompt chars:", len(user_prompt or ""))

            # ✅ NEW: créer/charger un thumbnail pour réduire le coût vision
            thumb_url = await ImageThumbnailer.get_or_create_thumbnail_url(
                source_url=face_photo_url,
                bucket_name="user-photos-cache",
                max_side=768,
                quality=85,
            )

            print(f"   • Image (thumb): {thumb_url[:60]}...")

            # ✅ FIX: Utiliser analyze_image() au lieu de call_chat() avec has_image
            response = await self.openai.analyze_image(
                image_urls=[thumb_url],
                prompt=user_prompt,
                max_tokens=600,
                vision_detail_override="low",
            )

            print(f"✅ RÉPONSE REÇUE")

            prompt_tokens = response.get("prompt_tokens", 0)
            completion_tokens = response.get("completion_tokens", 0)
            total_tokens = response.get("total_tokens", 0)
            budget_percent = (total_tokens / 4000) * 100

            print(f"\n📊 TOKENS CONSOMMÉS:")
            print(f"   • Prompt: {prompt_tokens}")
            print(f"   • Completion: {completion_tokens}")
            print(f"   • Total: {total_tokens}")
            print(f"   • Budget: {budget_percent:.1f}% (vs 4000 max)")
            print(f"   • Status: {'⚠️ DÉPASSEMENT!' if budget_percent > 100 else '⚠️ Approche limite' if budget_percent > 90 else '✅ OK'}")

            content = response.get("content", "")
            print(f"\n📝 RÉPONSE BRUTE (premiers 400 chars):")
            print(f"   {content[:400]}...")

            print(f"\n🔍 PARSING JSON:")
            content_cleaned = self._fix_json_for_parsing(content)
            result = RobustJSONParser.parse_json_with_fallback(content_cleaned)

            if result:
                print(f"   ✅ Succès")
                print(f"      • Saison: {result.get('saison_confirmee', 'N/A')}")
                print(f"      • Sous-ton: {result.get('sous_ton_detecte', 'N/A')}")
            else:
                print(f"   ⚠️  Erreur parsing")
                result = {}

            print("\n" + "=" * 80 + "\n")
            return result

        except Exception as e:
            print(f"\n❌ ERREUR PART 1: {e}")
            import traceback
            traceback.print_exc()
            return {}

    async def _call_part2(self, saison: str, sous_ton: str, eye_color: str, hair_color: str) -> dict:
        """PART 2 - Texte pur"""
        print("\n" + "=" * 80)
        print("📋 APPEL 2/3: COLORIMETRY PART 2 - PALETTE + COULEURS GÉNÉRIQUES + ASSOCIATIONS")
        print("=" * 80)

        # Paramètres de sortie (utilisés aussi pour détecter un tronquage)
        max_tokens_first_call = 1800
        max_tokens_retry = 2000

        try:
            print("\n📌 AVANT APPEL:")
            print(f"   • Type: OpenAI Chat (gpt-4-turbo)")
            print(f"   • Max tokens (1er call): {max_tokens_first_call}")
            print(f"   • Input data: saison={saison}, sous_ton={sous_ton}")

            self.openai.set_context("Colorimetry", "Part 2")
            self.openai.set_system_prompt(COLORIMETRY_PART2_SYSTEM_PROMPT)

            user_prompt = COLORIMETRY_PART2_USER_PROMPT_TEMPLATE.format(
                SAISON=saison,
                SOUS_TON=sous_ton,
                EYE_COLOR=eye_color or "indéterminé",
                HAIR_COLOR=hair_color or "indéterminé",
            )

            print("\n🤖 APPEL OPENAI EN COURS...")
            response = await self.openai.call_chat(
                prompt=user_prompt,
                model="gpt-4-turbo",
                max_tokens=max_tokens_first_call,
                temperature=0.2,
            )
            print("✅ RÉPONSE REÇUE")

            finish_reason = response.get("finish_reason")
            completion_tokens = int(response.get("completion_tokens", 0) or 0)

            # ✅ Détection de tronquage
            is_truncated = (finish_reason == "length") or (completion_tokens >= int(0.98 * max_tokens_first_call))

            if is_truncated:
                print("⚠️ Part 2 tronquée (finish_reason=length ou tokens proches du max).")
                print("   ↳ Retry avec plus de tokens + response_format json_object + température basse.")

                response = await self.openai.call_chat(
                    prompt=user_prompt,
                    model="gpt-4-turbo",
                    max_tokens=max_tokens_retry,
                    temperature=0.1,
                    response_format={"type": "json_object"},
                )

            content = response.get("content", "") or ""

            prompt_tokens = int(response.get("prompt_tokens", 0) or 0)
            completion_tokens = int(response.get("completion_tokens", 0) or 0)
            total_tokens = int(response.get("total_tokens", prompt_tokens + completion_tokens) or (prompt_tokens + completion_tokens))
            budget_percent = (total_tokens / 4000) * 100 if total_tokens else 0.0

            print("\n📊 TOKENS CONSOMMÉS:")
            print(f"   • Prompt: {prompt_tokens}")
            print(f"   • Completion: {completion_tokens}")
            print(f"   • Total: {total_tokens}")
            print(f"   • Budget: {budget_percent:.1f}% (vs 4000 max)")
            print(f"   • Finish reason: {response.get('finish_reason')}")

            print("\n📝 RÉPONSE BRUTE (premiers 400 chars):")
            print(f"   {content[:400]}...")

            print("\n🔍 PARSING JSON (avec retry + fallback robuste):")
            parser = ColorimetryJSONParser()
            content_cleaned = parser.clean_gpt_response(content)
            result = parser.parse_json_safely(content_cleaned, max_retries=3)

            if result and parser.validate_part2_structure(result):
                palette = result.get("palette_personnalisee", [])
                generiques = result.get("couleurs_generiques", [])
                associations = result.get("associations_gagnantes", [])
                print("   ✅ Succès (parsing robuste)")
                print(f"      • Palette personnalisée: {len(palette)} couleurs")
                print(f"      • Couleurs génériques: {len(generiques)} couleurs")
                print(f"      • Associations: {len(associations)} occasions")
                return result

            print("   ⚠️  Parsing échoué → FALLBACK")
            return get_fallback_part2(saison)

        except Exception as e:
            print(f"\n❌ ERREUR PART 2: {e}")
            import traceback
            traceback.print_exc()
            return get_fallback_part2(saison)

    async def _call_part3(self, saison: str, sous_ton: str, unwanted_colors: list) -> dict:
        """PART 3 - Texte pur"""
        print("\n" + "=" * 80)
        print("📋 APPEL 3/3: COLORIMETRY PART 3 - MAQUILLAGE + VERNIS + COULEURS REFUSÉES")
        print("=" * 80)

        try:
            unwanted_str = ", ".join(unwanted_colors) if unwanted_colors else "Aucune"

            print("\n📌 AVANT APPEL:")
            print(f"   • Type: OpenAI Chat (gpt-4)")
            print(f"   • Max tokens: 1400")
            print(f"   • Couleurs refusées: {unwanted_str}")

            self.openai.set_context("Colorimetry", "Part 3")
            self.openai.set_system_prompt(COLORIMETRY_PART3_SYSTEM_PROMPT)

            user_prompt = COLORIMETRY_PART3_USER_PROMPT_TEMPLATE.format(
                SAISON=saison,
                SOUS_TON=sous_ton,
                UNWANTED_COLORS=unwanted_str,
            )

            print(f"\n🤖 APPEL OPENAI EN COURS...")
            response = await self.openai.call_chat(
                prompt=user_prompt,
                model="gpt-4",
                max_tokens=1400,
            )
            print(f"✅ RÉPONSE REÇUE")

            prompt_tokens = response.get("prompt_tokens", 0)
            completion_tokens = response.get("completion_tokens", 0)
            total_tokens = response.get("total_tokens", 0)
            budget_percent = (total_tokens / 4000) * 100

            print(f"\n📊 TOKENS CONSOMMÉS:")
            print(f"   • Prompt: {prompt_tokens}")
            print(f"   • Completion: {completion_tokens}")
            print(f"   • Total: {total_tokens}")
            print(f"   • Budget: {budget_percent:.1f}% (vs 4000 max)")

            content = response.get("content", "")
            print(f"\n📝 RÉPONSE BRUTE (premiers 400 chars):")
            print(f"   {content[:400]}...")

            print(f"\n🔍 PARSING JSON (Part 3 robuste):")
            content_cleaned = self._fix_json_for_parsing(content)
            result = RobustJSONParser.parse_json_with_fallback(content_cleaned)

            if result:
                print(f"   ✅ Succès")
                print(f"      • Vernis ongles: {len(result.get('nailColors', []))} couleurs")
                print(f"      • Guide maquillage: {len(result.get('guide_maquillage', {}))} champs")
                print(f"      • Couleurs refusées: {len(result.get('unwanted_colors', []))} couleurs")
            else:
                print(f"   ⚠️  Erreur parsing")
                result = {}

            print("\n" + "=" * 80 + "\n")
            return result

        except Exception as e:
            print(f"\n❌ ERREUR PART 3: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def _fix_json_for_parsing(self, text: str) -> str:
        """Nettoie le JSON avant parsing"""
        if not text:
            return text

        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
        text = text.replace("\\'", "'")

        def fix_invalid_escapes(match):
            char = match.group(1)
            if char in '"\\bfnrt/':
                return match.group(0)
            if char == "u":
                return match.group(0)
            return char

        text = re.sub(r"\\([^\"\\bfnrtu/])", fix_invalid_escapes, text)
        return text


# ═══════════════════════════════════════════════════════════
# ✅ INITIALISER SUPABASE POUR COLOR IMAGE MATCHER
# ═══════════════════════════════════════════════════════════
import os
from app.services.color_image_matcher import ColorImageMatcher

# Utiliser les mêmes credentials que pour Supabase (tu les as déjà)
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://eqtovvjueqsralaprsvm.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")  # À configurer en env var!

if SUPABASE_KEY:
    ColorImageMatcher.init_supabase(SUPABASE_URL, SUPABASE_KEY)

colorimetry_service = ColorimetryService()