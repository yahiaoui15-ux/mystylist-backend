"""
COLORIMETRY PART 2 v6.0 - ACCOLADES ÉCHAPPÉES POUR .format()
✅ CRITIQUE: Utilise {{ et }} pour accolades littérales
✅ Utilise {SAISON}, {SOUS_TON} pour variables
✅ Budget: ~50%
"""

COLORIMETRY_PART2_SYSTEM_PROMPT = """Vous êtes expert colorimètre. Générez UNIQUEMENT JSON valide.
Commencez par { et terminez par }.
Échappez apostrophes: s\'harmonise
Aucun texte avant/après JSON."""

COLORIMETRY_PART2_USER_PROMPT_TEMPLATE = """PALETTE COLORIMETRIE - Part 2.

CLIENT: Saison {SAISON} | Sous-ton {SOUS_TON} | Yeux {EYE_COLOR} | Cheveux {HAIR_COLOR}

RETOURNEZ JSON VALIDE:
{{
  "palette_personnalisee": [
    {{"name": "couleur1", "hex": "#HEX1", "note": 10, "commentaire": "15 mots max"}},
    {{"name": "couleur2", "hex": "#HEX2", "note": 10, "commentaire": "15 mots max"}},
    {{"name": "couleur3", "hex": "#HEX3", "note": 9, "commentaire": "15 mots max"}},
    {{"name": "couleur4", "hex": "#HEX4", "note": 9, "commentaire": "15 mots max"}},
    {{"name": "couleur5", "hex": "#HEX5", "note": 9, "commentaire": "15 mots max"}},
    {{"name": "couleur6", "hex": "#HEX6", "note": 9, "commentaire": "15 mots max"}},
    {{"name": "couleur7", "hex": "#HEX7", "note": 8, "commentaire": "15 mots max"}},
    {{"name": "couleur8", "hex": "#HEX8", "note": 8, "commentaire": "15 mots max"}},
    {{"name": "couleur9", "hex": "#HEX9", "note": 8, "commentaire": "15 mots max"}},
    {{"name": "couleur10", "hex": "#HEX10", "note": 8, "commentaire": "15 mots max"}}
  ],
  "allColorsWithNotes": [
    {{"name": "camel", "displayName": "Camel", "note": 10, "commentaire": "Essentiel harmonie naturelle", "hex": "#C19A6B"}},
    {{"name": "jaune", "displayName": "Jaune", "note": 9, "commentaire": "Doré amplifie or naturel", "hex": "#FFFF00"}},
    {{"name": "orange", "displayName": "Orange", "note": 9, "commentaire": "Chaud amplifie vitalité", "hex": "#FFA500"}},
    {{"name": "rouge", "displayName": "Rouge", "note": 8, "commentaire": "Chauds OK froids non", "hex": "#FF0000"}},
    {{"name": "marron", "displayName": "Marron", "note": 9, "commentaire": "Intensifie yeux", "hex": "#8B4513"}},
    {{"name": "rose_corail", "displayName": "Rose Corail", "note": 9, "commentaire": "S\'harmonise magnifiquement", "hex": "#FF7F50"}},
    {{"name": "bordeaux", "displayName": "Bordeaux", "note": 9, "commentaire": "Chaud sophistiqué parfait", "hex": "#800020"}},
    {{"name": "beige", "displayName": "Beige", "note": 8, "commentaire": "Chaud flatte carnation", "hex": "#F5F5DC"}},
    {{"name": "kaki", "displayName": "Kaki", "note": 8, "commentaire": "Polyvalent chaud", "hex": "#C3B091"}},
    {{"name": "vert", "displayName": "Vert", "note": 8, "commentaire": "Chauds OK", "hex": "#008000"}},
    {{"name": "gris", "displayName": "Gris", "note": 6, "commentaire": "Taupe OK froid non", "hex": "#808080"}},
    {{"name": "blanc", "displayName": "Blanc", "note": 5, "commentaire": "Pur peut heurter", "hex": "#FFFFFF"}},
    {{"name": "noir", "displayName": "Noir", "note": 4, "commentaire": "Charbon meilleur", "hex": "#000000"}},
    {{"name": "bleu", "displayName": "Bleu", "note": 3, "commentaire": "Froids isolent", "hex": "#0000FF"}},
    {{"name": "marine", "displayName": "Marine", "note": 3, "commentaire": "Froid désharmonise", "hex": "#000080"}},
    {{"name": "violet", "displayName": "Violet", "note": 2, "commentaire": "Froid ternit", "hex": "#800080"}},
    {{"name": "rose_pale", "displayName": "Rose Pale", "note": 2, "commentaire": "Froid ternit teint", "hex": "#FFB6C1"}},
    {{"name": "turquoise", "displayName": "Turquoise", "note": 1, "commentaire": "Froide incompatible", "hex": "#40E0D0"}},
    {{"name": "rose_fuchsia", "displayName": "Rose Fuchsia", "note": 1, "commentaire": "Froid extrême", "hex": "#FF20F0"}}
  ],
  "associations_gagnantes": [
    {{"occasion": "professionnel", "colors": ["C1", "C2", "C3"], "color_hex": ["#H1", "#H2", "#H3"], "effet": "Élégance confidente", "description": "Bureau réunion présentation autorité apaisement chaleur professionnelle"}},
    {{"occasion": "casual", "colors": ["C2", "C3", "C4"], "color_hex": ["#H2", "#H3", "#H4"], "effet": "Sans-effort naturel", "description": "Décontraction café shopping loisirs énergie légère accessibilité"}},
    {{"occasion": "soiree", "colors": ["C5", "C6", "C1"], "color_hex": ["#H5", "#H6", "#H1"], "effet": "Sophistication", "description": "Dîner cocktail élégance nocturne richesse profondeur chaleur"}},
    {{"occasion": "weekend", "colors": ["C3", "C1", "C7"], "color_hex": ["#H3", "#H1", "#H7"], "effet": "Naturel énergique", "description": "Nature randonnée exploration stabilité authenticité bien-être détente"}},
    {{"occasion": "famille", "colors": ["C4", "C2", "C5"], "color_hex": ["#H4", "#H2", "#H5"], "effet": "Chaleur accueillante", "description": "Moments importants bienveillance douceur solidité rayonnement"}}
  ]
}}

REGLES:
✅ palette_personnalisee = 10 couleurs EXACTEMENT
✅ allColorsWithNotes = 19 couleurs (noms FIXES)
✅ associations_gagnantes = 5 occasions
✅ Commentaires = max 15 mots
✅ Apostrophes échappées: s\'harmonise
✅ JSON COMPLET VALIDE - terminer avec }}
"""

