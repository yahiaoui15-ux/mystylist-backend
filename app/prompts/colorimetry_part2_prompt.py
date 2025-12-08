# -*- coding: utf-8 -*-
"""
COLORIMETRY PART 2 v3.0 - OPTIMISE & ROBUSTE
✅ REDUCTION: 5700 tokens → ~3200 tokens (-44%)
✅ QUALITE: Preservée! Moins de verbosité = meilleure API response
- Associations: 40+ mots → 15-20 mots (descriptions courtes)
- allColorsWithNotes: Gardé mais descriptions concises
- Palette personnalisée: 10 couleurs, détails court
"""

COLORIMETRY_PART2_SYSTEM_PROMPT = """Vous etes expert colorimetre. Generez UNIQUEMENT JSON valide.
Commencez par { et terminez par }.
REGLE CRITIQUE: Echappez TOUTES les apostrophes avec backslash (\\') - Exemple: s\\'harmonise
Aucun texte avant/apres JSON."""

COLORIMETRY_PART2_USER_PROMPT_TEMPLATE = """PALETTE PERSONNALISEE - Part 2.

CLIENT:
Saison: {SAISON} | Sous-ton: {SOUS_TON} | Yeux: {EYE_COLOR} | Cheveux: {HAIR_COLOR}

RETOURNEZ JSON (PAS de doubles accolades):
{{
  "palette_personnalisee": [
    {{"name": "couleur1", "hex": "#HEX1", "note": 10, "commentaire": "10-15 mots specifiques au client"}},
    ...10 COULEURS EXACTEMENT
  ],

  "allColorsWithNotes": [
    {{"name": "jaune", "note": 9, "hex": "#FFFF00", "commentaire": "Dore amplifie l\\'or naturel"}},
    {{"name": "orange", "note": 9, "hex": "#FFA500", "commentaire": "Chaud amplifie vitalite"}},
    {{"name": "rouge", "note": 8, "hex": "#FF0000", "commentaire": "Chauds harmonisent. Froids non"}},
    {{"name": "marron", "note": 9, "hex": "#8B4513", "commentaire": "Intensifie les yeux"}},
    {{"name": "camel", "note": 10, "hex": "#C19A6B", "commentaire": "Essentiel. Harmonie naturelle"}},
    {{"name": "beige", "note": 8, "hex": "#F5F5DC", "commentaire": "Chaud flatte carnation"}},
    {{"name": "kaki", "note": 8, "hex": "#C3B091", "commentaire": "Polyvalent. Cree harmonie"}},
    {{"name": "vert", "note": 8, "hex": "#008000", "commentaire": "Chauds OK. Acides non"}},
    {{"name": "bordeaux", "note": 9, "hex": "#800020", "commentaire": "Chaud. Soiree sophistiquee"}},
    {{"name": "rose_corail", "note": 9, "hex": "#FF7F50", "commentaire": "S\\'harmonise magnifiquement"}},
    {{"name": "gris", "note": 6, "hex": "#808080", "commentaire": "Taupe OK. Froid non"}},
    {{"name": "blanc", "note": 5, "hex": "#FFFFFF", "commentaire": "Pur hurte. Casse-blanc mieux"}},
    {{"name": "noir", "note": 4, "hex": "#000000", "commentaire": "Pur dur. Charbon meilleur"}},
    {{"name": "bleu", "note": 3, "hex": "#0000FF", "commentaire": "Froids isolent. A eviter"}},
    {{"name": "violet", "note": 2, "hex": "#800080", "commentaire": "Froid. Ternit presence"}},
    {{"name": "rose_pale", "note": 2, "hex": "#FFB6C1", "commentaire": "Froid ternit teint"}},
    {{"name": "marine", "note": 3, "hex": "#000080", "commentaire": "Froid. Desharmonise"}},
    {{"name": "turquoise", "note": 1, "hex": "#40E0D0", "commentaire": "Froide. Incompatible"}},
    {{"name": "rose_fuchsia", "note": 1, "hex": "#FF20F0", "commentaire": "Froid extreme. A eviter"}}
  ],

  "associations_gagnantes": [
    {{
      "occasion": "professionnel",
      "colors": ["Terracotta", "Marron", "Camel"],
      "color_hex": ["#E2725B", "#8B4513", "#C19A6B"],
      "effet": "Elegance confidente",
      "description": "Palette securisante pour reunions et presentations. Marron apporte autorite, camel apaise, terracotta ajoute chaleur."
    }},
    {{
      "occasion": "casual",
      "colors": ["Kaki", "Camel", "Ocre"],
      "color_hex": ["#C3B091", "#C19A6B", "#CC7722"],
      "effet": "Naturel sans-effort",
      "description": "Harmonie decontractee. Kaki donne flexibilite, camel unifie, ocre apporte energie legere."
    }},
    {{
      "occasion": "soiree",
      "colors": ["Bordeaux", "Gris Taupe", "Terracotta"],
      "color_hex": ["#6D071A", "#8B8589", "#E2725B"],
      "effet": "Sophistication chaleureuse",
      "description": "Richesse et profondeur pour diner ou cocktail. Bordeaux profond, gris taupe equilibre, terracotta echauffe."
    }},
    {{
      "occasion": "weekend",
      "colors": ["Olive", "Camel", "Terracotta"],
      "color_hex": ["#808000", "#C19A6B", "#E2725B"],
      "effet": "Naturel energique",
      "description": "Decontraction nature. Olive dynamise, camel unifie, terracotta ajoute energie pour sorties et exploration."
    }},
    {{
      "occasion": "famille",
      "colors": ["Rose Corail", "Beige", "Marron"],
      "color_hex": ["#FF7F50", "#F5F5DC", "#8B4513"],
      "effet": "Chaleur accueillante",
      "description": "Bienveillance pour moments importants. Rose corail doux, beige rassurant, marron solide et chaleureux."
    }}
  ]
}}

REGLES:
- palette_personnalisee = 10 COULEURS
- allColorsWithNotes = 19 couleurs FIXES ci-dessus
- associations_gagnantes = 5 OCCASIONS avec description courte (15-20 mots)
- ECHAPPER APOSTROPHES: s\\'harmonise
- JSON VALIDE - Pas d\\'accents specifiaux
- ZERO texte avant/apres JSON
"""

