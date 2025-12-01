# -*- coding: utf-8 -*-
"""
COLORIMETRY PART 2 v2.1 - SIMPLIFIE & ROBUSTE
- Pas de {{ }} doubles - JSON direct
- Escaping strict des apostrophes
- Palette reduite 10 couleurs (au lieu de 12)
- Associations AUGMENTEES a 5 (professionnel, casual, soiree, weekend, famille)
"""

COLORIMETRY_PART2_SYSTEM_PROMPT = """Vous etes expert colorimetre. Generez UNIQUEMENT JSON valide parfait.
Commencez par { et terminez par }.
REGLE CRITIQUE: Echappez TOUTES les apostrophes avec backslash (\\') - Exemple: s\\'harmonise
Aucun texte avant/apres JSON."""

COLORIMETRY_PART2_USER_PROMPT_TEMPLATE = """PALETTE PERSONNALISEE - Part 2 colorimetrie.

DONNEES CLIENT:
Saison: {SAISON}
Sous-ton: {SOUS_TON}
Yeux: {EYE_COLOR}
Cheveux: {HAIR_COLOR}

RETOURNEZ UNIQUEMENT JSON VALIDE (PAS de doubles accolades - utiliser simples accolades directement):
{{
  "palette_personnalisee": [
    {{
      "name": "couleur1",
      "hex": "#HEX1",
      "note": 10,
      "commentaire": "15-20 mots specifiques au client"
    }},
    ...10 COULEURS MAXIMUM (jamais moins!)
  ],

  "allColorsWithNotes": [
    {{"name": "jaune", "note": 9, "hex": "#FFFF00", "commentaire": "Jaunes dores amplifient or naturel."}},
    {{"name": "rouge", "note": 8, "hex": "#FF0000", "commentaire": "Rouges chauds harmonisent. Froids ternissent."}},
    {{"name": "vert", "note": 8, "hex": "#008000", "commentaire": "Verts chauds harmonisent naturellement."}},
    {{"name": "bleu", "note": 3, "hex": "#0000FF", "commentaire": "Bleus froids isolent. A eviter absolument."}},
    {{"name": "orange", "note": 9, "hex": "#FFA500", "commentaire": "Orange chaud amplifie vitalite et eclat."}},
    {{"name": "violet", "note": 2, "hex": "#800080", "commentaire": "Violets froids ternissent presence naturelle."}},
    {{"name": "blanc", "note": 5, "hex": "#FFFFFF", "commentaire": "Blanc pur cree micro-contraste hurte."}},
    {{"name": "noir", "note": 4, "hex": "#000000", "commentaire": "Noir pur dur. Charbon plus flatteur."}},
    {{"name": "gris", "note": 6, "hex": "#808080", "commentaire": "Gris taupe OK. Gris froid non."}},
    {{"name": "beige", "note": 8, "hex": "#F5F5DC", "commentaire": "Beiges chauds flattent carnation doree."}},
    {{"name": "marron", "note": 9, "hex": "#8B4513", "commentaire": "Marrons chauds intensifient yeux."}},
    {{"name": "rose_pale", "note": 2, "hex": "#FFB6C1", "commentaire": "Rose pale froid ternit teint chaud."}},
    {{"name": "rose_fuchsia", "note": 1, "hex": "#FF20F0", "commentaire": "Fuchsia froid cree dissonance extreme."}},
    {{"name": "rose_corail", "note": 9, "hex": "#FF7F50", "commentaire": "Rose corail chaud s\\'harmonise magnifiquement."}},
    {{"name": "camel", "note": 10, "hex": "#C19A6B", "commentaire": "Camel essentiel. Reproduit harmonie naturelle."}},
    {{"name": "marine", "note": 3, "hex": "#000080", "commentaire": "Marine froid cree contraste desharmonise."}},
    {{"name": "bordeaux", "note": 9, "hex": "#800020", "commentaire": "Bordeaux chaud sophistique s\\'harmonise parfait."}},
    {{"name": "kaki", "note": 8, "hex": "#C3B091", "commentaire": "Kaki chaud complete sous-ton creant harmonie."}},
    {{"name": "turquoise", "note": 1, "hex": "#40E0D0", "commentaire": "Turquoise froide incompatible total."}}
  ],

  "associations_gagnantes": [
    {{
      "occasion": "professionnel",
      "colors": ["Terracotta", "Marron", "Camel"],
      "color_hex": ["#E2725B", "#8B4513", "#C3B091"],
      "effet": "Elegance confidente"
    }},
    {{
      "occasion": "casual",
      "colors": ["Kaki", "Ocre", "Camel"],
      "color_hex": ["#C3B091", "#CC7722", "#C19A6B"],
      "effet": "Naturel sans-effort"
    }},
    {{
      "occasion": "soiree",
      "colors": ["Bordeaux", "Gris Taupe", "Terracotta"],
      "color_hex": ["#6D071A", "#8B8589", "#E2725B"],
      "effet": "Sophistication chaleureuse",
      "description": "Harmonie riche et profonde qui respire l\\'elegance nocturne. Bordeaux apporte profondeur, gris taupe cree equilibre, terracotta ajoute chaleur. Parfait pour diners, cocktails, evenements ou vous souhaitez briller discretement avec raffinement."
    }},
    {{
      "occasion": "weekend",
      "colors": ["Olive", "Camel", "Terre"],
      "color_hex": ["#808000", "#C19A6B", "#D2B48C"],
      "effet": "Naturel energique",
      "description": "Harmonie detente et exploration qui evoque la nature. Olive apporte energie decontractee, camel cree harmonie, terre ajoute stabilite. Parfait pour sorties nature, randonnees, visites ou vous souhaitez confort et authenticite."
    }},
    {{
      "occasion": "famille",
      "colors": ["Rose Corail", "Beige", "Marron"],
      "color_hex": ["#FF7F50", "#F5F5DC", "#8B4513"],
      "effet": "Chaleur accueillante",
      "description": "Harmonie chaleureuse et bienveillante parfaite pour les moments importants. Rose corail apporte douceur, beige cree base rassurante, marron ajoute solidite. Ideal pour repas de famille, fetes, reunions ou vous souhaitez rayonner naturellement avec elegance."
    }}
  ]
}}

REGLES STRICTES - OBLIGATOIRE:
- palette_personnalisee = 10 COULEURS EXACTEMENT
- allColorsWithNotes = 19 couleurs FIXES (donnees ci-dessus)
- associations_gagnantes = 5 OCCASIONS (professionnel, casual, soiree, weekend, famille - CHAQUE avec description 40+ mots)
- ECHAPPER APOSTROPHES: s\\'harmonise (backslash-apostrophe)
- Pas d\\'accents accentues dans JSON - utiliser version plain: e au lieu de e accent
- JSON VALIDE COMPLET - Pas de caracteres de controle
- ZERO texte avant/apres JSON
"""

