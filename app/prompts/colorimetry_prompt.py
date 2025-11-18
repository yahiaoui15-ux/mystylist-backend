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

RETOURNEZ CE JSON (ET RIEN D'AUTRE):
{
  "saison_confirmee": "Automne|Printemps|Été|Hiver",
  "sous_ton_detecte": "chaud|froid|neutre",
  
  "analyse_colorimetrique_detaillee": {
    "temperature": "chaud|froid|neutre",
    "valeur": "claire|médium|profonde",
    "intensite": "douce|médium|vivace",
    "contraste_naturel": "bas|moyen|haut",
    
    "description_teint": "2-3 phrases personnalisées analysant PRÉCISÉMENT le teint observé",
    "description_yeux": "2-3 phrases analysant les yeux en détail",
    "description_cheveux": "2-3 phrases analysant les cheveux",
    "harmonie_globale": "2-3 phrases expliquant pourquoi ces 3 éléments convergent",
    
    "bloc_emotionnel": "Paragraphe de 3-4 phrases expliquant ce que cela signifie pour elle",
    
    "impact_visuel": {
      "effet_couleurs_chaudes": "Explique comment les couleurs chaudes l'affectent",
      "effet_couleurs_froides": "Explique pourquoi les froides ne conviennent pas",
      "pourquoi": "Explication scientifique simple (ex: vous avez un undertone doré...)"
    }
  },
  
  "justification_saison": "6-7 phrases complètes expliquant pourquoi cette saison vous convient",
  
  "palette_personnalisee": [
    {"name": "moutarde", "displayName": "Moutarde", "hex": "#E1AD01", "note": 10, "commentaire": "Sublime votre teint"},
    {"name": "cuivre", "displayName": "Cuivre", "hex": "#B87333", "note": 9, "commentaire": "Réchauffe votre carnation"},
    {"name": "olive", "displayName": "Olive", "hex": "#808000", "note": 9, "commentaire": "Harmonise vos tons chauds"},
    {"name": "terracotta", "displayName": "Terracotta", "hex": "#E2725B", "note": 10, "commentaire": "Parfait pour votre palette d'automne"},
    {"name": "camel", "displayName": "Camel", "hex": "#C19A6B", "note": 10, "commentaire": "Incontournable pour vous"},
    {"name": "chocolat", "displayName": "Chocolat", "hex": "#7B3F00", "note": 9, "commentaire": "Élégant et flatteur pour votre teint"},
    {"name": "bordeaux", "displayName": "Bordeaux", "hex": "#6D071A", "note": 9, "commentaire": "Sophistiqué qui sublime votre teint chaud"},
    {"name": "kaki", "displayName": "Kaki", "hex": "#C3B091", "note": 8, "commentaire": "Naturel et polyvalent pour vous"},
    {"name": "ocre", "displayName": "Ocre", "hex": "#CC7722", "note": 9, "commentaire": "Illumine votre teint doré"},
    {"name": "bronze", "displayName": "Bronze", "hex": "#CD7F32", "note": 10, "commentaire": "Magnifie vos tons chauds"},
    {"name": "rouille", "displayName": "Rouille", "hex": "#B7410E", "note": 8, "commentaire": "Couleur signature pour votre automne"},
    {"name": "brique", "displayName": "Brique", "hex": "#CB4154", "note": 8, "commentaire": "Donne du caractère à votre look"}
  ],
  
  "alternatives_couleurs_refusees": {
    "couleur1": ["alt1", "alt2"]
  },
  
  "notes_compatibilite": {
    "rouge": {"note": "8", "commentaire": "Brique chaud vous sublime"},
    "bleu": {"note": "3", "commentaire": "Froid ne vous convient pas"},
    "jaune": {"note": "9", "commentaire": "Jaune doré vous met en valeur"},
    "vert": {"note": "8", "commentaire": "Vert chaud vous va excellemment"},
    "orange": {"note": "9", "commentaire": "Orange chaud crée une belle harmonie pour vous"},
    "violet": {"note": "2", "commentaire": "Violet froid à éviter pour vous"},
    "blanc": {"note": "5", "commentaire": "Blanc neutre reste acceptable pour vous"},
    "noir": {"note": "4", "commentaire": "Noir est trop dur pour vous"},
    "gris": {"note": "6", "commentaire": "Gris taupe vous convient mieux"},
    "beige": {"note": "8", "commentaire": "Beige chaud vous va excellemment"},
    "marron": {"note": "9", "commentaire": "Marron chaud vous met parfaitement en valeur"},
    "rose_pale": {"note": "3", "commentaire": "Rose pâle froid ne vous convient pas"},
    "rose_fuchsia": {"note": "2", "commentaire": "Rose fuchsia froid à éviter absolument"},
    "rose_corail": {"note": "9", "commentaire": "Corail chaud vous sublime"},
    "camel": {"note": "10", "commentaire": "Camel est incontournable pour vous"},
    "marine": {"note": "4", "commentaire": "Marine froid ne vous convient pas"},
    "bordeaux": {"note": "9", "commentaire": "Bordeaux vous convient parfaitement"},
    "kaki": {"note": "8", "commentaire": "Kaki est très bon pour vous"},
    "turquoise": {"note": "2", "commentaire": "Turquoise froid ne vous convient pas"}
  },
  
  "associations_gagnantes": [
    {"occasion": "professionnel", "colors": ["#C19A6B", "#E2725B", "#000080"], "effet": "Élégance autorité"},
    {"occasion": "casual", "colors": ["#C3B091", "#CC7722", "#D4AF76"], "effet": "Naturel chic"},
    {"occasion": "soirée", "colors": ["#6D071A", "#8B8589", "#E2725B"], "effet": "Sophistication"},
    {"occasion": "weekend", "colors": ["#228B22", "#E1AD01", "#B87333"], "effet": "Décontracté stylé"},
    {"occasion": "famille", "colors": ["#7B3F00", "#FF7F50", "#000080"], "effet": "Doux harmonieux"},
    {"occasion": "voyage", "colors": ["#C19A6B", "#2F4F4F", "#D4A574"], "effet": "Confortable élégant"}
  ],
  
  "guide_maquillage": {
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
  },
  
  "shopping_couleurs": {
    "priorite_1": ["Moutarde", "Camel", "Bordeaux"],
    "priorite_2": ["Cuivre", "Terracotta", "Bronze"],
    "eviter_absolument": ["Rose froid", "Bleu électrique", "Violet froid"]
  }
}
"""