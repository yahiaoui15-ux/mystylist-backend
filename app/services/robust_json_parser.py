"""
JSON Parser Minimal - Version simple et robuste
Gère les strings malformées et caractères spéciaux
"""

import json
import re


class RobustJSONParser:
    """Parser JSON robuste - Simple et fiable"""
    
    @staticmethod
    def parse_json_with_fallback(response_text: str) -> dict:
        """
        Parse JSON avec 3 stratégies de fallback
        
        Retourne TOUJOURS un dict (jamais d'exception)
        """
        print("\n📋 Parsing JSON robuste:")
        
        # STRATÉGIE 1: Parser direct
        print("   Tentative 1: Parsing direct...")
        try:
            data = json.loads(response_text)
            print("      ✅ JSON valide!")
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
        
        # STRATÉGIE 3: Extraction partielle
        print("   Tentative 3: Extraction partielle...")
        try:
            match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text)
            if match:
                partial = match.group(0)
                data = json.loads(partial)
                print("      ✅ Extraction partielle valide!")
                return data
        except Exception:
            print("      ❌ Extraction échouée")
        
        # FALLBACK: Retourner dict minimal
        print("   Tentative 4: Fallback minimal")
        print("      ⚠️ Retour données minimales")
        return {
            "saison_confirmee": "",
            "sous_ton_detecte": "",
            "justification_saison": "",
            "palette_personnalisee": [],
            "notes_compatibilite": {},
            "associations_gagnantes": [],
            "guide_maquillage": {},
            "shopping_couleurs": {},
            "alternatives_couleurs_refusees": {},
            "eye_color": "",
            "hair_color": ""
        }
    
    @staticmethod
    def _clean_json(json_str: str) -> str:
        """Nettoie le JSON pour le rendre parsable"""
        
        # Extraire le JSON (du premier { au dernier })
        start_idx = json_str.find('{')
        end_idx = json_str.rfind('}')
        
        if start_idx == -1 or end_idx == -1:
            return "{}"
        
        result = json_str[start_idx:end_idx+1]
        
        # Consolider les multi-lignes
        result = result.replace('\n', ' ').replace('\r', ' ')
        
        # Corriger les strings non terminées avant , } ou ]
        result = re.sub(r'": "([^"]*?)([,}])', r'": "\1"\2', result)
        
        # Supprimer les virgules traînantes
        result = re.sub(r',(\s*})', r'\1', result)
        result = re.sub(r',(\s*])', r'\1', result)
        
        # Ajouter les virgules manquantes
        result = re.sub(r'([\}\])"', r'\1,"', result)
        
        return result