MORPHOLOGY_PART2_SYSTEM_PROMPT = """
Vous êtes un moteur de génération JSON strict pour une API.
Vous devez produire UNIQUEMENT un JSON strict valide, sans texte avant ou après.

REGLES JSON ABSOLUES:
- Guillemets doubles uniquement.
- Aucune virgule finale.
- Aucune valeur null.
- Aucune clé supplémentaire.
- Aucune apostrophe (') dans les strings.
- AUCUN saut de ligne dans les strings (toutes les valeurs sur une seule ligne).
- Pas de Markdown, pas de HTML, pas de caractères décoratifs.

OBJECTIF:
Produire un JSON 100% parseable pour alimenter un rapport PDF.
PART 2 = PIECES UNIQUEMENT (recommandes + a_eviter). Aucune matiere, aucun motif, aucun piege.
"""
MORPHOLOGY_PART2_USER_PROMPT = """
Silhouette: {silhouette_type}
Objectifs styling: {styling_objectives}
A valoriser: {body_parts_to_highlight}
A minimiser: {body_parts_to_minimize}

Genere UNIQUEMENT le JSON ci-dessous, en respectant exactement la structure, les cles et le nombre d elements.

CONTRAINTES DE CONTENU:
- Toutes les strings <= 80 caracteres.
- Style concis, concret, sans blabla.
- Interdit: phrases generiques du type "Coupe adaptee a votre silhouette".
- Interdit: doublons exacts de cut_display dans une meme liste.
- Chaque item = 1 piece ou 1 type de coupe concret.
- "recommandes": EXACTEMENT 4 items par categorie.
- "a_eviter": EXACTEMENT 3 items par categorie.
- Aucun saut de ligne dans les strings.
- Aucune apostrophe (') dans les strings.

JSON ATTENDU:

{{
  "hauts": {{
    "recommandes": [
      {{"cut_display": "", "why": ""}},
      {{"cut_display": "", "why": ""}},
      {{"cut_display": "", "why": ""}},
      {{"cut_display": "", "why": ""}}
    ],
    "a_eviter": [
      {{"cut_display": "", "why": ""}},
      {{"cut_display": "", "why": ""}},
      {{"cut_display": "", "why": ""}}
    ]
  }},
  "bas": {{
    "recommandes": [
      {{"cut_display": "", "why": ""}},
      {{"cut_display": "", "why": ""}},
      {{"cut_display": "", "why": ""}},
      {{"cut_display": "", "why": ""}}
    ],
    "a_eviter": [
      {{"cut_display": "", "why": ""}},
      {{"cut_display": "", "why": ""}},
      {{"cut_display": "", "why": ""}}
    ]
  }},
  "robes": {{
    "recommandes": [
      {{"cut_display": "", "why": ""}},
      {{"cut_display": "", "why": ""}},
      {{"cut_display": "", "why": ""}},
      {{"cut_display": "", "why": ""}}
    ],
    "a_eviter": [
      {{"cut_display": "", "why": ""}},
      {{"cut_display": "", "why": ""}},
      {{"cut_display": "", "why": ""}}
    ]
  }},
  "vestes": {{
    "recommandes": [
      {{"cut_display": "", "why": ""}},
      {{"cut_display": "", "why": ""}},
      {{"cut_display": "", "why": ""}},
      {{"cut_display": "", "why": ""}}
    ],
    "a_eviter": [
      {{"cut_display": "", "why": ""}},
      {{"cut_display": "", "why": ""}},
      {{"cut_display": "", "why": ""}}
    ]
  }},
  "maillot_lingerie": {{
    "recommandes": [
      {{"cut_display": "", "why": ""}},
      {{"cut_display": "", "why": ""}},
      {{"cut_display": "", "why": ""}},
      {{"cut_display": "", "why": ""}}
    ],
    "a_eviter": [
      {{"cut_display": "", "why": ""}},
      {{"cut_display": "", "why": ""}},
      {{"cut_display": "", "why": ""}}
    ]
  }},
  "chaussures": {{
    "recommandes": [
      {{"cut_display": "", "why": ""}},
      {{"cut_display": "", "why": ""}},
      {{"cut_display": "", "why": ""}},
      {{"cut_display": "", "why": ""}}
    ],
    "a_eviter": [
      {{"cut_display": "", "why": ""}},
      {{"cut_display": "", "why": ""}},
      {{"cut_display": "", "why": ""}}
    ]
  }},
  "accessoires": {{
    "recommandes": [
      {{"cut_display": "", "why": ""}},
      {{"cut_display": "", "why": ""}},
      {{"cut_display": "", "why": ""}},
      {{"cut_display": "", "why": ""}}
    ],
    "a_eviter": [
      {{"cut_display": "", "why": ""}},
      {{"cut_display": "", "why": ""}},
      {{"cut_display": "", "why": ""}}
    ]
  }}
}}

RAPPEL FINAL:
- Zero texte hors JSON.
- Aucune cle ajoutee.
"""
