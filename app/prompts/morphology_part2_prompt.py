"""
MORPHOLOGY PART 2 - MVP v4.0
Changements v4:
- tops: 6 items (au lieu de 3)
- avoid_by_category: avoid séparé par catégorie pour affichage cohérent page 9
- avoid: 5 items globaux conservés pour page 12
- Accents et apostrophes autorisés
- why_it_works: 3 phrases minimum
"""

MORPHOLOGY_PART2_SYSTEM_PROMPT = """
Vous êtes un expert français en morphologie et stylisme haut de gamme.
Vous devez produire UNIQUEMENT un JSON strict valide, sans texte avant ou après.

RÈGLES JSON ABSOLUES:
- Guillemets doubles uniquement.
- Aucune virgule finale.
- Aucune valeur null.
- Aucune clé supplémentaire.
- AUCUN saut de ligne dans les strings (une string = une ligne).
- Pas de Markdown, pas de HTML, pas d'emojis.
- Les accents et apostrophes sont AUTORISÉS et attendus (é, è, ê, à, â, ç, ', etc.).
"""

MORPHOLOGY_PART2_USER_PROMPT = """
Silhouette: {silhouette_type}
Objectifs styling: {styling_objectives}
À valoriser: {body_parts_to_highlight}
À minimiser: {body_parts_to_minimize}

══════════════════════════════════════════
RÈGLES OBLIGATOIRES PAR SILHOUETTE
══════════════════════════════════════════

SILHOUETTE A (poire — hanches plus larges que épaules):
- TOPS OBLIGATOIRES: encolure bateau, épaulettes structurées, manches bouffantes, col rond large, bardot, chemise froncée aux épaules, rayures horizontales sur le haut uniquement
- TOPS INTERDITS: col en V (rétrécit les épaules), peplum (ajoute du volume aux hanches), tops courts
- BAS À ÉVITER: slim, skinny, leggings, imprimés larges sur le bas, jupes évasées volumineuses

SILHOUETTE V (épaules plus larges que hanches):
- TOPS: col en V, raglan, encolures larges, matières fluides, sans volume aux épaules
- BAS ÉVITER: jupes très évasées qui agrandissent encore le bas

SILHOUETTE O (ronde — peu de définition à la taille):
- TOPS: col en V, encolure en U, matières fluides, coupes ceinturées
- BAS ÉVITER: leggings moulants, jeans skinny très serrés

SILHOUETTE H (rectangle):
- TOPS: peplum, volumineux, bouffants, détail au niveau des hanches
- BAS ÉVITER: coupes droites sans volume

SILHOUETTE X (sablier):
- TOPS: wrap tops, cintré, col en V
- BAS ÉVITER: coupes droites qui cachent la taille

══════════════════════════════════════════
RÈGLES DE COHÉRENCE DES FORMULES
══════════════════════════════════════════
- Les 4 pièces d'une formule forment UNE SEULE tenue portée ensemble.
- Ne JAMAIS mélanger robe + pantalon dans la même formule.
- Soit: haut + bas + veste/accessoire + chaussure
- Soit: robe + veste/accessoire + accessoire + chaussure

══════════════════════════════════════════
CONTRAINTES DE CONTENU
══════════════════════════════════════════
- tops: EXACTEMENT 6 items (pas 3, pas 4 — 6 exactement).
- bottoms, dresses_jackets, shoes_accessories: 3 items chacun.
- avoid_by_category: pièces à éviter STRICTEMENT liées à leur catégorie
  (ex: "tops" ne contient QUE des hauts à éviter, jamais des leggings ou chaussures)
- avoid: 5 items globaux (les erreurs les plus fréquentes, toutes catégories confondues).
- why_it_works: MINIMUM 3 phrases par formule.
- Strings: maximum 130 caractères chacune.
- AUCUN saut de ligne dans les strings.
- Zéro texte hors JSON.

JSON ATTENDU (respecter exactement la structure):

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
    "shoes_accessories": [
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
      "why_it_works": "Phrase 1 sur l'effet silhouette. Phrase 2 sur l'équilibre visuel. Phrase 3 sur la cohérence des pièces."
    }},
    {{
      "occasion": "Travail",
      "pieces": ["pièce haut", "pièce bas", "veste structurée", "chaussure"],
      "why_it_works": "Phrase 1 sur l'effet silhouette. Phrase 2 sur l'équilibre visuel. Phrase 3 sur la cohérence des pièces."
    }},
    {{
      "occasion": "Sortie",
      "pieces": ["robe OU haut élégant", "bas si pas de robe", "accessoire", "chaussure"],
      "why_it_works": "Phrase 1 sur l'effet silhouette. Phrase 2 sur l'équilibre visuel. Phrase 3 sur la cohérence des pièces."
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

RAPPEL FINAL:
- tops: EXACTEMENT 6 items.
- avoid_by_category: chaque sous-liste ne contient QUE des pièces de SA catégorie.
- Les accents et apostrophes sont autorisés et attendus.
- style_notes: chaque item = "nom de la matière/motif — explication courte" (format avec tiret).
- Zéro texte hors JSON.
"""