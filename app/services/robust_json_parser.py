"""
JSON Parser Robuste - Version améliorée
✅ Compte les accolades correctement
✅ Gère les objets imbriqués complexes
✅ Extrait TOUT le JSON valide (pas juste une partie)
"""

import json
import re


class RobustJSONParser:
    """Parser JSON robuste avec comptage d'accolades"""
    
    @staticmethod
    def parse_json_with_fallback(response_text: str) -> dict:
        """
        Parse JSON avec 4 stratégies de fallback
        
        ✅ Stratégie 1: Parser direct (JSON valide)
        ✅ Stratégie 2: Nettoyer et réessayer
        ✅ Stratégie 3: Extraction complète (compte accolades)
        ✅ Stratégie 4: Fallback minimal
        
        Retourne TOUJOURS un dict (jamais d'exception)
        """
        print("\n📋 Parsing JSON robuste:")
        
        # STRATÉGIE 1: Parser direct
        print("   Tentative 1: Parsing direct...")
        try:
            data = json.loads(response_text)
            print("      ✅ JSON valide directement!")
            return data
        except json.JSONDecodeError as e:
            print(f"      ❌ Erreur: {str(e)[:60]}...")
        
        # STRATÉGIE 2: Nettoyer et réessayer
        print("   Tentative 2: Après nettoyage...")
        try:
            cleaned = RobustJSONParser._clean_json(response_text)
            data = json.loads(cleaned)
            print("      ✅ JSON valide après nettoyage!")
            return data
        except Exception as e:
            print(f"      ❌ Erreur: {str(e)[:60]}...")
        
        # STRATÉGIE 3: Extraction complète (NOUVELLE - compte accolades)
        print("   Tentative 3: Extraction complète (compte accolades)...")
        try:
            extracted = RobustJSONParser._extract_complete_json(response_text)
            if extracted:
                data = json.loads(extracted)
                print("      ✅ JSON complet extrait et valide!")
                return data
        except Exception as e:
            print(f"      ❌ Erreur: {str(e)[:60]}...")
        
        # FALLBACK: Retourner dict minimal
        print("   Tentative 4: Fallback minimal")
        print("      ⚠️ Retour données minimales")
        return RobustJSONParser._minimal_fallback()
    
    @staticmethod
    def _extract_complete_json(response_text: str) -> str:
        """
        ✅ NOUVEAU: Extrait le JSON COMPLET en comptant les accolades
        
        Trouve le premier `{` et compte:
        - Chaque `{` = +1
        - Chaque `}` = -1
        - Quand le compte = 0, on a le JSON complet
        """
        start_idx = response_text.find('{')
        
        if start_idx == -1:
            return None
        
        bracket_count = 0
        in_string = False
        escape_next = False
        
        for i in range(start_idx, len(response_text)):
            char = response_text[i]
            
            # Gérer les échappements dans les strings
            if escape_next:
                escape_next = False
                continue
            
            if char == '\\':
                escape_next = True
                continue
            
            # Gérer les délimiteurs de strings
            if char == '"':
                in_string = not in_string
                continue
            
            # Compter les accolades SEULEMENT hors des strings
            if not in_string:
                if char == '{':
                    bracket_count += 1
                elif char == '}':
                    bracket_count -= 1
                    
                    # Quand on revient à 0, on a le JSON complet!
                    if bracket_count == 0:
                        return response_text[start_idx:i+1]
        
        # Si on arrive ici, il manque des accolades fermantes
        return None
    
    @staticmethod
    def _clean_json(json_str: str) -> str:
        """
        ✅ AMÉLIORÉ: Nettoie le JSON pour le rendre parsable
        
        Corrige les erreurs courantes d'OpenAI:
        - Caractères mal échappés
        - Strings non terminées
        - Virgules traînantes
        """
        
        # Extraire le JSON (du premier { au dernier })
        start_idx = json_str.find('{')
        end_idx = json_str.rfind('}')
        
        if start_idx == -1 or end_idx == -1:
            return "{}"
        
        result = json_str[start_idx:end_idx+1]
        
        # ✅ CORRECTION 1: Nettoyer les caractères de contrôle
        result = re.sub(r'[\x00-\x1f\x7f]', ' ', result)
        
        # ✅ CORRECTION 2: Consolider les multi-lignes
        result = result.replace('\n', ' ').replace('\r', ' ')
        
        # ✅ CORRECTION 3: Corriger les quotes mal échappées
        # Remplacer \" par " (si c'est une vraie quote, pas un délimiteur)
        result = re.sub(r'\\"', '"', result)
        
        # ✅ CORRECTION 4: Supprimer les virgules traînantes avant } ou ]
        result = re.sub(r',\s*}', '}', result)
        result = re.sub(r',\s*]', ']', result)
        
        # ✅ CORRECTION 5: Ajouter les virgules manquantes entre propriétés
        # Si on a "}X où X n'est pas , ; ou }, ajouter une virgule
        result = re.sub(r'"\s*:\s*("[^"]*"|[0-9]+|true|false|null|{|[)\s*"', r'\g<0>,', result)
        
        # ✅ CORRECTION 6: Corriger les strings non terminées
        # Pattern: clé": valeur sans guillemets fermants avant ,}]
        result = re.sub(r'": "([^"]*?)(\s*[,}\]])', r'": "\1"\2', result)
        
        return result
    
    @staticmethod
    def _minimal_fallback() -> dict:
        """Retourne une structure minimale valide"""
        return {
            "saison_confirmee": "Indéterminée",
            "sous_ton_detecte": "",
            "justification_saison": "Analyse en cours...",
            "palette_personnalisee": [],
            "notes_compatibilite": {},
            "associations_gagnantes": [],
            "guide_maquillage": {
                "teint": "",
                "blush": "",
                "bronzer": "",
                "highlighter": "",
                "yeux": "",
                "eyeliner": "",
                "mascara": "",
                "brows": "",
                "lipsNude": "",
                "lipsDay": "",
                "lipsEvening": "",
                "lipsAvoid": "",
                "vernis_a_ongles": []
            },
            "shopping_couleurs": {
                "priorite_1": [],
                "priorite_2": [],
                "eviter_absolument": []
            },
            "alternatives_couleurs_refusees": {},
            "analyse_colorimetrique_detaillee": {
                "temperature": "neutre",
                "valeur": "médium",
                "intensite": "médium",
                "contraste_naturel": "moyen",
                "description_teint": "",
                "description_yeux": "",
                "description_cheveux": "",
                "harmonie_globale": "",
                "bloc_emotionnel": "",
                "impact_visuel": {
                    "effet_couleurs_chaudes": "",
                    "effet_couleurs_froides": "",
                    "pourquoi": ""
                }
            },
            "eye_color": "",
            "hair_color": ""
        }