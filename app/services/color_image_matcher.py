"""
COLOR IMAGE MATCHER v2 - Requête Supabase directement
✅ Cherche les images dans la table colorimetry_images
✅ Fuzzy-match intelligent sur les couleurs
✅ Retourne l'URL directement depuis la BDD
"""

from difflib import SequenceMatcher
import re
from supabase import create_client, Client
from typing import Optional

class ColorImageMatcher:
    """Matcher intelligent - requête Supabase"""
    
    # 🎨 MAPPING: Couleurs OpenAI → Noms de fichiers (pour fuzzy match)
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
        "cerise": ["bordeaux", "corail", "rouille"],  # Cerise → couleurs rouges
        
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
    
    # Supabase client (sera initialisé une seule fois)
    _supabase_client: Optional[Client] = None
    
    @classmethod
    def init_supabase(cls, url: str, key: str):
        """Initialise le client Supabase une seule fois"""
        if cls._supabase_client is None:
            cls._supabase_client = create_client(url, key)
            print("✅ ColorImageMatcher: Supabase client initialisé")
    
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
    
    @classmethod
    def get_image_for_association(cls, season: str, context: str, colors: list) -> dict:
        """
        Trouve l'image correspondant à une association de couleurs
        
        ✅ VERSION v2: Requête Supabase directement
        
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
        
        if not cls._supabase_client:
            return {
                "filename": None,
                "url": None,
                "found": False,
                "reason": "Supabase client not initialized"
            }
        
        # Normaliser saison et contexte
        season_slug = cls.SEASONS.get(season, season.lower())
        context_slug = cls.CONTEXTS.get(context, context.lower())
        
        # Matcher les 3 couleurs
        color_slugs = []
        for color in colors:
            matched = cls.find_matching_filename_color(color)
            if matched:
                color_slugs.append(matched)
        
        # Si on a au moins 2 couleurs matchées, chercher en BDD
        if len(color_slugs) < 2:
            return {
                "filename": None,
                "url": None,
                "found": False,
                "reason": f"Could not match all colors (matched: {len(color_slugs)}/3)"
            }
        
        try:
            # 🔍 REQUÊTE SUPABASE - Chercher une image qui match saison + context + couleurs
            response = cls._supabase_client.table("colorimetry_images").select(
                "file_name, public_url"
            ).eq("season", season_slug).eq("context", context_slug).execute()
            
            if not response.data or len(response.data) == 0:
                return {
                    "filename": None,
                    "url": None,
                    "found": False,
                    "reason": f"No images found for {season_slug}/{context_slug}"
                }
            
            # 📊 FUZZY MATCH: Parmi les images trouvées, cherche celle qui match le mieux les couleurs
            best_match = None
            best_score = 0
            
            for image in response.data:
                # Extraire les couleurs du filename
                # Format: colorimetry_{season}_{context}_{color1}_{color2}_{color3}.jpg
                filename = image["file_name"]
                parts = filename.replace(".jpg", "").split("_")
                
                if len(parts) < 6:
                    continue
                
                image_colors = [parts[3], parts[4], parts[5]]
                
                # Calculer le score de match
                matches = 0
                for color_slug in color_slugs:
                    if color_slug in image_colors:
                        matches += 1
                
                # Score: nombre de couleurs qui matchent
                score = matches / 3.0  # Sur 3 couleurs
                
                if score > best_score:
                    best_score = score
                    best_match = image
            
            if best_match:
                return {
                    "filename": best_match["file_name"],
                    "url": best_match["public_url"],
                    "found": True,
                    "score": best_score,
                    "season": season_slug,
                    "context": context_slug,
                    "colors_matched": color_slugs
                }
            else:
                # Pas de match parfait, retourner la première image trouvée
                if response.data:
                    first = response.data[0]
                    return {
                        "filename": first["file_name"],
                        "url": first["public_url"],
                        "found": True,
                        "score": 0.5,  # Score faible car pas de match parfait
                        "reason": "No perfect color match, using first available image"
                    }
        
        except Exception as e:
            print(f"❌ Erreur requête Supabase: {e}")
            return {
                "filename": None,
                "url": None,
                "found": False,
                "reason": f"Database error: {str(e)}"
            }