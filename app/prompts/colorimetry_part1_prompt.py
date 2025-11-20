"""
COLORIMETRY PART 1 - Saison + Analyses détaillées (40-50 mots chaque)
Input: ~1400 tokens | Output: ~1200 tokens
"""

COLORIMETRY_PART1_SYSTEM_PROMPT = """Vous êtes expert colorimètre senior. Générez analyses TRÈS SPÉCIFIQUES au client, JAMAIS génériques. Chaque description doit référencer ses caractéristiques exactes. Retournez UNIQUEMENT JSON valide."""

COLORIMETRY_PART1_USER_PROMPT = """Analysez colorimétrie complète - SAISON, ANALYSES DÉTAILLÉES.

CLIENT SPÉCIFIQUE:
- Photo: {face_photo_url}
- Yeux: {eye_color}
- Cheveux: {hair_color}
- Âge: {age}

RETOURNEZ:
{{
  "saison_confirmee": "Automne|Printemps|Été|Hiver",
  "sous_ton_detecte": "chaud|froid|neutre",
  
  "justification_saison": "40-50 mots spécifiques analysant:
    - Tonalité exacte carnation (dorée/olive/pale/rose?)
    - Comment yeux {eye_color} confirment/contredisent la saison
    - Comment cheveux {hair_color} renforcent l'harmonie
    - Contraste naturel observé
    Exemple: 'Carnation dorée-olive riche + yeux marron foncé + cheveux brun chaud créent harmonie Automne. Contraste ~70% typique saison riche. Profil très net, sans ambiguïté.'",
    
  "eye_color": "{eye_color}",
  "hair_color": "{hair_color}",
  
  "analyse_colorimetrique_detaillee": {{
    "temperature": "chaud|froid|neutre",
    "valeur": "clair|moyen|fonce",
    "intensite": "douce|medium|intense",
    "contraste_naturel": "faible|moyen|fort",
    
    "description_teint": "40-50 mots SPÉCIFIQUES sur carnation:
      - Tonalité exacte (dorée? olive? rose?)
      - Saturation (riche? pâle?)
      - Uniformité (homogène? taches?)
      Exemple: 'Carnation olive-dorée saturée, uniforme. Reflets chauds dominent clairement. Sous-ton chaud sans ambiguïté. Teint riche qui réagit positivement aux couleurs chaudes.'",
    
    "description_yeux": "40-50 mots SPÉCIFIQUES sur {eye_color}:
      - Nuance/profondeur
      - Clarté/intensité
      - Impact direct sur saison
      Exemple: 'Yeux marron-foncé intensément saturés, avec concentration pigment élevée. Aucune teinte claire frappante. Ancrage automne certain. Intensité moyenne-forte qui renforce harmonie chaud.'",
    
    "description_cheveux": "40-50 mots SPÉCIFIQUES sur {hair_color}:
      - Tonalité/reflets exacts
      - Éclat/saturation
      - Alignement saison
      Exemple: 'Cheveux brun-foncé chauds, sans teinte froide. Reflets dorés/rouille visibles. Luminosité modérée. Renforce clairement profil automne chaud. Cohérence totale avec carnation.'",
    
    "harmonie_globale": "50 mots: Comment teint+yeux+cheveux créent TRINITÉ COHÉRENTE:
      Exemple: 'Trois éléments (carnation olive-dorée + yeux marron + cheveux brun chaud) s\\'alignent parfaitement. Aucune contradiction ou élément discordant. Contraste naturel ~70% confirme saison. Profil très net, harmonieux, non ambigu. Synergie totale.'",
    
    "bloc_emotionnel": "50 mots: Impact ÉMOTIONNEL et PRATIQUE de cette saison pour ce client:
      Exemple: 'Votre Automne apporte luminosité douce (jamais harshness), sophistication naturelle sans effort. Vous avez l\\'avantage d\\'une harmonie innée qui permet des looks élégants instantanément. Confiance subtle, pas de drama. Votre palette crée cohésion qui flatte sans surcharge.'",
    
    "impact_visuel": {{
      "effet_couleurs_chaudes": "40-50 mots SPÉCIFIQUE à THIS client:
        Exemple: 'Réchauffent votre carnation olive (la rendent dorée-lumineuse). Amplifient intensité yeux marron. Créent cohésion globale instantanée. Harmonisent avec reflets cheveux. Effet: teint vivant, regard renforcé, allure sophistiquée.'",
      
      "effet_couleurs_froides": "40-50 mots sur dégâts spécifiques à THIS client:
        Exemple: 'Ternissent carnation dorée (la rendent grisâtre-morne). Isolent yeux marron (contraste désharmonisé). Contredisent reflets cheveux (effet décousu). Créent apparence désunitée. Effet: teint éteint, regard perdu, allure confuse.'",
      
      "pourquoi": "25 mots: SCIENCE du phénomène:
        Exemple: 'Sous-ton naturel chaud = nécessité harmonie pigmentaire chaleureuse. Froid = opposition crée dissonance optique.'"
    }}
  }}
}}

RÈGLES QUALITÉ STRICTE:
✅ Chaque description = 40-50 mots SPÉCIFIQUES (pas une de moins!)
✅ bloc_emotionnel = 50 mots minimum (impact émotionnel + pratique)
✅ Référencer CLIENT par yeux/cheveux/carnation
✅ Vocabulaire PRÉCIS (doré, olivâtre, saturé, chaud, intense, etc.)
✅ JAMAIS: "harmonieuses", "typiques", "complètent" - phrases creuses
✅ INCLURE: observations RÉELLES basées photo
✅ JSON valide complet
✅ ZÉRO texte avant/après
"""