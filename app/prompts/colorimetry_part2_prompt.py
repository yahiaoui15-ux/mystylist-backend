"""
COLORIMETRY PART 2 ENRICHI - Maquillage + Associations spécifiques
Input: ~1400 tokens | Output: ~1600 tokens
"""

COLORIMETRY_PART2_SYSTEM_PROMPT = """Vous êtes expert colorimètre + maquillage. Générez recommandations DÉTAILLÉES et SPÉCIFIQUES. Retournez UNIQUEMENT JSON valide."""

COLORIMETRY_PART2_USER_PROMPT = """Complétez colorimétrie (Part 2) - Maquillage + Associations spécifiques.

CONTEXTE CLIENT:
- Saison: {saison_confirmee}
- Sous-ton: {sous_ton_detecte}
- Top couleurs palette: {palette_names}

RETOURNEZ:
{{
  "notes_compatibilite": {{
    "rouge": {{"note": "8", "commentaire": "25 mots: Rouges chauds (brique/terracotta) harmonisent sous-ton chaud. Froids bleutés créent dissonance. ÉVITER: rouge vif froid."}},
    "bleu": {{"note": "3", "commentaire": "25 mots: Blus froids ternissent carnation sous-ton chaud, isolent yeux, affaiblissent présence. Navy très problématique. Zéro bleu froid recommandé."}},
    "jaune": {{"note": "9", "commentaire": "25 mots: Jaunes dorés amplifient or naturel carnation, illuminent instantanément. Créent pont avec sous-ton. PRÉFÉRER dorés moutarde/ambrés à citrons pâles froids."}},
    "vert": {{"note": "8", "commentaire": "25 mots: Verts chauds (olive/kaki/sauge) harmonisent palette naturelle. Acides froids créent contraste heurté. Vert pastel = non recommandé."}},
    "orange": {{"note": "9", "commentaire": "25 mots: Oranges chaudes amplifient vitalité sous-ton. Terracotta/corail magnifient. Créent harmonie instantanée. Éviter: orange pâle désaturé."}},
    "violet": {{"note": "2", "commentaire": "25 mots: Violets TOUJOURS problématiques sous-ton chaud. Froids = pire. Même mauve froid ternit présence, crée fatigue. Absolument déconseillé."}},
    "blanc": {{"note": "5", "commentaire": "25 mots: Blanc pur crée micro-contraste heurté, légèrement durcissant. Crème/écru/ivoire mieux acceptés. Blanc contextuel seulement."}},
    "noir": {{"note": "4", "commentaire": "25 mots: Noir pur trop dur contraste. Charbon/marron foncé plus flatteurs. Noir acceptable seulement si maquillage riche ou couleur chaleureuse proche."}},
    "gris": {{"note": "6", "commentaire": "25 mots: Gris taupe chauds OK. Gris froids bleutés problématiques. Gris moyen acceptable secondaire. Non couleur principale recommandée."}},
    "beige": {{"note": "8", "commentaire": "25 mots: Beiges/camels chauds flattent carnation, créent continuation naturelle. PRÉFÉRER caramel-doré à grisâtre. Excellent choix intemporel."}},
    "marron": {{"note": "9", "commentaire": "25 mots: Marrons chauds (chocolat/cognac) intensifient yeux, harmonisent cheveux naturellement. Meilleure couleur neutre pour ce profil."}},
    "rose_pale": {{"note": "2", "commentaire": "25 mots: Rose pâle froid (mauve/lilas) ternit carnation chauds, fatigue instantanément. Absolument déconseillé près visage."}},
    "rose_fuchsia": {{"note": "1", "commentaire": "25 mots: Fuchsia froid crée dissonance extrême sous-ton chaud. Repousser visuellement présence. JAMAIS recommandé pour ce client."}},
    "rose_corail": {{"note": "9", "commentaire": "25 mots: Rose corail chaud (NOT froid pâle) s'harmonise magnifiquement. Amplifie vitalité, crée look frais sans casser cohésion."}},
    "camel": {{"note": "10", "commentaire": "25 mots: Camel ESSENTIEL pour ce profil. Reproduit harmonie naturelle exactement. Incontournable investissement. Fonctionne TOUTES occasions."}},
    "marine": {{"note": "3", "commentaire": "25 mots: Marine bleu froid crée contraste désharmonisé malgré 'classique'. Ternit sous-ton chaud. Charbon/navy = problématiques."}},
    "bordeaux": {{"note": "9", "commentaire": "25 mots: Bordeaux chaud rouge-brun sophistiqué s'harmonise parfaitement. Crée profondeur élégante. Excellent choix événementiel."}},
    "kaki": {{"note": "8", "commentaire": "25 mots: Kaki chaud complète sous-ton, crée harmonie terreuse rappelant palette innée. Excellent couleur signature personnelle."}},
    "turquoise": {{"note": "1", "commentaire": "25 mots: Turquoise froide incompatible total sous-ton chaud. Crée clash visuel majeur, isole présence. Absolument éviter."}}
  }},
  
  "allColorsWithNotes": [
    {{"name": "jaune", "note": 9, "hex": "#FFFF00", "commentaire": "Jaunes dorés = meilleur ami palette. Amplifient or naturel. Pâles citrons destructeurs."}},
    {{"name": "rouge", "note": 8, "hex": "#FF0000", "commentaire": "Rouges chauds (brique) magnifient. Froids bleutés isolent. Éviter vif froid."}},
    {{"name": "vert", "note": 8, "hex": "#008000", "commentaire": "Verts chauds harmonisent naturel. Acides froids destructeurs. Olive = meilleure."}},
    {{"name": "bleu", "note": 3, "hex": "#0000FF", "commentaire": "Bleus froids ternissent carnation. Navy problématique. Zéro recommandation."}}
  ],
  
  "associations_gagnantes": [
    {{
      "occasion": "professionnel",
      "colors": ["#C19A6B", "#E2725B", "#8B4513"],
      "effet": "Élégance confidente",
      "description": "Camel + Terracotta + Marron = trinité professionnelle harmonieuse. Crée présence-sérénité. Yeux brillent. Recommandé réunions/présentations clés."
    }},
    {{
      "occasion": "casual",
      "colors": ["#C3B091", "#CC7722", "#D2B48C"],
      "effet": "Naturel sans-effort",
      "description": "Kaki + Ocre + Doré clair = look décontracté mais intentionnel. Harmonie facile. Brunch/shopping/daily optimal."
    }},
    {{
      "occasion": "soiree",
      "colors": ["#6D071A", "#8B8589", "#E2725B"],
      "effet": "Sophistication chaleureuse",
      "description": "Bordeaux + Taupe + Terracotta = soirée élégante sans froideur. Crée mystère + chaleur. Événements formels idéaux."
    }},
    {{
      "occasion": "weekend",
      "colors": ["#228B22", "#E1AD01", "#B87333"],
      "effet": "Détente avec caractère",
      "description": "Vert olive + Moutarde + Cuivre = weekend confiant. Facile à porter. Crée signature personnelle sans effort."
    }},
    {{
      "occasion": "famille",
      "colors": ["#7B3F00", "#E2725B", "#C3B091"],
      "effet": "Douceur naturelle",
      "description": "Chocolat + Terracotta + Kaki = harmonie familiale. Approchable + stylée. Aucune impression d'effort. Photos flatteuses."
    }}
  ],
  
  "guide_maquillage": {{
    "teint": "Doré (riche, pas pâle)",
    "blush": "Pêche corail chaud (PAS rose pâle froid)",
    "bronzer": "Bronze chaud (PAS shimmer froid)",
    "highlighter": "Or (crée luminosité naturelle sous-ton)",
    "yeux": "Cuivre/bronze/terre (amplifient marron foncé)",
    "eyeliner": "Marron chaud (plus flatteur que noir pur)",
    "mascara": "Noir (acceptable ici, apporte définition)",
    "brows": "Brun chaud naturel (PAS noirs, PAS blonds)",
    "lipsNude": "Beige chaud doré (crème/ivoire désaturés)",
    "lipsDay": "Rose corail CHAUD (pêche-corail, non pâle)",
    "lipsEvening": "Bordeaux riche (sophistiqué élégant)",
    "lipsAvoid": "Rose pâle froid, fuchsia, mauve, nude grisâtre",
    "vernis_a_ongles": ["#E1AD01 (moutarde)", "#7B3F00 (chocolat)", "#CC7722 (ocre)", "#6D071A (bordeaux)"]
  }},
  
  "shopping_couleurs": {{
    "priorite_1": ["Moutarde", "Camel", "Bordeaux"],
    "priorite_2": ["Cuivre", "Terracotta", "Bronze"],
    "eviter_absolument": ["Rose pâle froid", "Bleu marine/froid", "Violet", "Turquoise", "Fuchsia"]
  }},
  
  "alternatives_couleurs_refusees": {{}}
}}

RÈGLES:
✅ Chaque commentaire = 25 mots MINIMUM (détail, pourquoi, impact)
✅ Spécifique client ({saison_confirmee}, yeux/cheveux référencés)
✅ Pas générique ("harmonise bien" = INTERDIT)
✅ ÉVITER/PAS dans chaque note
✅ JSON valide complet
✅ ZÉRO texte avant/après
"""