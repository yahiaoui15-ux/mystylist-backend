from supabase import create_client
from app.config_prod import settings


class SupabaseClient:
    def __init__(self):
        self.client = None
    
    def _get_client(self):
        """Initialise le client à la première utilisation"""
        if self.client is None:
            try:
                self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
                print(f"✅ Client Supabase initialisé avec succès")
            except Exception as e:
                print(f"❌ Erreur lors de l'initialisation Supabase: {e}")
                self.client = None
        return self.client
    
    def query(self, table: str, select_fields: str = "*", filters: dict = None):
        """
        Exécute une query SELECT avec filtres optionnels.
        Retourne la response complète (avec .data et .error).
        
        Exemple:
            response = supabase.query("user_profiles", "*", {"user_id": "123"})
            if response.data:
                user = response.data[0]
        """
        try:
            client = self._get_client()
            if client is None:
                raise Exception("Client Supabase non initialisé")
            
            query_obj = client.table(table).select(select_fields)
            
            if filters:
                for key, value in filters.items():
                    query_obj = query_obj.eq(key, value)
            
            response = query_obj.execute()
            return response
        except Exception as e:
            print(f"❌ Erreur query {table}: {e}")
            raise
    
    def insert_table(self, table: str, data: dict):
        """
        Insère des données dans une table.
        Retourne les données insérées ou None en cas d'erreur.
        """
        try:
            client = self._get_client()
            if client is None:
                raise Exception("Client Supabase non initialisé")
            response = client.table(table).insert(data).execute()
            return response.data if response.data else None
        except Exception as e:
            print(f"❌ Erreur insert {table}: {e}")
            raise

    def get_client(self):
        """Expose le client Supabase natif (supabase-py)"""
        return self._get_client()

# ❌ SUPPRIMÉ: méthode upload_pdf (n'existe pas en Python)
# Utiliser PDFStorageManager.save_pdf_to_supabase() à la place (REST API HTTP)


# Instance globale
supabase = SupabaseClient()