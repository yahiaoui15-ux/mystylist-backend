"""
Token Counter Utility v1.0
Compte les tokens détaillés pour CHAQUE appel OpenAI
Aide à ajuster le prompt si besoin sans exploser le budget
"""

import tiktoken

class TokenCounter:
    """Utilitaire pour compter et logger les tokens OpenAI"""
    
    def __init__(self, model: str = "gpt-4-turbo"):
        """
        Init le compteur pour un modèle spécifique
        
        Args:
            model: "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo", etc.
        """
        self.model = model
        self.encoding = tiktoken.encoding_for_model(model)
        self.MAX_TOKENS = 4000  # Budget max pour colorimetry
        
    def count_tokens(self, text: str) -> int:
        """Compte les tokens dans un texte"""
        return len(self.encoding.encode(text))
    
    def count_messages(self, messages: list) -> int:
        """
        Compte les tokens dans une liste de messages (format OpenAI)
        
        Args:
            messages: Liste de {"role": "...", "content": "..."}
        
        Returns:
            Nombre total de tokens
        """
        total = 0
        for msg in messages:
            # Ajouter overhead par message (~4 tokens)
            total += 4
            
            if isinstance(msg["content"], str):
                # Texte simple
                total += self.count_tokens(msg["content"])
            elif isinstance(msg["content"], list):
                # Content avec images (vision)
                for item in msg["content"]:
                    if item["type"] == "text":
                        total += self.count_tokens(item["text"])
                    elif item["type"] == "image_url":
                        # Images coûtent cher: ~250-800 tokens selon résolution
                        # Estimation: 255 tokens pour image 512x512
                        total += 255
        
        return total
    
    def log_colorimetry_call(self, system_prompt: str, user_prompt: str, image_urls: list, max_output_tokens: int = 4000):
        """
        Log détaillé pour appel colorimetry (Vision)
        
        Args:
            system_prompt: Le system prompt
            user_prompt: Le user prompt avec {placeholders} remplacés
            image_urls: Liste des URLs d'images
            max_output_tokens: Max tokens attendus en sortie
        """
        print("\n" + "="*80)
        print("🔤 TOKEN COUNTER - Appel OpenAI Colorimetry")
        print("="*80)
        
        # Compter system prompt
        system_tokens = self.count_tokens(system_prompt)
        print(f"\n📝 System Prompt: {system_tokens} tokens")
        print(f"   {system_prompt[:100]}...")
        
        # Compter user prompt
        user_tokens = self.count_tokens(user_prompt)
        print(f"\n📝 User Prompt: {user_tokens} tokens")
        print(f"   {user_prompt[:100]}...")
        
        # Compter images
        image_tokens = len(image_urls) * 255  # Estimation
        print(f"\n🖼️  Images: {len(image_urls)} × ~255 tokens = {image_tokens} tokens")
        
        # Overhead OpenAI
        overhead = 10  # Overhead général
        
        # Total input
        total_input = system_tokens + user_tokens + image_tokens + overhead
        
        print(f"\n📊 INPUT TOTAL: {total_input} tokens")
        input_percent = (total_input / self.MAX_TOKENS) * 100
        print(f"   Utilisation: {input_percent:.1f}% du budget")
        
        # Tokens restants pour output
        remaining = self.MAX_TOKENS - total_input
        print(f"\n📊 OUTPUT BUDGET: {remaining} tokens ({(remaining/self.MAX_TOKENS)*100:.1f}%)")
        print(f"   Max tokens demandés: {max_output_tokens}")
        
        # Vérification
        if total_input >= self.MAX_TOKENS * 0.9:
            print(f"\n⚠️  WARNING: Proche de la limite! ({total_input}/{self.MAX_TOKENS})")
            print(f"   Risque de troncature ou token limit error")
            return False
        
        if remaining < 1000:
            print(f"\n⚠️  WARNING: Output budget serré! Seulement {remaining} tokens")
            print(f"   Les réponses longues seront tronquées")
            return False
        
        print(f"\n✅ BUDGET OK - {remaining} tokens disponibles pour la réponse")
        print("="*80 + "\n")
        
        return True
    
    def log_completion_tokens(self, prompt_tokens: int, completion_tokens: int):
        """
        Log les tokens utilisés après réception réponse OpenAI
        
        Args:
            prompt_tokens: Tokens consommés par le prompt
            completion_tokens: Tokens consommés par la réponse
        """
        print("\n" + "="*80)
        print("🔤 TOKEN USAGE - Résultat Réel")
        print("="*80)
        
        total = prompt_tokens + completion_tokens
        
        print(f"\n📊 Prompt Tokens: {prompt_tokens}")
        print(f"📊 Completion Tokens: {completion_tokens}")
        print(f"📊 TOTAL: {total} tokens")
        
        usage_percent = (total / self.MAX_TOKENS) * 100
        print(f"\n📊 Utilisation du budget: {usage_percent:.1f}%")
        
        if usage_percent >= 100:
            print(f"\n❌ ERREUR: Dépassement du budget!")
        elif usage_percent >= 90:
            print(f"\n⚠️  WARNING: Approche de la limite ({total}/{self.MAX_TOKENS})")
        else:
            print(f"\n✅ NORMAL: {(self.MAX_TOKENS - total)} tokens restants")
        
        print("="*80 + "\n")
    
    def estimate_json_output_size(self) -> int:
        """
        Estime le nombre de tokens pour la réponse JSON colorimetry
        
        Returns:
            Estimation en tokens
        """
        # Structure estimée:
        # - Palette: 12 couleurs × 50 tokens = 600
        # - Notes: 19 couleurs × 30 tokens = 570
        # - Associations: 5 × 40 tokens = 200
        # - Guide maquillage: 100
        # - Analyse détaillée: 300
        # - Autres champs: 100
        
        return 1870  # Estimation conservatrice


# Instance globale
token_counter = TokenCounter(model="gpt-4-turbo")