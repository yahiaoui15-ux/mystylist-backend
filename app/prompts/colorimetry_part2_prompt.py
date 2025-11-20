"""
COLORIMETRY PART 2 - Palette personnalisée + Couleurs génériques + Associations
Input: ~1100 tokens | Output: ~1400 tokens
"""

COLORIMETRY_PART2_SYSTEM_PROMPT = """Vous êtes expert colorimètre. Générez UNIQUEMENT JSON valide. Commencez par { et terminez par }. Aucun texte avant/après."""

COLORIMETRY_PART2_USER_PROMPT_TEMPLATE = """PALETTE PERSONNALISÉE - Part 2 colorimétrie.

DONNÉES CLIENT:
Saison: {SAISON}
Sous-ton: {SOUS_TON}
Yeux: {EYE_COLOR}
Cheveux: {HAIR_COLOR}

RETOURNEZ JSON VALIDE (doubles accolades {{ }} pour imbrication):
{{
  "palette_personnalisee": [
    {{
      "name": "couleur1",
      "hex": "#HEX1",
      "note": 10,
      "commentaire": "15-20 mots: Effet visuel + pourquoi fonctionne. Ex: 'Illumine carnation dorée. Renforce yeux marron. Parfait près visage.'"
    }},
    {{
      "name": "couleur2",
      "hex": "#HEX2",
      "note": 10,
      "commentaire": "15-20 mots"
    }},
    ...12 COULEURS TOTAL (jamais moins!)
  ],

  "allColorsWithNotes": [
    {{"name": "jaune", "note": 9, "hex": "#FFFF00", "commentaire": "Jaunes dorés amplifient or naturel du teint."}},
    {{"name": "rouge", "note": 8, "hex": "#FF0000", "commentaire": "Rouges chauds harmonisent. Froids ternissent."}},
    {{"name": "vert", "note": 8, "hex": "#008000", "commentaire": "Verts chauds harmonisent naturellement."}},
    {{"name": "bleu", "note": 3, "hex": "#0000FF", "commentaire": "Bleus froids isolent. À éviter absolument."}},
    {{"name": "orange", "note": 9, "hex": "#FFA500", "commentaire": "Orange chaud amplifie vitalité et éclat."}},
    {{"name": "violet", "note": 2, "hex": "#800080", "commentaire": "Violets froids ternissent présence naturelle."}},
    {{"name": "blanc", "note": 5, "hex": "#FFFFFF", "commentaire": "Blanc pur crée micro-contraste heurté."}},
    {{"name": "noir", "note": 4, "hex": "#000000", "commentaire": "Noir pur dur. Charbon plus flatteur."}},
    {{"name": "gris", "note": 6, "hex": "#808080", "commentaire": "Gris taupe OK. Gris froid non."}},
    {{"name": "beige", "note": 8, "hex": "#F5F5DC", "commentaire": "Beiges chauds flattent carnation dorée."}},
    {{"name": "marron", "note": 9, "hex": "#8B4513", "commentaire": "Marrons chauds intensifient yeux."}},
    {{"name": "rose_pale", "note": 2, "hex": "#FFB6C1", "commentaire": "Rose pâle froid ternit teint chaud."}},
    {{"name": "rose_fuchsia", "note": 1, "hex": "#FF20F0", "commentaire": "Fuchsia froid crée dissonance extrême."}},
    {{"name": "rose_corail", "note": 9, "hex": "#FF7F50", "commentaire": "Rose corail chaud s'harmonise magnifiquement."}},
    {{"name": "camel", "note": 10, "hex": "#C3B091", "commentaire": "Camel essentiel. Reproduit harmonie naturelle."}},
    {{"name": "marine", "note": 3, "hex": "#000080", "commentaire": "Marine froid crée contraste désharmonisé."}},
    {{"name": "bordeaux", "note": 9, "hex": "#800020", "commentaire": "Bordeaux chaud sophistiqué s'harmonise parfait."}},
    {{"name": "kaki", "note": 8, "hex": "#9B8B56", "commentaire": "Kaki chaud complète sous-ton créant harmonie."}},
    {{"name": "turquoise", "note": 1, "hex": "#40E0D0", "commentaire": "Turquoise froide incompatible total."}}
  ],

  "associations_gagnantes": [
    {{
      "occasion": "professionnel",
      "colors": ["Terracotta", "Marron", "Camel"],
      "color_hex": ["#E2725B", "#8B4513", "#C3B091"],
      "effet": "Elegance confidente"
    }},
    {{
      "occasion": "casual",
      "colors": ["Kaki", "Ocre Jaune", "Camel"],
      "color_hex": ["#C3B091", "#CC7722", "#D2B48C"],
      "effet": "Naturel sans-effort"
    }},
    {{
      "occasion": "soirée",
      "colors": ["Bordeaux", "Gris Taupe", "Terracotta"],
      "color_hex": ["#6D071A", "#8B8589", "#E2725B"],
      "effet": "Sophistication chaleureuse",
      "description": "Harmonie riche et profonde qui respire l'élégance nocturne. Bordeaux apporte profondeur, gris taupe crée équilibre, terracotta ajoute chaleur. Parfait pour dîners, cocktails, événements où vous souhaitez briller discrètement avec raffinement."
    }},
    {{
      "occasion": "weekend",
      "colors": ["Moutarde", "Cuivre", "Olive"],
      "color_hex": ["#E1AD01", "#B87333", "#6B8E23"],
      "effet": "Détente avec caractère"
    }},
    {{
      "occasion": "famille",
      "colors": ["Chocolat", "Terracotta", "Kaki"],
      "color_hex": ["#7B3F00", "#E2725B", "#C3B091"],
      "effet": "Douceur naturelle"
    }}
  ]
}}

RÈGLES:
✅ palette_personnalisee = 12 couleurs MINIMUM
✅ Chaque couleur a name + hex + note + commentaire (15-20 mots)
✅ allColorsWithNotes = 19 couleurs génériques (déjà présentes)
✅ associations_gagnantes: 5 occasions, chaque occasion a "description" de 40-50 mots pour SOIRÉE
✅ JSON valide complet
✅ Doubles accolades {{ }} pour imbrication
✅ ZÉRO texte avant/après
"""