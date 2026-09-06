"""
COLORIMETRY DECLARATIVE v1.0
Calcul deterministe de la saison colorimetrique a partir du questionnaire
declaratif, sans photo et sans appel GPT.

Entrees (onboarding_data.colorimetry_declarative) :
    skin_depth   : very_light | light | light_medium | medium | medium_tan
                   | tan | tan_deep | deep | deep_rich | very_deep | unknown
    sun_reaction : always_burns | burns_easily | burns_then_tans | tans_easily
                   | rarely_burns | never_burns | unknown
    metal        : gold | silver | both | unknown
    veins        : blue | green | mixed | unknown

Entrees existantes (etape 1) :
    hair_color   : slug de EyeHairColorStep (noir, brun, blond, roux...)
    eye_color    : slug de EyeHairColorStep

Sortie : dict compatible avec le format attendu par ColorimetryService.
"""

from typing import Optional


# ---------------------------------------------------------------------------
# ECHELLES DE PROFONDEUR (1 = le plus clair, 10 = le plus fonce)
# ---------------------------------------------------------------------------

SKIN_DEPTH_SCALE = {
    "very_light": 1,
    "light": 2,
    "light_medium": 3,
    "medium": 4,
    "medium_tan": 5,
    "tan": 6,
    "tan_deep": 7,
    "deep": 8,
    "deep_rich": 9,
    "very_deep": 10,
}

# Profondeur des cheveux ramenee sur la meme echelle 1-10
HAIR_DEPTH_SCALE = {
    "blond-platine": 1,
    "blond-clair": 2,
    "blond": 3,
    "blanc": 1,
    "gris": 4,
    "blond-fonce": 4,
    "roux-clair": 4,
    "chatain-clair": 5,
    "roux": 5,
    "chatain": 6,
    "roux-fonce": 6,
    "brun-clair": 6,
    "chatain-fonce": 8,
    "brun": 7,
    "brun-fonce": 9,
    "noir": 10,
}

# Cheveux porteurs d'un signal de temperature
HAIR_WARM = {"roux", "roux-clair", "roux-fonce", "blond", "blond-clair"}
HAIR_COOL = {"blond-platine", "gris", "blanc"}

# Yeux porteurs d'un signal de temperature
EYE_WARM = {"noisette", "ambre", "marron-clair"}
EYE_COOL = {"bleu", "bleu-gris", "gris"}


# ---------------------------------------------------------------------------
# SCORES DE TEMPERATURE
# Positif = chaud, negatif = froid. Le poids porte l'importance du signal.
# ---------------------------------------------------------------------------

SUN_TEMP_SCORE = {
    "always_burns": -1,
    "burns_easily": -1,
    "burns_then_tans": 0,
    "tans_easily": 1,
    "rarely_burns": 1,
    "never_burns": 0,
}

METAL_TEMP_SCORE = {
    "gold": 2,
    "silver": -2,
    "both": 0,
}

VEINS_TEMP_SCORE = {
    "green": 1,
    "blue": -1,
    "mixed": 0,
}


def _depth_from_sun(sun_reaction: str) -> Optional[int]:
    """Profondeur estimee depuis le phototype, si skin_depth est unknown."""
    return {
        "always_burns": 1,
        "burns_easily": 2,
        "burns_then_tans": 4,
        "tans_easily": 6,
        "rarely_burns": 8,
        "never_burns": 10,
    }.get(sun_reaction)


def compute_skin_depth(skin_depth: str, sun_reaction: str, hair_color: str) -> int:
    """Profondeur de peau sur 1-10, avec replis successifs."""
    if skin_depth in SKIN_DEPTH_SCALE:
        return SKIN_DEPTH_SCALE[skin_depth]
    from_sun = _depth_from_sun(sun_reaction)
    if from_sun is not None:
        return from_sun
    # dernier repli : correlation faible avec la profondeur des cheveux
    hair = HAIR_DEPTH_SCALE.get(hair_color, 6)
    return max(1, min(10, round(hair * 0.6) + 1))


