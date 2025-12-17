"""
MORPHOLOGY PART 2 - OPTIMIZED - 4 recommandes + 2 a_eviter
✅ 28 items total (4 × 7 + 2 × 7)
✅ ~2000 tokens garanti
✅ Bon équilibre contenu/tokens
"""

MORPHOLOGY_PART2_SYSTEM_PROMPT = """Vous etes expert en styling morphologique.
Generez recommandations vetements pour 7 categories.
Retournez UNIQUEMENT JSON valide, sans texte avant/apres."""

MORPHOLOGY_PART2_USER_PROMPT = """TACHE: Generez recommandations vetements pour silhouette {silhouette_type}.

STRUCTURE JSON REQUISE (STRICTE):
{{
  "recommendations": {{
    "hauts": {{
      "introduction": "Pour silhouette {silhouette_type}, choisissez hauts structures.",
      "recommandes": [
        {{"cut_display": "Haut structure", "why": "Cree volume et verticalite"}},
        {{"cut_display": "Encolure V", "why": "Allonge le buste"}},
        {{"cut_display": "Camisole ajustee", "why": "Epouse sans serrer"}},
        {{"cut_display": "Blazer ceinture", "why": "Marque la taille"}}
      ],
      "a_eviter": [
        {{"cut_display": "Haut moulant", "why": "Souligne les formes"}},
        {{"cut_display": "Rayures horiz", "why": "Elargit visuellement"}}
      ]
    }},
    
    "bas": {{
      "introduction": "Pour silhouette {silhouette_type}, privilegiez taille haute.",
      "recommandes": [
        {{"cut_display": "Jean taille haute", "why": "Allonge jambes"}},
        {{"cut_display": "Pantalon structure", "why": "Cree belle ligne"}},
        {{"cut_display": "Jupe patineuse", "why": "Cache et structure"}},
        {{"cut_display": "Pantalon evasé", "why": "Equilibre proportions"}}
      ],
      "a_eviter": [
        {{"cut_display": "Taille basse", "why": "Raccourcit jambes"}},
        {{"cut_display": "Baggy excessif", "why": "Ajoute volume"}}
      ]
    }},
    
    "robes": {{
      "introduction": "Pour silhouette {silhouette_type}, robes creent proportions.",
      "recommandes": [
        {{"cut_display": "Robe portefeuille", "why": "Marque la taille"}},
        {{"cut_display": "Robe ceinturee", "why": "Definit proportions"}},
        {{"cut_display": "Robe cache-coeur", "why": "Valorise le buste"}},
        {{"cut_display": "Encolure V", "why": "Allonge le buste"}}
      ],
      "a_eviter": [
        {{"cut_display": "Robe ample", "why": "Ajoute volume"}},
        {{"cut_display": "Robe moulante", "why": "Souligne trop"}}
      ]
    }},
    
    "vestes": {{
      "introduction": "Pour silhouette {silhouette_type}, vestes structurent.",
      "recommandes": [
        {{"cut_display": "Veste cintree", "why": "Marque taille"}},
        {{"cut_display": "Blazer structure", "why": "Cree verticalite"}},
        {{"cut_display": "Veste fluide", "why": "Cree mouvement"}},
        {{"cut_display": "Longueur taille", "why": "Allonge proportions"}}
      ],
      "a_eviter": [
        {{"cut_display": "Veste ample", "why": "Ajoute volume"}},
        {{"cut_display": "Epaulettes larges", "why": "Elargit trop"}}
      ]
    }},
    
    "maillot_lingerie": {{
      "introduction": "Pour silhouette {silhouette_type}, confort essentiel.",
      "recommandes": [
        {{"cut_display": "Soutien-gorge structure", "why": "Cree belle forme"}},
        {{"cut_display": "Maillot cache-coeur", "why": "Flatteuse et fem"}},
        {{"cut_display": "Ceinture gaine douce", "why": "Lisse delicatement"}},
        {{"cut_display": "Matieres stretch", "why": "Epouser naturellement"}}
      ],
      "a_eviter": [
        {{"cut_display": "Trop serre", "why": "Inconfortable"}},
        {{"cut_display": "Trop ample", "why": "Ajoute volume"}}
      ]
    }},
    
    "chaussures": {{
      "introduction": "Pour silhouette {silhouette_type}, talons fins ideaux.",
      "recommandes": [
        {{"cut_display": "Talon fin haut", "why": "Affine cheville"}},
        {{"cut_display": "Escarpin pointe", "why": "Allonge jambes"}},
        {{"cut_display": "Bottine talon", "why": "Allonge et structure"}},
        {{"cut_display": "Couleur peau", "why": "Allonge visuellement"}}
      ],
      "a_eviter": [
        {{"cut_display": "Plates larges", "why": "Raccourcit jambes"}},
        {{"cut_display": "Bottines molles", "why": "Elargit chevilles"}}
      ]
    }},
    
    "accessoires": {{
      "introduction": "Pour silhouette {silhouette_type}, discrets elegants.",
      "recommandes": [
        {{"cut_display": "Ceinture fine", "why": "Marque taille"}},
        {{"cut_display": "Bijoux verticaux", "why": "Allongent buste"}},
        {{"cut_display": "Foulard long", "why": "Cree verticalite"}},
        {{"cut_display": "Details discrets", "why": "Raffinent look"}}
      ],
      "a_eviter": [
        {{"cut_display": "Ceintures larges", "why": "Ecrasent taille"}},
        {{"cut_display": "Sacs volumineux", "why": "Ajoutent poids"}}
      ]
    }}
  }}
}}

REGLES STRICTES:
✅ EXACTEMENT 4 recommandes par categorie
✅ EXACTEMENT 2 a_eviter par categorie
✅ 7 categories EXACTEMENT
✅ introduction courte (10-15 mots)
✅ "why" = MAX 8 mots
✅ AUCUN accent, apostrophe dans JSON
✅ JSON VALIDE uniquement
✅ Zero texte avant/apres JSON

Repondez UNIQUEMENT le JSON.
"""