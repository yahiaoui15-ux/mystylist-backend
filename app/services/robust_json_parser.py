# -*- coding: utf-8 -*-
"""
JSON Parser Robuste v2.4 - AMÉLIORÉ
✅ Basé sur votre parser actuel
✅ + PRÉ-TRAITEMENT des newlines/caractères contrôle (LA FIX PRINCIPALE)
✅ + Ordre de stratégies optimisé
✅ Extraction du JSON même avec texte avant/après
✅ Support des blocs ```json
✅ Pas d'escaping d'apostrophe
✅ Compte accolades correctement
"""

import json
import re


class RobustJSONParser:
    """Parser JSON robuste avec extraction markdown + apostrophes"""
    
    @staticmethod
    def parse_json_with_fallback(response_text: str) -> dict:
        """
        Parse JSON avec stratégies optimisées
        
        ✅ Stratégie 0 (NEW): PRÉ-TRAITEMENT des newlines/caractères contrôle
        ✅ Stratégie 1: Extraire JSON des blocs ```json
        ✅ Stratégie 2: Parser direct (JSON valide)
        ✅ Stratégie 3: Fix escapes invalides + retry
        ✅ Stratégie 4: Extraction complète (compte accolades)
        ✅ Stratégie 5: Nettoyage agressif
        ✅ Stratégie 6: Fallback minimal
        
        Retourne TOUJOURS un dict (jamais d'exception)
        """
        print("\n🔋 Parsing JSON robuste:")
        
        if not response_text or not isinstance(response_text, str):
            print("   ❌ Contenu vide ou invalide → Fallback")
            return RobustJSONParser._minimal_fallback()
        
        # ✅ STRATÉGIE 0 (NEW): PRÉ-TRAITEMENT - Échapper les newlines/caractères contrôle
        # C'EST LA FIX PRINCIPALE POUR LES CRASHES!
        print("   Stratégie 0: Pré-traitement des newlines/caractères contrôle...")
        preprocessed = RobustJSONParser._preprocess_control_chars(response_text)
        
        # ✅ STRATÉGIE 1: Extraire JSON des blocs ```json
        print("   Stratégie 1: Extraction depuis bloc ```json...")
        json_from_markdown = RobustJSONParser._extract_json_from_markdown(preprocessed)
        if json_from_markdown:
            try:
                cleaned = RobustJSONParser._fix_invalid_escapes(json_from_markdown)
                data = json.loads(cleaned)
                print("      ✅ JSON extrait du bloc markdown!")
                return data
            except json.JSONDecodeError as e:
                print(f"      ❌ Erreur: {str(e)[:60]}...")
        
        # ✅ STRATÉGIE 2: Parser direct
        print("   Stratégie 2: Parsing direct...")
        try:
            data = json.loads(preprocessed)
            print("      ✅ JSON valide directement!")
            return data
        except json.JSONDecodeError as e:
            print(f"      ❌ Erreur: {str(e)[:60]}...")
        
        # ✅ STRATÉGIE 3: Fix escapes invalides + retry
        print("   Stratégie 3: Fix escapes invalides...")
        try:
            cleaned_escapes = RobustJSONParser._fix_invalid_escapes(preprocessed)
            data = json.loads(cleaned_escapes)
            print("      ✅ JSON valide après fix escapes!")
            return data
        except json.JSONDecodeError as e:
            print(f"      ❌ Erreur: {str(e)[:60]}...")
        
        # ✅ STRATÉGIE 4: Extraction complète (compte accolades)
        print("   Stratégie 4: Extraction complète (compte accolades)...")
        try:
            extracted = RobustJSONParser._extract_complete_json(preprocessed)
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
        
        # ✅ STRATÉGIE 5: Nettoyage agressif final
        print("   Stratégie 5: Nettoyage agressif...")
        try:
            aggressive_clean = RobustJSONParser._aggressive_clean(preprocessed)
            if aggressive_clean and aggressive_clean != "{}":
                data = json.loads(aggressive_clean)
                print("      ✅ JSON valide après nettoyage agressif!")
                return data
        except Exception as e:
            print(f"      ❌ Erreur: {str(e)[:60]}...")
        
        # ✅ STRATÉGIE 6: Fallback minimal
        print("   Stratégie 6: Fallback minimal")
        print("      ⚠️ Retour données minimales")
        return RobustJSONParser._minimal_fallback()
    
    @staticmethod
    def _preprocess_control_chars(text: str) -> str:
        """
        ✅ NEW - PRÉ-TRAITEMENT DES CARACTÈRES DE CONTRÔLE
        
        C'EST LA FIX PRINCIPALE POUR VOS CRASHES!
        
        Remplace les caractères de contrôle par leurs équivalents échappés
        avant toute tentative de parsing JSON.
        
        Convertit:
        - Vraies newlines → \\n
        - Carriage returns → \\r
        - Tabs → \\t
        - Autres caractères contrôle → espaces
        """
        if not text:
            return text
        
        # Remplacer les vraies newlines non échappées par \\n
        # Pattern: newline qui n'est pas déjà précédée par un backslash
        text = re.sub(r'(?<!\\)\n', r'\\n', text)
        text = re.sub(r'(?<!\\)\r', r'\\r', text)
        text = re.sub(r'(?<!\\)\t', r'\\t', text)
        
        # Supprimer les autres caractères de contrôle
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', ' ', text)
        
        return text
    
    @staticmethod
    def _extract_json_from_markdown(text: str) -> str:
        """
        Extrait JSON depuis bloc ```json
        
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
        Corrige SEULEMENT les escapes VRAIMENT invalides
        
        IMPORTANT - En JSON, les SEULES escapes valides sont:
        - \\" (guillemet)
        - \\\\ (backslash)
        - \\/ (slash)
        - \\b (backspace)
        - \\f (form feed)
        - \\n (newline)
        - \\r (carriage return)
        - \\t (tab)
        - \\uXXXX (unicode)
        
        ❌ L'apostrophe ' NE DOIT PAS être échappée!
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
        Extrait le JSON COMPLET en comptant les accolades
        
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
        Nettoie le JSON pour le rendre parsable
        """
        
        start_idx = json_str.find('{')
        end_idx = json_str.rfind('}')
        
        if start_idx == -1 or end_idx == -1:
            return "{}"
        
        result = json_str[start_idx:end_idx+1]
        
        # Supprimer les virgules traînantes
        result = re.sub(r',(\s*})', r'\1', result)
        result = re.sub(r',(\s*])', r'\1', result)
        
        # Fix escapes invalides
        result = RobustJSONParser._fix_invalid_escapes(result)
        
        return result
    
    @staticmethod
    def _aggressive_clean(json_str: str) -> str:
        """
        Nettoyage agressif final
        """
        
        # Étape 1: Extraire JSON
        start = json_str.find('{')
        end = json_str.rfind('}')
        
        if start == -1 or end == -1:
            return "{}"
        
        result = json_str[start:end+1]
        
        # Étape 2: Nettoyer
        result = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', ' ', result)
        result = re.sub(r',(\s*[}\]])', r'\1', result)
        result = RobustJSONParser._fix_invalid_escapes(result)
        
        return result
    
    @staticmethod
    def _minimal_fallback() -> dict:
        """
        Fallback minimal quand tout échoue
        """
        return {
            "notes_compatibilite": {},
            "unwanted_colors": [],
            "guide_maquillage": {},
            "nailColors": []
        }