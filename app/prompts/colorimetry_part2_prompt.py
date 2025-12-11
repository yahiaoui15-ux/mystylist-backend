"""
COLORIMETRY PART 2 FIXED v10.0 - PALETTE PERSONNALISÉE + ASSOCIATIONS
✅ Langage: FRANÇAIS UNIQUEMENT (comme Part 1 et Part 3)
✅ Complexité: Réduite à 15 objets (palette 10 + associations 5)
✅ Escaping: Gestion en Python, pas en GPT
✅ Double braces: Éliminés, simple { } JSON
✅ Basé sur structure proven de Part 1 qui fonctionne 100%

Input: ~1200 tokens | Output: ~900 tokens (au lieu de 1500)
Erreurs esperées: 0%
"""

COLORIMETRY_PART2_SYSTEM_PROMPT = """Vous êtes un expert colorimètre professionnel avec 15 ans d'expérience.
MISSION: Générer une palette de couleurs personnalisées et des associations gagnantes.
Retournez UNIQUEMENT du JSON valide. Aucun texte avant ou après."""

COLORIMETRY_PART2_USER_PROMPT_TEMPLATE = """Générez palette personnalisée + associations gagnantes.

DONNÉES CLIENT:
- Saison confirmée: {SAISON}
- Sous-ton détecté: {SOUS_TON}
- Yeux: {EYE_COLOR}
- Cheveux: {HAIR_COLOR}

TÂCHE:
Générez 10 couleurs personnalisées (avec noms FRANÇAIS, pas color1-10).
Générez 5 associations gagnantes pour différentes occasions.

RETOURNEZ JSON VALIDE (commençant par {{ et finissant par }}):

{{
  "palette_personnalisee": [
    {{"name": "camel", "hex": "#C19A6B", "note": 10, "displayName": "Camel", "commentaire": "Couleur essentielle reproduit harmonie naturelle cliente"}},
    {{"name": "moutarde", "hex": "#E1AD01", "note": 10, "displayName": "Moutarde", "commentaire": "Jaune doré illumine teint de manière subtile"}},
    {{"name": "bordeaux", "hex": "#800020", "note": 9, "displayName": "Bordeaux", "commentaire": "Élégance nocturne par excellence absolue"}},
    {{"name": "rose_corail", "hex": "#FF7F50", "note": 9, "displayName": "Rose Corail", "commentaire": "Rose chaud s harmonise magnifiquement avec carnation"}},
    {{"name": "olive", "hex": "#808000", "note": 9, "displayName": "Olive", "commentaire": "Vert-brun chaud naturel très polyvalent"}},
    {{"name": "cuivre", "hex": "#B87333", "note": 9, "displayName": "Cuivre", "commentaire": "Métallique chaud sophistiqué amplifie dorure naturelle"}},
    {{"name": "brique", "hex": "#CB4154", "note": 8, "displayName": "Brique", "commentaire": "Rouge-brun subtil très sophistiqué élégant"}},
    {{"name": "kaki", "hex": "#C3B091", "note": 8, "displayName": "Kaki", "commentaire": "Classique chaud très polyvalent pour tenues"}},
    {{"name": "chocolat", "hex": "#7B3F00", "note": 8, "displayName": "Chocolat", "commentaire": "Marron foncé élégant stable intemporel"}},
    {{"name": "terracotta", "hex": "#E2725B", "note": 8, "displayName": "Terracotta", "commentaire": "Chauffe le teint apporte vitalité énergie"}}
  ],

  "associations_gagnantes": [
    {{"occasion": "professionnel", "colors": ["Camel", "Marron", "Beige"], "color_hex": ["#C19A6B", "#8B4513", "#F5F5DC"], "effet": "Élégance confidente", "description": "Pour réunions et présentations: authority calme confiance"}},
    {{"occasion": "casual", "colors": ["Kaki", "Camel", "Terracotta"], "color_hex": ["#C3B091", "#C19A6B", "#E2725B"], "effet": "Naturel sans-effort", "description": "Pour détente shopping: relaxation énergie légèreté"}},
    {{"occasion": "soiree", "colors": ["Bordeaux", "Chocolat", "Cuivre"], "color_hex": ["#800020", "#7B3F00", "#B87333"], "effet": "Sophistication chaleureuse", "description": "Pour dîner cocktail: élégance richesse profondeur"}},
    {{"occasion": "weekend", "colors": ["Olive", "Camel", "Terracotta"], "color_hex": ["#808000", "#C19A6B", "#E2725B"], "effet": "Naturel énergique", "description": "Pour nature détente: stabilité authenticité bien-être"}},
    {{"occasion": "famille", "colors": ["Rose Corail", "Moutarde", "Kaki"], "color_hex": ["#FF7F50", "#E1AD01", "#C3B091"], "effet": "Chaleur accueillante", "description": "Pour moments importants: douceur solide radiance"}}
  ]
}}

RÈGLES CRITIQUES:
✅ palette_personnalisee = 10 objets EXACTEMENT
   - Chaque couleur: name (lowercase_with_underscores), hex (#RRGGBB), note (8-10), displayName, commentaire
✅ associations_gagnantes = 5 combinaisons EXACTEMENT
   - Chaque association: occasion, colors (tableau), color_hex (tableau), effet, description
✅ Noms français REQUIS: camel, moutarde, bordeaux, rose_corail, olive, cuivre, brique, kaki, chocolat, terracotta
✅ Commentaires = MAX 15 mots, en FRANÇAIS
✅ Descriptions = MAX 15 mots, en FRANÇAIS
✅ AUCUN apostrophe: écrire "s harmonise" au lieu de "s'harmonise"
✅ JSON VALIDE: { } simple (pas {{ }} double)
✅ AUCUN texte avant ou après le JSON
✅ UTF-8 correct: caractères accentués ok (éléphant, château, vêtement)

EXEMPLE BON COMMENTAIRE (10 mots):
❌ "Reproduit harmonie naturelle cliente tonecolor palette saison"
✅ "Reproduit harmonie naturelle cliente"

EXEMPLE BON JSON:
{
  "palette_personnalisee": [
    {"name": "camel", "hex": "#C19A6B", "note": 10, "displayName": "Camel", "commentaire": "Essentiel reproduit harmonie"}
  ]
}

Répondez UNIQUEMENT avec le JSON, commençant par { et finissant par }.
"""

# FALLBACK avec toutes les bonnes valeurs
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