COLORIMETRY_PART2_SYSTEM_PROMPT = """
Vous êtes expert colorimétre. Vous renvoyez UNIQUEMENT un JSON STRICT et valide.
Commencez par { et finissez par }. Zéro texte avant/après.
Règle JSON: guillemets doubles uniquement, aucune virgule finale, pas de retours à la ligne dans les strings.
""".strip()

COLORIMETRY_PART2_USER_PROMPT_TEMPLATE = """
Générez palette + couleurs génériques + associations pour cette cliente (selon SA SAISON réelle).

DONNÉES CLIENT:
- Saison: {SAISON}
- Sous-ton: {SOUS_TON}
- Yeux: {EYE_COLOR}
- Cheveux: {HAIR_COLOR}

OBJECTIF:
Retourner un JSON STRICT avec 4 clés:
1) palette_personnalisee (10 couleurs, note 8-10)
2) couleurs_generiques (8 à 12 couleurs "globales" notées 0-10)
3) associations_gagnantes (5 occasions, 3 couleurs chacune)
4) allColorsWithNotes (au moins 20 couleurs notées 0-10, incluant toute la palette + couleurs génériques + autres alternatives)

STRUCTURE JSON REQUISE:
{{
  "palette_personnalisee": [
    {{"name":"nom_lower","hex":"#RRGGBB","note":9,"displayName":"Nom Affiche","commentaire":"Raison spécifique <15 mots"}}
  ],
  "couleurs_generiques": [
    {{"name":"bleu","hex":"#0000FF","note":8,"displayName":"Bleu","commentaire":"Pourquoi ce bleu marche pour vous <15 mots"}}
  ],
  "associations_gagnantes": [
    {{"occasion":"professionnel","colors":["Nom Affiche 1","Nom Affiche 2","Nom Affiche 3"],"color_hex":["#RRGGBB","#RRGGBB","#RRGGBB"],"effet":"Effet court","description":"Description personnalisée courte"}}
  ],
  "allColorsWithNotes": [
    {{"name":"nom_lower","hex":"#RRGGBB","note":7,"displayName":"Nom Affiche","commentaire":"Commentaire court"}}
  ]
}}

RÈGLES STRICTES:
- palette_personnalisee: EXACTEMENT 10 items, notes 8 à 10 uniquement.
- associations_gagnantes: EXACTEMENT 5 items, occasions EXACTES:
  "professionnel", "casual", "soiree", "weekend", "famille"
- Pour associations_gagnantes:
  - colors DOIT reprendre les displayName de la palette_personnalisee ou de couleurs_generiques (pas de nouveaux noms).
  - color_hex DOIT correspondre exactement aux hex des colors dans palette_personnalisee/couleurs_generiques.
- couleurs_generiques: 8 à 12 items, notes 0 à 10.
- allColorsWithNotes: au moins 20 items, notes 0 à 10, inclure:
  - les 10 couleurs de la palette
  - toutes les couleurs_generiques
  - + des alternatives pertinentes à la saison

CONTRAINTES TEXTE:
- Pas d'apostrophe: écrire "s harmonise" pas "s'harmonise"
- Pas de guillemets typographiques
- Pas d’emojis
- Pas de retours à la ligne dans les strings

Répondez UNIQUEMENT avec le JSON.
""".strip()
FALLBACK_PART2_DATA_BY_SEASON = {
  "Printemps": {
    "palette_personnalisee": [
      {"name":"peche","hex":"#F4A460","note":10,"displayName":"Pêche","commentaire":"Réchauffe le teint et garde de la fraîcheur"},
      {"name":"corail","hex":"#FF7F50","note":10,"displayName":"Corail","commentaire":"Dynamise le visage sans durcir"},
      {"name":"saumon","hex":"#FA8072","note":9,"displayName":"Saumon","commentaire":"Lumineux et flatteur près du visage"},
      {"name":"camel_clair","hex":"#D2B48C","note":9,"displayName":"Camel clair","commentaire":"Neutre chaud facile à porter"},
      {"name":"ivoire","hex":"#FFFFF0","note":9,"displayName":"Ivoire","commentaire":"Adoucit et illumine sans contraste dur"},
      {"name":"menthe","hex":"#98FF98","note":8,"displayName":"Vert menthe","commentaire":"Apporte une fraîcheur chic et tendre"},
      {"name":"turquoise_clair","hex":"#40E0D0","note":8,"displayName":"Turquoise clair","commentaire":"Réveille le regard en douceur"},
      {"name":"jaune_dore","hex":"#E1AD01","note":8,"displayName":"Jaune doré","commentaire":"Illumine avec chaleur maîtrisée"},
      {"name":"rose_chaud","hex":"#FFB6C1","note":8,"displayName":"Rose chaud","commentaire":"Féminin et lumineux sans froideur"},
      {"name":"vert_olive_clair","hex":"#C3B091","note":8,"displayName":"Kaki clair","commentaire":"Naturel chic et très combinable"}
    ],
    "couleurs_generiques": [
      {"name":"bleu","hex":"#0000FF","note":7,"displayName":"Bleu","commentaire":"Préférer des bleus clairs et lumineux"},
      {"name":"rouge","hex":"#FF0000","note":7,"displayName":"Rouge","commentaire":"Mieux en rouge chaud type corail"},
      {"name":"jaune","hex":"#FFFF00","note":8,"displayName":"Jaune","commentaire":"Très flatteur en jaune doré"},
      {"name":"vert","hex":"#008000","note":7,"displayName":"Vert","commentaire":"Choisir des verts frais et tendres"},
      {"name":"orange","hex":"#FFA500","note":8,"displayName":"Orange","commentaire":"Super en pêche et corail"},
      {"name":"violet","hex":"#800080","note":5,"displayName":"Violet","commentaire":"À garder léger, éviter trop sombre"},
      {"name":"gris","hex":"#808080","note":5,"displayName":"Gris","commentaire":"Préférer gris clair et doux"},
      {"name":"noir","hex":"#000000","note":3,"displayName":"Noir","commentaire":"Souvent trop dur, préférer chocolat"},
      {"name":"blanc","hex":"#FFFFFF","note":7,"displayName":"Blanc","commentaire":"Ivoire souvent plus flatteur que blanc pur"}
    ],
    "associations_gagnantes": [
      {"occasion":"professionnel","colors":["Ivoire","Camel clair","Turquoise clair"],"color_hex":["#FFFFF0","#D2B48C","#40E0D0"],"effet":"Crédible lumineux","description":"Tenue nette, douce et moderne"},
      {"occasion":"casual","colors":["Pêche","Kaki clair","Ivoire"],"color_hex":["#F4A460","#C3B091","#FFFFF0"],"effet":"Naturel frais","description":"Facile, flatteur, sans effort"},
      {"occasion":"soiree","colors":["Corail","Ivoire","Jaune doré"],"color_hex":["#FF7F50","#FFFFF0","#E1AD01"],"effet":"Chaleur élégante","description":"Féminin lumineux, sans trop briller"},
      {"occasion":"weekend","colors":["Vert menthe","Camel clair","Rose chaud"],"color_hex":["#98FF98","#D2B48C","#FFB6C1"],"effet":"Détente chic","description":"Décontracté mais harmonieux"},
      {"occasion":"famille","colors":["Saumon","Ivoire","Turquoise clair"],"color_hex":["#FA8072","#FFFFF0","#40E0D0"],"effet":"Accueillant","description":"Doux et solaire, photogénique"}
    ],
    "allColorsWithNotes": []  # rempli plus bas
  },

  "Ete": {
    "palette_personnalisee": [
      {"name":"bleu_poudre","hex":"#B0C4DE","note":10,"displayName":"Bleu poudré","commentaire":"Adoucit le contraste et flatte le teint"},
      {"name":"rose_poudre","hex":"#E6A8D7","note":10,"displayName":"Rose poudré","commentaire":"Féminin doux sans durcir"},
      {"name":"lavande","hex":"#B57EDC","note":9,"displayName":"Lavande","commentaire":"Éclaire le visage avec douceur"},
      {"name":"gris_perle","hex":"#D9D9D9","note":9,"displayName":"Gris perle","commentaire":"Neutre élégant et léger"},
      {"name":"bleu_gris","hex":"#708090","note":9,"displayName":"Bleu ardoise doux","commentaire":"Structurant mais jamais agressif"},
      {"name":"taupe","hex":"#8B8589","note":8,"displayName":"Taupe","commentaire":"Chic discret, parfait en base"},
      {"name":"vert_sauge","hex":"#9DC183","note":8,"displayName":"Vert sauge","commentaire":"Naturel raffiné, très flatteur"},
      {"name":"framboise_douce","hex":"#C04A7A","note":8,"displayName":"Framboise douce","commentaire":"Apporte une touche chic au teint"},
      {"name":"bleu_ciel","hex":"#87CEEB","note":8,"displayName":"Bleu ciel","commentaire":"Illumine et rafraîchit"},
      {"name":"blanc_casse","hex":"#F5F5DC","note":8,"displayName":"Beige clair","commentaire":"Plus doux que blanc pur"}
    ],
    "couleurs_generiques": [
      {"name":"bleu","hex":"#0000FF","note":8,"displayName":"Bleu","commentaire":"Préférer bleus doux et grisés"},
      {"name":"rouge","hex":"#FF0000","note":6,"displayName":"Rouge","commentaire":"Mieux en framboise douce que rouge vif"},
      {"name":"jaune","hex":"#FFFF00","note":4,"displayName":"Jaune","commentaire":"Souvent trop chaud, limiter"},
      {"name":"vert","hex":"#008000","note":7,"displayName":"Vert","commentaire":"Sauge et verts grisés recommandés"},
      {"name":"violet","hex":"#800080","note":7,"displayName":"Violet","commentaire":"Lavande et mauve très flatteurs"},
      {"name":"gris","hex":"#808080","note":8,"displayName":"Gris","commentaire":"Excellent en gris perle"},
      {"name":"noir","hex":"#000000","note":4,"displayName":"Noir","commentaire":"Peut durcir, préférer bleu ardoise"},
      {"name":"blanc","hex":"#FFFFFF","note":6,"displayName":"Blanc","commentaire":"Blanc cassé plus harmonieux"}
    ],
    "associations_gagnantes": [
      {"occasion":"professionnel","colors":["Gris perle","Bleu poudré","Taupe"],"color_hex":["#D9D9D9","#B0C4DE","#8B8589"],"effet":"Crédible doux","description":"Propre, chic, sans rigidité"},
      {"occasion":"casual","colors":["Bleu ciel","Beige clair","Vert sauge"],"color_hex":["#87CEEB","#F5F5DC","#9DC183"],"effet":"Frais naturel","description":"Simple, lumineux et reposant"},
      {"occasion":"soiree","colors":["Framboise douce","Gris perle","Lavande"],"color_hex":["#C04A7A","#D9D9D9","#B57EDC"],"effet":"Féminin raffiné","description":"Élégant, subtil, photogénique"},
      {"occasion":"weekend","colors":["Vert sauge","Taupe","Bleu ciel"],"color_hex":["#9DC183","#8B8589","#87CEEB"],"effet":"Détente chic","description":"Harmonieux et confortable"},
      {"occasion":"famille","colors":["Rose poudré","Beige clair","Bleu poudré"],"color_hex":["#E6A8D7","#F5F5DC","#B0C4DE"],"effet":"Doux accueillant","description":"Tendre et lumineux, sans effort"}
    ],
    "allColorsWithNotes": []
  },

  "Automne": {
    "palette_personnalisee": [
      {"name":"camel","hex":"#C19A6B","note":10,"displayName":"Camel","commentaire":"Base chaude, naturelle, très flatteuse"},
      {"name":"moutarde","hex":"#E1AD01","note":10,"displayName":"Moutarde","commentaire":"Jaune doré qui illumine le teint"},
      {"name":"bordeaux","hex":"#800020","note":9,"displayName":"Bordeaux","commentaire":"Chaleur élégante, idéale en soirée"},
      {"name":"rose_corail","hex":"#FF7F50","note":9,"displayName":"Rose corail","commentaire":"Apporte de la vie sans froideur"},
      {"name":"olive","hex":"#808000","note":9,"displayName":"Olive","commentaire":"Vert chaud naturel, très chic"},
      {"name":"cuivre","hex":"#B87333","note":9,"displayName":"Cuivre","commentaire":"Métal chaud qui réchauffe l harmonie"},
      {"name":"brique","hex":"#CB4154","note":8,"displayName":"Brique","commentaire":"Rouge brun sophistiqué et portable"},
      {"name":"kaki","hex":"#C3B091","note":8,"displayName":"Kaki","commentaire":"Neutre chaud facile à assortir"},
      {"name":"chocolat","hex":"#7B3F00","note":8,"displayName":"Chocolat","commentaire":"Foncé chaud plus doux que noir"},
      {"name":"terracotta","hex":"#E2725B","note":8,"displayName":"Terracotta","commentaire":"Chaleur solaire, flatte le teint"}
    ],
    "couleurs_generiques": [
      {"name":"bleu","hex":"#0000FF","note":5,"displayName":"Bleu","commentaire":"Préférer bleu pétrole plutôt que bleu froid"},
      {"name":"rouge","hex":"#FF0000","note":7,"displayName":"Rouge","commentaire":"Meilleur en brique et bordeaux"},
      {"name":"jaune","hex":"#FFFF00","note":8,"displayName":"Jaune","commentaire":"Excellent en moutarde"},
      {"name":"vert","hex":"#008000","note":8,"displayName":"Vert","commentaire":"Olive et kaki très flatteurs"},
      {"name":"orange","hex":"#FFA500","note":8,"displayName":"Orange","commentaire":"Terracotta et rouille recommandés"},
      {"name":"violet","hex":"#800080","note":4,"displayName":"Violet","commentaire":"Souvent trop froid, limiter"},
      {"name":"gris","hex":"#808080","note":5,"displayName":"Gris","commentaire":"Préférer gris taupe"},
      {"name":"noir","hex":"#000000","note":2,"displayName":"Noir","commentaire":"Durcit, préférer chocolat"},
      {"name":"blanc","hex":"#FFFFFF","note":6,"displayName":"Blanc","commentaire":"Ivoire mieux que blanc pur"}
    ],
    "associations_gagnantes": [
      {"occasion":"professionnel","colors":["Camel","Chocolat","Ivoire"],"color_hex":["#C19A6B","#7B3F00","#FFFFF0"],"effet":"Crédible chaleureux","description":"Autorité douce, rendu premium"},
      {"occasion":"casual","colors":["Kaki","Camel","Terracotta"],"color_hex":["#C3B091","#C19A6B","#E2725B"],"effet":"Naturel sans effort","description":"Décontracté harmonieux et flatteur"},
      {"occasion":"soiree","colors":["Bordeaux","Chocolat","Cuivre"],"color_hex":["#800020","#7B3F00","#B87333"],"effet":"Sophistication chaude","description":"Chic profond, sans agressivité"},
      {"occasion":"weekend","colors":["Olive","Camel","Terracotta"],"color_hex":["#808000","#C19A6B","#E2725B"],"effet":"Authentique chic","description":"Parfait en extérieur et photos"},
      {"occasion":"famille","colors":["Rose corail","Moutarde","Kaki"],"color_hex":["#FF7F50","#E1AD01","#C3B091"],"effet":"Accueillant lumineux","description":"Chaleur douce, très flatteur"}
    ],
    "allColorsWithNotes": []
  },

  "Hiver": {
    "palette_personnalisee": [
      {"name":"noir","hex":"#000000","note":10,"displayName":"Noir","commentaire":"Contraste net, très structurant"},
      {"name":"blanc_optique","hex":"#FFFFFF","note":10,"displayName":"Blanc","commentaire":"Illumine fortement, effet très clean"},
      {"name":"bleu_marine","hex":"#000080","note":9,"displayName":"Bleu marine","commentaire":"Chic profond, excellent au quotidien"},
      {"name":"rouge_froid","hex":"#B00020","note":9,"displayName":"Rouge cerise","commentaire":"Frappe juste, très élégant"},
      {"name":"fuchsia","hex":"#FF1493","note":9,"displayName":"Fuchsia","commentaire":"Éclat froid, boost immédiat du teint"},
      {"name":"vert_emeraude","hex":"#008B8B","note":8,"displayName":"Émeraude","commentaire":"Intense et premium, très flatteur"},
      {"name":"violet_prune","hex":"#4B0082","note":8,"displayName":"Prune","commentaire":"Profond et sophistiqué"},
      {"name":"gris_anthracite","hex":"#2F4F4F","note":8,"displayName":"Anthracite","commentaire":"Neutre puissant, moins dur que noir"},
      {"name":"bleu_roi","hex":"#0000CD","note":8,"displayName":"Bleu roi","commentaire":"Éclat froid, très visuel"},
      {"name":"rose_froid","hex":"#E75480","note":8,"displayName":"Rose froid","commentaire":"Féminin net, sans jaunir"}
    ],
    "couleurs_generiques": [
      {"name":"bleu","hex":"#0000FF","note":9,"displayName":"Bleu","commentaire":"Excellent en bleu roi et marine"},
      {"name":"rouge","hex":"#FF0000","note":8,"displayName":"Rouge","commentaire":"Mieux en rouge cerise froid"},
      {"name":"jaune","hex":"#FFFF00","note":2,"displayName":"Jaune","commentaire":"Souvent trop chaud, éviter"},
      {"name":"vert","hex":"#008000","note":7,"displayName":"Vert","commentaire":"Émeraude froid recommandé"},
      {"name":"violet","hex":"#800080","note":7,"displayName":"Violet","commentaire":"Prune et indigo très flatteurs"},
      {"name":"gris","hex":"#808080","note":7,"displayName":"Gris","commentaire":"Anthracite et gris froids parfaits"},
      {"name":"noir","hex":"#000000","note":10,"displayName":"Noir","commentaire":"Base idéale si contraste élevé"},
      {"name":"blanc","hex":"#FFFFFF","note":10,"displayName":"Blanc","commentaire":"Optique très flatteur en hiver"}
    ],
    "associations_gagnantes": [
      {"occasion":"professionnel","colors":["Noir","Blanc","Bleu marine"],"color_hex":["#000000","#FFFFFF","#000080"],"effet":"Autorité nette","description":"Image crédible, très structurée"},
      {"occasion":"casual","colors":["Anthracite","Bleu marine","Rose froid"],"color_hex":["#2F4F4F","#000080","#E75480"],"effet":"Chic simple","description":"Décontracté mais maîtrisé"},
      {"occasion":"soiree","colors":["Rouge cerise","Noir","Fuchsia"],"color_hex":["#B00020","#000000","#FF1493"],"effet":"Impact glamour","description":"Fort et élégant, sans surcharge"},
      {"occasion":"weekend","colors":["Bleu roi","Blanc","Anthracite"],"color_hex":["#0000CD","#FFFFFF","#2F4F4F"],"effet":"Frais dynamique","description":"Très flatteur en photo"},
      {"occasion":"famille","colors":["Rose froid","Blanc","Bleu marine"],"color_hex":["#E75480","#FFFFFF","#000080"],"effet":"Doux net","description":"Féminin, lumineux, rassurant"}
    ],
    "allColorsWithNotes": []
  }
}

