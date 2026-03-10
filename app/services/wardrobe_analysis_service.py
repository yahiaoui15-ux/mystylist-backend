import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional, List

from app.utils.supabase_client import supabase
from app.utils.openai_client import openai_client


class WardrobeAnalysisService:
    """
    Analyse un vêtement uploadé dans wardrobe_items et remplit :
    - category_key
    - subcategory
    - dominant_color
    - detected_color (compatibilité temporaire = dominant_color)
    - detected_colors
    - secondary_colors
    - accent_colors
    - detected_pattern
    - detected_material
    - detected_style
    - detected_season
    - ai_label
    - ai_description
    - confidence_score
    - analysis_json
    - status
    - error_message
    """

    ALLOWED_CATEGORY_KEYS = {
        "hauts",
        "bas",
        "robes",
        "vestes",
        "chaussures",
        "sacs",
        "bijoux",
        "maillots_bain",
        "lingerie",
        "accessoires",
        "tenue_sport",
    }

    ALLOWED_COLOR_NAMES = {
        "noir",
        "blanc",
        "ecru",
        "beige",
        "camel",
        "marron",
        "gris",
        "bleu",
        "marine",
        "vert",
        "kaki",
        "rouge",
        "rose",
        "violet",
        "jaune",
        "orange",
        "dore",
        "argente",
        "multicolore",
    }

    def __init__(self):
        self.supabase = supabase
        self.client = supabase.get_client()

    async def analyze_item(self, item_id: str) -> Dict[str, Any]:
        try:
            item = self._get_item(item_id)
            if not item:
                raise ValueError(f"wardrobe_item introuvable: {item_id}")

            image_url = (item.get("image_url") or "").strip()
            if not image_url:
                raise ValueError("image_url manquante pour cet article")

            self._update_item(
                item_id,
                {
                    "status": "processing",
                    "error_message": None,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                },
            )

            analysis = await self._run_ai_analysis(image_url=image_url)
            normalized = self._normalize_analysis(analysis)

            update_payload = {
                "status": "completed",
                "category_key": normalized.get("category_key"),
                "subcategory": normalized.get("subcategory"),
                "dominant_color": normalized.get("dominant_color"),
                "detected_color": normalized.get("detected_color"),  # compatibilité
                "detected_colors": normalized.get("detected_colors"),
                "secondary_colors": normalized.get("secondary_colors"),
                "accent_colors": normalized.get("accent_colors"),
                "detected_pattern": normalized.get("detected_pattern"),
                "detected_material": normalized.get("detected_material"),
                "detected_style": normalized.get("detected_style"),
                "detected_season": normalized.get("detected_season"),
                "ai_label": normalized.get("ai_label"),
                "ai_description": normalized.get("ai_description"),
                "confidence_score": normalized.get("confidence_score"),
                "analysis_json": normalized.get("analysis_json"),
                "error_message": None,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }

            self._update_item(item_id, update_payload)

            return {
                "status": "success",
                "item_id": item_id,
                "category_key": normalized.get("category_key"),
                "ai_label": normalized.get("ai_label"),
                "dominant_color": normalized.get("dominant_color"),
            }

        except Exception as e:
            try:
                self._update_item(
                    item_id,
                    {
                        "status": "error",
                        "error_message": str(e)[:1000],
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                    },
                )
            except Exception:
                pass

            return {
                "status": "error",
                "item_id": item_id,
                "error": str(e),
            }

    def _get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        response = self.supabase.query(
            "wardrobe_items",
            select_fields="*",
            filters={"id": item_id},
        )
        return response.data[0] if response.data else None

    def _update_item(self, item_id: str, payload: Dict[str, Any]) -> None:
        self.client.table("wardrobe_items").update(payload).eq("id", item_id).execute()

    async def _run_ai_analysis(self, image_url: str) -> Dict[str, Any]:
        prompt = """
Tu analyses UNE photo de vêtement portée ou non portée.

Tu dois identifier le vêtement principal visible sur l'image et répondre STRICTEMENT en JSON valide, sans aucun texte autour.

Contraintes :
- category_key doit être UNE SEULE valeur parmi :
  ["hauts","bas","robes","vestes","chaussures","sacs","bijoux","maillots_bain","lingerie","accessoires","tenue_sport"]
- subcategory = sous-type simple et court (ex: "jupe midi plissée", "blazer", "chemise", "jean droit")

Pour les couleurs :
- dominant_color = couleur la plus visible
- detected_colors = liste ordonnée des couleurs visibles avec poids décimal entre 0 et 1
- la somme des poids dans detected_colors doit être proche de 1
- secondary_colors = couleurs importantes mais non dominantes
- accent_colors = petites touches visuelles marquantes
- utilise uniquement des noms de couleurs simples en français, sans nuances marketing
- couleurs autorisées :
  ["noir","blanc","ecru","beige","camel","marron","gris","bleu","marine","vert","kaki","rouge","rose","violet","jaune","orange","dore","argente","multicolore"]
- ne mets pas dominant_color dans secondary_colors
- n’invente pas de couleurs absentes
- si une couleur est très minoritaire, mets-la plutôt dans accent_colors

Autres champs :
- detected_pattern = motif principal s'il y en a un, sinon ""
- detected_material = matière probable si identifiable, sinon ""
- detected_style = style mode dominant (ex: chic, casual, bohème, rock, minimaliste, classique, sportswear), sinon ""
- detected_season = saison la plus pertinente parmi ["printemps","ete","automne","hiver"] ou ""
- ai_label = nom court, élégant, utile pour affichage client
- ai_description = description courte en 1 phrase max, orientée mode
- confidence_score = nombre entre 0 et 100

Format exact attendu :
{
  "category_key": "",
  "subcategory": "",
  "dominant_color": "",
  "detected_colors": [
    {"name": "", "weight": 0.0}
  ],
  "secondary_colors": [
    {"name": "", "weight": 0.0}
  ],
  "accent_colors": [
    {"name": "", "weight": 0.0}
  ],
  "detected_pattern": "",
  "detected_material": "",
  "detected_style": "",
  "detected_season": "",
  "ai_label": "",
  "ai_description": "",
  "confidence_score": 0
}
""".strip()

        openai_client.set_context("wardrobe_analysis", "analyze_item")
        openai_client.set_system_prompt(
            "Tu es un expert mode e-commerce. Réponds uniquement en JSON strict, sans markdown."
        )

        response = await openai_client.analyze_image(
            image_urls=[image_url],
            prompt=prompt,
            max_tokens=700,
            temperature=0.1,
        )

        content = (response.get("content") or "").strip()
        if not content:
            raise ValueError("Réponse IA vide")

        parsed = self._extract_json(content)
        if not isinstance(parsed, dict):
            raise ValueError("Réponse IA non exploitable")

        return parsed

    def _extract_json(self, content: str) -> Dict[str, Any]:
        try:
            return json.loads(content)
        except Exception:
            pass

        match = re.search(r"\{[\s\S]*\}", content)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass

        raise ValueError(f"Impossible de parser le JSON IA: {content[:500]}")

    def _normalize_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        raw_category = self._clean_text(analysis.get("category_key"))
        category_key = self._normalize_category_key(raw_category)

        if category_key not in self.ALLOWED_CATEGORY_KEYS:
            raise ValueError(f"category_key invalide après normalisation: {raw_category}")

        subcategory = self._clean_text(analysis.get("subcategory"))

        dominant_color = self._normalize_color_name(
            self._clean_text(analysis.get("dominant_color"))
        )

        detected_colors = self._normalize_color_list(analysis.get("detected_colors"))
        secondary_colors = self._normalize_color_list(analysis.get("secondary_colors"))
        accent_colors = self._normalize_color_list(analysis.get("accent_colors"))
        
        # Déduction automatique si GPT ne fournit pas secondary/accent
        if detected_colors and not secondary_colors and not accent_colors:
            for c in detected_colors:
                w = c["weight"]
                name = c["name"]

                if dominant_color and name == dominant_color:
                    continue

                if w >= 0.15:
                    secondary_colors.append(c)
                else:
                    accent_colors.append(c)

        # Si GPT oublie dominant_color mais detected_colors existe
        if not dominant_color and detected_colors:
            dominant_color = detected_colors[0]["name"]

        # Si GPT oublie detected_colors mais dominant_color existe
        if dominant_color and not detected_colors:
            detected_colors = [{"name": dominant_color, "weight": 1.0}]

        # Retirer la dominante des secondaires
        if dominant_color:
            secondary_colors = [
                x for x in secondary_colors if x["name"] != dominant_color
            ]

        # Retirer doublons entre secondary et accent
        secondary_names = {x["name"] for x in secondary_colors}
        accent_colors = [
            x for x in accent_colors if x["name"] not in secondary_names and x["name"] != dominant_color
        ]

        detected_pattern = self._clean_text(analysis.get("detected_pattern"))
        detected_material = self._clean_text(analysis.get("detected_material"))
        detected_style = self._clean_text(analysis.get("detected_style"))
        detected_season = self._normalize_season(self._clean_text(analysis.get("detected_season")))
        ai_label = self._clean_text(analysis.get("ai_label"))
        ai_description = self._clean_text(analysis.get("ai_description"))
        confidence_score = self._normalize_confidence(analysis.get("confidence_score"))

        cleaned = {
            "category_key": category_key,
            "subcategory": subcategory,
            "dominant_color": dominant_color,
            "detected_color": dominant_color,  # compatibilité temporaire
            "detected_colors": detected_colors,
            "secondary_colors": secondary_colors,
            "accent_colors": accent_colors,
            "detected_pattern": detected_pattern,
            "detected_material": detected_material,
            "detected_style": detected_style,
            "detected_season": detected_season,
            "ai_label": ai_label,
            "ai_description": ai_description,
            "confidence_score": confidence_score,
        }

        return {
            **cleaned,
            "analysis_json": cleaned,
        }

    def _normalize_category_key(self, raw: str) -> str:
        k = self._slug(raw)

        aliases = {
            "haut": "hauts",
            "hauts": "hauts",
            "top": "hauts",
            "tops": "hauts",
            "chemise": "hauts",
            "blouse": "hauts",
            "pull": "hauts",
            "tshirt": "hauts",
            "tee_shirt": "hauts",
            "tee-shirt": "hauts",

            "bas": "bas",
            "pantalon": "bas",
            "jean": "bas",
            "jupe": "bas",
            "short": "bas",
            "shorts": "bas",

            "robe": "robes",
            "robes": "robes",
            "dress": "robes",

            "veste": "vestes",
            "vestes": "vestes",
            "manteau": "vestes",
            "blazer": "vestes",
            "outerwear": "vestes",

            "chaussure": "chaussures",
            "chaussures": "chaussures",
            "shoe": "chaussures",
            "shoes": "chaussures",
            "basket": "chaussures",
            "sandale": "chaussures",
            "escarpin": "chaussures",
            "mocassin": "chaussures",

            "sac": "sacs",
            "sacs": "sacs",
            "bag": "sacs",
            "handbag": "sacs",

            "bijou": "bijoux",
            "bijoux": "bijoux",
            "jewelry": "bijoux",

            "maillot_de_bain": "maillots_bain",
            "maillot": "maillots_bain",
            "swimwear": "maillots_bain",
            "bikini": "maillots_bain",

            "lingerie": "lingerie",
            "sous_vetement": "lingerie",
            "bra": "lingerie",

            "accessoire": "accessoires",
            "accessoires": "accessoires",
            "foulard": "accessoires",
            "ceinture": "accessoires",

            "tenue_sport": "tenue_sport",
            "sport": "tenue_sport",
            "sportswear": "tenue_sport",
            "legging": "tenue_sport",
        }

        return aliases.get(k, raw)

    def _normalize_season(self, value: str) -> str:
        k = self._slug(value)
        mapping = {
            "printemps": "printemps",
            "spring": "printemps",
            "ete": "ete",
            "summer": "ete",
            "automne": "automne",
            "fall": "automne",
            "autumn": "automne",
            "hiver": "hiver",
            "winter": "hiver",
        }
        return mapping.get(k, value or "")

    def _normalize_confidence(self, value: Any) -> float:
        try:
            score = float(value)
        except Exception:
            score = 0.0
        score = max(0.0, min(100.0, score))
        return round(score, 2)

    def _normalize_color_name(self, value: str) -> str:
        raw = self._clean_text(value).lower()
        if not raw:
            return ""

        aliases = {
            "blanche": "blanc",
            "blanches": "blanc",
            "blanc casse": "ecru",
            "ivoire": "ecru",
            "ecrue": "ecru",
            "ecrus": "ecru",
            "beiges": "beige",
            "camel clair": "camel",
            "marrons": "marron",
            "brun": "marron",
            "brune": "marron",
            "grise": "gris",
            "gris clair": "gris",
            "gris fonce": "gris",
            "bleue": "bleu",
            "bleues": "bleu",
            "bleu marine": "marine",
            "navy": "marine",
            "verte": "vert",
            "vert olive": "kaki",
            "kaki olive": "kaki",
            "rouges": "rouge",
            "rouge brique": "rouge",
            "rosee": "rose",
            "violette": "violet",
            "jaunes": "jaune",
            "orangee": "orange",
            "dorée": "dore",
            "doré": "dore",
            "argentée": "argente",
            "argenté": "argente",
            "multicolor": "multicolore",
        }

        slugged = self._slug(raw).replace("_", " ")
        normalized = aliases.get(slugged, raw)
        normalized = self._slug(normalized).replace("_", " ")

        if normalized == "bleu marine":
            normalized = "marine"

        normalized = normalized.replace(" ", "_")
        normalized = normalized.replace("_", " ").strip()

        final_aliases = {
            "blanc": "blanc",
            "ecru": "ecru",
            "beige": "beige",
            "camel": "camel",
            "marron": "marron",
            "gris": "gris",
            "bleu": "bleu",
            "marine": "marine",
            "vert": "vert",
            "kaki": "kaki",
            "rouge": "rouge",
            "rose": "rose",
            "violet": "violet",
            "jaune": "jaune",
            "orange": "orange",
            "dore": "dore",
            "argente": "argente",
            "noir": "noir",
            "multicolore": "multicolore",
        }

        return final_aliases.get(final_aliases.get(normalized, normalized), normalized) if final_aliases.get(normalized, None) else ""

    def _normalize_color_list(self, value: Any) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        if not isinstance(value, list):
            return out

        seen = set()

        for item in value:
            if not isinstance(item, dict):
                continue

            name = self._normalize_color_name(str(item.get("name") or ""))
            weight = item.get("weight")

            try:
                weight = float(weight)
            except Exception:
                continue

            if not name:
                continue
            if name not in self.ALLOWED_COLOR_NAMES:
                continue
            if weight <= 0:
                continue
            if name in seen:
                continue

            seen.add(name)
            out.append({
                "name": name,
                "weight": round(weight, 4),
            })

        out.sort(key=lambda x: x["weight"], reverse=True)

        # borne haute simple
        for row in out:
            if row["weight"] > 1:
                row["weight"] = 1.0

        return out

    def _clean_text(self, value: Any) -> str:
        if value is None:
            return ""
        return str(value).strip()[:300]

    def _slug(self, value: str) -> str:
        s = (value or "").strip().lower()
        s = s.replace("é", "e").replace("è", "e").replace("ê", "e")
        s = s.replace("à", "a").replace("â", "a")
        s = s.replace("ù", "u").replace("û", "u")
        s = s.replace("î", "i").replace("ï", "i")
        s = s.replace("ô", "o")
        s = s.replace("ç", "c")
        s = re.sub(r"[^a-z0-9]+", "_", s)
        s = re.sub(r"_+", "_", s).strip("_")
        return s


wardrobe_analysis_service = WardrobeAnalysisService()