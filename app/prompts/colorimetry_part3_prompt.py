"""
COLORIMETRY PART 3 FIXED v7.5 - Notes + Unwanted + Makeup + NAIL COLORS
✅ nailColors OBLIGATOIRE (4 couleurs)
✅ Colorimetry UNIQUEMENT (pas archétypes - c'est du styling)
✅ Réduit le size pour éviter truncation
"""

COLORIMETRY_PART3_SYSTEM_PROMPT = """Expert colorimétre final. Générez JSON complet + nailColors.
Commencez par { et finissez par }. Zéro texte avant/après."""

COLORIMETRY_PART3_USER_PROMPT_TEMPLATE = """PART 3: Notes compatibilité + Unwanted + Makeup + NAILS

DONNÉES CLIENT:
Saison: {SAISON}
Sous-ton: {SOUS_TON}
Unwanted: {UNWANTED_COLORS}

TÂCHE CRITIQUE:
1. notes_compatibilite = 19 couleurs avec scores objectifs
2. unwanted_colors = couleurs refusées avec analyse
3. guide_maquillage = Complet
4. ⭐ nailColors = 4 couleurs OBLIGATOIRES (displayName + hex)

JSON REQUIS:
{{
  "notes_compatibilite": {{
    "rouge": {{"note": 8, "commentaire": "Rouges chauds harmonisent. Froids ternissent."}},
    "bleu": {{"note": 3, "commentaire": "Bleus froids isolent. À éviter absolument."}},
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
    "rose_corail": {{"note": 9, "commentaire": "Rose corail chaud s harmonise magnifiquement."}},
    "camel": {{"note": 10, "commentaire": "Camel essentiel. Reproduit harmonie naturelle."}},
    "marine": {{"note": 3, "commentaire": "Marine froid crée contraste désharmonisé."}},
    "bordeaux": {{"note": 9, "commentaire": "Bordeaux chaud sophistiqué s harmonise parfait."}},
    "kaki": {{"note": 8, "commentaire": "Kaki chaud complète sous-ton créant harmonie."}},
    "turquoise": {{"note": 1, "commentaire": "Turquoise froide incompatible total."}}
  }},

  "unwanted_colors": [
    {{
      "displayName": "couleur_refusee",
      "note": 8,
      "commentaire": "ANALYSE: Compatible colorimétrie (note réelle). Préférence personnelle valide. Alternatives: couleur1, couleur2."
    }}
  ],

  "guide_maquillage": {{
    "teint": "Doré riche (pas pâle)",
    "blush": "Pêche corail chaud",
    "bronzer": "Bronze chaud",
    "highlighter": "Or",
    "eyeshadows": "Cuivre/bronze/terre",
    "eyeliner": "Marron chaud",
    "mascara": "Noir",
    "brows": "Brun chaud naturel",
    "lipsNatural": "Beige chaud doré",
    "lipsDay": "Rose corail CHAUD",
    "lipsEvening": "Bordeaux riche",
    "lipsAvoid": "Rose pâle froid"
  }},

  "nailColors": [
    {{"displayName": "Doré", "hex": "#E1AD01"}},
    {{"displayName": "Bronze", "hex": "#CD7F32"}},
    {{"displayName": "Cuivre", "hex": "#B87333"}},
    {{"displayName": "Bordeaux", "hex": "#6D071A"}}
  ]
}}

RÈGLES CRITIQUES:
✅ notes_compatibilite = 19 couleurs EXACTEMENT
✅ unwanted_colors = Dynamic (1-10 couleurs présentes)
✅ guide_maquillage = TOUS les champs
✅ nailColors = 4 couleurs OBLIGATOIRES (JAMAIS vide)
✅ JSON valide complet
✅ Zéro texte avant/après

Répondez UNIQUEMENT le JSON.
"""