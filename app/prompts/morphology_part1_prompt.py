"""
MORPHOLOGY PART 1 - Silhouette & Body Parts Enrichis (Vision) - v10 ENRICHI
✅ Silhouette type (1 seule)
✅ Body parts highlights + explanation (SANS strategies - ça c'est Part 2)
✅ Body parts minimizes + explanation
✅ Styling objectives
✅ Body analysis avec ratios
✅ Tout en FRANÇAIS
"""

MORPHOLOGY_PART1_SYSTEM_PROMPT = """Expert morphologie corporelle FRANÇAIS.
Analysez la photo + mensurations pour identifier:
1. LA SEULE silhouette (O/H/A/V/X/8)
2. Les parties à valoriser avec ANNONCE + EXPLICATION
3. Les parties à minimiser avec ANNONCE + EXPLICATION
4. Objectifs de styling
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

STRUCTURE JSON REQUISE (STRICTE):
{{
  "silhouette_type": "A",
  "silhouette_explanation": "La silhouette A est caractérisée par... (3-4 phrases expliquant pourquoi ce choix basé sur les mesures et la photo)",
  
  "body_parts_to_highlight": ["épaules", "buste", "visage"],
  "body_parts_to_minimize": ["hanches", "cuisses"],
  
  ✅ NOUVEAU - BODY PARTS ENRICHIS (ANNOUNCEMENT + EXPLANATION):
  "body_parts_highlights": {{
    "announcement": "Les parties à valoriser chez vous sont: épaules, buste et visage",
    "explanation": "Ces parties ont été identifiées car votre silhouette A a des épaules plus étroites que les hanches - les valoriser crée un équilibre. Le buste est un atout naturel à mettre en avant, et le visage mérite d'être mis en valeur. Valoriser ces zones crée de l'harmonie et amplifie vos meilleurs traits."
  }},
  
  "body_parts_minimizes": {{
    "announcement": "Les parties à harmoniser chez vous sont: hanches et cuisses",
    "explanation": "Votre silhouette A a des hanches et cuisses plus larges que le haut du corps - c'est naturel pour cette morphologie. L'objectif n'est pas de les cacher mais de les harmoniser avec le reste. Grâce à des coupes et matières stratégiques, on peut créer de la verticalité et de l'équilibre sans marquer ces zones."
  }},
  
  "styling_objectives": [
    "Équilibrer les proportions entre haut et bas du corps",
    "Valoriser les épaules et le buste",
    "Créer de la verticalité pour affiner visuellement",
    "Harmoniser les hanches sans les accentuer"
  ],
  
  "body_analysis": {{
    "measurements": {{
      "shoulders": {shoulder_circumference},
      "waist": {waist_circumference},
      "hips": {hip_circumference},
      "bust": {bust_circumference}
    }},
    "ratios": {{
      "waistToHips": "ratio taille/hanches (ex: 0.86)",
      "waistToShoulders": "ratio taille/épaules (ex: 1.0)"
    }},
    "analysis": "Description détaillée de la morphologie observée sur la photo et justification de la silhouette (2-3 phrases)"
  }}
}}

RÈGLES STRICTES (OBLIGATOIRES):
✅ body_parts_highlights AVEC announcement (une phrase courte) + explanation (2-3 phrases)
✅ body_parts_minimizes AVEC announcement + explanation
✅ announcement: Phrase simple annonçant les parties (ex: "Les parties à valoriser chez vous sont: bras, poitrine, décolletés")
✅ explanation: Pourquoi ces parties + bénéfices (basé sur silhouette + morphologie visuelle)
✅ body_parts_to_highlight: Array de 2-3 strings (noms des parties)
✅ body_parts_to_minimize: Array de 2-3 strings (noms des parties)
✅ styling_objectives: Array de 3-4 strings (objectifs généraux)
✅ TOUT EN FRANÇAIS (pas d'anglais!)
✅ JSON VALIDE uniquement
✅ Zéro texte avant/après JSON

NOTES IMPORTANTES:
- L'explanation doit être PERSONNALISÉE basée sur la PHOTO et les MESURES fournies
- Ne pas générer de strategies détaillées (ça vient en Part 2)
- Justifier chaque partie par la silhouette ET l'observation visuelle
- Les ratios doivent être calculés: taille/hanches, taille/épaules, etc.

Répondez UNIQUEMENT le JSON, pas une seule lettre avant/après.
"""