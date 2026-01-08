MORPHOLOGY_PART3_SYSTEM_PROMPT = """
Vous etes un moteur de generation JSON strict pour une API.
Vous devez produire UNIQUEMENT un JSON strict valide, sans texte avant/apres.

REGLES JSON ABSOLUES:
- Guillemets doubles uniquement.
- Aucune virgule finale.
- Aucune valeur null.
- Aucune cle supplementaire.
- Aucune apostrophe (') dans les strings.
- AUCUN saut de ligne dans les strings.
- Pas de Markdown, pas de HTML, pas de puces, pas d emojis.

IMPORTANT:
PART 3 = DETAILS UNIQUEMENT (matieres + motifs + pieges).
Aucune liste recommandes / a_eviter de pieces (c est en PART 2).
- Matieres et motifs: elements courts (2 a 5 mots), pas de phrases.
- Pieges: EXACTEMENT 7, format exact "Piege X: ...", X de 1 a 7.
"""
MORPHOLOGY_PART3_USER_PROMPT = """
Silhouette: {silhouette_type}
Objectifs: {styling_objectives}
A valoriser: {body_parts_to_highlight}
A minimiser: {body_parts_to_minimize}

Retourne UNIQUEMENT ce JSON:

{{
  "details": {{
    "hauts": {{
      "matieres": ["...","...","...","..."],
      "motifs": {{
        "recommandes": ["...","...","..."],
        "a_eviter": ["...","...","..."]
      }},
      "pieges": ["Piege 1: ...","Piege 2: ...","Piege 3: ...","Piege 4: ...","Piege 5: ...","Piege 6: ...","Piege 7: ..."]
    }},
    "bas": {{
      "matieres": ["...","...","...","..."],
      "motifs": {{
        "recommandes": ["...","...","..."],
        "a_eviter": ["...","...","..."]
      }},
      "pieges": ["Piege 1: ...","Piege 2: ...","Piege 3: ...","Piege 4: ...","Piege 5: ...","Piege 6: ...","Piege 7: ..."]
    }},
    "robes": {{
      "matieres": ["...","...","...","..."],
      "motifs": {{
        "recommandes": ["...","...","..."],
        "a_eviter": ["...","...","..."]
      }},
      "pieges": ["Piege 1: ...","Piege 2: ...","Piege 3: ...","Piege 4: ...","Piege 5: ...","Piege 6: ...","Piege 7: ..."]
    }},
    "vestes": {{
      "matieres": ["...","...","...","..."],
      "motifs": {{
        "recommandes": ["...","...","..."],
        "a_eviter": ["...","...","..."]
      }},
      "pieges": ["Piege 1: ...","Piege 2: ...","Piege 3: ...","Piege 4: ...","Piege 5: ...","Piege 6: ...","Piege 7: ..."]
    }},
    "maillot_lingerie": {{
      "matieres": ["...","...","...","..."],
      "motifs": {{
        "recommandes": ["...","...","..."],
        "a_eviter": ["...","...","..."]
      }},
      "pieges": ["Piege 1: ...","Piege 2: ...","Piege 3: ...","Piege 4: ...","Piege 5: ...","Piege 6: ...","Piege 7: ..."]
    }},
    "chaussures": {{
      "matieres": ["...","...","...","..."],
      "motifs": {{
        "recommandes": ["...","...","..."],
        "a_eviter": ["...","...","..."]
      }},
      "pieges": ["Piege 1: ...","Piege 2: ...","Piege 3: ...","Piege 4: ...","Piege 5: ...","Piege 6: ...","Piege 7: ..."]
    }},
    "accessoires": {{
      "matieres": ["...","...","...","..."],
      "motifs": {{
        "recommandes": ["...","...","..."],
        "a_eviter": ["...","...","..."]
      }},
      "pieges": ["Piege 1: ...","Piege 2: ...","Piege 3: ...","Piege 4: ...","Piege 5: ...","Piege 6: ...","Piege 7: ..."]
    }}
  }}
}}

Contraintes:
- "matieres": EXACTEMENT 4 elements (2 a 5 mots), pas de phrases.
- "motifs": 3 recommandes + 3 a eviter (2 a 5 mots), pas de phrases.
- "pieges": EXACTEMENT 7, format strict "Piege X: ...".
- Zero texte hors JSON.
"""
