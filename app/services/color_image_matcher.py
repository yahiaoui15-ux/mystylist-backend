"""
COLOR IMAGE MATCHER - Trouve les images correspondantes aux associations de couleurs
✅ Normalise les noms de couleurs OpenAI vers les noms de fichiers
✅ Cherche l'image dans Supabase qui match saison + contexte + 3 couleurs
✅ Retourne l'URL publique de l'image
"""

from difflib import SequenceMatcher
import re

class ColorImageMatcher:
    """Matcher intelligent couleurs OpenAI → images Supabase"""
    
    # 🎨 MAPPING: Couleurs OpenAI → Noms de fichiers
    COLOR_ALIASES = {
        # ROSES/CORAILS
        "rose": ["rose", "peche", "corail", "saumon", "rosenude", "rosepoudre", "rosepastel", "rosevieux", "rosefroid", "rosefuchsia", "roserubis"],
        "pêche": ["peche"],
        "corail": ["corail"],
        "saumon": ["saumon"],
        "rose pâle": ["rosepale", "rosenude", "rosepoudre"],
        "rose pétale": ["rosepale", "peche"],
        "rose fuchsia": ["rosefuchsia"],
        
        # ORANGES/ABRICOT
        "orange": ["orange", "abricot", "rouille", "moutarde", "terracotta", "terrecuite", "ocre"],
        "abricot": ["abricot"],
        "rouille": ["rouille"],
        "moutarde": ["moutarde"],
        "terracotta": ["terracotta", "terrecuite"],
        "ocre": ["ocre"],
        "orangé pastel": ["abricot", "peche"],
        
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
        "écru": ["ecru"],
        "taupe": ["taupe", "taupefroid"],
        "camel": ["camel"],
        "brun": ["brun", "chocolat"],
        "gris": ["gris", "grisfonce", "grisacier", "grisargent", "grisperle"],
        
        # VERTS
        "vert": ["vert", "vertmousse", "vertdoux", "vertemerande", "vertpomme", "vertdeau", "kaki", "olive"],
        "menthe": ["menthe"],
        "kaki": ["kaki"],
        "olive": ["olive"],
        "émeraude": ["vertemerande"],
        "vert pomme": ["vertpomme"],
        "vert mousse": ["vertmousse"],
        
        # BLEUS/TURQUOISE
        "bleu": ["bleu", "bleuciel", "bleuacier", "bleupoudre", "bleupastel", "bleuelectrique", "bleunuit", "bleuardoise"],
        "turquoise": ["turquoise"],
        "lavande": ["lavande"],
        "marine": ["marine"],
        "bleu ciel": ["bleuciel"],
        "bleu électrique": ["bleuelectrique"],
        "bleu nuit": ["bleunuit"],
        "bleu ardoise": ["bleuardoise"],
        "bleu acier": ["bleuacier"],
        "bleu poudre": ["bleupoudre"],
        
        # ROUGES/BORDEAUX
        "rouge": ["rouge", "rougerubis", "bordeaux"],
        "bordeaux": ["bordeaux"],
        "rubis": ["rougerubis"],
        "cuivre": ["cuivre"],
        
        # VIOLETS
        "violet": ["violet", "prune", "prunedouce"],
        "prune": ["prune", "prunedouce"],
        "mauve": ["mauve"],
        
        # NOIRS/BLANC
        "noir": ["noir"],
        "blanc": ["blanc"],
        "anthracite": ["anthracite"],
        "argent": ["argent", "grisargent"],
        "perle": ["perle", "grisperle"],
        
        # SPÉCIAL
        "denim": ["denim"],
        "ble": ["ble"],
    }
    
    # 🌍 SAISONS
    SEASONS = {
        "Printemps": "printemps",
        "Été": "ete",
        "Automne": "automne",
        "Hiver": "hiver",
    }
    
    # 📋 CONTEXTES
    CONTEXTS = {
        "professionnel": "professionnel",
        "casual": "casual",
        "soirée": "soiree",
        "weekend": "weekend",
        "famille": "casual",  # Fallback à casual
    }
    
    @staticmethod
    def normalize_color(color_name: str) -> str:
        """Normalise un nom de couleur OpenAI en slug"""
        if not color_name:
            return ""
        
        # Minuscules + supprime accents
        normalized = color_name.lower()
        normalized = normalized.replace("à", "a").replace("é", "e").replace("è", "e")
        normalized = normalized.replace("ê", "e").replace("ë", "e").replace("ï", "i")
        normalized = normalized.replace("ô", "o").replace("ö", "o").replace("û", "u")
        normalized = normalized.replace("ù", "u").replace("ç", "c")
        
        # Supprime espaces
        normalized = normalized.strip()
        
        return normalized
    
    @staticmethod
    def find_matching_filename_color(color_name: str) -> str:
        """
        Trouve le nom de couleur de fichier qui match le mieux avec la couleur OpenAI
        Retourne: "peche", "menthe", "olive", etc.
        """
        normalized = ColorImageMatcher.normalize_color(color_name)
        
        # Cherche dans le mapping
        for openai_color, filename_colors in ColorImageMatcher.COLOR_ALIASES.items():
            openai_norm = ColorImageMatcher.normalize_color(openai_color)
            
            # Match exact?
            if normalized == openai_norm:
                return filename_colors[0]  # Retourne le premier match
            
            # Contient le mot?
            for word in openai_norm.split():
                if word in normalized or normalized in word:
                    return filename_colors[0]
        
        # Fallback: cherche avec SequenceMatcher si pas de match exact
        best_match = None
        best_ratio = 0
        
        for openai_color, filename_colors in ColorImageMatcher.COLOR_ALIASES.items():
            for filename_color in filename_colors:
                ratio = SequenceMatcher(None, normalized, filename_color).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = filename_color
        
        return best_match if best_ratio > 0.6 else None
    
    @staticmethod
    def build_image_filename(season: str, context: str, colors: list) -> str:
        """
        Construit le nom du fichier image à partir de saison, contexte et 3 couleurs
        Ex: "colorimetry_printemps_casual_peche_menthe_ivoire.jpg"
        """
        # Normaliser saison et contexte
        season_slug = ColorImageMatcher.SEASONS.get(season, season.lower())
        context_slug = ColorImageMatcher.CONTEXTS.get(context, context.lower())
        
        # Matcher les 3 couleurs
        color_slugs = []
        for color in colors:
            matched = ColorImageMatcher.find_matching_filename_color(color)
            if matched:
                color_slugs.append(matched)
        
        # Si on a moins de 3 couleurs matchées, retourner None
        if len(color_slugs) < 3:
            return None
        
        # Construire le nom
        filename = f"colorimetry_{season_slug}_{context_slug}_{color_slugs[0]}_{color_slugs[1]}_{color_slugs[2]}.jpg"
        return filename
    
    @staticmethod
    def get_supabase_image_url(filename: str, bucket: str = "colorimetry") -> str:
        """
        Retourne l'URL publique Supabase pour une image
        Ex: https://eqtovvjueqsralaprsvm.supabase.co/storage/v1/object/public/colorimetry/filename.jpg
        """
        if not filename:
            return None
        
        base_url = "https://eqtovvjueqsralaprsvm.supabase.co/storage/v1/object/public"
        return f"{base_url}/{bucket}/{filename}"
    
    @staticmethod
    def get_image_for_association(season: str, context: str, colors: list) -> dict:
        """
        Retourne l'image correspondant à une association de couleurs
        
        Args:
            season: "Printemps", "Été", "Automne", "Hiver"
            context: "professionnel", "casual", "soirée", "weekend"
            colors: ["Rose Pétale", "Menthe Vital", "Orangé Pastel"]
        
        Returns:
            {
                "filename": "colorimetry_printemps_casual_peche_menthe_orange.jpg",
                "url": "https://...",
                "found": True/False
            }
        """
        filename = ColorImageMatcher.build_image_filename(season, context, colors)
        
        if not filename:
            return {
                "filename": None,
                "url": None,
                "found": False,
                "reason": "Could not match all 3 colors"
            }
        
        url = ColorImageMatcher.get_supabase_image_url(filename)
        
        return {
            "filename": filename,
            "url": url,
            "found": True,
            "season": season,
            "context": context,
            "colors_matched": colors
        }


# 🧪 TEST
if __name__ == "__main__":
    matcher = ColorImageMatcher()
    
    # Test 1: Printemps Casual
    result = matcher.get_image_for_association(
        season="Printemps",
        context="casual",
        colors=["Rose Pétale", "Menthe Vital", "Orangé Pastel"]
    )
    print(f"Test 1: {result}")
    
    # Test 2: Automne Professionnel
    result = matcher.get_image_for_association(
        season="Automne",
        context="professionnel",
        colors=["Camel", "Olive", "Ivoire"]
    )
    print(f"Test 2: {result}")
    
    # Test 3: Été Soirée
    result = matcher.get_image_for_association(
        season="Été",
        context="soirée",
        colors=["Bleu Ardoise", "Mauve", "Perle"]
    )
    print(f"Test 3: {result}")