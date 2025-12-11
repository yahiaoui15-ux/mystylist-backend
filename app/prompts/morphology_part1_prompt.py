"""
MORPHOLOGY PART 1 - Analyse silhouette avec VISION
✅ Retourne: silhouette_type, silhouette_explanation, body_parts_to_highlight/minimize
✅ Utilise photo du corps
✅ Petit output (~200 tokens)
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

⚠️ TRANCHEZ! UNE SEULE silhouette, pas deux!

JSON REQUIS:
{{
  "silhouette_type": "O" ou "H" ou "A" ou "V" ou "X" ou "8",
  
  "silhouette_explanation": "3-4 phrases bienveillantes et valorisantes. Mentionnez: poitrine, hanches, ventre, épaules, taille, jambes. Exemple: 'Tu as une magnifique morphologie en O avec des courbes harmonieuses. Tes épaules, taille et hanches sont équilibrés, créant une silhouette douce et féminine. Ton buste généreux et tes hanches arrondies sont des atouts naturels. Tes jambes sont jolies et proportionnées.'",
  
  "body_parts_to_highlight": [
    "décrivez 3 parties à valoriser (ex: 'poitrine généreuse', 'taille fine', 'jambes longues')"
  ],
  
  "body_parts_to_minimize": [
    "décrivez 2-3 parties à minimiser (ex: 'hanches', 'ventre', 'bras')"
  ],
  
  "body_analysis": {{
    "shoulder_circumference": {shoulder_circumference},
    "waist_circumference": {waist_circumference},
    "hip_circumference": {hip_circumference},
    "bust_circumference": {bust_circumference},
    "waist_hip_ratio": calculé précisément,
    "short_description": "1 phrase description rapide silhouette"
  }},
  
  "styling_objectives": [
    "Objectif 1 (ex: créer de la verticalité)",
    "Objectif 2 (ex: allonger les jambes)",
    "Objectif 3 (ex: marquer la taille)",
    "Objectif 4 si applicable"
  ]
}}

RÈGLES:
✅ UNE SEULE silhouette (tranchez si doute)
✅ Explications bienveillantes et détaillées
✅ Body parts spécifiques et personnalisés
✅ Styling objectives = 3-4 actions concrètes
✅ JSON valide complet

Répondez UNIQUEMENT le JSON.
"""