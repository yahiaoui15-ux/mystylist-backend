# -*- coding: utf-8 -*-
"""
COLORIMETRY PART 2 v4.0 - CORRIGE AVEC LE BON NOM
✅ CIBLE: app/prompts/colorimetry_part2_prompt.py (PAS colorimetry_prompt.py!)
✅ REDUCTION: 5700 tokens → ~3200 tokens
✅ Remplace COMPLETEMENT le fichier existant
"""

COLORIMETRY_PART2_SYSTEM_PROMPT = """Vous etes expert colorimetre. Generez UNIQUEMENT JSON valide parfait.
Commencez par { et terminez par }.
REGLE CRITIQUE: Echappez TOUTES les apostrophes avec backslash (\\') - Exemple: s\\'harmonise
Aucun texte avant/apres JSON."""

COLORIMETRY_PART2_USER_PROMPT_TEMPLATE = """PALETTE PERSONNALISEE - Part 2.

CLIENT:
Saison: {SAISON} | Sous-ton: {SOUS_TON} | Yeux: {EYE_COLOR} | Cheveux: {HAIR_COLOR}

RETOURNEZ JSON VALIDE (PAS de doubles accolades):
{{
  "palette_personnalisee": [
    {{"name": "couleur1", "hex": "#HEX1", "note": 10, "commentaire": "10-15 mots specifiques client"}},
    {{"name": "couleur2", "hex": "#HEX2", "note": 10, "commentaire": "10-15 mots"}},
    {{"name": "couleur3", "hex": "#HEX3", "note": 9, "commentaire": "10-15 mots"}},
    {{"name": "couleur4", "hex": "#HEX4", "note": 9, "commentaire": "10-15 mots"}},
    {{"name": "couleur5", "hex": "#HEX5", "note": 9, "commentaire": "10-15 mots"}},
    {{"name": "couleur6", "hex": "#HEX6", "note": 9, "commentaire": "10-15 mots"}},
    {{"name": "couleur7", "hex": "#HEX7", "note": 8, "commentaire": "10-15 mots"}},
    {{"name": "couleur8", "hex": "#HEX8", "note": 8, "commentaire": "10-15 mots"}},
    {{"name": "couleur9", "hex": "#HEX9", "note": 8, "commentaire": "10-15 mots"}},
    {{"name": "couleur10", "hex": "#HEX10", "note": 8, "commentaire": "10-15 mots"}}
  ],

  "allColorsWithNotes": [
    {{"name": "jaune", "note": 9, "hex": "#FFFF00", "commentaire": "Dore amplifie or naturel"}},
    {{"name": "orange", "note": 9, "hex": "#FFA500", "commentaire": "Chaud amplifie vitalite"}},
    {{"name": "rouge", "note": 8, "hex": "#FF0000", "commentaire": "Chauds OK. Froids non"}},
    {{"name": "marron", "note": 9, "hex": "#8B4513", "commentaire": "Intensifie yeux"}},
    {{"name": "camel", "note": 10, "hex": "#C19A6B", "commentaire": "Essentiel harmonie"}},
    {{"name": "beige", "note": 8, "hex": "#F5F5DC", "commentaire": "Chaud flatte"}},
    {{"name": "kaki", "note": 8, "hex": "#C3B091", "commentaire": "Polyvalent"}},
    {{"name": "vert", "note": 8, "hex": "#008000", "commentaire": "Chauds OK"}},
    {{"name": "bordeaux", "note": 9, "hex": "#800020", "commentaire": "Chaud sophistique"}},
    {{"name": "rose_corail", "note": 9, "hex": "#FF7F50", "commentaire": "S\\'harmonise"}},
    {{"name": "gris", "note": 6, "hex": "#808080", "commentaire": "Taupe OK"}},
    {{"name": "blanc", "note": 5, "hex": "#FFFFFF", "commentaire": "Pur peut hurter"}},
    {{"name": "noir", "note": 4, "hex": "#000000", "commentaire": "Charbon meilleur"}},
    {{"name": "bleu", "note": 3, "hex": "#0000FF", "commentaire": "Froids isolent"}},
    {{"name": "violet", "note": 2, "hex": "#800080", "commentaire": "Froid ternit"}},
    {{"name": "rose_pale", "note": 2, "hex": "#FFB6C1", "commentaire": "Froid ternit"}},
    {{"name": "marine", "note": 3, "hex": "#000080", "commentaire": "Froid desharmonise"}},
    {{"name": "turquoise", "note": 1, "hex": "#40E0D0", "commentaire": "Froide incompatible"}},
    {{"name": "rose_fuchsia", "note": 1, "hex": "#FF20F0", "commentaire": "Extreme eviter"}}
  ],

  "associations_gagnantes": [
    {{
      "occasion": "professionnel",
      "colors": ["Couleur1", "Couleur2", "Couleur3"],
      "color_hex": ["#HEX1", "#HEX2", "#HEX3"],
      "effet": "Description courte",
      "description": "15-20 mots: convient reunions presentations autorite apaisement chaleur."
    }},
    {{
      "occasion": "casual",
      "colors": ["Couleur2", "Couleur3", "Couleur4"],
      "color_hex": ["#HEX2", "#HEX3", "#HEX4"],
      "effet": "Sans-effort naturel",
      "description": "15-20 mots: decontraction sorties cafe shopping loisirs energie legere."
    }},
    {{
      "occasion": "soiree",
      "colors": ["Couleur5", "Couleur6", "Couleur1"],
      "color_hex": ["#HEX5", "#HEX6", "#HEX1"],
      "effet": "Sophistication",
      "description": "15-20 mots: diner cocktail elegance nocturne richesse profondeur chaleur."
    }},
    {{
      "occasion": "weekend",
      "colors": ["Couleur3", "Couleur1", "Couleur7"],
      "color_hex": ["#HEX3", "#HEX1", "#HEX7"],
      "effet": "Naturel energique",
      "description": "15-20 mots: decontraction nature randonnee exploration stabilite authenticite."
    }},
    {{
      "occasion": "famille",
      "colors": ["Couleur4", "Couleur2", "Couleur5"],
      "color_hex": ["#HEX4", "#HEX2", "#HEX5"],
      "effet": "Chaleur accueillante",
      "description": "15-20 mots: moments importants bienveillance douceur solidite rayonnement elegance."
    }}
  ]
}}

REGLES STRICTES:
- palette_personnalisee = 10 COULEURS EXACTEMENT
- allColorsWithNotes = 19 couleurs FIXES (dont les noms ci-dessus)
- associations_gagnantes = 5 OCCASIONS avec description courte 15-20 mots max
- ECHAPPER APOSTROPHES: s\\'harmonise (backslash avant apostrophe)
- Pas d\\'accents speciaux: e accent → e normal
- JSON COMPLET VALIDE - terminer avec }
"""

# Fallback identique au precedent - ne pas changer!
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