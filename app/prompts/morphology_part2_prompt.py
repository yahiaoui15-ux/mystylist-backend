"""
MORPHOLOGY PART 2 - Recommandations Vêtements (Text) - v4 ULTRA-SIMPLIFIE
✅ 7 catégories: hauts, bas, robes, vestes, maillot_lingerie, chaussures, accessoires
✅ Chaque catégorie: introduction COURTE + recommandes (6) + a_eviter (5)
✅ PAS de matieres, motifs, pieges (Part 3)
✅ Tout en FRANÇAIS
✅ ~2000 tokens
"""

MORPHOLOGY_PART2_SYSTEM_PROMPT = """Vous êtes expert en styling morphologique FRANÇAIS.
Générez recommandations de vêtements pour 7 catégories.
Chaque catégorie: introduction courte (1 phrase) + pièces recommandées (6) + à éviter (5).
Retournez UNIQUEMENT JSON valide, sans texte avant/après."""

MORPHOLOGY_PART2_USER_PROMPT = """TÂCHE: Générez recommandations de VÊTEMENTS pour silhouette {silhouette_type}.

Objectifs: {styling_objectives}
À valoriser: {body_parts_to_highlight}
À minimiser: {body_parts_to_minimize}

STRUCTURE JSON REQUISE (STRICTE - 7 CATÉGORIES):
{{
  "recommendations": {{
    "hauts": {{
      "introduction": "Pour votre silhouette {silhouette_type}, privilégiez [conseil principal].",
      "recommandes": [
        {{"cut_display": "Nom du vêtement", "why": "Pourquoi (10-15 mots MAX)"}},
        {{"cut_display": "...", "why": "..."}},
        {{"cut_display": "...", "why": "..."}},
        {{"cut_display": "...", "why": "..."}},
        {{"cut_display": "...", "why": "..."}},
        {{"cut_display": "...", "why": "..."}}
      ],
      "a_eviter": [
        {{"cut_display": "Nom du vêtement", "why": "Pourquoi l'éviter (10-15 mots MAX)"}},
        {{"cut_display": "...", "why": "..."}},
        {{"cut_display": "...", "why": "..."}},
        {{"cut_display": "...", "why": "..."}},
        {{"cut_display": "...", "why": "..."}}
      ]
    }},

    "bas": {{
      "introduction": "Pour votre silhouette {silhouette_type}, privilégiez [conseil principal].",
      "recommandes": [6 items],
      "a_eviter": [5 items]
    }},

    "robes": {{
      "introduction": "...",
      "recommandes": [6 items],
      "a_eviter": [5 items]
    }},

    "vestes": {{
      "introduction": "...",
      "recommandes": [6 items],
      "a_eviter": [5 items]
    }},

    "maillot_lingerie": {{
      "introduction": "...",
      "recommandes": [6 items],
      "a_eviter": [5 items]
    }},

    "chaussures": {{
      "introduction": "...",
      "recommandes": [6 items],
      "a_eviter": [5 items]
    }},

    "accessoires": {{
      "introduction": "...",
      "recommandes": [6 items],
      "a_eviter": [5 items]
    }}
  }}
}}

RÈGLES STRICTES (OBLIGATOIRES):
✅ EXACTEMENT 6 items recommandes pour CHAQUE categorie
✅ EXACTEMENT 5 items a_eviter pour CHAQUE categorie
✅ 7 categories EXACTEMENT: hauts, bas, robes, vestes, maillot_lingerie, chaussures, accessoires
✅ introduction = 1 PHRASE COURTE SEULEMENT (15-20 mots MAX)
✅ Chaque item = {{"cut_display": "...", "why": "..."}}
✅ "why" = MAX 15 mots (court et spécifique!)
✅ TOUT EN FRANÇAIS (pas d'anglais!)
✅ JSON VALIDE uniquement - PAS de caractères spéciaux mal échappés
✅ Zéro texte avant/après JSON
✅ Pas d'apostrophes non échappées dans les strings

PERSONNALISATION REQUISE:
- Silhouette: {silhouette_type}
- Objectifs: {styling_objectives}
- À valoriser: {body_parts_to_highlight}
- À minimiser: {body_parts_to_minimize}

EXEMPLES DE FORMAT CORRECT:
✅ introduction: "Pour votre silhouette A, accentuez vos épaules avec des coupes structurées."
✅ "why": "Allonge les jambes et crée une verticalité"
✅ "why": "Valorise le buste sans ajouter de volume"
❌ "Votre silhouette A nécessite des vêtements qui..." (trop long!)

Répondez UNIQUEMENT le JSON, pas une seule lettre avant/après.
"""