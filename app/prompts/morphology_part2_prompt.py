"""
MORPHOLOGY PART 2 - RECOMMANDATIONS STYLING (OPTIMISÉ v12 - DESCRIPTIONS LONGUES)
✅ Descriptions `why` passées de 10-15 mots → 80-100 mots (2-3 phrases)
✅ `matieres` complètement personnalisé par silhouette (2-3 phrases)
✅ 7 catégories: hauts, bas, robes, vestes, maillot, chaussures, accessoires
✅ Tout en FRANÇAIS
✅ JSON VALIDE et COMPLET
✅ ~2500 tokens (augmenté de 1582 pour plus de contenu)
"""

MORPHOLOGY_PART2_SYSTEM_PROMPT = """Vous êtes expert styling morphologique français spécialisé en conseils détaillés.
Générez UNIQUEMENT JSON valide. Zéro texte avant/après le JSON.
Commencez par { et terminez par }.

IMPORTANT: Les descriptions `why` DOIVENT être complètes (2-3 phrases, 80-100 mots).
Les sections `matieres` DOIVENT être personnalisées et détaillées (2-3 phrases)."""

MORPHOLOGY_PART2_USER_PROMPT = """RECOMMANDATIONS STYLING DÉTAILLÉES - Silhouette {SILHOUETTE}

À valoriser: {TO_HIGHLIGHT}
À minimiser: {TO_MINIMIZE}

TÂCHE: Générez recommandations DÉTAILLÉES pour 7 catégories.
- introduction: Une phrase recommandation générale
- recommandes: 3-4 pièces avec cut_display + why COMPLET (80-100 mots, 2-3 phrases)
- a_eviter: 2-3 pièces à éviter
- matieres: 2-3 phrases PERSONNALISÉES pour {SILHOUETTE}

FORMAT JSON STRICT:
{{
  "recommendations": {{
    "hauts": {{
      "introduction": "Pour silhouette {SILHOUETTE}, privilégiez hauts qui mettent en valeur.",
      "recommandes": [
        {{
          "cut_display": "Top structuré col bateau",
          "why": "Cette coupe épouse délicatement le haut du corps sans l'élargir, ce qui crée une belle définition des épaules. Elle structure le buste naturellement et attire le regard vers le haut, ce qui aide à équilibrer les proportions si vous avez une silhouette avec hanches plus larges. Le col bateau crée une ligne horizontale qui valorise la poitrine sans ajouter du volume inutile."
        }},
        {{
          "cut_display": "Chemise cintrée ajustée",
          "why": "Cette chemise épouse les courbes du corps sans marquer ou ajouter de volume. Elle offre une structure impeccable grâce à ses coutures latérales ajustées, ce qui crée une belle définition à la taille. Pour une silhouette {SILHOUETTE}, cette définition est essentielle car elle crée un équilibre visuel en attirant l'attention vers le haut."
        }},
        {{
          "cut_display": "Pull col en V profond",
          "why": "Le col en V allonge naturellement le cou et le buste, ce qui crée une ligne verticale flatteuse pour votre silhouette. Cette coupe affine optiquement en guidant le regard vers le bas. Les manches ajustées complètent cette ligne verticale, rendant l'ensemble élégant et structuré."
        }}
      ],
      "a_eviter": [
        {{"cut": "Haut oversize", "why": "Perd la définition du corps."}},
        {{"cut": "Tunique informe", "why": "Cache la structure naturelle."}}
      ],
      "matieres": "Pour silhouette {SILHOUETTE}, privilégier les matières fluides et légèrement structurées comme la soie, le coton mélangé ou le lin qui épousent délicatement sans marquer les rondeurs. Éviter les tissus rigides (coton pur épais, polyester lourd) qui accentuent le volume. Les matières extensibles (spandex léger) offrent confort et tenue naturelle."
    }},

    "bas": {{
      "introduction": "Affinez avec des coupes qui créent la verticalité.",
      "recommandes": [
        {{
          "cut_display": "Jean taille haute skinny",
          "why": "La taille haute positionne naturellement le jean au-dessus des hanches, ce qui crée instantanément une apparence plus élancée. La coupe skinny dans les cuisses crée une ligne verticalité qui affine visuellement. Cette combinaison est particulièrement efficace pour les silhouettes avec hanches plus larges, car elle minimise l'apparence du volume du bas tout en maximisant la longueur des jambes."
        }},
        {{
          "cut_display": "Pantalon droit fluide",
          "why": "Cette coupe offre un équilibre parfait entre structure et confort. La coupe droit crée une ligne verticale continue de la taille aux chevilles, ce qui affine visuellement. Le tissu fluide ne marque pas et ne crée pas de volume inutile, tout en restant chic et intemporel. C'est le choix idéal pour équilibrer les proportions."
        }},
        {{
          "cut_display": "Jupe evasee taille haute",
          "why": "La taille haute épouse la partie fine du corps (sous les hanches) et l'évase crée du mouvement sans ajouter du volume de manière statique. Cette structure dynamique camoufle subtilement les hanches en créant des lignes diagonales flatteuses. Le mouvement du tissu rend l'ensemble plus léger et plus féminin."
        }}
      ],
      "a_eviter": [
        {{"cut": "Legging très moulant", "why": "Souligne les hanches."}},
        {{"cut": "Pantalon large", "why": "Élargit visuellement."}}
      ],
      "matieres": "Privilégier les matières fluides avec légère structure (coton mélangé, viscose, laine fine) qui ne marquent pas tout en maintenant une belle ligne. Pour silhouette {SILHOUETTE}, éviter les matières trop élastiques ou trop rigides. Les tissus doux avec un léger poids offrent la meilleure tenue et le meilleur confort."
    }},

    "robes": {{
      "introduction": "Choisissez coupes qui équilibrent haut et bas.",
      "recommandes": [
        {{
          "cut_display": "Robe cache-coeur",
          "why": "Cette coupe crée une définition nette à la taille en créant un point focal au centre du corps. Le croisement au centre marque la taille de manière flatteuse, ce qui crée instantanément une apparence plus équilibrée. Pour silhouette {SILHOUETTE}, cette définition à la taille aide à compenser la largeur des hanches en créant une proportion plus harmonieuse."
        }},
        {{
          "cut_display": "Robe portefeuille",
          "why": "La ceinture intégrée crée une définition précise à la taille, ce qui est fondamental pour équilibrer les proportions. Le croisement ajoute une dimension flatteuse sans ajouter de volume. Cette coupe offre également de la flexibilité pour ajuster le positionnement, ce qui permet d'optimiser l'ajustement pour votre morphologie spécifique."
        }},
        {{
          "cut_display": "Robe empire taille haute",
          "why": "Cette coupe rehausse la ligne de taille naturelle en la plaçant plus haut, ce qui crée instantanément une apparence plus élancée. La taille empire crée une définition au-dessus des hanches larges, ce qui minimise leur apparence visuelle. Le tissu qui tombe droit à partir de là crée une ligne verticale flatteuse."
        }}
      ],
      "a_eviter": [
        {{"cut": "Robe trop ample", "why": "Ajoute du volume partout."}},
        {{"cut": "Robe moulante hanche", "why": "Souligne les rondeurs."}}
      ],
      "matieres": "Choisir des matières qui offrent une légère structure (coton mélangé, viscose lisse, laine légère) pour maintenir une belle ligne sans marquer. Pour silhouette {SILHOUETTE}, les matières avec un léger poids aident à créer une silhouette nette et flatteuse. Éviter les tissus qui collent trop ou qui sont trop rigides."
    }},

    "vestes": {{
      "introduction": "Privilégiez coupes structurées qui créent des lignes flatteuses.",
      "recommandes": [
        {{
          "cut_display": "Blazer cintré ajusté",
          "why": "Un blazer bien cintré structure instantanément le haut du corps en créant une définition nette à la taille. Cette coupe structurée affine optiquement en guidant l'oeil vers le haut et vers le centre du corps. Pour silhouette {SILHOUETTE}, cette structure est essentielle pour créer un équilibre visuel avec le bas du corps."
        }},
        {{
          "cut_display": "Veste ajustée col pointu",
          "why": "Le col pointu crée des lignes verticales au niveau du visage et du haut du buste, ce qui affine visuellement. La coupe ajustée structure sans ajouter de volume inutile. Ces deux éléments combinés créent une silhouette nette et sophistiquée qui met en valeur le haut du corps."
        }},
        {{
          "cut_display": "Cardigan structuré ceinturé",
          "why": "Cette coupe offre la souplesse d'un cardigan avec la structure d'une veste. La ceinture crée une définition précise à la taille, ce qui aide à équilibrer les proportions. Le cardigan est parfait pour les jours où vous cherchez du confort sans sacrifier le style et la structure nécessaire."
        }}
      ],
      "a_eviter": [
        {{"cut": "Veste oversize", "why": "Perd l'effet structurant."}},
        {{"cut": "Veste cape large", "why": "Ajoute du volume inutile."}}
      ],
      "matieres": "Privilégier les matières structurantes (laine fine, coton rigide, mélanges avec polyester) qui maintiennent la forme de la veste. Pour silhouette {SILHOUETTE}, la structure du tissu est cruciale pour créer des lignes définies. Éviter les matières trop souples qui perdent leur forme."
    }},

    "maillot_lingerie": {{
      "introduction": "Choisissez coupes qui flattent votre silhouette.",
      "recommandes": [
        {{
          "cut_display": "Maillot taille haute gainant",
          "why": "La taille haute positionne le maillot pour flatter naturellement votre morphologie. Le contrôle discret aplatit et lisse sans être inconfortable. Cette coupe crée une silhouette plus harmonieuse sur la plage ou à la piscine, en minimisant subtilement le volume du bas du corps tout en restant totalement invisible."
        }},
        {{
          "cut_display": "Maillot avec détails en haut",
          "why": "Les détails (motifs, couleurs contrastantes, textures) au niveau du haut attirent l'attention vers la poitrine et le buste. Cela crée un équilibre visuel en guidant le regard vers le haut, ce qui aide à compenser la largeur des hanches. Cette stratégie de placement est subtile mais très efficace."
        }},
        {{
          "cut_display": "Soutien-gorge push-up structuré",
          "why": "Un bon soutien-gorge structuré valorise la poitrine en créant une présence au niveau du haut du buste. Cela attire naturellement le regard vers le haut, ce qui aide à équilibrer les proportions. Le confort et la confiance qu'il offre se reflètent également dans votre port général."
        }}
      ],
      "a_eviter": [
        {{"cut": "Maillot trop moulant", "why": "Marque inutilement."}},
        {{"cut": "Maillot sans structure", "why": "Manque de soutien et de définition."}}
      ],
      "matieres": "Choisir des matières avec légère compression (nylon/spandex mélange) qui offrent du soutien tout en restant confortables. Pour silhouette {SILHOUETTE}, les matières qui glissent légèrement sont idéales car elles ne marquent pas. Les matières quick-dry modernes combinent confort, durabilité et efficacité."
    }},

    "chaussures": {{
      "introduction": "Allongez la silhouette avec des talons stratégiques.",
      "recommandes": [
        {{
          "cut_display": "Talon fin 5-7cm escarpin",
          "why": "Un talon fin affine optiquement la jambe en créant une ligne délicate. La hauteur ajoute immédiatement de la longueur à votre silhouette, ce qui est particulièrement important si vous êtes plus petite. Pour silhouette {SILHOUETTE}, cette combination crée une ligne verticale continue très flatteuse."
        }},
        {{
          "cut_display": "Escarpin pointu nude",
          "why": "La forme pointue crée une ligne verticale prolongée depuis la jambe jusqu'au pied. La couleur nude crée une continuité de couleur avec votre peau, ce qui étire optiquement la ligne de la jambe. C'est un classique intemporel qui fait partie de tous les garde-robes de style."
        }},
        {{
          "cut_display": "Chaussure tonal avec peau",
          "why": "Lorsque votre chaussure correspond à votre ton de peau ou à votre tenue, cela crée une ligne verticale ininterrompue qui allonge visuellement la jambe. Cette technique simple mais puissante est l'une des plus efficaces pour paraître plus grande et plus élancée."
        }}
      ],
      "a_eviter": [
        {{"cut": "Chaussure très plate", "why": "Coupe la jambe trop bas."}},
        {{"cut": "Chaussure contrastante", "why": "Crée un contraste qui casse la ligne verticale."}}
      ],
      "matieres": "Privilégier les matières lisses et brillantes (cuir, vernis, satin) qui créent une finition épurée. Pour silhouette {SILHOUETTE}, les matières qui reflètent légèrement la lumière aident à affiner visuellement. Éviter les matières trop texturées ou opaques qui peuvent alourdir."
    }},

    "accessoires": {{
      "introduction": "Utilisez accessoires pour créer des lignes verticales.",
      "recommandes": [
        {{
          "cut_display": "Collier long sautoir",
          "why": "Un collier long crée une ligne verticale continue du cou jusqu'aux hanches, ce qui affine visuellement et allonge. Cette ligne guide le regard vers le bas de manière flatteuse, créant un équilibre visuel. Le sautoir est particulièrement efficace pour silhouette {SILHOUETTE} car il crée une continuité élégante."
        }},
        {{
          "cut_display": "Foulard léger drapé",
          "why": "Un foulard drapé crée du volume au niveau du buste de manière flatteuse et élégante. Le drapage ajoute une dimension sans être volumineux, ce qui aide à compenser la largeur des hanches. C'est également une façon facile de transformer un look en ajoutant de la sophistication."
        }},
        {{
          "cut_display": "Ceinture fine taille",
          "why": "Une ceinture fine marque délicatement la taille sans la couper visuellement. Cette accentuation crée une définition importante pour l'équilibre des proportions. Contrairement à une ceinture large, une fine ceinture affine et ajoute de la finesse à votre silhouette."
        }}
      ],
      "a_eviter": [
        {{"cut": "Collier court massif", "why": "Élargit le cou et les épaules."}},
        {{"cut": "Ceinture large", "why": "Peut couper ou ajouter du volume."}}
      ],
      "matieres": "Privilégier les matières délicates et fines (soie, lin léger, mélanges fins) qui ne surchargent pas. Pour silhouette {SILHOUETTE}, la finesse des accessoires est importante pour maintenir l'équilibre. Éviter les matières trop épaisses ou trop volumineuses."
    }}
  }}
}}

RÈGLES OBLIGATOIRES:
✅ 7 catégories EXACTEMENT: hauts, bas, robes, vestes, maillot_lingerie, chaussures, accessoires
✅ Chaque catégorie: introduction + recommandes (3-4 items) + a_eviter (2-3 items)
✅ why = 80-100 MOTS (2-3 phrases complètes) - PERSONNALISÉ pour {SILHOUETTE}
✅ matieres = 2-3 phrases (100+ mots) - PERSONNALISÉ pour {SILHOUETTE}
✅ Tout en FRANÇAIS, pas d'anglais
✅ cut_display et cut DIFFÉRENTS (display pour recommandes, simple pour a_eviter)
✅ JSON VALIDE - Zéro erreur parsing
✅ Zéro caractère spécial mal échappé
✅ Zéro texte avant/après JSON

PERSONNALISATION REQUISE:
- Silhouette: {SILHOUETTE}
- À valoriser: {TO_HIGHLIGHT}
- À minimiser: {TO_MINIMIZE}

Adaptez TOUS les `why` ET `matieres` à cette silhouette spécifique.
Les descriptions doivent être détaillées, utiles et authentiques.

Répondez UNIQUEMENT le JSON.
"""