"""
COLORIMETRY PART 2 FIXED v10.1 - PALETTE PERSONNALISÉE + ASSOCIATIONS
✅ Exemple SIMPLIFIÉ (sinon OpenAI le copie)
✅ Structure claire sans template complet
✅ Force vraies valeurs personnalisées
"""

COLORIMETRY_PART2_SYSTEM_PROMPT = """Vous êtes expert colorimétre. Générez UNIQUEMENT JSON valide.
Commencez par { et finissez par }. Zéro texte avant/après."""

COLORIMETRY_PART2_USER_PROMPT_TEMPLATE = """Générez palette + associations pour client Automne.

DONNÉES CLIENT:
- Saison: {SAISON}
- Sous-ton: {SOUS_TON}
- Yeux: {EYE_COLOR}
- Cheveux: {HAIR_COLOR}

TÂCHE:
1. Générez 10 couleurs PERSONNALISÉES (pas template)
   - Noms FRANÇAIS uniques adaptés au client
   - hex codes vrais pour chaque couleur
   - notes 8-10 basées sur compatibilité
   - commentaires DIFFÉRENTS pour chaque couleur

2. Générez 5 associations gagnantes
   - Chaque occasion avec 3 couleurs combinées
   - Effets et descriptions PERSONNALISÉS

STRUCTURE JSON REQUISE:
{{
  "palette_personnalisee": [
    {{"name": "nom_lower", "hex": "#XXXXXX", "note": 9, "displayName": "Nom Affiche", "commentaire": "Raison spécifique pour ce client"}},
    ... 10 TOTAL
  ],
  "associations_gagnantes": [
    {{"occasion": "professionnel", "colors": ["Couleur1", "Couleur2", "Couleur3"], "color_hex": ["#XXXXX", "#XXXXX", "#XXXXX"], "effet": "Effet", "description": "Description personnalisée"}},
    ... 5 TOTAL (professionnel, casual, soiree, weekend, famille)
  ]
}}

RÈGLES:
✅ 10 couleurs EXACTEMENT
✅ 5 associations EXACTEMENT
✅ Pas de copie du template - VRAIES valeurs
✅ Noms français variés (camel, moutarde, bordeaux, rose corail, etc.)
✅ Hex codes vrais (#RRGGBB format)
✅ Notes 8-10 uniquement
✅ Commentaires courts (<15 mots) EN FRANÇAIS
✅ Pas d'apostrophe: "s harmonise" pas "s'harmonise"
✅ JSON valide

Répondez UNIQUEMENT le JSON, pas de texte avant/après.
"""

# FALLBACK
FALLBACK_PART2_DATA = {
    "palette_personnalisee": [
        {"name": "camel", "hex": "#C19A6B", "note": 10, "displayName": "Camel", "commentaire": "Essentiel reproduit harmonie naturelle"},
        {"name": "moutarde", "hex": "#E1AD01", "note": 10, "displayName": "Moutarde", "commentaire": "Jaune doré illumine teint subtilement"},
        {"name": "bordeaux", "hex": "#800020", "note": 9, "displayName": "Bordeaux", "commentaire": "Élégance nocturne par excellence"},
        {"name": "rose_corail", "hex": "#FF7F50", "note": 9, "displayName": "Rose Corail", "commentaire": "Rose chaud s harmonise magnifiquement"},
        {"name": "olive", "hex": "#808000", "note": 9, "displayName": "Olive", "commentaire": "Vert-brun chaud très polyvalent"},
        {"name": "cuivre", "hex": "#B87333", "note": 9, "displayName": "Cuivre", "commentaire": "Métallique chaud sophistiqué amplifie dorure"},
        {"name": "brique", "hex": "#CB4154", "note": 8, "displayName": "Brique", "commentaire": "Rouge-brun subtil très sophistiqué"},
        {"name": "kaki", "hex": "#C3B091", "note": 8, "displayName": "Kaki", "commentaire": "Classique chaud très polyvalent"},
        {"name": "chocolat", "hex": "#7B3F00", "note": 8, "displayName": "Chocolat", "commentaire": "Marron foncé élégant stable"},
        {"name": "terracotta", "hex": "#E2725B", "note": 8, "displayName": "Terracotta", "commentaire": "Chauffe teint apporte vitalité énergie"}
    ],
    "associations_gagnantes": [
        {"occasion": "professionnel", "colors": ["Camel", "Marron", "Beige"], "color_hex": ["#C19A6B", "#8B4513", "#F5F5DC"], "effet": "Élégance confidente", "description": "Pour réunions: authority calme confiance"},
        {"occasion": "casual", "colors": ["Kaki", "Camel", "Terracotta"], "color_hex": ["#C3B091", "#C19A6B", "#E2725B"], "effet": "Naturel sans-effort", "description": "Pour détente: relaxation énergie légèreté"},
        {"occasion": "soiree", "colors": ["Bordeaux", "Chocolat", "Cuivre"], "color_hex": ["#800020", "#7B3F00", "#B87333"], "effet": "Sophistication chaleureuse", "description": "Pour dîner: élégance richesse profondeur"},
        {"occasion": "weekend", "colors": ["Olive", "Camel", "Terracotta"], "color_hex": ["#808000", "#C19A6B", "#E2725B"], "effet": "Naturel énergique", "description": "Pour nature: stabilité authenticité bien-être"},
        {"occasion": "famille", "colors": ["Rose Corail", "Moutarde", "Kaki"], "color_hex": ["#FF7F50", "#E1AD01", "#C3B091"], "effet": "Chaleur accueillante", "description": "Pour moments: douceur solide radiance"}
    ]
}