"""
MORPHOLOGY PART 2 - MVP v2.1
Corrections v2.1:
- Règles silhouette-specific explicites (A/V/X/H/O)
- why_it_works: 3-4 phrases minimum
- Pièces d'une formule = tenue cohérente (pas robe + pantalon)
- style_notes: matières + motifs recommandés/éviter
- Interdits renforcés par silhouette
"""

MORPHOLOGY_PART2_SYSTEM_PROMPT = """
Vous êtes un expert français en morphologie et stylisme haut de gamme.
Vous devez produire UNIQUEMENT un JSON strict valide, sans texte avant ou après.

RÈGLES JSON ABSOLUES:
- Guillemets doubles uniquement.
- Aucune virgule finale.
- Aucune valeur null.
- Aucune clé supplémentaire.
- Aucune apostrophe dans les strings: remplacer ' par un espace ou reformuler.
- AUCUN saut de ligne dans les strings.
- Pas de Markdown, pas de HTML, pas d emojis.

OBJECTIF:
Produire un JSON 100% parseable pour alimenter un rapport PDF premium.
Le ton doit être concret, premium, utile, pédagogique et parfaitement cohérent avec la silhouette.
"""

MORPHOLOGY_PART2_USER_PROMPT = """
Silhouette: {silhouette_type}
Objectifs styling: {styling_objectives}
A valoriser: {body_parts_to_highlight}
A minimiser: {body_parts_to_minimize}

══════════════════════════════════════════
RÈGLES OBLIGATOIRES PAR SILHOUETTE
══════════════════════════════════════════

SILHOUETTE A (poire - hanches plus larges que epaules):
- TOPS OBLIGATOIRES: encolure bateau, epaulettes structurees, manches bouffantes, col rond large, bardot, rayures horizontales sur le haut, empiecements colores sur les epaules
- TOPS ABSOLUMENT INTERDITS: col en V (retrecit les epaules), peplum (ajoute du volume aux hanches), tops courts qui decouvrent la taille
- BAS: droits, palazzo, legerement evases depuis la hanche, couleurs sombres et unies
- BAS INTERDITS: slim, skinny, collants, leggings, imprimés larges sur le bas
- ROBES: empire (ne marque pas les hanches), portefeuille (croise sur la poitrine)
- ROBES INTERDITES: fourreau, moulante, evasee depuis les hanches
- VESTES: structurees avec epaulettes, s arretant a la taille ou juste sous la taille, jamais au niveau des hanches
- ACCESSOIRES: ceinture fine pour marquer la taille, colliers longs, sacs portés haut

SILHOUETTE V (épaules plus larges que hanches):
- TOPS: col en V, raglan, encolures larges, matieres fluides, pas de volume aux epaules
- BAS: evases, palazzo, motifs et couleurs claires sur le bas pour compenser
- ROBES: trapeze, evasees depuis la taille

SILHOUETTE O (ronde - peu de definition a la taille):
- TOPS: col en V, encolure en U, matieres fluides, coupes ceinturees
- BAS: droits, palazzo, tailles hautes
- ROBES: empire, portefeuille
- EVITER: horizontal, volumes excessifs, ceintures trop larges

SILHOUETTE H (rectangle - peu de definition entre taille et hanches):
- TOPS: peplum, volumineux, bouffants, detail au niveau des hanches
- BAS: evases, jupes froncees, volume acceptable
- Objectif: creer l illusion d une taille

SILHOUETTE X (sablier - taille tres marquee):
- Mettre en valeur la taille: ceintures, coupes cintrees, robes portefeuille
- Eviter: coupes qui cachent la silhouette

══════════════════════════════════════════
RÈGLES DE COHÉRENCE DES FORMULES DE TENUES
══════════════════════════════════════════
IMPORTANT: Les pieces d une formule constituent UNE SEULE tenue portee ensemble.
- Ne JAMAIS melanger robe + pantalon dans la meme formule.
- Choisir SOIT: haut + bas + veste/accessoire
- SOIT: robe + veste/accessoire
- Les 4 pieces doivent former un look complet et coherent.
- Les couleurs doivent etre compatibles entre elles.

══════════════════════════════════════════
CONTRAINTES DE CONTENU
══════════════════════════════════════════
- Toutes les strings <= 130 caracteres.
- why_it_works: MINIMUM 3 phrases distinctes (pas une seule phrase courte).
  Expliquer: (1) comment la combinaison flatte la silhouette {silhouette_type},
  (2) quel effet visuel est cree, (3) pourquoi les pieces fonctionnent ensemble.
- Interdit: phrases generiques du type "Coupe adaptee a votre silhouette".
- Interdit: doublons exacts entre les 3 formules.
- Interdit: leggings, t-shirt loose, cardigan oversize.
- Chaque item doit etre elegant, portable et coherent avec une cliente premium.
- Aucun saut de ligne dans les strings.
- Aucune apostrophe dans les strings.
- Zero texte hors JSON.

JSON ATTENDU (respecter exactement la structure et le nombre d elements):

{{
  "essentials": {{
    "tops": [
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
  "avoid": [
    {{"name": "", "why": ""}},
    {{"name": "", "why": ""}},
    {{"name": "", "why": ""}}
  ],
  "outfit_formulas": [
    {{
      "occasion": "Quotidien",
      "pieces": ["haut recommande", "bas recommande", "veste ou accessoire", "chaussure"],
      "why_it_works": "Phrase 1 sur leffet silhouette. Phrase 2 sur lequilibre visuel cree. Phrase 3 sur la coherence des pieces ensemble."
    }},
    {{
      "occasion": "Travail",
      "pieces": ["haut recommande", "bas recommande", "veste structuree", "chaussure"],
      "why_it_works": "Phrase 1 sur leffet silhouette. Phrase 2 sur lequilibre visuel cree. Phrase 3 sur la coherence des pieces ensemble."
    }},
    {{
      "occasion": "Sortie",
      "pieces": ["robe recommandee OU haut elegant", "bas si pas de robe", "accessoire", "chaussure"],
      "why_it_works": "Phrase 1 sur leffet silhouette. Phrase 2 sur lequilibre visuel cree. Phrase 3 sur la coherence des pieces ensemble."
    }}
  ],
  "shopping_priorities": ["", "", "", "", ""],
  "style_notes": {{
    "matieres_recommandees": ["", "", ""],
    "motifs_recommandes": ["", "", ""],
    "matieres_eviter": ["", ""],
    "motifs_eviter": ["", ""]
  }}
}}

RAPPEL FINAL:
- Zero texte hors JSON.
- Aucune cle ajoutee.
- 3 items exacts par sous-categorie essentials.
- 3 items exacts dans avoid.
- 3 formules exactes avec 4 pieces COHERENTES (pas robe + pantalon ensemble).
- 5 priorites shopping exactes.
- why_it_works: MINIMUM 3 phrases pour chaque formule.
- style_notes: 3 matieres recommandees, 3 motifs recommandes, 2 matieres a eviter, 2 motifs a eviter.
"""