def _build_all_colors_with_notes_from_fallback(block: dict) -> dict:
    # garantit allColorsWithNotes >= 20 : palette + generiques + compléments saison
    palette = block.get("palette_personnalisee", [])
    generiques = block.get("couleurs_generiques", [])
    extras = []

    # petits compléments neutres utiles
    extras_pool = [
      {"name":"ivoire","hex":"#FFFFF0","note":7,"displayName":"Ivoire","commentaire":"Alternative plus douce que blanc pur"},
      {"name":"beige","hex":"#F5F5DC","note":6,"displayName":"Beige","commentaire":"Base neutre facile à combiner"},
      {"name":"marron","hex":"#8B4513","note":6,"displayName":"Marron","commentaire":"Alternative chaude au noir"},
      {"name":"marine","hex":"#000080","note":7,"displayName":"Marine","commentaire":"Neutre chic pour structurer"},
      {"name":"gris_taupe","hex":"#8B8589","note":6,"displayName":"Gris taupe","commentaire":"Neutre doux et élégant"}
    ]

    used = set((c.get("displayName") or "") for c in (palette + generiques))
    for x in extras_pool:
        if x["displayName"] not in used:
            extras.append(x)
            used.add(x["displayName"])

    all_colors = palette + generiques + extras
    # si < 20, duplique pas : ajoute variations génériques simples
    while len(all_colors) < 20:
        all_colors.append({"name":"neutre","hex":"#999999","note":5,"displayName":f"Neutre {len(all_colors)+1}","commentaire":"Alternative de secours"})

    block["allColorsWithNotes"] = all_colors[:30]  # 20 à 30 c est bien
    return block

def get_fallback_part2(season: str) -> dict:
    s = (season or "").strip().lower()
    if "print" in s:
        base = FALLBACK_PART2_DATA_BY_SEASON["Printemps"].copy()
    elif "ete" in s or "été" in s:
        base = FALLBACK_PART2_DATA_BY_SEASON["Ete"].copy()
    elif "hiv" in s:
        base = FALLBACK_PART2_DATA_BY_SEASON["Hiver"].copy()
    else:
        base = FALLBACK_PART2_DATA_BY_SEASON["Automne"].copy()

    return _build_all_colors_with_notes_from_fallback(base)

FALLBACK_PART2_DATA = get_fallback_part2("Automne")
