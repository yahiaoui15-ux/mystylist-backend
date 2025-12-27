"""
MORPHOLOGY PART 2 - Recommandations par catégorie (TEXT)
Objectif: renvoyer des recommandations exploitables par le template PDF.
IMPORTANT: JSON STRICT, structure stable.
"""

MORPHOLOGY_PART2_SYSTEM_PROMPT = """
Vous êtes un expert français en conseils vestimentaires morphologiques.
Vous devez produire UNIQUEMENT un JSON strict valide, sans texte avant/après.
Toutes les clés/strings entre guillemets doubles. Pas de virgule finale.
Pas d'apostrophes (') dans les strings JSON.
"""

# NOTE: formaté via .format_map(...) => accolades JSON doublées {{ }}
MORPHOLOGY_PART2_USER_PROMPT = """
Silhouette: {silhouette_type}
Objectifs styling: {styling_objectives}

Génère des recommandations par catégories.
Rends UNIQUEMENT ce JSON:

{{
  "recommendations": {{
    "hauts": {{
      "introduction": "1-2 phrases",
      "recommandes": [{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}}],
      "pieces_a_eviter": [{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}}]
    }},
    "bas": {{
      "introduction": "1-2 phrases",
      "recommandes": [{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}}],
      "pieces_a_eviter": [{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"..." ,"why":"..."}}]
    }},
    "robes": {{
      "introduction": "1-2 phrases",
      "recommandes": [{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"..." ,"why":"..."}}],
      "pieces_a_eviter": [{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"..." ,"why":"..."}}]
    }},
    "vestes": {{
      "introduction": "1-2 phrases",
      "recommandes": [{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"..." ,"why":"..."}}],
      "pieces_a_eviter": [{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"..." ,"why":"..."}}]
    }},
    "maillot_lingerie": {{
      "introduction": "1-2 phrases",
      "recommandes": [{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"..." ,"why":"..."}}],
      "pieces_a_eviter": [{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"..." ,"why":"..."}}]
    }},
    "chaussures": {{
      "introduction": "1-2 phrases",
      "recommandes": [{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"..." ,"why":"..."}}],
      "pieces_a_eviter": [{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"..." ,"why":"..."}}]
    }},
    "accessoires": {{
      "introduction": "1-2 phrases",
      "recommandes": [{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"..." ,"why":"..."}}],
      "pieces_a_eviter": [{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"...","why":"..."}},{{"cut_display":"..." ,"why":"..."}}]
    }}
  }}
}}

Contraintes:
- Chaque why: 1 phrase claire (pas vague).
- Zéro texte hors JSON.
"""
