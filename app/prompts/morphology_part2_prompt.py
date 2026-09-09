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

VOCABULAIRE OBLIGATOIRE — termes français uniquement
Les noms de pièces doivent utiliser le vocabulaire français de la mode.
✗ INTERDIT : "wrap top", "wide leg", "a-line", "crop top", "oversized"
✓ UTILISER : "cache-cœur", "pantalon palazzo", "jupe trapèze", "top court", "oversize"
Un nom en anglais ne correspond à aucun produit dans le catalogue et casse la recherche.

══════════════════════════════════════════
RÈGLES OBLIGATOIRES PAR SILHOUETTE
══════════════════════════════════════════

SILHOUETTE A (poire — hanches > épaules)
Objectif : élargir visuellement la ligne d'épaules, marquer la taille,
laisser le bas tomber sans mouler la hanche.
- TOPS : encolure bateau, encolure carrée, col en V large, épaulettes,
  manches bouffantes, froncé aux épaules, cache-cœur, bardot
- TOPS INTERDITS : hauts qui s'arrêtent sur la partie la plus large des hanches,
  cardigans longs et fluides, hauts moulants sur les hanches
- BAS : droits, évasés, trapèze, palazzo, taille haute
- BAS INTERDITS : slim, skinny, leggings, imprimés larges sur les hanches
- VESTES : structurées aux épaules, blazers à épaulettes, vestes courtes cintrées
- ROBES : empire, portefeuille, trapèze, robe-chemise ceinturée

SILHOUETTE V (triangle inversé — épaules > hanches)
Objectif : adoucir la ligne d'épaules et donner du volume au bas du corps.
- TOPS : col en V, décolleté profond, col bénitier, raglan, drapés,
  matières fluides sans structure aux épaules
- TOPS INTERDITS : encolure bateau, col carmen, épaulettes, manches bouffantes,
  cols roulés, rayures horizontales en haut
- BAS : évasés, palazzo, jupes trapèze, jupes froncées, flare
- VESTES : longues, cintrées à la taille, sans structure d'épaule
- ROBES : trapèze, patineuse, portefeuille avec jupe ample
- ACCESSOIRES : colliers longs et sautoirs. Éviter les ras-du-cou.

SILHOUETTE X (sablier — épaules ≈ hanches, taille marquée)
Objectif : souligner la taille, ne jamais la masquer.
- TOPS : cache-cœur, cintrés, col en V, drapés, taille marquée
- TOPS INTERDITS : oversize, coupes informes, tuniques droites longues
- BAS : jupes trapèze, jupes crayon, pantalons droits taille haute, taille haute
- VESTES : cintrées, blazers cintrés, vestes ceinturées
- ROBES : portefeuille, cintrée ceinturée, drapée, fourreau ajustée à la taille
- ROBES INTERDITES : empire, robes droites sans ceinture — elles masquent la taille

SILHOUETTE H (rectangle — épaules ≈ hanches, taille peu marquée)
Objectif : créer une taille visuelle et du relief aux hanches ou aux épaules.
- TOPS : peplum, cache-cœur, tuniques ceinturées, découpes, fronces, volants
- TOPS INTERDITS : coupes très moulantes sans détail, tops informes
- BAS : évasés, jupes froncées, jupes trapèze, taille haute
- VESTES : ceinturées, blazers cintrés, manteaux à ceinture
- ROBES : portefeuille, cache-cœur ceinturée, empire, robe-chemise ceinturée
- ACCESSOIRES : ceintures fines ou moyennes à la taille naturelle.
  Éviter les ceintures-corsets, trop massives.

SILHOUETTE O (ronde — volumes au centre, taille peu dessinée)
Objectif : créer de la verticalité et allonger la ligne, sans marquer la taille.
- TOPS : col en V, encolure en U, matières fluides, tuniques, coupes non ajustées
  à la taille
- TOPS INTERDITS : matières rigides, coupes serrées à la taille, détails au niveau
  du ventre, rayures horizontales
- BAS : droits, palazzo, larges fluides, taille haute confortable
- VESTES : longues ouvertes, mi-longues fluides, gilets longs — jamais ceinturées
- ROBES : empire, portefeuille, cache-cœur, droite fluide
- ACCESSOIRES : sautoirs et colliers longs pour la verticalité.
  Les ceintures avec parcimonie.

RÈGLE COMMUNE
Chaque nom de pièce doit désigner une coupe qui existe réellement dans le
commerce français. En cas de doute, choisis le terme le plus courant et le plus
simple. Ne combine jamais plus de deux qualificatifs dans un nom.

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
- jackets : EXACTEMENT 3 items — obligatoirement 2 vestes/blazers + 1 MANTEAU
  (manteau, trench ou cape). Sans couleur dans name.
- bottoms : EXACTEMENT 3 items (pantalons, jupes, jeans uniquement, sans couleur dans name)
- shoes_accessories : EXACTEMENT 3 items
- avoid_by_category : pièces STRICTEMENT de leur catégorie
- style_notes : format "nom — explication courte"
- Strings max 130 caractères. Zéro texte hors JSON.
- INTERDICTION DES DOUBLONS : dans une même catégorie, deux pièces ne doivent
  jamais désigner la même coupe sous des noms différents.
  ✗ "Blazer cintré" et "Blazer ajusté" dans jackets
  ✗ "Top cintré" et "Haut ajusté" dans tops
  Chaque item doit être une coupe distincte et reconnaissable.
  
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