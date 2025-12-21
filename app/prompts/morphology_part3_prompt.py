"""
MORPHOLOGY PART 3 - DÉTAILS STYLING (OPTIMISÉ - TOKEN-LEAN)
✅ 7 pièges OBLIGATOIRES + matieres + motifs
✅ Prompt compact sans exemples JSON volumineux
✅ Token budget: ~1200-1500 au lieu de 2680+
"""

MORPHOLOGY_PART3_SYSTEM_PROMPT = """Vous êtes expert styling morphologique français spécialisé pièges.
Générez détails styling en JSON valide UNIQUEMENT.
Zéro texte avant/après JSON.
IMPÉRATIF: 7 pièges exactement par catégorie."""

MORPHOLOGY_PART3_USER_PROMPT = """Silhouette: {silhouette_type}
Objectifs: {styling_objectives}
À valoriser: {body_parts_to_highlight}
À minimiser: {body_parts_to_minimize}

Générez JSON avec 7 catégories (hauts, bas, robes, vestes, maillot_lingerie, chaussures, accessoires).
Chaque catégorie: matieres (2-3 phrases personnalisées), motifs (recommandes + a_eviter), pieges (array de 7 strings).

Pièges: spécifiques à silhouette {silhouette_type}, 1-2 phrases chacun.
Matieres: détaillé pour {silhouette_type}.

JSON strict, français, zéro erreur.

{{
  "details": {{
    "hauts": {{"matieres": "", "motifs": {{"recommandes": "", "a_eviter": ""}}, "pieges": ["", "", "", "", "", "", ""]}},
    "bas": {{"matieres": "", "motifs": {{"recommandes": "", "a_eviter": ""}}, "pieges": ["", "", "", "", "", "", ""]}},
    "robes": {{"matieres": "", "motifs": {{"recommandes": "", "a_eviter": ""}}, "pieges": ["", "", "", "", "", "", ""]}},
    "vestes": {{"matieres": "", "motifs": {{"recommandes": "", "a_eviter": ""}}, "pieges": ["", "", "", "", "", "", ""]}},
    "maillot_lingerie": {{"matieres": "", "motifs": {{"recommandes": "", "a_eviter": ""}}, "pieges": ["", "", "", "", "", "", ""]}},
    "chaussures": {{"matieres": "", "motifs": {{"recommandes": "", "a_eviter": ""}}, "pieges": ["", "", "", "", "", "", ""]}},
    "accessoires": {{"matieres": "", "motifs": {{"recommandes": "", "a_eviter": ""}}, "pieges": ["", "", "", "", "", "", ""]}}
  }}
}}
"""