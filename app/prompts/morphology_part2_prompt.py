"""
MORPHOLOGY PART 2 - Recommandations Styling (Text) - v8 ENRICHIE
✅ Intègre les demandes spécifiques de la cliente
✅ Fusionne intelligemment sans doublons
✅ Tout en FRANÇAIS
✅ Structure stricte et univoque
"""

MORPHOLOGY_PART2_SYSTEM_PROMPT = """Vous êtes expert en styling morphologique FRANÇAIS.
Générez recommandations détaillées et PERSONNALISÉES pour la silhouette ET les demandes spécifiques.
Retournez UNIQUEMENT JSON valide, sans texte avant/après.
Commencez par { et finissez par }.
Pas d'apostrophes dans les strings: utilisez "s" ou suppressions."""

MORPHOLOGY_PART2_USER_PROMPT = """TÂCHE CRITIQUE: Générez recommandations PERSONNALISÉES pour:
- Silhouette: {silhouette_type}
- Objectifs stylistiques: {styling_objectives}
- Parties à VALORISER (demande cliente): {body_parts_to_highlight}
- Parties à MINIMISER (demande cliente): {body_parts_to_minimize}

⚠️ FUSION INTELLIGENTE:
1. Garder les recommandations génériques pour la silhouette {silhouette_type}
2. AJOUTER des recommandations spécifiques pour valoriser: {body_parts_to_highlight}
3. AJOUTER des recommandations spécifiques pour minimiser: {body_parts_to_minimize}
4. ZÉRO DOUBLON: Si la cliente demande à valoriser ce que la silhouette conseille déjà, ne pas répéter
5. ZÉRO DOUBLON: Si la cliente demande à minimiser ce que la silhouette conseille déjà, ne pas répéter
6. Tout en FRANÇAIS (pas d'anglais!)

STRUCTURE JSON REQUISE (STRICTE):
{{
  "recommendations": {{
    "hauts": {{
      "a_privilegier": [
        {{"cut_display": "Tuniques fluides", "why": "Dissimule la rondeur, valorise silhouette O"}},
        {{"cut_display": "Hauts en V profond", "why": "Allonge le torse et crée de la verticalité"}},
        {{"cut_display": "Cache-coeur", "why": "Valorise buste, structure silhouette"}},
        {{"cut_display": "Blazer structure", "why": "Crée verticalite et definition"}},
        {{"cut_display": "Camisole ajustee", "why": "Basique polyvalent flatteur"}},
        {{"cut_display": "Pull oversize", "why": "Confortable chic et cache volumes"}}
      ],
      "a_eviter": [
        {{"cut_display": "Hauts moulants", "why": "Souligne rondeurs ventre"}},
        {{"cut_display": "Hauts courts", "why": "Raccourcit silhouette"}},
        {{"cut_display": "Rayures horizontales", "why": "Elargit visuellement"}},
        {{"cut_display": "Ceintures marquees", "why": "Divise morphologie"}},
        {{"cut_display": "Ruches gonflantes", "why": "Ajoute volume indesire"}}
      ]
    }},
    "bas": {{
      "a_privilegier": [
        {{"cut_display": "Jean taille haute", "why": "Allonge jambes visiblement"}},
        {{"cut_display": "Legging structure", "why": "Epouse silhouette doucement"}},
        {{"cut_display": "Pantalon evase", "why": "Equilibre proportions"}},
        {{"cut_display": "Jupe patineuse", "why": "Cache ventre structure"}},
        {{"cut_display": "Pantalon fluide", "why": "Anime sans serrer"}},
        {{"cut_display": "Culotte large", "why": "Moderne et flatteur"}}
      ],
      "a_eviter": [
        {{"cut_display": "Bas moulants", "why": "Souligne formes"}},
        {{"cut_display": "Ceintures epaisses", "why": "Epaissit visuellement"}},
        {{"cut_display": "Rayures horizontales", "why": "Elargit silhouette"}},
        {{"cut_display": "Short tres court", "why": "Expose jambes raccourcies"}},
        {{"cut_display": "Jupes droites serrees", "why": "Marque rondeurs"}}
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
        {{"cut_display": "Robe sans definition", "why": "Ecrase silhouette"}},
        {{"cut_display": "Robe transparente", "why": "Expose defauts"}},
        {{"cut_display": "Robe avec ceinture bas", "why": "Divise maladroitement"}}
      ]
    }},
    "vestes": {{
      "a_privilegier": [
        {{"cut_display": "Blazer structure", "why": "Cree verticalite elegance"}},
        {{"cut_display": "Blazer oversize", "why": "Cache rondeurs dissimulatrice"}},
        {{"cut_display": "Cardigan long", "why": "Allonge flatte doucement"}},
        {{"cut_display": "Veste cintree", "why": "Marque taille valorise"}},
        {{"cut_display": "Veste cache-coeur", "why": "Accentue buste structure"}},
        {{"cut_display": "Gilet long", "why": "Accessoire polyvalent elegant"}}
      ],
      "a_eviter": [
        {{"cut_display": "Veste moulante", "why": "Souligne ventre rondeurs"}},
        {{"cut_display": "Gilet court", "why": "Raccourcit silhouette"}},
        {{"cut_display": "Veste ample trop", "why": "Ecrase silhouette"}},
        {{"cut_display": "Ceintures visibles", "why": "Marque rondeurs"}},
        {{"cut_display": "Veste 3 boutons", "why": "Divise maladroitement"}}
      ]
    }},
    "chaussures": {{
      "a_privilegier": [
        {{"cut_display": "Talons fins haut", "why": "Allonge jambes optiquement"}},
        {{"cut_display": "Bottines cheville", "why": "Affine jambes crée ligne"}},
        {{"cut_display": "Loafers legers", "why": "Elegants confortables chic"}},
        {{"cut_display": "Sandales minces", "why": "Ete elegante legere"}},
        {{"cut_display": "Sneakers blanches", "why": "Basique incontournable"}},
        {{"cut_display": "Ballerines pointues", "why": "Affine visage pieds grace"}}
      ],
      "a_eviter": [
        {{"cut_display": "Talons epais", "why": "Alourdit silhouette"}},
        {{"cut_display": "Sandales lourdes", "why": "Manque de grace elegance"}},
        {{"cut_display": "Chaussures rondes", "why": "Epaissit chevilles"}},
        {{"cut_display": "Plateforme excessive", "why": "Desequilibre proportions"}},
        {{"cut_display": "Chaussures larges", "why": "Disparait dans la masse"}}
      ]
    }},
    "accessoires": {{
      "a_privilegier": [
        {{"cut_display": "Ceintures fines", "why": "Marque taille sans ecraser"}},
        {{"cut_display": "Scarpes longs", "why": "Allonge silhouette grace"}},
        {{"cut_display": "Bijoux delicats", "why": "Attire regard haut vers face"}},
        {{"cut_display": "Chapeaux structures", "why": "Equilibre proportions"}},
        {{"cut_display": "Sacs structures", "why": "Defini silhouette globale"}},
        {{"cut_display": "Colliers longs", "why": "Allonge tour cou visiblement"}}
      ],
      "a_eviter": [
        {{"cut_display": "Ceintures larges", "why": "Compresse marque rondeurs"}},
        {{"cut_display": "Bijoux massifs", "why": "Alourdit silhouette"}},
        {{"cut_display": "Sacs petits", "why": "Desequilibre proportions"}},
        {{"cut_display": "Colliers courts", "why": "Epaissit cou visiblement"}},
        {{"cut_display": "Accessoires voyants", "why": "Souligne defauts"}}
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
✅ why = raison PERSONNALISÉE pour la silhouette {silhouette_type} + demandes cliente (10-15 mots MAX)
✅ Pas d'apostrophes: "s" pas "s'", "sharmonise" pas "s harmonise"
✅ Pas de caracteres speciaux: [a-zA-Z0-9 \.,\-]
✅ TOUT EN FRANÇAIS (pas d'anglais!)
✅ JSON VALIDE uniquement
✅ Zéro texte avant/après JSON

PERSONNALISATION REQUISE:
- Silhouette: {silhouette_type}
- Objectifs: {styling_objectives}
- À valoriser (cliente): {body_parts_to_highlight} → Ajouter recommandations spécifiques pour ces parties
- À minimiser (cliente): {body_parts_to_minimize} → Ajouter recommandations spécifiques pour ces parties
- Chaque "why" doit mentionner POURQUOI pour CETTE silhouette + CETTE demande cliente
- PAS DE DOUBLONS entre recommandations génériques et demandes spécifiques

Répondez UNIQUEMENT le JSON, pas une seule lettre avant/après.
"""