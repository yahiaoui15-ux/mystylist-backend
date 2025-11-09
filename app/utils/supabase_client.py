from supabase import create_client
from app.config import SUPABASE_URL, SUPABASE_KEY

class SupabaseClient:
    def __init__(self):
        self.client = None
    
    def _get_client(self):
        """Initialise le client à la première utilisation"""
        if self.client is None:
            self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return self.client
    
    async def get_user_profile(self, user_id: str):
        """Récupère le profil utilisateur"""
        try:
            client = self._get_client()
            response = client.table("user_profiles").select("*").eq("user_id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"❌ Erreur Supabase: {e}")
            return None
    
    async def get_visuels(self, category: str, cut_key: str):
        """Récupère les visuels pédagogiques"""
        try:
            client = self._get_client()
            response = client.table("visuels").select("*").eq("category", category).eq("cut_key", cut_key).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"❌ Erreur visuels: {e}")
            return None
    
    async def query_table(self, table: str, filters: dict = None):
        """Requête générique sur une table"""
        try:
            client = self._get_client()
            query = client.table(table).select("*")
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            response = query.execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"❌ Erreur query {table}: {e}")
            return []

# Instance globale
supabase = SupabaseClient()