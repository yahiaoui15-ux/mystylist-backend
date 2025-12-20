"""
MORPHOLOGY PART 2 - RECOMMANDATIONS STYLING (OPTIMISÉ v11)
✅ Prompt DRASTIQUEMENT réduit (7244 tokens → ~3000)
✅ 7 catégories: hauts, bas, robes, vestes, maillot, chaussures, accessoires
✅ Chaque catégorie: introduction + recommandes (3-4 items) + a_eviter (2-3 items)
✅ Tout en FRANÇAIS
✅ JSON VALIDE et COMPLET
"""

MORPHOLOGY_PART2_SYSTEM_PROMPT = """Vous êtes expert styling morphologique. Générez UNIQUEMENT JSON valide.
Zéro texte avant/après le JSON. Commencez par { et terminez par }."""

MORPHOLOGY_PART2_USER_PROMPT_TEMPLATE = """RECOMMANDATIONS STYLING - Silhouette {SILHOUETTE}

À valoriser: {TO_HIGHLIGHT}
À minimiser: {TO_MINIMIZE}

TÂCHE: Générez recommandations pour 7 catégories.
- introduction: Une phrase recommandation générale
- recommandes: 3-4 pièces avec cut_display + why court (1 phrase max)
- a_eviter: 2-3 pièces à éviter

FORMAT JSON STRICT:
{{
  "recommendations": {{
    "hauts": {{
      "introduction": "Pour silhouette {SILHOUETTE}, privilégiez hauts structurés qui valorisent.",
      "recommandes": [
        {{"cut_display": "Haut structuré col bateau", "why": "Définit les épaules sans les élargir."}},
        {{"cut_display": "Chemise ajustée", "why": "Structure la silhouette avec fluidité."}},
        {{"cut_display": "Pull col en V", "why": "Allonge le buste naturellement."}}
      ],
      "a_eviter": [
        {{"cut": "Haut oversize", "why": "Perd les proportions."}},
        {{"cut": "Tunique informe", "why": "Cache le haut du corps."}}
      ]
    }},

    "bas": {{
      "introduction": "Affinez avec des coupes qui créent la verticalité.",
      "recommandes": [
        {{"cut_display": "Jean taille haute", "why": "Allonge les jambes immédiatement."}},
        {{"cut_display": "Pantalon droit fluide", "why": "Équilibre les hanches sans moulant."}},
        {{"cut_display": "Jupe évasée", "why": "Camoufle subtilement en créant du mouvement."}}
      ],
      "a_eviter": [
        {{"cut": "Legging très moulant", "why": "Souligne les hanches."}},
        {{"cut": "Pantalon large", "why": "Élargit visuellement."}}
      ]
    }},

    "robes": {{
      "introduction": "Choisissez coupes qui équilibrent haut et bas.",
      "recommandes": [
        {{"cut_display": "Robe cache-cœur", "why": "Met en valeur le buste et affine optiquement."}},
        {{"cut_display": "Robe portefeuille", "why": "Crée de la définition à la taille."}},
        {{"cut_display": "Robe empire", "why": "Rehausse la poitrine et crée de la verticalité."}}
      ],
      "a_eviter": [
        {{"cut": "Robe trop ample", "why": "Ajoute du volume partout."}},
        {{"cut": "Robe moulante hanche", "why": "Souligne les rondeurs."}}
      ]
    }},

    "vestes": {{
      "introduction": "Privilégiez coupes structurées qui créent des lignes flatteuses.",
      "recommandes": [
        {{"cut_display": "Blazer cintrée", "why": "Structure et affine instantanément."}},
        {{"cut_display": "Veste ajustée col pointu", "why": "Crée des lignes verticales flatteuses."}},
        {{"cut_display": "Cardigan structuré", "why": "Ajoute de la profondeur au haut du corps."}}
      ],
      "a_eviter": [
        {{"cut": "Veste oversize", "why": "Perd l'effet structurant."}},
        {{"cut": "Veste croisée volumineux", "why": "Ajoute du volume inutile."}}
      ]
    }},

    "maillot_lingerie": {{
      "introduction": "Choisissez coupes qui flattent votre silhouette.",
      "recommandes": [
        {{"cut_display": "Maillot taille haute soutenant", "why": "Aplatit le ventre et allonge les jambes."}},
        {{"cut_display": "Maillot avec détails en haut", "why": "Attire l'attention vers le haut du corps."}},
        {{"cut_display": "Soutien-gorge push-up", "why": "Valorise la poitrine et crée du relief."}}
      ],
      "a_eviter": [
        {{"cut": "Maillot trop moulant", "why": "Marque inutilement."}},
        {{"cut": "Maillot sans structure", "why": "Manque de soutien."}}
      ]
    }},

    "chaussures": {{
      "introduction": "Allongez la silhouette avec des talons stratégiques.",
      "recommandes": [
        {{"cut_display": "Talon fin (5-7cm)", "why": "Affine la jambe immédiatement."}},
        {{"cut_display": "Escarpin pointu", "why": "Crée une ligne verticale flatteuse."}},
        {{"cut_display": "Chaussure tonal avec peau", "why": "Allonge visuellement la jambe."}}
      ],
      "a_eviter": [
        {{"cut": "Chaussure très plate", "why": "Coupe la jambe trop bas."}},
        {{"cut": "Chaussure trop claire/foncée", "why": "Crée un contraste qui casse la ligne."}}
      ]
    }},

    "accessoires": {{
      "introduction": "Utilisez accessoires pour créer des lignes verticales.",
      "recommandes": [
        {{"cut_display": "Collier long", "why": "Crée une ligne verticale qui affine."}},
        {{"cut_display": "Foulard drapé", "why": "Ajoute de la profondeur au buste."}},
        {{"cut_display": "Ceinture fine taille", "why": "Définit et flatte la silhouette."}}
      ],
      "a_eviter": [
        {{"cut": "Collier court massif", "why": "Élargit le cou et les épaules."}},
        {{"cut": "Ceinture large", "why": "Peut couper ou ajouter du volume."}}
      ]
    }}
  }}
}}

RÈGLES OBLIGATOIRES:
✅ 7 catégories EXACTEMENT: hauts, bas, robes, vestes, maillot_lingerie, chaussures, accessoires
✅ Chaque catégorie: introduction + recommandes (3-4 items) + a_eviter (2-3 items)
✅ why = 1 phrase COURTE max (10-15 mots)
✅ Tout en FRANÇAIS, pas d'anglais
✅ cut_display et cut DIFFÉRENTS (display pour recommandes, simple pour a_eviter)
✅ JSON VALIDE - Zéro erreur parsing
✅ Zéro caractère spécial mal échappé (apostrophes simples seulement!)
✅ Zéro texte avant/après JSON

PERSONNALISATION:
- Silhouette: {SILHOUETTE}
- À valoriser: {TO_HIGHLIGHT}
- À minimiser: {TO_MINIMIZE}

Adaptez TOUS les "why" à cette silhouette spécifique. Pas de générique!

Répondez UNIQUEMENT le JSON.
"""