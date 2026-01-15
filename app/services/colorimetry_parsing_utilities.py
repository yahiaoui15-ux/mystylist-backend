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
        Compatible avec RobustJSONParser actuel (pas de _fix_invalid_escapes/_extract_complete_json/_clean_json)
        """
        if not response_text:
            return "{}"

        cleaned = response_text

        # 1) retirer ```json ... ```
        cleaned = self.robust_parser._strip_code_fences(cleaned)

        # 2) extraire le bloc { ... }
        cleaned = self.robust_parser._extract_json_block(cleaned)

        # 3) échapper les retours ligne dans les strings JSON
        cleaned = self.robust_parser._escape_newlines_inside_strings(cleaned)

        return cleaned


    
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
    
    def parse_part3_json_safely(self, content: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """
        ✅ Parse Part 3 avec retry + logique 'meaningful' spécifique Part 3
        """
        for attempt in range(1, max_retries + 1):
            try:
                result = self.robust_parser.parse_json_with_fallback(content)

                if result and self._is_meaningful_part3_result(result):
                    print(f"   ✅ JSON Part 3 parsé avec succès (attempt {attempt})")
                    return result

                if attempt < max_retries:
                    print(f"   ⚠️  Tentative {attempt}: Part 3 vide/minimal, retry...")
                    time.sleep(0.5 * attempt)
                    continue

                # dernière tentative : retourner ce qu'on a (même minimal) pour ne pas crasher
                print(f"   ⚠️  Tentative {attempt}: Part 3 minimal utilisé")
                return result

            except Exception as e:
                print(f"   ⚠️  Tentative {attempt} (Part 3): {str(e)[:60]}")
                if attempt < max_retries:
                    time.sleep(0.5 * attempt)
                    continue
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
    
    def validate_part3_structure(self, data: Dict[str, Any]) -> bool:
        """
        ✅ Valide que la structure Part 3 est exploitable

        Vérifie:
        - guide_maquillage: dict (même si partiellement rempli)
        - nailColors: list
        - unwanted_colors: list (peut être vide)
        - notes_compatibilite: dict (peut être vide)
        """
        if not isinstance(data, dict):
            return False

        guide = data.get("guide_maquillage", None)
        if guide is None or not isinstance(guide, dict):
            print("   ⚠️  Part 3 invalide: guide_maquillage manquant ou non dict")
            return False

        nail_colors = data.get("nailColors", None)
        if nail_colors is None or not isinstance(nail_colors, list):
            print("   ⚠️  Part 3 invalide: nailColors manquant ou non list")
            return False

        unwanted = data.get("unwanted_colors", None)
        if unwanted is None or not isinstance(unwanted, list):
            print("   ⚠️  Part 3 invalide: unwanted_colors manquant ou non list")
            return False

        notes = data.get("notes_compatibilite", {})
        if notes is None:
            notes = {}
        if not isinstance(notes, dict):
            print("   ⚠️  Part 3 invalide: notes_compatibilite non dict")
            return False


    @staticmethod
    def _is_meaningful_part3_result(result: dict) -> bool:
        """
        ✅ Vérifie si le résultat Part 3 est meaningful

        Un Part 3 meaningful a au moins:
        - 1 champ non vide dans guide_maquillage, OU
        - >= 2 nailColors, OU
        - >= 8 notes_compatibilite (ou autre seuil selon ton prompt)
        """
        guide = result.get("guide_maquillage", {})
        nail_colors = result.get("nailColors", [])
        notes = result.get("notes_compatibilite", {})

        # compter champs non vides du guide
        guide_filled = 0
        if isinstance(guide, dict):
            guide_filled = sum(1 for v in guide.values() if isinstance(v, str) and v.strip())

        has_guide = guide_filled >= 2
        has_nails = isinstance(nail_colors, list) and len(nail_colors) >= 2
        has_notes = isinstance(notes, dict) and len(notes.keys()) >= 8

        return has_guide or has_nails or has_notes

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

def analyze_colorimetry_part3(content: str) -> Dict[str, Any]:
    """
    ✅ Wrapper pour utilisation facile dans colorimetry.py (Part 3)
    """
    parser = ColorimetryJSONParser()

    # Nettoyer
    content_cleaned = parser.clean_gpt_response(content)

    # Parser avec retry spécifique Part 3
    result = parser.parse_part3_json_safely(content_cleaned, max_retries=3)

    # Valider structure
    if result and parser.validate_part3_structure(result):
        return result

    # Fallback minimal Part 3
    return {
        "notes_compatibilite": {},
        "guide_maquillage": {},
        "nailColors": [],
        "unwanted_colors": [],
        "alternatives_couleurs_refusees": {},
    }
