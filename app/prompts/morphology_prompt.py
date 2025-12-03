"""
MORPHOLOGY PROMPT - VERSION COMPLÈTE
Retourne JSON enrichi avec toutes les 7 catégories vestimentaires
Pour Pages 8-15 du rapport
"""

MORPHOLOGY_SYSTEM_PROMPT = """Vous êtes une experte en morphologie corporelle et en styling professionnel.
Analysez la photo et les mensurations fourties, puis retournez UNIQUEMENT du JSON valide.
Pas d'autres texte avant ou après les accolades JSON.
Soyez précise, bienveillante et actionnable dans vos recommandations."""

MORPHOLOGY_USER_PROMPT = """Analysez la morphologie de la cliente et fournissez des recommandations détaillées pour les vêtements.

DONNÉES:
- Photo: {body_photo_url}
- Épaules: {shoulder_circumference} cm
- Taille: {waist_circumference} cm
- Hanches: {hip_circumference} cm

SILHOUETTES: O (ronde), H (rectangle), A (poire), V (inverse), X (sablier), 8 (figure entière)

RETOURNEZ UNIQUEMENT CE JSON VALIDE (pas de texte avant ou après):
{{
  "silhouette_type": "O ou H ou A ou V ou X ou 8",
  
  "silhouette_explanation": "Description détaillée de 2-3 phrases expliquant sa silhouette, ses proportions, ses caractéristiques. Soyez bienveillante et valorisante.",
  
  "body_analysis": {{
    "shoulder_width": "{shoulder_circumference}",
    "waist": "{waist_circumference}",
    "hips": "{hip_circumference}",
    "waist_hip_ratio": nombre entre 0.6 et 1.0,
    "body_description": "Description très courte (1-2 phrases) de la silhouette"
  }},
  
  "styling_objectives": [
    "Objectif 1 (créer verticalité, allonger, harmoniser, etc.)",
    "Objectif 2",
    "Objectif 3",
    "Objectif 4 si applicable"
  ],
  
  "recommendations": {{
    "hauts": {{
      "a_privilegier": [
        {{
          "cut": "encolure_en_v",
          "cut_display": "Encolure en V",
          "why": "Explication courte (1 phrase) du bénéfice pour sa morphologie"
        }},
        {{
          "cut": "manches_raglan",
          "cut_display": "Manches raglan ou kimono",
          "why": "Explication"
        }},
        {{
          "cut": "coupes_ceinturees",
          "cut_display": "Coupes ceinturées",
          "why": "Explication"
        }},
        {{
          "cut": "hauts_portefeuille",
          "cut_display": "Hauts portefeuille",
          "why": "Explication"
        }},
        {{
          "cut": "tuniques_fluides",
          "cut_display": "Tuniques fluides",
          "why": "Explication"
        }},
        {{
          "cut": "couches_superpositions",
          "cut_display": "Couches et superpositions",
          "why": "Explication"
        }}
      ],
      "a_eviter": [
        {{
          "cut": "col_roule_serre",
          "cut_display": "Col roulé très serré",
          "why": "Explication courte"
        }},
        {{
          "cut": "polos_stretch",
          "cut_display": "Polos stretch très ajustés",
          "why": "Explication"
        }},
        {{
          "cut": "volumes_buste",
          "cut_display": "Volumes excessifs au buste",
          "why": "Explication"
        }},
        {{
          "cut": "matieres_rigides",
          "cut_display": "Matières rigides",
          "why": "Explication"
        }},
        {{
          "cut": "rayures_horizontales",
          "cut_display": "Rayures horizontales larges",
          "why": "Explication"
        }}
      ]
    }},
    
    "bas": {{
      "a_privilegier": [
        {{
          "cut": "tailles_hautes",
          "cut_display": "Tailles hautes",
          "why": "Allongent les jambes et structurent"
        }},
        {{
          "cut": "coupes_droites",
          "cut_display": "Coupes droites ou évasées",
          "why": "Épousent légèrement sans serrer"
        }},
        {{
          "cut": "jupes_crayon",
          "cut_display": "Jupes crayon ou portefeuille",
          "why": "Marquent la taille et créent de la définition"
        }},
        {{
          "cut": "longueurs_midi",
          "cut_display": "Longueurs midi ou cheville",
          "why": "Allongent les jambes"
        }},
        {{
          "cut": "rayures_verticales",
          "cut_display": "Rayures verticales subtiles",
          "why": "Créent une illusion d'allongement"
        }},
        {{
          "cut": "matieres_fluides",
          "cut_display": "Matières fluides",
          "why": "Bougent naturellement et flattent"
        }}
      ],
      "a_eviter": [
        {{
          "cut": "tailles_basses",
          "cut_display": "Tailles basses",
          "why": "Raccourcissent les jambes"
        }},
        {{
          "cut": "baggy_hanches",
          "cut_display": "Baggy ou sursize",
          "why": "Ajoutent du volume"
        }},
        {{
          "cut": "moulant_excessif",
          "cut_display": "Moulant excessif",
          "why": "Accentue chaque détail"
        }},
        {{
          "cut": "ceintures_larges",
          "cut_display": "Ceintures très larges",
          "why": "Écrasent la taille"
        }},
        {{
          "cut": "rayures_horizontales",
          "cut_display": "Rayures horizontales",
          "why": "Élargissent visuellement"
        }}
      ]
    }},
    
    "robes": {{
      "a_privilegier": [
        {{
          "cut": "robes_portefeuille",
          "cut_display": "Robes portefeuille",
          "why": "Marquent la taille naturellement"
        }},
        {{
          "cut": "ceintures_integrees",
          "cut_display": "Ceintures intégrées",
          "why": "Définissent sans ajouter de volume"
        }},
        {{
          "cut": "longueurs_midi_cheville",
          "cut_display": "Longueurs midi à cheville",
          "why": "Allongent et créent de la fluidité"
        }},
        {{
          "cut": "encolures_v",
          "cut_display": "Encolures en V ou cache-cœur",
          "why": "Allongent le buste et le cou"
        }},
        {{
          "cut": "matieres_fluides",
          "cut_display": "Matières fluides",
          "why": "Bougent naturellement"
        }},
        {{
          "cut": "robes_cache_coeur",
          "cut_display": "Robes cache-cœur",
          "why": "Marquent la taille avec féminité"
        }}
      ],
      "a_eviter": [
        {{
          "cut": "robes_amples",
          "cut_display": "Robes trop amples",
          "why": "Ajoutent du volume"
        }},
        {{
          "cut": "ceintures_larges",
          "cut_display": "Ceintures trop larges non-intégrées",
          "why": "Peuvent écraser"
        }},
        {{
          "cut": "coupes_droites",
          "cut_display": "Coupes droites sans définition",
          "why": "N'épousent pas assez"
        }},
        {{
          "cut": "longueurs_courtes",
          "cut_display": "Longueurs courtes",
          "why": "Raccourcissent les jambes"
        }},
        {{
          "cut": "col_roule",
          "cut_display": "Col roulé très serré",
          "why": "Écrase le cou"
        }}
      ]
    }},
    
    "vestes": {{
      "a_privilegier": [
        {{
          "cut": "vestes_cintrees",
          "cut_display": "Vestes cintrées",
          "why": "Marquent la taille et structurent"
        }},
        {{
          "cut": "ceintures_integrees",
          "cut_display": "Ceintures intégrées",
          "why": "Structurent sans ajouter de volume"
        }},
        {{
          "cut": "longueurs_taille",
          "cut_display": "Longueurs arrivant à la taille",
          "why": "Allongent et définissent"
        }},
        {{
          "cut": "epaulettes_subtiles",
          "cut_display": "Épaulettes subtiles",
          "why": "Harmonisent sans surcharger"
        }},
        {{
          "cut": "manteaux_fluides",
          "cut_display": "Manteaux fluides",
          "why": "Créent de l'élégance"
        }},
        {{
          "cut": "coutures_verticales",
          "cut_display": "Coutures verticales",
          "why": "Créent des lignes allongeantes"
        }}
      ],
      "a_eviter": [
        {{
          "cut": "vestes_amples",
          "cut_display": "Vestes trop amples",
          "why": "Ajoutent du volume"
        }},
        {{
          "cut": "longueurs_hanches",
          "cut_display": "Longueurs aux hanches",
          "why": "Accentuent le volume"
        }},
        {{
          "cut": "ceintures_larges",
          "cut_display": "Ceintures très larges",
          "why": "Peuvent écraser"
        }},
        {{
          "cut": "epaulettes_excessives",
          "cut_display": "Épaulettes excessives",
          "why": "Élargissent trop"
        }},
        {{
          "cut": "matieres_rigides",
          "cut_display": "Matières trop rigides",
          "why": "Figent la silhouette"
        }}
      ]
    }},
    
    "maillot_lingerie": {{
      "a_privilegier": [
        {{
          "cut": "soutiens_gorge_structurants",
          "cut_display": "Soutiens-gorge structurants",
          "why": "Créent une belle forme"
        }},
        {{
          "cut": "maillots_motifs_buste",
          "cut_display": "Maillots avec motifs au buste",
          "why": "Valorisent et créent du relief"
        }},
        {{
          "cut": "ceintures_gaines",
          "cut_display": "Gaines douces",
          "why": "Lissent légèrement"
        }},
        {{
          "cut": "matieres_stretch",
          "cut_display": "Matières stretch confortables",
          "why": "Épousent naturellement"
        }},
        {{
          "cut": "coupes_cache_coeur",
          "cut_display": "Coupes cache-cœur",
          "why": "Flattent et créent de la féminité"
        }},
        {{
          "cut": "lanieres_verticales",
          "cut_display": "Lanières verticales",
          "why": "Créent une illusion d'allongement"
        }}
      ],
      "a_eviter": [
        {{
          "cut": "soutiens_gorge_serres",
          "cut_display": "Soutiens-gorge trop serrés",
          "why": "Créent de l'inconfort"
        }},
        {{
          "cut": "matieres_rigides",
          "cut_display": "Matières rigides",
          "why": "Ne s'adaptent pas"
        }},
        {{
          "cut": "maillots_amples",
          "cut_display": "Maillots trop amples",
          "why": "Ajoutent du volume"
        }},
        {{
          "cut": "coutures_mal_placees",
          "cut_display": "Coutures mal placées",
          "why": "Peuvent marquer"
        }},
        {{
          "cut": "doublures_insuffisantes",
          "cut_display": "Doublures insuffisantes",
          "why": "Manquent de confort"
        }}
      ]
    }},
    
    "chaussures": {{
      "a_privilegier": [
        {{
          "cut": "talon_fin",
          "cut_display": "Chaussures à talon fin",
          "why": "Affinent la cheville et allongent"
        }},
        {{
          "cut": "escarpins_pointes",
          "cut_display": "Escarpins pointus",
          "why": "Créent une ligne allongée"
        }},
        {{
          "cut": "bottines_talon",
          "cut_display": "Bottines à talon",
          "why": "Allongent les jambes"
        }},
        {{
          "cut": "teintes_peau",
          "cut_display": "Teintes proches de la peau",
          "why": "Allongent visuellement"
        }},
        {{
          "cut": "details_verticaux",
          "cut_display": "Détails verticaux",
          "why": "Créent une ligne qui affine"
        }},
        {{
          "cut": "matieres_nobles",
          "cut_display": "Matières nobles (cuir, daim)",
          "why": "Créent une ligne nette"
        }}
      ],
      "a_eviter": [
        {{
          "cut": "chaussures_plates_larges",
          "cut_display": "Chaussures plates et larges",
          "why": "Raccourcissent les jambes"
        }},
        {{
          "cut": "bottines_molles",
          "cut_display": "Bottines trop molles",
          "why": "Élargissent les chevilles"
        }},
        {{
          "cut": "chaussures_arrondies",
          "cut_display": "Chaussures arrondies trop larges",
          "why": "Épaississent les pieds"
        }},
        {{
          "cut": "sandales_echancrees",
          "cut_display": "Sandales très échancrées",
          "why": "Peuvent raccourcir"
        }},
        {{
          "cut": "matieres_molles",
          "cut_display": "Matières molles",
          "why": "S'affaissent"
        }}
      ]
    }},
    
    "accessoires": {{
      "a_privilegier": [
        {{
          "cut": "ceintures_fines",
          "cut_display": "Ceintures fines ou moyennes",
          "why": "Définissent sans ajouter de volume"
        }},
        {{
          "cut": "sacs_taille_moyenne",
          "cut_display": "Sacs de taille moyenne",
          "why": "Créent de l'équilibre"
        }},
        {{
          "cut": "bijoux_verticaux",
          "cut_display": "Bijoux verticaux (colliers longs)",
          "why": "Allongent le cou et le buste"
        }},
        {{
          "cut": "foulards_port_long",
          "cut_display": "Foulards (port long)",
          "why": "Créent de la verticalité"
        }},
        {{
          "cut": "capes_legeres",
          "cut_display": "Capes légères",
          "why": "Créent des lignes épurées"
        }},
        {{
          "cut": "accessoires_discrets",
          "cut_display": "Accessoires discrets de qualité",
          "why": "Valorisent sans surcharger"
        }}
      ],
      "a_eviter": [
        {{
          "cut": "ceintures_larges",
          "cut_display": "Ceintures très larges",
          "why": "Écrasent plutôt que définissent"
        }},
        {{
          "cut": "sacs_volumineux",
          "cut_display": "Sacs trop volumineux",
          "why": "Ajoutent du poids visuel"
        }},
        {{
          "cut": "bijoux_lourds",
          "cut_display": "Bijoux trop lourds",
          "why": "Écrasent le haut du corps"
        }},
        {{
          "cut": "foulards_court",
          "cut_display": "Foulards port court",
          "why": "Élargissent le cou"
        }},
        {{
          "cut": "surcharge_accessoires",
          "cut_display": "Surcharge d'accessoires",
          "why": "Perturbent l'équilibre"
        }}
      ]
    }}
  }},
  
  "instant_tips": [
    "Conseil immédiatement actionnable 1",
    "Conseil immédiatement actionnable 2",
    "Conseil immédiatement actionnable 3"
  ]
}}
"""