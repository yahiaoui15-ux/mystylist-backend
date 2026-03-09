import re
import uuid
import unicodedata
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from app.utils.supabase_client import supabase


class SearchRecommendationService:
    """
    Génère des recommandations affiliées pour une recherche utilisateur.

    Pipeline:
    1. Lit user_searches
    2. Lit user_ai_profiles
    3. Crée un run dans user_search_runs
    4. Cherche des candidats dans affiliate_products
    5. Score les candidats
    6. Insère les meilleurs dans user_search_recommendations
    7. Met le run en completed / failed
    """

    ALGORITHM_VERSION = "search_reco_v1"

    ARTICLE_TYPE_TO_SECONDARY_CATEGORIES = {
        "tenue_complete": ["Vêtements~~Robe", "Vêtements~~Combinaison"],
        "hauts": [
            "Vêtements~~Top & Blouse",
            "Vêtements~~Tee-Shirt",
            "Vêtements~~Chemise",
            "Vêtements~~Pull",
            "Vêtements~~Gilet",
            "Clothing~~Shirts & Tops",
        ],
        "bas": [
            "Vêtements~~Pantalon",
            "Vêtements~~Jean",
            "Vêtements~~Jupe",
            "Vêtements~~Short & Bermuda",
            "Clothing~~Pants",
            "Clothing~~Skirts",
            "Clothing~~Shorts",
        ],
        "robes": [
            "Vêtements~~Robe",
            "Clothing~~Dresses",
        ],
        "chaussures": [
            "Chaussures",
            "Chaussures~~Baskets",
            "Chaussures~~Boots & Bottines",
            "Chaussures~~Sandales",
            "Chaussures~~Escarpins",
            "Chaussures~~Ballerines",
            "Chaussures~~Mocassins",
            "Footwear~~Chaussures",
            "Footwear~~Sneakers",
        ],
        "accessoires": [
            "Accessoires~~Sacs",
            "Accessoires~~Bijoux",
            "Accessoires~~Ceinture",
            "Accessoires~~Ceintures",
            "Accessoires~~Echarpe",
            "Accessoires~~Echarpe & Foulard",
            "Maroquinerie~~Sacs",
            "Maroquinerie~~Cabas",
        ],
        "sacs": [
            "Accessoires~~Sacs",
            "Maroquinerie~~Sacs",
            "Maroquinerie~~Cabas",
        ],
        "vestes_manteaux": [
            "Vêtements~~Veste & Blouson",
            "Vêtements~~Manteau",
            "Vêtements~~Gilet",
            "Clothing~~Outerwear",
            "Clothing~~Outerwear~~Coats & Jackets",
        ],
        "sous-vetements": [
            "Vêtements~~Underwear",
            "Vêtements~~Sous-Vêtements",
            "Lingerie~~Lingerie",
            "Clothing~~Underwear & Socks~~Lingerie",
            "Clothing~~Underwear & Socks~~Bras",
            "Clothing~~Underwear & Socks~~Underwear",
        ],
        "maillots_bain": [
            "Vêtements~~Maillot de bain",
            "Clothing~~Swimwear",
        ],
        "vetements_sport": [
            "Sport~~Legging",
            "Sport~~Tee-shirts & Débardeurs",
            "Sport~~Brassières",
            "Clothing~~Activewear",
        ],
        "bijoux": [
            "Accessoires~~Bijoux",
        ],
    }

    COLOR_WORDS = [
        "noir", "blanc", "bleu", "rose", "rouge", "vert", "jaune",
        "orange", "marron", "beige", "gris", "violet", "prune",
        "camel", "kaki", "bordeaux", "multicolore", "marine",
        "argent", "argente", "doré", "dore",
    ]

    STYLE_HINTS = {
        "minimaliste": ["uni", "simple", "epure", "épuré", "droit", "classique"],
        "romantique": ["dentelle", "fluide", "volant", "fleur", "plisse", "plissé"],
        "classique": ["tailleur", "droit", "chemise", "blazer", "intemporel"],
        "casual": ["tee", "t-shirt", "jean", "maille", "pull", "basket"],
        "chic": ["blazer", "robe", "escarpin", "tailleur", "manteau"],
        "boheme": ["imprime", "imprimé", "fluide", "long", "brode", "brodé"],
        "rock": ["cuir", "noir", "boot", "bottine", "metal", "métal"],
        "vintage": ["retro", "rétro", "col", "taille haute", "plisse", "plissé"],
        "moderne": ["oversize", "structure", "droit", "minimal"],
        "sportswear": ["legging", "sport", "sweat", "activewear", "basket"],
    }

    CATEGORY_KEY_NORMALIZATION = {
        "tenue_complete": "tenue_complete",
        "hauts": "hauts",
        "bas": "bas",
        "robes": "robes",
        "chaussures": "chaussures",
        "accessoires": "accessoires",
        "sacs": "sacs",
        "vestes_manteaux": "vestes_manteaux",
        "sous-vetements": "sous-vetements",
        "maillots_bain": "maillots_bain",
        "vetements_sport": "vetements_sport",
        "bijoux": "bijoux",
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

            # MVP: "tenue_complete" = raccourci vers plusieurs catégories concrètes
            normalized_article_types = [self._normalize_text(x).replace(" ", "_") for x in selected_article_types if x]

            if normalized_article_types == ["tenue_complete"]:
                selected_article_types = [
                    "hauts",
                    "bas",
                    "robes",
                    "vestes",
                    "chaussures",
                    "sacs",
                    "accessoires",
                ]
            else:
                # si tenue_complete est combiné avec d'autres catégories, on l'ignore
                selected_article_types = [x for x in selected_article_types if self._normalize_text(x).replace(" ", "_") != "tenue_complete"]

            weights_json = {
                "budget": 20,
                "color_best": 30,
                "color_ok": 10,
                "color_avoid": -40,
                "brand_preferred": 15,
                "style_match": 20,
                "morphology_match": 15,
                "base_category_match": 10,
            }

            filters_json = {
                "selected_seasons": search_row.get("selected_seasons") or [],
                "selected_styles": search_row.get("selected_styles") or [],
                "selected_occasions": search_row.get("selected_occasions") or [],
                "selected_article_types": selected_article_types,
                "selected_budgets": search_row.get("selected_budgets") or {},
            }

            run_id = self._create_run(
                user_search_id=search_id,
                status="running",
                algorithm_version=self.ALGORITHM_VERSION,
                weights_json=weights_json,
                filters_json=filters_json,
            )

            all_inserted = 0

            # On efface les recos existantes du run par sécurité si besoin futur
            # Ici pas nécessaire car run neuf.

            for raw_category in selected_article_types:
                category_key = self._normalize_category_key(raw_category)
                if not category_key:
                    continue

                candidates = self._fetch_candidates_for_category(
                    category_key=category_key,
                    limit=250,
                )

                budget = self._extract_budget_for_category(
                    category_key=category_key,
                    budgets=search_row.get("selected_budgets") or {},
                )

                scored = []
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

                top_rows = scored[:5]
                inserted = self._insert_recommendations(
                    run_id=run_id,
                    category_key=category_key,
                    scored_rows=top_rows,
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
        secondary_categories = self.ARTICLE_TYPE_TO_SECONDARY_CATEGORIES.get(category_key, [])
        if not secondary_categories:
            return []

        collected: List[Dict[str, Any]] = []
        seen: set = set()

        for secondary in secondary_categories:
            try:
                response = (
                    self.client.table("affiliate_products")
                    .select(
                        "merchant_id,product_id,product_name,brand,primary_category,"
                        "secondary_category,product_url,image_url,buy_url,price,currency,"
                        "availability,is_deleted,last_seen_at"
                    )
                    .eq("is_deleted", False)
                    .eq("primary_category", "Femme")
                    .eq("secondary_category", secondary)
                    .limit(60)
                    .execute()
                )

                rows = response.data or []
                for row in rows:
                    key = f"{row.get('merchant_id')}::{row.get('product_id')}"
                    if key in seen:
                        continue
                    seen.add(key)
                    collected.append(row)
                    if len(collected) >= limit:
                        return collected
            except Exception as e:
                print(f"⚠️ Erreur fetch catégorie {secondary}: {e}")

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
    ) -> int:
        inserted = 0

        for idx, row in enumerate(scored_rows, start=1):
            payload = {
                "id": str(uuid.uuid4()),
                "run_id": run_id,
                "merchant_id": int(row["merchant_id"]),
                "product_id": str(row["product_id"]),
                "category_key": category_key,
                "rank": idx,
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
            inserted += 1

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
        price = self._safe_float(product.get("price"))
        currency = self._normalize_currency(product.get("currency"))
        image_url = (product.get("image_url") or "").strip()
        buy_url = (product.get("buy_url") or "").strip()
        product_url = (product.get("product_url") or "").strip()
        merchant_id = product.get("merchant_id")
        product_id = product.get("product_id")

        if not merchant_id or not product_id or not title:
            return None

        extracted_color = self._extract_color_from_title(title)

        color_score, color_reason = self._compute_color_score(extracted_color, ai_profile)
        style_score, style_reason = self._compute_style_score(title, secondary_category, search_row, ai_profile)
        morphology_score, morphology_reason = self._compute_morphology_score(title, secondary_category, ai_profile)
        budget_score, budget_reason = self._compute_budget_score(price, budget)
        brand_score, brand_reason = self._compute_brand_score(brand, ai_profile)
        category_score = 10

        total_score = color_score + style_score + morphology_score + budget_score + brand_score + category_score

        reasons_json = {
            "color": color_reason,
            "style": style_reason,
            "morphology": morphology_reason,
            "budget": budget_reason,
            "brand": brand_reason,
            "category": f"Produit retenu dans la catégorie {category_key}",
            "extracted_color": extracted_color,
            "secondary_category": secondary_category,
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
            return 30, f"Couleur très favorable pour ce profil: {extracted_color}"
        if c in ok:
            return 10, f"Couleur acceptable pour ce profil: {extracted_color}"

        return 0, f"Couleur neutre/non reconnue: {extracted_color}"

    def _compute_style_score(
        self,
        title: str,
        secondary_category: str,
        search_row: Dict[str, Any],
        ai_profile: Dict[str, Any],
    ) -> Tuple[float, str]:
        hay = self._normalize_text(f"{title} {secondary_category}")
        requested_styles = [self._normalize_text(x) for x in (search_row.get("selected_styles") or []) if x]
        profile_styles = [self._normalize_text(x) for x in (ai_profile.get("style_keywords") or []) if x]

        matched_tokens: List[str] = []
        score = 0

        for style in requested_styles + profile_styles:
            hints = self.STYLE_HINTS.get(style, [])
            for hint in hints:
                if self._normalize_text(hint) in hay:
                    matched_tokens.append(f"{style}:{hint}")
                    score += 8
                    break

        score = min(score, 20)

        if matched_tokens:
            return score, f"Match style via: {', '.join(matched_tokens[:3])}"

        return 0, "Aucun indice de style clair détecté"

    def _compute_morphology_score(
        self,
        title: str,
        secondary_category: str,
        ai_profile: Dict[str, Any],
    ) -> Tuple[float, str]:
        hay = self._normalize_text(f"{title} {secondary_category}")

        recommended = self._extract_string_list(ai_profile.get("cuts_recommended"))
        avoided = self._extract_string_list(ai_profile.get("cuts_avoid"))

        positive_matches = [cut for cut in recommended if self._token_match(cut, hay)]
        negative_matches = [cut for cut in avoided if self._token_match(cut, hay)]

        if negative_matches:
            return -15, f"Coupe plutôt déconseillée: {negative_matches[0]}"
        if positive_matches:
            return 15, f"Coupe compatible avec la morphologie: {positive_matches[0]}"

        return 0, "Pas d’indice morphologique explicite détecté"

    def _compute_budget_score(self, price: Optional[float], budget: Optional[float]) -> Tuple[float, str]:
        if price is None:
            return 0, "Prix absent"
        if budget is None:
            return 0, "Budget non défini pour cette catégorie"
        if price <= budget:
            return 20, f"Dans le budget ({price} <= {budget})"
        return -30, f"Hors budget ({price} > {budget})"

    def _compute_brand_score(self, brand: str, ai_profile: Dict[str, Any]) -> Tuple[float, str]:
        preferred = [self._normalize_text(x) for x in (ai_profile.get("preferred_brands") or []) if x]
        b = self._normalize_text(brand)

        for p in preferred:
            if p and p in b:
                return 15, f"Marque préférée détectée: {brand}"

        return 0, "Marque non préférée"

    # =========================
    # Helpers
    # =========================
    def _normalize_category_key(self, raw: str) -> Optional[str]:
        if not raw:
            return None

        key = self._normalize_text(raw).replace(" ", "_")

        aliases = {
            "hauts": "hauts",
            "haut": "hauts",
            "bas": "bas",
            "robes": "robes",
            "robe": "robes",
            "chaussures": "chaussures",
            "accessoires": "accessoires",
            "sacs": "sacs",
            "bijoux": "bijoux",
            "tenue_complete": None,

            # IMPORTANT: alignement avec la contrainte DB
            "vestes_&_manteaux": "vestes",
            "vestes_manteaux": "vestes",
            "vestes_et_manteaux": "vestes",
            "vestes": "vestes",

            "sous-vetements": "lingerie",
            "sous_vetements": "lingerie",
            "lingerie": "lingerie",

            "maillots_de_bain": "maillots_bain",
            "maillots_bain": "maillots_bain",

            "vetements_de_sport": "tenue_sport",
            "vetements_sport": "tenue_sport",
            "tenue_sport": "tenue_sport",
        }

        return aliases.get(key, key if key in self.ARTICLE_TYPE_TO_SECONDARY_CATEGORIES else None)

    def _extract_budget_for_category(self, category_key: str, budgets: Dict[str, Any]) -> Optional[float]:
        if not budgets:
            return None

        candidates = [
            category_key,
            category_key.replace("_", " "),
            category_key.replace("_", "-"),
        ]

        if category_key == "vestes_manteaux":
            candidates += ["vestes & manteaux", "vestes_manteaux", "vestes et manteaux"]
        elif category_key == "maillots_bain":
            candidates += ["maillots de bain", "maillots_bain"]
        elif category_key == "vetements_sport":
            candidates += ["vêtements de sport", "vetements_sport"]
        elif category_key == "sous-vetements":
            candidates += ["sous-vêtements", "sous-vetements"]

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
                return color
        return None

    def _extract_profile_color_names(self, value: Any) -> List[str]:
        rows = self._ensure_list(value)
        out = []
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
        out = []
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
        # ta table affiliate_products a parfois currency/availability inversés
        # on force EUR par défaut
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


search_recommendation_service = SearchRecommendationService()