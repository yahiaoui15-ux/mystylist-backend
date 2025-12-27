"""
MORPHOLOGY PART 3 - Détails Styling
"""

MORPHOLOGY_PART3_SYSTEM_PROMPT = """
Tu es expert en détails de styling morphologique.

IMPORTANT:
- Réponds UNIQUEMENT en JSON STRICT.
- Zéro texte hors JSON.
- EXACTEMENT 7 pièges par catégorie.
"""

MORPHOLOGY_PART3_USER_PROMPT = """
Silhouette: {silhouette_type}
Objectifs: {styling_objectives}
À valoriser: {body_parts_to_highlight}
À minimiser: {body_parts_to_minimize}

Génère un JSON structuré avec:
- matieres (puces)
- motifs (recommandes / a_eviter)
- pieges (liste de 7)

JSON strict, aucune phrase hors JSON.
"""
