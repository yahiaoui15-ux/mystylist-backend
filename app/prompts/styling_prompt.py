"""
STYLING PROMPT FIXED v2.0 - Archétypes + essenceShort + primaryArchetype
✅ Génère la structure "style" avec archétypes personnalisés
✅ Inclut primaryArchetype (meilleur archétype pour client)
✅ Inclut essenceShort (essence du style en une phrase)
"""

STYLING_SYSTEM_PROMPT = """Vous êtes un expert en styling personnel.
Créez un profil stylistique complet basé sur les analyses colorimétrie et morphologie.
Retournez UNIQUEMENT du JSON valide, sans texte avant/après."""

STYLING_USER_PROMPT = """Créez le profil stylistique COMPLET basé sur ces analyses.

COLORIMETRIE:
- Saison: {season}
- Palette personnalisée: {palette}

MORPHOLOGIE:
- Type silhouette: {silhouette_type}
- Recommandations: {recommendations}

PRÉFÉRENCES CLIENT:
- Style: {style_preferences}
- Marques: {brand_preferences}

RETOURNEZ UNIQUEMENT CE JSON (structure complète):
{{
  "style": {{
    "archetypes": [
      {{"name": "Classic Chic", "description": "Timeless elegant pieces"}},
      {{"name": "Romantic", "description": "Soft feminine details"}},
      {{"name": "Bohemian", "description": "Free spirited natural"}},
      {{"name": "Minimalist", "description": "Clean simple lines"}},
      {{"name": "Natural Casual", "description": "Effortless comfortable"}}
    ],
    "primaryArchetype": "Classic Chic",
    "essenceShort": "Sophisticated warmth with timeless elegance"
  }},
  
  "capsule_wardrobe": [
    {{"piece": "Jean classique", "color": "#1E3A5F", "why": "Basique incontournable"}},
    {{"piece": "T-shirt blanc", "color": "#FFFFFF", "why": "Fond de garde-robe"}},
    {{"piece": "Blazer structurant", "color": "#8B8B8B", "why": "Élégance professionnelle"}},
    {{"piece": "Pantalon noir", "color": "#000000", "why": "Classique polyvalent"}},
    {{"piece": "Cardigan chaud", "color": "#C3B091", "why": "Couche polyvalente"}}
  ],
  
  "mix_and_match_formulas": [
    {{
      "name": "Bureau élégant",
      "pieces": ["Blazer", "Pantalon noir", "T-shirt blanc"],
      "colors": ["#8B8B8B", "#000000", "#FFFFFF"],
      "description": "Élégance professionnelle et confiance"
    }},
    {{
      "name": "Weekend décontracté",
      "pieces": ["Jean", "Cardigan", "Baskets blanches"],
      "colors": ["#1E3A5F", "#C3B091", "#FFFFFF"],
      "description": "Confort et style naturel"
    }},
    {{
      "name": "Soirée sophistiquée",
      "pieces": ["Robe noire", "Veste structure", "Talons"],
      "colors": ["#000000", "#505050", "#2C2C2C"],
      "description": "Sophistication et présence"
    }},
    {{
      "name": "Casual chic",
      "pieces": ["Jean", "Pull cosy", "Blazer clair"],
      "colors": ["#1E3A5F", "#C3B091", "#D2B48C"],
      "description": "Élégance décontractée du quotidien"
    }},
    {{
      "name": "Brunch amies",
      "pieces": ["Robe portefeuille", "Cardigan léger", "Loafers"],
      "colors": ["#E2725B", "#D2B48C", "#8B4513"],
      "description": "Chaleur et féminité naturelle"
    }}
  ],
  
  "shopping_guide": {{
    "budget_recommended": "1500-2500€",
    "priority_pieces": ["Jean classique", "Blazer neutre", "Basiques blancs", "Chaussures confortables"],
    "where_to_shop": ["Zara", "ASOS", "Uniqlo", "mango", "COS"],
    "tips": "Privilégier la qualité des basiques et investir dans les coupes bien coupées"
  }},
  
  "occasions": [
    {{"occasion": "Bureau", "formula": "Bureau élégant"}},
    {{"occasion": "Weekend", "formula": "Weekend décontracté"}},
    {{"occasion": "Soirée", "formula": "Soirée sophistiquée"}},
    {{"occasion": "Casual", "formula": "Casual chic"}},
    {{"occasion": "Social", "formula": "Brunch amies"}}
  ]
}}

INSTRUCTIONS (CRITICAL):
1. STRUCTURE "style": Générer style.archetypes, style.primaryArchetype, style.essenceShort
   - archetypes: Tableau de 5 archétypes (objets avec name + description)
   - primaryArchetype: Le MEILLEUR archétype pour ce client basé sur saison + silhouette (string)
   - essenceShort: Description courte (max 10 mots) de l'essence du style du client
2. Adapter les archétypes et essenceShort à la saison: {season} et silhouette: {silhouette_type}
3. capsule_wardrobe: 5 pièces essentielles avec couleurs de la palette
4. mix_and_match_formulas: 5 combinaisons pour différentes occasions
5. ALL descriptions en FRANÇAIS
6. Escape apostrophes: s\\'harmonise
7. MANDATORY: Start {{, end }}. NO TEXT BEFORE OR AFTER JSON.
"""