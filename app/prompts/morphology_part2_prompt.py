"""
MORPHOLOGY PART 2 - RECOMMANDATIONS STYLING (OPTIMISE - TOKEN-LEAN) - MODIFIÉ v2
✅ 6 pièces recommandées (au lieu de 3-4)
✅ Renommé: "a_eviter" → "pieces_a_eviter"
✅ Descriptions longues (80-100 mots) + matieres personnalisées
✅ Motifs avec structure claire
✅ Token budget: ~1600-1900 au lieu de 1500-1800
"""

MORPHOLOGY_PART2_SYSTEM_PROMPT = """Vous êtes expert styling morphologique français.
Générez recommandations détaillées en JSON valide UNIQUEMENT.
Zéro texte avant/après JSON."""

IMPORTANT:
- Tu DOIS répondre UNIQUEMENT avec un JSON STRICT.
- AUCUN texte avant ou après.
- Toutes les clés DOIVENT être entre guillemets doubles.
- AUCUNE virgule finale.
- AUCUN commentaire.
- Si tu ne peux pas générer une valeur, mets null ou [].
- La réponse doit être directement compatible avec json.loads().


MORPHOLOGY_PART2_USER_PROMPT = """Silhouette: {silhouette_type}
Objectifs: {styling_objectives}

Générez JSON avec 7 catégories (hauts, bas, robes, vestes, maillot_lingerie, chaussures, accessoires).
Chaque catégorie: introduction (1 phrase), recommandes (6 items), pieces_a_eviter (3-4 items), matieres (2-3 phrases avec puces), motifs (structure claire).

Pour recommandes et pieces_a_eviter: cut_display (nom pièce), why (MAX 50 mots explicatif spécifique à {silhouette_type}).

Matieres: 2-3 lignes avec STRUCTURE DE PUCES (•).
Motifs: avec puces pour recommandes et a_eviter.

Tout en français. JSON valide uniquement.

{{
  "recommendations": {{
    "hauts": {{
      "introduction": "",
      "recommandes": [
        {{"cut_display": "", "why": ""}},
        {{"cut_display": "", "why": ""}},
        {{"cut_display": "", "why": ""}},
        {{"cut_display": "", "why": ""}},
        {{"cut_display": "", "why": ""}},
        {{"cut_display": "", "why": ""}}
      ],
      "pieces_a_eviter": [
        {{"cut_display": "", "why": ""}},
        {{"cut_display": "", "why": ""}},
        {{"cut_display": "", "why": ""}}
      ],
      "matieres": "• Optez pour...\n• Privilégiez...\n• Évitez...",
      "motifs": {{
        "recommandes": "• Rayures...\n• Motifs géométriques...",
        "a_eviter": "• Motifs trop larges...\n• Pois volumineux..."
      }}
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