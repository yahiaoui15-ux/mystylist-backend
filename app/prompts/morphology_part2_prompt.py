"""
MORPHOLOGY PART 2 - Recommandations Styling Simplifiées (Text) - v10 SIMPLIFIE
✅ 7 catégories: hauts, bas, robes, vestes, maillot_lingerie, chaussures, accessoires
✅ Chaque catégorie: introduction + recommandes + a_eviter + matieres + motifs + pieges
✅ NO strategies (déjà en Part 1)
✅ Tout en FRANÇAIS
✅ Structure stricte et univoque
"""

MORPHOLOGY_PART2_SYSTEM_PROMPT = """Vous êtes expert en styling morphologique FRANÇAIS.
Générez recommandations de vêtements et accessoires pour 7 catégories.
Chaque catégorie: introduction + pièces recommandées + à éviter + matières + motifs + pièges.
Retournez UNIQUEMENT JSON valide, sans texte avant/après."""

MORPHOLOGY_PART2_USER_PROMPT = """TÂCHE: Générez recommandations de VÊTEMENTS pour silhouette {silhouette_type}.

Silhouette {silhouette_type}:
- Objectives: {styling_objectives}
- À valoriser: {body_parts_to_highlight}
- À minimiser: {body_parts_to_minimize}

STRUCTURE JSON REQUISE (STRICTE - 7 CATÉGORIES):
{{
  "recommendations": {{
    "hauts": {{
      "introduction": "Pour votre silhouette {silhouette_type}, les hauts doivent [conseil principal]. Privilégiez [caractéristique clé].",
      "recommandes": [
        {{"cut_display": "Nom du vêtement", "why": "Pourquoi c'est adapté à votre silhouette (10-15 mots MAX)"}},
        {{"cut_display": "Nom du vêtement", "why": "..."}},
        {{"cut_display": "Nom du vêtement", "why": "..."}},
        {{"cut_display": "Nom du vêtement", "why": "..."}},
        {{"cut_display": "Nom du vêtement", "why": "..."}},
        {{"cut_display": "Nom du vêtement", "why": "..."}}
      ],
      "a_eviter": [
        {{"cut_display": "Nom du vêtement", "why": "Pourquoi l'éviter (10-15 mots MAX)"}},
        {{"cut_display": "Nom du vêtement", "why": "..."}},
        {{"cut_display": "Nom du vêtement", "why": "..."}},
        {{"cut_display": "Nom du vêtement", "why": "..."}},
        {{"cut_display": "Nom du vêtement", "why": "..."}}
      ],
      "matieres": "Description des matières recommandées (1-2 phrases courtes avec spécificités pour {silhouette_type})",
      "motifs": {{
        "recommandes": "Liste de motifs à privilégier (virgules séparées)",
        "a_eviter": "Liste de motifs à éviter (virgules séparées)"
      }},
      "pieges": [
        "Piège courant 1 pour silhouette {silhouette_type}",
        "Piège courant 2",
        "Piège courant 3",
        "Piège courant 4",
        "Piège courant 5",
        "Piège courant 6",
        "Piège courant 7"
      ]
    }},

    "bas": {{
      "introduction": "Pour votre silhouette {silhouette_type}, les bas doivent [conseil principal]. Privilégiez [caractéristique clé].",
      "recommandes": [6 items avec cut_display + why],
      "a_eviter": [5 items avec cut_display + why],
      "matieres": "...",
      "motifs": {{"recommandes": "...", "a_eviter": "..."}},
      "pieges": [7 items]
    }},

    "robes": {{
      "introduction": "...",
      "recommandes": [6 items],
      "a_eviter": [5 items],
      "matieres": "...",
      "motifs": {{"recommandes": "...", "a_eviter": "..."}},
      "pieges": [7 items]
    }},

    "vestes": {{
      "introduction": "...",
      "recommandes": [6 items],
      "a_eviter": [5 items],
      "matieres": "...",
      "motifs": {{"recommandes": "...", "a_eviter": "..."}},
      "pieges": [7 items]
    }},

    "maillot_lingerie": {{
      "introduction": "...",
      "recommandes": [6 items],
      "a_eviter": [5 items],
      "matieres": "...",
      "motifs": {{"recommandes": "...", "a_eviter": "..."}},
      "pieges": [7 items]
    }},

    "chaussures": {{
      "introduction": "...",
      "recommandes": [6 items],
      "a_eviter": [5 items],
      "matieres": "...",
      "motifs": {{"recommandes": "...", "a_eviter": "..."}},
      "pieges": [7 items]
    }},

    "accessoires": {{
      "introduction": "...",
      "recommandes": [6 items],
      "a_eviter": [5 items],
      "matieres": "...",
      "motifs": {{"recommandes": "...", "a_eviter": "..."}},
      "pieges": [7 items]
    }}
  }}
}}

RÈGLES STRICTES (OBLIGATOIRES):
✅ EXACTEMENT 6 items dans recommandes pour CHAQUE categorie
✅ EXACTEMENT 5 items dans a_eviter pour CHAQUE categorie
✅ EXACTEMENT 7 items dans pieges pour CHAQUE categorie
✅ 7 categories EXACTEMENT: hauts, bas, robes, vestes, maillot_lingerie, chaussures, accessoires
✅ Chaque item = {{"cut_display": "...", "why": "..."}}
✅ "why" = MAX 15 mots (court et spécifique!)
✅ introduction = 1-2 phrases
✅ matieres = 1-2 phrases courtes
✅ motifs.recommandes = liste virgules (pas d'array!)
✅ motifs.a_eviter = liste virgules (pas d'array!)
✅ TOUT EN FRANÇAIS (pas d'anglais!)
✅ JSON VALIDE uniquement
✅ Zéro texte avant/après JSON
✅ Pas de caractères spéciaux/échappés (apostrophes doivent être simples!)

PERSONNALISATION REQUISE:
- Silhouette: {silhouette_type}
- Objectifs: {styling_objectives}
- À valoriser: {body_parts_to_highlight} → adapter recommandes pour ces parties
- À minimiser: {body_parts_to_minimize} → adapter a_eviter et matieres pour ces parties

EXEMPLES DE FORMAT "why" CORRECT (15 mots MAX):
✅ "Allonge les jambes et crée une verticalité immédiate"
✅ "Valorise le buste sans ajouter de volume ailleurs"
✅ "Crée de la fluidité et cache les rondeurs"
❌ "Cette pièce est vraiment très intéressante pour votre silhouette car elle crée..." (trop long!)

Répondez UNIQUEMENT le JSON, pas une seule lettre avant/après.
"""