"""
MORPHOLOGY PART 3 - Détails Styling (Matières + Motifs + Pièges) - v1 NOUVEAU
✅ 7 catégories: hauts, bas, robes, vestes, maillot_lingerie, chaussures, accessoires
✅ Chaque catégorie: matieres + motifs (recommandes + a_eviter) + pieges (7 items)
✅ Complémente Part 2 (recommandes + a_eviter)
✅ Tout en FRANÇAIS
✅ ~2000 tokens
"""

MORPHOLOGY_PART3_SYSTEM_PROMPT = """Vous êtes expert en styling morphologique FRANÇAIS.
Générez détails styling pour 7 catégories de vêtements.
Chaque catégorie: matières recommandées + motifs (à privilégier/éviter) + pièges courants.
Retournez UNIQUEMENT JSON valide, sans texte avant/après."""

MORPHOLOGY_PART3_USER_PROMPT = """TÂCHE: Générez DÉTAILS de styling pour silhouette {silhouette_type}.

Objectifs: {styling_objectives}
À valoriser: {body_parts_to_highlight}
À minimiser: {body_parts_to_minimize}

STRUCTURE JSON REQUISE (STRICTE - 7 CATÉGORIES):
{{
  "details": {{
    "hauts": {{
      "matieres": "Recommandations matières (1-2 phrases courtes spécifiques à {silhouette_type})",
      "motifs": {{
        "recommandes": "Rayures verticales, petits motifs, dégradés, détails au niveau de l'encolure",
        "a_eviter": "Rayures horizontales, gros motifs répétitifs, pois, carreaux volumineux"
      }},
      "pieges": [
        "Piège courant 1 spécifique à {silhouette_type}",
        "Piège courant 2",
        "Piège courant 3",
        "Piège courant 4",
        "Piège courant 5",
        "Piège courant 6",
        "Piège courant 7"
      ]
    }},

    "bas": {{
      "matieres": "...",
      "motifs": {{"recommandes": "...", "a_eviter": "..."}},
      "pieges": [7 items]
    }},

    "robes": {{
      "matieres": "...",
      "motifs": {{"recommandes": "...", "a_eviter": "..."}},
      "pieges": [7 items]
    }},

    "vestes": {{
      "matieres": "...",
      "motifs": {{"recommandes": "...", "a_eviter": "..."}},
      "pieges": [7 items]
    }},

    "maillot_lingerie": {{
      "matieres": "...",
      "motifs": {{"recommandes": "...", "a_eviter": "..."}},
      "pieges": [7 items]
    }},

    "chaussures": {{
      "matieres": "...",
      "motifs": {{"recommandes": "...", "a_eviter": "..."}},
      "pieges": [7 items]
    }},

    "accessoires": {{
      "matieres": "...",
      "motifs": {{"recommandes": "...", "a_eviter": "..."}},
      "pieges": [7 items]
    }}
  }}
}}

RÈGLES STRICTES (OBLIGATOIRES):
✅ EXACTEMENT 7 items dans pieges pour CHAQUE categorie
✅ 7 categories EXACTEMENT: hauts, bas, robes, vestes, maillot_lingerie, chaussures, accessoires
✅ matieres = 1-2 phrases courtes PERSONNALISÉES pour {silhouette_type}
✅ motifs.recommandes = liste virgules (ex: "Rayures verticales, petits motifs, dégradés")
✅ motifs.a_eviter = liste virgules
✅ pieges = Array de 7 strings (chaque piège 1-2 phrases courtes)
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

EXEMPLES DE FORMAT CORRECT:
✅ matieres: "Privilégier matières fluides (soie, coton) qui épousent sans serrer pour silhouette A. Éviter tissus rigides."
✅ motifs.recommandes: "Rayures verticales, losanges verticaux, petits motifs discrets, dégradés"
✅ pieges: ["Ourlets qui coupent la silhouette à la mauvaise hauteur (casser la verticalité)", "Encolures asymétriques qui perturbent l'équilibre", ...]
❌ matieres: "Pour votre silhouette, les matières doivent absolument être...très légères et fluides car sinon cela ne va pas bien..." (trop long!)
❌ Utiliser des retours à la ligne dans les strings JSON

CONTEXTE - Ceci COMPLÈTE Part 2:
- Part 2 génère: recommendations (introduction + recommandes + a_eviter)
- Part 3 génère: details (matieres + motifs + pieges)
- Template PDFMonkey fusionnera les deux pour l'affichage complet

Répondez UNIQUEMENT le JSON, pas une seule lettre avant/après.
"""