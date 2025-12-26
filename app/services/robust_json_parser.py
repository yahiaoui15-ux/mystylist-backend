import json
import re


class RobustJSONParser:
    """
    Parseur JSON robuste pour réponses IA.
    Objectif PRODUIT :
    - Ne JAMAIS casser le pipeline
    - Ne JAMAIS vider un rapport
    - Toujours retourner quelque chose d'exploitable
    """

    @staticmethod
    def _strip_code_fences(text: str) -> str:
        if not text:
            return ""
        text = text.strip()
        text = re.sub(r"^```(?:json)?", "", text, flags=re.IGNORECASE).strip()
        text = re.sub(r"```$", "", text).strip()
        return text

    @staticmethod
    def _extract_json_block(text: str) -> str:
        if not text:
            return ""
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return text
        return text[start:end + 1]

    @staticmethod
    def _escape_newlines_inside_strings(text: str) -> str:
        """
        Remplace les retours ligne réels par \\n uniquement
        lorsqu'on est à l'intérieur d'une chaîne JSON.
        """
        if not text:
            return ""

        result = []
        in_string = False
        escape = False

        for char in text:
            if escape:
                result.append(char)
                escape = False
                continue

            if char == "\\":
                result.append(char)
                escape = True
                continue

            if char == '"':
                in_string = not in_string
                result.append(char)
                continue

            if in_string and char == "\n":
                result.append("\\n")
                continue

            if in_string and char == "\r":
                continue

            result.append(char)

        return "".join(result)

    @staticmethod
    def parse_json_with_fallback(response_text: str) -> dict:
        """
        Règle ABSOLUE :
        - NE JAMAIS lever d'exception
        - TOUJOURS retourner un dictionnaire
        """

        if not response_text:
            return {
                "_parse_error": True,
                "_parse_error_msg": "Réponse IA vide",
                "_raw_excerpt": ""
            }

        cleaned = response_text
        cleaned = RobustJSONParser._strip_code_fences(cleaned)
        cleaned = RobustJSONParser._extract_json_block(cleaned)
        cleaned = RobustJSONParser._escape_newlines_inside_strings(cleaned)

        # Tentative standard
        try:
            return json.loads(cleaned)
        except Exception:
            pass

        # Tentative avec correction des guillemets typographiques
        cleaned = (
            cleaned.replace("“", '"')
                   .replace("”", '"')
                   .replace("’", "'")
        )

        try:
            return json.loads(cleaned)
        except Exception as e:
            # Fallback FINAL : jamais bloquant
            print("⚠️ JSON non parsable — mode dégradé activé")
            print(str(e))

            return {
                "_parse_error": True,
                "_parse_error_msg": str(e),
                "_raw_excerpt": response_text[:800]
            }
