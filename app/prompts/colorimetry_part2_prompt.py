"""
COLORIMETRY PART 2 - STRICT JSON VALIDATION (FIXED)
Input: ~1200 tokens | Output: ~1600 tokens
FIX: Pas de .format() sur le prompt - utiliser f-strings dans colorimetry.py
"""

COLORIMETRY_PART2_SYSTEM_PROMPT = """Vous êtes expert colorimètre. Générez UNIQUEMENT du JSON VALIDE parfait. Commencez par { et terminez par }. Aucun texte avant/après. Si vous n'êtes pas sûr, retournez {} plutôt que JSON cassé."""

# ⚠️ IMPORTANT: Ce template NE utilise PAS .format()
# On le complète avec f-string dans colorimetry.py
COLORIMETRY_PART2_USER_PROMPT_TEMPLATE = """STRICTEMENT JSON VALIDE - Part 2 colorimétrie avancée.

CLIENT:
Saison: {SAISON}
Sous-ton: {SOUS_TON}
Top couleurs: {PALETTE_NAMES}

RETOURNEZ EXACTEMENT (pas d'erreur d'échappement):
{{
  "notes_compatibilite": {{
    "rouge": {{"note": 8, "commentaire": "Rouges chauds harmonisent. Froids ternissent."}},
    "bleu": {{"note": 3, "commentaire": "Blus froids isolent. À éviter absolument."}},
    "jaune": {{"note": 9, "commentaire": "Jaunes dorés amplifient or naturel."}},
    "vert": {{"note": 8, "commentaire": "Verts chauds harmonisent. Acides froids non."}},
    "orange": {{"note": 9, "commentaire": "Orange chaud amplifie vitalité."}},
    "violet": {{"note": 2, "commentaire": "Violets froids ternissent présence."}},
    "blanc": {{"note": 5, "commentaire": "Blanc pur crée micro-contraste heurté."}},
    "noir": {{"note": 4, "commentaire": "Noir pur dur. Charbon plus flatteur."}},
    "gris": {{"note": 6, "commentaire": "Gris taupe OK. Gris froid non."}},
    "beige": {{"note": 8, "commentaire": "Beiges chauds flattent carnation."}},
    "marron": {{"note": 9, "commentaire": "Marrons chauds intensifient yeux."}},
    "rose_pale": {{"note": 2, "commentaire": "Rose pâle froid ternit teint chaud."}},
    "rose_fuchsia": {{"note": 1, "commentaire": "Fuchsia froid crée dissonance extrême."}},
    "rose_corail": {{"note": 9, "commentaire": "Rose corail chaud s'harmonise magnifiquement."}},
    "camel": {{"note": 10, "commentaire": "Camel essentiel. Reproduit harmonie naturelle."}},
    "marine": {{"note": 3, "commentaire": "Marine froid crée contraste désharmonisé."}},
    "bordeaux": {{"note": 9, "commentaire": "Bordeaux chaud sophistiqué s'harmonise parfait."}},
    "kaki": {{"note": 8, "commentaire": "Kaki chaud complète sous-ton créant harmonie."}},
    "turquoise": {{"note": 1, "commentaire": "Turquoise froide incompatible total."}}
  }},

  "allColorsWithNotes": [
    {{"name": "jaune", "note": 9, "hex": "#FFFF00", "commentaire": "Jaunes dorés amplifient or. Pâles citrons non."}},
    {{"name": "rouge", "note": 8, "hex": "#FF0000", "commentaire": "Rouges chauds magnifient. Froids isolent."}},
    {{"name": "vert", "note": 8, "hex": "#008000", "commentaire": "Verts chauds harmonisent naturel."}},
    {{"name": "bleu", "note": 3, "hex": "#0000FF", "commentaire": "Blus froids ternissent carnation."}}
  ],

  "associations_gagnantes": [
    {{
      "occasion": "professionnel",
      "colors": ["#C19A6B", "#E2725B", "#8B4513"],
      "effet": "Elegance confidente"
    }},
    {{
      "occasion": "casual",
      "colors": ["#C3B091", "#CC7722", "#D2B48C"],
      "effet": "Naturel sans-effort"
    }},
    {{
      "occasion": "soiree",
      "colors": ["#6D071A", "#8B8589", "#E2725B"],
      "effet": "Sophistication chaleureuse"
    }},
    {{
      "occasion": "weekend",
      "colors": ["#228B22", "#E1AD01", "#B87333"],
      "effet": "Détente avec caractère"
    }},
    {{
      "occasion": "famille",
      "colors": ["#7B3F00", "#E2725B", "#C3B091"],
      "effet": "Douceur naturelle"
    }}
  ],

  "guide_maquillage": {{
    "teint": "Doré riche (pas pâle)",
    "blush": "Pêche corail chaud",
    "bronzer": "Bronze chaud",
    "highlighter": "Or",
    "yeux": "Cuivre/bronze/terre",
    "eyeliner": "Marron chaud",
    "mascara": "Noir",
    "brows": "Brun chaud naturel",
    "lipsNude": "Beige chaud doré",
    "lipsDay": "Rose corail CHAUD",
    "lipsEvening": "Bordeaux riche",
    "lipsAvoid": "Rose pâle froid",
    "vernis_a_ongles": ["#E1AD01", "#7B3F00", "#CC7722", "#6D071A"]
  }},

  "shopping_couleurs": {{
    "priorite_1": ["Moutarde", "Camel", "Bordeaux"],
    "priorite_2": ["Cuivre", "Terracotta", "Bronze"],
    "eviter_absolument": ["Rose pâle froid", "Bleu marine froid", "Violet", "Turquoise"]
  }},

  "alternatives_couleurs_refusees": {{}}
}}

RÈGLES:
- Commencer par ouverture accolade simple {{
- JSON imbriqué utilise doubles accolades {{}}
- Fermer par accolade simple }}
- Les notes sont NOMBRES: 8 (pas "8")
- Zéro texte avant/après JSON
"""