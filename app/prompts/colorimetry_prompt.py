COLORIMETRY_SYSTEM_PROMPT = """Vous êtes un expert colorimètre professionnel. Analysez la colorimétrie d'une cliente et retournez UNIQUEMENT un JSON valide, sans texte additionnel."""

COLORIMETRY_USER_PROMPT = """Analysez cette photo pour la colorimétrie de la cliente.

DONNÉES:
- Photo: {face_photo_url}
- Yeux: {eye_color}
- Cheveux: {hair_color}
- Âge: {age}
- Couleurs refusées: {unwanted_colors}

SAISONS:
AUTOMNE: moutarde, cuivre, olive, terracotta, camel, chocolat, bordeaux, kaki, ocre, bronze, rouille, brique
PRINTEMPS: corail, pêche, turquoise clair, vert pomme, jaune doré, rose saumon, bleu ciel, abricot
ÉTÉ: rose poudré, bleu lavande, gris perle, mauve, bleu ciel pâle, rose antique, lilas, taupe
HIVER: noir, blanc, rouge vif, fuchsia, bleu royal, émeraude, violet profond, rose vif

RETOURNEZ CE JSON (ET RIEN D'AUTRE):
{{
  "saison_confirmee": "Automne|Printemps|Été|Hiver",
  "sous_ton_detecte": "chaud|froid|neutre",
  "justification_saison": "6-7 phrases expliquant pourquoi cette saison",
  "palette_personnalisee": [
    {{"name": "moutarde", "displayName": "Moutarde", "hex": "#E1AD01", "note": 10, "commentaire": "Sublime votre teint"}},
    {{"name": "cuivre", "displayName": "Cuivre", "hex": "#B87333", "note": 9, "commentaire": "Réchauffe carnation"}},
    {{"name": "olive", "displayName": "Olive", "hex": "#808000", "note": 9, "commentaire": "Harmonise tons chauds"}},
    {{"name": "terracotta", "displayName": "Terracotta", "hex": "#E2725B", "note": 10, "commentaire": "Parfait palette automne"}},
    {{"name": "camel", "displayName": "Camel", "hex": "#C19A6B", "note": 10, "commentaire": "Incontournable pour vous"}},
    {{"name": "chocolat", "displayName": "Chocolat", "hex": "#7B3F00", "note": 9, "commentaire": "Élégant flatteur"}},
    {{"name": "bordeaux", "displayName": "Bordeaux", "hex": "#6D071A", "note": 9, "commentaire": "Sophistiqué teint chaud"}},
    {{"name": "kaki", "displayName": "Kaki", "hex": "#C3B091", "note": 8, "commentaire": "Naturel polyvalent"}},
    {{"name": "ocre", "displayName": "Ocre", "hex": "#CC7722", "note": 9, "commentaire": "Illumine teint doré"}},
    {{"name": "bronze", "displayName": "Bronze", "hex": "#CD7F32", "note": 10, "commentaire": "Magnifie tons chauds"}},
    {{"name": "rouille", "displayName": "Rouille", "hex": "#B7410E", "note": 8, "commentaire": "Couleur signature automne"}},
    {{"name": "brique", "displayName": "Brique", "hex": "#CB4154", "note": 8, "commentaire": "Caractère look"}}
  ],
  "alternatives_couleurs_refusees": {{
    "couleur1": ["alt1", "alt2"]
  }},
  "notes_compatibilite": {{
    "rouge": {{"note": "8", "commentaire": "Brique chaud sublime"}},
    "bleu": {{"note": "3", "commentaire": "Froid contraste mal"}},
    "jaune": {{"note": "9", "commentaire": "Jaune doré parfait"}},
    "vert": {{"note": "8", "commentaire": "Vert chaud excellent"}},
    "orange": {{"note": "9", "commentaire": "Orange chaud harmonie"}},
    "violet": {{"note": "2", "commentaire": "Violet froid à éviter"}},
    "blanc": {{"note": "5", "commentaire": "Blanc neutre acceptable"}},
    "noir": {{"note": "4", "commentaire": "Noir trop dur"}},
    "gris": {{"note": "6", "commentaire": "Gris taupe mieux"}},
    "beige": {{"note": "8", "commentaire": "Beige chaud excellent"}},
    "marron": {{"note": "9", "commentaire": "Marron chaud parfait"}},
    "rose_pale": {{"note": "3", "commentaire": "Rose pâle froid"}},
    "rose_fuchsia": {{"note": "2", "commentaire": "Rose fuchsia à éviter"}},
    "rose_corail": {{"note": "9", "commentaire": "Corail chaud sublime"}},
    "camel": {{"note": "10", "commentaire": "Camel incontournable"}},
    "marine": {{"note": "4", "commentaire": "Marine froid mauvais"}},
    "bordeaux": {{"note": "9", "commentaire": "Bordeaux excellent"}},
    "kaki": {{"note": "8", "commentaire": "Kaki très bon"}},
    "turquoise": {{"note": "2", "commentaire": "Turquoise froid mauvais"}}
  }},
  "associations_gagnantes": [
    {{"occasion": "professionnel", "colors": ["#C19A6B", "#E2725B", "#000080"], "effet": "Élégance autorité"}},
    {{"occasion": "casual", "colors": ["#C3B091", "#CC7722", "#D4AF76"], "effet": "Naturel chic"}},
    {{"occasion": "soirée", "colors": ["#6D071A", "#8B8589", "#E2725B"], "effet": "Sophistication"}},
    {{"occasion": "weekend", "colors": ["#228B22", "#E1AD01", "#B87333"], "effet": "Décontracté stylé"}},
    {{"occasion": "famille", "colors": ["#7B3F00", "#FF7F50", "#000080"], "effet": "Doux harmonieux"}}
  ],
  "guide_maquillage": {{
    "teint": "Fond teint sous-tons dorés, enlumineur or champagne",
    "blush": "pêche, abricot, corail chaud, terre cuite",
    "bronzer": "bronze doré, terracotta chaud",
    "highlighter": "or champagne, bronze clair, pêche lumineux",
    "yeux": "terre cuite, bronze, cuivre, kaki, doré chaud, moutarde",
    "eyeliner": "marron, bronze, kaki profond",
    "mascara": "marron noir adoucit regard",
    "brows": "brun chaud auburn",
    "lipsNude": "beige rosé, brun naturel",
    "lipsDay": "rose corail, pêche douce",
    "lipsEvening": "bordeaux profond, rouge brique",
    "lipsAvoid": "roses froids, fuchsia, mauves froids",
    "vernis_a_ongles": ["#E1AD01", "#7B3F00", "#CC7722", "#6D071A", "#CD7F32"]
  }},
  "shopping_couleurs": {{
    "priorite_1": ["Moutarde", "Camel", "Bordeaux"],
    "priorite_2": ["Cuivre", "Terracotta", "Bronze"],
    "eviter_absolument": ["Rose froid", "Bleu électrique", "Violet froid"]
  }}
}}"""