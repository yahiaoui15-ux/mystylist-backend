"""
COLORIMETRY PART 2 FIXED v9.1 - NOMS FRANCAIS DANS PALETTE
✓ Demande les vrais noms (camel, moutarde, bordeaux) pas color1-10
✓ Prompt simplifié et clair
✓ Fallback avec données françaises complètes
✓ ENCODAGE UTF-8 CORRECT
"""

COLORIMETRY_PART2_SYSTEM_PROMPT = """You are a color analysis expert. You MUST respond with ONLY valid JSON, no text before or after.
Start with { and end with }. Every response must be valid JSON.
Escape apostrophes with backslash in strings (example: s\'harmonise)."""

# ✓ FIX: Demander NOMS FRANCAIS au lieu de color1-10
COLORIMETRY_PART2_USER_PROMPT_TEMPLATE = """RETURN ONLY JSON. NO TEXT BEFORE OR AFTER.
Start immediately with single brace and end with single brace.

CLIENT PROFILE:
Season: {SAISON}
Undertone: {SOUS_TON}
Eyes: {EYE_COLOR}
Hair: {HAIR_COLOR}

TASK: Generate a personalized color palette with FRENCH COLOR NAMES and winning color combinations for different occasions.

REQUIRED JSON STRUCTURE (start with single {{ end with single }}):

{{
  "palette_personnalisee": [
    {{"name": "camel", "hex": "#C19A6B", "note": 10, "commentaire": "Couleur essentielle reproduit harmonie naturelle cliente", "displayName": "Camel"}},
    {{"name": "moutarde", "hex": "#E1AD01", "note": 10, "commentaire": "Jaune doré illumine teint de manière subtile", "displayName": "Moutarde"}},
    {{"name": "bordeaux", "hex": "#800020", "note": 9, "commentaire": "Élégance nocturne par excellence", "displayName": "Bordeaux"}},
    {{"name": "rose_corail", "hex": "#FF7F50", "note": 9, "commentaire": "Rose chaud s\'harmonise magnifiquement avec carnation", "displayName": "Rose Corail"}},
    {{"name": "olive", "hex": "#808000", "note": 9, "commentaire": "Vert-brun chaud naturel très polyvalent", "displayName": "Olive"}},
    {{"name": "cuivre", "hex": "#B87333", "note": 9, "commentaire": "Métallique chaud sophistiqué amplifies dorure", "displayName": "Cuivre"}},
    {{"name": "brique", "hex": "#CB4154", "note": 8, "commentaire": "Rouge-brun subtil et très sophistiqué", "displayName": "Brique"}},
    {{"name": "kaki", "hex": "#C3B091", "note": 8, "commentaire": "Classique chaud très polyvalent pour tenues", "displayName": "Kaki"}},
    {{"name": "chocolat", "hex": "#7B3F00", "note": 8, "commentaire": "Marron foncé élégant et stable", "displayName": "Chocolat"}},
    {{"name": "terracotta", "hex": "#E2725B", "note": 8, "commentaire": "Chauffe le teint apporte vitalité et énergie", "displayName": "Terracotta"}}
  ],

  "allColorsWithNotes": [
    {{"name": "camel", "displayName": "Camel", "note": 10, "commentaire": "Camel essentiel. Reproduit harmonie naturelle.", "hex": "#C19A6B"}},
    {{"name": "jaune", "displayName": "Jaune", "note": 9, "commentaire": "Jaunes dorés amplifient or naturel.", "hex": "#FFFF00"}},
    {{"name": "orange", "displayName": "Orange", "note": 9, "commentaire": "Orange chaud amplifie vitalité.", "hex": "#FFA500"}},
    {{"name": "marron", "displayName": "Marron", "note": 9, "commentaire": "Marrons chauds intensifient yeux.", "hex": "#8B4513"}},
    {{"name": "rose_corail", "displayName": "Rose Corail", "note": 9, "commentaire": "Rose corail chaud s\'harmonise magnifiquement.", "hex": "#FF7F50"}},
    {{"name": "bordeaux", "displayName": "Bordeaux", "note": 9, "commentaire": "Bordeaux chaud sophistiqué s\'harmonise parfait.", "hex": "#800020"}},
    {{"name": "rouge", "displayName": "Rouge", "note": 8, "commentaire": "Rouges chauds harmonisent. Froids ternissent.", "hex": "#FF0000"}},
    {{"name": "vert", "displayName": "Vert", "note": 8, "commentaire": "Verts chauds harmonisent. Acides froids non.", "hex": "#008000"}},
    {{"name": "beige", "displayName": "Beige", "note": 8, "commentaire": "Beiges chauds flattent carnation.", "hex": "#F5F5DC"}},
    {{"name": "kaki", "displayName": "Kaki", "note": 8, "commentaire": "Kaki chaud complète sous-ton créant harmonie.", "hex": "#C3B091"}},
    {{"name": "gris", "displayName": "Gris", "note": 6, "commentaire": "Gris taupe OK. Gris froid non.", "hex": "#808080"}},
    {{"name": "blanc", "displayName": "Blanc", "note": 5, "commentaire": "Blanc pur crée micro-contraste heurté.", "hex": "#FFFFFF"}},
    {{"name": "noir", "displayName": "Noir", "note": 4, "commentaire": "Noir pur dur. Charbon plus flatteur.", "hex": "#000000"}},
    {{"name": "bleu", "displayName": "Bleu", "note": 3, "commentaire": "Blus froids isolent. À éviter absolument.", "hex": "#0000FF"}},
    {{"name": "marine", "displayName": "Marine", "note": 3, "commentaire": "Marine froid crée contraste désharmonisé.", "hex": "#000080"}},
    {{"name": "violet", "displayName": "Violet", "note": 2, "commentaire": "Violets froids ternissent présence.", "hex": "#800080"}},
    {{"name": "rose_pale", "displayName": "Rose Pâle", "note": 2, "commentaire": "Rose pâle froid ternit teint chaud.", "hex": "#FFB6C1"}},
    {{"name": "rose_fuchsia", "displayName": "Rose Fuchsia", "note": 1, "commentaire": "Fuchsia froid crée dissonance extrême.", "hex": "#FF1493"}},
    {{"name": "turquoise", "displayName": "Turquoise", "note": 1, "commentaire": "Turquoise froide incompatible total.", "hex": "#40E0D0"}}
  ],

  "associations_gagnantes": [
    {{"occasion": "professionnel", "colors": ["Camel", "Marron", "Beige"], "color_hex": ["#C19A6B", "#8B4513", "#F5F5DC"], "effet": "Élégance confidente", "description": "Bureau meetings presentations authority calm warm professional"}},
    {{"occasion": "casual", "colors": ["Kaki", "Camel", "Terracotta"], "color_hex": ["#C3B091", "#C19A6B", "#E2725B"], "effet": "Effortless natural", "description": "Relaxation cafe shopping leisure light energy accessibility"}},
    {{"occasion": "soiree", "colors": ["Bordeaux", "Chocolat", "Cuivre"], "color_hex": ["#800020", "#7B3F00", "#B87333"], "effet": "Sophistication", "description": "Dinner cocktail evening elegance richness depth warmth"}},
    {{"occasion": "weekend", "colors": ["Olive", "Camel", "Terracotta"], "color_hex": ["#808000", "#C19A6B", "#E2725B"], "effet": "Natural energetic", "description": "Nature hiking exploration stability authenticity wellbeing relaxation"}},
    {{"occasion": "famille", "colors": ["Rose Corail", "Moutarde", "Kaki"], "color_hex": ["#FF7F50", "#E1AD01", "#C3B091"], "effet": "Warm welcoming", "description": "Important moments kindness gentleness solidity radiance elegance"}}
  ]
}}

INSTRUCTIONS (CRITICAL):
1. Generate 10 personalized colors for palette_personnalisee with FRENCH NAMES (NOT color1-10!)
   Use names like: camel, moutarde, bordeaux, rose_corail, olive, cuivre, brique, kaki, chocolat, terracotta
2. Each color MUST have: name (lowercase french), hex code (#RRGGBB), note (10/9/8), commentaire (max 15 words), displayName (capitalized)
3. For allColorsWithNotes: Update the 10 from your palette above to have proper notes. Keep other 9 colors unchanged.
4. For associations_gagnantes: Create 5 winning color combinations using your 10 palette colors
5. ALL commentaires must be in FRENCH and max 15 words
6. Escape apostrophes: s\'harmonise not s'harmonise
7. MANDATORY: Start with single brace {{, end with single brace }}. NO TEXT BEFORE OR AFTER JSON.
8. Return response in French language throughout
"""

