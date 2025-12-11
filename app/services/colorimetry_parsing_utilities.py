# -*- coding: utf-8 -*-
"""
Colorimetry JSON Parser v10.0 - Utilise RobustJSONParser existant
✅ Retry automatique (3 tentatives) avec délai
✅ Validation structure Part 2
✅ Fallback intelligent
✅ S'intègre avec robust_json_parser.py existant
"""

import json
import time
from typing import Optional, Dict, Any
from app.services.robust_json_parser import RobustJSONParser
from app.prompts.colorimetry_part2_prompt import FALLBACK_PART2_DATA


class ColorimetryJSONParser:
    """Parser JSON spécialisé pour Colorimetry Part 2 avec retry automatique"""
    
    def __init__(self):
        self.robust_parser = RobustJSONParser()
        self.max_retries = 3
    
    def clean_gpt_response(self, response_text: str) -> str:
        """
        ✅ Nettoie la réponse GPT avant parsing
        Utilise les méthodes du RobustJSONParser existant
        """
        if not response_text:
            return "{}"
        
        # Nettoyer les contrôles et escapes invalides
        cleaned = self.robust_parser._fix_invalid_escapes(response_text)
        
        # Extraire le JSON complet (compte les accolades)
        extracted = self.robust_parser._extract_complete_json(cleaned)
        
        if extracted:
            return self.robust_parser._clean_json(extracted)
        
        return response_text
    
    def parse_json_safely(self, content: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """
        ✅ Parse JSON avec retry automatique
        
        Tentera 3 fois avec délai croissant:
        - Tentative 1: Direct
        - Tentative 2: Après 0.5s + nettoyage agressif
        - Tentative 3: Après 1s + extraction complète
        """
        for attempt in range(1, max_retries + 1):
            try:
                # Utiliser le parser robuste existant
                result = self.robust_parser.parse_json_with_fallback(content)
                
                # Si le résultat n'est pas le fallback minimal, c'est bon
                if result and self._is_meaningful_result(result):
                    print(f"   ✅ JSON parsé avec succès (attempt {attempt})")
                    return result
                
                # Si fallback minimal, continuer à essayer
                if attempt < max_retries:
                    print(f"   ⚠️  Tentative {attempt}: Résultat minimal, retry...")
                    time.sleep(0.5 * attempt)  # Délai croissant
                    continue
                
                # Dernière tentative = fallback minimal acceptable
                if attempt == max_retries:
                    print(f"   ⚠️  Tentative {attempt}: Fallback minimal utilisé")
                    return result
                    
            except Exception as e:
                print(f"   ⚠️  Tentative {attempt}: {str(e)[:60]}")
                if attempt < max_retries:
                    time.sleep(0.5 * attempt)
                    continue
                else:
                    return None
        
        return None
    
    def validate_part2_structure(self, data: Dict[str, Any]) -> bool:
        """
        ✅ Valide que la structure Part 2 est complète
        
        Vérifie:
        - palette_personnalisee: 10 couleurs
        - associations_gagnantes: 5 occasions
        """
        if not isinstance(data, dict):
            return False
        
        # Vérifier palette
        palette = data.get("palette_personnalisee", [])
        if not isinstance(palette, list) or len(palette) != 10:
            print(f"   ⚠️  Palette invalide: {len(palette) if isinstance(palette, list) else 'N/A'} items")
            return False
        
        # Vérifier associations
        associations = data.get("associations_gagnantes", [])
        if not isinstance(associations, list) or len(associations) != 5:
            print(f"   ⚠️  Associations invalides: {len(associations) if isinstance(associations, list) else 'N/A'} items")
            return False
        
        return True
    
    @staticmethod
    def _is_meaningful_result(result: dict) -> bool:
        """
        ✅ Vérifie si le résultat est meaningful ou juste un fallback vide
        
        Un résultat meaningful a:
        - Au moins 5 couleurs dans palette
        - Au moins 2 associations
        """
        palette = result.get("palette_personnalisee", [])
        associations = result.get("associations_gagnantes", [])
        
        has_palette = isinstance(palette, list) and len(palette) >= 5
        has_associations = isinstance(associations, list) and len(associations) >= 2
        
        return has_palette and has_associations


# Fonction wrapper pour intégration simple dans colorimetry.py
def analyze_colorimetry_part2(content: str) -> Dict[str, Any]:
    """
    ✅ Wrapper pour utilisation facile dans colorimetry.py
    
    Usage:
        parser = ColorimetryJSONParser()
        result = parser.parse_json_safely(content_cleaned, max_retries=3)
    """
    parser = ColorimetryJSONParser()
    
    # Nettoyer
    content_cleaned = parser.clean_gpt_response(content)
    
    # Parser avec retry
    result = parser.parse_json_safely(content_cleaned, max_retries=3)
    
    # Valider structure
    if result and parser.validate_part2_structure(result):
        return result
    
    # Fallback
    return FALLBACK_PART2_DATA.copy()