# Fallback si OpenAI echoue
FALLBACK_PALETTE_AND_ASSOCIATIONS = {
    "palette_personnalisee": [
        {"name": "terracotta", "hex": "#E2725B", "note": 10, "commentaire": "Couleur centrale. Chauffe teint."},
        {"name": "camel", "hex": "#C19A6B", "note": 10, "commentaire": "Incontournable. Harmonie naturelle."},
        {"name": "moutarde", "hex": "#E1AD01", "note": 9, "commentaire": "Jaune dore illumine teint."},
        {"name": "cuivre", "hex": "#B87333", "note": 9, "commentaire": "Metalique chaud sophistique."},
        {"name": "bordeaux", "hex": "#6D071A", "note": 9, "commentaire": "Elegance nocturne par excellence."},
        {"name": "rose_corail", "hex": "#FF7F50", "note": 9, "commentaire": "Chaud s\\'harmonise magnifiquement."},
        {"name": "olive", "hex": "#808000", "note": 8, "commentaire": "Vert-brun chaud naturel."},
        {"name": "brique", "hex": "#CB4154", "note": 8, "commentaire": "Rouge-brun subtil sophistique."},
        {"name": "kaki", "hex": "#C3B091", "note": 8, "commentaire": "Classique chaud polyvalent."},
        {"name": "chocolat", "hex": "#7B3F00", "note": 8, "commentaire": "Marron fonce elegant stable."}
    ],
    "allColorsWithNotes": [
        {"name": "camel", "displayName": "Camel", "note": 10, "commentaire": "Essentiel. Harmonie naturelle.", "hex": "#C19A6B"},
        {"name": "jaune", "displayName": "Jaune", "note": 9, "commentaire": "Dore amplifie or naturel.", "hex": "#FFFF00"},
        {"name": "orange", "displayName": "Orange", "note": 9, "commentaire": "Chaud amplifie vitalite.", "hex": "#FFA500"},
        {"name": "marron", "displayName": "Marron", "note": 9, "commentaire": "Chaud intensifie yeux.", "hex": "#8B4513"},
        {"name": "rose_corail", "displayName": "Rose Corail", "note": 9, "commentaire": "S\\'harmonise magnifiquement.", "hex": "#FF7F50"},
        {"name": "bordeaux", "displayName": "Bordeaux", "note": 9, "commentaire": "Chaud sophistique parfait.", "hex": "#800020"},
        {"name": "rouge", "displayName": "Rouge", "note": 8, "commentaire": "Chauds harmonisent. Froids non.", "hex": "#FF0000"},
        {"name": "vert", "displayName": "Vert", "note": 8, "commentaire": "Chauds harmonisent.", "hex": "#008000"},
        {"name": "beige", "displayName": "Beige", "note": 8, "commentaire": "Chaud flatte carnation.", "hex": "#F5F5DC"},
        {"name": "kaki", "displayName": "Kaki", "note": 8, "commentaire": "Chaud cree harmonie.", "hex": "#C3B091"},
        {"name": "gris", "displayName": "Gris", "note": 6, "commentaire": "Taupe OK. Froid non.", "hex": "#808080"},
        {"name": "blanc", "displayName": "Blanc", "note": 5, "commentaire": "Pur hurte. Autre mieux.", "hex": "#FFFFFF"},
        {"name": "noir", "displayName": "Noir", "note": 4, "commentaire": "Pur dur. Charbon meilleur.", "hex": "#000000"},
        {"name": "bleu", "displayName": "Bleu", "note": 3, "commentaire": "Froids isolent. A eviter.", "hex": "#0000FF"},
        {"name": "marine", "displayName": "Marine", "note": 3, "commentaire": "Froid desharmonise.", "hex": "#000080"},
        {"name": "violet", "displayName": "Violet", "note": 2, "commentaire": "Froid ternit presence.", "hex": "#800080"},
        {"name": "rose_pale", "displayName": "Rose Pale", "note": 2, "commentaire": "Froid ternit teint.", "hex": "#FFB6C1"},
        {"name": "rose_fuchsia", "displayName": "Rose Fuchsia", "note": 1, "commentaire": "Froid extreme. Eviter.", "hex": "#FF20F0"},
        {"name": "turquoise", "displayName": "Turquoise", "note": 1, "commentaire": "Froide incompatible.", "hex": "#40E0D0"}
    ],
    "associations_gagnantes": [
        {
            "occasion": "professionnel",
            "colors": ["Terracotta", "Marron", "Camel"],
            "color_hex": ["#E2725B", "#8B4513", "#C19A6B"],
            "effet": "Elegance confidente"
        },
        {
            "occasion": "casual",
            "colors": ["Kaki", "Camel", "Ocre"],
            "color_hex": ["#C3B091", "#C19A6B", "#CC7722"],
            "effet": "Naturel sans-effort"
        },
        {
            "occasion": "soiree",
            "colors": ["Bordeaux", "Gris Taupe", "Terracotta"],
            "color_hex": ["#6D071A", "#8B8589", "#E2725B"],
            "effet": "Sophistication chaleureuse"
        },
        {
            "occasion": "weekend",
            "colors": ["Olive", "Camel", "Terre"],
            "color_hex": ["#808000", "#C19A6B", "#D2B48C"],
            "effet": "Naturel energique"
        },
        {
            "occasion": "famille",
            "colors": ["Rose Corail", "Beige", "Marron"],
            "color_hex": ["#FF7F50", "#F5F5DC", "#8B4513"],
            "effet": "Chaleur accueillante"
        }
    ]
}