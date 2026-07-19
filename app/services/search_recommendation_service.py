import re
import uuid
import unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse, urlunparse

from app.utils.supabase_client import supabase


class SearchRecommendationService:
    """
    Génère des recommandations affiliées pour une recherche utilisateur.

    v4 (SQL-first) :
    - search_products_v2 (fonction PostgreSQL) remplace les 2 requêtes + fusion Python
    - Filtres stricts en SQL : style, prix, couleurs saison/profil, coupes hard_exclude
    - ORDER BY random() côté SQL → diversité garantie à chaque appel
    - score morphologique via silhouette_cut_rules (Python, chargé une fois par requête)
    """

    ALGORITHM_VERSION = "search_reco_v4_sql"

    MVP_CATEGORY_TO_SOURCE_SECONDARY = {
        "hauts": {
            "Vêtements~~Top & Blouse",
            "Vêtements~~Chemise",
            "Vêtements~~Pull",
            "Vêtements~~Tee-Shirt",
            "Vêtements~~Gilet",
            "Clothing~~Shirts & Tops",
        },
        "bas": {
            "Vêtements~~Pantalon",
            "Vêtements~~Jean",
            "Vêtements~~Jupe",
            "Clothing~~Pants",
            "Clothing~~Skirts",
        },
        "robes": {
            "Vêtements~~Robe",
            "Clothing~~Dresses",
            "Vêtements~~Combinaison",
        },
        "vestes": {
            "Vêtements~~Veste & Blouson",
            "Vêtements~~Manteau",
            "Clothing~~Outerwear~~Coats & Jackets",
        },
        "chaussures": {
            "Chaussures~~Baskets",
            "Footwear~~Sneakers",
            "Chaussures~~Boots & Bottines",
            "Chaussures~~Bottes",
            "Chaussures~~Sandales",
            "Chaussures~~Escarpins",
            "Chaussures~~Mocassins",
            "Chaussures~~Derbies",
            "Chaussures~~Ballerines",
        },
        "sacs": {
            "Accessoires~~Sacs",
            "Maroquinerie~~Sacs",
        },
    }

    CATEGORY_KEY_NORMALIZATION = {
        "tenue_complete": "tenue_complete",
        "hauts": "hauts", "haut": "hauts",
        "bas": "bas",
        "robes": "robes", "robe": "robes",
        "chaussures": "chaussures", "chaussure": "chaussures",
        "vestes": "vestes", "vestes_manteaux": "vestes", "vestes_et_manteaux": "vestes",
        "vestes_&_manteaux": "vestes", "veste": "vestes", "manteaux": "vestes", "manteau": "vestes",
        "accessoires": None, "sacs": "sacs", "bijoux": None,
        "sous-vetements": None, "sous_vetements": None, "lingerie": None,
        "maillots_bain": None, "maillots_de_bain": None,
        "tenue_sport": None, "vetements_sport": None, "vetements_de_sport": None,
    }

    CATEGORY_LABELS = {
        "hauts": "Hauts", "bas": "Bas", "robes": "Robes",
        "vestes": "Vestes", "chaussures": "Chaussures",
        "sacs": "Sacs",
    }

    # Mapping category_key → product_family pour les règles de coupe
    CATEGORY_TO_PRODUCT_FAMILY = {
        "hauts": "top", "bas": "bottom", "robes": "dress",
        "vestes": "outerwear", "chaussures": "shoe","sacs": "bag",
    }

    COLOR_WORDS = [
        "noir", "blanc", "bleu", "rose", "rouge", "vert", "jaune",
        "orange", "marron", "beige", "gris", "violet", "prune",
        "camel", "kaki", "bordeaux", "multicolore", "marine",
        "argent", "argente", "doré", "dore", "écru", "ecru",
    ]

    NEUTRAL_COLORS = {
        "noir", "blanc", "ecru", "beige", "camel", "gris", "marine", "marron"
    }

    CATEGORY_SUBTYPE_HINTS = {
        "hauts": {
            "chemise": ["chemise"], "blouse": ["blouse"],
            "pull": ["pull", "maille"], "gilet": ["gilet", "cardigan"],
            "tee_shirt": ["tee-shirt", "tee shirt", "t-shirt", "t shirt"],
            "top": ["top"],
            "caraco": ["caraco", "camisole", "bretelles fines", "debardeur", "débardeur"],
        },
        "bas": {
            "pantalon": ["pantalon", "tailleur"], "jean": ["jean", "denim"],
            "jupe": ["jupe"], "short": ["short", "bermuda"],
        },
        "robes": {"robe": ["robe"], "combinaison": ["combinaison", "jumpsuit"]},
        "vestes": {
            "blazer": ["blazer", "tailleur"], "veste": ["veste", "blouson"],
            "manteau": ["manteau", "trench"],
            "doudoune": ["doudoune", "matelassee", "matelassée", "puffer"],
            "sans_manches": ["sans manches"],
        },
        "chaussures": {
            "baskets": ["basket", "sneaker", "running"],
            "boots": ["boots", "bottine", "bottes"], "sandales": ["sandale"],
            "escarpins": ["escarpin", "heel", "heels"],
            "mocassins": ["mocassin", "loafer"], "derbies": ["derby"],
            "ballerines": ["ballerine"],
        },
        "sacs": {
            "sac_a_dos": ["sac a dos", "backpack"],
            "sac_banane": ["banane"],
            "sac_seau": ["seau", "hobo"],
            "cabas": ["cabas", "tote", "shopping"],
            "pochette": ["pochette", "trotteur", "mini pochette"],
            "sac_bandouliere": ["bandouliere", "porte epaule", "epaule"],
            "sac_a_main": ["sac a main"],
        },
    }

    STYLE_COMPATIBILITY_MATRIX = {
        "chic": {"chic": 38, "classique": 28, "minimaliste": 20, "moderne": 14, "romantique": 8, "vintage": 4, "rock": -4, "boheme": -10, "casual": -14, "sportswear": -24},
        "classique": {"classique": 36, "chic": 24, "minimaliste": 18, "moderne": 10, "casual": 4, "vintage": 4, "romantique": 2, "rock": -8, "boheme": -10, "sportswear": -18},
        "casual": {"casual": 34, "sportswear": 16, "classique": 8, "minimaliste": 6, "moderne": 6, "rock": 4, "boheme": 2, "romantique": 0, "vintage": 0, "chic": -6},
        "sportswear": {"sportswear": 36, "casual": 16, "moderne": 8, "rock": 4, "classique": -8, "chic": -14, "boheme": -12, "romantique": -14, "minimaliste": -2, "vintage": -4},
        "boheme": {"boheme": 34, "romantique": 18, "vintage": 10, "chic": 4, "casual": 2, "classique": -4, "minimaliste": -8, "moderne": -8, "rock": -6, "sportswear": -16},
        "romantique": {"romantique": 34, "boheme": 16, "chic": 10, "classique": 8, "vintage": 6, "minimaliste": -2, "casual": -4, "moderne": -4, "rock": -12, "sportswear": -16},
        "rock": {"rock": 34, "moderne": 12, "casual": 8, "chic": 2, "sportswear": 2, "classique": -6, "boheme": -8, "romantique": -10, "minimaliste": 0, "vintage": 4},
        "minimaliste": {"minimaliste": 34, "classique": 22, "chic": 18, "moderne": 16, "casual": 6, "romantique": -2, "boheme": -10, "rock": -4, "sportswear": -8, "vintage": -4},
        "moderne": {"moderne": 34, "minimaliste": 18, "chic": 12, "classique": 10, "rock": 8, "casual": 6, "sportswear": 2, "boheme": -8, "romantique": -6, "vintage": 2},
        "vintage": {"vintage": 34, "romantique": 12, "boheme": 10, "classique": 6, "rock": 4, "chic": 2, "casual": 2, "minimaliste": -6, "moderne": -4, "sportswear": -10},
    }

    OCCASION_STYLE_BOOSTS = {
        "bureau": {"classique": 14, "chic": 14, "minimaliste": 8, "moderne": 4, "casual": -8, "sportswear": -18, "boheme": -8},
        "travail": {"classique": 14, "chic": 14, "minimaliste": 8, "moderne": 4, "casual": -8, "sportswear": -18, "boheme": -8},
        "pro": {"classique": 12, "chic": 12, "minimaliste": 8, "sportswear": -18, "casual": -6},
        "soirée": {"chic": 14, "rock": 8, "romantique": 8, "classique": 4},
        "weekend": {"casual": 10, "sportswear": 8, "boheme": 6, "chic": -4},
    }

    CATEGORY_STYLE_RULES = {
        "chic": {
            "hauts": {"chemise": 10, "blouse": 10, "top": 6, "tee_shirt": -16},
            "bas": {"pantalon": 12, "jupe": 10, "jean": -18},
            "robes": {"robe": 10, "combinaison": 10},
            "vestes": {"blazer": 14, "manteau": 10, "veste": 6},
            "chaussures": {"escarpins": 14, "mocassins": 10, "derbies": 8, "ballerines": 6, "boots": 4, "baskets": -18},
        },
        "classique": {
            "hauts": {"chemise": 12, "blouse": 8, "pull": 6, "gilet": 6, "tee_shirt": -10},
            "bas": {"pantalon": 12, "jupe": 8, "jean": -12},
            "robes": {"robe": 10, "combinaison": 8},
            "vestes": {"blazer": 10, "manteau": 10, "veste": 6},
            "chaussures": {"mocassins": 12, "derbies": 10, "escarpins": 8, "ballerines": 6, "baskets": -12},
        },
        "casual": {
            "hauts": {"tee_shirt": 10, "pull": 8, "gilet": 6, "chemise": 2},
            "bas": {"jean": 12, "pantalon": 6, "jupe": 2},
            "chaussures": {"baskets": 12, "boots": 6, "sandales": 4, "escarpins": -8},
        },
    }

    SEASON_HINTS = {
        "hiver": {"positive": {"laine", "maille", "cachemire", "manteau", "doudoune", "boots", "bottes", "velours", "tweed"}, "negative": {"sandale", "maillot", "lin", "crochet"}},
        "ete": {"positive": {"sandale", "lin", "crochet", "robe", "blouse", "top", "combinaison"}, "negative": {"laine", "cachemire", "doudoune", "manteau", "boots"}},
        "printemps": {"positive": {"blouse", "chemise", "veste", "blazer", "jupe", "pantalon", "mocassin", "ballerine"}, "negative": {"doudoune", "maillot"}},
        "automne": {"positive": {"maille", "pull", "gilet", "veste", "bottine", "boots", "manteau"}, "negative": {"maillot"}},
    }

    OFFICE_NEGATIVE_HINTS = {
        "sequins": ["sequin", "sequins", "paillette", "paillete", "paillettes", "strass", "lamé", "lame"],
        "too_playful_print": ["fleuri", "floral", "imprime", "imprimé", "graphic", "graphique", "carreaux", "check"],
        "too_evening": ["satin", "dos nu", "bustier", "taffetas", "brillant", "brillance"],
        "too_casual_outerwear": ["doudoune", "matelassee", "matelassée", "capuche", "sherpa"],
        "too_loose": ["oversize", "ample", "large"],
        "too_casual_bottoms": ["jean", "denim", "cargo", "jogger", "legging"],
        "too_bold_bottoms": ["cuir", "simili", "vinyle", "croco", "brode", "brodé", "dentelle", "tulle", "filet", "délavé", "delave", "washed", "jacquard", "python"],
    }

    OFFICE_POSITIVE_HINTS = {
        "structured": ["droit", "droite", "tailleur", "structure", "structuré", "structuree"],
        "smart_tops": ["chemise", "blouse", "col bateau", "maille fine"],
        "smart_bottoms": ["pantalon", "jupe midi", "jupe", "taille haute", "cigarette", "droit", "plis"],
        "smart_outerwear": ["blazer", "trench", "manteau"],
        "smart_shoes": ["mocassin", "escarpin", "derby", "ballerine"],
    }

    def __init__(self):
        self.supabase = supabase
        self.client = supabase.get_client()

    # =========================
    # Public API
    # =========================
    async def generate_for_search(self, search_id: str) -> Dict[str, Any]:
        run_id: Optional[str] = None

        try:
            search_row = self._get_search(search_id)
            if not search_row:
                raise ValueError(f"Recherche introuvable: {search_id}")

            user_id = search_row["user_id"]
            ai_profile = self._get_ai_profile(user_id)
            if not ai_profile:
                raise ValueError(f"user_ai_profiles introuvable pour user_id={user_id}")

            selected_article_types = search_row.get("selected_article_types") or []
            if not selected_article_types:
                raise ValueError("La recherche ne contient aucun type d'article sélectionné")

            normalized_article_types = [
                self._normalize_text(x).replace(" ", "_")
                for x in selected_article_types if x
            ]

            if normalized_article_types == ["tenue_complete"]:
                selected_article_types = ["hauts", "bas", "robes", "vestes", "chaussures"]
            else:
                selected_article_types = [
                    x for x in selected_article_types
                    if self._normalize_text(x).replace(" ", "_") != "tenue_complete"
                ]

            normalized_categories = []
            for raw_category in selected_article_types:
                category_key = self._normalize_category_key(raw_category)
                if category_key and category_key not in normalized_categories:
                    normalized_categories.append(category_key)

            if not normalized_categories:
                raise ValueError("Aucune catégorie MVP exploitable dans la recherche")

            weights_json = {
                "style_v6_primary": 38, "style_v6_tags": 16, "style_v6_confidence": 10,
                "category_specificity": 14, "budget": 20,
                "color_best": 24, "color_ok": 10, "color_avoid": "exclusion_sql",
                "brand_preferred": 12, "morphology_cut_rules": 12,
                "occasion_context": 12, "season_context": 8,
            }

            filters_json = {
                "selected_seasons": search_row.get("selected_seasons") or [],
                "selected_styles": search_row.get("selected_styles") or [],
                "selected_occasions": search_row.get("selected_occasions") or [],
                "selected_article_types": normalized_categories,
                "selected_budgets": search_row.get("selected_budgets") or {},
                "classifier_version": "style_v6",
                "scope": "mvp_femme_sql_v4",
            }

            run_id = self._create_run(
                user_search_id=search_id,
                status="running",
                algorithm_version=self.ALGORITHM_VERSION,
                weights_json=weights_json,
                filters_json=filters_json,
            )

            all_inserted = 0
            inserted_product_keys: Set[str] = set()
            inserted_family_keys: Set[str] = set()
            inserted_url_keys: Set[str] = set()

            # ── Charger les règles morpho UNE FOIS pour cette cliente ──
            silhouette = (ai_profile.get("silhouette_type") or "").upper()
            cut_rules = self._get_cut_rules_for_silhouette(silhouette)
            selected_styles = search_row.get("selected_styles") or []

            for category_key in normalized_categories:

                # Budget calculé AVANT le fetch (passé à la fonction SQL)
                budget = self._extract_budget_for_category(
                    category_key=category_key,
                    budgets=search_row.get("selected_budgets") or {},
                )

                candidates = self._fetch_candidates_for_category(
                    category_key=category_key,
                    user_id=user_id,
                    selected_styles=selected_styles,
                    price_max=budget,
                    limit=400,
                )

                scored: List[Dict[str, Any]] = []
                for row in candidates:
                    scored_row = self._score_product(
                        product=row,
                        category_key=category_key,
                        search_row=search_row,
                        ai_profile=ai_profile,
                        budget=budget,
                        cut_rules=cut_rules,
                    )
                    if scored_row is not None:
                        scored.append(scored_row)

                scored.sort(
                    key=lambda x: (
                        -(x["score_total"] or 0),
                        x.get("price") if x.get("price") is not None else 10**9,
                        x.get("title") or "",
                    )
                )

                top_rows = scored[:20]
                inserted = self._insert_recommendations(
                    run_id=run_id,
                    category_key=category_key,
                    scored_rows=top_rows,
                    inserted_product_keys=inserted_product_keys,
                    inserted_family_keys=inserted_family_keys,
                    inserted_url_keys=inserted_url_keys,
                )
                all_inserted += inserted

            self._update_run(run_id=run_id, status="success", error_message=None)

            return {
                "status": "success",
                "run_id": run_id,
                "recommendations_inserted": all_inserted,
            }

        except Exception as e:
            if run_id:
                try:
                    self._update_run(run_id=run_id, status="failed", error_message=str(e)[:1000])
                except Exception:
                    pass
            return {"status": "error", "error": str(e), "run_id": run_id}

    # =========================
    # Morpho helpers (nouveaux v4)
    # =========================
    def _get_cut_rules_for_silhouette(self, silhouette: str) -> List[Dict[str, Any]]:
        """
        Récupère les règles boost/penalty de coupe pour la silhouette.
        Appelé UNE FOIS par generate_for_search (pas par produit).
        """
        if not silhouette:
            return []
        try:
            resp = (
                self.client.table("silhouette_cut_rules")
                .select("keyword,weight,product_family,action")
                .eq("silhouette", silhouette.upper())
                .in_("action", ["boost", "penalty"])
                .execute()
            )
            return resp.data or []
        except Exception as e:
            print(f"⚠️ _get_cut_rules_for_silhouette failed: {e}")
            return []

    def _compute_cut_score_from_text(
        self,
        search_text_normalized: str,
        cut_rules: List[Dict[str, Any]],
        product_family: str = "all",
    ) -> float:
        """
        Score morphologique via keywords contre search_text_normalized.
        Rapide : pure Python string ops, pas de requête DB supplémentaire.
        """
        if not search_text_normalized or not cut_rules:
            return 0.0
        score = 0.0
        for rule in cut_rules:
            if rule.get("product_family") in ("all", product_family):
                kw = (rule.get("keyword") or "").lower()
                if kw and kw in search_text_normalized:
                    score += rule.get("weight", 0)
        return score

    # =========================
    # Data fetch (v4 : RPC → search_products_v2)
    # =========================
    def _get_search(self, search_id: str) -> Optional[Dict[str, Any]]:
        response = self.supabase.query("user_searches", select_fields="*", filters={"id": search_id})
        return response.data[0] if response.data else None

    def _get_ai_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        response = self.supabase.query("user_ai_profiles", select_fields="*", filters={"user_id": user_id})
        return response.data[0] if response.data else None

    def _fetch_candidates_for_category(
        self,
        category_key: str,
        user_id: str,
        selected_styles: List[str],
        price_max: Optional[float],
        limit: int = 400,
    ) -> List[Dict[str, Any]]:
        """
        v4 — Appelle search_products_v2 (fonction PostgreSQL).
        Filtres stricts en SQL : style, prix, couleurs, coupes hard_exclude.
        ORDER BY random() côté SQL → diversité garantie.
        """
        allowed_secondaries = list(self.MVP_CATEGORY_TO_SOURCE_SECONDARY.get(category_key, set()))
        if not allowed_secondaries:
            return []

        style_tags = [self._normalize_text(s) for s in (selected_styles or []) if s]

        try:
            resp = self.client.rpc(
                "search_products_v2",
                {
                    "p_user_id":              user_id,
                    "p_style_tags":           style_tags if style_tags else None,
                    "p_secondary_categories": allowed_secondaries,
                    "p_price_max":            price_max,
                    "p_sample_size":          limit,
                },
            ).execute()

            rows = resp.data or []
            print(
                f"🔍 search_products_v2 [{category_key}] "
                f"styles={style_tags} prix_max={price_max} → {len(rows)} candidats"
            )
            return rows

        except Exception as e:
            print(f"⚠️ search_products_v2 failed pour {category_key}: {e}")
            return self._fetch_candidates_legacy(category_key=category_key, limit=min(limit, 120))

    def _fetch_candidates_legacy(self, category_key: str, limit: int = 120) -> List[Dict[str, Any]]:
        """Fallback sans filtres SQL avancés."""
        allowed_secondaries = list(self.MVP_CATEGORY_TO_SOURCE_SECONDARY.get(category_key, set()))
        if not allowed_secondaries:
            return []
        collected: List[Dict[str, Any]] = []
        seen: Set[str] = set()
        for secondary in allowed_secondaries:
            try:
                resp = (
                    self.client.table("affiliate_product_enrichment")
                    .select(
                        "merchant_id,product_id,style_primary,style_tags,style_scores_json,"
                        "confidence_score,source_description,source_secondary_category"
                    )
                    .eq("classifier_version", "style_v6")
                    .eq("source_secondary_category", secondary)
                    .limit(min(60, limit))
                    .execute()
                )
                for row in (resp.data or []):
                    key = f"{row.get('merchant_id')}::{row.get('product_id')}"
                    if key not in seen:
                        seen.add(key)
                        collected.append(row)
                    if len(collected) >= limit:
                        return collected
            except Exception as ex:
                print(f"⚠️ Legacy fetch {secondary}: {ex}")
        return collected

    # =========================
    # Run management
    # =========================
    def _create_run(self, user_search_id, status, algorithm_version, weights_json, filters_json) -> str:
        run_id = str(uuid.uuid4())
        payload = {
            "id": run_id,
            "user_search_id": user_search_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "algorithm_version": algorithm_version,
            "weights_json": weights_json,
            "filters_json": filters_json,
            "error_message": None,
        }
        self.supabase.insert_table("user_search_runs", payload)
        return run_id

    def _update_run(self, run_id: str, status: str, error_message: Optional[str]) -> None:
        payload = {"status": status, "error_message": error_message}
        response = self.client.table("user_search_runs").update(payload).eq("id", run_id).execute()
        if not response or response.data is None:
            raise Exception(f"Impossible de mettre à jour user_search_runs pour run_id={run_id}")

    # =========================
    # Recommendation insert
    # =========================
    def _insert_recommendations(
        self,
        run_id: str,
        category_key: str,
        scored_rows: List[Dict[str, Any]],
        inserted_product_keys: Set[str],
        inserted_family_keys: Set[str],
        inserted_url_keys: Set[str],
    ) -> int:
        inserted = 0
        rank = 1

        for row in scored_rows:
            product_key = f"{row['merchant_id']}::{row['product_id']}"
            family_key = self._build_product_family_key(row)
            url_key = self._canonicalize_product_url(row.get("product_url") or row.get("buy_url") or "")

            if product_key in inserted_product_keys:
                continue
            if family_key in inserted_family_keys:
                continue
            if url_key and url_key in inserted_url_keys:
                continue

            payload = {
                "id": str(uuid.uuid4()),
                "run_id": run_id,
                "merchant_id": int(row["merchant_id"]),
                "product_id": str(row["product_id"]),
                "category_key": category_key,
                "rank": rank,
                "score_total": row["score_total"],
                "score_color": row["score_color"],
                "score_morphology": row["score_morphology"],
                "score_style": row["score_style"],
                "title": row["title"],
                "brand": row["brand"],
                "price": row["price"],
                "currency": row["currency"],
                "image_url": row["image_url"],
                "buy_url": row["buy_url"],
                "product_url": row["product_url"],
                "reasons_json": row["reasons_json"],
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

            self.supabase.insert_table("user_search_recommendations", payload)

            inserted_product_keys.add(product_key)
            inserted_family_keys.add(family_key)
            if url_key:
                inserted_url_keys.add(url_key)

            inserted += 1
            rank += 1

        return inserted

    # =========================
    # Scoring (v4)
    # =========================
    def _score_product(
        self,
        product: Dict[str, Any],
        category_key: str,
        search_row: Dict[str, Any],
        ai_profile: Dict[str, Any],
        budget: Optional[float],
        cut_rules: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[Dict[str, Any]]:
        title = (product.get("product_name") or "").strip()
        brand = (product.get("brand") or "").strip()
        secondary_category = (product.get("secondary_category") or "").strip()
        source_description = (product.get("source_description") or "").strip()
        style_primary = self._normalize_text(str(product.get("style_primary") or ""))
        # style_tags peut arriver sous l'alias style_tags_col (SQL) ou style_tags (legacy)
        style_tags = self._normalize_text_list(
            product.get("style_tags_col") or product.get("style_tags")
        )
        style_scores_json = product.get("style_scores_json") or {}
        confidence_score = self._safe_float(product.get("confidence_score")) or 0.0

        price = self._safe_float(product.get("sale_price")) or self._safe_float(product.get("price"))
        currency = self._normalize_currency(product.get("currency"))
        image_url = (product.get("image_url") or "").strip()
        buy_url = (product.get("buy_url") or "").strip()
        product_url = (product.get("product_url") or "").strip()
        merchant_id = product.get("merchant_id")
        product_id = product.get("product_id")

        if not merchant_id or not product_id or not title:
            return None

        subtype = self._infer_subtype(category_key, title, secondary_category)

        # ── COULEUR : color_match pré-calculé par SQL ─────────────────────
        # Les couleurs avoid ont déjà été exclues côté SQL (is_excluded impossible ici)
        color_match_sql = (product.get("color_match") or "neutral").lower()
        if color_match_sql == "best":
            color_score, color_reason = 24, "Couleur best (filtrage SQL)"
        elif color_match_sql == "ok":
            color_score, color_reason = 10, "Couleur ok (filtrage SQL)"
        else:
            # Couleur neutre : +4 si connue, 0 sinon
            extracted_color = self._extract_color_from_title(title)
            if extracted_color and self._normalize_text(extracted_color) in self.NEUTRAL_COLORS:
                color_score, color_reason = 4, f"Couleur neutre: {extracted_color}"
            else:
                color_score, color_reason = 0, "Couleur neutre/non reconnue"

        # ── MORPHOLOGIE : score via silhouette_cut_rules ──────────────────
        product_family = self.CATEGORY_TO_PRODUCT_FAMILY.get(category_key, "all")
        stn = (product.get("search_text_normalized") or "").lower()
        morphology_score = self._compute_cut_score_from_text(stn, cut_rules or [], product_family)
        morphology_reason = f"Score coupe: {morphology_score}"

        style_score, style_reason = self._compute_style_score(
            style_primary=style_primary, style_tags=style_tags,
            style_scores_json=style_scores_json, confidence_score=confidence_score,
            category_key=category_key, subtype=subtype,
            search_row=search_row, ai_profile=ai_profile,
        )
        budget_score, budget_reason = self._compute_budget_score(price, budget)
        brand_score, brand_reason = self._compute_brand_score(brand, ai_profile)
        season_score, season_reason = self._compute_season_score(
            title=title, secondary_category=secondary_category,
            source_description=source_description, search_row=search_row,
        )
        category_specificity_score, category_specificity_reason = self._compute_category_specificity_score(
            category_key=category_key, subtype=subtype, search_row=search_row,
        )
        office_visual_score, office_visual_reason = self._compute_office_visual_penalty(
            category_key=category_key, title=title,
            secondary_category=secondary_category, source_description=source_description,
            search_row=search_row,
        )

        total_score = (
            10 + color_score + style_score + morphology_score + budget_score
            + brand_score + season_score + category_specificity_score + office_visual_score
        )

        reasons_json = {
            "style": style_reason, "category_specificity": category_specificity_reason,
            "season": season_reason, "color": color_reason, "morphology": morphology_reason,
            "budget": budget_reason, "brand": brand_reason,
            "style_primary": style_primary, "style_tags": style_tags,
            "confidence_score": confidence_score, "secondary_category": secondary_category,
            "subtype": subtype, "color_match_sql": color_match_sql,
            "office_visual": office_visual_reason,
        }

        return {
            "merchant_id": merchant_id, "product_id": product_id, "title": title, "brand": brand,
            "price": price, "currency": currency, "image_url": image_url, "buy_url": buy_url,
            "product_url": product_url,
            "score_total": round(max(total_score, 0), 2),
            "score_color": round(max(color_score, 0), 2),
            "score_morphology": round(max(morphology_score, 0), 2),
            "score_style": round(max(style_score, 0), 2),
            "reasons_json": reasons_json,
        }

    async def get_saved_recommendations_for_search(self, search_id: str) -> Dict[str, Any]:
        search_row = self._get_search(search_id)
        if not search_row:
            raise ValueError(f"user_searches introuvable: {search_id}")

        latest_run_response = (
            self.client.table("v_user_search_latest_run").select("*")
            .eq("search_id", search_id).limit(1).execute()
        )

        latest_runs = latest_run_response.data or []
        if not latest_runs:
            return {"ok": True, "found": False, "search_id": search_id, "recommendations_by_category": []}

        latest_run = latest_runs[0]
        run_id = latest_run.get("run_id") or latest_run.get("id")
        if not run_id:
            return {"ok": True, "found": False, "search_id": search_id, "recommendations_by_category": []}

        recommendations_response = (
            self.client.table("user_search_recommendations").select("*")
            .eq("run_id", run_id).order("category_key").order("rank").execute()
        )

        recommendation_rows = recommendations_response.data or []
        if not recommendation_rows:
            return {"ok": True, "found": False, "search_id": search_id, "run_id": run_id, "recommendations_by_category": []}

        recommendations_by_category = self._group_saved_recommendations(recommendation_rows)

        return {
            "ok": True, "found": True, "search_id": search_id, "run_id": run_id,
            "generated_at": latest_run.get("created_at"), "updated_at": latest_run.get("created_at"),
            "search": {
                "id": search_row.get("id"), "title": search_row.get("title"),
                "style": search_row.get("style"), "season": search_row.get("season"),
                "occasion": search_row.get("occasion"),
            },
            "recommendations_by_category": recommendations_by_category,
        }

    def _compute_style_score(
        self,
        style_primary: str, style_tags: List[str], style_scores_json: Dict[str, Any],
        confidence_score: float, category_key: str, subtype: str,
        search_row: Dict[str, Any], ai_profile: Dict[str, Any],
    ) -> Tuple[float, str]:
        requested_styles = [self._normalize_text(x) for x in (search_row.get("selected_styles") or []) if x]
        profile_styles = [self._normalize_text(x) for x in (ai_profile.get("style_keywords") or []) if x]
        occasions = [self._normalize_text(x) for x in (search_row.get("selected_occasions") or []) if x]

        target_styles: List[str] = []
        for style in requested_styles + profile_styles:
            if style and style not in target_styles:
                target_styles.append(style)

        if not target_styles:
            if style_primary:
                return round(min(max(confidence_score, 0.0), 1.0) * 6, 2), f"Style V6: {style_primary}"
            return 0, "Aucun style cible"

        score = 0.0
        reasons: List[str] = []

        for target_style in target_styles[:3]:
            compat = self.STYLE_COMPATIBILITY_MATRIX.get(target_style, {})
            base = compat.get(style_primary, 0)
            if base:
                score += base
                reasons.append(f"{target_style}→{style_primary}")
            if target_style in style_tags:
                score += 8
                reasons.append(f"tag:{target_style}")
            raw = self._safe_float(style_scores_json.get(target_style))
            if raw is not None:
                score += min(raw * 2.5, 10)

        occasion_delta = 0.0
        for occasion in occasions:
            mapping = self.OCCASION_STYLE_BOOSTS.get(occasion)
            if mapping:
                occasion_delta += mapping.get(style_primary, 0)
        if occasion_delta:
            score += occasion_delta
            reasons.append(f"occasion:{round(occasion_delta, 1)}")

        confidence_bonus = min(max(confidence_score, 0.0), 1.0) * 10.0
        score += confidence_bonus
        reasons.append(f"conf:{round(confidence_bonus, 1)}")

        if requested_styles:
            score += self._compute_category_style_rule_bonus(requested_styles[0], category_key, subtype)

        return round(score, 2), " / ".join(reasons[:4]) if reasons else f"Style: {style_primary or 'n/a'}"

    def _compute_category_style_rule_bonus(self, requested_style: str, category_key: str, subtype: str) -> float:
        return float(self.CATEGORY_STYLE_RULES.get(requested_style, {}).get(category_key, {}).get(subtype, 0))

    def _compute_budget_score(self, price: Optional[float], budget: Optional[float]) -> Tuple[float, str]:
        if price is None: return 0, "Prix absent"
        if budget is None: return 0, "Budget non défini"
        if price <= budget: return 20, f"Dans le budget ({price} <= {budget})"
        if price <= budget * 1.15: return -6, f"Légèrement au-dessus ({price} > {budget})"
        return -24, f"Hors budget ({price} > {budget})"

    def _compute_brand_score(self, brand: str, ai_profile: Dict[str, Any]) -> Tuple[float, str]:
        preferred = [self._normalize_text(x) for x in (ai_profile.get("preferred_brands") or []) if x]
        b = self._normalize_text(brand)
        for p in preferred:
            if p and p in b:
                return 12, f"Marque préférée: {brand}"
        return 0, "Marque non préférée"

    def _compute_season_score(
        self, title: str, secondary_category: str, source_description: str, search_row: Dict[str, Any],
    ) -> Tuple[float, str]:
        selected_seasons = [self._normalize_text(x) for x in (search_row.get("selected_seasons") or []) if x]
        if not selected_seasons:
            return 0, "Pas de saison ciblée"
        hay = self._normalize_text(f"{title} {secondary_category} {source_description}")
        total = 0.0
        reasons: List[str] = []
        for season in selected_seasons[:2]:
            hints = self.SEASON_HINTS.get(season)
            if not hints: continue
            positive = sum(1 for t in hints["positive"] if self._normalize_text(t) in hay)
            negative = sum(1 for t in hints["negative"] if self._normalize_text(t) in hay)
            delta = min(positive * 4, 8) - min(negative * 6, 12)
            if delta != 0:
                total += delta
                reasons.append(f"{season}:{delta}")
        return (round(total, 2), " / ".join(reasons)) if reasons else (0, "Saisonnalité neutre")

    def _compute_category_specificity_score(
        self, category_key: str, subtype: str, search_row: Dict[str, Any],
    ) -> Tuple[float, str]:
        requested_styles = [self._normalize_text(x) for x in (search_row.get("selected_styles") or []) if x]
        requested_occasions = [self._normalize_text(x) for x in (search_row.get("selected_occasions") or []) if x]
        score = 0.0
        reasons: List[str] = []
        office_context = any(x in {"bureau", "travail", "pro"} for x in requested_occasions)

        if office_context:
            if category_key == "hauts":
                if subtype in {"chemise", "blouse"}: score += 16; reasons.append("haut bureau")
                elif subtype in {"pull", "gilet", "top"}: score += 6; reasons.append("haut sobre")
                elif subtype == "tee_shirt": score -= 18; reasons.append("tee-shirt peu bureau")
                elif subtype == "caraco": score -= 22; reasons.append("caraco peu bureau")
            elif category_key == "bas":
                if subtype == "pantalon": score += 22; reasons.append("pantalon bureau")
                elif subtype == "jupe": score += 8; reasons.append("jupe bureau")
                elif subtype == "jean": score -= 22; reasons.append("jean peu bureau")
                elif subtype == "short": score -= 26; reasons.append("short hors bureau")
            elif category_key == "vestes":
                if subtype == "blazer": score += 18; reasons.append("blazer bureau")
                elif subtype in {"veste", "manteau"}: score += 8; reasons.append("veste bureau")
                elif subtype == "doudoune": score -= 22; reasons.append("doudoune casual")
                elif subtype == "sans_manches": score -= 18; reasons.append("sans manches peu bureau")
            elif category_key == "chaussures":
                if subtype in {"escarpins", "mocassins", "derbies", "ballerines"}: score += 14; reasons.append("chaussure bureau")
                elif subtype == "boots": score += 2; reasons.append("boots ok si sobres")
                elif subtype == "baskets": score -= 22; reasons.append("basket peu bureau")
            elif category_key == "robes":
                if subtype in {"robe", "combinaison"}: score += 12; reasons.append("robe/combi bureau")
            elif category_key == "sacs":
                if subtype in {"sac_a_main", "cabas"}: score += 14; reasons.append("sac bureau structuré")
                elif subtype == "sac_bandouliere": score += 8; reasons.append("sac bandoulière sobre")
                elif subtype == "sac_a_dos": score += 2; reasons.append("sac à dos neutre si sobre")
                elif subtype == "sac_banane": score -= 20; reasons.append("banane peu bureau")
                elif subtype == "pochette": score -= 6; reasons.append("pochette plutôt soirée")

        if requested_styles:
            main = requested_styles[0]
            if main == "chic":
                if category_key == "bas" and subtype == "jean": score -= 14; reasons.append("jean peu chic")
                if category_key == "bas" and subtype == "short": score -= 20; reasons.append("short peu chic")
                if category_key == "hauts" and subtype == "tee_shirt": score -= 10; reasons.append("tee-shirt peu chic")
                if category_key == "hauts" and subtype == "caraco": score -= 8; reasons.append("caraco peu chic")
                if category_key == "chaussures" and subtype == "baskets": score -= 14; reasons.append("basket peu chic")
                if category_key == "vestes" and subtype == "doudoune": score -= 14; reasons.append("doudoune peu chic")
            elif main == "classique":
                if category_key == "bas" and subtype == "jean": score -= 12; reasons.append("jean peu classique")
                if category_key == "bas" and subtype == "short": score -= 16; reasons.append("short peu classique")
                if category_key == "chaussures" and subtype == "baskets": score -= 10; reasons.append("basket peu classique")
            if main in {"chic", "classique"}:
                if category_key == "sacs" and subtype == "sac_banane": score -= 12; reasons.append("banane peu chic")
        return (round(score, 2), " / ".join(reasons)) if reasons else (0, "Catégorie neutre")

    def _compute_office_visual_penalty(
        self, category_key: str, title: str, secondary_category: str,
        source_description: str, search_row: Dict[str, Any],
    ) -> Tuple[float, str]:
        requested_occasions = [self._normalize_text(x) for x in (search_row.get("selected_occasions") or []) if x]
        requested_styles = [self._normalize_text(x) for x in (search_row.get("selected_styles") or []) if x]
        office_context = any(x in {"bureau", "travail", "pro"} for x in requested_occasions)
        chic_or_classic = any(x in {"chic", "classique", "minimaliste"} for x in requested_styles)
        if not office_context and not chic_or_classic:
            return 0, "Pas de pénalité visuelle"

        hay = self._normalize_text(f"{title} {secondary_category} {source_description}")
        score = 0.0
        reasons: List[str] = []

        if category_key in {"hauts", "bas", "robes"}:
            if self._contains_any_text(hay, self.OFFICE_NEGATIVE_HINTS["sequins"]): score -= 24; reasons.append("trop soirée")
            if self._contains_any_text(hay, self.OFFICE_NEGATIVE_HINTS["too_evening"]): score -= 14; reasons.append("registre soirée")

        if category_key == "bas":
            if self._contains_any_text(hay, self.OFFICE_NEGATIVE_HINTS["too_playful_print"]): score -= 20; reasons.append("imprimé bureau")
        elif category_key == "robes":
            if self._contains_any_text(hay, self.OFFICE_NEGATIVE_HINTS["too_playful_print"]): score -= 12; reasons.append("imprimé peu bureau")

        if category_key == "vestes":
            if self._contains_any_text(hay, self.OFFICE_NEGATIVE_HINTS["too_casual_outerwear"]): score -= 18; reasons.append("outerwear casual")

        if category_key == "hauts":
            if self._contains_any_text(hay, self.OFFICE_NEGATIVE_HINTS["too_loose"]): score -= 6; reasons.append("coupe casual")
            if self._contains_any_text(hay, ["chemise", "blouse"]):
                if not self._contains_any_text(hay, ["imprime", "imprimé", "fleuri", "floral", "carreaux", "check"]):
                    score += 6; reasons.append("chemise sobre")
            if self._contains_any_text(hay, self.OFFICE_POSITIVE_HINTS["smart_tops"]): score += 6; reasons.append("registre bureau")
        elif category_key == "bas":
            if self._contains_any_text(hay, self.OFFICE_NEGATIVE_HINTS["too_casual_bottoms"]): score -= 18; reasons.append("bas casual")
            if self._contains_any_text(hay, self.OFFICE_NEGATIVE_HINTS["too_bold_bottoms"]): score -= 28; reasons.append("matière trop mode")
            if self._contains_any_text(hay, self.OFFICE_POSITIVE_HINTS["smart_bottoms"]): score += 12; reasons.append("bas structuré")
            if self._contains_any_text(hay, ["crayon", "midi"]) and self._contains_any_text(hay, ["cuir", "croco", "simili"]): score -= 10; reasons.append("jupe crayon marquée")
            if self._contains_any_text(hay, ["pantalon cigarette", "pantalon droit"]): score += 12; reasons.append("pantalon bureau premium")
            elif self._contains_any_text(hay, ["jupe midi"]): score += 6; reasons.append("jupe midi bureau")
        elif category_key == "vestes":
            if self._contains_any_text(hay, self.OFFICE_POSITIVE_HINTS["smart_outerwear"]): score += 8; reasons.append("veste structurée")
        elif category_key == "chaussures":
            if self._contains_any_text(hay, self.OFFICE_POSITIVE_HINTS["smart_shoes"]): score += 8; reasons.append("chaussure habillée")
        elif category_key == "sacs":
            if self._contains_any_text(hay, self.OFFICE_POSITIVE_HINTS.get("smart_bags", ["cuir de vachette", "cuir grainé", "structure"])):
                score += 8; reasons.append("sac en cuir structuré")
            if self._contains_any_text(hay, ["toile", "coton", "raphia", "paille", "crochet"]):
                score -= 8; reasons.append("matière trop décontractée pour bureau")
        return (round(score, 2), " / ".join(reasons)) if reasons else (0, "Ajustement visuel neutre")

    # =========================
    # Helpers
    # =========================
    def _normalize_category_key(self, raw: str) -> Optional[str]:
        if not raw: return None
        key = self._normalize_text(raw).replace(" ", "_")
        return self.CATEGORY_KEY_NORMALIZATION.get(key, key if key in self.MVP_CATEGORY_TO_SOURCE_SECONDARY else None)

    def _contains_any_text(self, haystack: str, tokens: List[str]) -> bool:
        h = self._normalize_text(haystack)
        return any(self._normalize_text(t) in h for t in tokens)

    def _extract_budget_for_category(self, category_key: str, budgets: Dict[str, Any]) -> Optional[float]:
        if not budgets:
            return None
        candidates = [category_key, category_key.replace("_", " "), category_key.replace("_", "-")]
        if category_key == "vestes":
            candidates += ["vestes", "vestes_manteaux", "vestes et manteaux", "vestes & manteaux"]
        elif category_key in ("chaussures", "robes", "hauts", "bas"):
            candidates += [category_key]

        normalized_map = {self._normalize_text(str(k)).replace(" ", "_"): v for k, v in budgets.items()}

        for key in candidates:
            nk = self._normalize_text(str(key)).replace(" ", "_")
            if nk in normalized_map:
                return self._safe_float(normalized_map[nk])

        # Fallback : tenue_complete divisé par 5
        tc_key = self._normalize_text("tenue_complete").replace(" ", "_")
        if tc_key in normalized_map:
            tc_budget = self._safe_float(normalized_map[tc_key])
            if tc_budget:
                return tc_budget / 5.0

        return None

    def _extract_color_from_title(self, title: str) -> Optional[str]:
        hay = self._normalize_text(title)
        for color in self.COLOR_WORDS:
            if self._normalize_text(color) in hay:
                return self._normalize_text(color).replace("é", "e")
        return None

    def _extract_profile_color_names(self, value: Any) -> List[str]:
        rows = self._ensure_list(value)
        out: List[str] = []
        for row in rows:
            if isinstance(row, dict):
                display_name = row.get("displayName") or row.get("display_name")
                name = row.get("name")
                if display_name: out.append(self._normalize_text(str(display_name)))
                if name: out.append(self._normalize_text(str(name)))
            elif isinstance(row, str):
                out.append(self._normalize_text(row))
        return list(dict.fromkeys([x for x in out if x]))

    def _extract_string_list(self, value: Any) -> List[str]:
        return [row for row in self._ensure_list(value) if isinstance(row, str)]

    def _token_match(self, phrase: str, haystack_normalized: str) -> bool:
        phrase_n = self._normalize_text(phrase)
        if not phrase_n: return False
        tokens = [t for t in phrase_n.split() if len(t) >= 3]
        return any(token in haystack_normalized for token in tokens[:3]) if tokens else False

    def _normalize_currency(self, value: Any) -> str:
        v = (str(value).strip() if value is not None else "")
        return v.upper() if v.upper() in {"EUR", "USD", "GBP"} else "EUR"

    def _safe_float(self, value: Any) -> Optional[float]:
        if value is None or value == "": return None
        try: return float(value)
        except Exception: return None

    def _ensure_list(self, value: Any) -> List[Any]:
        if value is None: return []
        return value if isinstance(value, list) else []

    def _normalize_text(self, value: str) -> str:
        s = (value or "").strip().lower()
        s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
        s = re.sub(r"[^a-z0-9\s\-_&]", " ", s)
        s = re.sub(r"\s{2,}", " ", s).strip()
        return s

    def _normalize_text_list(self, value: Any) -> List[str]:
        rows = self._ensure_list(value)
        out = [self._normalize_text(str(x)) for x in rows if isinstance(x, str) and str(x).strip()]
        return list(dict.fromkeys(out))

    def _normalize_product_family_text(self, value: str) -> str:
        s = self._normalize_text(value or "")
        s = re.sub(r"\btaille\s+[a-z0-9/\-]+\b", " ", s)
        s = re.sub(r"\b(xx?s|xx?l|xs|s|m|l|xl|xxl|3xl|4xl)\b", " ", s)
        s = re.sub(r"\b(32|34|36|38|40|42|44|46|48|50|52)\b", " ", s)
        s = re.sub(r"\bseconde\s+main\b", " ", s)
        s = re.sub(r"\s{2,}", " ", s).strip()
        return s

    def _build_product_family_key(self, row: Dict[str, Any]) -> str:
        brand = self._normalize_text(str(row.get("brand") or ""))
        title = self._normalize_product_family_text(str(row.get("title") or row.get("product_name") or ""))
        return f"{brand}::{title}"

    def _canonicalize_product_url(self, url: str) -> str:
        if not url: return ""
        try:
            parsed = urlparse(url.strip())
            clean = urlunparse((parsed.scheme.lower(), parsed.netloc.lower(), parsed.path.rstrip("/"), "", "", ""))
            return clean.replace("http://", "https://")
        except Exception:
            return (url or "").strip().lower()

    def _infer_subtype(self, category_key: str, title: str, secondary_category: str) -> str:
        hay = self._normalize_text(f"{title} {secondary_category}")
        rules = self.CATEGORY_SUBTYPE_HINTS.get(category_key, {})
        for subtype, tokens in rules.items():
            for token in tokens:
                if self._normalize_text(token) in hay:
                    return subtype
        return "other"

    def _group_saved_recommendations(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        grouped: Dict[str, Dict[str, Any]] = {}
        for row in rows:
            category_key = str(row.get("category_key") or "").strip().lower()
            if not category_key: continue
            if category_key not in grouped:
                grouped[category_key] = {
                    "category_key": category_key,
                    "category_label": self.CATEGORY_LABELS.get(category_key, category_key.capitalize()),
                    "items": [],
                }
            reasons_json = row.get("reasons_json") or {}
            reason = reasons_json.get("category") or reasons_json.get("style") or reasons_json.get("color") or ""
            grouped[category_key]["items"].append({
                "id": str(row.get("id")), "product_id": str(row.get("product_id")),
                "title": row.get("title") or "", "brand": row.get("brand") or "",
                "image_url": row.get("image_url") or "",
                "price": float(row.get("price")) if row.get("price") else None,
                "currency": row.get("currency") or "EUR",
                "buy_url": row.get("buy_url") or "", "product_url": row.get("product_url") or "",
                "score_total": float(row.get("score_total") or 0), "reason": reason,
            })
        return list(grouped.values())


search_recommendation_service = SearchRecommendationService()