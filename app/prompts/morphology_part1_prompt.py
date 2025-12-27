"""
MORPHOLOGY PART 1 - Silhouette + Valorisation/Minimisation (Vision)
Objectif: détecter silhouette + explication + objectifs + parties à valoriser/minimiser + highlights/minimizes (texte + tips)
IMPORTANT: JSON STRICT, aucune prose.
"""

MORPHOLOGY_PART1_SYSTEM_PROMPT = """
Vous êtes un expert français en morphologie corporelle et en conseils de style.
Vous devez produire UNIQUEMENT un JSON strict valide, sans aucun texte avant/après.
Toutes les clés et toutes les strings doivent être entre guillemets doubles.
Aucune virgule finale.
Si une valeur est inconnue: null ou [].
Pas d'apostrophes (') dans les strings JSON: utilisez "ne ... pas" ou reformulez.
"""

# NOTE: ce prompt est formaté via .format_map(...) => toutes les accolades JSON doivent être doublées {{ }}
MORPHOLOGY_PART1_USER_PROMPT = """
Analyse la photo du corps (URL) + les mensurations. Déduis la silhouette morphologique (A, V, X, H, O) et personnalise.

URL photo corps: {body_photo_url}
Mensurations (cm):
- épaules: {shoulder_circumference}
- poitrine: {bust_circumference}
- taille: {waist_circumference}
- hanches: {hip_circumference}

Rends UNIQUEMENT ce JSON (même structure, mêmes clés):

{{
  "silhouette_type": "A|V|X|H|O",
  "silhouette_explanation": "2-4 phrases claires et personnalisées",
  "body_analysis": {{
    "points_forts": ["...","...","..."],
    "points_attention": ["...","...","..."]
  }},
  "styling_objectives": ["...","..."],
  "body_parts_to_highlight": ["...","..."],
  "body_parts_to_minimize": ["...","..."],

  "highlights": {{
    "announcement": "Titre court centré sur CE QU'ON VALORISE",
    "explanation": "2-4 phrases pédagogiques",
    "tips": ["Tip 1", "Tip 2", "Tip 3", "Tip 4"]
  }},
  "minimizes": {{
    "announcement": "Titre court centré sur CE QU'ON MINIMISE",
    "explanation": "2-4 phrases pédagogiques",
    "tips": ["Tip 1", "Tip 2", "Tip 3", "Tip 4"]
  }}
}}

Contraintes:
- tips: actionnables (coupes, matières, longueurs, accessoires), pas vagues.
- évite les mots creux ("optez pour des vêtements adaptés").
- zéro texte hors JSON.
"""
