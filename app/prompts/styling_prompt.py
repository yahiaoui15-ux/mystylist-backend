STYLING_SYSTEM_PROMPT = """Vous êtes un expert en styling personnel.
Créez un profil stylistique complet basé sur les analyses.
Retournez UNIQUEMENT du JSON valide, sans texte avant/après."""

STYLING_USER_PROMPT = """Créez le profil stylistique complet basé sur ces analyses.

COLORIMETRIE:
- Saison: {season}
- Palette: {palette}

MORPHOLOGIE:
- Silhouette: {silhouette_type}
- Recommandations: {recommendations}

RETOURNEZ UNIQUEMENT CE JSON:
{{
  "archetypes": ["classique", "boheme", "sportif"],
  
  "capsule_wardrobe": [
    {{"piece": "Jean bleu", "color": "#1E3A5F", "why": "Basique"}},
    {{"piece": "T-shirt blanc", "color": "#FFFFFF", "why": "Incontournable"}},
    {{"piece": "Blazer neutre", "color": "#8B8B8B", "why": "Structurant"}},
    {{"piece": "Pantalon noir", "color": "#000000", "why": "Classique"}},
    {{"piece": "Cardigan", "color": "#D2B48C", "why": "Polyvalent"}}
  ],
  
  "mix_and_match_formulas": [
    {{
      "name": "Bureau chic",
      "pieces": ["Blazer", "Pantalon noir", "T-shirt blanc"],
      "colors": ["#8B8B8B", "#000000", "#FFFFFF"],
      "description": "Elegance professionnelle"
    }},
    {{
      "name": "Weekend",
      "pieces": ["Jean", "Pull", "Baskets"],
      "colors": ["#1E3A5F", "#D2B48C", "#FFFFFF"],
      "description": "Confort et style"
    }},
    {{
      "name": "Soiree",
      "pieces": ["Robe noire", "Veste", "Talons"],
      "colors": ["#000000", "#505050", "#000000"],
      "description": "Sophistication"
    }}
  ],
  
  "shopping_guide": {{
    "budget_recommended": "2000€",
    "priority_pieces": ["Jean", "Blazer", "Basiques", "Chaussures"],
    "where_to_shop": ["ASOS", "Uniqlo", "Zara"],
    "tips": "Investir dans les basiques"
  }},
  
  "occasions": [
    {{"occasion": "Bureau", "formula": "Bureau chic"}},
    {{"occasion": "Weekend", "formula": "Weekend"}},
    {{"occasion": "Soiree", "formula": "Soiree"}}
  ]
}}
"""