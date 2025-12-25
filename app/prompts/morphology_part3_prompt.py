"""
MORPHOLOGY PART 3 - DÉTAILS STYLING (OPTIMISE - TOKEN-LEAN) - MODIFIÉ v2
✅ 7 pièges OBLIGATOIRES + matieres + motifs avec puces
✅ Motifs: structure à puces claire
✅ Matieres: structure à puces personnalisées
✅ Prompt compact sans exemples JSON volumineux
✅ Token budget: ~1300-1600 au lieu de 1200-1500
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
Chaque catégorie: matieres (avec structure PUCES), motifs (recommandes + a_eviter avec puces), pieges (array de 7 strings).

Pièges: spécifiques à silhouette {silhouette_type}, 1-2 phrases chacun.
Matieres: détaillé pour {silhouette_type}, avec PUCES (•).
Motifs: recommandes et a_eviter EN PUCES (•).

JSON strict, français, zéro erreur.

{{
  "details": {{
    "hauts": {{
      "matieres": "• Matière 1 avec explication\n• Matière 2 avec explication\n• Matière 3...",
      "motifs": {{
        "recommandes": "• Motif 1: pourquoi\n• Motif 2: pourquoi",
        "a_eviter": "• À éviter 1: pourquoi\n• À éviter 2: pourquoi"
      }},
      "pieges": [
        "Piège 1: explication détaillée",
        "Piège 2: explication détaillée",
        "Piège 3: explication détaillée",
        "Piège 4: explication détaillée",
        "Piège 5: explication détaillée",
        "Piège 6: explication détaillée",
        "Piège 7: explication détaillée"
      ]
    }},
    "bas": {{...}},
    "robes": {{...}},
    "vestes": {{...}},
    "maillot_lingerie": {{...}},
    "chaussures": {{...}},
    "accessoires": {{...}}
  }}
}}
"""