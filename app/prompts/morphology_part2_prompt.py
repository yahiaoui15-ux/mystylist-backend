"""
MORPHOLOGY PART 2 - RECOMMANDATIONS STYLING (OPTIMISE - TOKEN-LEAN)
✅ Descriptions longues (80-100 mots) + matieres personnalisées
✅ Prompt compact sans exemples JSON volumineux
✅ Token budget: ~1500-1800 au lieu de 3760+
"""

MORPHOLOGY_PART2_SYSTEM_PROMPT = """Vous êtes expert styling morphologique français.
Générez recommandations détaillées en JSON valide UNIQUEMENT.
Zéro texte avant/après JSON."""

MORPHOLOGY_PART2_USER_PROMPT = """Silhouette: {silhouette_type}
Objectifs: {styling_objectives}

Générez JSON avec 7 catégories (hauts, bas, robes, vestes, maillot_lingerie, chaussures, accessoires).
Chaque catégorie: introduction (1 phrase), recommandes (3-4 items), a_eviter (2-3 items), matieres (2-3 phrases).

Pour recommandes et a_eviter: cut_display (nom pièce), why (MAX 50 mots explicatif spécifique à {silhouette_type}).
Matieres: personnalisé pour {silhouette_type}, 1-2 phrases (pas plus de 30 mots).

Tout en français. JSON valide uniquement.

{{
  "recommendations": {{
    "hauts": {{"introduction": "", "recommandes": [{{"cut_display": "", "why": ""}}], "a_eviter": [], "matieres": ""}},
    "bas": {{"introduction": "", "recommandes": [{{"cut_display": "", "why": ""}}], "a_eviter": [], "matieres": ""}},
    "robes": {{"introduction": "", "recommandes": [{{"cut_display": "", "why": ""}}], "a_eviter": [], "matieres": ""}},
    "vestes": {{"introduction": "", "recommandes": [{{"cut_display": "", "why": ""}}], "a_eviter": [], "matieres": ""}},
    "maillot_lingerie": {{"introduction": "", "recommandes": [{{"cut_display": "", "why": ""}}], "a_eviter": [], "matieres": ""}},
    "chaussures": {{"introduction": "", "recommandes": [{{"cut_display": "", "why": ""}}], "a_eviter": [], "matieres": ""}},
    "accessoires": {{"introduction": "", "recommandes": [{{"cut_display": "", "why": ""}}], "a_eviter": [], "matieres": ""}}
  }}
}}
"""