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

    Nouvelle logique V2 :
    1. Lit user_searches
    2. Lit user_ai_profiles
    3. Crée un run dans user_search_runs
    4. Cherche des candidats dans affiliate_product_enrichment (style_v6)
    5. Récupère les données commerciales dans affiliate_products
    6. Score les candidats selon style/catégorie/budget/couleurs/morphologie
    7. Insère les meilleurs dans user_search_recommendations
    8. Met le run en completed / failed
    """

    ALGORITHM_VERSION = "search_reco_v2_v6"

    # =========================
    # Scope MVP strict
    # =========================
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
    }

    CATEGORY_KEY_NORMALIZATION = {
        "tenue_complete": "tenue_complete",
        "hauts": "hauts",
        "haut": "hauts",
        "bas": "bas",
        "robes": "robes",
        "robe": "robes",
        "chaussures": "chaussures",
        "chaussure": "chaussures",
        "vestes": "vestes",
        "vestes_manteaux": "vestes",
        "vestes_et_manteaux": "vestes",
        "vestes_&_manteaux": "vestes",
        "veste": "vestes",
        "manteaux": "vestes",
        "manteau": "vestes",
        # catégories hors scope MVP volontairement ignorées
        "accessoires": None,
        "sacs": None,
        "bijoux": None,
        "sous-vetements": None,
        "sous_vetements": None,
        "lingerie": None,
        "maillots_bain": None,
        "maillots_de_bain": None,
        "tenue_sport": None,
        "vetements_sport": None,
        "vetements_de_sport": None,
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
            "chemise": ["chemise"],
            "blouse": ["blouse"],
            "pull": ["pull", "maille"],
            "gilet": ["gilet", "cardigan"],
            "tee_shirt": ["tee-shirt", "tee shirt", "t-shirt", "t shirt"],
            "top": ["top"],
        },
        "bas": {
            "pantalon": ["pantalon", "tailleur"],
            "jean": ["jean", "denim"],
            "jupe": ["jupe"],
        },
        "robes": {
            "robe": ["robe"],
            "combinaison": ["combinaison", "jumpsuit"],
        },
        "vestes": {
            "blazer": ["blazer", "tailleur"],
            "veste": ["veste", "blouson"],
            "manteau": ["manteau", "trench"],
        },
        "chaussures": {
            "baskets": ["basket", "sneaker", "running"],
            "boots": ["boots", "bottine", "bottes"],
            "sandales": ["sandale"],
            "escarpins": ["escarpin", "heel", "heels"],
            "mocassins": ["mocassin", "loafer"],
            "derbies": ["derby"],
            "ballerines": ["ballerine"],
        },
    }

    STYLE_COMPATIBILITY_MATRIX = {
        "chic": {
            "chic": 38,
            "classique": 28,
            "minimaliste": 20,
            "moderne": 14,
            "romantique": 8,
            "vintage": 4,
            "rock": -4,
            "boheme": -10,
            "casual": -14,
            "sportswear": -24,
        },
        "classique": {
            "classique": 36,
            "chic": 24,
            "minimaliste": 18,
            "moderne": 10,
            "casual": 4,
            "vintage": 4,
            "romantique": 2,
            "rock": -8,
            "boheme": -10,
            "sportswear": -18,
        },
        "casual": {
            "casual": 34,
            "sportswear": 16,
            "classique": 8,
            "minimaliste": 6,
            "moderne": 6,
            "rock": 4,
            "boheme": 2,
            "romantique": 0,
            "vintage": 0,
            "chic": -6,
        },
        "sportswear": {
            "sportswear": 36,
            "casual": 16,
            "moderne": 8,
            "rock": 4,
            "classique": -8,
            "chic": -14,
            "boheme": -12,
            "romantique": -14,
            "minimaliste": -2,
            "vintage": -4,
        },
        "boheme": {
            "boheme": 34,
            "romantique": 18,
            "vintage": 10,
            "chic": 4,
            "casual": 2,
            "classique": -4,
            "minimaliste": -8,
            "moderne": -8,
            "rock": -6,
            "sportswear": -16,
        },
        "romantique": {
            "romantique": 34,
            "boheme": 16,
            "chic": 10,
            "classique": 8,
            "vintage": 6,
            "minimaliste": -2,
            "casual": -4,
            "moderne": -4,
            "rock": -12,
            "sportswear": -16,
        },
        "rock": {
            "rock": 34,
            "moderne": 12,
            "casual": 8,
            "chic": 2,
            "sportswear": 2,
            "classique": -6,
            "boheme": -8,
            "romantique": -10,
            "minimaliste": 0,
            "vintage": 4,
        },
        "minimaliste": {
            "minimaliste": 34,
            "classique": 22,
            "chic": 18,
            "moderne": 16,
            "casual": 6,
            "romantique": -2,
            "boheme": -10,
            "rock": -4,
            "sportswear": -8,
            "vintage": -4,
        },
        "moderne": {
            "moderne": 34,
            "minimaliste": 18,
            "chic": 12,
            "classique": 10,
            "rock": 8,
            "casual": 6,
            "sportswear": 2,
            "boheme": -8,
            "romantique": -6,
            "vintage": 2,
        },
        "vintage": {
            "vintage": 34,
            "romantique": 12,
            "boheme": 10,
            "classique": 6,
            "rock": 4,
            "chic": 2,
            "casual": 2,
            "minimaliste": -6,
            "moderne": -4,
            "sportswear": -10,
        },
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
        "hiver": {
            "positive": {"laine", "maille", "cachemire", "manteau", "doudoune", "boots", "bottes", "velours", "tweed"},
            "negative": {"sandale", "maillot", "lin", "crochet"},
        },
        "ete": {
            "positive": {"sandale", "lin", "crochet", "robe", "blouse", "top", "combinaison"},
            "negative": {"laine", "cachemire", "doudoune", "manteau", "boots"},
        },
        "printemps": {
            "positive": {"blouse", "chemise", "veste", "blazer", "jupe", "pantalon", "mocassin", "ballerine"},
            "negative": {"doudoune", "maillot"},
        },
        "automne": {
            "positive": {"maille", "pull", "gilet", "veste", "bottine", "boots", "manteau"},
            "negative": {"maillot"},
        },
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
                for x in selected_article_types
                if x
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
                "style_v6_primary": 38,
                "style_v6_tags": 16,
                "style_v6_confidence": 10,
                "category_specificity": 14,
                "budget": 20,
                "color_best": 24,
                "color_ok": 10,
                "color_avoid": -40,
                "brand_preferred": 12,
                "morphology_match": 12,
                "occasion_context": 12,
                "season_context": 8,
            }

            filters_json = {
                "selected_seasons": search_row.get("selected_seasons") or [],
                "selected_styles": search_row.get("selected_styles") or [],
                "selected_occasions": search_row.get("selected_occasions") or [],
                "selected_article_types": normalized_categories,
                "selected_budgets": search_row.get("selected_budgets") or {},
                "classifier_version": "style_v6",
                "scope": "mvp_femme_useful",
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

            for category_key in normalized_categories:
                candidates = self._fetch_candidates_for_category(
                    category_key=category_key,
                    limit=280,
                )

                budget = self._extract_budget_for_category(
                    category_key=category_key,
                    budgets=search_row.get("selected_budgets") or {},
                )

                scored: List[Dict[str, Any]] = []
                for row in candidates:
                    scored_row = self._score_product(
                        product=row,
                        category_key=category_key,
                        search_row=search_row,
                        ai_profile=ai_profile,
                        budget=budget,
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

            self._update_run(
                run_id=run_id,
                status="success",
                error_message=None,
            )

            return {
                "status": "success",
                "run_id": run_id,
                "recommendations_inserted": all_inserted,
            }

        except Exception as e:
            if run_id:
                try:
                    self._update_run(
                        run_id=run_id,
                        status="failed",
                        error_message=str(e)[:1000],
                    )
                except Exception:
                    pass

            return {
                "status": "error",
                "error": str(e),
                "run_id": run_id,
            }

    # =========================
    # Data fetch
    # =========================
    def _get_search(self, search_id: str) -> Optional[Dict[str, Any]]:
        response = self.supabase.query(
            "user_searches",
            select_fields="*",
            filters={"id": search_id},
        )
        return response.data[0] if response.data else None

    def _get_ai_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        response = self.supabase.query(
            "user_ai_profiles",
            select_fields="*",
            filters={"user_id": user_id},
        )
        return response.data[0] if response.data else None

    def _fetch_candidates_for_category(self, category_key: str, limit: int = 250) -> List[Dict[str, Any]]:
        allowed_secondaries = list(self.MVP_CATEGORY_TO_SOURCE_SECONDARY.get(category_key, set()))
        if not allowed_secondaries:
            return []

        # 1) on récupère d'abord les produits enrichis V6
        enrichment_rows = self._fetch_enrichment_rows_for_category(
            category_key=category_key,
            allowed_secondaries=allowed_secondaries,
            limit=max(limit * 2, 250),
        )
        if not enrichment_rows:
            return []

        # 2) puis on hydrate avec les données commerciales depuis affiliate_products
        product_rows = self._fetch_affiliate_products_for_enrichments(enrichment_rows)
        if not product_rows:
            return []

        product_map = {
            (int(r["merchant_id"]), str(r["product_id"])): r
            for r in product_rows
            if r.get("merchant_id") is not None and r.get("product_id") is not None
        }

        merged: List[Dict[str, Any]] = []
        seen: Set[str] = set()

        for e in enrichment_rows:
            merchant_id = e.get("merchant_id")
            product_id = e.get("product_id")
            if merchant_id is None or product_id is None:
                continue

            key_tuple = (int(merchant_id), str(product_id))
            p = product_map.get(key_tuple)
            if not p:
                continue

            uniq = f"{merchant_id}::{product_id}"
            if uniq in seen:
                continue
            seen.add(uniq)

            merged.append({
                "merchant_id": merchant_id,
                "product_id": product_id,
                "sid": p.get("sid") or e.get("sid"),
                "product_name": p.get("product_name") or e.get("source_product_name"),
                "brand": p.get("brand") or e.get("source_brand"),
                "primary_category": p.get("primary_category") or e.get("source_primary_category"),
                "secondary_category": p.get("secondary_category") or e.get("source_secondary_category"),
                "product_url": (p.get("product_url") or "").strip(),
                "image_url": (p.get("image_url") or "").strip(),
                "buy_url": (p.get("buy_url") or "").strip(),
                "price": p.get("price"),
                "sale_price": p.get("sale_price"),
                "currency": p.get("currency"),
                "availability": p.get("availability"),
                "is_deleted": p.get("is_deleted"),
                "last_seen_at": p.get("last_seen_at"),
                "keywords": p.get("keywords"),
                "style_primary": e.get("style_primary"),
                "style_tags": e.get("style_tags") or [],
                "style_scores_json": e.get("style_scores_json") or {},
                "confidence_score": e.get("confidence_score"),
                "source_product_name": e.get("source_product_name"),
                "source_brand": e.get("source_brand"),
                "source_primary_category": e.get("source_primary_category"),
                "source_secondary_category": e.get("source_secondary_category"),
                "source_keywords": e.get("source_keywords"),
                "source_description": e.get("source_description"),
                "secondary_category_levels": e.get("secondary_category_levels") or [],
                "classifier_version": e.get("classifier_version"),
                "classifier_meta_json": e.get("classifier_meta_json") or {},
                "signals_json": e.get("signals_json") or {},
            })

            if len(merged) >= limit:
                break

        return merged

    def _fetch_enrichment_rows_for_category(
        self,
        category_key: str,
        allowed_secondaries: List[str],
        limit: int,
    ) -> List[Dict[str, Any]]:
        collected: List[Dict[str, Any]] = []
        seen: Set[str] = set()

        # On interroge par secondary_category autorisée pour garder un contrôle fin
        for secondary in allowed_secondaries:
            try:
                response = (
                    self.client.table("affiliate_product_enrichment")
                    .select(
                        "merchant_id,product_id,sid,style_primary,style_tags,style_scores_json,"
                        "confidence_score,source_product_name,source_brand,source_primary_category,"
                        "source_secondary_category,source_keywords,source_description,"
                        "secondary_category_levels,classifier_version,classifier_meta_json,signals_json"
                    )
                    .eq("classifier_version", "style_v6")
                    .eq("source_secondary_category", secondary)
                    .limit(min(120, limit))
                    .execute()
                )

                rows = response.data or []
                for row in rows:
                    if self._normalize_text(str(row.get("source_primary_category") or "")) != "femme":
                        continue

                    product_key = f"{row.get('merchant_id')}::{row.get('product_id')}"
                    if product_key in seen:
                        continue
                    seen.add(product_key)
                    collected.append(row)

                    if len(collected) >= limit:
                        return collected

            except Exception as e:
                print(f"⚠️ Erreur fetch enrichment {secondary}: {e}")

        return collected

    def _fetch_affiliate_products_for_enrichments(self, enrichment_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        by_merchant: Dict[int, List[str]] = defaultdict(list)

        for row in enrichment_rows:
            merchant_id = row.get("merchant_id")
            product_id = row.get("product_id")
            if merchant_id is None or product_id is None:
                continue
            by_merchant[int(merchant_id)].append(str(product_id))

        collected: List[Dict[str, Any]] = []
        seen: Set[str] = set()

        for merchant_id, product_ids in by_merchant.items():
            unique_ids = list(dict.fromkeys(product_ids))
            chunks = [unique_ids[i:i + 150] for i in range(0, len(unique_ids), 150)]

            for chunk in chunks:
                try:
                    response = (
                        self.client.table("affiliate_products")
                        .select(
                            "merchant_id,sid,product_id,product_name,brand,primary_category,"
                            "secondary_category,product_url,image_url,buy_url,price,sale_price,"
                            "currency,availability,keywords,is_deleted,last_seen_at"
                        )
                        .eq("merchant_id", merchant_id)
                        .eq("is_deleted", False)
                        .eq("primary_category", "Femme")
                        .in_("product_id", chunk)
                        .execute()
                    )

                    rows = response.data or []
                    for row in rows:
                        key = f"{row.get('merchant_id')}::{row.get('product_id')}"
                        if key in seen:
                            continue
                        seen.add(key)
                        collected.append(row)

                except Exception as e:
                    print(f"⚠️ Erreur fetch affiliate_products merchant={merchant_id}: {e}")

        return collected

    # =========================
    # Run management
    # =========================
    def _create_run(
        self,
        user_search_id: str,
        status: str,
        algorithm_version: str,
        weights_json: Dict[str, Any],
        filters_json: Dict[str, Any],
    ) -> str:
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
        payload = {
            "status": status,
            "error_message": error_message,
        }

        response = (
            self.client.table("user_search_runs")
            .update(payload)
            .eq("id", run_id)
            .execute()
        )

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
    # Scoring
    # =========================
    def _score_product(
        self,
        product: Dict[str, Any],
        category_key: str,
        search_row: Dict[str, Any],
        ai_profile: Dict[str, Any],
        budget: Optional[float],
    ) -> Optional[Dict[str, Any]]:
        title = (product.get("product_name") or "").strip()
        brand = (product.get("brand") or "").strip()
        secondary_category = (product.get("secondary_category") or "").strip()
        source_description = (product.get("source_description") or "").strip()
        style_primary = self._normalize_text(str(product.get("style_primary") or ""))
        style_tags = self._normalize_text_list(product.get("style_tags"))
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

        extracted_color = self._extract_color_from_title(title)
        subtype = self._infer_subtype(category_key, title, secondary_category)

        color_score, color_reason = self._compute_color_score(extracted_color, ai_profile)
        style_score, style_reason = self._compute_style_score(
            style_primary=style_primary,
            style_tags=style_tags,
            style_scores_json=style_scores_json,
            confidence_score=confidence_score,
            category_key=category_key,
            subtype=subtype,
            search_row=search_row,
            ai_profile=ai_profile,
        )
        morphology_score, morphology_reason = self._compute_morphology_score(
            title=title,
            secondary_category=secondary_category,
            source_description=source_description,
            ai_profile=ai_profile,
        )
        budget_score, budget_reason = self._compute_budget_score(price, budget)
        brand_score, brand_reason = self._compute_brand_score(brand, ai_profile)
        season_score, season_reason = self._compute_season_score(
            title=title,
            secondary_category=secondary_category,
            source_description=source_description,
            search_row=search_row,
        )
        category_specificity_score, category_specificity_reason = self._compute_category_specificity_score(
            category_key=category_key,
            subtype=subtype,
            search_row=search_row,
        )

        total_score = (
            10
            + color_score
            + style_score
            + morphology_score
            + budget_score
            + brand_score
            + season_score
            + category_specificity_score
        )

        reasons_json = {
            "style": style_reason,
            "category_specificity": category_specificity_reason,
            "season": season_reason,
            "color": color_reason,
            "morphology": morphology_reason,
            "budget": budget_reason,
            "brand": brand_reason,
            "style_primary": style_primary,
            "style_tags": style_tags,
            "confidence_score": confidence_score,
            "secondary_category": secondary_category,
            "subtype": subtype,
            "extracted_color": extracted_color,
        }

        return {
            "merchant_id": merchant_id,
            "product_id": product_id,
            "title": title,
            "brand": brand,
            "price": price,
            "currency": currency,
            "image_url": image_url,
            "buy_url": buy_url,
            "product_url": product_url,
            "score_total": round(max(total_score, 0), 2),
            "score_color": round(max(color_score, 0), 2),
            "score_morphology": round(max(morphology_score, 0), 2),
            "score_style": round(max(style_score, 0), 2),
            "reasons_json": reasons_json,
        }

    def _compute_color_score(self, extracted_color: Optional[str], ai_profile: Dict[str, Any]) -> Tuple[float, str]:
        if not extracted_color:
            return 0, "Couleur non détectée dans le titre produit"

        best = self._extract_profile_color_names(ai_profile.get("colors_best"))
        ok = self._extract_profile_color_names(ai_profile.get("colors_ok"))
        avoid = self._extract_profile_color_names(ai_profile.get("colors_avoid"))
        keywords = [self._normalize_text(x) for x in (ai_profile.get("color_keywords") or []) if x]

        c = self._normalize_text(extracted_color)

        if c in avoid:
            return -40, f"Couleur déconseillée pour ce profil: {extracted_color}"
        if c in best or c in keywords:
            return 24, f"Couleur très favorable pour ce profil: {extracted_color}"
        if c in ok:
            return 10, f"Couleur acceptable pour ce profil: {extracted_color}"
        if c in self.NEUTRAL_COLORS:
            return 4, f"Couleur neutre facile à porter: {extracted_color}"

        return 0, f"Couleur neutre/non reconnue: {extracted_color}"

    def _compute_style_score(
        self,
        style_primary: str,
        style_tags: List[str],
        style_scores_json: Dict[str, Any],
        confidence_score: float,
        category_key: str,
        subtype: str,
        search_row: Dict[str, Any],
        ai_profile: Dict[str, Any],
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
                base_conf_bonus = min(max(confidence_score, 0.0), 1.0) * 6
                return round(base_conf_bonus, 2), f"Style V6 détecté: {style_primary}"
            return 0, "Aucun style cible explicite"

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

            raw_style_score = self._safe_float(style_scores_json.get(target_style))
            if raw_style_score is not None:
                score += min(raw_style_score * 2.5, 10)

        # bonus/malus contexte occasion
        occasion_delta = 0.0
        for occasion in occasions:
            mapping = self.OCCASION_STYLE_BOOSTS.get(occasion)
            if mapping:
                occasion_delta += mapping.get(style_primary, 0)
        if occasion_delta:
            score += occasion_delta
            reasons.append(f"occasion:{round(occasion_delta, 1)}")

        # bonus confiance
        confidence_bonus = min(max(confidence_score, 0.0), 1.0) * 10.0
        score += confidence_bonus
        reasons.append(f"conf:{round(confidence_bonus, 1)}")

        # règle catégorie/sous-type selon le style principal demandé
        if requested_styles:
            main_requested_style = requested_styles[0]
            score += self._compute_category_style_rule_bonus(
                requested_style=main_requested_style,
                category_key=category_key,
                subtype=subtype,
            )

        reason = " / ".join(reasons[:4]) if reasons else f"Style V6 principal: {style_primary or 'n/a'}"
        return round(score, 2), reason

    def _compute_category_style_rule_bonus(self, requested_style: str, category_key: str, subtype: str) -> float:
        style_rules = self.CATEGORY_STYLE_RULES.get(requested_style, {})
        category_rules = style_rules.get(category_key, {})
        return float(category_rules.get(subtype, 0))

    def _compute_morphology_score(
        self,
        title: str,
        secondary_category: str,
        source_description: str,
        ai_profile: Dict[str, Any],
    ) -> Tuple[float, str]:
        hay = self._normalize_text(f"{title} {secondary_category} {source_description}")

        recommended = self._extract_string_list(ai_profile.get("cuts_recommended"))
        avoided = self._extract_string_list(ai_profile.get("cuts_avoid"))

        positive_matches = [cut for cut in recommended if self._token_match(cut, hay)]
        negative_matches = [cut for cut in avoided if self._token_match(cut, hay)]

        if negative_matches:
            return -12, f"Coupe plutôt déconseillée: {negative_matches[0]}"
        if positive_matches:
            return 12, f"Coupe compatible avec la morphologie: {positive_matches[0]}"

        return 0, "Pas d’indice morphologique explicite détecté"

    def _compute_budget_score(self, price: Optional[float], budget: Optional[float]) -> Tuple[float, str]:
        if price is None:
            return 0, "Prix absent"
        if budget is None:
            return 0, "Budget non défini pour cette catégorie"
        if price <= budget:
            return 20, f"Dans le budget ({price} <= {budget})"
        if price <= budget * 1.15:
            return -6, f"Légèrement au-dessus du budget ({price} > {budget})"
        return -24, f"Hors budget ({price} > {budget})"

    def _compute_brand_score(self, brand: str, ai_profile: Dict[str, Any]) -> Tuple[float, str]:
        preferred = [self._normalize_text(x) for x in (ai_profile.get("preferred_brands") or []) if x]
        b = self._normalize_text(brand)

        for p in preferred:
            if p and p in b:
                return 12, f"Marque préférée détectée: {brand}"

        return 0, "Marque non préférée"

    def _compute_season_score(
        self,
        title: str,
        secondary_category: str,
        source_description: str,
        search_row: Dict[str, Any],
    ) -> Tuple[float, str]:
        selected_seasons = [self._normalize_text(x) for x in (search_row.get("selected_seasons") or []) if x]
        if not selected_seasons:
            return 0, "Pas de saison ciblée"

        hay = self._normalize_text(f"{title} {secondary_category} {source_description}")
        total = 0.0
        reasons: List[str] = []

        for season in selected_seasons[:2]:
            hints = self.SEASON_HINTS.get(season)
            if not hints:
                continue

            positive = sum(1 for token in hints["positive"] if self._normalize_text(token) in hay)
            negative = sum(1 for token in hints["negative"] if self._normalize_text(token) in hay)

            delta = min(positive * 4, 8) - min(negative * 6, 12)
            if delta != 0:
                total += delta
                reasons.append(f"{season}:{delta}")

        if reasons:
            return round(total, 2), " / ".join(reasons)
        return 0, "Cohérence saisonnière neutre"

    def _compute_category_specificity_score(
        self,
        category_key: str,
        subtype: str,
        search_row: Dict[str, Any],
    ) -> Tuple[float, str]:
        requested_styles = [self._normalize_text(x) for x in (search_row.get("selected_styles") or []) if x]
        requested_occasions = [self._normalize_text(x) for x in (search_row.get("selected_occasions") or []) if x]

        score = 0.0
        reasons: List[str] = []

        if "bureau" in requested_occasions or "travail" in requested_occasions or "pro" in requested_occasions:
            if category_key == "hauts":
                if subtype in {"chemise", "blouse"}:
                    score += 10
                    reasons.append("haut bureau pertinent")
                elif subtype == "tee_shirt":
                    score -= 14
                    reasons.append("tee-shirt peu bureau")
            elif category_key == "bas":
                if subtype in {"pantalon", "jupe"}:
                    score += 10
                    reasons.append("bas bureau pertinent")
                elif subtype == "jean":
                    score -= 16
                    reasons.append("jean peu bureau")
            elif category_key == "vestes":
                if subtype == "blazer":
                    score += 12
                    reasons.append("blazer pertinent")
            elif category_key == "chaussures":
                if subtype in {"escarpins", "mocassins", "derbies", "ballerines"}:
                    score += 10
                    reasons.append("chaussure bureau pertinente")
                elif subtype == "baskets":
                    score -= 16
                    reasons.append("basket peu bureau")

        if requested_styles:
            main_style = requested_styles[0]
            if main_style == "chic":
                if category_key == "bas" and subtype == "jean":
                    score -= 10
                    reasons.append("jean peu chic")
                if category_key == "hauts" and subtype == "tee_shirt":
                    score -= 8
                    reasons.append("tee-shirt peu chic")
                if category_key == "chaussures" and subtype == "baskets":
                    score -= 12
                    reasons.append("basket peu chic")

        if reasons:
            return round(score, 2), " / ".join(reasons)
        return 0, "Catégorie/sous-type neutre"

    # =========================
    # Helpers
    # =========================
    def _normalize_category_key(self, raw: str) -> Optional[str]:
        if not raw:
            return None
        key = self._normalize_text(raw).replace(" ", "_")
        return self.CATEGORY_KEY_NORMALIZATION.get(key, key if key in self.MVP_CATEGORY_TO_SOURCE_SECONDARY else None)

    def _extract_budget_for_category(self, category_key: str, budgets: Dict[str, Any]) -> Optional[float]:
        if not budgets:
            return None

        candidates = [
            category_key,
            category_key.replace("_", " "),
            category_key.replace("_", "-"),
        ]

        if category_key == "vestes":
            candidates += ["vestes", "vestes_manteaux", "vestes et manteaux", "vestes & manteaux"]
        elif category_key == "chaussures":
            candidates += ["chaussures"]
        elif category_key == "robes":
            candidates += ["robes", "robe"]
        elif category_key == "hauts":
            candidates += ["hauts", "haut"]
        elif category_key == "bas":
            candidates += ["bas"]

        normalized_map = {
            self._normalize_text(str(k)).replace(" ", "_"): v
            for k, v in budgets.items()
        }

        for key in candidates:
            nk = self._normalize_text(str(key)).replace(" ", "_")
            if nk in normalized_map:
                return self._safe_float(normalized_map[nk])

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
                if display_name:
                    out.append(self._normalize_text(str(display_name)))
                if name:
                    out.append(self._normalize_text(str(name)))
            elif isinstance(row, str):
                out.append(self._normalize_text(row))
        return list(dict.fromkeys([x for x in out if x]))

    def _extract_string_list(self, value: Any) -> List[str]:
        rows = self._ensure_list(value)
        out: List[str] = []
        for row in rows:
            if isinstance(row, str):
                out.append(row)
        return out

    def _token_match(self, phrase: str, haystack_normalized: str) -> bool:
        phrase_n = self._normalize_text(phrase)
        if not phrase_n:
            return False

        tokens = [t for t in phrase_n.split() if len(t) >= 3]
        if not tokens:
            return False

        return any(token in haystack_normalized for token in tokens[:3])

    def _normalize_currency(self, value: Any) -> str:
        v = (str(value).strip() if value is not None else "")
        if v.upper() in {"EUR", "USD", "GBP"}:
            return v.upper()
        return "EUR"

    def _safe_float(self, value: Any) -> Optional[float]:
        if value is None or value == "":
            return None
        try:
            return float(value)
        except Exception:
            return None

    def _ensure_list(self, value: Any) -> List[Any]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return []

    def _normalize_text(self, value: str) -> str:
        s = (value or "").strip().lower()
        s = "".join(
            c for c in unicodedata.normalize("NFD", s)
            if unicodedata.category(c) != "Mn"
        )
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
        if not url:
            return ""

        try:
            parsed = urlparse(url.strip())
            clean = urlunparse((
                parsed.scheme.lower(),
                parsed.netloc.lower(),
                parsed.path.rstrip("/"),
                "",
                "",
                ""
            ))
            clean = clean.replace("http://", "https://")
            return clean
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


search_recommendation_service = SearchRecommendationService()