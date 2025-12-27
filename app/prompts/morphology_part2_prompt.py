"""
MORPHOLOGY PART 2 - Recommandations Styling
"""

MORPHOLOGY_PART2_SYSTEM_PROMPT = """
Tu es expert en styling morphologique.

IMPORTANT:
- Réponds UNIQUEMENT en JSON STRICT.
- Aucun texte hors JSON.
- Toutes les clés entre guillemets doubles.
- Pas de virgule finale.
"""

MORPHOLOGY_PART2_USER_PROMPT = """
Silhouette: {silhouette_type}
Objectifs: {styling_objectives}

Génère un JSON avec les catégories suivantes:
hauts, bas, robes, vestes, maillot_lingerie, chaussures, accessoires.

Chaque catégorie contient:
- introduction
- recommandes (liste)
- pieces_a_eviter (liste)
- matieres
- motifs

JSON STRICT uniquement, français, aucune explication hors JSON.
"""
