COLORIMETRY_SYSTEM_PROMPT = """Vous êtes un expert colorimètre professionnel qui génère UNIQUEMENT du JSON valide.

RÈGLES ABSOLUES:
1. RÉPONDEZ AVEC UNIQUEMENT DU JSON VALIDE - ZÉRO texte avant ou après
2. Commencez par { et finissez strictement par }
3. VALIDEZ chaque virgule, guillemet et accolade
4. Ignorez complètement le texte libre - STRUCTURE SEULEMENT
5. Si doutes, renvoyez structure minimale valide

JAMAIS:
- Texte avant ou après JSON
- Apostrophes non échappées
- Clés de style dictionnaire dans arrays
- Accolades ou virgules mal placées
"""

COLORIMETRY_USER_PROMPT = """Analysez cette photo pour la colorimétrie STRICT JSON UNIQUEMENT.

DONNÉES:
- Photo: {face_photo_url}
- Yeux: {eye_color}
- Cheveux: {hair_color}
- Âge: {age}
- Couleurs refusées: {unwanted_colors}

RETOURNEZ UNIQUEMENT CE JSON EXACT (structure à copier):

{
  "saison_confirmee": "Automne",
  "sous_ton_detecte": "chaud",
  "justification_saison": "Analyse basée sur votre carnation, yeux et cheveux",
  "palette_personnalisee": [
    {"name": "moutarde", "hex": "#E1AD01", "note": 10, "commentaire": "Sublime"},
    {"name": "cuivre", "hex": "#B87333", "note": 9, "commentaire": "Rechauffe"},
    {"name": "olive", "hex": "#808000", "note": 9, "commentaire": "Harmonise"},
    {"name": "terracotta", "hex": "#E2725B", "note": 10, "commentaire": "Parfait"},
    {"name": "camel", "hex": "#C19A6B", "note": 10, "commentaire": "Incontournable"},
    {"name": "chocolat", "hex": "#7B3F00", "note": 9, "commentaire": "Elegant"},
    {"name": "bordeaux", "hex": "#6D071A", "note": 9, "commentaire": "Sophistique"},
    {"name": "kaki", "hex": "#C3B091", "note": 8, "commentaire": "Naturel"},
    {"name": "ocre", "hex": "#CC7722", "note": 9, "commentaire": "Illumine"},
    {"name": "bronze", "hex": "#CD7F32", "note": 10, "commentaire": "Magnifie"},
    {"name": "rouille", "hex": "#B7410E", "note": 8, "commentaire": "Signature"},
    {"name": "brique", "hex": "#CB4154", "note": 8, "commentaire": "Caractere"}
  ],
  "notes_compatibilite": {
    "rouge": {"note": "8", "commentaire": "Brique"},
    "bleu": {"note": "3", "commentaire": "Froid"},
    "jaune": {"note": "9", "commentaire": "Dore"},
    "vert": {"note": "8", "commentaire": "Chaud"},
    "orange": {"note": "9", "commentaire": "Harmonie"},
    "violet": {"note": "2", "commentaire": "Eviter"},
    "blanc": {"note": "5", "commentaire": "Neutre"},
    "noir": {"note": "4", "commentaire": "Dur"},
    "gris": {"note": "6", "commentaire": "Taupe"},
    "beige": {"note": "8", "commentaire": "Bon"},
    "marron": {"note": "9", "commentaire": "Parfait"},
    "rose_pale": {"note": "3", "commentaire": "Froid"},
    "rose_fuchsia": {"note": "2", "commentaire": "Non"},
    "rose_corail": {"note": "9", "commentaire": "Sublime"},
    "camel": {"note": "10", "commentaire": "Oui"},
    "marine": {"note": "4", "commentaire": "Non"},
    "bordeaux": {"note": "9", "commentaire": "Parfait"},
    "kaki": {"note": "8", "commentaire": "Bon"},
    "turquoise": {"note": "2", "commentaire": "Non"}
  },
  "associations_gagnantes": [
    {"occasion": "professionnel", "colors": ["#C19A6B", "#E2725B", "#000080"], "effet": "Elegance"},
    {"occasion": "casual", "colors": ["#C3B091", "#CC7722", "#D4AF76"], "effet": "Naturel"},
    {"occasion": "soiree", "colors": ["#6D071A", "#8B8589", "#E2725B"], "effet": "Sophistique"},
    {"occasion": "weekend", "colors": ["#228B22", "#E1AD01", "#B87333"], "effet": "Decontracte"},
    {"occasion": "famille", "colors": ["#7B3F00", "#FF7F50", "#000080"], "effet": "Doux"}
  ],
  "guide_maquillage": {
    "teint": "Dore",
    "blush": "Peche corail",
    "bronzer": "Bronze",
    "highlighter": "Or",
    "yeux": "Cuivre bronze",
    "eyeliner": "Marron",
    "mascara": "Noir",
    "brows": "Brun",
    "lipsNude": "Beige",
    "lipsDay": "Rose corail",
    "lipsEvening": "Bordeaux",
    "lipsAvoid": "Rose froid",
    "vernis_a_ongles": ["#E1AD01", "#7B3F00", "#CC7722", "#6D071A", "#CD7F32"]
  },
  "shopping_couleurs": {
    "priorite_1": ["Moutarde", "Camel", "Bordeaux"],
    "priorite_2": ["Cuivre", "Terracotta", "Bronze"],
    "eviter_absolument": ["Rose froid", "Bleu froid", "Violet froid"]
  },
  "alternatives_couleurs_refusees": {"couleur": []},
  "analyse_colorimetrique_detaillee": {
    "temperature": "chaud",
    "valeur": "medium",
    "intensite": "douce",
    "contraste_naturel": "moyen",
    "description_teint": "Teint harmonieux avec carnation riche",
    "description_yeux": "Yeux qui s'harmonisent avec la palette",
    "description_cheveux": "Cheveux complementant le profil colorimetrique",
    "harmonie_globale": "Ensemble coherent et harmonieux",
    "bloc_emotionnel": "Votre profil colorimetrique apporte luminosite et confiance",
    "impact_visuel": {
      "effet_couleurs_chaudes": "Illumine et rechauffe le teint",
      "effet_couleurs_froides": "Ternit et affaiblit l'eclat",
      "pourquoi": "Sous-ton naturel chaud necessitant harmonie chaude"
    }
  }
}

VALIDATIONS OBLIGATOIRES:
- Commencez par { et finissez par }
- Tous les { doivent avoir un }
- Toutes les [ doivent avoir un ]
- Chaque objet dans array est un objet JSON complet
- Pas de virgule apres le dernier element d'un array/objet
"""