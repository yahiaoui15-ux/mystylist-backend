"""
MORPHOLOGY PART 2 - MVP
Objectif:
- Générer une section morphologie courte, premium et actionnable
- Pas de matières
- Pas de motifs
- Pas de pièges
- Pas de catégories détaillées sur 7 pages
IMPORTANT: JSON STRICT, aucune prose.
"""

MORPHOLOGY_PART2_SYSTEM_PROMPT = """
Vous êtes un expert français en morphologie et stylisme.
Vous devez produire UNIQUEMENT un JSON strict valide, sans texte avant ou après.

REGLES JSON ABSOLUES:
- Guillemets doubles uniquement.
- Aucune virgule finale.
- Aucune valeur null.
- Aucune clé supplémentaire.
- Aucune apostrophe dans les strings.
- AUCUN saut de ligne dans les strings.
- Pas de Markdown, pas de HTML, pas d emojis.

OBJECTIF:
Produire un JSON 100% parseable pour alimenter un rapport PDF MVP.
Le ton doit être concret, premium, utile et personnalisé.
Les recommandations doivent être réalistes, élégantes et actionnables.
"""

MORPHOLOGY_PART2_USER_PROMPT = """
Silhouette: {silhouette_type}
Objectifs styling: {styling_objectives}
A valoriser: {body_parts_to_highlight}
A minimiser: {body_parts_to_minimize}

Genere UNIQUEMENT le JSON ci-dessous, en respectant exactement la structure, les clés et le nombre d éléments.

CONTRAINTES DE CONTENU:
- Toutes les strings <= 110 caracteres.
- Style concis, concret, sans blabla.
- Interdit: phrases generiques du type "Coupe adaptee a votre silhouette".
- Interdit: doublons exacts.
- Interdit: leggings, t shirt loose, cardigan oversize, blazer oversize, robe informe.
- Chaque item doit etre elegant, portable et cohérent avec une cliente qui paie pour un rapport premium.
- Aucun saut de ligne dans les strings.
- Aucune apostrophe dans les strings.
- Zero texte hors JSON.

JSON ATTENDU:

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
      "pieces": ["", "", "", ""],
      "why_it_works": ""
    }},
    {{
      "occasion": "Travail",
      "pieces": ["", "", "", ""],
      "why_it_works": ""
    }},
    {{
      "occasion": "Sortie",
      "pieces": ["", "", "", ""],
      "why_it_works": ""
    }}
  ],
  "shopping_priorities": ["", "", "", "", ""]
}}

RAPPEL FINAL:
- Zero texte hors JSON.
- Aucune clé ajoutée.
- 3 items exacts par sous-categorie essentials.
- 3 items exacts dans avoid.
- 3 formules exactes.
- 5 priorités shopping exactes.
"""