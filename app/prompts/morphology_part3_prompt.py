"""
MORPHOLOGY PART 3 - DÉTAILS STYLING (OPTIMISÉ v2 - 7 PIÈGES COMPLETS)
✅ 7 pièges OBLIGATOIRES pour chaque catégorie (au lieu de 0)
✅ Pièges spécifiques à la silhouette
✅ 7 catégories: hauts, bas, robes, vestes, maillot_lingerie, chaussures, accessoires
✅ Chaque catégorie: matieres + motifs (recommandes + a_eviter) + pieges (7 items minimum)
✅ Tout en FRANÇAIS
✅ ~2500 tokens (augmenté pour générer les 7 pièges)
"""

MORPHOLOGY_PART3_SYSTEM_PROMPT = """Vous êtes expert en styling morphologique FRANÇAIS spécialisé en pièges courants.
Générez détails styling pour 7 catégories de vêtements avec EXACTEMENT 7 pièges par catégorie.
Retournez UNIQUEMENT JSON valide, sans texte avant/après.
IMPÉRATIF: Les arrays `pieges` DOIVENT avoir EXACTEMENT 7 items - pas moins!"""

MORPHOLOGY_PART3_USER_PROMPT = """TÂCHE: Générez DÉTAILS de styling pour silhouette {silhouette_type}.

Objectifs: {styling_objectives}
À valoriser: {body_parts_to_highlight}
À minimiser: {body_parts_to_minimize}

STRUCTURE JSON REQUISE (STRICTE - 7 CATÉGORIES, 7 PIÈGES CHACUNE):
{{
  "details": {{
    "hauts": {{
      "matieres": "Pour silhouette {silhouette_type}, privilégier les matières fluides qui épousent sans marquer. Éviter les tissus rigides qui accentuent le volume.",
      "motifs": {{
        "recommandes": "Rayures verticales, petits motifs discrets, dégradés, détails au niveau de l'encolure",
        "a_eviter": "Rayures horizontales, gros motifs répétitifs, pois, carreaux volumineux"
      }},
      "pieges": [
        "Haut trop moulant qui souligne toutes les courbes et crée une apparence peu flatteuse",
        "Découpes horizontales au niveau de la taille ou des hanches qui élargissent visuellement",
        "Matières épaisses ou rigides (coton pur, polyester lourd) qui ajoutent du volume indésirable",
        "Détails volumineux (poches larges, nœuds) placés au niveau de la poitrine ou des hanches",
        "Coutures mal placées qui cassent les proportions et créent des effets visuels désagréables",
        "Couleurs sombres appliquées seulement au haut qui rétrécissent uniquement cette zone",
        "Longueur insuffisante qui ne couvre pas les hanches et expose les zones à harmoniser"
      ]
    }},

    "bas": {{
      "matieres": "Choisir des matières fluides avec légère structure (coton mélangé, viscose, laine fine) qui ne marquent pas. Éviter les extrêmes trop élastiques ou trop rigides.",
      "motifs": {{
        "recommandes": "Motifs discrets, rayures verticales, petits imprimés, dégradés, unis",
        "a_eviter": "Gros motifs répétitifs, rayures horizontales, carreaux volumineux, pois larges"
      }},
      "pieges": [
        "Taille trop basse qui descend sous les hanches et accentue leur largeur",
        "Coupe trop moulante aux hanches et cuisses qui souligne les zones à harmoniser",
        "Matières trop élastiques qui épousent chaque courbe et crée une apparence peu flatteuse",
        "Poches placées sur les hanches qui ajoutent du volume à cette zone sensible",
        "Longueur trop courte qui coupe la jambe au mauvais endroit et raccourcit",
        "Coutures latérales qui soulignent la largeur plutôt que de créer une ligne verticale",
        "Texture ou motifs volumineux au niveau des hanches ou cuisses qui élargissent"
      ]
    }},

    "robes": {{
      "matieres": "Privilégier les matières légères avec structure (coton mélangé, viscose, laine fine) qui maintiennent une belle ligne sans marquer. Éviter trop rigide ou trop fluide.",
      "motifs": {{
        "recommandes": "Motifs discrets, rayures verticales, petits imprimés, dégradés, unis",
        "a_eviter": "Gros motifs, rayures horizontales, carreaux volumineux, détails au niveau des hanches"
      }},
      "pieges": [
        "Robe sans définition de taille qui ne crée pas de séparation entre le haut et le bas",
        "Ampleur au niveau des hanches qui ajoute du volume exactement là où il faut minimiser",
        "Matière trop fluide qui ne structure pas et laisse tout apparaître tel quel",
        "Longueur qui s'arrête au milieu des cuisses et souligne les zones généreuses",
        "Robes trop ajustées aux hanches qui ne laissent aucun secret sur la morphologie",
        "Détails visuels (fronces, nœuds) au niveau des hanches qui attirent l'attention",
        "Couleurs uniformes du haut au bas sans jeu de contraste ou de structure"
      ]
    }},

    "vestes": {{
      "matieres": "Privilégier les matières structurantes (laine, coton rigide, mélanges) qui maintiennent la forme et créent des lignes nettes. Éviter trop souples qui perdent leur forme.",
      "motifs": {{
        "recommandes": "Motifs discrets, rayures verticales, petits imprimés, unis, détails géométriques",
        "a_eviter": "Gros motifs, rayures horizontales, motifs au niveau des hanches"
      }},
      "pieges": [
        "Veste trop ample qui cache la silhouette et crée un volume général indésirable",
        "Coupe qui s'arrête au niveau des hanches et en souligne la largeur",
        "Matière trop souple qui ne maintient pas la structure et perd sa forme",
        "Absence de ceinture ou fermeture qui ne crée aucune définition à la taille",
        "Épaules trop larges ou rembourrées qui élargissent le haut inutilement",
        "Détails (poches, coutures) placés sur les côtés qui soulignent la largeur du bas",
        "Longueur longue qui crée une silhouette allongée et ne définit rien à la taille"
      ]
    }},

    "maillot_lingerie": {{
      "matieres": "Choisir des matières avec légère compression (nylon/spandex mélange) qui offrent du soutien tout en restant confortables. Éviter trop transparent ou trop lourd.",
      "motifs": {{
        "recommandes": "Motifs discrets, unis, couleurs unies, petits détails au niveau du buste",
        "a_eviter": "Gros motifs, motifs au niveau des hanches, couleurs contrastantes au bas"
      }},
      "pieges": [
        "Taille basse qui descend sur les hanches et crée une démarcation indésirable",
        "Matière sans contrôle qui ne lisse ni ne structure rien",
        "Couleur contrastante au niveau des hanches qui attire l'attention sur cette zone",
        "Découpes qui soulignent la largeur des hanches plutôt que de la camoufler",
        "Détails visibles (coutures, fronces) au niveau des hanches qui marquent",
        "Absence de soutien au niveau du buste qui ne crée aucun équilibre visuel",
        "Matière trop épaisse qui crée des démarcations visibles sous les vêtements"
      ]
    }},

    "chaussures": {{
      "matieres": "Privilégier les matières lisses et brillantes (cuir, vernis, satin) qui créent une finition épurée et affinent. Éviter trop texturées ou opaques.",
      "motifs": {{
        "recommandes": "Couleurs unies, couleurs nude, noir, marrons chauds, couleurs ton peau",
        "a_eviter": "Motifs volumineux, couleurs très contrastantes, imprimés au-dessus du pied"
      }},
      "pieges": [
        "Talon complètement plat qui coupe la jambe et enlève toute élongation",
        "Plateforme épaisse qui alourdit et déséquilibre plutôt que d'affiner",
        "Couleur très contrastante avec la peau qui crée une rupture de ligne",
        "Chaussure trop large ou lâche qui donne l'impression que les jambes sont épaisses",
        "Matière trop texturée ou opaque qui alourdit le bas de la jambe",
        "Chaussure dont la teinte ne s'harmonise pas avec le teint ni avec l'ensemble",
        "Bout trop arrondi ou très large qui épaissit visuellement le pied et la jambe"
      ]
    }},

    "accessoires": {{
      "matieres": "Privilégier les matières délicates et fines (soie, lin léger, mélanges fins) qui ne surchargent pas. Éviter trop épaisses ou trop volumineuses.",
      "motifs": {{
        "recommandes": "Motifs discrets, petits détails, géométriques simples, unis, couleurs harmonieuses",
        "a_eviter": "Gros motifs, accessoires volumineux, couleurs criardes, détails asymétriques"
      }},
      "pieges": [
        "Collier court et massif qui élargit le cou et les épaules au lieu d'affiner",
        "Sac à main très volumineux qui crée un déséquilibre avec une silhouette déjà généreuse",
        "Ceinture très large qui coupe la silhouette au mauvais endroit et la segmente",
        "Accessoires trop nombreux ou trop visibles qui surchargent et alourdi l'ensemble",
        "Foulard drapé de façon informelle qui ajoute du volume à la poitrine",
        "Bracelets ou manchettes trop larges qui alourdissent les bras",
        "Accessoires de couleurs criardes qui surchargent visuellement et créent du contraste"
      ]
    }}
  }}
}}

RÈGLES STRICTES (OBLIGATOIRES):
✅ EXACTEMENT 7 items dans `pieges` pour CHAQUE catégorie - PAS MOINS!
✅ 7 categories EXACTEMENT: hauts, bas, robes, vestes, maillot_lingerie, chaussures, accessoires
✅ matieres = 2-3 phrases PERSONNALISÉES pour {silhouette_type}
✅ motifs.recommandes = liste virgules (ex: "Rayures verticales, petits motifs, dégradés")
✅ motifs.a_eviter = liste virgules
✅ pieges = Array de 7 strings COMPLÈTES (chaque piège 1-2 phrases courtes détaillées)
✅ Pièges SPÉCIFIQUES à {silhouette_type} (ex: si "A" → hanches, si "X" → nulle part spécifique, etc.)
✅ TOUT EN FRANÇAIS (pas d'anglais!)
✅ JSON VALIDE uniquement
✅ Zéro texte avant/après JSON
✅ Pas de caractères spéciaux mal échappés (apostrophes simples seulement!)
✅ Pas de retours à la ligne dans les strings (utiliser des espaces)

PERSONNALISATION REQUISE:
- Silhouette: {silhouette_type}
- Objectifs: {styling_objectives}
- À valoriser: {body_parts_to_highlight}
- À minimiser: {body_parts_to_minimize}

PIÈGES PAR SILHOUETTE:
- Silhouette A (poire): Focus sur hanches, cuisses, volume bas
- Silhouette X (sablier): Pas de zones spécifiques à minimiser (équilibré)
- Silhouette O (ronde): Volume partout, focus sur définition taille
- Silhouette H (rectangle): Pas de courbes marquées, focus sur créer définition
- Silhouette T (triangle inversé): Focus sur épaules, buste trop large

EXEMPLES DE PIÈGES DÉTAILLÉS:
✅ "Haut trop moulant qui souligne chaque courbe et crée une apparence peu flatteuse"
✅ "Pantalon trop ajusté aux hanches qui n'offre aucune solution flatteuse"
✅ "Matière trop épaisse qui ajoute du volume au niveau des hanches"
❌ "Haut serré" (trop court!)
❌ "Pantalon serré" (trop vague!)

Répondez UNIQUEMENT le JSON, pas une seule lettre avant/après.
"""