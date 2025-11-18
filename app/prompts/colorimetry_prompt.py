COLORIMETRY_SYSTEM_PROMPT = """Vous êtes un expert colorimètre professionnel. Analysez la colorimétrie d'une cliente et retournez UNIQUEMENT un JSON valide, sans texte additionnel.

⚠️ IMPORTANT - ADRESSEZ-VOUS DIRECTEMENT À LA CLIENTE:
- Utilisez toujours "vous" et le tutoiement direct
- N'écrivez JAMAIS "la cliente", "elle", "son", "sa", "cette femme", etc.
"""

COLORIMETRY_USER_PROMPT = """Analysez cette photo pour la colorimétrie complète de la cliente.

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

RETOURNEZ CE JSON (12 couleurs palette + toutes les sections obligatoires):
{{
  "saison_confirmee": "Automne ou Printemps ou Été ou Hiver",
  "sous_ton_detecte": "chaud ou froid ou neutre",
  
  "analyse_colorimetrique_detaillee": {{
    "temperature": "chaud ou froid ou neutre",
    "valeur": "claire ou médium ou profonde",
    "intensite": "douce ou médium ou vivace",
    "contraste_naturel": "bas ou moyen ou haut",
    "description_teint": "Votre teint...",
    "description_yeux": "Vos yeux...",
    "description_cheveux": "Vos cheveux...",
    "harmonie_globale": "Harmonie...",
    "bloc_emotionnel": "L'énergie de votre saison...",
    "impact_visuel": {{
      "effet_couleurs_chaudes": "Les couleurs chaudes...",
      "effet_couleurs_froides": "Les couleurs froides...",
      "pourquoi": "Explication: vous avez..."
    }}
  }},
  
  "justification_saison": "6-7 phrases pourquoi cette saison vous convient",
  
  "palette_personnalisee": [
    {{"name": "moutarde", "displayName": "Moutarde", "hex": "#E1AD01", "note": 10, "commentaire": "Sublime"}},
    {{"name": "cuivre", "displayName": "Cuivre", "hex": "#B87333", "note": 9, "commentaire": "Réchauffe"}},
    {{"name": "olive", "displayName": "Olive", "hex": "#808000", "note": 9, "commentaire": "Harmonise"}},
    {{"name": "terracotta", "displayName": "Terracotta", "hex": "#E2725B", "note": 10, "commentaire": "Parfait"}},
    {{"name": "camel", "displayName": "Camel", "hex": "#C19A6B", "note": 10, "commentaire": "Incontournable"}},
    {{"name": "chocolat", "displayName": "Chocolat", "hex": "#7B3F00", "note": 9, "commentaire": "Élégant"}},
    {{"name": "bordeaux", "displayName": "Bordeaux", "hex": "#6D071A", "note": 9, "commentaire": "Sophistiqué"}},
    {{"name": "kaki", "displayName": "Kaki", "hex": "#C3B091", "note": 8, "commentaire": "Naturel"}},
    {{"name": "ocre", "displayName": "Ocre", "hex": "#CC7722", "note": 9, "commentaire": "Illumine"}},
    {{"name": "bronze", "displayName": "Bronze", "hex": "#CD7F32", "note": 10, "commentaire": "Magnifie"}},
    {{"name": "rouille", "displayName": "Rouille", "hex": "#B7410E", "note": 8, "commentaire": "Signature"}},
    {{"name": "brique", "displayName": "Brique", "hex": "#CB4154", "note": 8, "commentaire": "Caractère"}}
  ],
  
  "alternatives_couleurs_refusees": {{"couleur": ["alt1", "alt2"]}},
  
  "notes_compatibilite": {{
    "rouge": {{"note": "8", "commentaire": "Brique"}},
    "bleu": {{"note": "3", "commentaire": "Froid"}},
    "jaune": {{"note": "9", "commentaire": "Doré"}},
    "vert": {{"note": "8", "commentaire": "Chaud"}},
    "orange": {{"note": "9", "commentaire": "Harmonie"}},
    "violet": {{"note": "2", "commentaire": "À éviter"}},
    "blanc": {{"note": "5", "commentaire": "Neutre"}},
    "noir": {{"note": "4", "commentaire": "Dur"}},
    "gris": {{"note": "6", "commentaire": "Taupe"}},
    "beige": {{"note": "8", "commentaire": "Excellent"}},
    "marron": {{"note": "9", "commentaire": "Parfait"}},
    "rose_pale": {{"note": "3", "commentaire": "Froid"}},
    "rose_fuchsia": {{"note": "2", "commentaire": "Éviter"}},
    "rose_corail": {{"note": "9", "commentaire": "Sublime"}},
    "camel": {{"note": "10", "commentaire": "Incontournable"}},
    "marine": {{"note": "4", "commentaire": "Non"}},
    "bordeaux": {{"note": "9", "commentaire": "Parfait"}},
    "kaki": {{"note": "8", "commentaire": "Bon"}},
    "turquoise": {{"note": "2", "commentaire": "Non"}}
  }},
  
  "associations_gagnantes": [
    {{"occasion": "professionnel", "colors": ["#C19A6B", "#E2725B", "#000080"], "effet": "Élégance"}},
    {{"occasion": "casual", "colors": ["#C3B091", "#CC7722", "#D4AF76"], "effet": "Naturel"}},
    {{"occasion": "soirée", "colors": ["#6D071A", "#8B8589", "#E2725B"], "effet": "Sophistication"}},
    {{"occasion": "weekend", "colors": ["#228B22", "#E1AD01", "#B87333"], "effet": "Décontracté"}},
    {{"occasion": "famille", "colors": ["#7B3F00", "#FF7F50", "#000080"], "effet": "Doux"}},
    {{"occasion": "voyage", "colors": ["#C19A6B", "#2F4F4F", "#D4A574"], "effet": "Confortable"}}
  ],
  
  "guide_maquillage": {{
    "teint": "Fond teint doré",
    "blush": "pêche, abricot, corail chaud",
    "bronzer": "bronze doré, terracotta",
    "highlighter": "or champagne",
    "yeux": "terre cuite, bronze, cuivre, kaki, doré",
    "eyeliner": "marron, bronze, kaki",
    "mascara": "marron noir",
    "brows": "brun chaud auburn",
    "lipsNude": "beige rosé, brun",
    "lipsDay": "rose corail, pêche",
    "lipsEvening": "bordeaux, rouge brique",
    "lipsAvoid": "rose froid, fuchsia",
    "vernis_a_ongles": ["#E1AD01", "#7B3F00", "#CC7722", "#6D071A", "#CD7F32"]
  }},
  
  "shopping_couleurs": {{
    "priorite_1": ["Moutarde", "Camel", "Bordeaux"],
    "priorite_2": ["Cuivre", "Terracotta", "Bronze"],
    "eviter_absolument": ["Rose froid", "Bleu électrique", "Violet froid"]
  }}
}}
"""