# -*- coding: utf-8 -*-
"""
JSON Parser Robuste v2.1 - Version corrigée
✅ Compte les accolades correctement
✅ Gère les objets imbriqués complexes
✅ Extrait TOUT le JSON valide (pas juste une partie)
✅ FIXÉ: Regex character set cassée
✅ FIXÉ v2.1: Ne plus créer de \\' invalides - remplacer par guillemets ou supprimer
"""

import json
import re


class RobustJSONParser:
    """Parser JSON robuste avec comptage d'accolades et nettoyage apostrophes"""
    
    @staticmethod
    def parse_json_with_fallback(response_text: str) -> dict:
        """
        Parse JSON avec 5 stratégies de fallback
        
        ✅ Stratégie 1: Parser direct (JSON valide)
        ✅ Stratégie 2: Fix escapes invalides + retry
        ✅ Stratégie 3: Extraction complète (compte accolades)
        ✅ Stratégie 4: Nettoyage agressif
        ✅ Stratégie 5: Fallback minimal
        
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
        
        # STRATÉGIE 2: Fix escapes invalides + retry
        print("   Tentative 2: Fix escapes invalides (\\' etc.)...")
        try:
            cleaned_escapes = RobustJSONParser._fix_invalid_escapes(response_text)
            data = json.loads(cleaned_escapes)
            print("      ✅ JSON valide après fix escapes!")
            return data
        except json.JSONDecodeError as e:
            print(f"      ❌ Erreur: {str(e)[:60]}...")
        
        # STRATÉGIE 3: Extraction complète (compte accolades) + nettoyage
        print("   Tentative 3: Extraction complète (compte accolades)...")
        try:
            extracted = RobustJSONParser._extract_complete_json(response_text)
            if extracted:
                # Nettoyer puis parser
                extracted_clean = RobustJSONParser._fix_invalid_escapes(extracted)
                extracted_clean = RobustJSONParser._clean_json(extracted_clean)
                data = json.loads(extracted_clean)
                print("      ✅ JSON complet extrait et valide!")
                return data
            else:
                print("      ❌ Pas pu extraire le JSON complet")
        except Exception as e:
            print(f"      ❌ Erreur parsing extrait: {str(e)[:60]}...")
        
        # STRATÉGIE 4: Nettoyage agressif final
        print("   Tentative 4: Nettoyage agressif...")
        try:
            aggressive_clean = RobustJSONParser._aggressive_clean(response_text)
            if aggressive_clean and aggressive_clean != "{}":
                data = json.loads(aggressive_clean)
                print("      ✅ JSON valide après nettoyage agressif!")
                return data
        except Exception as e:
            print(f"      ❌ Erreur: {str(e)[:60]}...")
        
        # FALLBACK: Retourner dict minimal
        print("   Tentative 5: Fallback minimal")
        print("      ⚠️ Retour données minimales")
        return RobustJSONParser._minimal_fallback()
    
    @staticmethod
    def _fix_invalid_escapes(text: str) -> str:
        """
        ✅ CORRIGÉ v2.1: Corrige les séquences d'échappement JSON INVALIDES
        
        IMPORTANT - En JSON, les SEULES séquences valides sont:
        - \\"  (guillemet)
        - \\\\  (backslash)
        - \\/  (slash)
        - \\b  (backspace)
        - \\f  (form feed)
        - \\n  (newline)
        - \\r  (carriage return)
        - \\t  (tab)
        - \\uXXXX (unicode)
        
        TOUT AUTRE \\X est INVALIDE !
        Notamment: \\' (apostrophe échappée) N'EXISTE PAS en JSON !
        
        Cette méthode:
        1. Remplace \\' par ' (apostrophe simple)
        2. Corrige les autres escapes invalides
        """
        if not text:
            return text
        
        # 1. Supprimer caractères de contrôle (sauf les utiles)
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', ' ', text)
        
        # 2. ✅ CRUCIAL: \\' → ' (l'apostrophe échappée n'existe pas en JSON!)
        text = text.replace("\\'", "'")
        
        # 3. Corriger les autres escapes invalides
        # Pattern: backslash suivi d'un caractère qui n'est pas une séquence valide
        def fix_escape(match):
            char_after = match.group(1)
            
            # Séquences valides à préserver
            if char_after in '"\\bfnrt/':
                return match.group(0)
            
            # \\u suivi de 4 hex est valide (on garde)
            if char_after == 'u':
                return match.group(0)
            
            # Tout le reste: supprimer le backslash, garder le caractère
            return char_after
        
        # Appliquer la correction pour \\X où X n'est pas valide
        text = re.sub(r'\\([^"\\bfnrtu/])', fix_escape, text)
        
        return text
    
    @staticmethod
    def _remove_apostrophes_in_json_strings(text: str) -> str:
        """
        ✅ ALTERNATIVE: Supprime les apostrophes problématiques dans les strings JSON
        au lieu d'essayer de les échapper (car \\' n'est pas valide)
        
        Approche: remplacer ' par ` ou supprimer
        """
        result = []
        in_string = False
        i = 0
        
        while i < len(text):
            char = text[i]
            
            # Détecter début/fin de string JSON
            if char == '"' and (i == 0 or text[i-1] != '\\'):
                in_string = not in_string
                result.append(char)
                i += 1
                continue
            
            # Si dans une string et on trouve une apostrophe
            if in_string and char == "'":
                # Option 1: Remplacer par guillemet typographique ou rien
                # On supprime simplement pour éviter tout problème
                # (ou on pourrait utiliser ` ou ʼ)
                result.append("")  # Supprimer l'apostrophe
                i += 1
                continue
            
            result.append(char)
            i += 1
        
        return ''.join(result)
    
    @staticmethod
    def _extract_complete_json(response_text: str) -> str:
        """
        ✅ Extrait le JSON COMPLET en comptant les accolades
        
        Trouve le premier `{` et compte:
        - Chaque `{` = +1
        - Chaque `}` = -1
        - Quand le compte = 0, on a le JSON complet
        
        Gère correctement les strings et les échappements
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
                        extracted = response_text[start_idx:i+1]
                        return extracted
        
        # Si on arrive ici, il manque des accolades fermantes
        # Retourner quand même ce qu'on a
        if bracket_count > 0:
            return response_text[start_idx:] + '}' * bracket_count
        
        return None
    
    @staticmethod
    def _clean_json(json_str: str) -> str:
        """
        ✅ Nettoie le JSON pour le rendre parsable
        
        Corrige les erreurs courantes d'OpenAI:
        - Caractères de contrôle
        - Multi-lignes 
        - Quotes mal échappées
        - Virgules traînantes
        - Strings non terminées
        """
        
        # Extraire le JSON (du premier { au dernier })
        start_idx = json_str.find('{')
        end_idx = json_str.rfind('}')
        
        if start_idx == -1 or end_idx == -1:
            return "{}"
        
        result = json_str[start_idx:end_idx+1]
        
        # ✅ CORRECTION 1: Nettoyer les caractères de contrôle
        result = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', ' ', result)
        
        # ✅ CORRECTION 2: Consolider les multi-lignes
        result = result.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        
        # ✅ CORRECTION 3: Réduire les espaces multiples
        result = re.sub(r' +', ' ', result)
        
        # ✅ CORRECTION 4: Supprimer les virgules traînantes
        result = re.sub(r',(\s*})', r'\1', result)
        result = re.sub(r',(\s*])', r'\1', result)
        
        # ✅ CORRECTION 5: Fix escapes invalides
        result = RobustJSONParser._fix_invalid_escapes(result)
        
        return result
    
    @staticmethod
    def _aggressive_clean(json_str: str) -> str:
        """
        ✅ Nettoyage AGRESSIF pour cas désespérés
        
        Supprime tout ce qui n'est pas JSON valide
        """
        # Extraire entre premier { et dernier }
        start_idx = json_str.find('{')
        end_idx = json_str.rfind('}')
        
        if start_idx == -1 or end_idx == -1:
            return "{}"
        
        result = json_str[start_idx:end_idx+1]
        
        # Nettoyage basique
        result = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', ' ', result)
        result = result.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        
        # ✅ Fix escapes invalides (dont \\')
        result = RobustJSONParser._fix_invalid_escapes(result)
        
        # Supprimer virgules traînantes
        result = re.sub(r',(\s*[}\]])', r'\1', result)
        
        # Réduire espaces
        result = re.sub(r' +', ' ', result)
        
        # Essayer de réparer les strings non terminées
        # Compter les guillemets (en excluant les échappés)
        quote_count = len(re.findall(r'(?<!\\)"', result))
        if quote_count % 2 != 0:
            # Nombre impair de guillemets = problème
            # Ajouter un guillemet avant la dernière }
            last_brace = result.rfind('}')
            if last_brace > 0:
                result = result[:last_brace] + '"' + result[last_brace:]
        
        return result
    
    @staticmethod
    def _minimal_fallback() -> dict:
        """Retourne une structure minimale valide avec TOUS les champs"""
        return {
            "saison_confirmee": "Indéterminée",
            "sous_ton_detecte": "",
            "justification_saison": "Analyse en cours...",
            "palette_personnalisee": [],
            "allColorsWithNotes": [],
            "notes_compatibilite": {},
            "associations_gagnantes": [],
            "guide_maquillage": {
                "teint": "",
                "blush": "",
                "bronzer": "",
                "highlighter": "",
                "eyeshadows": "",
                "eyeliner": "",
                "mascara": "",
                "brows": "",
                "lipsNatural": "",
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
                "valeur": "medium",
                "intensite": "medium",
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
            "unwanted_colors": [],
            "nailColors": [],
            "eye_color": "",
            "hair_color": ""
        }