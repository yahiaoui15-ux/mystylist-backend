# -*- coding: utf-8 -*-
"""
JSON Parser Robuste v2.3 - FIXÉ apostrophes + extraction JSON blocks
✅ Extraction du JSON même avec texte avant/après
✅ Support des blocs ```json
✅ Pas d'escaping d'apostrophe (elle n'en a pas besoin!)
✅ Compte accolades correctement
"""

import json
import re


class RobustJSONParser:
    """Parser JSON robuste avec extraction markdown + apostrophes"""
    
    @staticmethod
    def parse_json_with_fallback(response_text: str) -> dict:
        """
        Parse JSON avec 6 stratégies de fallback
        
        ✅ Stratégie 0: Extraire JSON des blocs ```json (NOUVEAU v2.3)
        ✅ Stratégie 1: Parser direct (JSON valide)
        ✅ Stratégie 2: Fix escapes invalides + retry
        ✅ Stratégie 3: Extraction complète (compte accolades)
        ✅ Stratégie 4: Nettoyage agressif
        ✅ Stratégie 5: Fallback minimal
        
        Retourne TOUJOURS un dict (jamais d'exception)
        """
        print("\n📋 Parsing JSON robuste:")
        
        # ✅ STRATÉGIE 0 (NEW): Extraire du bloc ```json (NOUVEAU v2.3)
        print("   Tentative 0: Extraction depuis bloc ```json...")
        json_from_markdown = RobustJSONParser._extract_json_from_markdown(response_text)
        if json_from_markdown:
            try:
                cleaned = RobustJSONParser._fix_invalid_escapes(json_from_markdown)
                data = json.loads(cleaned)
                print("      ✅ JSON extrait du bloc markdown!")
                return data
            except json.JSONDecodeError as e:
                print(f"      ❌ Erreur parsing bloc markdown: {str(e)[:60]}...")
        
        # STRATÉGIE 1: Parser direct
        print("   Tentative 1: Parsing direct...")
        try:
            data = json.loads(response_text)
            print("      ✅ JSON valide directement!")
            return data
        except json.JSONDecodeError as e:
            print(f"      ❌ Erreur: {str(e)[:60]}...")
        
        # STRATÉGIE 2: Fix escapes invalides + retry
        print("   Tentative 2: Fix escapes invalides...")
        try:
            cleaned_escapes = RobustJSONParser._fix_invalid_escapes(response_text)
            data = json.loads(cleaned_escapes)
            print("      ✅ JSON valide après fix escapes!")
            return data
        except json.JSONDecodeError as e:
            print(f"      ❌ Erreur: {str(e)[:60]}...")
        
        # STRATÉGIE 3: Extraction complète (compte accolades)
        print("   Tentative 3: Extraction complète (compte accolades)...")
        try:
            extracted = RobustJSONParser._extract_complete_json(response_text)
            if extracted:
                extracted_clean = RobustJSONParser._fix_invalid_escapes(extracted)
                extracted_clean = RobustJSONParser._clean_json(extracted_clean)
                data = json.loads(extracted_clean)
                print("      ✅ JSON complet extrait et valide!")
                return data
            else:
                print("      ❌ Pas pu extraire le JSON complet")
        except Exception as e:
            print(f"      ❌ Erreur: {str(e)[:60]}...")
        
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
    def _extract_json_from_markdown(text: str) -> str:
        """
        ✅ NOUVEAU v2.3: Extrait JSON depuis bloc ```json
        
        Cherche les blocs:
        ```json
        {
          ...
        }
        ```
        
        Retourne le JSON ou None si pas trouvé
        """
        if not text:
            return None
        
        # Chercher le bloc ```json...```
        pattern = r'```json\s*(.*?)\s*```'
        match = re.search(pattern, text, re.DOTALL)
        
        if match:
            json_content = match.group(1).strip()
            if json_content:
                return json_content
        
        # Alternative: chercher juste ```...```
        pattern2 = r'```\s*(.*?)\s*```'
        match2 = re.search(pattern2, text, re.DOTALL)
        
        if match2:
            json_content = match2.group(1).strip()
            # Vérifier que c'est du JSON (commence par {)
            if json_content.startswith('{'):
                return json_content
        
        return None
    
    @staticmethod
    def _fix_invalid_escapes(text: str) -> str:
        """
        ✅ CORRIGÉ v2.3: Corrige SEULEMENT les escapes VRAIMENT invalides
        
        IMPORTANT - En JSON, les SEULES escapes valides sont:
        - \\"  (guillemet)
        - \\\\  (backslash)
        - \\/  (slash)
        - \\b  (backspace)
        - \\f  (form feed)
        - \\n  (newline)
        - \\r  (carriage return)
        - \\t  (tab)
        - \\uXXXX (unicode)
        
        ❌ L'apostrophe ' NE DOIT PAS être échappée! C'est une chaîne dans "..."
        ❌ \\' n'existe pas en JSON valide!
        
        Cette méthode:
        1. Supprimer les caractères de contrôle
        2. Remplacer \\' par ' (l'apostrophe n'a pas besoin d'escape)
        3. Corriger les autres escapes invalides
        """
        if not text:
            return text
        
        # 1. Supprimer caractères de contrôle
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', ' ', text)
        
        # 2. ✅ CRUCIAL: \\' → ' (l'apostrophe N'A PAS besoin d'escape en JSON!)
        text = text.replace("\\'", "'")
        
        # 3. Corriger les autres escapes invalides
        def fix_escape(match):
            char_after = match.group(1)
            
            # Escapes valides à préserver
            if char_after in '"\\bfnrt/':
                return match.group(0)
            
            # \\u suivi de 4 hex est valide
            if char_after == 'u':
                return match.group(0)
            
            # Tout le reste: supprimer le backslash
            return char_after
        
        text = re.sub(r'\\([^"\\bfnrtu/])', fix_escape, text)
        
        return text
    
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
        if bracket_count > 0:
            return response_text[start_idx:] + '}' * bracket_count
        
        return None
    
    @staticmethod
    def _clean_json(json_str: str) -> str:
        """
        ✅ Nettoie le JSON pour le rendre parsable
        """
        
        start_idx = json_str.find('{')
        end_idx = json_str.rfind('}')
        
        if start_idx == -1 or end_idx == -1:
            return "{}"
        
        result = json_str[start_idx:end_idx+1]
        
        # Nettoyer les caractères de contrôle
        result = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', ' ', result)
        
        # Consolider les multi-lignes
        result = result.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        
        # Réduire les espaces multiples
        result = re.sub(r' +', ' ', result)
        
        # Supprimer les virgules traînantes
        result = re.sub(r',(\s*})', r'\1', result)
        result = re.sub(r',(\s*])', r'\1', result)
        
        # Fix escapes invalides
        result = RobustJSONParser._fix_invalid_escapes(result)
        
        return result
    
    @staticmethod
    def _aggressive_clean(json_str: str) -> str:
        """
        ✅ Nettoyage agressif final
        """
        
        # Étape 1: Extraire JSON
        start = json_str.find('{')
        end = json_str.rfind('}')
        
        if start == -1 or end == -1:
            return "{}"
        
        result = json_str[start:end+1]
        
        # Étape 2: Nettoyer
        result = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', ' ', result)
        result = result.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        result = re.sub(r' +', ' ', result)
        result = re.sub(r',(\s*[}\]])', r'\1', result)
        result = RobustJSONParser._fix_invalid_escapes(result)
        
        return result
    
    @staticmethod
    def _minimal_fallback() -> dict:
        """
        ✅ Fallback minimal quand tout échoue
        """
        return {
            "notes_compatibilite": {},
            "unwanted_colors": [],
            "guide_maquillage": {},
            "nailColors": []
        }