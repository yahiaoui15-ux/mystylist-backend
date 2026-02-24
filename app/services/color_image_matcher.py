"""
COLOR IMAGE MATCHER v2.2 - ROBUST DB MATCH
✅ Cherche les images dans la table colorimetry_images
✅ Normalise saisons + contextes (accents, casse, alias)
✅ Match des couleurs via colonnes DB color_1/color_2/color_3 (PAS via filename)
✅ Fuzzy-match intelligent sur les couleurs OpenAI
✅ Retourne l'URL directement depuis la BDD + couleurs DB
"""

from difflib import SequenceMatcher
from supabase import create_client, Client
from typing import Optional, List, Dict, Any


class ColorImageMatcher:
    """Matcher intelligent - requête Supabase"""

    # 🎨 MAPPING: Couleurs OpenAI → Slugs DB (pour fuzzy match)
    # IMPORTANT: les slugs retournés doivent correspondre à tes valeurs DB (color_1/2/3)
    COLOR_ALIASES = {
        # ROSES/CORAILS
        "rose": ["rose", "peche", "corail", "saumon", "rose_nude", "rose_poudre", "rose_pastel", "rose_vieux", "rose_froid", "rose_fuchsia", "rose_rubis"],
        "pêche": ["peche"],
        "peche": ["peche"],
        "corail": ["corail"],
        "saumon": ["saumon"],
        "rose pâle": ["rose_pale", "rose_nude", "rose_poudre"],
        "rose pale": ["rose_pale", "rose_nude", "rose_poudre"],
        "rose pétale": ["rose_pale", "peche"],
        "rose petale": ["rose_pale", "peche"],
        "rose fuchsia": ["rose_fuchsia"],

        # ORANGES/ABRICOT
        "orange": ["orange", "abricot", "rouille", "moutarde", "terracotta", "terre_cuite", "ocre"],
        "abricot": ["abricot"],
        "rouille": ["rouille"],
        "moutarde": ["moutarde"],
        "terracotta": ["terracotta", "terre_cuite"],
        "terre cuite": ["terre_cuite"],
        "ocre": ["ocre"],
        "orangé pastel": ["abricot", "peche"],
        "orange pastel": ["abricot", "peche"],

        # JAUNES/OR
        "jaune": ["jaune", "or", "champagne"],
        "or": ["or", "bronze", "cuivre", "ambre"],
        "champagne": ["champagne"],
        "vanille": ["vanille"],
        "sable": ["sable", "ecru"],

        # BEIGES/NEUTRES
        "beige": ["beige", "taupe", "ivoire", "creme", "ecru", "sable"],
        "ivoire": ["ivoire"],
        "crème": ["creme"],
        "creme": ["creme"],
        "écru": ["ecru"],
        "ecru": ["ecru"],
        "taupe": ["taupe", "taupe_froid"],
        "camel": ["camel"],
        "brun": ["brun", "chocolat"],
        "chocolat": ["chocolat"],
        "gris": ["gris", "gris_fonce", "gris_acier", "gris_argent", "gris_perle"],

        # VERTS
        "vert": ["vert", "vert_mousse", "vert_doux", "vert_emeraude", "vert_pomme", "vert_eau", "kaki", "olive"],
        "menthe": ["menthe"],
        "kaki": ["kaki"],
        "olive": ["olive"],
        "émeraude": ["vert_emeraude"],
        "emeraude": ["vert_emeraude"],
        "vert pomme": ["vert_pomme"],
        "vert mousse": ["vert_mousse"],

        # BLEUS/TURQUOISE
        "bleu": ["bleu", "bleu_ciel", "bleu_acier", "bleu_poudre", "bleu_pastel", "bleu_electrique", "bleu_nuit", "bleu_ardoise"],
        "turquoise": ["turquoise"],
        "lavande": ["lavande"],
        "marine": ["marine"],
        "bleu ciel": ["bleu_ciel"],
        "bleu électrique": ["bleu_electrique"],
        "bleu electrique": ["bleu_electrique"],
        "bleu nuit": ["bleu_nuit"],
        "bleu ardoise": ["bleu_ardoise"],
        "bleu acier": ["bleu_acier"],
        "bleu poudre": ["bleu_poudre"],

        # ROUGES/BORDEAUX
        "rouge": ["rouge", "rouge_rubis", "bordeaux"],
        "bordeaux": ["bordeaux"],
        "rubis": ["rouge_rubis"],
        "cuivre": ["cuivre"],
        "cerise": ["bordeaux", "corail", "rouille"],

        # VIOLETS
        "violet": ["violet", "prune", "prune_douce"],
        "prune": ["prune", "prune_douce"],
        "mauve": ["mauve"],

        # NOIRS/BLANC
        "noir": ["noir"],
        "blanc": ["blanc"],
        "anthracite": ["anthracite"],
        "argent": ["argent", "gris_argent"],
        "perle": ["perle", "gris_perle"],

        # SPÉCIAL
        "denim": ["denim"],
        "ble": ["ble"],
    }

    # 🌍 SAISONS (alias robustes -> slug DB)
    SEASON_ALIASES = {
        "printemps": "printemps",
        "spring": "printemps",

        "ete": "ete",
        "été": "ete",
        "summer": "ete",

        "automne": "automne",
        "autumn": "automne",
        "fall": "automne",

        "hiver": "hiver",
        "winter": "hiver",
    }

    # 📋 CONTEXTES (alias robustes -> slug DB)
    CONTEXT_ALIASES = {
        "professionnel": "professionnel",
        "pro": "professionnel",
        "work": "professionnel",
        "bureau": "professionnel",

        "casual": "casual",
        "quotidien": "casual",
        "famille": "casual",

        "soiree": "soiree",
        "soirée": "soiree",
        "evening": "soiree",
        "party": "soiree",

        "weekend": "weekend",
        "week-end": "weekend",
        "week end": "weekend",
    }

    # Supabase client (sera initialisé une seule fois)
    _supabase_client: Optional[Client] = None

    @classmethod
    def init_supabase(cls, url: str, key: str) -> None:
        """Initialise le client Supabase une seule fois"""
        if cls._supabase_client is None:
            cls._supabase_client = create_client(url, key)
            print("✅ ColorImageMatcher: Supabase client initialisé")

    # -----------------------------
    # Normalisation helpers
    # -----------------------------
    @staticmethod
    def _strip_accents(s: str) -> str:
        if not s:
            return ""
        repl = (
            ("à", "a"), ("â", "a"),
            ("é", "e"), ("è", "e"), ("ê", "e"), ("ë", "e"),
            ("î", "i"), ("ï", "i"),
            ("ô", "o"), ("ö", "o"),
            ("ù", "u"), ("û", "u"), ("ü", "u"),
            ("ç", "c"),
        )
        s2 = s
        for a, b in repl:
            s2 = s2.replace(a, b).replace(a.upper(), b)
        return s2

    @classmethod
    def normalize_slug(cls, value: str) -> str:
        """Normalise en slug: lower + strip accents + espaces -> underscore"""
        if not value:
            return ""
        v = cls._strip_accents(str(value).strip().lower())
        v = " ".join(v.split())
        v = v.replace("-", " ")
        v = v.replace(" ", "_")
        return v

    @classmethod
    def normalize_season(cls, season: str) -> str:
        s = cls.normalize_slug(season)
        # "printemps" / "ete" / etc.
        return cls.SEASON_ALIASES.get(s, s)

    @classmethod
    def normalize_context(cls, context: str) -> str:
        c = cls.normalize_slug(context)
        # "soiree" etc.
        return cls.CONTEXT_ALIASES.get(c, c)

    # -----------------------------
    # Matching colors
    # -----------------------------
    @classmethod
    def normalize_color(cls, color_name: str) -> str:
        """Normalise un nom de couleur OpenAI en slug"""
        return cls.normalize_slug(color_name)

    @classmethod
    def find_matching_db_color_slug(cls, color_name: str) -> Optional[str]:
        """
        Trouve le slug DB qui match le mieux avec la couleur OpenAI
        Retourne: "peche", "menthe", "olive", etc.
        """
        normalized = cls.normalize_color(color_name)
        if not normalized:
            return None

        # 1) Match exact / substring via alias
        for openai_color, db_slugs in cls.COLOR_ALIASES.items():
            openai_norm = cls.normalize_color(openai_color)
            if normalized == openai_norm:
                return db_slugs[0]
            # contient / inclus
            if openai_norm and (openai_norm in normalized or normalized in openai_norm):
                return db_slugs[0]
            for word in openai_norm.split("_"):
                if word and (word in normalized or normalized in word):
                    return db_slugs[0]

        # 2) Fallback fuzzy
        best_match = None
        best_ratio = 0.0
        for _, db_slugs in cls.COLOR_ALIASES.items():
            for slug in db_slugs:
                ratio = SequenceMatcher(None, normalized, cls.normalize_slug(slug)).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = slug

        return best_match if best_ratio >= 0.60 else None

    # -----------------------------
    # DB queries
    # -----------------------------
    @classmethod
    def get_image_for_context(cls, season: str, context: str) -> Dict[str, Any]:
        """
        Solution 1: récupère 1 record DB par (season, context)
        Retourne url + couleurs associées à l'image.
        """
        if not cls._supabase_client:
            return {"found": False, "reason": "Supabase client not initialized"}

        season_slug = cls.normalize_season(season)
        context_slug = cls.normalize_context(context)

        try:
            resp = (
                cls._supabase_client
                .table("colorimetry_images")
                .select("id, season, context, color_1, color_2, color_3, file_name, public_url, created_at")
                .eq("season", season_slug)
                .eq("context", context_slug)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )

            if not resp.data:
                return {"found": False, "reason": f"No image for {season_slug}/{context_slug}"}

            row = resp.data[0]
            return {
                "found": True,
                "id": row.get("id"),
                "season": row.get("season"),
                "context": row.get("context"),
                "url": row.get("public_url"),
                "filename": row.get("file_name"),
                "colors_db": [row.get("color_1"), row.get("color_2"), row.get("color_3")],
            }

        except Exception as e:
            return {"found": False, "reason": f"Database error: {str(e)}"}

    @classmethod
    def get_image_for_association(cls, season: str, context: str, colors: List[str]) -> Dict[str, Any]:
        """
        Trouve l'image correspondant à une association de couleurs

        ✅ VERSION v2.2: Requête Supabase directement + match sur color_1/2/3 (DB), pas filename.

        Args:
            season: "Printemps", "Été", "Automne", "Hiver" (ou slugs / anglais)
            context: "professionnel", "casual", "soirée", "weekend" (ou alias)
            colors: ["Rose Pétale", "Menthe Vital", "Orangé Pastel"]

        Returns:
            {
                "filename": "...",
                "url": "...",
                "found": True/False,
                "score": 0..1,
                "season": "...",
                "context": "...",
                "colors_matched": ["peche","menthe","abricot"],
                "colors_db": ["peche","menthe","orange"]
            }
        """
        if not cls._supabase_client:
            return {"filename": None, "url": None, "found": False, "reason": "Supabase client not initialized"}

        season_slug = cls.normalize_season(season)
        context_slug = cls.normalize_context(context)

        # Matcher les couleurs OpenAI -> slugs DB
        color_slugs: List[str] = []
        for c in colors or []:
            matched = cls.find_matching_db_color_slug(c)
            if matched:
                color_slugs.append(cls.normalize_slug(matched))

        # Dédupliquer en gardant l'ordre
        seen = set()
        color_slugs = [x for x in color_slugs if x and not (x in seen or seen.add(x))]

        if len(color_slugs) < 2:
            return {
                "filename": None,
                "url": None,
                "found": False,
                "reason": f"Could not match enough colors (matched: {len(color_slugs)}/{len(colors or [])})",
            }

        try:
            # On récupère toutes les images du couple (season, context)
            response = (
                cls._supabase_client
                .table("colorimetry_images")
                .select("id, file_name, public_url, color_1, color_2, color_3, created_at")
                .eq("season", season_slug)
                .eq("context", context_slug)
                .execute()
            )

            if not response.data:
                return {
                    "filename": None,
                    "url": None,
                    "found": False,
                    "reason": f"No images found for {season_slug}/{context_slug}",
                }

            best = None
            best_score = -1.0

            for row in response.data:
                db_colors = [
                    cls.normalize_slug(row.get("color_1") or ""),
                    cls.normalize_slug(row.get("color_2") or ""),
                    cls.normalize_slug(row.get("color_3") or ""),
                ]
                db_colors = [c for c in db_colors if c]

                if not db_colors:
                    continue

                matches = sum(1 for slug in color_slugs if slug in db_colors)
                score = matches / 3.0  # sur 3 (même si OpenAI n’a matché que 2)

                # tie-breaker: si score égal, prend la plus récente
                if score > best_score:
                    best_score = score
                    best = row
                elif score == best_score and best is not None:
                    # fallback "plus récente" si created_at existe
                    cur_dt = row.get("created_at") or ""
                    best_dt = best.get("created_at") or ""
                    if cur_dt and best_dt and cur_dt > best_dt:
                        best = row

            if best:
                colors_db = [best.get("color_1"), best.get("color_2"), best.get("color_3")]
                return {
                    "filename": best.get("file_name"),
                    "url": best.get("public_url"),
                    "found": True,
                    "score": max(0.0, best_score),
                    "season": season_slug,
                    "context": context_slug,
                    "colors_matched": color_slugs,
                    "colors_db": colors_db,
                    "id": best.get("id"),
                }

            # fallback extrême: première ligne
            first = response.data[0]
            return {
                "filename": first.get("file_name"),
                "url": first.get("public_url"),
                "found": True,
                "score": 0.0,
                "season": season_slug,
                "context": context_slug,
                "colors_matched": color_slugs,
                "colors_db": [first.get("color_1"), first.get("color_2"), first.get("color_3")],
                "reason": "No scored match, using first available image",
                "id": first.get("id"),
            }

        except Exception as e:
            return {"filename": None, "url": None, "found": False, "reason": f"Database error: {str(e)}"}