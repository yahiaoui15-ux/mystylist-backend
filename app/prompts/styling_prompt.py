STYLING_SYSTEM_PROMPT = """Vous êtes un expert en styling personnel avec 20 ans d'expérience.

MISSION: Générer un profil stylistique complet qui combine:
- Analyse colorimétrie (saison, palette)
- Analyse morphologie (silhouette, recommandations)
- Préférences personnelles
- Guide d'achat et formules mix&match

Créer une garde-robe capsule de 25 pièces essentielles ET 10 formules complètes de mix&match.

REPONSE EN JSON VALIDE UNIQUEMENT - PAS D'AUTRES TEXTE."""

STYLING_USER_PROMPT = """Basé sur ces analyses, créez le profil stylistique complet.

COLORIMETRIE:
- Saison: {season}
- Palette: {palette}
- Guide maquillage: {guide_maquillage}

MORPHOLOGIE:
- Silhouette: {silhouette_type}
- Recommandations: {recommendations}

PREFERENCES:
- Style personnel: {style_preferences}
- Marques préférées: {brand_preferences}

REPONDEZ AVEC CE JSON (ET RIEN D'AUTRE):
{{
  "archetypes": ["classique", "bohème", "moderne"],
  "capsule_wardrobe": [
    {{
      "piece": "Jean bleu brut",
      "color": "#1E3A5F",
      "why": "Basique indispensable...",
      "occasions": ["casual", "weekend"]
    }}
  ],
  "mix_and_match_formulas": [
    {{
      "name": "Formule 1 - Bureau chic",
      "pieces": ["Blazer camel", "Pantalon noir", "T-shirt blanc", "Escarpins noirs"],
      "colors": ["#C19A6B", "#000000", "#FFFFFF"],
      "description": "Élégance professionnelle..."
    }},
    {{
      "name": "Formule 2 - Weekend décontracté",
      "pieces": ["Jean skinny", "Pull oversize", "Baskets blanches", "Sac à main"],
      "colors": ["#1E3A5F", "#8B4513"],
      "description": "Confort et style..."
    }},
    {{
      "name": "Formule 3 - Soirée",
      "pieces": ["Robe noire", "Veste blazer", "Talons"],
      "colors": ["#000000"],
      "description": "Sophistication..."
    }},
    {{
      "name": "Formule 4 - Casual élégant",
      "pieces": ["Chemise lin", "Pantalon chino", "Loafers"],
      "colors": ["#F5DEB3", "#E6D7C3"],
      "description": "Intemporel et confortable..."
    }},
    {{
      "name": "Formule 5 - Rendez-vous",
      "pieces": ["Robe fluide", "Cardigan", "Ballerines"],
      "colors": ["#D4A5A5", "#8B7355"],
      "description": "Féminine et douce..."
    }},
    {{
      "name": "Formule 6 - Sports-chic",
      "pieces": ["Legging", "Hoodie", "Baskets sport"],
      "colors": ["#000000", "#505050"],
      "description": "Trendy et confortable..."
    }},
    {{
      "name": "Formule 7 - Dîner en ville",
      "pieces": ["Pantalon habillé", "Top paillettes", "Escarpins"],
      "colors": ["#000000", "#C0C0C0"],
      "description": "Élégance urbaine..."
    }},
    {{
      "name": "Formule 8 - Brunch avec amies",
      "pieces": ["Robe courte", "Blazer loose", "Sandales",  "Sac à main"],
      "colors": ["#FF69B4", "#FFFFFF"],
      "description": "Frais et joyeux..."
    }},
    {{
      "name": "Formule 9 - Réunion importante",
      "pieces": ["Costume tailleur", "Chemise unie", "Talons fermés", "Montre"],
      "colors": ["#1A1A1A", "#F5F5DC"],
      "description": "Professionnalisme maximal..."
    }},
    {{
      "name": "Formule 10 - Détente à la maison",
      "pieces": ["Pantalon large", "Pull confortable", "Chaussettes douces", "Cardignat"],
      "colors": ["#D2B48C", "#A9A9A9"],
      "description": "Confort absolu..."
    }}
  ],
  "shopping_guide": {{
    "budget_recommended": "2000-3000€ pour capsule complète",
    "priority_pieces": ["Jean", "Blanc basique", "Blazer", "Chaussures neutres"],
    "where_to_shop": ["ASOS", "Cos", "Uniqlo", "Zara"],
    "tips": "Investir dans les basiques, puis ajouter pièces tendance"
  }},
  "occasions": [
    {{"occasion": "Bureau", "formula": "Formule 1"}},
    {{"occasion": "Weekend", "formula": "Formule 2"}},
    {{"occasion": "Soirée", "formula": "Formule 3"}}
  ]
}}"""