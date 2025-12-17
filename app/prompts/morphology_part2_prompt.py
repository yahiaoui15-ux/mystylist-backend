"""
MORPHOLOGY PART 2 - ULTRA SIMPLE - Zéro caractères spéciaux
✅ Pas d'apostrophes, d'accents dans les strings JSON
✅ Texte simplifié et lisible
✅ JSON guaranteed valid
"""

MORPHOLOGY_PART2_SYSTEM_PROMPT = """Vous etes expert en styling morphologique FRANCAIS.
Generez recommandations de vetements pour 7 categories.
Chaque categorie: introduction courte (1 phrase) + pieces recommandees (6) + a eviter (5).
Retournez UNIQUEMENT JSON valide, sans texte avant/apres."""

MORPHOLOGY_PART2_USER_PROMPT = """TACHE: Generez recommandations de VETEMENTS pour silhouette {silhouette_type}.

Objectifs: {styling_objectives}
A valoriser: {body_parts_to_highlight}
A minimiser: {body_parts_to_minimize}

STRUCTURE JSON REQUISE (STRICTE - 7 CATEGORIES):
{{
  "recommendations": {{
    "hauts": {{
      "introduction": "Pour votre silhouette {silhouette_type}, privilegiez des hauts structures.",
      "recommandes": [
        {{"cut_display": "Haut structure", "why": "Cree de la verticalite et du volume"}},
        {{"cut_display": "Encolure en V", "why": "Allonge le buste naturellement"}},
        {{"cut_display": "Camisole ajustee", "why": "Epouse doucement sans serrer"}},
        {{"cut_display": "Blazer ceinture", "why": "Marque la taille et structure"}},
        {{"cut_display": "Pull fluide", "why": "Cree de la fluidite et du mouvement"}},
        {{"cut_display": "Top cache-coeur", "why": "Valorise le buste et la taille"}}
      ],
      "a_eviter": [
        {{"cut_display": "Haut trop moulant", "why": "Souligne les formes trop"}},
        {{"cut_display": "Col roulé serré", "why": "Ecrase le cou et buste"}},
        {{"cut_display": "Rayures horizontales", "why": "Elargit visuellement"}},
        {{"cut_display": "Volumes excessifs", "why": "Ajoute du poids"}},
        {{"cut_display": "Manches bouffantes", "why": "Desequilibre proportions"}}
      ]
    }},

    "bas": {{
      "introduction": "Pour votre silhouette {silhouette_type}, privilegiez taille haute.",
      "recommandes": [
        {{"cut_display": "Jean taille haute", "why": "Allonge les jambes"}},
        {{"cut_display": "Pantalon structure", "why": "Cree une belle ligne"}},
        {{"cut_display": "Jupe patineuse", "why": "Cache et structure"}},
        {{"cut_display": "Legging structure", "why": "Epouse doucement"}},
        {{"cut_display": "Pantalon evasé", "why": "Equilibre les proportions"}},
        {{"cut_display": "Culotte large", "why": "Moderne et flatteur"}}
      ],
      "a_eviter": [
        {{"cut_display": "Taille basse", "why": "Raccourcit les jambes"}},
        {{"cut_display": "Baggy excessif", "why": "Ajoute du volume"}},
        {{"cut_display": "Rayures horizontales", "why": "Elargit visuellement"}},
        {{"cut_display": "Ceinture epaisse", "why": "Epaissit visuellement"}},
        {{"cut_display": "Jupes tres serrees", "why": "Marque trop les courbes"}}
      ]
    }},

    "robes": {{
      "introduction": "Pour votre silhouette {silhouette_type}, privilegiez portefeuille.",
      "recommandes": [
        {{"cut_display": "Robe portefeuille", "why": "Marque la taille"}},
        {{"cut_display": "Robe cache-coeur", "why": "Valorise le buste"}},
        {{"cut_display": "Robe ceinturee", "why": "Definit les proportions"}},
        {{"cut_display": "Encolure en V", "why": "Allonge le buste"}},
        {{"cut_display": "Longueur midi", "why": "Allonge les jambes"}},
        {{"cut_display": "Matieres fluides", "why": "Cree du mouvement"}}
      ],
      "a_eviter": [
        {{"cut_display": "Robe trop ample", "why": "Ajoute du volume"}},
        {{"cut_display": "Robe moulante", "why": "Souligne trop"}},
        {{"cut_display": "Longueur courte", "why": "Raccourcit les jambes"}},
        {{"cut_display": "Coupes droites", "why": "Ne suit pas silhouette"}},
        {{"cut_display": "Col roulé", "why": "Ecrase le cou"}}
      ]
    }},

    "vestes": {{
      "introduction": "Pour votre silhouette {silhouette_type}, privilegiez structures.",
      "recommandes": [
        {{"cut_display": "Veste cintree", "why": "Marque la taille"}},
        {{"cut_display": "Blazer ceinture", "why": "Structure elegamment"}},
        {{"cut_display": "Veste fluide", "why": "Cree du mouvement"}},
        {{"cut_display": "Longueur taille", "why": "Allonge les proportions"}},
        {{"cut_display": "Manteau structure", "why": "Cree de la verticalité"}},
        {{"cut_display": "Gilet long", "why": "Allonge elegamment"}}
      ],
      "a_eviter": [
        {{"cut_display": "Veste trop ample", "why": "Ajoute du volume"}},
        {{"cut_display": "Longueur hanches", "why": "Accentue le volume"}},
        {{"cut_display": "Epaulettes excessives", "why": "Elargit trop"}},
        {{"cut_display": "Matieres rigides", "why": "Figent la silhouette"}},
        {{"cut_display": "Coutures asymetriques", "why": "Crée du desequilibre"}}
      ]
    }},

    "maillot_lingerie": {{
      "introduction": "Pour votre silhouette {silhouette_type}, confort essentiel.",
      "recommandes": [
        {{"cut_display": "Soutien-gorge structure", "why": "Cree une belle forme"}},
        {{"cut_display": "Maillot cache-coeur", "why": "Flatteuse et feminine"}},
        {{"cut_display": "Ceinture gaine douce", "why": "Lisse delicatement"}},
        {{"cut_display": "Matieres stretch", "why": "Epouser naturellement"}},
        {{"cut_display": "Lanières verticales", "why": "Allongent visuellement"}},
        {{"cut_display": "Coupes adaptees", "why": "Confortables et flatteuses"}}
      ],
      "a_eviter": [
        {{"cut_display": "Trop serre", "why": "Cree inconfort"}},
        {{"cut_display": "Matieres rigides", "why": "Peu adaptees au corps"}},
        {{"cut_display": "Trop ample", "why": "Ajoute du volume"}},
        {{"cut_display": "Coutures visibles", "why": "Peut marquer"}},
        {{"cut_display": "Elastiques epais", "why": "Trop visibles"}}
      ]
    }},

    "chaussures": {{
      "introduction": "Pour votre silhouette {silhouette_type}, talons fins ideal.",
      "recommandes": [
        {{"cut_display": "Talon fin haut", "why": "Affine la cheville"}},
        {{"cut_display": "Escarpin pointe", "why": "Allonge les jambes"}},
        {{"cut_display": "Bottine talon", "why": "Allonge et structure"}},
        {{"cut_display": "Couleur peau", "why": "Allonge visuellement"}},
        {{"cut_display": "Matière noble", "why": "Crée une belle ligne"}},
        {{"cut_display": "Details verticaux", "why": "Affine visuellement"}}
      ],
      "a_eviter": [
        {{"cut_display": "Plates larges", "why": "Raccourcit les jambes"}},
        {{"cut_display": "Bottines molles", "why": "Elargit les chevilles"}},
        {{"cut_display": "Arrondies larges", "why": "Epaissit les pieds"}},
        {{"cut_display": "Sandales decoupees", "why": "Peut raccourcir"}},
        {{"cut_display": "Matieres molles", "why": "Se deforment"}}
      ]
    }},

    "accessoires": {{
      "introduction": "Pour votre silhouette {silhouette_type}, discrets elegants.",
      "recommandes": [
        {{"cut_display": "Ceinture fine", "why": "Marque la taille"}},
        {{"cut_display": "Sacs taille moyenne", "why": "Cree de l'equilibre"}},
        {{"cut_display": "Bijoux verticaux", "why": "Allongent le buste"}},
        {{"cut_display": "Foulard long", "why": "Cree de la verticalite"}},
        {{"cut_display": "Cape legère", "why": "Crée des lignes épurées"}},
        {{"cut_display": "Details discrets", "why": "Raffinent le look"}}
      ],
      "a_eviter": [
        {{"cut_display": "Ceintures larges", "why": "Ecrasent la taille"}},
        {{"cut_display": "Sacs volumineux", "why": "Ajoutent du poids"}},
        {{"cut_display": "Bijoux lourds", "why": "Ecrasent le haut"}},
        {{"cut_display": "Foulards courts", "why": "Elargissent le cou"}},
        {{"cut_display": "Surcharge", "why": "Desequilibre l'ensemble"}}
      ]
    }}
  }}
}}

REGLES STRICTES (OBLIGATOIRES):
✅ EXACTEMENT 6 items recommandes par categorie
✅ EXACTEMENT 5 items a_eviter par categorie
✅ 7 categories EXACTEMENT
✅ introduction = 1 phrase courte (15-20 mots MAX)
✅ Chaque item = {{"cut_display": "...", "why": "..."}}
✅ "why" = MAX 15 mots
✅ AUCUN accent, apostrophe, tiret dans les strings JSON
✅ Remplacer: é=e, è=e, ê=e, à=a, ù=u, ç=c, etc.
✅ JSON VALIDE uniquement
✅ Zero texte avant/apres JSON

PERSONNALISATION REQUISE:
- Silhouette: {silhouette_type}
- Objectifs: {styling_objectives}

Repondez UNIQUEMENT le JSON, pas une seule lettre avant/apres.
"""