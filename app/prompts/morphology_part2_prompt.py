"""
MORPHOLOGY PART 2 - VERSION ENRICHIE - 3000 TOKENS
✅ Contenu détaillé et chaleureux comme une vraie styliste
✅ 6 recommandes + 2 a_eviter + matieres + motifs + pieges
✅ ~3000 tokens garanti
✅ Conseils détaillés 2-3 phrases par item
"""

MORPHOLOGY_PART2_SYSTEM_PROMPT = """Tu es une styliste experte en morphologie avec 15 ans d'expérience.
Tu donnes des conseils détaillés, chaleureux et professionnels.
Chaque recommandation doit être un vrai conseil comme tu l'expliquerais à une cliente en face à face.
Tu expliques le POURQUOI derrière chaque recommandation.
Retourne UNIQUEMENT du JSON valide, sans texte avant ou après."""

MORPHOLOGY_PART2_USER_PROMPT = """TACHE: Génère des recommandations vêtements détaillées et chaleureuses pour silhouette {silhouette_type}.

INSTRUCTIONS IMPORTANTES:
- Chaque "why" doit être 2-3 phrases complètes (50-80 mots)
- Explique le POURQUOI et pas juste le QUOI
- Utilise un ton chaleureux, bienveillant, expert
- Tous les conseils doivent être adaptés spécifiquement à la silhouette {silhouette_type}
- Ajoute des sections matieres, motifs, pieges pour chaque catégorie
- Les "pieges" doivent lister 3-5 erreurs communes à éviter absolument
- Aucun accent ou apostrophe bizarre dans le JSON

STRUCTURE JSON REQUISE (STRICTE):
{{
  "recommendations": {{
    "hauts": {{
      "introduction": "Pour silhouette {silhouette_type}, choisissez hauts structures qui valorisent vos atouts.",
      "recommandes": [
        {{"cut_display": "Haut structure avec definition", "why": "Les hauts structurés avec un peu de définition sont parfaits pour votre silhouette car ils créent une belle ligne sans être trop moulants. Ils épousent vos formes de manière flatteuse tout en maintenant une élégance intemporelle. C'est l'allié parfait pour un look quotidien qui vous met en valeur sans effort."}},
        {{"cut_display": "Encolure V ou Sweetheart", "why": "Une encolure en V ou Sweetheart allonge naturellement votre buste et crée une verticalité très flatteuse. Ce détail simple mais puissant capte le regard vers le haut et affine visuellement l'ensemble du buste. C'est une pièce incontournable pour paraître plus élancée instantanément."}},
        {{"cut_display": "Camisole ajustée en soie", "why": "Une camisole bien ajustée mais pas moulante en tissu noble comme la soie apporte une sophistication immédiate. Ce type de pièce crée une belle ligne tout en restant confortable et polyvalente. Parfait pour des looks stratifiés ou porté seul pour un style minimaliste et chic."}},
        {{"cut_display": "Blazer ou Veste cintrée", "why": "Un blazer bien cintré à la taille est votre meilleur ami car il crée une structure élégante et marque vos formes de manière flatteuse. Il ajoute de la verticalité et de l'impact immédiatement à n'importe quelle tenue. C'est une pièce d'investissement qui élève chaque look."}},
        {{"cut_display": "Pull fin avec texture", "why": "Un pull fin avec une belle texture crée du relief intéressant sans ajouter de volume. Le tricot apporte une touche chaleureuse et sophistiquée à vos tenues. Privilégiez les pulls avec des détails comme des côtes verticales ou des torsades pour créer de la verticalité."}},
        {{"cut_display": "Chemise ajustée cintrée", "why": "Une chemise bien cintrée crée une silhouette impeccable et professionnelle. Le coton ou la soie apportent une elegance naturelle et la structure du tissu valorise vos formes. C'est une basique intemporelle qui se décline à l'infini selon votre style personnel."}}
      ],
      "a_eviter": [
        {{"cut_display": "Hauts trop moulants ou oversize", "why": "Les hauts trop moulants qui collent à chaque courbe accentuent ce que vous pourriez préférer minimiser. À l'inverse, les oversize trop amples créent du volume non désiré et vous font paraître plus grande que vous ne l'êtes. Cherchez l'équilibre parfait entre ajustement et confort."}},
        {{"cut_display": "Rayures horizontales larges", "why": "Les rayures horizontales larges élargissent visuellement le buste et les hanches, ce qui n'est pas favorable pour votre silhouette. Même de fines rayures horizontales peuvent ajouter de la largeur perceptible. Privilégiez les rayures verticales ou les imprimés discrets pour une meilleure harmonie."}}
      ],
      "matieres": "Privilégiez les matieres de qualité avec un peu de structure: coton épais, soie, lin mélangé, polyamide stretch. Évitez les tissus trop fluides ou trop rigides. Les matieres avec un peu d'élasticité (2-5% spandex) sont vos meilleures alliées pour un confort optimal.",
      "motifs": {{
        "recommandes": "Motifs discrets, rayures verticales fines, petits imprimés géométriques, dégradés subtils, carreaux fins, fleurs minuscules. Les petits motifs créent du relief intéressant sans surcharger visuellement.",
        "a_eviter": "Gros motifs qui attirent trop le regard, rayures horizontales larges, imprimés trop clairs ou trop lumineux, petits pois, damier large. Ces motifs élargissent visuellement et rompent les lignes flatteuses."
      }},
      "pieges": [
        "Les coupes trop amples qui cachent votre silhouette au lieu de la valoriser",
        "Les tuniques qui s'arrêtent pile à la taille (la plus large) au lieu de créer de la verticalité",
        "Les hauts avec des fronces ou des nœuds au niveau de la poitrine qui ajoutent du volume",
        "Les manches bouffantes qui élargissent les épaules",
        "Les matières trop fluides (mousseline, viscose) qui épousent trop les formes"
      ]
    }},
    
    "bas": {{
      "introduction": "Pour silhouette {silhouette_type}, privilégiez taille haute et structures flatteuses.",
      "recommandes": [
        {{"cut_display": "Jean taille haute bien ajuste", "why": "Un jean taille haute est transformateur car il crée une proportion parfaite et allonge instantanément les jambes. La coupe doit être ajustée mais pas moulante pour un look à la fois élégant et confortable. C'est l'un des meilleurs investissements pour une silhouette harmonieuse."}},
        {{"cut_display": "Pantalon structure en chino", "why": "Un pantalon structuré en chino ou coton épais crée une belle ligne sans être collant. La structure du tissu épouse légèrement vos courbes de manière flatteuse tout en maintenant une élégance professionnelle ou décontractée. Impeccable pour le bureau comme pour les sorties."}},
        {{"cut_display": "Jupe trapeze ou patineuse", "why": "Une jupe qui s'évase légèrement à partir de la taille est votre secret pour un look ultra-féminin et flatteur. Elle cache les hanches tout en créant du mouvement dynamique et élégant. Vous vous sentirez à la fois à l'aise et magnifiquement mise en valeur."}},
        {{"cut_display": "Pantalon evasé ou bootcut", "why": "Un pantalon évasé ou bootcut depuis la taille crée une belle verticalité et balance magnifiquement votre silhouette. Cette coupe est flatteuse car elle épouse les courbes sans les souligner excessivement. Vous paraîtrez plus élancée et le style est intemporel."}},
        {{"cut_display": "Pantalon cigarette taille haute", "why": "Un pantalon cigarette bien ajusté à la taille crée une ligne claire et structurée. La coupe droite et élégante allonge les jambes et crée une silhouette harmonieuse. C'est parfait pour un look chic et intemporel qui marche dans tous les contextes."}},
        {{"cut_display": "Jupe crayon midi taille haute", "why": "Une jupe crayon midi taille haute crée une belle définition sans être trop moulante. La longueur midi est particulièrement flatteuse car elle allonge les jambes et crée une allure sophistiquée. C'est un vrai basique de garde-robe pour les looks élégants."}}
      ],
      "a_eviter": [
        {{"cut_display": "Taille basse ou super basse", "why": "Les tailles basses créent une proportion moins harmonieuse en raccourcissant les jambes visuellement. Elles mettent en avant la partie que vous préférez minimiser et rompent la verticalité flatteuse. Pour votre silhouette, la taille haute est vraiment votre meilleure option."}},
        {{"cut_display": "Baggy ou trop ample sans structure", "why": "Les coupes trop amples sans structure ajoutent du volume là où vous n'en voulez pas. Elles vous font paraître plus grande qu'en réalité et cachent vos formes au lieu de les valoriser harmonieusement. Cherchez toujours une coupe ajustée avec un peu de structure."}}
      ],
      "matieres": "Privilégiez les matieres structurées: denim qualité, coton épais, laine mélangée, chino, lin mélangé. Ces matieres créent une belle ligne et durent longtemps. Évitez les matieres trop fluides qui ne tiennent pas la forme.",
      "motifs": {{
        "recommandes": "Unis classiques, motifs subtils, petits carreaux, rayures fines verticales, dégradés discrets. Pour les bas, la simplicité est souvent la meilleure option pour créer une silhouette harmonieuse.",
        "a_eviter": "Motifs larges ou trop lumineux qui élargissent visuellement, rayures horizontales, gros carreaux, imprimés trop chargés, effets tie-dye. Ces motifs rompent les lignes flatteuses."
      }},
      "pieges": [
        "Les pantalons trop longs qui traînent et raccourcissent les jambes",
        "Les ceintures trop larges qui écrasent la taille au lieu de la sublimer",
        "Les coupes trop amples au niveau des hanches qui ajoutent du volume",
        "Les motifs ou détails trop imposants qui attirent le regard vers le bas",
        "Les pantalons sans stretch qui ne respirent pas et ne suivent pas vos mouvements"
      ]
    }},
    
    "robes": {{
      "introduction": "Pour silhouette {silhouette_type}, les robes créent des proportions magnifiques quand elles sont bien choisies.",
      "recommandes": [
        {{"cut_display": "Robe portefeuille élégante", "why": "Les robes portefeuille avec leur drapé délicat sont une option fantastique car elles créent une belle illusion de taille tout en restant infiniment élégantes. Le drapé valorise votre buste et minimise visuellement les hanches avec subtilité. C'est un classique qui marche pour toutes les occasions du casual au chic."}},
        {{"cut_display": "Robe ceinturee ou cache-coeur", "why": "Une robe ceinturée définit magnifiquement la taille et crée une silhouette super féminine et harmonieuse. Les robes cache-cœur font le même miracle en structurant le buste et en créant une taille marquée naturellement. Vous vous sentirez à la fois à l'aise et sublimée."}},
        {{"cut_display": "Robe trapeze ou evasée", "why": "Les robes évasées à partir de la taille ou trapèze ajoutent une belle dynamique sans insister sur la région de la taille. Elles cachent harmonieusement le bas du corps tout en créant mouvement et élégance. Parfait pour des occasions spéciales ou pour le quotidien."}},
        {{"cut_display": "Robe asymétrique chic", "why": "Une robe asymétrique crée du mouvement intéressant et capture le regard de manière flatteuse. Cette coupe moderne crée de la verticalité tout en restant très féminine. C'est parfait pour un look sophistiqué qui sort de l'ordinaire avec goût."}},
        {{"cut_display": "Robe avec encolure V ou Sweetheart", "why": "Une robe avec encolure en V ou Sweetheart allonge naturellement votre silhouette et valorise le haut du corps. Ce détail simple crée une verticalité très flatteuse qui améliore l'équilibre général de votre proportions. C'est un détail à chercher absolument quand vous achetez une robe."}},
        {{"cut_display": "Robe ligne A ou patineuse", "why": "Une robe qui s'évase légèrement à partir de la taille crée une silhouette ultra-féminine et flatteuse. La coupe A est particulièrement valorisante car elle minimise les hanches avec élégance tout en créant du mouvement gracieux. Vous vous sentirez magnifique et à l'aise."}}
      ],
      "a_eviter": [
        {{"cut_display": "Robe trop ample ou informe", "why": "Les robes trop amples qui cachent votre silhouette au lieu de la valoriser vous font paraître plus grande qu'en réalité. Elles créent un manque de structure qui n'est pas flatteur. Cherchez toujours une robe qui définit au minimum la taille."}},
        {{"cut_display": "Robe trop moulante partout", "why": "Une robe excessivement moulante souligne chaque courbe de manière peu flatteuse et vous met mal à l'aise. Elle laisse peu de place à l'imagination et crée un look trop exposé. L'équilibre entre ajustement et confort est la clé d'une robe réussie."}}
      ],
      "matieres": "Privilégiez les matieres fluides mais structurées: coton mélangé, soie, crêpe, jersey épais, popeline. Ces matieres épousent légèrement sans coller et créent une belle ligne. Évitez les matieres trop fragiles ou trop rigides.",
      "motifs": {{
        "recommandes": "Motifs subtils, petits imprimés, rayures fines, dégradés, fleurs minuscules, géométrie discrète. Les robes unies colorées sont aussi d'excellents choix pour des occasions plus formelles.",
        "a_eviter": "Gros motifs qui écrasent la silhouette, rayures horizontales larges, imprimés trop lumineux ou trop chargés, petits pois larges, carreaux gros. Ces motifs enlèvent de la fluidité à votre robe."
      }},
      "pieges": [
        "Les robes qui s'arrêtent pile à mi-cuisse (la partie la plus large)",
        "Les encolures trop hautes qui raccourcissent le buste",
        "Les ceintures trop larges qui écrasent la taille",
        "Les robes avec trop de détails (volants, fronces) qui ajoutent du volume",
        "Les matieres trop fluides (mousseline) qui flottent sans créer de ligne"
      ]
    }},
    
    "vestes": {{
      "introduction": "Pour silhouette {silhouette_type}, les vestes structurent et définissent magnifiquement.",
      "recommandes": [
        {{"cut_display": "Veste cintrée ou peplum", "why": "Une veste bien cintrée à la taille est transformatrice car elle crée une structure ultra-flatteuse et définit votre silhouette magnifiquement. La coupe cintrée marque la taille de manière élégante et crée un équilibre harmonieux. C'est un élément clé pour des looks instantanément chics et sophistiqués."}},
        {{"cut_display": "Blazer structuré classique", "why": "Un bon blazer structuré est l'outil parfait pour créer de la verticalité et de l'impact immédiatement. La structure des épaules et la définition de la taille créent une ligne très flatteuse et professionnelle. C'est un investissement basique pour tous vos looks."}},
        {{"cut_display": "Veste fluide avec ceinture", "why": "Une veste légèrement fluide avec une ceinture intégrée ou à ajouter crée du mouvement élégant et définit la taille. Cette coupe apporte de la sophistication tout en restant très portable au quotidien. L'effet est à la fois chic et confortable."}},
        {{"cut_display": "Veste cache-coeur", "why": "Une veste cache-cœur crée une belle structure et valorise magnifiquement le buste. Le drapé du cache-cœur minimise les hanches avec subtilité tout en créant une taille marquée. C'est un style intemporel qui marche pour tous les âges et tous les styles."}},
        {{"cut_display": "Veste a taille marquee courte", "why": "Une veste courte à taille marquée crée des proportions impeccables et allonge les jambes visuellement. La longueur courte la rend super facile à porter avec tout et crée un look moderne. C'est parfait pour structurer votre garde-robe quotidienne."}},
        {{"cut_display": "Cardigan long structure", "why": "Un cardigan long et structuré avec une ceinture crée une verticalité magnifique et minimise les hanches. La longueur allonge votre silhouette et la coupe structurée crée une belle définition. C'est ultra-polyvalent pour tous les contextes."}}
      ],
      "a_eviter": [
        {{"cut_display": "Veste trop ample ou oversize", "why": "Une veste trop ample sans structure ajoute du volume non désiré et crée une silhouette informe. Elle cache votre silhouette au lieu de la valoriser et vous paraissez plus grande qu'en réalité. Cherchez toujours une veste qui crée une belle ligne."}},
        {{"cut_display": "Epaulettes larges ou revers trop amples", "why": "Les épaulettes larges élargissent excessivement les épaules et rompent la belle ligne que vous pouvez créer. Les revers trop amples ajoutent du volume inutile et rendent la veste trop imposante. Cherchez des vestes avec une structure épaulée discrète et harmonieuse."}}
      ],
      "matieres": "Privilégiez les matieres structurées: laine, coton épais, linen blend, polyester mélangé avec un peu de stretch. Ces matieres créent une belle ligne et gardent leur forme toute la journée. Évitez les matieres trop fluides.",
      "motifs": {{
        "recommandes": "Unis classiques, motifs discrets, petits carreaux, rayures fines verticales, textures subtiles. Pour les vestes, la simplicité crée souvent l'effet le plus flatteur et intemporel.",
        "a_eviter": "Gros motifs, rayures horizontales larges, carreaux larges, imprimés trop chargés. Ces motifs élargissent visuellement et créent du désordre visuel."
      }},
      "pieges": [
        "Les vestes qui s'arrêtent pile à la taille (la plus large) au lieu de la sublimer",
        "Les encolures trop amples qui raccourcissent la silhouette",
        "Les manches trop larges qui élargissent les bras",
        "Les vestes sans aucune définition à la taille",
        "Les matières trop lourds qui ajoutent du poids visuel"
      ]
    }},
    
    "maillot_lingerie": {{
      "introduction": "Pour silhouette {silhouette_type}, confort ET élégance sont essentiels.",
      "recommandes": [
        {{"cut_display": "Soutien-gorge structure balconnet", "why": "Un soutien-gorge balconnet bien structuré crée une belle forme et valorise magnifiquement votre buste. La structure apporte du confort toute la journée tout en créant une silhouette impeccable. C'est un basique indispensable pour tous vos looks."}},
        {{"cut_display": "Maillot cache-coeur elegant", "why": "Un maillot cache-cœur crée une belle structure et minimise les hanches avec subtilité tout en restant super confortable. Le style est à la fois flatteur et facile à vivre. Idéal pour les jours où vous voulez vous sentir sublime sans effort."}},
        {{"cut_display": "Ceinture gaine douce", "why": "Une ceinture gaine douce crée une belle silhouette sans inconfort ni sensation d'étouffement. Elle lisse délicatement et crée une confiance immédiate. Parfait pour lisser les imperfections sous les robes moulantes."}},
        {{"cut_display": "Matieres stretch respirantes", "why": "Les matieres avec élasticité (coton stretch, modal stretch) épousent vos formes de manière flatteuse tout en respirant. Ces matieres créent une belle ligne tout en restant confortables toute la journée. C'est le secret du style sans effort."}},
        {{"cut_display": "Soutien-gorge sans armature de qualite", "why": "Un bon soutien-gorge sans armature apporte du confort exceptionnel tout en créant une belle forme. La qualité des matieres fait la différence pour un port confortable et flatteur. Indispensable pour les jours relax chics."}},
        {{"cut_display": "Culotte haute ou mi-hauteur", "why": "Une culotte haute ou mi-hauteur crée une belle ligne sous les robes et pantalons sans être visible. Elle offre du confort et de la confiance tout en créant une silhouette harmonieuse. C'est un basique à avoir absolument."}}
      ],
      "a_eviter": [
        {{"cut_display": "Ceintures ou gaines trop serrees", "why": "Une ceinture ou gaine trop serrée crée de l'inconfort et laisse des marques indésirables. Elle n'améliore pas vraiment la silhouette et rend les mouvements difficiles. Cherchez la douce compression plutôt que la restriction."}},
        {{"cut_display": "Maillots ou sous-vetements trop amples", "why": "Un maillot ou sous-vêtement trop ample crée des bourrelets inutiles et rend les mouvements inconfortables. Le confort n'est pas compromis quand vous choisissez la bonne taille. L'ajustement est vraiment la clé du confort."}}
      ],
      "matieres": "Privilégiez les matieres nobles et douces: coton organique, soie, modal, matieres stretch confortables. Ces matieres respirent et respectent votre peau delicate. Évitez les matieres synthétiques bon marché.",
      "motifs": {{
        "recommandes": "Unis classiques, couleurs douces, motifs minuscules discrets. Pour la lingerie, la discrétion est souvent la meilleure option pour créer des lignes impeccables.",
        "a_eviter": "Motifs trop visibles ou trop charges, couleurs trop lumineuses qui marquent sous les vetements, textures trop epaisses qui creatent de la visibilite."
      }},
      "pieges": [
        "Les soutiens-gorges mal ajustes qui creent des bourrelets",
        "Les matieres synthétiques bon marche qui ne respirent pas",
        "Les ceintures trop serrees qui laissent des marques",
        "Les culottessans suffisamment de couverture",
        "L'absence de bonnes bases (sous-vetements mal choisis compromet tous vos looks)"
      ]
    }},
    
    "chaussures": {{
      "introduction": "Pour silhouette {silhouette_type}, les chaussures doivent affiner et allonger.",
      "recommandes": [
        {{"cut_display": "Talon fin elegance (5-8cm)", "why": "Un talon fin entre 5 et 8cm crée une silhouette ultra-flatteuse en affinant la cheville et en allongeant les jambes. La finesse du talon apporte de l'élégance sans faire mal. C'est l'option parfaite pour paraître plus grande et harmoniser votre silhouette."}},
        {{"cut_display": "Escarpin pointe fine", "why": "Un escarpin à pointe fine allonge instantanément les jambes et crée une ligne très élégante. Le style intemporel marche avec tout et toute l'année. C'est un investissement basique pour tous vos looks plus formels."}},
        {{"cut_display": "Bottine talon structuree", "why": "Une bottine avec talon crée une belle verticalité et structure élégamment votre silhouette. La hauteur de talon allonge les jambes et crée une proportion parfaite. Indispensable pour tous les contextes automne-hiver."}},
        {{"cut_display": "Sandale talon ou nu-pieds talon", "why": "Une sandale ou nu-pieds avec talon crée une belle ligne en été tout en restant confortable. Le talon fin affine la cheville et allonge le pied. Parfait pour les occasions plus décontractées en saison chaude."}},
        {{"cut_display": "Mule elegant ou sandale plateau", "why": "Une mule élégante avec talon ou une sandale avec petit plateau crée une belle silhouette sans l'effort d'enfiler une chaussure. Le style est moderne et très portable. Indispensable pour l'été chic et décontracté."}},
        {{"cut_display": "Chaussure couleur peau", "why": "Une chaussure couleur peau crée une belle continuité de ligne et allonge visuellement les jambes. C'est un trick simple mais très efficace pour paraître plus grande. Parfait pour les robes ou pantalons cropped."}}
      ],
      "a_eviter": [
        {{"cut_display": "Chaussures plates trop larges", "why": "Les chaussures plates et larges raccourcissent visuellement les jambes et élargissent le pied. Elles créent une ligne moins flatteuse surtout avec des pantalons ou robes. Un petit talon ou une finesse apporte toujours plus de sophistication."}},
        {{"cut_display": "Bottines molles sans structure", "why": "Les bottines molles sans structure élargissent la cheville et créent un look peu flatteur. Elles manquent de cette definition elegante qui affine. Cherchez toujours une chaussure avec un peu de structure."}}
      ],
      "matieres": "Privilégiez les matieres qualité: cuir, suede, satin pour les occasions, canvas épais pour casual. Ces matieres durent longtemps et créent une meilleure ligne. Évitez les matieres synthétiques bon marche.",
      "motifs": {{
        "recommandes": "Unis classiques, couleurs neutres, couleur peau, petits details discrets. Pour les chaussures, la simplicité crée souvent l'effet le plus elegant et versatile.",
        "a_eviter": "Motifs trop charges, couleurs trop lumineuses, details trop imposants. Ces elements distraient du reste de votre look."
      }},
      "pieges": [
        "Les chaussures mal ajustees qui creent des ampoules",
        "Les talons trop hauts qui compromettent votre confort",
        "Les chaussures sans support qui laissent les pieds flotter",
        "L'absence de couleur peau ou neutre dans la garde-robe",
        "Les formes trop imposantes qui enlargissent les pieds"
      ]
    }},
    
    "accessoires": {{
      "introduction": "Pour silhouette {silhouette_type}, les accessoires doivent sublimer sans surcharger.",
      "recommandes": [
        {{"cut_display": "Ceinture fine elegante", "why": "Une ceinture fine mais de qualite marque la taille elegamment sans l'ecraser. Elle ajoute un detail sophistique qui transforme instantanément un look. C'est l'accessoire parfait pour creer une belle definition."}},
        {{"cut_display": "Bijoux verticaux (colliers, boucles)", "why": "Les bijoux verticaux comme les colliers longs ou les boucles asymetriques allongent naturellement votre silhouette. Ils creent de la verticalite et capturent le regard vers le haut. Parfait pour equilibrer les proportions avec elegance."}},
        {{"cut_display": "Foulard long ou echarpe", "why": "Un foulard long ou une echarpe cree une belle verticalite et ajoute de la sophistication instantanement. L'accessoire apporte du mouvement et de la fluidite a votre silhouette. Indispensable pour les occasions plus raffinées."}},
        {{"cut_display": "Sac elegant proportion fine", "why": "Un sac avec des proportions fines et elegantes ne surcharge pas votre silhouette. Cherchez des formes allongees plutot que des volumes massifs. Un bon sac structure votre look sans l'ecraser visuellement."}},
        {{"cut_display": "Bijoux fins discrets", "why": "Les bijoux fins comme les bracelets fins ou les anneaux discrets apportent de l'elegance sans surcharge. Ils raffinent votre look et creent une impression de delicatesse. Parfait pour tous les contextes du casual au formel."}},
        {{"cut_display": "Chapeau ou barrette elegant", "why": "Un chapeau bien choisi ou une barrette elegante ajoute du style et cree de la verticalite. Ces accessoires capturent le regard vers le haut et subliment votre visage. Parfait pour ajouter une touche de sophistication."}}
      ],
      "a_eviter": [
        {{"cut_display": "Ceintures larges qui ecrasent", "why": "Les ceintures larges ajoutent du volume et ecrasent la taille au lieu de la sublimer. Elles creent une impression de lourdeur qui n'est pas flatteuse. Les ceintures fines ou moyennes sont toujours votre meilleur choix."}},
        {{"cut_display": "Sacs volumineux ou charges", "why": "Les sacs trop volumineux ou trop charges ajoutent du poids visuel et desequilibrent votre silhouette. Ils creent une impression de desordre. Cherchez des sacs structures avec des proportions equilibrees."}}
      ],
      "matieres": "Privilégiez les matieres de qualité: cuir, soie, bijoux dores ou argentes, tissus nobles. Ces matieres elevéent votre look et durent longtemps. Evitez les matieres bon marche qui ne flattent pas.",
      "motifs": {{
        "recommandes": "Unis classiques, couleurs or, argent, petits details discrets. Pour les accessoires, l'elegance reside dans la simplicite et la qualité.",
        "a_eviter": "Motifs trop charges, couleurs trop lumineuses, details trop imposants. Ces elements surchargeront votre silhouette."
      }},
      "pieges": [
        "Les bijoux trop lourds qui tirent vers le bas",
        "Les sacs qui descendent trop bas sur la hanche",
        "Les accessoires trop nombreux qui surchargeant",
        "L'absence d'equilibre entre les accessoires et la tenue",
        "Les matieres bon marche qui ne respirent pas la qualité"
      ]
    }}
  }}
}}

REGLES STRICTES:
✅ 6 recommandes par categorie
✅ 2 a_eviter par categorie
✅ 7 categories EXACTEMENT
✅ introduction courte (10-20 mots)
✅ "why" = 2-3 PHRASES COMPLETES (50-80 mots chacune)
✅ Ajouter matieres, motifs avec recommandes/a_eviter, pieges (3-5 items)
✅ AUCUN accent bizarre, apostrophe dans JSON (remplacer par simple ou laisser vide)
✅ JSON VALIDE uniquement
✅ Explique le POURQUOI et pas juste le QUOI
✅ Tone chaleureux, expert, bienveillant
✅ Zero texte avant/apres JSON

Repondez UNIQUEMENT le JSON.
"""