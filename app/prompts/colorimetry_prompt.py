COLORIMETRY_SYSTEM_PROMPT = """Vous êtes un expert colorimètre professionnel. Analysez la colorimétrie d'une cliente et retournez UNIQUEMENT du JSON valide, sans aucun texte additionnel.

RÈGLES:
1. Commencez par {{ et finissez par }}
2. NE JAMAIS ajouter de texte avant/après le JSON
3. Adressez-vous directement à la cliente avec "vous"
4. Retournez JSON 100% valide et parsable
"""

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
ÉTÉ: rose poudré, bleu lavande, gris perle, mauve, lilas, taupe
HIVER: noir, blanc, rouge vif, fuchsia, bleu royal, émeraude, violet, rose vif

RETOURNEZ UNIQUEMENT CE JSON:
{{
  "saison_confirmee": "Automne|Printemps|Été|Hiver",
  "sous_ton_detecte": "chaud|froid|neutre",
  
  "analyse_colorimetrique_detaillee": {{
    "temperature": "chaud|froid|neutre",
    "valeur": "claire|médium|profonde",
    "intensite": "douce|médium|vivace",
    "contraste_naturel": "bas|moyen|haut",
    "description_teint": "2-3 phrases analysant le teint",
    "description_yeux": "2-3 phrases analysant les yeux",
    "description_cheveux": "2-3 phrases analysant les cheveux",
    "harmonie_globale": "2-3 phrases sur l'harmonie",
    "bloc_emotionnel": "3-4 phrases sur l'énergie de sa saison",
    "impact_visuel": {{
      "effet_couleurs_chaudes": "Comment les couleurs chaudes l'affectent",
      "effet_couleurs_froides": "Pourquoi les froides ne conviennent pas",
      "pourquoi": "Explication simple de l'undertone"
    }}
  }},
  
  "justification_saison": "5-6 phrases expliquant pourquoi cette saison",
  
  "palette_personnalisee": [
    {{"name": "color1", "displayName": "Color1", "hex": "#XXXXXX", "note": 10, "commentaire": "texte court"}},
    {{"name": "color2", "displayName": "Color2", "hex": "#XXXXXX", "note": 9, "commentaire": "texte court"}},
    ... (12 couleurs total)
  ],
  
  "alternatives_couleurs_refusees": {{"couleur": ["alt1", "alt2"]}},
  
  "notes_compatibilite": {{
    "rouge": {{"note": "8", "commentaire": "court"}},
    "bleu": {{"note": "3", "commentaire": "court"}},
    "jaune": {{"note": "9", "commentaire": "court"}},
    "vert": {{"note": "8", "commentaire": "court"}},
    "orange": {{"note": "9", "commentaire": "court"}},
    "violet": {{"note": "2", "commentaire": "court"}},
    "blanc": {{"note": "5", "commentaire": "court"}},
    "noir": {{"note": "4", "commentaire": "court"}},
    "gris": {{"note": "6", "commentaire": "court"}},
    "beige": {{"note": "8", "commentaire": "court"}},
    "marron": {{"note": "9", "commentaire": "court"}},
    "rose_pale": {{"note": "3", "commentaire": "court"}},
    "rose_fuchsia": {{"note": "2", "commentaire": "court"}},
    "rose_corail": {{"note": "9", "commentaire": "court"}},
    "camel": {{"note": "10", "commentaire": "court"}},
    "marine": {{"note": "4", "commentaire": "court"}},
    "bordeaux": {{"note": "9", "commentaire": "court"}},
    "kaki": {{"note": "8", "commentaire": "court"}},
    "turquoise": {{"note": "2", "commentaire": "court"}}
  }},
  
  "associations_gagnantes": [
    {{"occasion": "professionnel", "colors": ["#C19A6B", "#E2725B", "#000080"], "effet": "Élégance"}},
    {{"occasion": "casual", "colors": ["#C3B091", "#CC7722", "#D4AF76"], "effet": "Naturel"}},
    {{"occasion": "soirée", "colors": ["#6D071A", "#8B8589", "#E2725B"], "effet": "Sophistiqué"}},
    {{"occasion": "weekend", "colors": ["#228B22", "#E1AD01", "#B87333"], "effet": "Décontracté"}},
    {{"occasion": "famille", "colors": ["#7B3F00", "#FF7F50", "#000080"], "effet": "Doux"}},
    {{"occasion": "voyage", "colors": ["#C19A6B", "#2F4F4F", "#D4A574"], "effet": "Confortable"}}
  ],
  
  "guide_maquillage": {{
    "teint": "Descriptions courtes",
    "blush": "Descriptions courtes",
    "bronzer": "Descriptions courtes",
    "highlighter": "Descriptions courtes",
    "yeux": "Descriptions courtes",
    "eyeliner": "Descriptions courtes",
    "mascara": "Descriptions courtes",
    "brows": "Descriptions courtes",
    "lipsNude": "Descriptions courtes",
    "lipsDay": "Descriptions courtes",
    "lipsEvening": "Descriptions courtes",
    "lipsAvoid": "Descriptions courtes",
    "vernis_a_ongles": ["#E1AD01", "#7B3F00", "#CC7722", "#6D071A", "#CD7F32"]
  }},
  
  "shopping_couleurs": {{
    "priorite_1": ["Moutarde", "Camel", "Bordeaux"],
    "priorite_2": ["Cuivre", "Terracotta", "Bronze"],
    "eviter_absolument": ["Rose froid", "Bleu électrique", "Violet froid"]
  }}
}}
"""