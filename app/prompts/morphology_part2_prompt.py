"""
MORPHOLOGY PART 2 - Recommandations Vêtements (Text) - v4 FIXED
✅ JSON escaping correct (apostrophes échappées)
✅ 7 catégories: hauts, bas, robes, vestes, maillot_lingerie, chaussures, accessoires
✅ Chaque catégorie: introduction COURTE + recommandes (6) + a_eviter (5)
✅ Tout en FRANÇAIS sans caractères mal échappés
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
      "introduction": "Pour votre silhouette {silhouette_type}, privilegiez [conseil principal].",
      "recommandes": [
        {{"cut_display": "Nom du vetement", "why": "Pourquoi (10-15 mots MAX)"}},
        {{"cut_display": "...", "why": "..."}},
        {{"cut_display": "...", "why": "..."}},
        {{"cut_display": "...", "why": "..."}},
        {{"cut_display": "...", "why": "..."}},
        {{"cut_display": "...", "why": "..."}}
      ],
      "a_eviter": [
        {{"cut_display": "Nom du vetement", "why": "Pourquoi l eviter (10-15 mots MAX)"}},
        {{"cut_display": "...", "why": "..."}},
        {{"cut_display": "...", "why": "..."}},
        {{"cut_display": "...", "why": "..."}},
        {{"cut_display": "...", "why": "..."}}
      ]
    }},

    "bas": {{
      "introduction": "Pour votre silhouette {silhouette_type}, privilegiez [conseil principal].",
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
✅ "why" = MAX 15 mots (court et specifique!)
✅ TOUT EN FRANÇAIS (utiliser caracteresaccentus DIRECTEMENT, pas d echappement JSON)
✅ JSON VALIDE uniquement
✅ Zéro texte avant/après JSON
✅ IMPORTANT: Pas d apostrophes dans les strings! Utiliser des espaces ou tirets si besoin

PERSONNALISATION REQUISE:
- Silhouette: {silhouette_type}
- Objectifs: {styling_objectives}
- À valoriser: {body_parts_to_highlight}
- À minimiser: {body_parts_to_minimize}

EXEMPLES DE FORMAT CORRECT:
✅ introduction: "Pour votre silhouette A, accentuez vos epaules avec des coupes structurees."
✅ "why": "Allonge les jambes et cree une verticalite"
✅ "why": "Valorise le buste sans ajouter de volume"
❌ "Votre silhouette A necessite des vetements qui..." (trop long!)
❌ "L'apostrophe dans inopportunement" (apostrophe = BAD!)
✅ "Peut couper la silhouette de maniere inopportune" (pas d apostrophe = GOOD!)

Répondez UNIQUEMENT le JSON, pas une seule lettre avant/après.
"""