# Fallback - ne pas changer!
FALLBACK_PALETTE_AND_ASSOCIATIONS = {
    "palette_personnalisee": [
        {"name": "terracotta", "hex": "#E2725B", "note": 10, "commentaire": "Couleur centrale chauffe teint"},
        {"name": "camel", "hex": "#C19A6B", "note": 10, "commentaire": "Incontournable harmonie naturelle"},
        {"name": "moutarde", "hex": "#E1AD01", "note": 9, "commentaire": "Jaune doré illumine teint"},
        {"name": "cuivre", "hex": "#B87333", "note": 9, "commentaire": "Métallique chaud sophistiqué"},
        {"name": "bordeaux", "hex": "#6D071A", "note": 9, "commentaire": "Élégance nocturne par excellence"},
        {"name": "rose_corail", "hex": "#FF7F50", "note": 9, "commentaire": "Chaud s\'harmonise magnifiquement"},
        {"name": "olive", "hex": "#808000", "note": 8, "commentaire": "Vert-brun chaud naturel"},
        {"name": "brique", "hex": "#CB4154", "note": 8, "commentaire": "Rouge-brun subtil sophistiqué"},
        {"name": "kaki", "hex": "#C3B091", "note": 8, "commentaire": "Classique chaud polyvalent"},
        {"name": "chocolat", "hex": "#7B3F00", "note": 8, "commentaire": "Marron foncé élégant stable"}
    ],
    "allColorsWithNotes": [
        {"name": "camel", "displayName": "Camel", "note": 10, "commentaire": "Essentiel harmonie naturelle", "hex": "#C19A6B"},
        {"name": "jaune", "displayName": "Jaune", "note": 9, "commentaire": "Doré amplifie or naturel", "hex": "#FFFF00"},
        {"name": "orange", "displayName": "Orange", "note": 9, "commentaire": "Chaud amplifie vitalité", "hex": "#FFA500"},
        {"name": "marron", "displayName": "Marron", "note": 9, "commentaire": "Intensifie yeux", "hex": "#8B4513"},
        {"name": "rose_corail", "displayName": "Rose Corail", "note": 9, "commentaire": "S\'harmonise magnifiquement", "hex": "#FF7F50"},
        {"name": "bordeaux", "displayName": "Bordeaux", "note": 9, "commentaire": "Chaud sophistiqué parfait", "hex": "#800020"},
        {"name": "rouge", "displayName": "Rouge", "note": 8, "commentaire": "Chauds harmonisent froids non", "hex": "#FF0000"},
        {"name": "vert", "displayName": "Vert", "note": 8, "commentaire": "Chauds harmonisent", "hex": "#008000"},
        {"name": "beige", "displayName": "Beige", "note": 8, "commentaire": "Chaud flatte carnation", "hex": "#F5F5DC"},
        {"name": "kaki", "displayName": "Kaki", "note": 8, "commentaire": "Chaud crée harmonie", "hex": "#C3B091"},
        {"name": "gris", "displayName": "Gris", "note": 6, "commentaire": "Taupe OK froid non", "hex": "#808080"},
        {"name": "blanc", "displayName": "Blanc", "note": 5, "commentaire": "Pur heurte autre mieux", "hex": "#FFFFFF"},
        {"name": "noir", "displayName": "Noir", "note": 4, "commentaire": "Pur dur charbon meilleur", "hex": "#000000"},
        {"name": "bleu", "displayName": "Bleu", "note": 3, "commentaire": "Froids isolent à éviter", "hex": "#0000FF"},
        {"name": "marine", "displayName": "Marine", "note": 3, "commentaire": "Froid désharmonise", "hex": "#000080"},
        {"name": "violet", "displayName": "Violet", "note": 2, "commentaire": "Froid ternit présence", "hex": "#800080"},
        {"name": "rose_pale", "displayName": "Rose Pale", "note": 2, "commentaire": "Froid ternit teint", "hex": "#FFB6C1"},
        {"name": "rose_fuchsia", "displayName": "Rose Fuchsia", "note": 1, "commentaire": "Froid extrême éviter", "hex": "#FF20F0"},
        {"name": "turquoise", "displayName": "Turquoise", "note": 1, "commentaire": "Froide incompatible total", "hex": "#40E0D0"}
    ],
    "associations_gagnantes": [
        {"occasion": "professionnel", "colors": ["Terracotta", "Marron", "Camel"], "color_hex": ["#E2725B", "#8B4513", "#C19A6B"], "effet": "Élégance confidente"},
        {"occasion": "casual", "colors": ["Kaki", "Camel", "Ocre"], "color_hex": ["#C3B091", "#C19A6B", "#CC7722"], "effet": "Naturel sans-effort"},
        {"occasion": "soiree", "colors": ["Bordeaux", "Gris Taupe", "Terracotta"], "color_hex": ["#6D071A", "#8B8589", "#E2725B"], "effet": "Sophistication chaleureuse"},
        {"occasion": "weekend", "colors": ["Olive", "Camel", "Terre"], "color_hex": ["#808000", "#C19A6B", "#D2B48C"], "effet": "Naturel énergique"},
        {"occasion": "famille", "colors": ["Rose Corail", "Beige", "Marron"], "color_hex": ["#FF7F50", "#F5F5DC", "#8B4513"], "effet": "Chaleur accueillante"}
    ]
}