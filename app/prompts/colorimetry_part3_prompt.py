"""
COLORIMETRY PART 3 - RESTRUCTURÉ v8.0
✅ nailColors EN PREMIER (pas en dernier)
✅ SECTION SÉPARÉE pour nailColors avec instruction EXPLICITE
✅ Pas d'ambiguïté: 4 couleurs OBLIGATOIRES
"""

COLORIMETRY_PART3_SYSTEM_PROMPT = """Vous êtes expert colorimètre final. Générez UNIQUEMENT JSON valide. Commencez par { et terminez par }. Aucun texte avant/après."""

COLORIMETRY_PART3_USER_PROMPT_TEMPLATE = """PART 3: MAQUILLAGE PERSONNALISÉ + NOTES COMPATIBILITÉ

DONNÉES CLIENT:
Saison: {SAISON}
Sous-ton: {SOUS_TON}
Couleurs refusées: {UNWANTED_COLORS}

========================================================================
⭐ SECTION PRIORITAIRE: ONGLES (nailColors)
========================================================================
TÂCHE CRITIQUE:
Générer EXACTEMENT 4 couleurs de vernis à ongles harmonisant avec la saison {SAISON}.
- Chaque couleur: "displayName" (nom français) + "hex" (code couleur #RRGGBB)
- Les 4 couleurs DOIVENT être présentes (JAMAIS vide)
- Exemple: "Doré" (warm gold), "Bronze" (warm bronze), "Cuivre" (warm copper), "Bordeaux" (warm burgundy)

EXEMPLE NAILCOLORS (pour {SAISON}):
[
  {{"displayName": "Doré", "hex": "#E1AD01"}},
  {{"displayName": "Bronze", "hex": "#CD7F32"}},
  {{"displayName": "Cuivre", "hex": "#B87333"}},
  {{"displayName": "Bordeaux", "hex": "#6D071A"}}
]

========================================================================
SECTION 2: NOTES COMPATIBILITÉ (19 couleurs)
========================================================================
Notation colorimétrique objective basée saison/sous-ton UNIQUEMENT.

Exemple:
- "rouge": {{"note": 8, "commentaire": "Rouges chauds harmonisent. Froids ternissent."}},
- "bleu": {{"note": 3, "commentaire": "Bleus froids isolent. À éviter absolument."}},

(... et 17 autres couleurs: jaune, vert, orange, violet, blanc, noir, gris, beige, marron, rose_pale, rose_fuchsia, rose_corail, camel, marine, bordeaux, kaki, turquoise)

========================================================================
SECTION 3: COULEURS REFUSÉES
========================================================================
Analyse objective de chaque couleur refusée par le client.
- "displayName": Nom de la couleur
- "note": Compatibilité RÉELLE (selon saison/sous-ton uniquement - pas de pénalité pour rejet)
- "commentaire": Analyse + alternatives

Exemple:
  {{
    "displayName": "Rose pâle",
    "note": 6,
    "commentaire": "Compatible avec teint chaud (note 6/10). Vous préférez ne pas la porter - c'est votre choix personnel valide. Alternatives: rose corail, pêche, beige doré."
  }}

========================================================================
SECTION 4: GUIDE MAQUILLAGE COMPLET
========================================================================
12 champs obligatoires:
- teint, blush, bronzer, highlighter
- eyeshadows, eyeliner, mascara, brows
- lipsNatural, lipsDay, lipsEvening, lipsAvoid

========================================================================
JSON REQUIS (COMPLET):
========================================================================
{{
  "nailColors": [
    {{"displayName": "Couleur 1", "hex": "#RRGGBB"}},
    {{"displayName": "Couleur 2", "hex": "#RRGGBB"}},
    {{"displayName": "Couleur 3", "hex": "#RRGGBB"}},
    {{"displayName": "Couleur 4", "hex": "#RRGGBB"}}
  ],

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
    "rose_corail": {{"note": 9, "commentaire": "Rose corail chaud harmonise magnifiquement."}},
    "camel": {{"note": 10, "commentaire": "Camel essentiel. Reproduit harmonie naturelle."}},
    "marine": {{"note": 3, "commentaire": "Marine froid crée contraste désharmonisé."}},
    "bordeaux": {{"note": 9, "commentaire": "Bordeaux chaud s harmonise parfait."}},
    "kaki": {{"note": 8, "commentaire": "Kaki chaud complète sous-ton créant harmonie."}},
    "turquoise": {{"note": 1, "commentaire": "Turquoise froide incompatible total."}}
  }},

  "unwanted_colors": [
    {{
      "displayName": "couleur_refusee",
      "note": 8,
      "commentaire": "ANALYSE: Compatible colorimétrie (note réelle 8/10). Préférence personnelle valide. Alternatives: couleur1, couleur2."
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
  }}
}}

========================================================================
REGLES CRITIQUES:
========================================================================
✅ nailColors = TOUJOURS 4 couleurs (JAMAIS vide - JAMAIS moins de 4)
   - displayName en français
   - hex codes corrects (#RRGGBB)
   - Couleurs harmonisant avec {SAISON}

✅ notes_compatibilite = 19 couleurs EXACTEMENT
   - note = entier 1-10
   - commentaire = analyse colorimétrique objective

✅ unwanted_colors = DYNAMIC (0-10 couleurs)
   - Si aucune refusée: array vide []
   - Si présentes: analyse objective + alternatives

✅ guide_maquillage = 12 champs TOUS présents

✅ JSON valide complet
✅ Doubles accolades {{ }} pour imbrication
✅ ZERO texte avant/après

PRIORITÉ ABSOLUE: nailColors DOIT contenir 4 couleurs, PAS un array vide!
"""