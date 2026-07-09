# app/services/product_matcher_service.py
from typing import Dict, Any, List, Optional
import re
import hashlib
import os
import httpx
import unicodedata

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.utils.supabase_client import supabase
from urllib.parse import quote, urlparse




class ProductMatcherService:
    """
    Match une pièce IA vers:
    1) un produit affilié (TABLE: affiliate_products)
    2) sinon un visuel pédagogique (table `visuels`)

    v10 (Fix précision produits):
    - PHASE 1 COMPOUND: recherche "pantalon palazzo", "robe portefeuille", "jupe trapeze"
      avant de rechercher uniquement "pantalon", "robe", "jupe"
    - RE-SCORING FINAL: remonte les candidats contenant le plus de mots-clés
      de la recommandation (nom de pièce + qualificatif de coupe)
    - PHASE 0: style-aware search via affiliate_product_enrichment (inchangé)
    - Image-first selection: tente jusqu'à 4 candidats pour le produit principal
    """

    VISUELS_TYPE_MAP = {
        "tops": "haut",
        "bottoms": "bas",
        "dresses_playsuits": "robe",
        "outerwear": "haut",
        "swim_lingerie": "lingerie",
        "shoes": "chaussures",
        "accessories": "accessoire",
    }

    PRODUCT_BLACKLIST_KEYWORDS = [
        "trousse", "pochette beaute", "pochette maquillage",
        "sac voyage", "bagage", "valise", "cosmetic",
        "beauty bag", "bébé", "bebe", "enfant", "garçon", "garcon", "fille",
        "maternité", "maternite", "sport", "jogging", "pyjama", "nuisette",
        # Maroquinerie / accessoires financiers — évite de confondre
        # "robe portefeuille" avec un vrai portefeuille en cuir
        "portefeuille en cuir", "portefeuille effet cuir", "portefeuille graffiti",
        "porte-cartes", "porte-monnaie", "porte carte", "porte monnaie",
    ]

    # ── Termes structurels obligatoires ──────────────────────────────────────
    # Si la pièce GPT contient l'un de ces termes, le produit affilié DOIT
    # contenir ce terme (ou un de ses alias). Sinon exclu.
    # Seuls les termes avec ≥30 produits en base sont pertinents ici.
    _STRUCTURAL_TERMS = {
        "peplum",        # 11 produits  — très spécifique, garder
        "portefeuille",  # 601 produits ✅
        "cache coeur",   # 33 produits  — silhouette unique
        "cache-coeur",   # alias normalisé
        "trapeze",       # 134 produits — accepte aussi "evase" via aliases
        "evase",         # 1891 produits ✅ terme Rakuten pour "trapèze"
        "palazzo",       # 55 produits  ✅
        "wide leg",      # 108 produits ✅ terme anglais utilisé par Rakuten
        "cargo",         # 94 produits  ✅
    }
    # Supprimés vs version précédente :
    # "empire" (6 produits), "fourreau" (8), "col v", "col u", "col bateau",
    # "col carre", "bustier", "croise", "wrap" (0), "manches bouffantes", "raglan"
 
    # ── Aliases : terme GPT → terme(s) réellement utilisés par Rakuten ───────
    # Quand GPT génère un terme qui ne correspond pas à la nomenclature Rakuten,
    # on le traduit AVANT la recherche ET avant le filtre structurel.
    # Format : "terme_gpt": ["alias1", "alias2", ...]
    _STRUCTURAL_TERM_ALIASES: Dict[str, List[str]] = {
        # Coupes — termes GPT → équivalents Rakuten
        "trapeze":          ["trapeze", "evase", "patineuse"],   # 134+1891+36
        "evase":            ["evase", "trapeze", "patineuse"],   # même silhouette
        "a-line":           ["evase", "trapeze"],                # anglais → fr
        "a line":           ["evase", "trapeze"],
        "cache coeur":      ["cache coeur", "cache-coeur"],
        "cache-coeur":      ["cache coeur", "cache-coeur"],
        "portefeuille":     ["portefeuille"],                    # 601 ✅
        "wrap":             ["portefeuille", "cache coeur"],     # 0 → 601
        "peplum":           ["peplum"],                          # 11 ✅
        "palazzo":          ["palazzo", "wide leg"],             # 55+108
        "wide leg":         ["wide leg", "palazzo"],
        "jambe large":      ["wide leg", "palazzo"],             # 0 → 108
        "cargo":            ["cargo"],                           # 94 ✅
        "empire":           ["empire"],                          # 6 — pas structural mais garde keyword
        "fourreau":         ["fourreau"],                        # 8 — idem
        "droite":           ["droite"],                          # 4410 mais trop générique
        # Cols — GPT utilise souvent la terminologie morphologique
        "col u":            ["col rond"],                        # 11 → 10715
        "encolure u":       ["col rond"],
        "col en u":         ["col rond"],
        "ras du cou":       ["col rond"],
        "col arrondi":      ["col rond"],
        "col v":            ["col v", "decollete v", "encolure v"],  # 6130+82+75
        "decollete v":      ["col v", "decollete v"],
        "encolure v":       ["col v", "encolure v"],
        "col bateau":       ["col bateau"],                      # 423 ✅
        "col mariniere":    ["col bateau"],                      # 0 → 423
        "col carre":        ["col carre"],                       # 301 ✅
        "col montant":      ["col montant"],                     # 1179 ✅
        "col claudine":     ["col claudine", "col montant"],     # 51+1179
        # Manches
        "manches bouffantes": ["manches bouffantes", "manches ballon"],  # 38+28
        "manches ballon":     ["manches ballon", "manches bouffantes"],
        "manches volantees":  ["manches bouffantes", "manches ballon"],  # 0 → 38
        "sans manches":       ["sans manches"],                  # 1749 ✅
        # Anglicismes présents dans la base Rakuten
        "wide":             ["wide leg", "large"],
        "flare":            ["evase", "trapeze"],
    }
 
    # ── Aliases simples pour la recherche keyword ─────────────────────────────
    # Traduction directe d'un terme GPT vers SON équivalent Rakuten principal.
    # Utilisé dans _extract_keywords pour normaliser les termes avant ILIKE.
    _GPT_TO_RAKUTEN_KW: Dict[str, str] = {
        "col u":            "col rond",
        "encolure u":       "col rond",
        "col en u":         "col rond",
        "ras du cou":       "col rond",
        "col arrondi":      "col rond",
        "a-line":           "evase",
        "a line":           "evase",
        "wrap":             "portefeuille",
        "jambe large":      "wide leg",
        "jambe droite":     "droite",
        "col mariniere":    "col bateau",
        "manches volantees": "manches bouffantes",
        "manches bishope":  "manches bouffantes",
        "decollete v":      "col v",
        "encolure v":       "col v",
    }
 
    # ── Mapping styles styling → tags enrichment ──────────────────────────
    STYLE_LABEL_TO_ENRICHMENT_TAG: Dict[str, str] = {
        "Classique": "classique",
        "Chic": "chic",
        "Casual": "casual",
        "Rock": "rock",
        "Moderne": "moderne",
        "Sporty Chic": "sportswear",
        "Sportswear": "sportswear",
        "Vintage": "vintage",
        "Bohème": "boheme",
        "Boheme": "boheme",
        "Romantique": "romantique",
        "Minimaliste": "minimaliste",
        "Style Classique / Intemporel": "classique",
        "Style Chic / Élégant": "chic",
        "Style Casual / Décontracté": "casual",
        "Style Rock": "rock",
        "Style Moderne / Contemporain": "moderne",
        "Style Sporty Chic": "sportswear",
        "Style Urbain / Streetwear": "sportswear",
        "Style Vintage": "vintage",
        "Style Bohème": "boheme",
        "Style Romantique": "romantique",
        "Style Minimaliste": "minimaliste",
        "Style Naturel / Authentique": "boheme",
        "Style Féminin Moderne": "moderne",
        "Style Artistique / Créatif": "rock",
    }

    AFFILIATE_TABLE = os.getenv("AFFILIATE_TABLE", "affiliate_products")
    AFFILIATE_IMAGE_BUCKET = os.getenv("AFFILIATE_IMAGE_BUCKET", "affiliate-cache")
    AFFILIATE_PRIMARY_CATEGORY = (os.getenv("AFFILIATE_PRIMARY_CATEGORY", "Femme") or "").strip()

    HTTP_TIMEOUT = float(os.getenv("PDT_HTTP_TIMEOUT", "8.0").strip() or "8.0")
    MAX_TOKEN_LEN = int(os.getenv("PDT_MAX_TOKEN_LEN", "48").strip() or "48")

    PDT_PRODUCT_ID_RE = re.compile(r"(\d{6,})", re.IGNORECASE)
    AFFILIATE_HOST_HINTS = ("linksynergy.com", "linkshare.com", "rakuten", "awin")

    CATEGORY_TOKENS = {
        "tops": ["top", "tops", "haut", "hauts", "blouse", "chemis", "tee", "t-shirt", "pull", "maille", "sweat"],
        "bottoms": ["bas", "pantalon", "jean", "jupe", "short", "trouser", "pants", "jeans", "skirt", "shorts"],
        "dresses_playsuits": ["robe", "dress", "dresses", "combinaison", "jumpsuit", "playsuit"],
        "outerwear": ["manteau", "veste", "blouson", "trench", "coat", "jacket", "blazer"],
        "swim_lingerie": ["lingerie", "underwear", "swim", "swimwear", "maillot"],
        "shoes": ["chauss", "shoe", "shoes", "boots", "boot", "sneaker", "basket", "sandale"],
        "accessories": ["access", "accessory", "accessories", "sac", "bag", "ceinture", "belt", "bijou", "jewel"],
    }

    def __init__(self):
        self.client = supabase.get_client()

    # -------------------------
    # Public API
    # -------------------------
    def enrich_pieces(
        self,
        pieces: List[Dict[str, Any]],
        category: str,
        style_tags: Optional[List[str]] = None,
        colors_to_avoid: Optional[List[str]] = None,
        colors_best: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        out = []
        for p in pieces or []:
            if not isinstance(p, dict):
                continue
            p2 = dict(p)
            p2["match"] = self.match_piece(p2, category, style_tags=style_tags,
                                            colors_to_avoid=colors_to_avoid,
                                            colors_best=colors_best)
            m = p2.get("match") or {}
            p2["image_url"] = (m.get("image_url") or "").strip()
            p2["product_url"] = (m.get("product_url") or "").strip()
            p2["source"] = (m.get("source") or "").strip()
            out.append(p2)
        return out

    def match_piece(
        self,
        piece: Dict[str, Any],
        category: str,
        style_tags: Optional[List[str]] = None,
        colors_to_avoid: Optional[List[str]] = None,
        colors_best: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
 
        piece_title = (piece.get("piece_title") or "").strip()
        spec = (piece.get("spec") or "").strip()
        visual_key = (piece.get("visual_key") or "").strip()

        candidates = self._find_affiliate_products(
            piece_title=piece_title,
            spec=spec,
            category=category,
            limit=20,
            style_tags=style_tags,
            colors_to_avoid=colors_to_avoid,
            colors_best=colors_best,
        )
 
        # ── IMAGE-FIRST: on tente jusqu'à 4 candidats pour trouver une image ──
        valid_pool = self._pick_top_n_valid_candidates(
            candidates, n=4,
            colors_to_avoid=colors_to_avoid,
            colors_best=colors_best,
            piece_title=piece_title,
        )
 

        try:
            print(f"🧩 MATCH [{category}] '{piece_title[:60]}' → {len(candidates)} candidats / {len(valid_pool)} retenus")
        except Exception:
            pass

        if valid_pool:
            main = None
            safe_img = ""
            remaining = []

            for idx, candidate in enumerate(valid_pool):
                raw_img = (candidate.get("image_url") or "").strip()
                img = self._ensure_cached_public_image(raw_img, candidate) if raw_img else ""
                print("🖼️ IMG raw:", raw_img)
                print("🖼️ IMG safe:", img)
                if img:
                    main = candidate
                    safe_img = img
                    remaining = valid_pool[idx + 1:]
                    break

            if main is None:
                main = valid_pool[0]
                remaining = valid_pool[1:]

            alt1 = remaining[0] if len(remaining) > 0 else None
            alt2 = remaining[1] if len(remaining) > 1 else None

            return {
                "image_url": safe_img,
                "product_url": (main.get("buy_url") or main.get("product_url") or "").strip(),
                "source": "affiliate",
                "title": (main.get("product_name") or piece_title).strip(),
                "brand": (main.get("brand") or "").strip(),
                "price": str(main.get("price", "") or ""),
                "alt1_url": ((alt1 or {}).get("buy_url") or (alt1 or {}).get("product_url") or "").strip(),
                "alt1_label": self._format_alt_label(alt1) if alt1 else "",
                "alt2_url": ((alt2 or {}).get("buy_url") or (alt2 or {}).get("product_url") or "").strip(),
                "alt2_label": self._format_alt_label(alt2) if alt2 else "",
            }

        # 2) fallback visuel pédagogique
        visual = self._find_visual_by_key(visual_key=visual_key, category=category)
        if visual:
            return {
                "image_url": (visual.get("url_image") or "").strip(),
                "product_url": "",
                "source": "visual",
                "title": piece_title,
                "brand": "",
                "price": "",
                "alt1_url": "",
                "alt1_label": "",
                "alt2_url": "",
                "alt2_label": "",
            }

        print(f"⚠️ No visual fallback for visual_key='{visual_key}'")
        return {
            "image_url": "",
            "product_url": "",
            "source": "none",
            "title": piece_title,
            "brand": "",
            "price": "",
            "alt1_url": "",
            "alt1_label": "",
            "alt2_url": "",
            "alt2_label": "",
        }

    def match_piece_top4(
        self,
        piece: Dict[str, Any],
        category: str,
        colors_to_avoid: Optional[List[str]] = None,
        colors_best: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
 
        """
        Comme match_piece mais retourne une LISTE de 4 produits complets.
        Utilisé pour shopping_products_flat (page 12).
        """
        piece_title = (piece.get("piece_title") or "").strip()
        spec        = (piece.get("spec") or "").strip()

        candidates = self._find_affiliate_products(
            piece_title=piece_title,
            spec=spec,
            category=category,
            limit=30,
            colors_to_avoid=colors_to_avoid,
            colors_best=colors_best,
        )
        top4 = self._pick_top_n_valid_candidates(
            candidates, n=4,
            colors_to_avoid=colors_to_avoid,
            colors_best=colors_best,
            piece_title=piece_title,
        )
 
        results = []
        for candidate in top4:
            raw_img  = (candidate.get("image_url") or "").strip()
            safe_img = self._ensure_cached_public_image(raw_img, candidate) if raw_img else ""
            results.append({
                "image_url":   safe_img,
                "product_url": (candidate.get("buy_url") or candidate.get("product_url") or "").strip(),
                "brand":       (candidate.get("brand") or "").strip(),
                "price":       str(candidate.get("price", "") or ""),
                "title":       (candidate.get("product_name") or piece_title).strip(),
            })
            status = "✅" if safe_img else "⚠️"
            print(f"   {status} TOP4 [{category}] '{piece_title[:40]}' → {(candidate.get('brand') or '')[:20]}")

        return results

    # -------------------------
    # Style helpers
    # -------------------------
    def _map_styles_to_enrichment_tags(self, style_labels: List[str]) -> List[str]:
        tags = []
        for label in style_labels or []:
            label = (label or "").strip()
            tag = self.STYLE_LABEL_TO_ENRICHMENT_TAG.get(label)
            if tag:
                tags.append(tag)
            else:
                normalized = self._strip_accents(label.lower())
                if normalized.startswith("style "):
                    normalized = normalized[6:]
                normalized = re.sub(r"[^a-z0-9]", "", normalized)
                if len(normalized) >= 3:
                    tags.append(normalized)
        return list(dict.fromkeys(tags))

    def _find_affiliate_products_phase0_style(
        self,
        piece_title: str,
        style_tags: List[str],
        category: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        PHASE 0 — Style-aware: requête affiliate_product_enrichment sur style_primary.
        """
        if not style_tags:
            return []

        enrichment_tags = self._map_styles_to_enrichment_tags(style_tags)
        if not enrichment_tags:
            return []

        select_fields = ",".join([
            "product_id", "product_name", "brand", "primary_category",
            "secondary_category", "product_url", "image_url", "buy_url",
            "price", "sale_price", "currency", "availability",
            "is_deleted", "last_seen_at",
        ])

        try:
            q_enrich = (
                self.client.table("affiliate_product_enrichment")
                .select("product_id")
                .in_("style_primary", enrichment_tags)
                .limit(200)
            )
            resp_enrich = self._execute(q_enrich)
            enrich_data = getattr(resp_enrich, "data", None) or []
            product_ids = [row["product_id"] for row in enrich_data if row.get("product_id")]

            if not product_ids:
                return []

            kws = self._extract_keywords(piece_title, "")
            print(f"🔑 KWS (phase0) pour '{piece_title}': {kws}")   # ← à ajouter, à retirer une fois le diagnostic fait
            kw_safe = self._normalize_kw_for_ilike(kws[0]) if kws else ""

            q_products = (
                self.client.table(self.AFFILIATE_TABLE)
                .select(select_fields)
                .eq("is_deleted", False)
                .in_("product_id", product_ids[:50])
            )
            if self.AFFILIATE_PRIMARY_CATEGORY:
                q_products = q_products.eq("primary_category", self.AFFILIATE_PRIMARY_CATEGORY)
            if len(kw_safe) >= 3:
                q_products = q_products.ilike("product_name", self._ilike_pattern(kw_safe))

            q_products = q_products.limit(40)
            resp_products = self._execute(q_products)
            data = getattr(resp_products, "data", None) or []

            filtered = [r for r in data if self._category_match(r, category)]
            if filtered:
                print(f"✅ PHASE0 style [{category}] tags={enrichment_tags}: {len(filtered)} produits")
            return filtered[:limit]

        except Exception as e:
            print(f"⚠️ PHASE 0 style failed: {e}")
            return []

    # -------------------------
    # Relevance scoring  ← NEW
    # -------------------------
    def _score_candidate(
        self,
        candidate: Dict[str, Any],
        kws: List[str],
        colors_best: Optional[List[str]] = None,
    ) -> int:
 
        """
        Score un candidat selon le nombre de mots-clés de la recommandation
        présents dans son product_name.
        Chaque mot-clé trouvé vaut 1 point.
        Les mots-clés de coupe (palazzo, portefeuille, trapèze...) rapportent
        un bonus de 2 points supplémentaires car ils sont les plus discriminants.

        Exemples :
          "Pantalon palazzo Iro"    vs kws=["pantalon","palazzo"] → score 3 (1+2)
          "Pantalon slim en coton"  vs kws=["pantalon","palazzo"] → score 1 (1+0)
        """
        name_raw = (candidate.get("product_name") or "").lower()
        name = self._strip_accents(name_raw)

        CUT_TOKENS = {
            "empire", "portefeuille", "trapeze", "droit", "droite",
            "palazzo", "evase", "evasee", "cintre", "cintree", "oversize", "fluide",
            "ajuste", "ajustee", "structure", "structuree", "ceinture", "ceinturee",
            "long", "longue", "midi", "mini", "court", "courte",
            "croise", "croisee", "wrap", "flare", "wide", "large",
        }

        score = 0
        for kw in kws:
            kw_norm = self._strip_accents(kw.lower())
            if kw_norm in name:
                score += 1
                # Bonus pour les qualificatifs de coupe — très discriminants
                if kw_norm in CUT_TOKENS:
                    score += 2
        # Bonus couleurs favorites (palette cliente)
        if colors_best:
            name_for_color = self._strip_accents((candidate.get("product_name") or "").lower())
            for col in (colors_best or []):
                col_norm = self._strip_accents(col.lower())
                if col_norm and col_norm in name_for_color:
                    score += 4
                    break
        return score
 

    def _rescore_collected(
        self,
        collected: List[Dict[str, Any]],
        kws: List[str],
        colors_best: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Trie `collected` par score décroissant de pertinence.
        Les produits avec score 0 restent à la fin (fallback).
        Préserve l'ordre d'arrivée à score égal (tri stable Python).
        """
        if not kws:
            return collected
        scored = [
            (self._score_candidate(c, kws, colors_best=colors_best), i, c)
            for i, c in enumerate(collected)
        ]
 
        scored.sort(key=lambda x: (-x[0], x[1]))
        result = [c for _, _, c in scored]
        # Log les 4 premiers pour diagnostic
        for rank, (score, _, c) in enumerate(scored[:4]):
            name = (c.get("product_name") or "")[:50]
            print(f"   🏅 RANK {rank+1} score={score} '{name}'")
        return result

    # -------------------------
    # Output helpers
    # -------------------------
    def _format_alt_label(self, row: Optional[Dict[str, Any]]) -> str:
        if not row:
            return ""
        brand = (row.get("brand") or "").strip()
        price = row.get("price")
        title = (row.get("product_name") or "").strip()
        p = f"{price}€" if price is not None and str(price).strip() else ""
        if brand and p:
            return f"{brand} — {p}"
        if brand:
            return brand
        if title:
            return title[:48] + ("…" if len(title) > 48 else "")
        return "Alternative"

    def _find_visual_by_key(
        self, visual_key: str, category: str
    ) -> Optional[Dict[str, Any]]:
        """
        Fallback pédagogique : cherche un visuel dans la table 'visuels'
        quand aucun produit affilié ne correspond.
        Colonnes : type_vetement, coupe, nom_simplifie, url_image
        """
        if not visual_key:
            return None
        try:
            client = self.client

            # 1. Correspondance exacte sur nom_simplifie (ex: "pull_col_u")
            resp = (
                client.table("visuels")
                .select("*")
                .eq("nom_simplifie", visual_key)
                .limit(1)
                .execute()
            )
            if resp.data:
                return resp.data[0]

            # 2. Correspondance partielle sur coupe
            kw = self._strip_accents(visual_key.replace("_", " ").lower())
            resp2 = (
                client.table("visuels")
                .select("*")
                .ilike("coupe", f"%{kw}%")
                .limit(1)
                .execute()
            )
            if resp2.data:
                return resp2.data[0]

            # 3. Fallback sur type_vetement selon la catégorie
            cat = self._strip_accents(category.lower())
            resp3 = (
                client.table("visuels")
                .select("*")
                .ilike("type_vetement", f"%{cat}%")
                .limit(1)
                .execute()
            )
            return resp3.data[0] if resp3.data else None

        except Exception as e:
            print(f"⚠️ _find_visual_by_key failed key='{visual_key}': {e}")
            return None
        
    # -------------------------
    # Candidate selection / dedupe
    # -------------------------
    def _normalize_name_for_dedup(self, name: str) -> str:
        """
        Normalise un nom de produit pour la déduplication des variantes taille/couleur.
        "Brand - Pantalon palazzo femme - Taille S - Marron"
        "Brand - Pantalon palazzo femme - Taille L - Gris"
        → deviennent le même key "brand - pantalon palazzo femme"
        """
        name = (name or "").strip().lower()
        # Supprime le suffixe " - Taille XX - Couleur" et tout ce qui suit
        name = re.sub(r"\s*-\s*taille\s+\S+.*$", "", name, flags=re.IGNORECASE)
        # Supprime aussi les suffixes " - Couleur" seuls sans taille (ex: "- Noir - Place des T...")
        name = re.sub(r"\s*-\s*(noir|blanc|beige|gris|rouge|bleu|vert|rose|marron|camel|kaki|marine|bordeaux|multicolore|imprim\w*).*$", "", name, flags=re.IGNORECASE)
        return name.strip()[:80]

    def _pick_top3_valid_candidates(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return self._pick_top_n_valid_candidates(candidates, n=3)

    def _pick_top_n_valid_candidates(
        self,
        candidates: List[Dict[str, Any]],
        n: int = 4,
        colors_to_avoid: Optional[List[str]] = None,
        colors_best: Optional[List[str]] = None,
        piece_title: str = "",
    ) -> List[Dict[str, Any]]:
 

        # Termes structurels présents dans le titre de la pièce
        _title_norm = self._strip_accents((piece_title or "").lower())
        _required = [t for t in self._STRUCTURAL_TERMS if t in _title_norm]
 
 
        out: List[Dict[str, Any]] = []
        seen_urls        = set()
        seen_names_dedup = set()   # ← clé normalisée (sans taille/couleur)
        seen_images      = set()

        for c in candidates or []:
            if not isinstance(c, dict):
                continue

            buy_url    = (c.get("buy_url") or "").strip()
            product_id = str(c.get("product_id") or "").strip()
            raw_img    = (c.get("image_url") or "").strip()

            if not buy_url and not product_id and not raw_img:
                continue

            url_key = buy_url or product_id or raw_img

            # Clé de déduplication normalisée — filtre les variantes taille/couleur
            raw_name   = (c.get("product_name") or "").strip()
            dedup_name = self._normalize_name_for_dedup(raw_name)

            img_base = raw_img.split("?")[0] if raw_img else ""

            if url_key in seen_urls:
                continue
            if dedup_name and dedup_name in seen_names_dedup:
                continue
            if img_base and img_base in seen_images:
                continue

            seen_urls.add(url_key)
            if dedup_name:
                seen_names_dedup.add(dedup_name)
            if img_base:
                seen_images.add(img_base)

            # Filtre terme structurel avec aliases
            # Ex: pièce "trapèze" → accepte "trapeze" ET "evase" ET "patineuse"
            if _required:
                _name_norm = self._strip_accents((raw_name or "").lower())
                _passed = False
                for req_term in _required:
                    # Récupérer tous les alias acceptables pour ce terme
                    acceptable = self._STRUCTURAL_TERM_ALIASES.get(
                        req_term, [req_term]
                    )
                    if any(alias in _name_norm for alias in acceptable):
                        _passed = True
                        break
                if not _passed:
                    continue
 
 
            # Blacklist
            product_name_lower  = raw_name.lower()
            secondary_cat_lower = (c.get("secondary_category") or "").lower()
            combined_text = product_name_lower + " " + secondary_cat_lower
            if any(bk in combined_text for bk in self.PRODUCT_BLACKLIST_KEYWORDS):
                continue

            # Filtre couleurs incompatibles avec la colorimétrie cliente
            if colors_to_avoid:
                name_norm = self._strip_accents(raw_name.lower())
                if any(self._strip_accents(col.lower()) in name_norm for col in colors_to_avoid if col):
                    print(f"   🚫 Couleur exclue: '{raw_name[:60]}'")
                    continue
 
            # Bonus couleurs favorites : on les place en tête via un flag
            _color_preferred = False
            if colors_best:
                name_norm_cb = self._strip_accents(raw_name.lower())
                _color_preferred = any(
                    self._strip_accents(col.lower()) in name_norm_cb
                    for col in colors_best if col
                )
 

            # Couleurs favorites en priorité absolue
            if _color_preferred:
                out.insert(0, c)
            else:
                out.append(c)
            if len(out) >= n:
                break

        return out[:n]

    # -------------------------
    # Text helpers
    # -------------------------
    def _strip_accents(self, s: str) -> str:
        s = s or ""
        s = s.replace("œ", "oe").replace("Œ", "OE").replace("æ", "ae").replace("Æ", "AE")
        return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

    def _normalize_kw_for_ilike(self, kw: str) -> str:
        kw = (kw or "").strip().lower()
        if not kw:
            return ""
        kw = self._strip_accents(kw)
        # Convertit les tirets en espaces (ex: "col-v" → "col v" pour l'ILIKE)
        kw = kw.replace("-", " ")
        kw = re.sub(r"[^a-z0-9\s]", " ", kw)
        kw = re.sub(r"\s{2,}", " ", kw).strip()
        parts = kw.split()[:2]
        kw = " ".join(parts)
        if len(kw) > self.MAX_TOKEN_LEN:
            kw = kw[: self.MAX_TOKEN_LEN]
        return kw

    def _ilike_pattern(self, token: str) -> str:
        t = (token or "").strip()
        if not t:
            return ""
        t = t.replace("*", " ").strip()
        t = re.sub(r"\s{2,}", " ", t)
        return f"*{t}*"

    def _category_match(self, row: Dict[str, Any], category: str) -> bool:
        tokens = self.CATEGORY_TOKENS.get(category, [])
        if not tokens:
            return True
        sc = (row.get("secondary_category") or "").lower()
        pc = (row.get("primary_category") or "").lower()
        hay = f"{pc} {sc}"
        return any(t in hay for t in tokens)

    # -------------------------
    # Robust Supabase call (retry)
    # -------------------------
    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.6, min=0.6, max=3.0),
        retry=retry_if_exception_type(Exception),
    )
    def _execute(self, q):
        return q.execute()

    # -------------------------
    # Image cache (Supabase Storage)
    # -------------------------
    def _ensure_cached_public_image(self, image_url: str, affiliate_row: Dict[str, Any]) -> str:
        image_url = (image_url or "").strip()
        if image_url.endswith("?"):
            image_url = image_url[:-1]

        base_url = image_url.split("?", 1)[0]

        if not image_url:
            return ""

        if "supabase.co/storage/v1/object/public" in image_url:
            url = image_url.strip()
            return url[:-1] if url.endswith("?") else url

        try:
            product_id = str(affiliate_row.get("product_id") or "")
            name = str(affiliate_row.get("product_name") or "")
            key_seed = f"{product_id}|{name}|{base_url or image_url}"
            h = hashlib.sha256(key_seed.encode("utf-8")).hexdigest()[:24]

            ext = "jpg"
            low = (base_url or image_url).lower()
            if ".png" in low:
                ext = "png"
            elif ".webp" in low:
                ext = "webp"
            elif ".jpeg" in low:
                ext = "jpeg"

            object_path = f"pdt/{h}.{ext}"
            bucket = self.client.storage.from_(self.AFFILIATE_IMAGE_BUCKET)

            try:
                public = bucket.get_public_url(object_path)
                public_url = public.get("publicUrl") if isinstance(public, dict) else str(public or "")
                public_url = (public_url or "").strip()
                if public_url.endswith("?"):
                    public_url = public_url[:-1]
                if public_url:
                    r = httpx.get(
                        public_url,
                        headers={"Range": "bytes=0-0"},
                        timeout=self.HTTP_TIMEOUT,
                        follow_redirects=True,
                    )
                    if r.status_code in (200, 206):
                        return public_url
            except Exception:
                pass

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
                "Referer": "https://www.placedestendances.com/",
                "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
            }

            try_url = base_url or image_url
            r = httpx.get(try_url, headers=headers, timeout=6.0, follow_redirects=True)

            # 403 = IP bloquée par PDT → inutile de retenter
            if r.status_code == 403:
                print(f"⛔ 403 Forbidden — skip immédiat: {try_url[:80]}")
                return ""

            # Autre erreur → skip sans retry
            if r.status_code >= 400:
                print(f"⚠️ HTTP {r.status_code} — skip: {try_url[:80]}")
                return ""

            r.raise_for_status()

            content_type = (r.headers.get("content-type", "") or "").strip()
            data = r.content
            if not data or len(data) < 200:
                return ""

            bucket.upload(
                path=object_path,
                file=data,
                file_options={
                    "content-type": content_type or f"image/{ext}",
                    "upsert": "true",
                },
            )

            public = bucket.get_public_url(object_path)
            public_url = public.get("publicUrl") if isinstance(public, dict) else str(public or "")
            public_url = (public_url or "").strip()
            if public_url.endswith("?"):
                public_url = public_url[:-1]

            return public_url or ""

        except Exception as e:
            print(f"⚠️ Image cache failed: {e}")
            return ""

    # -------------------------
    # AFFILIATE MATCH
    # -------------------------
    def _base_query(self, select_fields: str):
        q = self.client.table(self.AFFILIATE_TABLE).select(select_fields)
        q = q.eq("is_deleted", False)
        if self.AFFILIATE_PRIMARY_CATEGORY:
            q = q.eq("primary_category", self.AFFILIATE_PRIMARY_CATEGORY)
        return q

    def _find_affiliate_products(
        self,
        piece_title: str,
        spec: str,
        category: str,
        limit: int = 20,
        style_tags: Optional[List[str]] = None,
        colors_to_avoid: Optional[List[str]] = None,
        colors_best: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
 
        """
        Recherche des produits affiliés en plusieurs phases par ordre de précision.

        PHASE 0  — Style-aware (inchangée)
        PHASE 1  — Mot-clé COMPOSÉ "pantalon palazzo" / "robe portefeuille" + filtre catégorie  ← NEW
        PHASE 1b — Mot-clé NOM SEUL "pantalon" + filtre catégorie (fallback si peu de résultats)
        PHASE 2  — Mot-clé composé SANS filtre catégorie
        PHASE 2b — Mot-clé nom seul SANS filtre catégorie
        PHASE 3  — Fallback catégorie (secondary_category)

        RE-SCORING FINAL : remonte les candidats contenant le plus de mots-clés  ← NEW
        """
        kws = self._extract_keywords(piece_title, spec)
        print(f"🔑 KWS pour '{piece_title}': {kws}")   # ← à ajouter, à retirer une fois le diagnostic fait


        select_fields = ",".join([
            "product_id", "product_name", "brand", "primary_category",
            "secondary_category", "product_url", "image_url", "buy_url",
            "price", "sale_price", "currency", "availability",
            "is_deleted", "last_seen_at",
        ])

        collected: List[Dict[str, Any]] = []
        seen = set()

        def _add_rows(rows: List[Dict[str, Any]]) -> None:
            nonlocal collected, seen
            for row in rows or []:
                key = (row.get("buy_url") or "").strip() or str(row.get("product_id") or "").strip()
                if not key:
                    key = hashlib.sha256((row.get("image_url") or "").encode("utf-8")).hexdigest()[:12]
                if key in seen:
                    continue
                # Exclusion couleurs interdites dès la collecte
                if colors_to_avoid:
                    name_norm = self._strip_accents((row.get("product_name") or "").lower())
                    if any(self._strip_accents(col.lower()) in name_norm for col in colors_to_avoid if col):
                        continue
                seen.add(key)
                collected.append(row)
                if len(collected) >= limit:
                    return
 
        # ────────────────────────────────────────────────────────
        # PHASE 0 — Style-aware via affiliate_product_enrichment
        # ────────────────────────────────────────────────────────
        if style_tags:
            phase0 = self._find_affiliate_products_phase0_style(
                piece_title=piece_title,
                style_tags=style_tags,
                category=category,
                limit=10,
            )
            _add_rows(phase0)

        # ────────────────────────────────────────────────────────
        # PHASE 1 — Mot-clé COMPOSÉ (nom + coupe) + filtre catégorie  ← NEW
        # Ex: "pantalon palazzo", "robe portefeuille", "jupe trapeze"
        # ────────────────────────────────────────────────────────
        if kws and len(collected) < limit:
            # kws est trié [nouns, cuts, colors, rest]
            # On compose le premier nom + le premier qualificatif de coupe
            compound_kw = " ".join(kws[:2]) if len(kws) >= 2 else kws[0]
            compound_safe = self._normalize_kw_for_ilike(compound_kw)

            if len(compound_safe) >= 5:  # ex: "robe" seul = 4 chars → skip, traité en 1b
                try:
                    pattern = self._ilike_pattern(compound_safe)
                    q = self._base_query(select_fields).ilike("product_name", pattern).limit(40)
                    resp = self._execute(q)
                    data = getattr(resp, "data", None) or []
                    filtered = [r for r in data if self._category_match(r, category)]
                    _add_rows(filtered)
                    if filtered:
                        print(f"✅ COMPOUND+CAT [{category}] '{compound_safe}': {len(filtered)}")
                    elif data:
                        # Produits trouvés mais pas dans la bonne catégorie → on les ajoute quand même
                        _add_rows(data)
                        print(f"✅ COMPOUND (no-cat) [{category}] '{compound_safe}': {len(data)}")
                except Exception as e:
                    print(f"⚠️ COMPOUND+CAT query failed: {e}")

        # ────────────────────────────────────────────────────────
        # PHASE 1b — Mot-clé NOM SEUL + filtre catégorie (fallback)
        # ────────────────────────────────────────────────────────
        if len(collected) < 6:
            for kw in kws[:1]:
                if len(collected) >= limit:
                    break
                kw_safe = self._normalize_kw_for_ilike(kw)
                if len(kw_safe) < 3:
                    continue
                try:
                    pattern = self._ilike_pattern(kw_safe)
                    q = self._base_query(select_fields).ilike("product_name", pattern).limit(40)
                    resp = self._execute(q)
                    data = getattr(resp, "data", None) or []
                    filtered = [r for r in data if self._category_match(r, category)]
                    _add_rows(filtered)
                    if filtered:
                        print(f"✅ KW+CAT [{category}] '{kw_safe}': {len(filtered)}")
                except Exception as e:
                    print(f"⚠️ KW+CAT query failed: {e}")

        # ────────────────────────────────────────────────────────
        # PHASE 2 — Mot-clé composé SANS filtre catégorie
        # ────────────────────────────────────────────────────────
        if len(collected) < 6 and kws:
            compound_kw = " ".join(kws[:2]) if len(kws) >= 2 else kws[0]
            compound_safe = self._normalize_kw_for_ilike(compound_kw)
            if len(compound_safe) >= 5:
                try:
                    pattern = self._ilike_pattern(compound_safe)
                    q = self._base_query(select_fields).ilike("product_name", pattern).limit(40)
                    resp = self._execute(q)
                    data = getattr(resp, "data", None) or []
                    _add_rows(data)
                    if data:
                        print(f"✅ COMPOUND [{category}] '{compound_safe}': {len(data)}")
                except Exception as e:
                    print(f"⚠️ COMPOUND query failed: {e}")

        # ────────────────────────────────────────────────────────
        # PHASE 2b — Mot-clé nom seul SANS filtre catégorie
        # ────────────────────────────────────────────────────────
        if len(collected) < 6:
            for kw in kws[:1]:
                if len(collected) >= limit:
                    break
                kw_safe = self._normalize_kw_for_ilike(kw)
                if len(kw_safe) < 3:
                    continue
                try:
                    pattern = self._ilike_pattern(kw_safe)
                    q = self._base_query(select_fields).ilike("product_name", pattern).limit(40)
                    resp = self._execute(q)
                    data = getattr(resp, "data", None) or []
                    _add_rows(data)
                    if data:
                        print(f"✅ KW [{category}] '{kw_safe}': {len(data)}")
                except Exception as e:
                    print(f"⚠️ KW query failed: {e}")

        # ────────────────────────────────────────────────────────
        # PHASE 3 — Fallback catégorie (secondary_category)
        # ────────────────────────────────────────────────────────
        def _ordered(q):
            try:
                return q.order("last_seen_at", desc=True)
            except Exception:
                return q

        if len(collected) < 10:
            for token in (self.CATEGORY_TOKENS.get(category, []) or [])[:1]:
                if len(collected) >= limit:
                    break
                t = self._normalize_kw_for_ilike(token)
                if len(t) < 3:
                    continue
                try:
                    pattern = self._ilike_pattern(t)
                    q = _ordered(self._base_query(select_fields)).ilike("secondary_category", pattern).limit(40)
                    resp = self._execute(q)
                    data = getattr(resp, "data", None) or []
                    _add_rows(data)
                    if data:
                        print(f"✅ CAT secondary [{category}] '{t}': {len(data)}")
                except Exception as e:
                    print(f"⚠️ CAT secondary query failed: {e}")

        print(f"📊 Total [{category}]: {len(collected)} produits collectés avant re-scoring")

        # ────────────────────────────────────────────────────────
        # RE-SCORING FINAL — remonte les meilleurs matches  ← NEW
        # Ex: "pantalon palazzo" score 3 > "pantalon slim" score 1
        # ────────────────────────────────────────────────────────
        rescored = self._rescore_collected(collected, kws, colors_best=colors_best)

 
        return rescored[:limit]

    def _extract_keywords(self, piece_title: str, spec: str) -> List[str]:
        # Noms de pièces — PRIORITÉ ABSOLUE
        TYPE_NOUNS = {
            "manteau", "veste", "blazer", "blouson", "trench", "cardigan", "kimono",
            "chemise", "blouse", "top", "pull", "tunique", "sweat", "body",
            "pantalon", "jean", "jupe", "short", "legging",
            "robe", "combinaison", "jumpsuit",
            "escarpins", "bottes", "sandales", "mocassins", "sneakers", "mules",
            "sac", "collier", "boucles", "bracelet", "foulard", "ceinture",
        }
        # Mots de couleur
        COLOR_TOKENS = {
            "blanc", "blanche", "noir", "noire", "bordeaux", "rouge", "beige",
            "camel", "ocre", "olive", "terracotta", "marine", "bleu", "bleue",
            "vert", "verte", "kaki", "moutarde", "rouille", "aubergine", "caramel",
            "ivoire", "ecru", "crème", "gris", "marron", "rose", "corail", "orange",
        }
        # Mots de coupe (adjectifs) — enrichis
        CUT_TOKENS = {
            "empire", "portefeuille", "trapèze", "trapeze", "droit", "droite",
            "palazzo", "évasé", "evasée", "cintré", "cintrée", "oversize", "fluide",
            "ajusté", "ajustée", "structuré", "structurée", "ceinturé", "ceinturée",
            "long", "longue", "midi", "mini", "court", "courte", "col", "encolure",
            "croisé", "croisée", "large", "flare", "wide", "slim", "skinny",
            "taille haute", "tailleur", "wrap",
        }

        text = f"{piece_title} {spec}".lower()
        text = re.sub(r"[^a-zàâçéèêëîïôûùüÿñæœ0-9\s-]", " ", text)
        text = re.sub(r"\s{2,}", " ", text).strip()

        stop = {
            "a", "à", "au", "aux", "de", "des", "du", "en", "et", "ou",
            "un", "une", "avec", "pour", "la", "le", "les", "d", "l",
            "sur", "dans", "sans", "style",
            "matiere", "matières", "coton", "laine", "viscose", "soie", "bio",
        }

        # ── Détection des composés spéciaux AVANT le split ──────────────────
        # "col v", "col u" etc. doivent être préservés comme un seul token de coupe,
        # car "v" et "u" seraient sinon filtrés (len < 3).
        COMPOUND_CUTS = [
            ("col v",        "col-v"),
            ("col u",        "col-u"),
            ("col bateau",   "col-bateau"),
            ("col rond",     "col-rond"),
            ("col carré",    "col-carre"),
            ("col carre",    "col-carre"),
            ("taille haute", "taille-haute"),
        ]

        def _preprocess_compounds(src: str) -> str:
            # Gère "col en V", "col en U", "encolure en V" etc. (avec "en" intercalé)
            src = re.sub(r"\b(col|encolure)\s+en\s+([a-z])\b", r"\1-\2", src)
            for phrase, replacement in COMPOUND_CUTS:
                src = src.replace(phrase, replacement)
            return src

        # Ajoute les composés normalisés aux CUT_TOKENS pour qu'ils soient reconnus
        CUT_TOKENS.update({
            "col-v", "col-u", "col-bateau", "col-rond", "col-carre", "taille-haute",
        })

        base = []
        for src in [piece_title.lower(), spec.lower()]:
            src = re.sub(r"[^a-zàâçéèêëîïôûùüÿñæœ0-9\s-]", " ", src)
            src = re.sub(r"\s{2,}", " ", src).strip()
            src = _preprocess_compounds(src)  # fusionne "col v" → "col-v"
            for t in src.split():
                if t in stop or (len(t) < 3 and "-" not in t):
                    continue
                if t not in base:
                    base.append(t)

        nouns  = [t for t in base if t in TYPE_NOUNS]
        colors = [t for t in base if t in COLOR_TOKENS and t not in nouns]
        cuts   = [t for t in base if t in CUT_TOKENS and t not in nouns and t not in colors]
        rest   = [t for t in base if t not in TYPE_NOUNS and t not in COLOR_TOKENS and t not in CUT_TOKENS]

        # Priorité : nom de pièce > coupe > couleur > reste
        ordered = nouns + cuts + colors + rest

        seen = set()
        final = []
        for x in ordered:
            k = x.strip().lower()
            if k and k not in seen:
                seen.add(k)
                final.append(k)

        # ── Normalisation aliases GPT → Rakuten ──────────────────────────────
        # Traduit les termes générés par GPT vers la nomenclature réelle Rakuten.
        # Ex: "col u" → "col rond", "a-line" → "evase", "wrap" → "portefeuille"
        normalized_final = []
        for kw in final:
            alias = self._GPT_TO_RAKUTEN_KW.get(kw.lower())
            normalized_final.append(alias if alias else kw)
        final = normalized_final

        return final[:8]


product_matcher_service = ProductMatcherService()