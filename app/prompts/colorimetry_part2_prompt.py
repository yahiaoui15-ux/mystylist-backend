"""
COLORIMETRY PART 2 v8.0 - OPTIMIZED TOKEN USAGE
✅ Structures minimales
✅ Pas de duplication
✅ Estimé: 2500 tokens max vs 5688 avant
"""

COLORIMETRY_PART2_SYSTEM_PROMPT = """You are a color analysis expert. You MUST respond with ONLY valid JSON, no text before or after.
Start with { and end with }. Every response must be valid JSON.
Escape apostrophes with backslash in strings (example: s\'harmonise)."""

COLORIMETRY_PART2_USER_PROMPT_TEMPLATE = """RETURN ONLY JSON. NO TEXT BEFORE OR AFTER.

CLIENT PROFILE:
Season: {SAISON}
Undertone: {SOUS_TON}
Eyes: {EYE_COLOR}
Hair: {HAIR_COLOR}

TASK: Generate a personalized color palette and associations.

REQUIRED JSON STRUCTURE (no text, no preamble, start with {{ end with }}):

{{
  "palette_personnalisee": [
    {{"name": "color1", "hex": "#HEX", "note": 10, "commentaire": "Brief description max 15 words"}},
    ... 10 colors total (notes 10,10,9,9,9,9,8,8,8,8)
  ],
  "allColorsWithNotes": [
    {{"name": "camel", "displayName": "Camel", "note": 10, "commentaire": "Essential harmony", "hex": "#C19A6B"}},
    {{"name": "jaune", "displayName": "Yellow", "note": 9, "commentaire": "Gold amplifies natural tone", "hex": "#FFFF00"}},
    {{"name": "orange", "displayName": "Orange", "note": 9, "commentaire": "Warm amplifies vitality", "hex": "#FFA500"}},
    {{"name": "marron", "displayName": "Brown", "note": 9, "commentaire": "Intensifies eyes", "hex": "#8B4513"}},
    {{"name": "rose_corail", "displayName": "Coral Pink", "note": 9, "commentaire": "Harmonizes beautifully", "hex": "#FF7F50"}},
    {{"name": "bordeaux", "displayName": "Burgundy", "note": 9, "commentaire": "Warm sophisticated perfect", "hex": "#800020"}},
    {{"name": "rouge", "displayName": "Red", "note": 8, "commentaire": "Warm OK cold not", "hex": "#FF0000"}},
    {{"name": "vert", "displayName": "Green", "note": 8, "commentaire": "Warm OK", "hex": "#008000"}},
    {{"name": "beige", "displayName": "Beige", "note": 8, "commentaire": "Warm flatters complexion", "hex": "#F5F5DC"}},
    {{"name": "kaki", "displayName": "Khaki", "note": 8, "commentaire": "Versatile warm", "hex": "#C3B091"}},
    {{"name": "gris", "displayName": "Gray", "note": 6, "commentaire": "Taupe OK cold not", "hex": "#808080"}},
    {{"name": "blanc", "displayName": "White", "note": 5, "commentaire": "Pure can jar", "hex": "#FFFFFF"}},
    {{"name": "noir", "displayName": "Black", "note": 4, "commentaire": "Charcoal better", "hex": "#000000"}},
    {{"name": "bleu", "displayName": "Blue", "note": 3, "commentaire": "Cold isolates", "hex": "#0000FF"}},
    {{"name": "marine", "displayName": "Navy", "note": 3, "commentaire": "Cold disharmonizes", "hex": "#000080"}},
    {{"name": "violet", "displayName": "Violet", "note": 2, "commentaire": "Cold dulls", "hex": "#800080"}},
    {{"name": "rose_pale", "displayName": "Pale Pink", "note": 2, "commentaire": "Cold dulls complexion", "hex": "#FFB6C1"}},
    {{"name": "turquoise", "displayName": "Turquoise", "note": 1, "commentaire": "Cold incompatible", "hex": "#40E0D0"}},
    {{"name": "rose_fuchsia", "displayName": "Fuchsia", "note": 1, "commentaire": "Cold extreme avoid", "hex": "#FF20F0"}}
  ],
  "associations_gagnantes": [
    {{"occasion": "professionnel", "colors": ["C1", "C2", "C3"], "color_hex": ["#H1", "#H2", "#H3"], "effet": "Elegant confident", "description": "Office meetings presentations authority calm warm professional"}},
    {{"occasion": "casual", "colors": ["C2", "C3", "C4"], "color_hex": ["#H2", "#H3", "#H4"], "effet": "Effortless natural", "description": "Relaxation cafe shopping leisure light energy accessibility"}},
    {{"occasion": "soiree", "colors": ["C5", "C6", "C1"], "color_hex": ["#H5", "#H6", "#H1"], "effet": "Sophistication", "description": "Dinner cocktail evening elegance richness depth warmth"}},
    {{"occasion": "weekend", "colors": ["C3", "C1", "C7"], "color_hex": ["#H3", "#H1", "#H7"], "effet": "Natural energetic", "description": "Nature hiking exploration stability authenticity wellbeing relaxation"}},
    {{"occasion": "famille", "colors": ["C4", "C2", "C5"], "color_hex": ["#H4", "#H2", "#H5"], "effet": "Warm welcoming", "description": "Important moments kindness gentleness solidity radiance elegance"}}
  ]
}}

INSTRUCTIONS:
1. Generate 10 personalized colors for palette_personnalisee (must match season/undertone)
2. For allColorsWithNotes: ONLY update the 10 from your palette above to have note 10,9,8. Keep other 9 colors unchanged.
3. For associations_gagnantes: Use your 10 palette colors (C1-C10) to create 5 winning associations
4. ALL commentaires must be max 15 words
5. Escape apostrophes: s\'harmonise not s'harmonise
6. START WITH { END WITH }
7. NO TEXT BEFORE OR AFTER JSON
"""

# Keep fallback exactly the same
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