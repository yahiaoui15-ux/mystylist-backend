MORPHOLOGY_PART2_SYSTEM_PROMPT = """
Vous êtes un moteur de génération JSON strict pour une API.
Vous devez produire UNIQUEMENT un JSON strict valide, sans texte avant ou après.

Règles JSON ABSOLUES:
- Guillemets doubles uniquement.
- Aucune virgule finale.
- Aucune valeur null.
- Aucune clé supplémentaire.
- Aucune apostrophe (') dans les strings.
- AUCUN saut de ligne dans les strings (toutes les valeurs sur une seule ligne).
- Pas de Markdown, pas de HTML, pas de caractères décoratifs.

Objectif:
Produire un JSON minimal, court, et 100% parseable, pour alimenter un rapport PDF.
"""
# NOTE: formaté via .format_map(...) => accolades JSON doublées {{ }}
MORPHOLOGY_PART2_USER_PROMPT = """
Silhouette: {silhouette_type}
Objectifs styling: {styling_objectives}

Génère UNIQUEMENT le JSON ci-dessous, en respectant exactement la structure, les clés et le nombre d éléments.

Contraintes de contenu:
- Toutes les strings <= 80 caractères.
- Style concis, concret, sans blabla.
- "matieres": 4 éléments.
- "motifs.recommandes": 3 éléments.
- "motifs.a_eviter": 3 éléments.
- "pieges": 7 éléments, format exact "Piege X: ...", X de 1 à 7.
- Aucun saut de ligne dans les strings.
- Aucune apostrophe (') dans les strings.

JSON attendu:

{{
  "hauts": {{
    "matieres": ["", "", "", ""],
    "motifs": {{
      "recommandes": ["", "", ""],
      "a_eviter": ["", "", ""]
    }},
    "pieges": ["Piege 1: ...", "Piege 2: ...", "Piege 3: ...", "Piege 4: ...", "Piege 5: ...", "Piege 6: ...", "Piege 7: ..."]
  }},
  "bas": {{
    "matieres": ["", "", "", ""],
    "motifs": {{
      "recommandes": ["", "", ""],
      "a_eviter": ["", "", ""]
    }},
    "pieges": ["Piege 1: ...", "Piege 2: ...", "Piege 3: ...", "Piege 4: ...", "Piege 5: ...", "Piege 6: ...", "Piege 7: ..."]
  }},
  "robes": {{
    "matieres": ["", "", "", ""],
    "motifs": {{
      "recommandes": ["", "", ""],
      "a_eviter": ["", "", ""]
    }},
    "pieges": ["Piege 1: ...", "Piege 2: ...", "Piege 3: ...", "Piege 4: ...", "Piege 5: ...", "Piege 6: ...", "Piege 7: ..."]
  }},
  "vestes": {{
    "matieres": ["", "", "", ""],
    "motifs": {{
      "recommandes": ["", "", ""],
      "a_eviter": ["", "", ""]
    }},
    "pieges": ["Piege 1: ...", "Piege 2: ...", "Piege 3: ...", "Piege 4: ...", "Piege 5: ...", "Piege 6: ...", "Piege 7: ..."]
  }},
  "maillot_lingerie": {{
    "matieres": ["", "", "", ""],
    "motifs": {{
      "recommandes": ["", "", ""],
      "a_eviter": ["", "", ""]
    }},
    "pieges": ["Piege 1: ...", "Piege 2: ...", "Piege 3: ...", "Piege 4: ...", "Piege 5: ...", "Piege 6: ...", "Piege 7: ..."]
  }},
  "chaussures": {{
    "matieres": ["", "", "", ""],
    "motifs": {{
      "recommandes": ["", "", ""],
      "a_eviter": ["", "", ""]
    }},
    "pieges": ["Piege 1: ...", "Piege 2: ...", "Piege 3: ...", "Piege 4: ...", "Piege 5: ...", "Piege 6: ...", "Piege 7: ..."]
  }},
  "accessoires": {{
    "matieres": ["", "", "", ""],
    "motifs": {{
      "recommandes": ["", "", ""],
      "a_eviter": ["", "", ""]
    }},
    "pieges": ["Piege 1: ...", "Piege 2: ...", "Piege 3: ...", "Piege 4: ...", "Piege 5: ...", "Piege 6: ...", "Piege 7: ..."]
  }}
}}

Rappel final:
- Zéro texte hors JSON.
- Aucune clé ajoutée.
"""
