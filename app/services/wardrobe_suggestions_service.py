import re
import unicodedata
from typing import Any, Dict, List, Optional, Tuple

from app.utils.supabase_client import supabase


class WardrobeSuggestionsService:
    """
    Génère des suggestions de produits affiliés complémentaires
    autour d'un vêtement central de la garde-robe utilisateur.
    """

    CATEGORY_LABELS = {
        "hauts": "Hauts",
        "bas": "Bas",
        "robes": "Robes",
        "vestes": "Vestes",
        "chaussures": "Chaussures",
        "sacs": "Sacs",
        "bijoux": "Bijoux",
        "maillots_bain": "Maillots de bain",
        "lingerie": "Lingerie",
        "accessoires": "Accessoires",
        "tenue_sport": "Tenue sport",
    }

    COMPLEMENTARY_CATEGORY_MAP = {
        "hauts": ["bas", "vestes", "chaussures", "sacs", "accessoires"],
        "bas": ["hauts", "vestes", "chaussures", "sacs", "accessoires"],
        "robes": ["vestes", "chaussures", "sacs", "accessoires"],
        "vestes": ["hauts", "bas", "chaussures", "sacs"],
        "chaussures": ["hauts", "bas", "robes", "sacs"],
        "sacs": ["hauts", "bas", "robes", "chaussures"],
        "bijoux": ["hauts", "bas", "robes", "chaussures"],
        "accessoires": ["hauts", "bas", "robes", "chaussures"],
        "maillots_bain": ["accessoires", "sacs"],
        "lingerie": ["accessoires"],
        "tenue_sport": ["chaussures", "accessoires"],
    }

    ARTICLE_TYPE_TO_SECONDARY_CATEGORIES = {
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
        "vestes": [
            "Vêtements~~Veste & Blouson",
            "Vêtements~~Manteau",
            "Vêtements~~Gilet",
            "Clothing~~Outerwear",
            "Clothing~~Outerwear~~Coats & Jackets",
        ],
        "lingerie": [
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
        "tenue_sport": [
            "Sport~~Legging",
            "Sport~~Tee-shirts & Débardeurs",
            "Sport~~Brassières",
            "Clothing~~Activewear",
        ],
        "bijoux": [
            "Accessoires~~Bijoux",
        ],
    }

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

    NEUTRAL_COLORS = {
        "noir", "blanc", "ecru", "beige", "camel", "gris", "marine", "marron"
    }

    COLOR_WORDS = [
        "noir", "blanc", "ecru", "beige", "camel", "marron", "gris",
        "bleu", "marine", "vert", "kaki", "rouge", "rose", "violet",
        "jaune", "orange", "dore", "argente", "multicolore"
    ]

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

        central_category = item.get("category_key")
        if not central_category:
            raise ValueError("category_key manquant sur wardrobe_item")

        target_categories = self.COMPLEMENTARY_CATEGORY_MAP.get(central_category, [])
        if not target_categories:
            return {
                "ok": True,
                "item_id": item_id,
                "central_item": self._build_central_item_payload(item),
                "suggestions_by_category": [],
            }

        inserted_product_keys = set()
        inserted_family_keys = set()
        inserted_url_keys = set()

        suggestions_by_category = []

        for category_key in target_categories:
            candidates = self._fetch_candidates_for_category(category_key=category_key, limit=250)

            scored = []
            for row in candidates:
                scored_row = self._score_product_for_wardrobe(
                    product=row,
                    category_key=category_key,
                    wardrobe_item=item,
                    ai_profile=ai_profile,
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

        return {
            "ok": True,
            "item_id": item_id,
            "central_item": self._build_central_item_payload(item),
            "suggestions_by_category": suggestions_by_category,
        }

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
    # Scoring
    # =========================
    def _score_product_for_wardrobe(
        self,
        product: Dict[str, Any],
        category_key: str,
        wardrobe_item: Dict[str, Any],
        ai_profile: Dict[str, Any],
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

        color_score, color_reason = self._compute_wardrobe_color_score(
            extracted_color=extracted_color,
            wardrobe_item=wardrobe_item,
            ai_profile=ai_profile,
        )
        style_score, style_reason = self._compute_style_score(
            title=title,
            secondary_category=secondary_category,
            wardrobe_item=wardrobe_item,
            ai_profile=ai_profile,
        )
        morphology_score, morphology_reason = self._compute_morphology_score(
            title=title,
            secondary_category=secondary_category,
            ai_profile=ai_profile,
        )
        brand_score, brand_reason = self._compute_brand_score(brand, ai_profile)

        category_score = 15
        total_score = color_score + style_score + morphology_score + brand_score + category_score

        reasons = [
            color_reason,
            style_reason,
            morphology_reason,
            brand_reason,
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
        }

    def _compute_wardrobe_color_score(
        self,
        extracted_color: Optional[str],
        wardrobe_item: Dict[str, Any],
        ai_profile: Dict[str, Any],
    ) -> Tuple[float, str]:
        dominant = self._normalize_text(str(wardrobe_item.get("dominant_color") or wardrobe_item.get("detected_color") or ""))
        secondary_colors = self._extract_color_names_from_json_list(wardrobe_item.get("secondary_colors"))
        accent_colors = self._extract_color_names_from_json_list(wardrobe_item.get("accent_colors"))

        best = self._extract_profile_color_names(ai_profile.get("colors_best"))
        ok = self._extract_profile_color_names(ai_profile.get("colors_ok"))
        avoid = self._extract_profile_color_names(ai_profile.get("colors_avoid"))

        if not extracted_color:
            return 5, "Couleur non détectée, score neutre"

        c = self._normalize_text(extracted_color)

        if c in avoid:
            return -35, f"Couleur peu favorable pour votre palette : {extracted_color}"

        # Rappel direct couleur secondaire du vêtement central
        if c in secondary_colors:
            if c in best:
                return 40, f"Rappel élégant d’une couleur du vêtement central, en plus très flatteuse pour votre palette"
            return 32, f"Rappel harmonieux d’une couleur du vêtement central"

        # Accent discret
        if c in accent_colors:
            if c in best:
                return 28, f"Belle reprise d’une couleur d’accent compatible avec votre palette"
            return 20, f"Reprise d’une couleur d’accent du vêtement central"

        # Même couleur dominante = possible mais un peu moins intéressant
        if dominant and c == dominant:
            if c in best:
                return 24, f"Ton sur ton cohérent avec le vêtement central et favorable à votre palette"
            return 16, f"Ton sur ton cohérent avec le vêtement central"

        # Neutres qui équilibrent une pièce forte
        if c in self.NEUTRAL_COLORS:
            if c in best:
                return 34, f"Neutre chic qui équilibre bien le vêtement central et convient à votre palette"
            if c in ok:
                return 24, f"Neutre équilibrant pour accompagner le vêtement central"
            return 18, f"Neutre facile à associer au vêtement central"

        # Couleur favorable au profil, même sans rappel direct
        if c in best:
            return 22, f"Couleur très favorable pour votre palette"
        if c in ok:
            return 10, f"Couleur compatible avec votre palette"

        return 0, f"Couleur sans lien fort détecté avec le vêtement central"

    def _compute_style_score(
        self,
        title: str,
        secondary_category: str,
        wardrobe_item: Dict[str, Any],
        ai_profile: Dict[str, Any],
    ) -> Tuple[float, str]:
        hay = self._normalize_text(f"{title} {secondary_category}")

        wardrobe_style = self._normalize_text(str(wardrobe_item.get("detected_style") or ""))
        profile_styles = [self._normalize_text(x) for x in (ai_profile.get("style_keywords") or []) if x]

        target_styles = []
        if wardrobe_style:
            target_styles.append(wardrobe_style)
        target_styles.extend(profile_styles)

        matched_tokens: List[str] = []
        score = 0

        for style in target_styles:
            hints = self.STYLE_HINTS.get(style, [])
            for hint in hints:
                if self._normalize_text(hint) in hay:
                    matched_tokens.append(f"{style}:{hint}")
                    score += 8
                    break

        score = min(score, 22)

        if matched_tokens:
            return score, f"Style cohérent avec votre vêtement et votre univers"

        return 0, "Pas d’indice de style fort détecté"

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
            return -15, f"Coupe moins favorable pour votre morphologie"
        if positive_matches:
            return 15, f"Coupe bien adaptée à votre morphologie"

        return 0, "Pas d’indice morphologique explicite détecté"

    def _compute_brand_score(self, brand: str, ai_profile: Dict[str, Any]) -> Tuple[float, str]:
        preferred = [self._normalize_text(x) for x in (ai_profile.get("preferred_brands") or []) if x]
        b = self._normalize_text(brand)

        for p in preferred:
            if p and p in b:
                return 12, f"Marque appréciée"

        return 0, "Marque non préférée"

    # =========================
    # Dedupe
    # =========================
    def _dedupe_scored_rows(
        self,
        scored_rows: List[Dict[str, Any]],
        inserted_product_keys: set,
        inserted_family_keys: set,
        inserted_url_keys: set,
        limit: int = 8,
    ) -> List[Dict[str, Any]]:
        out = []

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

            inserted_product_keys.add(product_key)
            inserted_family_keys.add(family_key)
            if url_key:
                inserted_url_keys.add(url_key)

            out.append(row)
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
        }

    # =========================
    # Helpers
    # =========================
    def _pick_best_reason(self, reasons: List[str]) -> str:
        for r in reasons:
            if r and "harmon" in self._normalize_text(r):
                return r
        for r in reasons:
            if r and "palette" in self._normalize_text(r):
                return r
        for r in reasons:
            if r and "style" in self._normalize_text(r):
                return r
        for r in reasons:
            if r:
                return r
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


wardrobe_suggestions_service = WardrobeSuggestionsService()