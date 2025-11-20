"""
COLORIMETRY PART 3 - Notes compatibilité + Unwanted colors + Maquillage + Vernis
Input: ~1200 tokens | Output: ~1400 tokens
"""

COLORIMETRY_PART3_SYSTEM_PROMPT = """Vous êtes expert colorimètre final. Générez UNIQUEMENT JSON valide parfait. Commencez par { et terminez par }. Aucun texte avant/après."""

COLORIMETRY_PART3_USER_PROMPT_TEMPLATE = """NOTES COMPATIBILITÉ + COULEURS REFUSÉES + MAQUILLAGE - Part 3.

DONNÉES CLIENT:
Saison: {SAISON}
Sous-ton: {SOUS_TON}
Unwanted colors: {UNWANTED_COLORS}

RETOURNEZ JSON VALIDE (doubles accolades {{ }} pour imbrication):
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

  "unwanted_colors": [
    {{
      "name": "couleur_refusee_1",
      "note": 2,
      "commentaire": "40 mots: Pourquoi client a raison/tort + comment remplacer. Ex: 'Vous avez raison: rose pâle froid contredit sous-ton chaud. Essayer rose_corail à la place: même warmth mais avec intensité. Ou beige chaud pour polyvalence.'"
    }},
    ...JUSQU'À 10 couleurs refusées si présentes
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
    {{"name": "Doré", "hex": "#E1AD01"}},
    {{"name": "Bronze", "hex": "#CD7F32"}},
    {{"name": "Cuivre", "hex": "#B87333"}},
    {{"name": "Bordeaux", "hex": "#6D071A"}}
  ]
}}

RÈGLES CRITIQUES:
✅ notes_compatibilite = 19 couleurs TOUTES présentes (identique Part 2)
✅ unwanted_colors = DYNAMIC basé input {UNWANTED_COLORS}
   - 1-10 couleurs refusées
   - Chaque couleur a note (2-4 généralement) + commentaire 40 mots
   - Commentaire = Validation IA (raison/tort) + Alternative recommandée
✅ guide_maquillage = TOUTES les catégories (teint/blush/bronzer/eyeliner/mascara/brows/lips/etc.)
✅ nailColors = 4 VRAIES couleurs (Doré, Bronze, Cuivre, Bordeaux - PAS moutarde!)
   - name + hex correctes
✅ JSON valide complet
✅ Doubles accolades {{ }} pour imbrication
✅ ZÉRO texte avant/après
"""