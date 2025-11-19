"""
COLORIMETRY PART 1 ENRICHI - Saison + Palette + Analyses détaillées
Input: ~2200 tokens | Output: ~1400 tokens
Justifications: 40-50 mots (spécifiques client, PAS génériques)
"""

COLORIMETRY_PART1_SYSTEM_PROMPT = """Vous êtes expert colorimètre senior. Générez analyses SPÉCIFIQUES et DÉTAILLÉES par client, jamais génériques. Retournez UNIQUEMENT JSON valide."""

COLORIMETRY_PART1_USER_PROMPT = """Analysez colorimétrie - SAISON, PALETTE, ANALYSES DÉTAILLÉES.

CLIENT SPÉCIFIQUE:
- Photo: {face_photo_url}
- Yeux: {eye_color}
- Cheveux: {hair_color}
- Âge: {age}

RETOURNEZ:
{{
  "saison_confirmee": "Automne|Printemps|Été|Hiver",
  "sous_ton_detecte": "chaud|froid|neutre",
  
  "justification_saison": "40-50 mots DÉTAILLÉS analysant:
    - Pigmentation spécifique de la carnation (riche/dorée/pale/olivâtre?)
    - Comment yeux {eye_color} impactent la saison
    - Comment cheveux {hair_color} confirment/contredisent
    - Contraste naturel observé
    Exemple BON: 'Votre carnation dorée-olive avec reflets chauds + yeux marron foncé créent harmonie automne. Cheveux brun-chaud confirment sous-ton chaud. Contraste moyen typique Automne riche.'
    Exemple MAUVAIS: 'Votre carnation présente des caractéristiques harmonieuses.' - TROP VAGUE!",
    
  "eye_color": "{eye_color}",
  "hair_color": "{hair_color}",
  
  "palette_personnalisee": [
    {{
      "name": "couleur",
      "hex": "#HEX",
      "note": 10,
      "commentaire": "30 mots SPÉCIFIQUES:
        - Effet EXACT sur ce client (illumine carnation dorée? renforce contraste?)
        - POURQUOI fonctionne (référencer yeux/cheveux/sous-ton)
        - Cas d'usage (près visage? sur corps?)
        Exemple: 'Moutarde dore illumine carnation riche car amplifie undertone naturellement chaud. Crée pont optique avec yeux marron foncé, fait briller reflets. Blond froid à éviter avec cette couleur.'
        PAS: 'Sublime car harmonise bien.'"
    }},
    ... 11 autres (12 TOTAL - TOUTES les couleurs)
  ],
  
  "analyse_colorimetrique_detaillee": {{
    "temperature": "chaud|froid|neutre",
    "valeur": "clair|moyen|fonce",
    "intensite": "douce|medium|intense",
    "contraste_naturel": "faible|moyen|fort",
    
    "description_teint": "30 mots SPÉCIFIQUES:
      - Tonalité exacte (dorée? olive? rose?)
      - Saturation (riche? pâle?)
      - Uniformité (homogène? taches?)
      Exemple: 'Carnation olive-dorée saturée, uniforme. Reflets chauds prédominants. Sous-ton clairement chaud sans ambiguïté.'
      PAS: 'Votre teint présente des caractéristiques harmonieuses.'",
    
    "description_yeux": "25 mots SPÉCIFIQUES sur {eye_color}:
      - Nuance exacte
      - Clarté/intensité
      - Impact sur saison
      Exemple: 'Yeux marron-foncé saturés, pas clairs. Concentration pigment = ancrage automne. Aucune teinte frappante.'",
    
    "description_cheveux": "25 mots SPÉCIFIQUES sur {hair_color}:
      - Nuance/tonalité
      - Éclat
      - Alignement avec saison
      Exemple: 'Cheveux brun-foncé chauds, pas blonds. Reflets dorés/rouille. Renforce clearly le profil automne chaud.'",
    
    "harmonie_globale": "40 mots: Comment teint+yeux+cheveux = HARMONIE COHÉRENTE:
      Exemple: 'Trois éléments (carnation olive-dorée + yeux marron + cheveux brun chaud) créent trinité cohérente automne. Aucune contradiction. Contraste naturel ~70% qui confirme saison. Profil très net, non ambigu.'",
    
    "bloc_emotionnel": "30 mots: Impact ÉMOTIONNEL de cette saison sur ce client:
      Exemple: 'Votre Automne apporte luminosité douce (pas harshness), confiance subtle (pas drama). Permet looks sophistiqués sans effort car harmonie naturelle.'",
    
    "impact_visuel": {{
      "effet_couleurs_chaudes": "30 mots SPÉCIFIQUE: Quel EXACT impact sur THIS client?
        Exemple: 'Réchauffent votre carnation olive (la rendent dorée-chaude). Amplifient yeux marron. Créent cohésion globale.'
        PAS: 'Illuminent votre teint'",
      
      "effet_couleurs_froides": "30 mots: Quel EXACT problème sur THIS client?
        Exemple: 'Ternissent carnation dorée (la rendent grisâtre-fade). Isolent yeux marron (font contraste heurté). Créent apparence désharmonisée.'",
      
      "pourquoi": "20 mots: SCIENCE du pourquoi:
        Exemple: 'Sous-ton chaud naturel = besoin harmonie chaleureuse. Couleurs froides = opposition pigmentaire crée désaccord.'"
    }}
  }}
}}

RÈGLES QUALITÉ:
✅ CHAQUE description = 25-50 mots SPÉCIFIQUES (pas génériques!)
✅ Référencer CLIENT par nom ou yeux/cheveux
✅ Utiliser vocabulaire PRÉCIS (doré, olivâtre, saturé, chaud, etc.)
✅ Éviter: "harmonieuses", "typiques", "complètent" - phrases creuses
✅ Incluire: observations réelles (carnation riche? pâle? dorée?)
✅ JSON valide complet
✅ ZÉRO texte avant/après
"""