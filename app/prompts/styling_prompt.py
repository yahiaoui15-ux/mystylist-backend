"""
STYLING PROMPT FIXED v2.2 - Archétypes PERSONNALISÉS + primaryArchetype + essenceShort
✅ Archétypes adaptés à Automne/Chaud/Silhouette O
✅ primaryArchetype = meilleur style pour ce client
✅ essenceShort = essence du style en phrase courte
✅ Page 16 du rapport remplie correctement
✅ essenceShort: 'Vous incarnez...'. Valorisant et personnel.

STYLING_SYSTEM_PROMPT = """Expert stylistique personnel. Générez profil stylistique complet.
Retournez UNIQUEMENT JSON valide, sans texte avant/après."""

STYLING_USER_PROMPT = """Créez profil stylistique PERSONNALISÉ pour client.

CLIENT ANALYSIS:
Saison colorimetrie: {season}
Sous-ton: {sous_ton}
Type silhouette: {silhouette_type}
Palette couleurs: {palette}

TÂCHE CRITIQUE:
1. Générez 5 archétypes PERSONNALISÉS (pas génériques)
   - Adaptés à {season}/Chaud/{silhouette_type}
   - Avec descriptions uniques pour ce client
   - EN FRANÇAIS

2. Générez primaryArchetype = LE MEILLEUR style pour ce client
   - Basé sur saison + silhouette + palette

3. Générez essenceShort = essence du style en 1-2 phrases courtes
   - Décrit l'identité stylistique du client
   - EN FRANÇAIS

JSON REQUIS:
{{
  "style": {{
    "archetypes": [
      {{
        "name": "Classique Chaud",
        "description": "Élégance intemporelle avec palette chaude naturelle"
      }},
      {{
        "name": "Bohème Sophistiqué",
        "description": "Confortable et authentique avec touches élégantes"
      }},
      {{
        "name": "Minimaliste Chaleureux",
        "description": "Épuré et harmonieux en tons chauds naturels"
      }},
      {{
        "name": "Casual Chic",
        "description": "Décontracté stylisé avec définition à la taille"
      }},
      {{
        "name": "Urbain Raffiné",
        "description": "Moderne et structuré en palette automne riche"
      }}
    ],
    "primaryArchetype": "Classique Chaud",
    "essenceShort": "Élégance naturelle chaleureuse. Intemporelle avec courbes valorisées."
  }},

  "shopping_guide": {{
    "budget_recommended": "1500-2500€",
    "priority_pieces": ["Jean taille haute", "Blazer structurant", "Basiques camel/bordeaux", "Chaussures talon fin"],
    "where_to_shop": ["Zara", "ASOS", "COS", "Mango"],
    "tips": "Privilégier coupes ajustées, matières fluides, couleurs chaudes"
  }},

  "capsule_wardrobe": [
    {{"piece": "Jean taille haute", "color": "#2C1810", "why": "Allonge jambes, structure silhouette O"}},
    {{"piece": "T-shirt blanc", "color": "#FFFFFF", "why": "Basique incontournable"}},
    {{"piece": "Blazer camel", "color": "#C19A6B", "why": "Couleur clé palette, crée verticalité"}},
    {{"piece": "Pantalon noir", "color": "#000000", "why": "Classique polyvalent"}},
    {{"piece": "Cardigan moutarde", "color": "#E1AD01", "why": "Couleur statement, très polyvalent"}}
  ],

  "outfits": [
    {{
      "name": "Bureau confiance",
      "pieces": ["Blazer camel", "Pantalon noir", "T-shirt blanc"],
      "description": "Élégance professionnelle et authority"
    }},
    {{
      "name": "Weekend détente",
      "pieces": ["Jean taille haute", "Cardigan moutarde", "Baskets blanches"],
      "description": "Confort et style naturel"
    }},
    {{
      "name": "Soirée sophistiquée",
      "pieces": ["Robe bordeaux", "Veste camel", "Talons fins"],
      "description": "Sophistication chaleureuse et profondeur"
    }},
    {{
      "name": "Casual chic",
      "pieces": ["Jean", "Pull olive", "Blazer clair"],
      "description": "Élégance décontractée quotidienne"
    }},
    {{
      "name": "Famille conviviale",
      "pieces": ["Robe rose corail", "Cardigan camel", "Loafers"],
      "description": "Chaleur et féminité naturelle"
    }}
  ]
}}

RÈGLES CRITIQUES:
✅ archetypes = 5 EXACTEMENT
   - name: court (1-2 mots)
   - description: courte en FRANÇAIS adaptée au client
   - Personnalisés à {season}/Chaud/{silhouette_type}

✅ primaryArchetype = 1 string
   - Le meilleur archetype pour ce client
   - Cohérent avec la palette et silhouette

✅ essenceShort = 1-2 phrases courtes EN FRANÇAIS
   - Essence du style du client
   - Mencione saison + caractéristique principale

✅ Noms d'archétypes variés:
   - Éviter "Classic", "Minimalist", etc (trop génériques)
   - Utiliser "Classique Chaud", "Bohème Sophistiqué", etc (personnalisé)

✅ JSON valide complet

Répondez UNIQUEMENT le JSON.
"""