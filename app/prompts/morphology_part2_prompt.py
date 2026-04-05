"""
MORPHOLOGY PART 2 - MVP v6.0
Changements vs v5b :
- essentials.tops : 4 items (au lieu de 6)
- essentials.dresses : 2 items robes/combinaisons (nouveau)
- essentials.jackets : 3 items vestes/blazers/manteaux (nouveau, remplace dresses_jackets)
- essentials.bottoms : 3 items (inchangé)
- essentials.shoes_accessories : 3 items (inchangé)
- avoid_by_category : ajoute "jackets" en plus de "dresses"
- outfit_formulas : EXACTEMENT 4 pièces
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
RÈGLES OBLIGATOIRES PAR SILHOUETTE
══════════════════════════════════════════

SILHOUETTE A (poire — hanches > épaules):
- TOPS: encolure bateau, épaulettes, manches bouffantes, col rond large, bardot, froncé aux épaules
- TOPS INTERDITS: col en V, peplum, tops courts
- BAS À ÉVITER: slim, skinny, leggings, imprimés larges
- VESTES: structurées aux épaules, blazer à épaulettes
- ROBES: empire, portefeuille, col en V interdit

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
RÈGLES FORMULES — CRITIQUE
══════════════════════════════════════════
- EXACTEMENT 4 pièces par formule. Ni 3, ni 5.
- Jamais robe + pantalon dans la même formule.
- Structure :
  Quotidien : haut + bas + accessoire + chaussure
  Travail : haut + bas + veste + chaussure
  Sortie : robe + accessoire + accessoire + chaussure
             OU haut + bas + veste + chaussure
- why_it_works: MINIMUM 3 phrases.

══════════════════════════════════════════
CONTRAINTES STRICTES
══════════════════════════════════════════
- tops : EXACTEMENT 4 items (hauts uniquement)
- dresses : EXACTEMENT 2 items (robes ou combinaisons uniquement)
- jackets : EXACTEMENT 3 items (vestes, blazers, manteaux uniquement)
- bottoms : EXACTEMENT 3 items (pantalons, jupes, jeans uniquement)
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
  "shopping_priorities": ["", "", "", "", ""],
  "style_notes": {{
    "matieres_recommandees": ["matière — raison", "matière — raison", "matière — raison"],
    "motifs_recommandes": ["motif — raison", "motif — raison", "motif — raison"],
    "matieres_eviter": ["matière — raison", "matière — raison"],
    "motifs_eviter": ["motif — raison", "motif — raison"]
  }}
}}

RAPPEL FINAL:
- tops: EXACTEMENT 4. dresses: EXACTEMENT 2. jackets: EXACTEMENT 3.
- dresses = robes/combi UNIQUEMENT. jackets = vestes/blazers UNIQUEMENT. tops = hauts UNIQUEMENT.
- Chaque outfit_formula: EXACTEMENT 4 pièces. Zéro texte hors JSON.
"""