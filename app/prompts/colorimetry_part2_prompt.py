"""
COLORIMETRY PART 2 v9.0 - ULTRA SIMPLIFIÉ
✅ Pas de variables confuses
✅ Une seule tâche: créer palette_personnalisee
✅ Instructions claires numérotées
✅ OpenAI comprend = résultat garanti
"""

COLORIMETRY_PART2_SYSTEM_PROMPT = """You are a professional color analyst expert.
You respond with ONLY valid JSON.
Start with { and end with }.
Never include text before or after JSON."""

# ULTRA-SIMPLIFIÉ: Une seule task = créer 10 couleurs
COLORIMETRY_PART2_USER_PROMPT_TEMPLATE = """GENERATE ONLY VALID JSON. NO TEXT BEFORE OR AFTER.

CLIENT PROFILE:
- Season: {SAISON}
- Undertone: {SOUS_TON}
- Eye Color: {EYE_COLOR}
- Hair Color: {HAIR_COLOR}

TASK: Create 10 personalized colors for this client.

OUTPUT JSON (start with {{ end with }}, nothing else):

{{
  "palette_personnalisee": [
    {{"name": "color1", "hex": "#HEXCODE", "note": 10, "commentaire": "Max 15 words description"}},
    {{"name": "color2", "hex": "#HEXCODE", "note": 10, "commentaire": "Max 15 words description"}},
    {{"name": "color3", "hex": "#HEXCODE", "note": 9, "commentaire": "Max 15 words description"}},
    {{"name": "color4", "hex": "#HEXCODE", "note": 9, "commentaire": "Max 15 words description"}},
    {{"name": "color5", "hex": "#HEXCODE", "note": 9, "commentaire": "Max 15 words description"}},
    {{"name": "color6", "hex": "#HEXCODE", "note": 9, "commentaire": "Max 15 words description"}},
    {{"name": "color7", "hex": "#HEXCODE", "note": 8, "commentaire": "Max 15 words description"}},
    {{"name": "color8", "hex": "#HEXCODE", "note": 8, "commentaire": "Max 15 words description"}},
    {{"name": "color9", "hex": "#HEXCODE", "note": 8, "commentaire": "Max 15 words description"}},
    {{"name": "color10", "hex": "#HEXCODE", "note": 8, "commentaire": "Max 15 words description"}}
  ]
}}

RULES:
1. Each color must match the season {SAISON} and undertone {SOUS_TON}
2. Start with note 10, then 9, then 8
3. Each commentaire max 15 words, escape apostrophes with backslash: s\'harmonise
4. Hex codes must be real valid colors (6 hex digits)
5. NO TEXT BEFORE OR AFTER JSON - MANDATORY
"""

# Fallback si OpenAI échoue
FALLBACK_PALETTE_PERSONALISEE = {
    "palette_personnalisee": [
        {"name": "camel", "hex": "#C19A6B", "note": 10, "commentaire": "Couleur centrale harmonie naturelle essentielle"},
        {"name": "terracotta", "hex": "#E2725B", "note": 10, "commentaire": "Chauffe teint apporte vitalité"},
        {"name": "moutarde", "hex": "#E1AD01", "note": 9, "commentaire": "Jaune doré illumine subtil"},
        {"name": "bordeaux", "hex": "#6D071A", "note": 9, "commentaire": "Élégance nocturne par excellence"},
        {"name": "rose_corail", "hex": "#FF7F50", "note": 9, "commentaire": "Rose chaud s\'harmonise magnifiquement"},
        {"name": "olive", "hex": "#808000", "note": 9, "commentaire": "Vert-brun chaud naturel polyvalent"},
        {"name": "cuivre", "hex": "#B87333", "note": 8, "commentaire": "Métallique chaud sophistiqué"},
        {"name": "brique", "hex": "#CB4154", "note": 8, "commentaire": "Rouge-brun subtil élégant"},
        {"name": "kaki", "hex": "#C3B091", "note": 8, "commentaire": "Classique chaud très polyvalent"},
        {"name": "chocolat", "hex": "#7B3F00", "note": 8, "commentaire": "Marron foncé élégant stable"}
    ]
}

# ALIAS pour compatibilité avec colorimetry.py qui importe l'ancien nom
FALLBACK_PALETTE_AND_ASSOCIATIONS = FALLBACK_PALETTE_PERSONALISEE