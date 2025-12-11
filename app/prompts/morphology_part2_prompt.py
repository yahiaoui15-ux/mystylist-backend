"""
MORPHOLOGY PART 2 - Recommandations styling (text-based)
✅ Retourne: recommendations (hauts/bas/robes/vestes/chaussures/accessoires)
✅ Pas d'image, juste silhouette type + objectives reçus de Part 1
✅ Recommandations détaillées (~400 tokens)
"""

MORPHOLOGY_PART2_SYSTEM_PROMPT = """Expert styling morphologie. Générez recommandations de vêtements.
Retournez UNIQUEMENT JSON valide (pas d'autre texte)."""

MORPHOLOGY_PART2_USER_PROMPT = """Générez recommandations complètes pour silhouette {silhouette_type}.

SILHOUETTE: {silhouette_type}
OBJECTIFS: {styling_objectives}

Fournissez recommandations détaillées pour CHAQUE catégorie:

JSON REQUIS:
{{
  "recommendations": {{
    "hauts": {{
      "a_privilegier": [
        {{"cut_display": "Encolure en V", "why": "Allonge le cou et affine"}},
        {{"cut_display": "Manches raglan", "why": "Fluidité et légèreté"}},
        {{"cut_display": "Coupes ceinturées", "why": "Accentuent la taille"}},
        {{"cut_display": "Tuniques fluides", "why": "Épousent sans serrer"}},
        {{"cut_display": "Hauts portefeuille", "why": "Marquent taille élégamment"}},
        {{"cut_display": "Superpositions", "why": "Créent profondeur"}}
      ],
      "a_eviter": [
        {{"cut_display": "Col roulé serré", "why": "Écrase le cou"}},
        {{"cut_display": "Polos stretch ajustés", "why": "Accentuent détails"}},
        {{"cut_display": "Volumes au buste", "why": "Élargissent"}},
        {{"cut_display": "Matières rigides", "why": "Figent silhouette"}},
        {{"cut_display": "Rayures horizontales", "why": "Élargissent"}}
      ]
    }},
    
    "bas": {{
      "a_privilegier": [
        {{"cut_display": "Tailles hautes", "why": "Allongent jambes"}},
        {{"cut_display": "Coupes droites", "why": "Épousent légèrement"}},
        {{"cut_display": "Jupes crayon", "why": "Marquent taille"}},
        {{"cut_display": "Longueurs midi", "why": "Allongent silhouette"}},
        {{"cut_display": "Rayures verticales", "why": "Allongent visuellement"}},
        {{"cut_display": "Matières fluides", "why": "Flattent formes"}}
      ],
      "a_eviter": [
        {{"cut_display": "Tailles basses", "why": "Raccourcissent jambes"}},
        {{"cut_display": "Baggy hanches", "why": "Ajoutent volume"}},
        {{"cut_display": "Moulant excessif", "why": "Accentuent détails"}},
        {{"cut_display": "Ceintures larges", "why": "Écrasent"}},
        {{"cut_display": "Rayures horizontales", "why": "Élargissent"}}
      ]
    }},
    
    "robes": {{
      "a_privilegier": [
        {{"cut_display": "Robes portefeuille", "why": "Marquent taille"}},
        {{"cut_display": "Ceintures intégrées", "why": "Structurent"}},
        {{"cut_display": "Longueurs midi/cheville", "why": "Allongent"}},
        {{"cut_display": "Encolures en V", "why": "Allongent buste"}},
        {{"cut_display": "Matières fluides", "why": "Flattent"}},
        {{"cut_display": "Cache-cœur", "why": "Valorisent"}}
      ],
      "a_eviter": [
        {{"cut_display": "Robes amples", "why": "Ajoutent volume"}},
        {{"cut_display": "Sans définition", "why": "Aplatissent"}},
        {{"cut_display": "Longueurs courtes", "why": "Raccourcissent"}},
        {{"cut_display": "Col roulé serré", "why": "Écrase"}}
      ]
    }},
    
    "vestes": {{
      "a_privilegier": [
        {{"cut_display": "Vestes cintrées", "why": "Marquent taille"}},
        {{"cut_display": "Ceintures intégrées", "why": "Structurent"}},
        {{"cut_display": "Longueurs à taille", "why": "Allongent proportions"}},
        {{"cut_display": "Épaulettes subtiles", "why": "Harmonisent"}},
        {{"cut_display": "Manteaux fluides", "why": "Créent élégance"}},
        {{"cut_display": "Coutures verticales", "why": "Allongent"}}
      ],
      "a_eviter": [
        {{"cut_display": "Vestes amples", "why": "Ajoutent volume"}},
        {{"cut_display": "Hanches mal", "why": "Accentuent"}},
        {{"cut_display": "Ceintures larges", "why": "Écrasent"}},
        {{"cut_display": "Épaulettes excessives", "why": "Élargissent"}},
        {{"cut_display": "Matières rigides", "why": "Figent"}}
      ]
    }},
    
    "chaussures": {{
      "a_privilegier": [
        {{"cut_display": "Talons fins", "why": "Affinent chevilles"}},
        {{"cut_display": "Escarpins pointus", "why": "Allongent"}},
        {{"cut_display": "Bottines talon", "why": "Structurent"}},
        {{"cut_display": "Teintes proches peau", "why": "Allongent jambes"}},
        {{"cut_display": "Détails verticaux", "why": "Affinent"}},
        {{"cut_display": "Matières nobles", "why": "Créent élégance"}}
      ],
      "a_eviter": [
        {{"cut_display": "Plates larges", "why": "Raccourcissent"}},
        {{"cut_display": "Bottines molles", "why": "Élargissent"}},
        {{"cut_display": "Arrondies larges", "why": "Épaississent"}},
        {{"cut_display": "Sandales échancrées", "why": "Raccourcissent"}},
        {{"cut_display": "Matières molles", "why": "Déforment"}}
      ]
    }},
    
    "accessoires": {{
      "a_privilegier": [
        {{"cut_display": "Ceintures fines/moyennes", "why": "Définissent taille"}},
        {{"cut_display": "Sacs taille moyenne", "why": "Équilibrent"}},
        {{"cut_display": "Bijoux verticaux", "why": "Allongent"}},
        {{"cut_display": "Foulards longs", "why": "Créent verticalité"}},
        {{"cut_display": "Capes légères", "why": "Épurent"}},
        {{"cut_display": "Accessoires qualité", "why": "Valorisent"}}
      ],
      "a_eviter": [
        {{"cut_display": "Ceintures larges", "why": "Écrasent"}},
        {{"cut_display": "Sacs volumineux", "why": "Alourdissent"}},
        {{"cut_display": "Bijoux lourds", "why": "Écrasent"}},
        {{"cut_display": "Foulards courts", "why": "Élargissent"}},
        {{"cut_display": "Surcharge", "why": "Perturbe équilibre"}}
      ]
    }}
  }}
}}

RÈGLES:
✅ Recommandations adaptées à silhouette {silhouette_type}
✅ Chaque catégorie: a_privilegier (6 items) + a_eviter (5 items)
✅ Chaque item: cut_display + why (raison courte)
✅ Personnalisé aux objectifs reçus

Répondez UNIQUEMENT le JSON.
"""