# ✓ FALLBACK avec noms français corrects
FALLBACK_PALETTE_AND_ASSOCIATIONS = {
    "palette_personnalisee": [
        {"name": "camel", "hex": "#C19A6B", "note": 10, "commentaire": "Couleur essentielle reproduit harmonie naturelle", "displayName": "Camel"},
        {"name": "moutarde", "hex": "#E1AD01", "note": 10, "commentaire": "Jaune doré illumine teint de manière subtile", "displayName": "Moutarde"},
        {"name": "bordeaux", "hex": "#800020", "note": 9, "commentaire": "Élégance nocturne par excellence absolue", "displayName": "Bordeaux"},
        {"name": "rose_corail", "hex": "#FF7F50", "note": 9, "commentaire": "Rose chaud s'harmonise magnifiquement avec teint", "displayName": "Rose Corail"},
        {"name": "olive", "hex": "#808000", "note": 9, "commentaire": "Vert-brun chaud naturel très polyvalent", "displayName": "Olive"},
        {"name": "cuivre", "hex": "#B87333", "note": 9, "commentaire": "Métallique chaud sophistiqué amplifies dorure naturelle", "displayName": "Cuivre"},
        {"name": "brique", "hex": "#CB4154", "note": 8, "commentaire": "Rouge-brun subtil très sophistiqué élégant", "displayName": "Brique"},
        {"name": "kaki", "hex": "#C3B091", "note": 8, "commentaire": "Classique chaud très polyvalent garde-robe", "displayName": "Kaki"},
        {"name": "chocolat", "hex": "#7B3F00", "note": 8, "commentaire": "Marron foncé élégant stable intemporel", "displayName": "Chocolat"},
        {"name": "terracotta", "hex": "#E2725B", "note": 8, "commentaire": "Chauffe le teint apporte vitalité énergie", "displayName": "Terracotta"}
    ],
    "allColorsWithNotes": [
        {"name": "camel", "displayName": "Camel", "note": 10, "commentaire": "Camel essentiel. Reproduit harmonie naturelle.", "hex": "#C19A6B"},
        {"name": "jaune", "displayName": "Jaune", "note": 9, "commentaire": "Jaunes dorés amplifient or naturel.", "hex": "#FFFF00"},
        {"name": "orange", "displayName": "Orange", "note": 9, "commentaire": "Orange chaud amplifie vitalité.", "hex": "#FFA500"},
        {"name": "marron", "displayName": "Marron", "note": 9, "commentaire": "Marrons chauds intensifient yeux.", "hex": "#8B4513"},
        {"name": "rose_corail", "displayName": "Rose Corail", "note": 9, "commentaire": "Rose corail chaud s'harmonise magnifiquement.", "hex": "#FF7F50"},
        {"name": "bordeaux", "displayName": "Bordeaux", "note": 9, "commentaire": "Bordeaux chaud sophistiqué s'harmonise parfait.", "hex": "#800020"},
        {"name": "rouge", "displayName": "Rouge", "note": 8, "commentaire": "Rouges chauds harmonisent. Froids ternissent.", "hex": "#FF0000"},
        {"name": "vert", "displayName": "Vert", "note": 8, "commentaire": "Verts chauds harmonisent. Acides froids non.", "hex": "#008000"},
        {"name": "beige", "displayName": "Beige", "note": 8, "commentaire": "Beiges chauds flattent carnation.", "hex": "#F5F5DC"},
        {"name": "kaki", "displayName": "Kaki", "note": 8, "commentaire": "Kaki chaud crée harmonie avec sous-ton.", "hex": "#C3B091"},
        {"name": "gris", "displayName": "Gris", "note": 6, "commentaire": "Gris taupe OK. Gris froid non.", "hex": "#808080"},
        {"name": "blanc", "displayName": "Blanc", "note": 5, "commentaire": "Blanc pur crée contraste heurté.", "hex": "#FFFFFF"},
        {"name": "noir", "displayName": "Noir", "note": 4, "commentaire": "Noir pur dur. Charbon plus flatteur.", "hex": "#000000"},
        {"name": "bleu", "displayName": "Bleu", "note": 3, "commentaire": "Blus froids isolent. À éviter absolument.", "hex": "#0000FF"},
        {"name": "marine", "displayName": "Marine", "note": 3, "commentaire": "Marine froid désharmonise visuellement.", "hex": "#000080"},
        {"name": "violet", "displayName": "Violet", "note": 2, "commentaire": "Violets froids ternissent présence.", "hex": "#800080"},
        {"name": "rose_pale", "displayName": "Rose Pale", "note": 2, "commentaire": "Rose pâle froid ternit teint.", "hex": "#FFB6C1"},
        {"name": "rose_fuchsia", "displayName": "Rose Fuchsia", "note": 1, "commentaire": "Fuchsia froid crée dissonance extrême.", "hex": "#FF20F0"},
        {"name": "turquoise", "displayName": "Turquoise", "note": 1, "commentaire": "Turquoise froide incompatible total.", "hex": "#40E0D0"}
    ],
    "associations_gagnantes": [
        {"occasion": "professionnel", "colors": ["Camel", "Marron", "Beige"], "color_hex": ["#C19A6B", "#8B4513", "#F5F5DC"], "effet": "Élégance confidente"},
        {"occasion": "casual", "colors": ["Kaki", "Camel", "Terracotta"], "color_hex": ["#C3B091", "#C19A6B", "#E2725B"], "effet": "Naturel sans-effort"},
        {"occasion": "soiree", "colors": ["Bordeaux", "Chocolat", "Cuivre"], "color_hex": ["#800020", "#7B3F00", "#B87333"], "effet": "Sophistication chaleureuse"},
        {"occasion": "weekend", "colors": ["Olive", "Camel", "Terracotta"], "color_hex": ["#808000", "#C19A6B", "#E2725B"], "effet": "Naturel énergique"},
        {"occasion": "famille", "colors": ["Rose Corail", "Moutarde", "Kaki"], "color_hex": ["#FF7F50", "#E1AD01", "#C3B091"], "effet": "Chaleur accueillante"}
    ]
}