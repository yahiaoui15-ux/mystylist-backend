"""
MORPHOLOGY PART 2 - MVP v6b
Changements vs v6 :
- Interdiction des couleurs dans les noms de pièces (sauf si pertinent morphologiquement)
- shopping_priorities : 5 pièces concrètes parmi les coupes recommandées, pas de banalités
"""

MORPHOLOGY_PART2_SYSTEM_PROMPT = """
Vous êtes un expert français en morphologie et stylisme haut de gamme.
Vous devez produire UNIQUEMENT un JSON strict valide, sans texte avant ou après.

RÈGLES JSON ABSOLUES:
- Guillemets doubles uniquement.
- Aucune virgule finale.
- Aucune valeur null.
- AUCUN saut de ligne dans les strings.
- Pas de Markdown, pas de HTML, pas d'emojis.
- Les accents et apostrophes sont AUTORISÉS.
"""

MORPHOLOGY_PART2_USER_PROMPT = """
Silhouette: {silhouette_type}
Objectifs styling: {styling_objectives}
À valoriser: {body_parts_to_highlight}
À minimiser: {body_parts_to_minimize}

══════════════════════════════════════════
RÈGLE ABSOLUE SUR LES NOMS DE PIÈCES
══════════════════════════════════════════
INTERDIT : inclure des couleurs dans les noms de pièces.
✗ "Top col en V noir", "Blouse fluide bleue", "Pantalon palazzo beige"
✓ "Top col en V", "Blouse fluide", "Pantalon palazzo"

EXCEPTION UNIQUE : si la couleur sombre ou claire a une pertinence directe
pour l'objectif morphologique (ex: "couleurs sombres sur le bas pour affiner"),
tu peux mentionner "sombre" ou "clair" UNIQUEMENT dans le champ "why", jamais dans "name".

══════════════════════════════════════════
RÈGLES OBLIGATOIRES PAR SILHOUETTE
══════════════════════════════════════════

SILHOUETTE A (poire — hanches > épaules):
- TOPS: encolure bateau, épaulettes, manches bouffantes, col rond large, bardot, froncé aux épaules
- TOPS INTERDITS: col en V, peplum, tops courts
- BAS À ÉVITER: slim, skinny, leggings, imprimés larges
- VESTES: structurées aux épaules, blazer à épaulettes
- ROBES: empire, portefeuille

SILHOUETTE V (épaules > hanches):
- TOPS: col en V, raglan, encolures larges, sans volume aux épaules
- BAS: évasés, palazzo
- VESTES: longues, cintrées à la taille

SILHOUETTE O (ronde, peu de taille):
- TOPS: col en V, encolure en U, matières fluides
- BAS: droits, palazzo
- VESTES: ceinturées, mi-longues structurées
- ROBES: empire, portefeuille, cache-cœur

SILHOUETTE H (rectangle):
- TOPS: peplum, volumineux, bouffants
- BAS: évasés, jupes froncées
- VESTES: avec ceinture, structurées à la taille

SILHOUETTE X (sablier):
- TOPS: wrap tops, cintrés, col en V
- BAS: évasés, jupes mi-longues
- VESTES: cintrées qui marquent la taille

══════════════════════════════════════════
RÈGLES FORMULES
══════════════════════════════════════════
- EXACTEMENT 4 pièces par formule. Ni 3, ni 5.
- Jamais robe + pantalon ensemble.
- Quotidien : haut + bas + accessoire + chaussure
- Travail : haut + bas + veste + chaussure
- Sortie : robe + accessoire + accessoire + chaussure
           OU haut + bas + veste + chaussure
- why_it_works: MINIMUM 3 phrases.

══════════════════════════════════════════
RÈGLES SHOPPING PRIORITIES — CRITIQUE ABSOLUE
══════════════════════════════════════════
INTERDICTION ABSOLUE de retourner shopping_priorities vide ou avec moins de 5 items.
Si ce champ est vide ou incomplet, la réponse sera REJETÉE et tu devras recommencer.

Les 5 priorités DOIVENT être des noms de coupe exacts tirés de tes essentials ci-dessus.
Copie littéralement les "name" depuis tes essentials : tops[0].name, bottoms[0].name,
dresses[0].name, jackets[0].name, tops[1].name (ou toute autre combinaison de 5 noms).

INTERDIT : tableau vide [], priorités génériques, phrases descriptives.
OBLIGATOIRE : exactement 5 strings, chacune = un "name" de tes essentials.

Exemple pour silhouette O :
"shopping_priorities": [
  "Top col en V",
  "Pantalon palazzo",
  "Robe portefeuille",
  "Blazer cintré",
  "Jupe droite taille haute"
]

══════════════════════════════════════════
CONTRAINTES
══════════════════════════════════════════
- tops : EXACTEMENT 4 items (hauts uniquement, sans couleur dans name)
- dresses : EXACTEMENT 2 items (robes ou combinaisons uniquement, sans couleur dans name)
- jackets : EXACTEMENT 3 items (vestes, blazers, manteaux uniquement, sans couleur dans name)
- bottoms : EXACTEMENT 3 items (pantalons, jupes, jeans uniquement, sans couleur dans name)
- shoes_accessories : EXACTEMENT 3 items
- avoid_by_category : pièces STRICTEMENT de leur catégorie
- style_notes : format "nom — explication courte"
- Strings max 130 caractères. Zéro texte hors JSON.

JSON ATTENDU:

{{
  "essentials": {{
    "tops": [
      {{"name": "", "why": ""}},
      {{"name": "", "why": ""}},
      {{"name": "", "why": ""}},
      {{"name": "", "why": ""}}
    ],
    "dresses": [
      {{"name": "", "why": ""}},
      {{"name": "", "why": ""}}
    ],
    "jackets": [
      {{"name": "", "why": ""}},
      {{"name": "", "why": ""}},
      {{"name": "", "why": ""}}
    ],
    "bottoms": [
      {{"name": "", "why": ""}},
      {{"name": "", "why": ""}},
      {{"name": "", "why": ""}}
    ],
    "shoes_accessories": [
      {{"name": "", "why": ""}},
      {{"name": "", "why": ""}},
      {{"name": "", "why": ""}}
    ]
  }},
  "avoid_by_category": {{
    "tops": [
      {{"name": "", "why": ""}},
      {{"name": "", "why": ""}}
    ],
    "bottoms": [
      {{"name": "", "why": ""}},
      {{"name": "", "why": ""}}
    ],
    "dresses": [
      {{"name": "", "why": ""}}
    ],
    "jackets": [
      {{"name": "", "why": ""}}
    ],
    "shoes": [
      {{"name": "", "why": ""}}
    ],
    "accessories": [
      {{"name": "", "why": ""}}
    ]
  }},
  "avoid": [
    {{"name": "", "why": ""}},
    {{"name": "", "why": ""}},
    {{"name": "", "why": ""}},
    {{"name": "", "why": ""}},
    {{"name": "", "why": ""}}
  ],
  "outfit_formulas": [
    {{
      "occasion": "Quotidien",
      "pieces": ["pièce 1", "pièce 2", "pièce 3", "pièce 4"],
      "why_it_works": "Phrase 1. Phrase 2. Phrase 3."
    }},
    {{
      "occasion": "Travail",
      "pieces": ["pièce 1", "pièce 2", "pièce 3", "pièce 4"],
      "why_it_works": "Phrase 1. Phrase 2. Phrase 3."
    }},
    {{
      "occasion": "Sortie",
      "pieces": ["pièce 1", "pièce 2", "pièce 3", "pièce 4"],
      "why_it_works": "Phrase 1. Phrase 2. Phrase 3."
    }}
  ],
  "shopping_priorities": [
    "coupe spécifique tirée des essentials",
    "coupe spécifique tirée des essentials",
    "coupe spécifique tirée des essentials",
    "coupe spécifique tirée des essentials",
    "coupe spécifique tirée des essentials"
  ],
  "style_notes": {{
    "matieres_recommandees": ["matière — raison", "matière — raison", "matière — raison"],
    "motifs_recommandes": ["motif — raison", "motif — raison", "motif — raison"],
    "matieres_eviter": ["matière — raison", "matière — raison"],
    "motifs_eviter": ["motif — raison", "motif — raison"]
  }}
}}

RAPPEL FINAL:
- AUCUNE couleur dans les champs "name" des essentials.
- shopping_priorities : 5 coupes précises issues de tes essentials, PAS de généralités.
- tops=4, dresses=2, jackets=3, bottoms=3. Chaque formule=4 pièces exactement.
- Zéro texte hors JSON.
"""