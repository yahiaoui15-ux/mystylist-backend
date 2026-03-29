import re
import unicodedata
from collections import defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple
from datetime import datetime, timezone
from app.utils.supabase_client import supabase


class WardrobeSuggestionsService:
    """
    Génère des suggestions de produits affiliés complémentaires
    autour d'un vêtement central de la garde-robe utilisateur.

    Nouvelle logique :
    - source de vérité style = affiliate_product_enrichment (style_v6)
    - hydratation produit via affiliate_products
    - scope MVP strict : hauts / bas / robes / vestes / chaussures
    - scoring basé sur cohérence tenue réelle
    """

    CATEGORY_LABELS = {
        "hauts": "Hauts",
        "bas": "Bas",
        "robes": "Robes",
        "vestes": "Vestes",
        "chaussures": "Chaussures",
    }

    COMPLEMENTARY_CATEGORY_MAP = {
        "hauts": ["bas", "vestes", "chaussures"],
        "bas": ["hauts", "vestes", "chaussures"],
        "robes": ["vestes", "chaussures"],
        "vestes": ["hauts", "bas", "chaussures"],
        "chaussures": ["hauts", "bas", "robes", "vestes"],
    }

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

    CATEGORY_SUBTYPE_HINTS = {
        "hauts": {
            "chemise": ["chemise"],
            "blouse": ["blouse"],
            "pull": ["pull", "maille"],
            "gilet": ["gilet", "cardigan"],
            "tee_shirt": ["tee-shirt", "tee shirt", "t-shirt", "t shirt"],
            "top": ["top"],
            "caraco": ["caraco", "camisole", "bretelles fines", "debardeur", "débardeur"],
        },
        "bas": {
            "pantalon": ["pantalon", "tailleur"],
            "jean": ["jean", "denim"],
            "jupe": ["jupe"],
            "short": ["short", "bermuda"],
        },
        "robes": {
            "robe": ["robe"],
            "combinaison": ["combinaison", "jumpsuit"],
        },
        "vestes": {
            "blazer": ["blazer", "tailleur"],
            "veste": ["veste", "blouson"],
            "manteau": ["manteau", "trench"],
            "doudoune": ["doudoune", "matelassee", "matelassée", "puffer"],
            "sans_manches": ["sans manches"],
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
            "chic": 34,
            "classique": 26,
            "minimaliste": 18,
            "moderne": 12,
            "romantique": 8,
            "vintage": 3,
            "rock": -4,
            "boheme": -10,
            "casual": -14,
            "sportswear": -24,
        },
        "classique": {
            "classique": 34,
            "chic": 22,
            "minimaliste": 18,
            "moderne": 8,
            "casual": 4,
            "vintage": 4,
            "romantique": 2,
            "rock": -8,
            "boheme": -10,
            "sportswear": -18,
        },
        "casual": {
            "casual": 30,
            "sportswear": 14,
            "classique": 8,
            "minimaliste": 5,
            "moderne": 5,
            "rock": 4,
            "boheme": 2,
            "romantique": 0,
            "vintage": 0,
            "chic": -6,
        },
        "sportswear": {
            "sportswear": 32,
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
            "boheme": 30,
            "romantique": 16,
            "vintage": 8,
            "chic": 4,
            "casual": 2,
            "classique": -4,
            "minimaliste": -8,
            "moderne": -8,
            "rock": -6,
            "sportswear": -16,
        },
        "romantique": {
            "romantique": 30,
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
            "rock": 30,
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
            "minimaliste": 30,
            "classique": 22,
            "chic": 18,
            "moderne": 14,
            "casual": 6,
            "romantique": -2,
            "boheme": -10,
            "rock": -4,
            "sportswear": -8,
            "vintage": -4,
        },
        "moderne": {
            "moderne": 30,
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
            "vintage": 30,
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

    NEUTRAL_COLORS = {
        "noir", "blanc", "ecru", "beige", "camel", "gris", "marine", "marron"
    }

    COLOR_WORDS = [
        "noir", "blanc", "ecru", "beige", "camel", "marron", "gris",
        "bleu", "marine", "vert", "kaki", "rouge", "rose", "violet",
        "jaune", "orange", "dore", "argente", "multicolore"
    ]

    CATEGORY_FIT_SCORES = {
        "hauts": {"bas": 34, "vestes": 18, "chaussures": 16},
        "bas": {"hauts": 34, "vestes": 18, "chaussures": 16},
        "robes": {"vestes": 22, "chaussures": 22},
        "vestes": {"hauts": 16, "bas": 18, "chaussures": 12},
        "chaussures": {"hauts": 10, "bas": 10, "robes": 12, "vestes": 8},
    }

    FORBIDDEN_CATEGORY_TARGETS = {
        "hauts": {"hauts", "robes"},
        "bas": {"bas", "robes"},
        "robes": {"robes", "hauts", "bas"},
        "vestes": {"vestes", "robes"},
        "chaussures": {"chaussures"},
    }

    WINTER_HINTS = {
        "laine", "maille", "pull", "col roule", "col roulé", "manteau", "doudoune",
        "bottine", "boots", "velours", "cachemire", "cardigan", "gilet", "cuir"
    }

    SUMMER_HINTS = {
        "short", "bermuda", "combishort", "debardeur", "débardeur", "sandale",
        "maillot", "lin", "crochet", "bikini", "swimwear", "brassiere", "brassière"
    }

    MIDSEASON_HINTS = {
        "jean", "chemise", "blouse", "veste", "blazer", "mocassin", "ballerine",
        "jupe", "pantalon", "robe"
    }

    HEAVY_TEXTURE_HINTS = {
        "laine", "maille", "velours", "cuir", "manteau", "doudoune", "cachemire", "tweed"
    }

    LIGHT_TEXTURE_HINTS = {
        "lin", "debardeur", "débardeur", "sandale", "maillot", "crochet", "dentelle", "voile"
    }

    PATTERN_NEUTRAL_VALUES = {"", "uni", "plain", "solide", "solid"}
    STRONG_PATTERNS = {
        "floral", "fleuri", "pois", "rayures", "rayure", "animal", "leopard",
        "léopard", "zebre", "zèbre", "carreaux", "check", "imprime", "imprimé",
        "graphic", "graphique"
    }

    OFFICE_NEGATIVE_HINTS = {
        "sequins": ["sequin", "sequins", "paillette", "paillete", "paillettes", "strass", "lamé", "lame"],
        "too_playful_print": ["fleuri", "floral", "imprime", "imprimé", "graphic", "graphique", "carreaux", "check"],
        "too_evening": ["satin", "dos nu", "bustier", "taffetas", "brillant", "brillance"],
        "too_casual_outerwear": ["doudoune", "matelassee", "matelassée", "capuche", "sherpa"],
        "too_loose": ["oversize", "ample", "large"],
        "too_casual_bottoms": ["jean", "denim", "cargo", "jogger", "legging"],
        "too_bold_bottoms": [
            "cuir", "simili", "vinyle", "croco",
            "brode", "brodé", "dentelle",
            "tulle", "filet", "délavé", "delave",
            "washed", "jacquard", "python"
        ],
    }

    OFFICE_POSITIVE_HINTS = {
        "smart_tops": ["chemise", "blouse", "col bateau", "maille fine"],
        "smart_bottoms": ["pantalon", "jupe midi", "jupe", "taille haute", "cigarette", "droit", "plis"],
        "smart_outerwear": ["blazer", "trench", "manteau"],
        "smart_shoes": ["mocassin", "escarpin", "derby", "ballerine"],
    }

    LIGHT_SHOE_HINTS = {
        "sandale", "escarpin", "ballerine", "mocassin", "slingback", "babies"
    }

    HEAVY_SHOE_HINTS = {
        "botte", "boots", "boot", "fourree", "fourré", "fourrure", "moon boot",
        "apres ski", "après ski", "pluie", "rain", "sherpa", "neige"
    }

    STATEMENT_HINTS = {
        "leopard", "léopard", "python", "zebre", "zèbre", "animal",
        "sequins", "paillette", "paillettes", "strass",
        "patchwork", "multicolore", "metal", "métal",
        "verni", "vinyle", "croco", "jacquard",
        "brode", "brodé", "dentelle", "transparence", "transparent"
    }

    SOFT_STATEMENT_HINTS = {
        "brode", "brodé", "dentelle", "fleuri", "floral"
    }

    CATEGORY_ROLE_WEIGHTS = {
        "hauts": {"should_be_quiet_if_central_is_strong": 12},
        "bas": {"should_be_quiet_if_central_is_strong": 12},
        "vestes": {"should_be_quiet_if_central_is_strong": 14},
        "chaussures": {"should_be_quiet_if_central_is_strong": 10},
    }

    SUMMER_CENTRAL_CATEGORIES = {"robes"}
    def __init__(self):
        self.supabase = supabase
        self.client = supabase.get_client()

    async def generate_for_item(self, item_id: str) -> Dict[str, Any]:
        item = self._get_wardrobe_item(item_id)
        if not item:
            raise ValueError(f"wardrobe_item introuvable: {item_id}")

        if item.get("status") != "completed":
            raise ValueError("Le vêtement n'est pas encore analysé")

        user_id = item.get("user_id")
        if not user_id:
            raise ValueError("user_id manquant sur wardrobe_item")

        ai_profile = self._get_ai_profile(user_id)
        if not ai_profile:
            raise ValueError(f"user_ai_profiles introuvable pour user_id={user_id}")

        central_category = self._normalize_text(str(item.get("category_key") or ""))
        if central_category not in self.COMPLEMENTARY_CATEGORY_MAP:
            return {
                "ok": True,
                "item_id": item_id,
                "central_item": self._build_central_item_payload(item),
                "suggestions_by_category": [],
            }

        target_categories = self.COMPLEMENTARY_CATEGORY_MAP.get(central_category, [])
        if not target_categories:
            return {
                "ok": True,
                "item_id": item_id,
                "central_item": self._build_central_item_payload(item),
                "suggestions_by_category": [],
            }

        inserted_product_keys: Set[str] = set()
        inserted_family_keys: Set[str] = set()
        inserted_url_keys: Set[str] = set()
        brand_counter: Dict[str, int] = {}

        suggestions_by_category = []

        for category_key in target_categories:
            candidates = self._fetch_candidates_for_category(category_key=category_key, limit=260)

            scored: List[Dict[str, Any]] = []
            for row in candidates:
                scored_row = self._score_product_for_wardrobe(
                    product=row,
                    category_key=category_key,
                    wardrobe_item=item,
                    ai_profile=ai_profile,
                    brand_counter=brand_counter,
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

            selected_rows = self._dedupe_scored_rows(
                scored_rows=scored,
                inserted_product_keys=inserted_product_keys,
                inserted_family_keys=inserted_family_keys,
                inserted_url_keys=inserted_url_keys,
                brand_counter=brand_counter,
                limit=8,
            )

            suggestions_by_category.append({
                "category_key": category_key,
                "category_label": self.CATEGORY_LABELS.get(category_key, category_key),
                "items": [
                    {
                        "id": f"{row['merchant_id']}_{row['product_id']}",
                        "product_id": str(row["product_id"]),
                        "title": row["title"],
                        "brand": row["brand"],
                        "image_url": row["image_url"],
                        "price": row["price"],
                        "currency": row["currency"],
                        "buy_url": row["buy_url"],
                        "product_url": row["product_url"],
                        "score_total": row["score_total"],
                        "reason": row["reason"],
                    }
                    for row in selected_rows
                ]
            })

        suggestions_by_category = [
            group for group in suggestions_by_category if group["items"]
        ]

        final_payload = {
            "ok": True,
            "item_id": item_id,
            "central_item": self._build_central_item_payload(item),
            "suggestions_by_category": suggestions_by_category,
        }

        self._save_generated_suggestions(
            item_id=item_id,
            user_id=user_id,
            central_item=final_payload["central_item"],
            suggestions_by_category=suggestions_by_category,
        )

        return final_payload

    def _save_generated_suggestions(
        self,
        item_id: str,
        user_id: str,
        central_item: Dict[str, Any],
        suggestions_by_category: List[Dict[str, Any]],
    ) -> None:
        now_iso = datetime.now(timezone.utc).isoformat()

        payload = {
            "wardrobe_item_id": item_id,
            "user_id": user_id,
            "central_item": central_item,
            "suggestions_by_category": suggestions_by_category,
            "algorithm_version": "v1",
            "refresh_count": 0,
            "generated_at": now_iso,
            "updated_at": now_iso,
        }

        self.client.table("wardrobe_suggestions_cache").upsert(
            payload,
            on_conflict="wardrobe_item_id"
        ).execute()

    # =========================
    # Fetch data
    # =========================
    def _get_wardrobe_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        response = self.supabase.query(
            "wardrobe_items",
            select_fields="*",
            filters={"id": item_id},
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

        enrichment_rows = self._fetch_enrichment_rows_for_category(
            category_key=category_key,
            allowed_secondaries=allowed_secondaries,
            limit=max(limit * 2, 250),
        )
        if not enrichment_rows:
            return []

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

            if not self._has_usable_image(p):
                continue

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
                        if not self._has_usable_image(row):
                            continue

                        key = f"{row.get('merchant_id')}::{row.get('product_id')}"
                        if key in seen:
                            continue
                        seen.add(key)
                        collected.append(row)

                except Exception as e:
                    print(f"⚠️ Erreur fetch affiliate_products merchant={merchant_id}: {e}")

        return collected

    # =========================
    # Scoring
    # =========================
    def _score_product_for_wardrobe(
        self,
        product: Dict[str, Any],
        category_key: str,
        wardrobe_item: Dict[str, Any],
        ai_profile: Dict[str, Any],
        brand_counter: Dict[str, int],
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
        if not self._has_usable_image(product):
            return None
        buy_url = (product.get("buy_url") or "").strip()
        product_url = (product.get("product_url") or "").strip()
        merchant_id = product.get("merchant_id")
        product_id = product.get("product_id")

        if not merchant_id or not product_id or not title:
            return None

        extracted_color = self._extract_color_from_title(title)
        subtype = self._infer_subtype(category_key, title, secondary_category)

        category_fit_score, category_fit_reason = self._compute_category_fit_score(
            central_category=str(wardrobe_item.get("category_key") or ""),
            target_category=category_key,
        )
        if category_fit_score <= -900:
            return None

        seasonality_score, seasonality_reason = self._compute_seasonality_score(
            wardrobe_item=wardrobe_item,
            title=title,
            secondary_category=secondary_category,
            source_description=source_description,
        )

        texture_score, texture_reason = self._compute_texture_weight_score(
            wardrobe_item=wardrobe_item,
            title=title,
            secondary_category=secondary_category,
            source_description=source_description,
        )

        color_score, color_reason = self._compute_wardrobe_color_score(
            extracted_color=extracted_color,
            wardrobe_item=wardrobe_item,
            ai_profile=ai_profile,
        )

        style_score, style_reason = self._compute_style_score(
            style_primary=style_primary,
            style_tags=style_tags,
            style_scores_json=style_scores_json,
            confidence_score=confidence_score,
            category_key=category_key,
            subtype=subtype,
            wardrobe_item=wardrobe_item,
            ai_profile=ai_profile,
        )

        morphology_score, morphology_reason = self._compute_morphology_score(
            title=title,
            secondary_category=secondary_category,
            source_description=source_description,
            ai_profile=ai_profile,
        )

        pattern_score, pattern_reason = self._compute_pattern_harmony_score(
            category_key=category_key,
            title=title,
            secondary_category=secondary_category,
            source_description=source_description,
            wardrobe_item=wardrobe_item,
        )

        visual_balance_score, visual_balance_reason = self._compute_visual_balance_score(
            category_key=category_key,
            title=title,
            secondary_category=secondary_category,
            source_description=source_description,
            subtype=subtype,
            wardrobe_item=wardrobe_item,
        )

        office_score, office_reason = self._compute_office_context_score(
            category_key=category_key,
            title=title,
            secondary_category=secondary_category,
            source_description=source_description,
            subtype=subtype,
            wardrobe_item=wardrobe_item,
        )

        shoe_score, shoe_reason = self._compute_shoe_seasonality_score(
            category_key=category_key,
            subtype=subtype,
            title=title,
            secondary_category=secondary_category,
            source_description=source_description,
            wardrobe_item=wardrobe_item,
        )

        statement_score, statement_reason = self._compute_statement_balance_score(
            category_key=category_key,
            title=title,
            secondary_category=secondary_category,
            source_description=source_description,
            wardrobe_item=wardrobe_item,
        )

        stylist_brain_score, stylist_brain_reason = self._compute_stylist_brain_score(
            category_key=category_key,
            title=title,
            secondary_category=secondary_category,
            source_description=source_description,
            subtype=subtype,
            wardrobe_item=wardrobe_item,
        )

        brand_score, brand_reason = self._compute_brand_score(brand, ai_profile)

        diversity_penalty, diversity_reason = self._compute_diversity_penalty(
            brand=brand,
            brand_counter=brand_counter,
        )

        total_score = (
            category_fit_score
            + seasonality_score
            + texture_score
            + color_score
            + style_score
            + morphology_score
            + pattern_score
            + visual_balance_score
            + office_score
            + shoe_score
            + brand_score
            + diversity_penalty
            + statement_score
            + stylist_brain_score
        )

        reasons = [
            category_fit_reason,
            style_reason,
            pattern_reason,
            visual_balance_reason,
            office_reason,
            color_reason,
            seasonality_reason,
            texture_reason,
            morphology_reason,
            brand_reason,
            diversity_reason,
            shoe_reason,
            statement_reason,
            stylist_brain_reason,
        ]
        reason = self._pick_best_reason(reasons)

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
            "reason": reason,
            "score_color": color_score,
            "score_style": style_score,
            "score_morphology": morphology_score,
            "score_category_fit": category_fit_score,
            "score_seasonality": seasonality_score,
            "score_texture": texture_score,
            "score_pattern": pattern_score,
            "score_visual_balance": visual_balance_score,
            "score_office": office_score,
            "score_shoe": shoe_score,
            "score_statement": statement_score,
            "score_stylist_brain": stylist_brain_score,
            "score_brand": brand_score,
            "score_diversity_penalty": diversity_penalty,
        }

    def _compute_wardrobe_color_score(
        self,
        extracted_color: Optional[str],
        wardrobe_item: Dict[str, Any],
        ai_profile: Dict[str, Any],
    ) -> Tuple[float, str]:
        dominant = self._normalize_text(str(
            wardrobe_item.get("dominant_color") or wardrobe_item.get("detected_color") or ""
        ))
        secondary_colors = self._extract_color_names_from_json_list(wardrobe_item.get("secondary_colors"))
        accent_colors = self._extract_color_names_from_json_list(wardrobe_item.get("accent_colors"))

        best = self._extract_profile_color_names(ai_profile.get("colors_best"))
        ok = self._extract_profile_color_names(ai_profile.get("colors_ok"))
        avoid = self._extract_profile_color_names(ai_profile.get("colors_avoid"))

        if not extracted_color:
            return 4, "Couleur non détectée, score neutre"

        c = self._normalize_text(extracted_color)

        if c in avoid:
            return -35, f"Couleur peu favorable pour votre palette : {extracted_color}"

        if c in secondary_colors:
            if c in best:
                return 24, "Rappel élégant d’une couleur du vêtement central"
            return 18, "Rappel harmonieux d’une couleur du vêtement central"

        if c in accent_colors:
            if c in best:
                return 18, "Belle reprise d’une couleur d’accent"
            return 12, "Reprise d’une couleur d’accent du vêtement central"

        if dominant and c == dominant:
            if c in best:
                return 22, "Ton sur ton cohérent avec le vêtement central"
            return 15, "Ton sur ton cohérent avec le vêtement central"

        if c in self.NEUTRAL_COLORS:
            if c in best:
                return 28, "Neutre chic qui équilibre bien le vêtement central"
            if c in ok:
                return 22, "Neutre équilibrant pour accompagner le vêtement central"
            return 20, "Neutre facile à associer au vêtement central"

        if c in best:
            return 20, "Couleur très favorable pour votre palette"
        if c in ok:
            return 10, "Couleur compatible avec votre palette"

        return 0, "Couleur sans lien fort détecté avec le vêtement central"

    def _compute_style_score(
        self,
        style_primary: str,
        style_tags: List[str],
        style_scores_json: Dict[str, Any],
        confidence_score: float,
        category_key: str,
        subtype: str,
        wardrobe_item: Dict[str, Any],
        ai_profile: Dict[str, Any],
    ) -> Tuple[float, str]:
        wardrobe_style = self._normalize_text(str(wardrobe_item.get("detected_style") or ""))
        profile_styles = [self._normalize_text(x) for x in (ai_profile.get("style_keywords") or []) if x]

        target_styles: List[str] = []
        if wardrobe_style:
            target_styles.append(wardrobe_style)
        for style in profile_styles:
            if style and style not in target_styles:
                target_styles.append(style)

        if not target_styles:
            if style_primary:
                return round(min(max(confidence_score, 0.0), 1.0) * 6, 2), f"Style V6 détecté: {style_primary}"
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
                score += min(raw_style_score * 2.2, 10)

        confidence_bonus = min(max(confidence_score, 0.0), 1.0) * 10.0
        score += confidence_bonus
        reasons.append(f"conf:{round(confidence_bonus, 1)}")

        # Ajustements spécifiques tenue
        if wardrobe_style in {"chic", "classique", "minimaliste"}:
            if category_key == "chaussures" and subtype == "baskets":
                score -= 16
            if category_key == "vestes" and subtype == "doudoune":
                score -= 18
            if category_key == "hauts" and subtype in {"tee_shirt", "caraco"}:
                score -= 10
            if category_key == "bas" and subtype == "jean":
                score -= 16

        reason = " / ".join(reasons[:4]) if reasons else f"Style V6 principal: {style_primary or 'n/a'}"
        return round(score, 2), reason

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
            return -12, "Coupe moins favorable pour votre morphologie"
        if positive_matches:
            return 12, "Coupe bien adaptée à votre morphologie"

        return 0, "Pas d’indice morphologique explicite détecté"

    def _compute_brand_score(self, brand: str, ai_profile: Dict[str, Any]) -> Tuple[float, str]:
        preferred = [self._normalize_text(x) for x in (ai_profile.get("preferred_brands") or []) if x]
        b = self._normalize_text(brand)

        for p in preferred:
            if p and p in b:
                return 10, "Marque appréciée"

        return 0, "Marque non préférée"

    def _compute_category_fit_score(self, central_category: str, target_category: str) -> Tuple[float, str]:
        central = self._normalize_text(central_category)
        target = self._normalize_text(target_category)

        forbidden = self.FORBIDDEN_CATEGORY_TARGETS.get(central, set())
        if target in forbidden:
            return -999, "Catégorie non pertinente avec le vêtement central"

        score = self.CATEGORY_FIT_SCORES.get(central, {}).get(target, 0)
        if score > 0:
            return score, "Catégorie complémentaire cohérente pour construire la tenue"

        return 0, "Compatibilité de catégorie neutre"

    def _compute_seasonality_score(
        self,
        wardrobe_item: Dict[str, Any],
        title: str,
        secondary_category: str,
        source_description: str,
    ) -> Tuple[float, str]:
        central_season = self._normalize_text(str(wardrobe_item.get("detected_season") or ""))
        central_hay = self._normalize_text(
            f"{wardrobe_item.get('ai_label') or ''} "
            f"{wardrobe_item.get('subcategory') or ''} "
            f"{wardrobe_item.get('detected_material') or ''}"
        )
        product_hay = self._normalize_text(f"{title} {secondary_category} {source_description}")

        product_is_winter = self._contains_any(product_hay, self.WINTER_HINTS)
        product_is_summer = self._contains_any(product_hay, self.SUMMER_HINTS)
        central_is_winter = central_season == "hiver" or self._contains_any(central_hay, self.WINTER_HINTS)
        central_is_summer = central_season == "ete" or self._contains_any(central_hay, self.SUMMER_HINTS)

        if central_is_winter and product_is_summer:
            return -30, "Article trop estival pour accompagner ce vêtement"
        if central_is_summer and product_is_winter:
            return -26, "Article trop hivernal pour accompagner ce vêtement"

        if central_is_winter and product_is_winter:
            return 16, "Bonne cohérence saisonnière avec le vêtement central"
        if central_is_summer and product_is_summer:
            return 16, "Bonne cohérence saisonnière avec le vêtement central"

        if central_season in {"printemps", "automne"}:
            if self._contains_any(product_hay, self.MIDSEASON_HINTS):
                return 10, "Bonne cohérence de mi-saison"

        return 0, "Cohérence saisonnière neutre"

    def _compute_texture_weight_score(
        self,
        wardrobe_item: Dict[str, Any],
        title: str,
        secondary_category: str,
        source_description: str,
    ) -> Tuple[float, str]:
        central_hay = self._normalize_text(
            f"{wardrobe_item.get('ai_label') or ''} "
            f"{wardrobe_item.get('subcategory') or ''} "
            f"{wardrobe_item.get('detected_material') or ''}"
        )
        product_hay = self._normalize_text(f"{title} {secondary_category} {source_description}")

        central_heavy = self._contains_any(central_hay, self.HEAVY_TEXTURE_HINTS)
        central_light = self._contains_any(central_hay, self.LIGHT_TEXTURE_HINTS)
        product_heavy = self._contains_any(product_hay, self.HEAVY_TEXTURE_HINTS)
        product_light = self._contains_any(product_hay, self.LIGHT_TEXTURE_HINTS)

        if central_heavy and product_light:
            return -14, "Matière trop légère par rapport au vêtement central"
        if central_light and product_heavy:
            return -12, "Matière visuellement plus lourde que le vêtement central"

        if central_heavy and product_heavy:
            return 10, "Belle cohérence de matière et de structure"
        if central_light and product_light:
            return 10, "Belle cohérence de légèreté"

        return 0, "Cohérence de matière neutre"

    def _compute_pattern_harmony_score(
        self,
        category_key: str,
        title: str,
        secondary_category: str,
        source_description: str,
        wardrobe_item: Dict[str, Any],
    ) -> Tuple[float, str]:
        central_pattern = self._normalize_text(str(wardrobe_item.get("detected_pattern") or ""))
        hay = self._normalize_text(f"{title} {secondary_category} {source_description}")

        product_is_patterned = self._contains_any(hay, self.STRONG_PATTERNS)
        central_is_patterned = bool(central_pattern and central_pattern not in self.PATTERN_NEUTRAL_VALUES)

        if not central_is_patterned and not product_is_patterned:
            return 4, "Sobriété visuelle cohérente"

        if central_is_patterned:
            if not product_is_patterned:
                return 18, "La pièce complémentaire laisse respirer le vêtement central"
            return -22, "Motif sur motif trop chargé"

        if not central_is_patterned and product_is_patterned:
            if category_key in {"vestes", "chaussures"}:
                return -4, "Motif présent mais encore gérable"
            return 2, "Pièce expressive possible"

        return 0, "Compatibilité de motif neutre"

    def _compute_visual_balance_score(
        self,
        category_key: str,
        title: str,
        secondary_category: str,
        source_description: str,
        subtype: str,
        wardrobe_item: Dict[str, Any],
    ) -> Tuple[float, str]:
        central_pattern = self._normalize_text(str(wardrobe_item.get("detected_pattern") or ""))
        central_style = self._normalize_text(str(wardrobe_item.get("detected_style") or ""))
        hay = self._normalize_text(f"{title} {secondary_category} {source_description}")

        score = 0.0
        reasons: List[str] = []

        central_is_patterned = bool(central_pattern and central_pattern not in self.PATTERN_NEUTRAL_VALUES)

        if central_is_patterned and category_key in {"vestes", "chaussures", "hauts", "bas"}:
            if self._contains_any(hay, self.STRONG_PATTERNS):
                score -= 18
                reasons.append("concurrence visuelle avec la pièce centrale")
            else:
                score += 10
                reasons.append("bonne sobriété autour de la pièce centrale")

        if central_style in {"chic", "classique", "minimaliste"}:
            if category_key == "vestes":
                if subtype == "blazer":
                    score += 14
                    reasons.append("veste structurée très cohérente")
                elif subtype == "doudoune":
                    score -= 18
                    reasons.append("outerwear trop casual")
            elif category_key == "chaussures":
                if subtype in {"escarpins", "mocassins", "derbies", "ballerines"}:
                    score += 10
                    reasons.append("chaussure habillée cohérente")
                elif subtype == "baskets":
                    score -= 16
                    reasons.append("basket peu cohérente avec la pièce centrale")
            elif category_key == "bas":
                if subtype == "jean":
                    score -= 12
                    reasons.append("bas trop casual")
            elif category_key == "hauts":
                if subtype in {"chemise", "blouse", "pull"}:
                    score += 6
                    reasons.append("haut équilibré")
                elif subtype in {"tee_shirt", "caraco"}:
                    score -= 10
                    reasons.append("haut trop casual ou trop léger")

        if reasons:
            return round(score, 2), " / ".join(reasons)
        return 0, "Équilibre visuel neutre"

    def _compute_office_context_score(
        self,
        category_key: str,
        title: str,
        secondary_category: str,
        source_description: str,
        subtype: str,
        wardrobe_item: Dict[str, Any],
    ) -> Tuple[float, str]:
        central_style = self._normalize_text(str(wardrobe_item.get("detected_style") or ""))
        if central_style not in {"chic", "classique", "minimaliste"}:
            return 0, "Pas de contexte bureau spécifique"

        hay = self._normalize_text(f"{title} {secondary_category} {source_description}")
        score = 0.0
        reasons: List[str] = []

        if category_key == "hauts":
            if subtype in {"chemise", "blouse"}:
                score += 16
                reasons.append("haut bureau très pertinent")
            elif subtype in {"pull", "gilet", "top"}:
                score += 6
                reasons.append("haut exploitable")
            elif subtype == "tee_shirt":
                score -= 18
                reasons.append("tee-shirt peu bureau")
            elif subtype == "caraco":
                score -= 22
                reasons.append("caraco trop délicat pour bureau")

            if self._contains_any_text(hay, self.OFFICE_NEGATIVE_HINTS["too_loose"]):
                score -= 6
                reasons.append("coupe trop casual")

            if self._contains_any_text(hay, ["chemise", "blouse"]):
                if not self._contains_any_text(hay, ["imprime", "imprimé", "fleuri", "floral", "carreaux", "check"]):
                    score += 6
                    reasons.append("chemise/blouse sobre premium")

        elif category_key == "bas":
            if subtype == "pantalon":
                score += 22
                reasons.append("pantalon bureau très pertinent")
            elif subtype == "jupe":
                score += 8
                reasons.append("jupe bureau pertinente")
            elif subtype == "jean":
                score -= 22
                reasons.append("jean peu bureau")
            elif subtype == "short":
                score -= 26
                reasons.append("short hors cible bureau")

            if self._contains_any_text(hay, self.OFFICE_NEGATIVE_HINTS["too_casual_bottoms"]):
                score -= 18
                reasons.append("bas trop casual")

            if self._contains_any_text(hay, self.OFFICE_NEGATIVE_HINTS["too_bold_bottoms"]):
                score -= 28
                reasons.append("matière ou effet trop mode pour bureau")

            if self._contains_any_text(hay, self.OFFICE_NEGATIVE_HINTS["too_playful_print"]):
                score -= 20
                reasons.append("imprimé trop présent pour bureau")

            if self._contains_any_text(hay, self.OFFICE_POSITIVE_HINTS["smart_bottoms"]):
                score += 12
                reasons.append("bas structuré")

            if self._contains_any_text(hay, ["pantalon cigarette", "pantalon droit"]):
                score += 12
                reasons.append("pantalon bureau premium")
            elif self._contains_any_text(hay, ["jupe midi"]):
                score += 6
                reasons.append("jupe midi acceptable bureau")

            if self._contains_any_text(hay, ["crayon", "midi"]) and self._contains_any_text(hay, ["cuir", "croco", "simili"]):
                score -= 10
                reasons.append("jupe crayon trop marquée")

        elif category_key == "vestes":
            if subtype == "blazer":
                score += 18
                reasons.append("blazer très pertinent")
            elif subtype in {"veste", "manteau"}:
                score += 8
                reasons.append("veste bureau pertinente")
            elif subtype == "doudoune":
                score -= 22
                reasons.append("doudoune trop casual")
            elif subtype == "sans_manches":
                score -= 18
                reasons.append("sans manches peu bureau")

            if self._contains_any_text(hay, self.OFFICE_NEGATIVE_HINTS["too_casual_outerwear"]):
                score -= 18
                reasons.append("outerwear trop casual")

        elif category_key == "chaussures":
            if subtype in {"escarpins", "mocassins", "derbies", "ballerines"}:
                score += 14
                reasons.append("chaussure bureau pertinente")
            elif subtype == "boots":
                score += 2
                reasons.append("boots acceptables si sobres")
            elif subtype == "baskets":
                score -= 22
                reasons.append("basket peu bureau")

        if reasons:
            return round(score, 2), " / ".join(reasons)
        return 0, "Compatibilité bureau neutre"

    def _compute_shoe_seasonality_score(
        self,
        category_key: str,
        subtype: str,
        title: str,
        secondary_category: str,
        source_description: str,
        wardrobe_item: Dict[str, Any],
    ) -> Tuple[float, str]:
        if category_key != "chaussures":
            return 0, "Pas de règle chaussures spécifique"

        hay = self._normalize_text(f"{title} {secondary_category} {source_description}")
        is_summer_central = self._is_summer_central_piece(wardrobe_item)
        central_style = self._normalize_text(str(wardrobe_item.get("detected_style") or ""))

        score = 0.0
        reasons: List[str] = []

        heavy_shoe = subtype == "boots" or self._contains_any_text(hay, list(self.HEAVY_SHOE_HINTS))
        light_shoe = subtype in {"sandales", "escarpins", "ballerines", "mocassins"} or self._contains_any_text(hay, list(self.LIGHT_SHOE_HINTS))

        if is_summer_central:
            if heavy_shoe:
                score -= 28
                reasons.append("chaussure trop hivernale pour une tenue estivale")
            if light_shoe:
                score += 14
                reasons.append("chaussure légère cohérente avec la tenue")

        if central_style in {"chic", "classique", "minimaliste"}:
            if subtype in {"escarpins", "ballerines", "mocassins"}:
                score += 10
                reasons.append("chaussure chic portable")
            elif subtype == "baskets":
                score -= 12
                reasons.append("basket moins élégante")
            elif subtype == "boots" and is_summer_central:
                score -= 8
                reasons.append("boots lourdes pour ce registre")

        if reasons:
            return round(score, 2), " / ".join(reasons)
        return 0, "Compatibilité chaussures neutre"

    def _compute_statement_balance_score(
        self,
        category_key: str,
        title: str,
        secondary_category: str,
        source_description: str,
        wardrobe_item: Dict[str, Any],
    ) -> Tuple[float, str]:
        hay = self._normalize_text(f"{title} {secondary_category} {source_description}")
        central_is_statement = self._central_piece_is_statement(wardrobe_item)

        product_is_statement = self._contains_any_text(hay, list(self.STATEMENT_HINTS))
        product_is_soft_statement = self._contains_any_text(hay, list(self.SOFT_STATEMENT_HINTS))

        if not central_is_statement and not product_is_statement:
            return 4, "Bonne sobriété d’ensemble"

        if central_is_statement:
            if product_is_statement:
                return -22, "Deux pièces fortes entrent en concurrence"
            if product_is_soft_statement:
                return -8, "Pièce encore un peu expressive"
            return 14, "La pièce complémentaire laisse la vedette au vêtement central"

        if not central_is_statement and product_is_statement:
            if category_key in {"vestes", "hauts"}:
                return -6, "Pièce forte mais encore portable"
            return -2, "Pièce expressive"

        return 0, "Équilibre statement neutre"

    def _compute_stylist_brain_score(
        self,
        category_key: str,
        title: str,
        secondary_category: str,
        source_description: str,
        subtype: str,
        wardrobe_item: Dict[str, Any],
    ) -> Tuple[float, str]:
        hay = self._normalize_text(f"{title} {secondary_category} {source_description}")
        central_is_statement = self._central_piece_is_statement(wardrobe_item)
        central_style = self._normalize_text(str(wardrobe_item.get("detected_style") or ""))

        score = 0.0
        reasons: List[str] = []

        product_is_statement = self._contains_any_text(hay, list(self.STATEMENT_HINTS))
        product_is_patterned = self._contains_any(hay, self.STRONG_PATTERNS)

        if central_is_statement:
            quiet_bonus = self.CATEGORY_ROLE_WEIGHTS.get(category_key, {}).get("should_be_quiet_if_central_is_strong", 0)

            if not product_is_statement and not product_is_patterned:
                score += quiet_bonus
                reasons.append("la pièce complémentaire laisse respirer la tenue")

            if category_key == "vestes" and subtype == "blazer":
                score += 8
                reasons.append("blazer structure bien la silhouette")

            if category_key == "chaussures" and subtype in {"ballerines", "mocassins", "escarpins"}:
                score += 8
                reasons.append("chaussure sobre qui équilibre la tenue")

        else:
            if category_key == "vestes" and subtype == "blazer":
                score += 6
                reasons.append("blazer apporte de la structure")
            if category_key == "bas" and subtype == "pantalon" and central_style in {"chic", "classique", "minimaliste"}:
                score += 8
                reasons.append("pantalon structuré très portable")
            if category_key == "hauts" and subtype in {"chemise", "blouse"} and central_style in {"boheme", "romantique"}:
                score += 6
                reasons.append("haut cohérent avec un registre féminin portable")

        if reasons:
            return round(score, 2), " / ".join(reasons)
        return 0, "Équilibre styliste neutre"

    def _compute_diversity_penalty(self, brand: str, brand_counter: Dict[str, int]) -> Tuple[float, str]:
        b = self._normalize_text(brand)
        count = brand_counter.get(b, 0)

        if count <= 0:
            return 0, "Diversité préservée"
        if count == 1:
            return -4, "Marque déjà présente"
        if count == 2:
            return -10, "Marque déjà très présente"
        return -18, "Marque surreprésentée"

    async def get_saved_suggestions_for_item(self, item_id: str) -> Dict[str, Any]:
        item = self._get_wardrobe_item(item_id)
        if not item:
            raise ValueError(f"wardrobe_item introuvable: {item_id}")

        response = (
            self.client.table("wardrobe_suggestions_cache")
            .select("*")
            .eq("wardrobe_item_id", item_id)
            .limit(1)
            .execute()
        )

        rows = response.data or []
        if not rows:
            return {
                "ok": True,
                "found": False,
                "item_id": item_id,
                "central_item": row.get("central_item") or self._build_central_item_payload(item),
                "suggestions_by_category": [],
            }

        row = rows[0]

        return {
            "ok": True,
            "found": True,
            "item_id": item_id,
            "central_item": self._build_central_item_payload(item),
            "suggestions_by_category": row.get("suggestions_by_category") or [],
            "generated_at": row.get("generated_at"),
            "updated_at": row.get("updated_at"),
        }
   
    # =========================
    # Dedupe
    # =========================
    def _dedupe_scored_rows(
        self,
        scored_rows: List[Dict[str, Any]],
        inserted_product_keys: Set[str],
        inserted_family_keys: Set[str],
        inserted_url_keys: Set[str],
        brand_counter: Dict[str, int],
        limit: int = 8,
    ) -> List[Dict[str, Any]]:
        out = []

        for row in scored_rows:
            if not self._has_usable_image(row):
                continue
            product_key = f"{row['merchant_id']}::{row['product_id']}"
            family_key = self._build_product_family_key(row)
            url_key = self._canonicalize_product_url(row.get("product_url") or row.get("buy_url") or "")

            if product_key in inserted_product_keys:
                continue
            if family_key in inserted_family_keys:
                continue
            if url_key and url_key in inserted_url_keys:
                continue

            brand_key = self._normalize_text(str(row.get("brand") or ""))
            if brand_counter.get(brand_key, 0) >= 2:
                continue

            inserted_product_keys.add(product_key)
            inserted_family_keys.add(family_key)
            if url_key:
                inserted_url_keys.add(url_key)

            out.append(row)
            brand_counter[brand_key] = brand_counter.get(brand_key, 0) + 1

            if len(out) >= limit:
                break

        return out

    # =========================
    # Payload
    # =========================
    def _build_central_item_payload(self, item: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": item.get("id"),
            "image_url": item.get("image_url"),
            "ai_label": item.get("ai_label"),
            "category_key": item.get("category_key"),
            "dominant_color": item.get("dominant_color") or item.get("detected_color"),
            "secondary_colors": item.get("secondary_colors") or [],
            "accent_colors": item.get("accent_colors") or [],
            "detected_pattern": item.get("detected_pattern") or "",
            "detected_style": item.get("detected_style") or "",
            "detected_season": item.get("detected_season") or "",
        }

    # =========================
    # Helpers
    # =========================
    def _contains_any(self, haystack: str, hints: Set[str]) -> bool:
        h = self._normalize_text(haystack)
        return any(self._normalize_text(token) in h for token in hints)

    def _has_usable_image(self, row: Dict[str, Any]) -> bool:
        image_url = (str(row.get("image_url") or "")).strip()
        if not image_url:
            return False

        low = image_url.lower()

        # placeholders / valeurs vides fréquentes
        if low in {"null", "none", "nan", "/placeholder.svg", "placeholder.svg"}:
            return False

        # on ne garde que des urls http(s) plausibles
        if not (low.startswith("http://") or low.startswith("https://")):
            return False

        # évite les urls manifestement cassées
        bad_tokens = [
            "placeholder",
            "undefined",
            "notfound",
            "no-image",
            "no_image",
            "missing",
        ]
        if any(token in low for token in bad_tokens):
            return False

        return True

    def _contains_any_text(self, haystack: str, tokens: List[str]) -> bool:
        h = self._normalize_text(haystack)
        return any(self._normalize_text(token) in h for token in tokens)

    def _pick_best_reason(self, reasons: List[str]) -> str:
        priority_markers = [
            "laisse respirer",
            "sobriete",
            "catégorie complémentaire",
            "categorie complementaire",
            "chaussure habillee",
            "chaussure bureau",
            "veste structuree",
            "blazer",
            "pantalon bureau",
            "rappel elegant",
            "neutre chic",
            "style",
            "coupe",
        ]

        normalized_reasons = [(r, self._normalize_text(r)) for r in reasons if r]

        for marker in priority_markers:
            for original, normalized in normalized_reasons:
                if marker in normalized:
                    return original

        for original, _ in normalized_reasons:
            return original

        return "Produit complémentaire sélectionné pour accompagner votre vêtement"

    def _extract_color_names_from_json_list(self, value: Any) -> List[str]:
        rows = self._ensure_list(value)
        out = []
        for row in rows:
            if isinstance(row, dict):
                name = row.get("name")
                if name:
                    out.append(self._normalize_text(str(name)))
            elif isinstance(row, str):
                out.append(self._normalize_text(row))
        return list(dict.fromkeys([x for x in out if x]))

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

    def _extract_color_from_title(self, title: str) -> Optional[str]:
        hay = self._normalize_text(title)
        for color in self.COLOR_WORDS:
            if self._normalize_text(color) in hay:
                return color
        return None

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
            from urllib.parse import urlparse, urlunparse
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

    def _central_piece_is_statement(self, wardrobe_item: Dict[str, Any]) -> bool:
        pattern = self._normalize_text(str(wardrobe_item.get("detected_pattern") or ""))
        style = self._normalize_text(str(wardrobe_item.get("detected_style") or ""))
        material = self._normalize_text(str(wardrobe_item.get("detected_material") or ""))
        label = self._normalize_text(str(wardrobe_item.get("ai_label") or ""))
        subcategory = self._normalize_text(str(wardrobe_item.get("subcategory") or ""))

        hay = f"{pattern} {style} {material} {label} {subcategory}"

        if pattern and pattern not in self.PATTERN_NEUTRAL_VALUES:
            return True

        if self._contains_any_text(hay, list(self.STATEMENT_HINTS)):
            return True

        return False

    def _is_summer_central_piece(self, wardrobe_item: Dict[str, Any]) -> bool:
        category_key = self._normalize_text(str(wardrobe_item.get("category_key") or ""))
        season = self._normalize_text(str(wardrobe_item.get("detected_season") or ""))
        material = self._normalize_text(str(wardrobe_item.get("detected_material") or ""))
        subcategory = self._normalize_text(str(wardrobe_item.get("subcategory") or ""))
        label = self._normalize_text(str(wardrobe_item.get("ai_label") or ""))

        hay = f"{category_key} {season} {material} {subcategory} {label}"

        if season == "ete":
            return True
        if category_key in self.SUMMER_CENTRAL_CATEGORIES:
            return True
        if self._contains_any_text(hay, ["ete", "été", "sandale", "lin", "leger", "léger", "sans manches"]):
            return True

        return False

    def _infer_subtype(self, category_key: str, title: str, secondary_category: str) -> str:
        hay = self._normalize_text(f"{title} {secondary_category}")
        rules = self.CATEGORY_SUBTYPE_HINTS.get(category_key, {})

        for subtype, tokens in rules.items():
            for token in tokens:
                if self._normalize_text(token) in hay:
                    return subtype

        return "other"


wardrobe_suggestions_service = WardrobeSuggestionsService()