def compute_undertone(
    sun_reaction: str,
    metal: str,
    veins: str,
    hair_color: str,
    eye_color: str,
    skin_depth_value: int,
) -> tuple:
    """
    Retourne (undertone, score, confiance).
    undertone : "chaud" | "froid" | "neutre"

    Ponderation conditionnelle : sur les carnations profondes (>= 7), le metal
    est peu discriminant (l'or ressort bien sur presque toutes les peaux
    foncees). On reduit son poids et on renforce le soleil et les veines.
    """
    deep_skin = skin_depth_value >= 7
    light_skin = skin_depth_value <= 3

    # Le soleil renseigne surtout la profondeur. Sur peau claire il ne dit
    # rien du sous-ton (une rousse chaude brule autant qu'une brune froide).
    w_sun = 1 if light_skin else (2 if not deep_skin else 2)
    w_metal = 2 if not deep_skin else 1
    w_veins = 1 if not deep_skin else 2
    w_hair = 1
    w_eye = 1

    score = 0.0
    weight_used = 0.0

    if sun_reaction in SUN_TEMP_SCORE:
        score += SUN_TEMP_SCORE[sun_reaction] * w_sun
        weight_used += w_sun * 1  # amplitude max du signal

    if metal in METAL_TEMP_SCORE:
        score += METAL_TEMP_SCORE[metal] * w_metal
        weight_used += w_metal * 2

    if veins in VEINS_TEMP_SCORE:
        score += VEINS_TEMP_SCORE[veins] * w_veins
        weight_used += w_veins * 1

    if hair_color in HAIR_WARM:
        score += 2 * w_hair
        weight_used += w_hair * 2
    elif hair_color in HAIR_COOL:
        score -= 2 * w_hair
        weight_used += w_hair * 2

    if eye_color in EYE_WARM:
        score += 1 * w_eye
        weight_used += w_eye * 1
    elif eye_color in EYE_COOL:
        score -= 1 * w_eye
        weight_used += w_eye * 1

    # normalisation sur -1..+1
    normalized = score / weight_used if weight_used else 0.0
    confidence = min(1.0, weight_used / 10.0)

    if normalized > 0.15:
        undertone = "chaud"
    elif normalized < -0.15:
        undertone = "froid"
    else:
        undertone = "neutre"

    return undertone, round(normalized, 3), round(confidence, 2)


def compute_contrast(skin_depth_value: int, hair_color: str, eye_color: str) -> tuple:
    """
    Contraste = ECART entre profondeur de peau et profondeur de cheveux.
    C'est le point critique pour ne pas biaiser les carnations profondes :
    peau foncee + cheveux noirs = ecart faible = contraste FAIBLE.
    """
    hair_depth = HAIR_DEPTH_SCALE.get(hair_color, 6)
    gap = abs(skin_depth_value - hair_depth)

    # les yeux tres clairs sur peau foncee augmentent le contraste percu
    if eye_color in {"bleu", "bleu-gris", "gris", "vert"} and skin_depth_value >= 6:
        gap += 2

    if gap <= 2:
        label = "faible"
    elif gap <= 5:
        label = "moyen"
    else:
        label = "fort"

    return label, gap


def compute_intensity(contrast_label: str, skin_depth_value: int, hair_color: str) -> str:
    """
    Intensite deduite du contraste et de la saturation naturelle.
    douce | medium | intense
    """
    if contrast_label == "fort":
        return "intense"
    if contrast_label == "faible":
        # une peau profonde avec faible contraste garde une richesse naturelle
        return "medium" if skin_depth_value >= 7 else "douce"
    return "medium"


def compute_season(undertone: str, skin_depth_value: int, hair_depth_value: int,
                   contrast_label: str, intensity: str) -> str:
    """
    Mapping vers les 4 saisons du backend existant.
    Printemps | Ete | Automne | Hiver
    """
    lightness = (skin_depth_value + hair_depth_value) / 2

    if undertone == "chaud":
        return "Printemps" if lightness <= 4 else "Automne"

    if undertone == "froid":
        if contrast_label == "fort" or intensity == "intense":
            return "Hiver"
        # Froid + profond => Hiver, jamais Ete. La palette Ete (pastels
        # poudres, gris perle) delave les carnations profondes, alors que
        # la palette Hiver (noir, blanc, emeraude, fuchsia) les valorise.
        if lightness >= 7:
            return "Hiver"
        return "Ete"

    # neutre : arbitrage par clarte globale et contraste
    if contrast_label == "fort":
        return "Hiver" if lightness >= 5 else "Printemps"
    if lightness <= 4:
        return "Printemps"
    return "Ete" if contrast_label == "faible" and lightness <= 6 else "Automne"


