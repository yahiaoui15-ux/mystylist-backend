"""
MORPHOLOGY PART 2 - Recommandations Styling (Text)
✅ Prompt ENRICHI avec exemple JSON complet
✅ Structure stricte et univoque
✅ Pas d'apostrophes problématiques
✅ Format JSON valide obligatoire
"""

MORPHOLOGY_PART2_SYSTEM_PROMPT = """Vous êtes expert en styling morphologique. 
Générez recommandations détaillées et PERSONNALISÉES.
Retournez UNIQUEMENT JSON valide, sans texte avant/après.
Commencez par { et finissez par }.
Pas d'apostrophes dans les strings: utilisez "s" ou suppressions."""

MORPHOLOGY_PART2_USER_PROMPT = """TÂCHE CRITIQUE: Générez recommandations pour silhouette: {silhouette_type}
Objectifs stylistiques: {styling_objectives}

STRUCTURE JSON REQUISE (STRICTE):
{{
  "recommendations": {{
    "hauts": {{
      "a_privilegier": [
        {{"cut_display": "Tuniques fluides", "why": "Dissimule la rondeur"}},
        {{"cut_display": "Hauts en V profond", "why": "Allonge le torse"}},
        {{"cut_display": "Cache-coeur", "why": "Valorise buste"}},
        {{"cut_display": "Blazer structure", "why": "Crée verticalite"}},
        {{"cut_display": "Camisole ajustee", "why": "Basique polyvalent"}},
        {{"cut_display": "Pull oversize", "why": "Confortable chic"}}
      ],
      "a_eviter": [
        {{"cut_display": "Hauts moulants", "why": "Souligne rondeurs"}},
        {{"cut_display": "Hauts courts", "why": "Raccourcit silhouette"}},
        {{"cut_display": "Rayures horizontales", "why": "Elargit visuellement"}},
        {{"cut_display": "Ceintures marques", "why": "Divise morphologie"}},
        {{"cut_display": "Ruches gonflantes", "why": "Ajoute volume"}}
      ]
    }},
    "bas": {{
      "a_privilegier": [
        {{"cut_display": "Jean taille haute", "why": "Allonge jambes visiblement"}},
        {{"cut_display": "Legging structure", "why": "Epouse silhouette doucement"}},
        {{"cut_display": "Pantalon evasé", "why": "Equilibre les proportions"}},
        {{"cut_display": "Jupe patineuse", "why": "Cache ventre structure"}},
        {{"cut_display": "Pantalon fluide", "why": "Anime sans serrer"}},
        {{"cut_display": "Culotte large", "why": "Moderne et flatteur"}}
      ],
      "a_eviter": [
        {{"cut_display": "Bas moulants", "why": "Souligne les formes"}},
        {{"cut_display": "Ceintures epaisses", "why": "Epaissit visiblement"}},
        {{"cut_display": "Rayures horizontales", "why": "Elargit silhouette"}},
        {{"cut_display": "Short tres court", "why": "Expose jambes raccourcies"}},
        {{"cut_display": "Jupes droites serrées", "why": "Marque rondeurs"}}
      ]
    }},
    "robes": {{
      "a_privilegier": [
        {{"cut_display": "Robe portefeuille", "why": "Ajustable tres flatteur"}},
        {{"cut_display": "Robe patineuse", "why": "Cache ventre valorise buste"}},
        {{"cut_display": "Robe cache-coeur", "why": "Accentue poitrine doucement"}},
        {{"cut_display": "Robe taille haute", "why": "Allonge jambes optiquement"}},
        {{"cut_display": "Robe fluide", "why": "Suit morphologie sans marquer"}},
        {{"cut_display": "Robe empire", "why": "Marque poitrine structure silhouette"}}
      ],
      "a_eviter": [
        {{"cut_display": "Robe moulante", "why": "Souligne rondeurs ventre"}},
        {{"cut_display": "Robe patineuse courte", "why": "Raccourcit silhouette"}},
        {{"cut_display": "Robe sans definition", "why": "Ecrase silhouette comprime"}},
        {{"cut_display": "Robe transparente", "why": "Expose defauts optiques"}},
        {{"cut_display": "Robe avec ceinture bas", "why": "Divise maladroitement"}}
      ]
    }},
    "vestes": {{
      "a_privilegier": [
        {{"cut_display": "Blazer structure", "why": "Cree verticalite elegance"}},
        {{"cut_display": "Blazer oversize", "why": "Cache rondeurs dissimulatrice"}},
        {{"cut_display": "Cardigan long", "why": "Allonge flatte doucement"}},
        {{"cut_display": "Veste cintre", "why": "Marque taille valorise"}},
        {{"cut_display": "Veste cache-coeur", "why": "Accentue buste structure"}},
        {{"cut_display": "Gilet long", "why": "Accessoire polyvalent elegant"}}
      ],
      "a_eviter": [
        {{"cut_display": "Veste moulante", "why": "Souligne ventre rondeurs"}},
        {{"cut_display": "Gilet court", "why": "Raccourcit silhouette"}},
        {{"cut_display": "Veste ample trop", "why": "Ecrase silhouette grossit"}},
        {{"cut_display": "Ceintures visibles", "why": "Marque rondeurs souligne"}},
        {{"cut_display": "Veste 3 boutons", "why": "Divise maladroitement vertical"}}
      ]
    }},
    "chaussures": {{
      "a_privilegier": [
        {{"cut_display": "Talons fins haut", "why": "Allonge jambes optiquement"}},
        {{"cut_display": "Bottines cheville", "why": "Affine jambes crée ligne"}},
        {{"cut_display": "Loafers legers", "why": "Elegants confortables chic"}},
        {{"cut_display": "Sandales minces", "why": "Ete elegante legere"}},
        {{"cut_display": "Sneakers blanches", "why": "Basique incontournable moderne"}},
        {{"cut_display": "Ballerines pointues", "why": "Affine visage pieds grace"}}
      ],
      "a_eviter": [
        {{"cut_display": "Talons epais", "why": "Alourdit silhouette visuellement"}},
        {{"cut_display": "Sandales lourdes", "why": "Manque de grace elegance"}},
        {{"cut_display": "Chaussures rondes", "why": "Epaissit chevilles pieds"}},
        {{"cut_display": "Plateforme excessive", "why": "Desequilibre proportions"}},
        {{"cut_display": "Chaussures larges", "why": "Disparait dans la masse"}}
      ]
    }},
    "accessoires": {{
      "a_privilegier": [
        {{"cut_display": "Ceintures fines", "why": "Marque taille sans ecraser"}},
        {{"cut_display": "Scarpe longs", "why": "Allonge silhouette grace"}},
        {{"cut_display": "Bijoux delicats", "why": "Attire regard haut vers face"}},
        {{"cut_display": "Chapeaux structures", "why": "Equilibre proportions visuelles"}},
        {{"cut_display": "Sacs structures", "why": "Defini silhouette globale"}},
        {{"cut_display": "Colliers longs", "why": "Allonge tour cou visiblement"}}
      ],
      "a_eviter": [
        {{"cut_display": "Ceintures larges", "why": "Compresse marque rondeurs"}},
        {{"cut_display": "Bijoux massifs", "why": "Alourdit silhouette comprime"}},
        {{"cut_display": "Sacs petits", "why": "Desequilibre proportions"}},
        {{"cut_display": "Colliers courts", "why": "Epaissit cou visiblement"}},
        {{"cut_display": "Accessoires voyants", "why": "Souligne defauts optiques"}}
      ]
    }}
  }}
}}

RÈGLES STRICTES (OBLIGATOIRES):
✅ Exactement 6 items dans a_privilegier pour CHAQUE categorie
✅ Exactement 5 items dans a_eviter pour CHAQUE categorie
✅ 6 categories: hauts, bas, robes, vestes, chaussures, accessoires
✅ Chaque item = {{"cut_display": "...", "why": "..."}}
✅ cut_display = nom du vetement/style court (3-5 mots)
✅ why = raison PERSONNALISÉE pour la silhouette {silhouette_type} (10-15 mots MAX)
✅ Pas d'apostrophes: "s" pas "s'", "sharmonise" pas "s harmonise"
✅ Pas de caracteres speciaux: [a-zA-Z0-9 \.,\-]
✅ JSON VALIDE uniquement
✅ Zéro texte avant/après JSON

CRITÈRES PERSONNALISATION:
- {silhouette_type} = silhouette du client
- {styling_objectives} = objectifs specifiques
- Chaque recommandation doit s adapter EXACTEMENT à cette silhouette
- Pas de recommandations generiques (ex: "flattering" sans raison specifique)

Répondez UNIQUEMENT le JSON, pas une seule lettre avant/après.
"""