# -*- coding: utf-8 -*-
"""
JSON Parser Robuste v3.0 - CORRIGÉ SANS FALLBACKS
✅ Ajoute les guillemets manquants autour des clés JSON
✅ Supprime TOUS les fallbacks - utilise VRAIES données uniquement
✅ Raise une erreur si parsing impossible (pas de silence!)
✅ 7 stratégies optimisées pour JSON cassé
"""

import json
import re


class RobustJSONParser:
    """Parser JSON robuste - NO FALLBACKS, vraies données uniquement"""
    
    @staticmethod
    def parse_json_with_fallback(response_text: str) -> dict:
        """
        Parse JSON avec 7 stratégies - SANS FALLBACK
        
        ✅ Stratégie 0: Pré-traitement newlines/caractères contrôle
        ✅ Stratégie 0.5: AJOUTER guillemets manquants (NEW!)
        ✅ Stratégie 1: Extraction depuis bloc ```json
        ✅ Stratégie 2: Parsing direct
        ✅ Stratégie 3: Fix escapes invalides
        ✅ Stratégie 4: Extraction complète (compte accolades)
        ✅ Stratégie 5: Nettoyage agressif
        ❌ PAS DE FALLBACK - Raise exception si tout échoue!
        
        Retourne TOUJOURS un dict valide avec VRAIES données ou RAISE
        """
        print("\n🔋 Parsing JSON robuste (NO FALLBACKS):")
        
        if not response_text or not isinstance(response_text, str):
            raise ValueError("❌ Contenu vide ou invalide - impossible de parser")
        
        # ✅ STRATÉGIE 0: PRÉ-TRAITEMENT - Échapper les newlines/caractères contrôle
        print("   Stratégie 0: Pré-traitement des newlines/caractères contrôle...")
        preprocessed = RobustJSONParser._preprocess_control_chars(response_text)
        
        # ✅ STRATÉGIE 0.5: AJOUTER GUILLEMETS MANQUANTS (NEW!)
        print("   Stratégie 0.5: Ajouter guillemets manquants autour des clés...")
        preprocessed = RobustJSONParser._add_missing_quotes(preprocessed)
        
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
        
        # ❌ PLUS DE FALLBACK - RAISE EXCEPTION
        error_msg = (
            "\n❌ IMPOSSIBLE DE PARSER LE JSON!\n"
            "   Toutes les 7 stratégies ont échoué.\n"
            "   Response reçue:\n"
            f"   {response_text[:200]}...\n"
        )
        print(error_msg)
        raise ValueError(error_msg)
    
    @staticmethod
    def _preprocess_control_chars(text: str) -> str:
        """
        Pré-traitement: Échappe les caractères de contrôle
        """
        if not text:
            return text
        
        # Remplacer les vraies newlines non échappées
        text = re.sub(r'(?<!\\)\n', r'\\n', text)
        text = re.sub(r'(?<!\\)\r', r'\\r', text)
        text = re.sub(r'(?<!\\)\t', r'\\t', text)
        
        # Supprimer les autres caractères de contrôle
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', ' ', text)
        
        return text
    
    @staticmethod
    def _add_missing_quotes(text: str) -> str:
        """
        ✅ NEW - AJOUTE les guillemets manquants autour des clés JSON
        
        Transforme:
          {saison_confirmee: "Automne"}
        En:
          {"saison_confirmee": "Automne"}
        
        Pattern regex:
        - (\\{|,) = accolade ouvrante ou virgule
        - \\s* = espaces optionnels
        - ([a-zA-Z_][a-zA-Z0-9_]*) = nom de clé (commence par lettre/underscore)
        - \\s*: = espaces optionnels puis deux-points
        
        Remplace par:
        - \\1 = le { ou ,
        - "\\2" = la clé entre guillemets
        - : = le deux-points
        """
        if not text:
            return text
        
        # Ajouter guillemets autour des clés sans guillemets
        text = re.sub(
            r'(\{|,)\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:',
            r'\1 "\2":',
            text
        )
        
        return text
    
    @staticmethod
    def _extract_json_from_markdown(text: str) -> str:
        """
        Extrait JSON depuis bloc ```json
        """
        if not text:
            return None
        
        # Chercher ```json...```
        pattern = r'```json\s*(.*?)\s*```'
        match = re.search(pattern, text, re.DOTALL)
        
        if match:
            json_content = match.group(1).strip()
            if json_content:
                return json_content
        
        # Alternative: chercher ```...```
        pattern2 = r'```\s*(.*?)\s*```'
        match2 = re.search(pattern2, text, re.DOTALL)
        
        if match2:
            json_content = match2.group(1).strip()
            if json_content.startswith('{'):
                return json_content
        
        return None
    
    @staticmethod
    def _fix_invalid_escapes(text: str) -> str:
        """
        Corrige les escapes invalides
        """
        if not text:
            return text
        
        # Supprimer caractères de contrôle
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', ' ', text)
        
        # ✅ CRUCIAL: \\' → ' (apostrophe n'a pas besoin d'escape)
        text = text.replace("\\'", "'")
        
        # Corriger autres escapes invalides
        def fix_escape(match):
            char_after = match.group(1)
            
            # Escapes valides à préserver
            if char_after in '"\\bfnrt/':
                return match.group(0)
            
            # \\u suivi de 4 hex
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
        """
        start_idx = response_text.find('{')
        
        if start_idx == -1:
            return None
        
        bracket_count = 0
        in_string = False
        escape_next = False
        
        for i in range(start_idx, len(response_text)):
            char = response_text[i]
            
            # Gérer les échappements
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
            
            # Compter les accolades HORS strings
            if not in_string:
                if char == '{':
                    bracket_count += 1
                elif char == '}':
                    bracket_count -= 1
                    
                    if bracket_count == 0:
                        extracted = response_text[start_idx:i+1]
                        return extracted
        
        # Si manquent des accolades fermantes
        if bracket_count > 0:
            return response_text[start_idx:] + '}' * bracket_count
        
        return None
    
    @staticmethod
    def _clean_json(json_str: str) -> str:
        """
        Nettoie le JSON
        """
        start_idx = json_str.find('{')
        end_idx = json_str.rfind('}')
        
        if start_idx == -1 or end_idx == -1:
            return None
        
        result = json_str[start_idx:end_idx+1]
        
        # Supprimer virgules traînantes
        result = re.sub(r',(\s*})', r'\1', result)
        result = re.sub(r',(\s*])', r'\1', result)
        
        # Fix escapes
        result = RobustJSONParser._fix_invalid_escapes(result)
        
        return result
    
    @staticmethod
    def _aggressive_clean(json_str: str) -> str:
        """
        Nettoyage agressif final
        """
        start = json_str.find('{')
        end = json_str.rfind('}')
        
        if start == -1 or end == -1:
            return None
        
        result = json_str[start:end+1]
        
        # Nettoyer
        result = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', ' ', result)
        result = re.sub(r',(\s*[}\]])', r'\1', result)
        result = RobustJSONParser._fix_invalid_escapes(result)
        
        return result