def compute_subtype(season: str, lightness: float, contrast_label: str,
                    intensity: str, temp_score: float,
                    contrast_gap: int = 0, skin_depth_value: int = 5) -> str:
    """
    Sous-type au sein de la saison, selon la taxonomie reconnue des
    12 saisons colorimetriques. Trois sous-types par saison, determines
    par la caracteristique SECONDAIRE dominante.

    saison_confirmee reste a 4 valeurs : ce sous-type est un LIBELLE
    d'affichage, il n'entre pas dans le matching produit.
    """
    strong_temp = abs(temp_score) >= 0.35

    if season == "Printemps":
        if lightness <= 2.5:
            return "clair"          # Light Spring
        if contrast_label == "fort" or intensity == "intense":
            return "vif"            # Bright Spring
        return "chaud"              # True Spring

    if season == "Ete":
        if lightness <= 3:
            return "clair"          # Light Summer
        if contrast_label == "faible" and not strong_temp:
            return "doux"           # Soft Summer
        return "froid"              # True Summer

    if season == "Automne":
        if lightness >= 7.5:
            return "profond"        # Deep Autumn
        if contrast_label == "faible" and not strong_temp:
            return "doux"           # Soft Autumn
        return "chaud"              # True Autumn

    if season == "Hiver":
        if lightness >= 7:
            return "profond"        # Deep Winter
        if contrast_gap >= 7 and skin_depth_value <= 3:
            return "vif"            # Bright Winter : peau claire, cheveux tres fonces
        return "froid"              # True Winter

    return ""


def _skin_value_label(depth: int) -> str:
    """Ramene la profondeur 1-10 sur le vocabulaire backend clair|moyen|fonce."""
    if depth <= 3:
        return "clair"
    if depth <= 6:
        return "moyen"
    return "fonce"


def analyze_declarative(
    skin_depth: str,
    sun_reaction: str,
    metal: str,
    veins: str,
    hair_color: str,
    eye_color: str,
) -> dict:
    """
    Point d'entree principal.
    Retourne un dict avec exactement le vocabulaire attendu par
    ColorimetryService._call_part2 et par le stockage en base.
    """
    skin_depth_value = compute_skin_depth(skin_depth, sun_reaction, hair_color)
    undertone, temp_score, confidence = compute_undertone(
        sun_reaction, metal, veins, hair_color, eye_color, skin_depth_value
    )
    contrast_label, contrast_gap = compute_contrast(skin_depth_value, hair_color, eye_color)
    intensity = compute_intensity(contrast_label, skin_depth_value, hair_color)
    hair_depth_value = HAIR_DEPTH_SCALE.get(hair_color, 6)
    season = compute_season(undertone, skin_depth_value, hair_depth_value,
                            contrast_label, intensity)
    lightness = (skin_depth_value + hair_depth_value) / 2
    subtype = compute_subtype(season, lightness, contrast_label, intensity,
                              temp_score, contrast_gap, skin_depth_value)

    return {
        "saison_confirmee": season,
        "sous_ton_detecte": undertone,
        "valeur_peau": _skin_value_label(skin_depth_value),
        "intensite": intensity,
        "contraste_naturel": contrast_label,
        "sous_type": subtype,
        "libelle_complet": f"{season} {subtype}".strip(),
        "eye_color": eye_color,
        "hair_color": hair_color,
        # metadonnees de tracabilite (non affichees)
        "_skin_depth_value": skin_depth_value,
        "_contrast_gap": contrast_gap,
        "_hair_depth_value": hair_depth_value,
        "_lightness": lightness,
        "_temperature_score": temp_score,
        "_confidence": confidence,
        "_source": "declarative",
    }


