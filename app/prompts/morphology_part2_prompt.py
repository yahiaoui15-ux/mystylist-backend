"""
MORPHOLOGY PART 2 - MVP v5.0
Changements v5 vs v4:
- avoid_by_category: shoes et accessories SÉPARÉS (plus shoes_accessories ensemble)
- tops: toujours 6 items
- style_notes: format "matière — raison courte"
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
- Les accents et apostrophes sont AUTORISÉS et attendus.
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
- TOPS: encolure bateau, épaulettes, manches bouffantes, col rond large, bardot, froncé aux épaules, rayures horizontales sur le haut
- TOPS INTERDITS: col en V, peplum, tops courts
- BAS À ÉVITER: slim, skinny, leggings, imprimés larges sur le bas
- CHAUSSURES À ÉVITER: chaussures très plates qui coupent la jambe
- ACCESSOIRES À ÉVITER: ceintures trop larges qui élargissent les hanches

SILHOUETTE V (épaules > hanches):
- TOPS: col en V, raglan, encolures larges, sans volume aux épaules
- BAS: évasés, palazzo
- CHAUSSURES À ÉVITER: platforms très massives qui élargissent la base
- ACCESSOIRES À ÉVITER: sacs portés haut sur l'épaule qui accentuent la largeur

SILHOUETTE O (ronde, peu de taille):
- TOPS: col en V, encolure en U, matières fluides
- BAS: droits, palazzo
- CHAUSSURES À ÉVITER: ballerines très plates qui n'allongent pas
- ACCESSOIRES À ÉVITER: ceintures épaisses qui coupent la silhouette

SILHOUETTE H (rectangle):
- TOPS: peplum, volumineux, bouffants
- BAS: évasés, jupes froncées
- CHAUSSURES À ÉVITER: bottes larges au genou qui effacent les courbes
- ACCESSOIRES À ÉVITER: ceintures trop fines qui n'ont pas d'impact

SILHOUETTE X (sablier):
- TOPS: wrap tops, cintrés, col en V
- BAS: évasés, jupes mi-longues
- CHAUSSURES À ÉVITER: chaussures massives qui alourdissent la silhouette
- ACCESSOIRES À ÉVITER: grosses ceintures qui cachent la taille naturelle

══════════════════════════════════════════
RÈGLES COHÉRENCE FORMULES
══════════════════════════════════════════
- 4 pièces = 1 seule tenue portée ensemble.
- Jamais robe + pantalon ensemble.
- why_it_works: MINIMUM 3 phrases.

══════════════════════════════════════════
CONTRAINTES
══════════════════════════════════════════
- tops: EXACTEMENT 6 items.
- bottoms, dresses_jackets, shoes_accessories: 3 items chacun.
- avoid_by_category: pièces STRICTEMENT de leur catégorie
  (tops = hauts seulement, bottoms = bas seulement, shoes = chaussures seulement, accessories = accessoires seulement)
- avoid: 5 items globaux toutes catégories confondues.
- style_notes: format "nom — explication courte" avec tiret.
- Strings max 130 caractères. Zéro texte hors JSON.

JSON ATTENDU:

{{
  "essentials": {{
    "tops": [
      {{"name": "", "why": ""}},
      {{"name": "", "why": ""}},
      {{"name": "", "why": ""}},
      {{"name": "", "why": ""}},
      {{"name": "", "why": ""}},
      {{"name": "", "why": ""}}
    ],
    "bottoms": [
      {{"name": "", "why": ""}},
      {{"name": "", "why": ""}},
      {{"name": "", "why": ""}}
    ],
    "dresses_jackets": [
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
    "dresses_jackets": [
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
      "pieces": ["pièce haut", "pièce bas", "accessoire", "chaussure"],
      "why_it_works": "Phrase 1. Phrase 2. Phrase 3."
    }},
    {{
      "occasion": "Travail",
      "pieces": ["pièce haut", "pièce bas", "veste", "chaussure"],
      "why_it_works": "Phrase 1. Phrase 2. Phrase 3."
    }},
    {{
      "occasion": "Sortie",
      "pieces": ["robe OU haut", "bas si pas robe", "accessoire", "chaussure"],
      "why_it_works": "Phrase 1. Phrase 2. Phrase 3."
    }}
  ],
  "shopping_priorities": ["", "", "", "", ""],
  "style_notes": {{
    "matieres_recommandees": ["matière — raison courte", "matière — raison courte", "matière — raison courte"],
    "motifs_recommandes": ["motif — raison courte", "motif — raison courte", "motif — raison courte"],
    "matieres_eviter": ["matière — raison courte", "matière — raison courte"],
    "motifs_eviter": ["motif — raison courte", "motif — raison courte"]
  }}
}}

RAPPEL: tops=6 exactement. avoid_by_category.shoes = chaussures UNIQUEMENT. avoid_by_category.accessories = accessoires UNIQUEMENT. Zéro texte hors JSON.
"""