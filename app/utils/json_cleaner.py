"""
Module de nettoyage JSON robuste pour gérer les caractères de contrôle invalides
Résout le problème: "Invalid control character" dans OpenAI responses
"""
import re
import json

def clean_json_response(response_text: str) -> str:
    """
    Nettoie une réponse JSON brute d'OpenAI en gérant les caractères de contrôle invalides.
    
    Problèmes gérés:
    - Sauts de ligne littéraux \n dans les strings (non échappés)
    - Sauts de ligne réels (vraies newlines) dans les strings
    - Caractères de contrôle invalides (char < 0x20)
    - Guillemets non échappés
    
    Args:
        response_text: Réponse brute d'OpenAI (potentiellement mal formée)
    
    Returns:
        String JSON valide et parseable
    """
    
    # Étape 1: Extraire uniquement le JSON (ignorer texte avant/après)
    response_text = response_text.strip()
    json_start = response_text.find('{')
    if json_start == -1:
        print(f"⚠️ Pas de {{ trouvé dans réponse OpenAI")
        return "{}"
    
    response_text = response_text[json_start:]
    json_end = response_text.rfind('}')
    if json_end == -1:
        print(f"⚠️ Pas de }} trouvé dans réponse OpenAI")
        return "{}"
    
    response_text = response_text[:json_end+1]
    
    # Étape 2: Traiter les caractères de contrôle invalides
    # Les caractères valides en JSON string sont >= 0x20 ou \t (0x09), \n (0x0A), \r (0x0D)
    # OpenAI parfois retourne des sauts de ligne RÉELS dans les strings (invalides)
    
    result = []
    i = 0
    in_string = False
    escape_next = False
    
    while i < len(response_text):
        char = response_text[i]
        code = ord(char)
        
        if escape_next:
            result.append(char)
            escape_next = False
            i += 1
            continue
        
        if char == '\\' and in_string:
            result.append(char)
            escape_next = True
            i += 1
            continue
        
        if char == '"':
            result.append(char)
            in_string = not in_string
            i += 1
            continue
        
        # Si on est dans une string et qu'on rencontre un caractère de contrôle invalide
        if in_string and code < 0x20 and code != 0x09:  # 0x09 = tab
            if code == 0x0A or code == 0x0D:  # newline ou carriage return
                # Remplacer par \n échappé
                result.append('\\n')
            else:
                # Ignorer les autres caractères de contrôle invalides
                print(f"⚠️ Caractère de contrôle invalide ignoré (char {code})")
            i += 1
            continue
        
        result.append(char)
        i += 1
    
    cleaned = ''.join(result)
    
    # Étape 3: Valider et parser
    try:
        parsed = json.loads(cleaned)
        return cleaned
    except json.JSONDecodeError as e:
        print(f"⚠️ Erreur parsing JSON après nettoyage: {e}")
        print(f"   Position: {e.pos}")
        print(f"   Snippet: {cleaned[max(0, e.pos-50):min(len(cleaned), e.pos+50)]}")
        
        # Dernière tentative: regex aggressive pour remplacer tous les newlines dans les strings
        # Pattern: chercher "...text\ntext..." et remplacer \n par \\n
        
        # Approche brute force: utiliser ast.literal_eval si json.loads échoue
        try:
            # Remplacer tous les sauts de ligne réels par des espaces
            cleaned2 = cleaned.replace('\n', ' ').replace('\r', ' ')
            parsed = json.loads(cleaned2)
            return cleaned2
        except:
            print(f"❌ Impossible de nettoyer le JSON")
            return "{}"


def repair_json_string_content(text: str) -> str:
    """
    Alternative: Réparer les strings JSON qui contiennent des newlines littérales.
    
    Utilise une approche regex pour trouver les patterns invalides.
    """
    # Pattern: chercher "xxx" où xxx peut contenir des newlines
    # Remplacer les newlines non échappées par \n
    
    def replace_newlines_in_strings(match):
        content = match.group(1)
        # Remplacer les sauts de ligne réels par des \n échappés
        content = content.replace('\n', '\\n').replace('\r', '\\r')
        return f'"{content}"'
    
    # Chercher toutes les strings avec newlines
    # ATTENTION: ce pattern ne fonctionne pas parfaitement avec les quotes imbriquées
    # mais c'est une approche brute-force acceptable
    pattern = r'"((?:[^"\\]|\\.)*?(?:\n|\r)(?:[^"\\]|\\.)*?)"'
    
    text = re.sub(pattern, replace_newlines_in_strings, text, flags=re.DOTALL)
    
    return text


# Test
if __name__ == "__main__":
    # Test avec un JSON cassé (sauts de ligne dans string)
    broken_json = '''{
    "color": "Bleu clair
    avec description",
    "value": 123
}'''
    
    print("JSON cassé:")
    print(broken_json)
    print("\nJSON nettoyé:")
    cleaned = clean_json_response(broken_json)
    print(cleaned)
    
    try:
        result = json.loads(cleaned)
        print("\n✅ Parsé avec succès:")
        print(result)
    except Exception as e:
        print(f"\n❌ Erreur: {e}")