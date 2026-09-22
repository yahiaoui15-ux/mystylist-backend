"""
Selection deterministe des coupes par morphologie et souhaits client.

Remplace le choix des coupes par GPT. GPT ne fera plus que rediger les
commentaires a partir des coupes que ce module a selectionnees.

Cascade de selection :
  1. FILTRE morphologie  — la silhouette doit etre dans `morphologies`
                           et absente de `deconseillees`
  2. VETO exposition     — toute coupe qui expose une zone que la
                           cliente veut dissimuler est ecartee
  3. FILTRE stature      — longueurs et volumes incompatibles ecartes
  4. SCORE pondere       — attenue une zone a minimiser : +3
                           flatte une zone a valoriser   : +2
                           expose une zone a valoriser   : +1
  5. SEUIL               — score minimum de 2, sauf si aucun souhait
                           ne concerne la categorie
  6. DEDUPLICATION       — jamais deux coupes partageant la meme image
"""

import re
import unicodedata
from functools import lru_cache
from typing import Any, Dict, List, Optional

from app.utils.supabase_client import supabase


# Zones qui ne filtrent rien : elles ne designent pas une zone habillable
ZONES_JOKER = {"silhouette", "visage"}

# Zones ou "flatte" signifie "met en avant, elargit" : a proscrire si la
# cliente veut les dissimuler. Sur jambes et taille, "flatte" signifie
# "affine, allonge", ce qui lui convient au contraire.
ZONES_ACCENTUEES = {"epaules", "hanches", "poitrine", "decollete", "bras"}

# Quelles zones ont un sens pour quelle categorie
ZONES_PAR_CATEGORIE = {
    "haut":    {"ventre", "taille", "poitrine", "decollete", "epaules", "bras"},
    "bas":     {"ventre", "taille", "hanches", "jambes"},
    "robe":    {"ventre", "taille", "poitrine", "decollete", "epaules",
                "bras", "hanches", "jambes"},
    "veste":   {"ventre", "taille", "poitrine", "decollete", "epaules",
                "bras", "hanches"},
    "manteau": {"ventre", "taille", "poitrine", "decollete", "epaules",
                "bras", "hanches", "jambes"},
}

# Regles de stature (taille en cm)
PETITE_MAX = 160
GRANDE_MIN = 172

# Familles de coupes : deux pieces de la meme famille ne sont jamais
# proposees ensemble dans une categorie. L'ordre compte — le premier
# motif trouve dans la cle determine la famille.
FAMILLES = [
    ("cache_coeur", "cache_coeur"), ("croisee", "cache_coeur"),
    ("peplum", "peplum"), ("chauve_souris", "chauve_souris"),
    ("bouffante", "manches_bouffantes"), ("epaulette", "epaulettes"),
    ("col_roul", "col_roule"), ("col_montant", "col_montant"),
    ("col_bateau", "col_bateau"), ("bardot", "col_bateau"),
    ("encolure_bateau", "col_bateau"), ("col_carre", "col_carre"),
    ("encolure_carree", "col_carre"), ("encolure_u", "encolure_u"),
    ("col_v", "col_v"), ("encolure_en_v", "col_v"),
    ("drape", "drape"), ("moulante", "moulante"), ("fourreau", "moulante"),
    ("portefeuille", "portefeuille"), ("trapeze", "evase"),
    ("a_line", "evase"), ("evasee", "evase"), ("evase", "evase"),
    ("patineuse", "evase"), ("plissee", "plisse"), ("froncee", "fronce"),
    ("palazzo", "large_fluide"), ("large_fluide", "large_fluide"),
    ("skinny", "ajuste_jambe"), ("slim", "ajuste_jambe"),
    ("legging", "ajuste_jambe"), ("flare", "flare"), ("bootcut", "flare"),
    ("cape", "cape"), ("poncho", "cape"), ("doudoune", "doudoune"),
    ("blazer", "blazer"), ("trench", "trench"), ("duffle", "duffle"),
    ("body", "body"), ("debardeur", "debardeur"), ("tunique", "tunique"),
    ("ceinture", "ceinture"), ("cintre", "cintre"),
    ("taille_haute", "taille_haute"), ("oversize", "oversize"),
]


