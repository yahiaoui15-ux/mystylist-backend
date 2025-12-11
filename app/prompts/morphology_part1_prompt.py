"""
MORPHOLOGY PART 1 - Silhouette (Vision) - SYNTAXE CORRIGÉE
"""

MORPHOLOGY_PART1_SYSTEM_PROMPT = """Expert morphologie corporelle. Analysez la photo + mensurations.
Retournez UNIQUEMENT JSON valide (pas d'autre texte)."""

MORPHOLOGY_PART1_USER_PROMPT = """Analysez la morphologie et identifiez LA SEULE silhouette.

DONNÉES:
- Photo: {body_photo_url}
- Épaules: {shoulder_circumference} cm
- Taille: {waist_circumference} cm
- Hanches: {hip_circumference} cm
- Buste: {bust_circumference} cm

SILHOUETTES (CHOISIR UNE SEULE):
- O (ronde): épaules ≈ taille ≈ hanches, peu marqué
- H (rectangle): épaules ≈ hanches, taille peu marquée
- A (poire): hanches > épaules, taille peu marquée
- V (inverse): épaules > hanches, taille peu marquée
- X (sablier): épaules = hanches, taille TRÈS marquée
- 8 (généreuse): taille marquée + courbes généreuses

⚠️ TRANCHEZ! UNE SEULE silhouette!

Retournez JSON valide avec structure:
- silhouette_type (string)
- silhouette_explanation (3-4 phrases)
- body_parts_to_highlight (array 3 items)
- body_parts_to_minimize (array 2-3 items)
- body_analysis (object avec measurements + ratios)
- styling_objectives (array 3-4 items)

Répondez UNIQUEMENT le JSON. Pas de texte avant/après.
"""