COLORIMETRY_SYSTEM_PROMPT = """Vous êtes un expert colorimètre professionnel.

INSTRUCTIONS STRICTES:
1. Retournez UNIQUEMENT du JSON valide
2. Commencez par { et finissez par }
3. N'ajoutez AUCUN texte avant ou après le JSON
4. ESCAPPEZ tous les caractères spéciaux:
   - Apostrophes: L'harmonie → L\\'harmonie
   - Guillemets internes: "dit-elle" → \\"dit-elle\\"
   - Retours à la ligne: utilisez \\n
   - Antislash: C:\\ → C:\\\\
5. Vérifiez chaque virgule entre éléments
6. Validez votre JSON avant de l'envoyer

IMPORTANT: Je vais parser votre réponse comme du JSON strict.
Aucun texte ne doit exister en dehors des accolades {{ }}.
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

IMPORTANT: Échappez les caractères spéciaux comme indiqué dans le system prompt.

RETOURNEZ UNIQUEMENT CE JSON (sans aucun texte avant/après):
{{
  "saison_confirmee": "Automne|Printemps|Été|Hiver",
  "sous_ton_detecte": "chaud|froid|neutre",
  
  "analyse_colorimetrique_detaillee": {{
    "temperature": "chaud|froid|neutre",
    "valeur": "claire|médium|profonde",
    "intensite": "douce|médium|vivace",
    "contraste_naturel": "bas|moyen|haut",
    "description_teint": "Phrase simple sans apostrophes",
    "description_yeux": "Phrase simple sans apostrophes",
    "description_cheveux": "Phrase simple sans apostrophes",
    "harmonie_globale": "Phrase simple sans apostrophes",
    "bloc_emotionnel": "Paragraphe simple",
    "impact_visuel": {{
      "effet_couleurs_chaudes": "Texte simple",
      "effet_couleurs_froides": "Texte simple",
      "pourquoi": "Texte simple"
    }}
  }},
  
  "justification_saison": "Texte simple",
  
  "palette_personnalisee": [
    {{"name": "moutarde", "displayName": "Moutarde", "hex": "#E1AD01", "note": 10, "commentaire": "Sublime"}},
    {{"name": "cuivre", "displayName": "Cuivre", "hex": "#B87333", "note": 9, "commentaire": "Rechauffe"}},
    {{"name": "olive", "displayName": "Olive", "hex": "#808000", "note": 9, "commentaire": "Harmonise"}},
    {{"name": "terracotta", "displayName": "Terracotta", "hex": "#E2725B", "note": 10, "commentaire": "Parfait"}},
    {{"name": "camel", "displayName": "Camel", "hex": "#C19A6B", "note": 10, "commentaire": "Incontournable"}},
    {{"name": "chocolat", "displayName": "Chocolat", "hex": "#7B3F00", "note": 9, "commentaire": "Elegant"}},
    {{"name": "bordeaux", "displayName": "Bordeaux", "hex": "#6D071A", "note": 9, "commentaire": "Sophistique"}},
    {{"name": "kaki", "displayName": "Kaki", "hex": "#C3B091", "note": 8, "commentaire": "Naturel"}},
    {{"name": "ocre", "displayName": "Ocre", "hex": "#CC7722", "note": 9, "commentaire": "Illumine"}},
    {{"name": "bronze", "displayName": "Bronze", "hex": "#CD7F32", "note": 10, "commentaire": "Magnifie"}},
    {{"name": "rouille", "displayName": "Rouille", "hex": "#B7410E", "note": 8, "commentaire": "Signature"}},
    {{"name": "brique", "displayName": "Brique", "hex": "#CB4154", "note": 8, "commentaire": "Caractere"}}
  ],
  
  "alternatives_couleurs_refusees": {{"couleur": ["alt1", "alt2"]}},
  
  "notes_compatibilite": {{
    "rouge": {{"note": "8", "commentaire": "Brique"}},
    "bleu": {{"note": "3", "commentaire": "Froid"}},
    "jaune": {{"note": "9", "commentaire": "Dore"}},
    "vert": {{"note": "8", "commentaire": "Chaud"}},
    "orange": {{"note": "9", "commentaire": "Harmonie"}},
    "violet": {{"note": "2", "commentaire": "Eviter"}},
    "blanc": {{"note": "5", "commentaire": "Neutre"}},
    "noir": {{"note": "4", "commentaire": "Dur"}},
    "gris": {{"note": "6", "commentaire": "Taupe"}},
    "beige": {{"note": "8", "commentaire": "Bon"}},
    "marron": {{"note": "9", "commentaire": "Parfait"}},
    "rose_pale": {{"note": "3", "commentaire": "Froid"}},
    "rose_fuchsia": {{"note": "2", "commentaire": "Non"}},
    "rose_corail": {{"note": "9", "commentaire": "Sublime"}},
    "camel": {{"note": "10", "commentaire": "Oui"}},
    "marine": {{"note": "4", "commentaire": "Non"}},
    "bordeaux": {{"note": "9", "commentaire": "Parfait"}},
    "kaki": {{"note": "8", "commentaire": "Bon"}},
    "turquoise": {{"note": "2", "commentaire": "Non"}}
  }},
  
  "associations_gagnantes": [
    {{"occasion": "professionnel", "colors": ["#C19A6B", "#E2725B", "#000080"], "effet": "Elegance"}},
    {{"occasion": "casual", "colors": ["#C3B091", "#CC7722", "#D4AF76"], "effet": "Naturel"}},
    {{"occasion": "soiree", "colors": ["#6D071A", "#8B8589", "#E2725B"], "effet": "Sophistique"}},
    {{"occasion": "weekend", "colors": ["#228B22", "#E1AD01", "#B87333"], "effet": "Decontracte"}},
    {{"occasion": "famille", "colors": ["#7B3F00", "#FF7F50", "#000080"], "effet": "Doux"}},
    {{"occasion": "voyage", "colors": ["#C19A6B", "#2F4F4F", "#D4A574"], "effet": "Confortable"}}
  ],
  
  "guide_maquillage": {{
    "teint": "Dore",
    "blush": "Peche, corail",
    "bronzer": "Bronze",
    "highlighter": "Or",
    "yeux": "Cuivre, bronze",
    "eyeliner": "Marron",
    "mascara": "Noir",
    "brows": "Brun",
    "lipsNude": "Beige",
    "lipsDay": "Rose corail",
    "lipsEvening": "Bordeaux",
    "lipsAvoid": "Rose froid",
    "vernis_a_ongles": ["#E1AD01", "#7B3F00", "#CC7722", "#6D071A", "#CD7F32"]
  }},
  
  "shopping_couleurs": {{
    "priorite_1": ["Moutarde", "Camel", "Bordeaux"],
    "priorite_2": ["Cuivre", "Terracotta", "Bronze"],
    "eviter_absolument": ["Rose froid", "Bleu froid", "Violet froid"]
  }}
}}
"""