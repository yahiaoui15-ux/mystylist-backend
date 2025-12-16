"""
MORPHOLOGY PART 2 - Recommandations Styling Enrichies (Text) - v9 ENRICHI
✅ Contenu en 3 PARTIES: Annoncer, Pourquoi, Comment
✅ Intègre demandes spécifiques de la cliente
✅ Fusion intelligente sans doublons
✅ Tout en FRANÇAIS
✅ Structure stricte et univoque
"""

MORPHOLOGY_PART2_SYSTEM_PROMPT = """Vous êtes expert en styling morphologique FRANÇAIS.
Générez recommandations détaillées et PERSONNALISÉES pour la silhouette ET les demandes spécifiques.
IMPORTANT: Enrichissez les blocs "body_parts_highlights" et "body_parts_minimizes" avec:
1. Annonce des parties (quelles parties du corps)
2. Explication (POURQUOI ces parties - basé sur morpho + demandes cliente)
3. Stratégies (COMMENT les valoriser/minimiser)
Retournez UNIQUEMENT JSON valide, sans texte avant/après."""

MORPHOLOGY_PART2_USER_PROMPT = """TÂCHE CRITIQUE: Générez recommandations ENRICHIES pour:
- Silhouette: {silhouette_type}
- Objectifs stylistiques: {styling_objectives}
- Parties à VALORISER (demande cliente): {body_parts_to_highlight}
- Parties à MINIMISER (demande cliente): {body_parts_to_minimize}

STRUCTURE JSON REQUISE (STRICTE):
{{
  "body_parts_highlights": {{
    "announcement": "Les parties à valoriser chez vous sont: bras, poitrine, et décolletés",
    "explanation": "Ces parties ont été identifiées car les bras sont fins et gracieux (silhouette {silhouette_type}), la poitrine est un atout à mettre en valeur, et vous l'avez spécifiquement demandé dans vos préférences. Valoriser ces zones crée de l'harmonie et amplifie vos meilleurs traits.",
    "strategies": [
      "Portez des hauts avec encolure en V profond pour allonger et valoriser le décolleté",
      "Choisissez des camisoles et débardeurs ajustés qui épousent délicatement les bras",
      "Optez pour des manches courtes ou sans manches pour mettre les bras en avant",
      "Privilégiez des matières fluides qui drapent légèrement au niveau de la poitrine",
      "Utilisez des détails comme des fronces ou des nœuds au niveau du buste pour attirer l'attention",
      "Portez des ceintures qui marquent la taille et créent de la proportion"
    ]
  }},

  "body_parts_minimizes": {{
    "announcement": "Les parties à harmoniser chez vous sont: ventre et hanches",
    "explanation": "Votre silhouette {silhouette_type} a des rondeurs naturelles au niveau du ventre et des hanches. Vous souhaitez les harmoniser, ce qui est parfaitement possible grâce à des coupes et matières stratégiques. L'objectif est de créer de la verticalité et de la fluidité sans marquer ces zones.",
    "strategies": [
      "Portez des robes portefeuille qui marquent la taille et cachent le ventre",
      "Choisissez des hauts qui ne suivent pas exactement les courbes: matières fluides, tuniques amples",
      "Préférez des pantalons et jupes taille haute qui allongent les jambes et structurent",
      "Utilisez des coupes évasées ou patineuses au niveau des hanches",
      "Optez pour des rayures VERTICALES qui créent une illusion d'allongement",
      "Évitez les matières rigides ou brillantes au niveau du ventre: couleurs sombres et mates"
    ]
  }},

  "recommendations": {{
    "hauts": {{
      "introduction": "Pour votre silhouette {silhouette_type}, les hauts doivent créer de la verticalité et époucer légèrement. Privilégiez les encolures en V et les matières fluides.",
      "recommandes": [
        {{"cut_display": "Tuniques fluides", "why": "Dissimule les rondeurs et crée de la fluidité"}},
        {{"cut_display": "Hauts en V profond", "why": "Allonge le torse et valorise le décolleté"}},
        {{"cut_display": "Cache-coeur", "why": "Marque la taille et valorise la poitrine"}},
        {{"cut_display": "Blazer structure", "why": "Crée verticalité et definition"}},
        {{"cut_display": "Camisole ajustee", "why": "Basique polyvalent flatteur"}},
        {{"cut_display": "Pull oversize", "why": "Confortable chic et cache volumes"}}
      ],
      "a_eviter": [
        {{"cut_display": "Hauts moulants", "why": "Souligne rondeurs ventre"}},
        {{"cut_display": "Hauts courts", "why": "Raccourcit silhouette"}},
        {{"cut_display": "Rayures horizontales", "why": "Elargit visuellement"}},
        {{"cut_display": "Ceintures marquees", "why": "Divise morphologie"}},
        {{"cut_display": "Ruches gonflantes", "why": "Ajoute volume indesire"}}
      ],
      "matieres": "Privilégier les matières fluides (soie, coton peigné, lin mélangé, jersey fin) qui épousent sans serrer. Les mailles structurantes de bonne qualité créent une belle verticalité. Éviter le denim rigide, la toile épaisse et les tissus qui marquent trop.",
      "motifs": {{
        "recommandes": "Rayures verticales, losanges verticaux, petits motifs discrets, dégradés, détails au niveau de l'encolure ou des épaules",
        "a_eviter": "Rayures horizontales, gros motifs répétitifs, pois, carreaux, imprimés trop volumineux au centre"
      }},
      "pieges": [
        "Ourlets qui coupent la silhouette à la mauvaise hauteur (casser la verticalité)",
        "Encolures asymétriques qui perturbent l'équilibre",
        "Nœuds ou fronces au niveau du buste qui accentuent",
        "Bandes stretch trop visibles qui marquent",
        "Matières brillantes au mauvais endroit (à éviter au centre)",
        "Coutures épaisses qui cassent les lignes",
        "Ceintures trop larges qui écrasent plutôt que définissent"
      ]
    }},

    "bas": {{
      "introduction": "Pour votre silhouette {silhouette_type}, les bas doivent allonger les jambes et créer une transition fluide. Privilégiez les tailles hautes et les coupes qui épousent légèrement.",
      "recommandes": [
        {{"cut_display": "Jean taille haute", "why": "Allonge les jambes visiblement"}},
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
      ],
      "matieres": "Privilégier les matières fluides et élastiques (coton stretch, lin mélangé, jersey) qui épousent légèrement. Éviter le denim trop rigide. Les matières mats valorisent plus que les brillants.",
      "motifs": {{
        "recommandes": "Rayures verticales, motifs discrets, petits imprimés, dégradés unis, placement horizontal au niveau des chevilles",
        "a_eviter": "Rayures horizontales, gros motifs répétitifs, pois, carreaux volumineux, imprimés trop clairs qui élargissent"
      }},
      "pieges": [
        "Longueur qui coupe la jambe à la mauvaise hauteur",
        "Ourlets trop courts qui cassent les proportions",
        "Poches trop voluminuses qui élargissent les hanches",
        "Ceintures trop serrées qui marquent",
        "Zip ou fermetures mal placées qui accentuent",
        "Matières trop épaisses au niveau des hanches",
        "Braguette ou surpiqûres qui accentuent"
      ]
    }},

    "robes": {{
      "introduction": "Pour votre silhouette {silhouette_type}, les robes doivent époucer légèrement et marquer la taille. Privilégiez les coupes portefeuille et les ceintures qui définissent.",
      "recommandes": [
        {{"cut_display": "Robe portefeuille", "why": "Marque la taille et s'adapte à tous"}},
        {{"cut_display": "Ceintures intégrées", "why": "Définissent la taille et équilibrent"}},
        {{"cut_display": "Longueurs midi à cheville", "why": "Allongent et créent fluidité"}},
        {{"cut_display": "Encolures en V", "why": "Allongent le buste et le cou"}},
        {{"cut_display": "Matières fluides", "why": "Bougent naturellement et flattent"}},
        {{"cut_display": "Robes cache-coeur", "why": "Marquent la taille et valorisent buste"}}
      ],
      "a_eviter": [
        {{"cut_display": "Robes trop amples", "why": "Ajoutent du volume"}},
        {{"cut_display": "Ceintures trop larges", "why": "Peuvent écraser plutôt que définir"}},
        {{"cut_display": "Coupes droites", "why": "N'épousent pas assez"}},
        {{"cut_display": "Longueurs courtes", "why": "Raccourcissent les jambes"}},
        {{"cut_display": "Col roulé très serré", "why": "Écrase le cou et le buste"}}
      ],
      "matieres": "Privilégier les matières fluides structurantes (soie, crêpe, coton peigné) qui épousent sans serrer. Éviter les matières trop rigides.",
      "motifs": {{
        "recommandes": "Rayures verticales, motifs discrets, petits imprimés géométriques, dégradés, détails au niveau de la taille",
        "a_eviter": "Rayures horizontales, gros motifs centrés au buste, pois volumineux, carreaux qui élargissent"
      }},
      "pieges": [
        "Ourlet qui coupe la jambe à la mauvaise hauteur",
        "Trop de volume au buste",
        "Ceintures mal positionnées",
        "Matières brillantes qui soulignent les zones à harmoniser",
        "Fermetures éclair ou détails qui accentuent",
        "Encolures trop hautes",
        "Longueurs qui figent plutôt que créer fluidité"
      ]
    }},

    "vestes": {{
      "introduction": "Pour votre silhouette {silhouette_type}, les vestes doivent structurer et créer de la verticalité. Privilégiez les coupes ajustées avec ceinture ou détails qui définissent.",
      "recommandes": [
        {{"cut_display": "Vestes cintrées", "why": "Marquent la taille et créent definition"}},
        {{"cut_display": "Ceintures intégrées", "why": "Structurent sans ajouter volume"}},
        {{"cut_display": "Longueurs à la taille", "why": "Allongent et définissent"}},
        {{"cut_display": "Épaulettes subtiles", "why": "Harmonisent les épaules"}},
        {{"cut_display": "Manteaux fluides", "why": "Bougent naturellement"}},
        {{"cut_display": "Coutures verticales", "why": "Créent des lignes qui allongent"}}
      ],
      "a_eviter": [
        {{"cut_display": "Vestes trop amples", "why": "Ajoutent du volume"}},
        {{"cut_display": "Longueurs aux hanches", "why": "Accentuent le volume"}},
        {{"cut_display": "Ceintures très larges", "why": "Peuvent écraser"}},
        {{"cut_display": "Épaulettes excessives", "why": "Élargissent les épaules"}},
        {{"cut_display": "Matières trop rigides", "why": "Figent la silhouette"}}
      ],
      "matieres": "Privilégier les matières semi-rigides (laine, lin, coton structurant) qui tiennent bien. Les matières fluides avec doublure créent une belle ligne.",
      "motifs": {{
        "recommandes": "Rayures verticales subtiles, motifs discrets, uni de qualité, petits carreaux fins",
        "a_eviter": "Rayures horizontales, gros carreaux, motifs volumineux, imprimés qui élargissent"
      }},
      "pieges": [
        "Longueur qui coupe mal le corps",
        "Fermeture ou boutonnage mal aligné",
        "Poches trop voluminuses",
        "Ceintures mal positionnées",
        "Épaulettes trop marquées",
        "Doublure qui montre et ajoute volume",
        "Coutures asymétriques"
      ]
    }},

    "maillot_lingerie": {{
      "introduction": "Pour votre silhouette {silhouette_type}, confort et confiance sont essentiels. Choisissez des coupes et soutiens adaptés qui vous mettent en valeur.",
      "recommandes": [
        {{"cut_display": "Soutiens-gorge structurants", "why": "Créent une belle forme et du confort"}},
        {{"cut_display": "Maillots avec motifs buste", "why": "Valorisent et créent du relief"}},
        {{"cut_display": "Ceintures gaines douces", "why": "Lissent légèrement sans comprimer"}},
        {{"cut_display": "Matières stretch confortables", "why": "Épousent naturellement"}},
        {{"cut_display": "Coupes cache-coeur", "why": "Flattent et créent féminité"}},
        {{"cut_display": "Lanières verticales", "why": "Créent illusion d'allongement"}}
      ],
      "a_eviter": [
        {{"cut_display": "Soutiens-gorge trop serrés", "why": "Créent inconfort et marques"}},
        {{"cut_display": "Matières rigides", "why": "Ne s'adaptent pas à votre corps"}},
        {{"cut_display": "Maillots trop amples", "why": "Ajoutent du volume"}},
        {{"cut_display": "Coutures mal placées", "why": "Peuvent marquer ou gonflements"}}
      ],
      "matieres": "Privilégier les matières stretch de qualité (coton bio, microfibre, nylon). Les doublures douces et ceintures gaines discrètes offrent confort et confiance.",
      "motifs": {{
        "recommandes": "Rayures verticales, petits motifs, dégradés, uni de qualité, motifs au niveau du buste",
        "a_eviter": "Rayures horizontales, gros motifs au centre, couleurs trop claires au niveau du buste"
      }},
      "pieges": [
        "Soutiens-gorge mal calibrés",
        "Matières qui glissent ou se déplacent",
        "Coutures épaisses qui marquent",
        "Doublures insuffisantes",
        "Élastiques trop serrés",
        "Gaines qui compriment excessivement",
        "Motifs mal placés"
      ]
    }},

    "chaussures": {{
      "introduction": "Pour votre silhouette {silhouette_type}, les chaussures affinent ou élargissent. Choisissez les formes qui allongent et créent élégance.",
      "recommandes": [
        {{"cut_display": "Talons fins haut", "why": "Affinent la cheville et allongent jambes"}},
        {{"cut_display": "Escarpins pointus", "why": "Créent une ligne allongée et élégante"}},
        {{"cut_display": "Bottines à talon", "why": "Allongent et structurent"}},
        {{"cut_display": "Chaussures teintes peau", "why": "Allongent visuellement les jambes"}},
        {{"cut_display": "Détails verticaux", "why": "Créent une ligne qui affine"}},
        {{"cut_display": "Matières nobles", "why": "Créent ligne nette et éclat"}}
      ],
      "a_eviter": [
        {{"cut_display": "Chaussures plates larges", "why": "Raccourcissent les jambes"}},
        {{"cut_display": "Bottines trop molles", "why": "Élargissent les chevilles"}},
        {{"cut_display": "Chaussures arrondies", "why": "Épaississent les pieds"}},
        {{"cut_display": "Sandales très échancrées", "why": "Peuvent raccourcir la jambe"}},
        {{"cut_display": "Matières molles", "why": "Déforment et perdent allure"}}
      ],
      "matieres": "Privilégier les matières nobles (cuir, daim, matières brillantes) qui reflètent lumière et créent ligne nette. Éviter les matières molles qui s'affaissent.",
      "motifs": {{
        "recommandes": "Couleurs unies, finitions brillantes, matières qui reflètent",
        "a_eviter": "Matières trop épaisses, couleurs très contrastées, surcharges de détails"
      }},
      "pieges": [
        "Talons trop bas ou nuls",
        "Largeur mal adaptée à vos pieds",
        "Hauteur de tige qui coupe mal la jambe",
        "Matières qui se déforment",
        "Couleurs qui tranchent trop",
        "Semelles visibles mal alignées",
        "Détails qui élargissent"
      ]
    }},

    "accessoires": {{
      "introduction": "Pour votre silhouette {silhouette_type}, les accessoires finissent la tenue avec élégance. Privilégiez les pièces qui créent verticalité et proportion.",
      "recommandes": [
        {{"cut_display": "Ceintures fines", "why": "Marquent taille sans ajouter volume"}},
        {{"cut_display": "Sacs taille moyenne", "why": "Créent équilibre sans poids visuel"}},
        {{"cut_display": "Bijoux verticaux", "why": "Allongent le cou et buste"}},
        {{"cut_display": "Foulards longs", "why": "Créent verticalité et fluidité"}},
        {{"cut_display": "Capes légères", "why": "Créent lignes épurées et élégantes"}},
        {{"cut_display": "Accessoires discrets", "why": "Valorisent sans surcharger"}}
      ],
      "a_eviter": [
        {{"cut_display": "Ceintures très larges", "why": "Écrasent plutôt que définissent"}},
        {{"cut_display": "Sacs volumineux", "why": "Ajoutent poids visuel"}},
        {{"cut_display": "Bijoux trop lourds", "why": "Écrasent le haut du corps"}},
        {{"cut_display": "Foulards courts", "why": "Élargissent le cou"}},
        {{"cut_display": "Surcharge accessoires", "why": "Perturbent l'équilibre"}}
      ],
      "matieres": "Privilégier les matières nobles (cuir, soie, matières brillantes) qui reflètent l'élégance. Les finitions douces et textures qualitatives créent effet raffiné.",
      "motifs": {{
        "recommandes": "Motifs discrets, couleurs uni de qualité, rayures verticales subtiles, géométries fines",
        "a_eviter": "Motifs volumineux, couleurs trop criardes, surcharges de détails, motifs qui élargissent"
      }},
      "pieges": [
        "Ceintures mal positionnées",
        "Sacs qui pèsent trop lourd d'un côté",
        "Bijoux mal proportionnés",
        "Foulards qui rétrécissent",
        "Accessoires de mauvaise qualité",
        "Surcharge d'accessoires",
        "Matières brillantes mal placées"
      ]
    }}
  }}
}}

RÈGLES STRICTES (OBLIGATOIRES):
✅ body_parts_highlights et body_parts_minimizes avec announcement + explanation + strategies
✅ Exactement 6 items dans a_privilegier pour CHAQUE categorie
✅ Exactement 5 items dans a_eviter pour CHAQUE categorie
✅ 7 categories: hauts, bas, robes, vestes, maillot_lingerie, chaussures, accessoires
✅ Chaque item = {{"cut_display": "...", "why": "..."}}
✅ TOUT EN FRANÇAIS (pas d'anglais!)
✅ JSON VALIDE uniquement
✅ Zéro texte avant/après JSON

PERSONNALISATION REQUISE:
- Silhouette: {silhouette_type}
- Objectifs: {styling_objectives}
- À valoriser (cliente): {body_parts_to_highlight} → Annoncer, expliquer, stratégies
- À minimiser (cliente): {body_parts_to_minimize} → Annoncer, expliquer, stratégies

Répondez UNIQUEMENT le JSON, pas une seule lettre avant/après.
"""