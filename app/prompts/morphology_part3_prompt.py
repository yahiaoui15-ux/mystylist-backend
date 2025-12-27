"""
MORPHOLOGY PART 3 - Détails (matières + motifs + pièges) par catégorie
Objectif: alimenter pages 9-15 (matières/motifs/pièges) sans être vide.
IMPORTANT: JSON STRICT, structure stable: details -> categories.
"""

MORPHOLOGY_PART3_SYSTEM_PROMPT = """
Vous êtes un expert français en styling morphologique.
Vous devez produire UNIQUEMENT un JSON strict valide, sans texte avant/après.
Toutes les clés/strings entre guillemets doubles. Pas de virgule finale.
Pas d'apostrophes (') dans les strings JSON.
Chaque catégorie doit contenir EXACTEMENT 7 pièges.
"""

# NOTE: formaté via .format_map(...) => accolades JSON doublées {{ }}
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
      "pieges": ["Piège 1: ...","Piège 2: ...","Piège 3: ...","Piège 4: ...","Piège 5: ...","Piège 6: ...","Piège 7: ..."]
    }},
    "bas": {{
      "matieres": ["...","...","...","..."],
      "motifs": {{
        "recommandes": ["...","...","..."],
        "a_eviter": ["...","...","..."]
      }},
      "pieges": ["Piège 1: ...","Piège 2: ...","Piège 3: ...","Piège 4: ...","Piège 5: ...","Piège 6: ...","Piège 7: ..."]
    }},
    "robes": {{
      "matieres": ["...","...","...","..."],
      "motifs": {{
        "recommandes": ["...","...","..."],
        "a_eviter": ["...","...","..."]
      }},
      "pieges": ["Piège 1: ...","Piège 2: ...","Piège 3: ...","Piège 4: ...","Piège 5: ...","Piège 6: ...","Piège 7: ..."]
    }},
    "vestes": {{
      "matieres": ["...","...","...","..."],
      "motifs": {{
        "recommandes": ["...","...","..."],
        "a_eviter": ["...","...","..."]
      }},
      "pieges": ["Piège 1: ...","Piège 2: ...","Piège 3: ...","Piège 4: ...","Piège 5: ...","Piège 6: ...","Piège 7: ..."]
    }},
    "maillot_lingerie": {{
      "matieres": ["...","...","...","..."],
      "motifs": {{
        "recommandes": ["...","...","..."],
        "a_eviter": ["...","...","..."]
      }},
      "pieges": ["Piège 1: ...","Piège 2: ...","Piège 3: ...","Piège 4: ...","Piège 5: ...","Piège 6: ...","Piège 7: ..."]
    }},
    "chaussures": {{
      "matieres": ["...","...","...","..."],
      "motifs": {{
        "recommandes": ["...","...","..."],
        "a_eviter": ["...","...","..."]
      }},
      "pieges": ["Piège 1: ...","Piège 2: ...","Piège 3: ...","Piège 4: ...","Piège 5: ...","Piège 6: ...","Piège 7: ..."]
    }},
    "accessoires": {{
      "matieres": ["...","...","...","..."],
      "motifs": {{
        "recommandes": ["...","...","..."],
        "a_eviter": ["...","...","..."]
      }},
      "pieges": ["Piège 1: ...","Piège 2: ...","Piège 3: ...","Piège 4: ...","Piège 5: ...","Piège 6: ...","Piège 7: ..."]
    }}
  }}
}}

Contraintes:
- Matieres: 4 à 6 éléments, spécifiques (ex: "crêpe", "viscose structurée", "maille fine", etc.)
- Motifs: 3 recommandés + 3 à éviter, spécifiques.
- Pièges: EXACTEMENT 7, chacun commence par "Piège X: ..."
- Zéro texte hors JSON.
"""
