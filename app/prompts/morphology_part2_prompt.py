"""
MORPHOLOGY PART 2 - Recommandations (Text) - SYNTAXE CORRIGÉE
"""

MORPHOLOGY_PART2_SYSTEM_PROMPT = """Expert styling morphologie. Générez recommandations.
Retournez UNIQUEMENT JSON valide."""

MORPHOLOGY_PART2_USER_PROMPT = """Générez recommandations pour silhouette: {silhouette_type}
Objectifs: {styling_objectives}

Retournez JSON avec recommendations (hauts/bas/robes/vestes/chaussures/accessoires).

Chaque catégorie:
- a_privilegier: 6 items avec cut_display + why
- a_eviter: 5 items avec cut_display + why

Adapté spécifiquement à silhouette {silhouette_type}.
Répondez UNIQUEMENT JSON.
"""