# Fallback hardcoded si OpenAI echoue - AVEC 5 ASSOCIATIONS
FALLBACK_PALETTE_AND_ASSOCIATIONS = {
    "palette_personnalisee": [
        {"name": "terracotta", "hex": "#E2725B", "note": 10, "commentaire": "Couleur centrale de votre palette. Apporte chaleur et luminosite au teint."},
        {"name": "camel", "hex": "#C19A6B", "note": 10, "commentaire": "Incontournable. Reproduit exactement l'harmonie naturelle de votre silhouette."},
        {"name": "moutarde", "hex": "#E1AD01", "note": 9, "commentaire": "Jaune dore chaud qui illumine le teint et renforce les yeux."},
        {"name": "cuivre", "hex": "#B87333", "note": 9, "commentaire": "Metalique chaud qui ajoute richesse et sophistication a votre palette."},
        {"name": "bordeaux", "hex": "#6D071A", "note": 9, "commentaire": "Couleur soiree par excellence. Profonde, elegante, chaleureuse."},
        {"name": "rose_corail", "hex": "#FF7F50", "note": 9, "commentaire": "Rose coral chaud qui s'harmonise magnifiquement avec votre teint."},
        {"name": "olive", "hex": "#808000", "note": 8, "commentaire": "Vert-brun chaud qui cree harmonies naturelles avec palette automne."},
        {"name": "brique", "hex": "#CB4154", "note": 8, "commentaire": "Rouge-brun chaud subtil et sophistique pour vos tenues."},
        {"name": "kaki", "hex": "#C3B091", "note": 8, "commentaire": "Couleur classique chaleureuse. Polyvalente pour toutes les saisons."},
        {"name": "chocolat", "hex": "#7B3F00", "note": 8, "commentaire": "Marron fonce qui cree base stable et elegante pour vos outfits."}
    ],
    "allColorsWithNotes": [
        {"name": "camel", "displayName": "Camel", "note": 10, "commentaire": "Camel essentiel. Reproduit harmonie naturelle.", "hex": "#C19A6B"},
        {"name": "jaune", "displayName": "Jaune", "note": 9, "commentaire": "Jaunes dores amplifient or naturel.", "hex": "#FFFF00"},
        {"name": "orange", "displayName": "Orange", "note": 9, "commentaire": "Orange chaud amplifie vitalite.", "hex": "#FFA500"},
        {"name": "marron", "displayName": "Marron", "note": 9, "commentaire": "Marrons chauds intensifient yeux.", "hex": "#8B4513"},
        {"name": "rose_corail", "displayName": "Rose Corail", "note": 9, "commentaire": "Rose corail chaud s'harmonise magnifiquement.", "hex": "#FF7F50"},
        {"name": "bordeaux", "displayName": "Bordeaux", "note": 9, "commentaire": "Bordeaux chaud sophistique s'harmonise parfait.", "hex": "#800020"},
        {"name": "rouge", "displayName": "Rouge", "note": 8, "commentaire": "Rouges chauds harmonisent. Froids ternissent.", "hex": "#FF0000"},
        {"name": "vert", "displayName": "Vert", "note": 8, "commentaire": "Verts chauds harmonisent. Acides froids non.", "hex": "#008000"},
        {"name": "beige", "displayName": "Beige", "note": 8, "commentaire": "Beiges chauds flattent carnation.", "hex": "#F5F5DC"},
        {"name": "kaki", "displayName": "Kaki", "note": 8, "commentaire": "Kaki chaud complete sous-ton creant harmonie.", "hex": "#C3B091"},
        {"name": "gris", "displayName": "Gris", "note": 6, "commentaire": "Gris taupe OK. Gris froid non.", "hex": "#808080"},
        {"name": "blanc", "displayName": "Blanc", "note": 5, "commentaire": "Blanc pur cree micro-contraste hurte.", "hex": "#FFFFFF"},
        {"name": "noir", "displayName": "Noir", "note": 4, "commentaire": "Noir pur dur. Charbon plus flatteur.", "hex": "#000000"},
        {"name": "bleu", "displayName": "Bleu", "note": 3, "commentaire": "Bleus froids isolent. A eviter absolument.", "hex": "#0000FF"},
        {"name": "marine", "displayName": "Marine", "note": 3, "commentaire": "Marine froid cree contraste desharmonise.", "hex": "#000080"},
        {"name": "violet", "displayName": "Violet", "note": 2, "commentaire": "Violets froids ternissent presence.", "hex": "#800080"},
        {"name": "rose_pale", "displayName": "Rose Pale", "note": 2, "commentaire": "Rose pale froid ternit teint chaud.", "hex": "#FFB6C1"},
        {"name": "rose_fuchsia", "displayName": "Rose Fuchsia", "note": 1, "commentaire": "Fuchsia froid cree dissonance extreme.", "hex": "#FF20F0"},
        {"name": "turquoise", "displayName": "Turquoise", "note": 1, "commentaire": "Turquoise froide incompatible total.", "hex": "#40E0D0"}
    ],
    "associations_gagnantes": [
        {
            "occasion": "professionnel",
            "colors": ["Terracotta", "Marron", "Camel"],
            "color_hex": ["#E2725B", "#8B4513", "#C3B091"],
            "effet": "Elegance confidente"
        },
        {
            "occasion": "casual",
            "colors": ["Kaki", "Ocre", "Camel"],
            "color_hex": ["#C3B091", "#CC7722", "#C19A6B"],
            "effet": "Naturel sans-effort"
        },
        {
            "occasion": "soiree",
            "colors": ["Bordeaux", "Gris Taupe", "Terracotta"],
            "color_hex": ["#6D071A", "#8B8589", "#E2725B"],
            "effet": "Sophistication chaleureuse",
            "description": "Harmonie riche et profonde qui respire l'elegance nocturne. Bordeaux apporte profondeur, gris taupe cree equilibre, terracotta ajoute chaleur. Parfait pour diners, cocktails, evenements ou vous souhaitez briller discretement avec raffinement."
        },
        {
            "occasion": "weekend",
            "colors": ["Olive", "Camel", "Terre"],
            "color_hex": ["#808000", "#C19A6B", "#D2B48C"],
            "effet": "Naturel energique",
            "description": "Harmonie detente et exploration qui evoque la nature. Olive apporte energie decontractee, camel cree harmonie, terre ajoute stabilite. Parfait pour sorties nature, randonnees, visites ou vous souhaitez confort et authenticite."
        },
        {
            "occasion": "famille",
            "colors": ["Rose Corail", "Beige", "Marron"],
            "color_hex": ["#FF7F50", "#F5F5DC", "#8B4513"],
            "effet": "Chaleur accueillante",
            "description": "Harmonie chaleureuse et bienveillante parfaite pour les moments importants. Rose corail apporte douceur, beige cree base rassurante, marron ajoute solidite. Ideal pour repas de famille, fetes, reunions ou vous souhaitez rayonner naturellement avec elegance."
        }
    ]
}