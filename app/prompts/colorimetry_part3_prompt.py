"""
COLORIMETRY PART 3 - Notes compatibilite + Unwanted colors + Maquillage + Vernis
Input: ~1200 tokens | Output: ~1400 tokens
v7.3 FIX: Separation objective (compatibility) vs subjective (personal preference)
"""

COLORIMETRY_PART3_SYSTEM_PROMPT = """Vous êtes expert colorimètre final. Générez UNIQUEMENT JSON valide parfait. Commencez par { et terminez par }. Aucun texte avant/après."""

COLORIMETRY_PART3_USER_PROMPT_TEMPLATE = """NOTES COMPATIBILITE + COULEURS REFUSEES + MAQUILLAGE - Part 3.

DONNEES CLIENT:
Saison: {SAISON}
Sous-ton: {SOUS_TON}
Unwanted colors: {UNWANTED_COLORS}

IMPORTANT: SEPAREZ BIEN:
- "note" = NOTE DE COMPATIBILITE COLORIMETRIQUE OBJECTIVE (basée saison/sous-ton uniquement)
- Si couleur refusée mais compatible = donnez la VRAIE note de compatibilité
- Ne pas pénaliser la note parce que le client refuse la couleur personnellement

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
      "displayName": "couleur_refusee_1",
      "note": 8,
      "commentaire": "ANALYSE OBJECTIVE: Cette couleur est compatible avec votre colorimétrie Automne/chaud (note 8/10). Vous avez choisi de ne pas la porter - c'est votre préférence personnelle et c'est valide. Alternatives: camel, moutarde, bronze."
    }},
    ...JUSQU'A 10 couleurs refusees si presentes
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

REGLES CRITIQUES:
✅ notes_compatibilite = 19 couleurs TOUTES présentes (identique Part 2)
✅ unwanted_colors = DYNAMIC basé input {UNWANTED_COLORS}
   - 1-10 couleurs refusées
   - Chaque couleur a "displayName", "note" (NOTE OBJECTIVE), "commentaire"
   - NOTE = Compatibilité colorimétrique REELLE basée saison/sous-ton
   - Ne PAS réduire la note juste parce que client refuse la couleur
   - Commentaire = Analyse objective + alternatives compatibles
✅ guide_maquillage = TOUTES les catégories (teint/blush/bronzer/eyeliner/mascara/brows/lips/etc.)
✅ nailColors = 4 VRAIES couleurs (Doré, Bronze, Cuivre, Bordeaux - PAS moutarde!)
   - name + hex correctes
✅ JSON valide complet
✅ Doubles accolades {{ }} pour imbrication
✅ ZERO texte avant/après
"""