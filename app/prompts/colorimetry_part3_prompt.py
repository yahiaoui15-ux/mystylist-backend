"""
COLORIMETRY PART 3 - ULTRA-STRICT v8.1 - FIXED
✅ nailColors EN PREMIER (section prioritaire)
✅ System prompt FORÇANT réponse JSON SEULE
✅ Format strict: ABSOLUMENT ZÉRO texte avant/après
✅ Blocs ```json si nécessaire (pour robustesse)
✅ ACCOLADES ÉCHAPPÉES pour .format()
"""

COLORIMETRY_PART3_SYSTEM_PROMPT = """RÈGLE ABSOLUE - RÉPONDEZ UNIQUEMENT AVEC LE JSON:
- ❌ Pas de "Voici...", "Reconnaissant...", ou explications
- ❌ Pas de texte avant le JSON
- ❌ Pas de texte après le JSON
- ❌ Pas de bloc ```json - juste le JSON brut
- ✅ Commencez par { (le tout premier caractère)
- ✅ Terminez par } (le tout dernier caractère)
- ✅ RIEN D'AUTRE

Si vous ne pouvez pas générer du JSON valide, retournez un JSON minimal: {}
Ne générez JAMAIS d'explications, de phrases, ou de texte quelconque."""

# 🔧 FIX: Les accolades { et } sont échappées en {{ }} pour éviter le KeyError
# lors de l'appel .format(SAISON=..., SOUS_TON=..., UNWANTED_COLORS=...)
COLORIMETRY_PART3_USER_PROMPT_TEMPLATE = """PART 3: MAQUILLAGE PERSONNALISÉ + NOTES COMPATIBILITÉ

DONNÉES CLIENT:
Saison: {SAISON}
Sous-ton: {SOUS_TON}
Couleurs refusées: {UNWANTED_COLORS}

========================================================================
⭐ SECTION PRIORITAIRE: ONGLES (nailColors)
========================================================================
TÂCHE CRITIQUE ABSOLUE:
Générer EXACTEMENT 4 couleurs de vernis à ongles harmonisant avec la saison {SAISON}.
RÈGLE STRICTE: Les 4 noms DOIVENT être DIFFÉRENTS (JAMAIS 2 fois le même nom!)
- Couleur 1: Nom unique + hex
- Couleur 2: Nom DIFFÉRENT + hex différent
- Couleur 3: Nom DIFFÉRENT + hex différent
- Couleur 4: Nom DIFFÉRENT + hex différent

EXEMPLE STRUCTURE (adapter les couleurs à {SAISON}):
[
  {{"displayName": "Sienna Brûlée", "hex": "#A0522D"}},
  {{"displayName": "Cannelle Épicée", "hex": "#D2691E"}},
  {{"displayName": "Oranger Rouille", "hex": "#FF4500"}},
  {{"displayName": "Prune Automnale", "hex": "#6D3C1B"}}
]

⚠️ IMPÉRATIF: Chaque displayName UNIQUE! Pas de doublons!

========================================================================
SECTION 2: NOTES COMPATIBILITÉ (19 couleurs EXACTEMENT)
========================================================================
Notation colorimétrique objective basée saison/sous-ton UNIQUEMENT.

Couleurs à évaluer (dans cet ordre):
1. rouge, 2. bleu, 3. jaune, 4. vert, 5. orange, 6. violet, 7. blanc, 8. noir,
9. gris, 10. beige, 11. marron, 12. rose_pale, 13. rose_fuchsia, 14. rose_corail,
15. camel, 16. marine, 17. bordeaux, 18. kaki, 19. turquoise

Exemple de format:
"rouge": {{"note": 8, "commentaire": "Rouges chauds harmonisent. Froids ternissent."}},

========================================================================
SECTION 3: COULEURS REFUSÉES (DYNAMIC - SI PRÉSENTES)
========================================================================
Si couleurs refusées ({UNWANTED_COLORS}):
- Analyser OBJECTIVEMENT chaque couleur
- Donner la note RÉELLE de compatibilité (pas de pénalité pour rejet)
- Proposer alternatives

Sinon: array vide []

========================================================================
SECTION 4: GUIDE MAQUILLAGE (12 champs TOUS REQUIS)
========================================================================
teint, blush, bronzer, highlighter, eyeshadows, eyeliner, mascara, brows,
lipsNatural, lipsDay, lipsEvening, lipsAvoid

========================================================================
JSON REQUIS - STRUCTURE EXACTE:
========================================================================
{{
  "nailColors": [
    {{"displayName": "Couleur1", "hex": "#XXXXXX"}},
    {{"displayName": "Couleur2", "hex": "#XXXXXX"}},
    {{"displayName": "Couleur3", "hex": "#XXXXXX"}},
    {{"displayName": "Couleur4", "hex": "#XXXXXX"}}
  ],
  "notes_compatibilite": {{
    "rouge": {{"note": X, "commentaire": "..."}},
    "bleu": {{"note": X, "commentaire": "..."}},
    "jaune": {{"note": X, "commentaire": "..."}},
    "vert": {{"note": X, "commentaire": "..."}},
    "orange": {{"note": X, "commentaire": "..."}},
    "violet": {{"note": X, "commentaire": "..."}},
    "blanc": {{"note": X, "commentaire": "..."}},
    "noir": {{"note": X, "commentaire": "..."}},
    "gris": {{"note": X, "commentaire": "..."}},
    "beige": {{"note": X, "commentaire": "..."}},
    "marron": {{"note": X, "commentaire": "..."}},
    "rose_pale": {{"note": X, "commentaire": "..."}},
    "rose_fuchsia": {{"note": X, "commentaire": "..."}},
    "rose_corail": {{"note": X, "commentaire": "..."}},
    "camel": {{"note": X, "commentaire": "..."}},
    "marine": {{"note": X, "commentaire": "..."}},
    "bordeaux": {{"note": X, "commentaire": "..."}},
    "kaki": {{"note": X, "commentaire": "..."}},
    "turquoise": {{"note": X, "commentaire": "..."}}
  }},
  "unwanted_colors": [
    {{
      "displayName": "...",
      "note": X,
      "commentaire": "..."
    }}
  ],
  "guide_maquillage": {{
    "teint": "...",
    "blush": "...",
    "bronzer": "...",
    "highlighter": "...",
    "eyeshadows": "...",
    "eyeliner": "...",
    "mascara": "...",
    "brows": "...",
    "lipsNatural": "...",
    "lipsDay": "...",
    "lipsEvening": "...",
    "lipsAvoid": "..."
  }}
}}

========================================================================
RÈGLES STRICTES ET OBLIGATOIRES:
========================================================================
✅ nailColors = TOUJOURS 4 couleurs (JAMAIS vide, JAMAIS moins de 4, JAMAIS plus de 4)
   - Générer des vraies couleurs (pas d'exemples)
   - displayName en français uniquement
   - hex codes corrects (#RRGGBB format)

✅ notes_compatibilite = 19 couleurs EXACTEMENT (pas plus, pas moins)
   - note = entier 1-10
   - commentaire = analyse colorimétrique objective

✅ unwanted_colors = DYNAMIC (0-10 couleurs selon input)
   - Si aucune refusée: array vide []
   - Si présentes: analyse objective RÉELLE

✅ guide_maquillage = 12 champs TOUS présents (pas d'omissions)

✅ JSON VALIDE COMPLET
✅ Doubles accolades {{ }} pour imbrication dans le template
✅ ZÉRO TEXTE avant le JSON
✅ ZÉRO TEXTE après le JSON
✅ ZÉRO EXPLICATIONS

IMPÉRATIF ULTIME: 
Votre PREMIÈRE réponse doit être {{ et votre DERNIÈRE doit être }}
Aucun mot, aucune explication, rien d'autre.
"""