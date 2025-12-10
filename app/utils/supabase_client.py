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
    
    def upload_pdf(self, bucket_name: str, file_path: str, file_data: bytes) -> str:
        """
        Upload un PDF dans Supabase Storage de manière PERMANENTE.
        
        Args:
            bucket_name (str): Nom du bucket (ex: "reports" ou "user-reports")
            file_path (str): Chemin du fichier dans le bucket (ex: "user_123/rapport_dec2025.pdf")
            file_data (bytes): Contenu du PDF en bytes
        
        Returns:
            str: URL publique du PDF (permanente, valable 2+ mois)
        
        Exemple:
            with open("rapport.pdf", "rb") as f:
                url = supabase.upload_pdf("reports", "user_123/rapport.pdf", f.read())
            print(f"PDF uploadé: {url}")
        """
        try:
            client = self._get_client()
            if client is None:
                raise Exception("Client Supabase non initialisé")
            
            # Upload le fichier dans Supabase Storage
            response = client.storage.from_(bucket_name).upload(file_path, file_data)
            
            print(f"✅ PDF uploadé avec succès: {file_path}")
            
            # Construire l'URL publique permanente
            # Format: https://supabase-url/storage/v1/object/public/bucket_name/file_path
            public_url = f"{settings.SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{file_path}"
            
            print(f"✅ URL public: {public_url}")
            
            return public_url
            
        except Exception as e:
            print(f"❌ Erreur upload PDF: {e}")
            raise


# Instance globale
supabase = SupabaseClient()