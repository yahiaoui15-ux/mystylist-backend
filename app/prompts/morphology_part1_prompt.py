"""
MORPHOLOGY PART 1 - Silhouette + Valorisation/Minimisation (Vision)
✅ Intègre les choix de la cliente
✅ Génère les tips (astuces de coupes/bijoux/accessoires)
"""

MORPHOLOGY_PART1_SYSTEM_PROMPT = """Expert morphologie corporelle et styling. Analysez la photo + mensurations + choix client.
Retournez UNIQUEMENT JSON valide (pas d'autre texte)."""

MORPHOLOGY_PART1_USER_PROMPT = """Analysez la morphologie et généralisez les recommandations de valorisation/minimisation.

DONNÉES CLIENT:
- Photo: {body_photo_url}
- Épaules: {shoulder_circumference} cm
- Taille: {waist_circumference} cm
- Hanches: {hip_circumference} cm
- Buste: {bust_circumference} cm
- Parties à VALORISER (client): {body_parts_to_highlight}
- Parties à MINIMISER (client): {body_parts_to_minimize}

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
  "silhouette_explanation": "La silhouette A est caractérisée par... (3-4 phrases détaillées)",
  
  "highlights": {{
    "announcement": "Les parties à valoriser chez vous sont : [épaules, buste, visage, + AJOUTER LES CHOIX CLIENT: bras]",
    "explanation": "La valorisation de ces parties aide à équilibrer... (explication détaillée basée sur la morphologie)",
    "tips": [
      "Décolletés sans manches ou bretelles fines pour mettre en avant les bras",
      "Bracelets fins ou manchettes pour souligner les poignets",
      "Manches courtes ajustées qui épousent les bras",
      "T-shirts ajustés et cols ronds pour valoriser le buste"
    ]
  }},
  
  "minimizes": {{
    "announcement": "Les parties à harmoniser chez vous sont : [hanches, cuisses, + AJOUTER LES CHOIX CLIENT: jambes]",
    "explanation": "Pour la silhouette A, harmoniser le bas du corps crée une apparence... (explication détaillée)",
    "tips": [
      "Jupes et pantalons longs qui couvrent complètement les jambes",
      "Motifs discrets ou unis sur les jambes, motifs sur le haut",
      "Matières fluides et structurées qui ne marquent pas",
      "Ceintures fines qui affinent la taille sans élargir les hanches"
    ]
  }},
  
  "body_analysis": {{
    "measurements": {{
      "shoulders": 90,
      "waist": 90,
      "hips": 105
    }},
    "ratios": {{
      "waistToHips": 0.86,
      "waistToShoulders": 1.0
    }}
  }},
  
  "styling_objectives": [
    "Équilibrer les proportions entre le haut et le bas du corps",
    "Valoriser les épaules et le buste pour harmoniser avec les hanches larges",
    "Créer de la verticalité pour affiner visuellement",
    "Harmoniser les hanches sans les accentuer"
  ]
}}

REGLES STRICTES:
✅ Personnaliser highlights.announcement avec les choix client
✅ Personnaliser minimizes.announcement avec les choix client
✅ Générer 4 tips SPÉCIFIQUES pour valoriser (pièces, coupes, bijoux, accessoires)
✅ Générer 4 tips SPÉCIFIQUES pour minimiser (idem)
✅ Tips doivent être ACTIONABLES et CONCRÈTES
✅ Pas d'apostrophes dans les strings JSON
✅ JSON VALIDE uniquement
✅ ZÉRO texte avant/après JSON
✅ Adressez-vous à la cliente: 'Vos atouts', 'Pour vous'. Tips: 'Privilégiez les...' pas 'conviennent à cette silhouette'

Répondez UNIQUEMENT le JSON.
"""