# ---------------------------------------------------------------------------
# AUTOTEST
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    cases = [
        ("Rousse peau tres claire",
         dict(skin_depth="very_light", sun_reaction="always_burns", metal="gold",
              veins="green", hair_color="roux", eye_color="vert")),
        ("Brune peau claire yeux bleus",
         dict(skin_depth="light", sun_reaction="burns_easily", metal="silver",
              veins="blue", hair_color="brun-fonce", eye_color="bleu")),
        ("Peau foncee cheveux noirs",
         dict(skin_depth="deep_rich", sun_reaction="never_burns", metal="gold",
              veins="green", hair_color="noir", eye_color="marron-fonce")),
        ("Peau mate cheveux noirs (Inde/Maghreb)",
         dict(skin_depth="tan", sun_reaction="rarely_burns", metal="gold",
              veins="green", hair_color="noir", eye_color="marron-fonce")),
        ("Peau claire-mate cheveux noirs (Asie)",
         dict(skin_depth="light_medium", sun_reaction="burns_then_tans", metal="gold",
              veins="mixed", hair_color="noir", eye_color="marron-fonce")),
        ("Blonde peau claire",
         dict(skin_depth="light", sun_reaction="burns_then_tans", metal="gold",
              veins="green", hair_color="blond", eye_color="bleu")),
        ("Chatain peau moyenne tout unknown",
         dict(skin_depth="unknown", sun_reaction="unknown", metal="unknown",
              veins="unknown", hair_color="chatain", eye_color="marron")),
        ("Peau tres foncee sous-ton froid",
         dict(skin_depth="very_deep", sun_reaction="never_burns", metal="silver",
              veins="blue", hair_color="noir", eye_color="marron-fonce")),
        ("Peau claire cheveux noirs yeux bleus (Asie froide)",
         dict(skin_depth="light", sun_reaction="burns_easily", metal="silver",
              veins="blue", hair_color="noir", eye_color="marron-fonce")),
        ("Blonde cendree peau claire",
         dict(skin_depth="light", sun_reaction="burns_easily", metal="silver",
              veins="blue", hair_color="blond-platine", eye_color="bleu-gris")),
        ("Peau mate sous-ton froid cheveux bruns",
         dict(skin_depth="tan", sun_reaction="tans_easily", metal="silver",
              veins="blue", hair_color="brun", eye_color="marron")),
        ("Cheveux gris peau claire (senior)",
         dict(skin_depth="light", sun_reaction="burns_then_tans", metal="silver",
              veins="mixed", hair_color="gris", eye_color="bleu")),
        ("Peau foncee cheveux noirs yeux verts",
         dict(skin_depth="deep", sun_reaction="rarely_burns", metal="gold",
              veins="green", hair_color="noir", eye_color="vert")),
    ]

    print(f"{'CAS':<42} {'SAISON':<11} {'SOUS-TON':<8} {'CONTR':<7} {'INT':<8} LIBELLE")
    print("-" * 95)
    for label, kwargs in cases:
        r = analyze_declarative(**kwargs)
        print(f"{label:<42} {r['saison_confirmee']:<11} {r['sous_ton_detecte']:<8} "
              f"{r['contraste_naturel']:<7} {r['intensite']:<8} {r['libelle_complet']} "
              f"(conf {r['_confidence']})")


# ---------------------------------------------------------------------------
# HELPER POUR LE CHEMIN PHOTO
# GPT vision renvoie deja valeur_peau / contraste_naturel / intensite.
# On applique le meme calcul de sous-type pour que l'affichage soit identique
# sur les deux chemins.
# ---------------------------------------------------------------------------

_VALEUR_TO_DEPTH = {"clair": 2, "moyen": 5, "fonce": 8}
_CONTRAST_TO_GAP = {"faible": 1, "moyen": 4, "fort": 7}


def subtype_from_labels(season: str, valeur_peau: str, contraste_naturel: str,
                        intensite: str, hair_color: str, sous_ton: str) -> dict:
    """
    Calcule le sous-type a partir des libelles renvoyes par GPT vision.
    Retourne {"sous_type": str, "libelle_complet": str}.
    """
    season = (season or "").strip()
    if season not in ("Printemps", "Ete", "Été", "Automne", "Hiver"):
        return {"sous_type": "", "libelle_complet": season}
    season_key = "Ete" if season in ("Ete", "Été") else season

    skin_depth_value = _VALEUR_TO_DEPTH.get((valeur_peau or "").strip().lower(), 5)
    hair_depth_value = HAIR_DEPTH_SCALE.get((hair_color or "").strip().lower(), 6)
    lightness = (skin_depth_value + hair_depth_value) / 2

    contrast_label = (contraste_naturel or "moyen").strip().lower()
    if contrast_label not in ("faible", "moyen", "fort"):
        contrast_label = "moyen"
    contrast_gap = _CONTRAST_TO_GAP[contrast_label]

    intensity = (intensite or "medium").strip().lower()
    if intensity not in ("douce", "medium", "intense"):
        intensity = "medium"

    st = (sous_ton or "neutre").strip().lower()
    temp_score = 0.5 if st == "chaud" else (-0.5 if st == "froid" else 0.0)

    subtype = compute_subtype(season_key, lightness, contrast_label, intensity,
                              temp_score, contrast_gap, skin_depth_value)
    return {
        "sous_type": subtype,
        "libelle_complet": f"{season} {subtype}".strip(),
    }