def _famille(cle: str) -> str:
    """Famille de coupe, pour eviter de proposer 4 fois la meme idee."""
    for motif, fam in FAMILLES:
        if motif in cle:
            return fam
    return cle

class CutSelector:
    """Selectionne les coupes a recommander. Aucun appel OpenAI."""

    @lru_cache(maxsize=1)
    def _load(self) -> List[Dict[str, Any]]:
        client = supabase.get_client()
        resp = client.table("visuels").select(
            "nom_simplifie,coupe,type_vetement,url_image,"
            "morphologies,deconseillees,flatte,attenue,expose,"
            "longueur,volume,manches"
        ).execute()
        rows = resp.data or []
        out = []
        for r in rows:
            if r.get("type_vetement") not in ZONES_PAR_CATEGORIE:
                continue
            if not r.get("url_image"):
                continue
            out.append({
                "cle":       r["nom_simplifie"],
                "coupe":     r.get("coupe") or r["nom_simplifie"],
                "categorie": r["type_vetement"],
                "url":       r["url_image"],
                "morphos":   set(r.get("morphologies") or []),
                "deco":      set(r.get("deconseillees") or []),
                "flatte":    set(r.get("flatte") or []),
                "attenue":   set(r.get("attenue") or []),
                "expose":    set(r.get("expose") or []),
                "longueur":  r.get("longueur") or "",
                "volume":    r.get("volume") or "",
                "manches":   r.get("manches") or "",
            })
        return out

    # ------------------------------------------------------------------

    @staticmethod
    def _nettoyer(zones) -> set:
        """Retire les jokers et normalise."""
        out = set()
        for z in (zones or []):
            if not isinstance(z, str):
                continue
            z = unicodedata.normalize("NFKD", z.strip().lower())
            z = "".join(c for c in z if not unicodedata.combining(c))
            z = re.sub(r"[^a-z]", "", z)
            if z and z not in ZONES_JOKER:
                out.add(z)
        return out

    @staticmethod
    def _stature_ok(coupe: Dict[str, Any], taille_cm: Optional[int]) -> bool:
        if not taille_cm:
            return True
        if taille_cm < PETITE_MAX:
            # une petite silhouette est coupee par les longueurs mollet
            # et noyee par les volumes amples
            if coupe["longueur"] == "mollet":
                return False
            if coupe["volume"] == "ample" and coupe["longueur"] in ("cuisse", "cheville"):
                return False
        if taille_cm > GRANDE_MIN:
            # sur une grande silhouette, les vestes tres courtes
            # deseequilibrent les proportions
            if coupe["categorie"] in ("veste", "manteau") and coupe["longueur"] == "taille":
                return False
        return True

    # ------------------------------------------------------------------

    def selectionner(
        self,
        silhouette: str,
        a_minimiser: Optional[List[str]] = None,
        a_valoriser: Optional[List[str]] = None,
        categorie: str = "haut",
        nombre: int = 3,
        taille_cm: Optional[int] = None,
        urls_deja_prises: Optional[set] = None,
    ) -> List[Dict[str, Any]]:
        """Retourne au plus `nombre` coupes, triees par pertinence."""

        silhouette = (silhouette or "").strip().upper()
        minim = self._nettoyer(a_minimiser)
        valor = self._nettoyer(a_valoriser)
        deja = urls_deja_prises if urls_deja_prises is not None else set()

        pertinentes = ZONES_PAR_CATEGORIE.get(categorie, set())
        minim_cat = minim & pertinentes
        valor_cat = valor & pertinentes
        aucun_souhait = not minim_cat and not valor_cat

        candidats = []
        for c in self._load():
            if c["categorie"] != categorie:
                continue

            # 1. morphologie
            if silhouette and silhouette not in c["morphos"]:
                continue
            if silhouette and silhouette in c["deco"]:
                continue

            # 2. veto : on n'expose ni n'accentue une zone a dissimuler
            if c["expose"] & minim_cat:
                continue
            if c["flatte"] & minim_cat & ZONES_ACCENTUEES:
                continue

            # 2 bis. veto manches : bras a dissimuler
            if "bras" in minim_cat and c["manches"] == "sans":
                continue

            # 3. stature — souple : classe apres, n'exclut pas
            niveau = 0 if self._stature_ok(c, taille_cm) else 2

            # 4. score
            score = (3 * len(c["attenue"] & minim_cat)
                     + 2 * len(c["flatte"] & valor_cat)
                     + 1 * len(c["expose"] & valor_cat))
            if "bras" in minim_cat:
                if c["manches"] == "longues":
                    score += 3 if c["volume"] in ("ample", "droit") else 2
                elif c["manches"] == "trois_quarts":
                    score += 1

            # 5. seuil — souple : une coupe sous le seuil ne sort que si
            # le quota ne peut pas etre rempli autrement
            if not aucun_souhait and score < 2:
                niveau = max(niveau, 1)

            candidats.append((niveau, score, c))

        # tri deterministe : niveau, puis score, puis ordre alphabetique
        candidats.sort(key=lambda x: (x[0], -x[1], x[2]["cle"]))

        # 6. deduplication par image ET par famille de coupe
        retenues, urls, familles = [], set(deja), set()
        for passe in (1, 2):
            if len(retenues) >= nombre:
                break
            for niveau, score, c in candidats:
                if len(retenues) >= nombre:
                    break
                if c["url"] in urls:
                    continue
                fam = _famille(c["cle"])
                # passe 1 : une seule piece par famille
                # passe 2 : on relache si le quota n'est pas atteint
                if passe == 1 and fam in familles:
                    continue
                urls.add(c["url"])
                familles.add(fam)
                retenues.append({
                    "visual_key": c["cle"],
                    "name":       c["coupe"],
                    "visual_url": c["url"],
                    "score":      score,
                    "flatte":     sorted(c["flatte"] & valor_cat),
                    "attenue":    sorted(c["attenue"] & minim_cat),
                    "manches":    c["manches"],
                    "longueur":   c["longueur"],
                    "volume":     c["volume"],
                })

        return retenues

    def a_eviter(
        self,
        silhouette: str,
        a_minimiser: Optional[List[str]] = None,
        categorie: str = "haut",
        nombre: int = 1,
    ) -> List[Dict[str, Any]]:
        """Coupes deconseillees : contre-indiquees pour la silhouette,
        ou exposant une zone que la cliente veut dissimuler."""

        silhouette = (silhouette or "").strip().upper()
        minim = self._nettoyer(a_minimiser) & ZONES_PAR_CATEGORIE.get(categorie, set())

        out = []
        for c in self._load():
            if c["categorie"] != categorie:
                continue
            raison = None
            if silhouette and silhouette in c["deco"]:
                raison = "silhouette"
            elif c["expose"] & minim:
                raison = "expose:" + ",".join(sorted(c["expose"] & minim))
            if raison:
                out.append({"visual_key": c["cle"], "name": c["coupe"],
                            "raison": raison})
        out.sort(key=lambda x: x["visual_key"])
        return out[:nombre]

    def selectionner_rapport(
        self,
        silhouette: str,
        a_minimiser: Optional[List[str]] = None,
        a_valoriser: Optional[List[str]] = None,
        taille_cm: Optional[int] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Selection complete pour un rapport. La deduplication d'image
        est partagee entre categories : une meme photo n'apparait jamais
        deux fois dans le document."""

        quotas = [("haut", 4), ("bas", 3), ("robe", 2),
                  ("veste", 2), ("manteau", 1)]
        urls = set()
        res = {}
        for cat, n in quotas:
            sel = self.selectionner(
                silhouette=silhouette, a_minimiser=a_minimiser,
                a_valoriser=a_valoriser, categorie=cat, nombre=n,
                taille_cm=taille_cm, urls_deja_prises=urls,
            )
            for s in sel:
                urls.add(s["visual_url"])
            res[cat] = sel
        return res


cut_selector = CutSelector()