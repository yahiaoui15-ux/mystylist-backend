from datetime import datetime
from app.utils.supabase_client import supabase

class SupabaseReportsService:
    def __init__(self):
        self.supabase = supabase
    
    async def save_report_metadata(self, user_id: str, report_data: dict, pdf_url: str = None) -> dict:
        """
        Sauvegarde les métadonnées du rapport à Supabase
        
        Args:
            user_id: ID de l'utilisateur
            report_data: dict complet du rapport
            pdf_url: URL du PDF généré
        
        Returns:
            dict avec report_id et status
        """
        try:
            print("💾 Sauvegarde rapport à Supabase...")
            
            # Préparer les données pour Supabase
            report_record = {
                "user_id": user_id,
                "user_email": report_data.get("user_email"),
                "user_name": report_data.get("user_name"),
                "season": report_data.get("colorimetry", {}).get("season"),
                "silhouette_type": report_data.get("morphology", {}).get("silhouette_type"),
                "colorimetry_data": report_data.get("colorimetry", {}),
                "morphology_data": report_data.get("morphology", {}),
                "styling_data": report_data.get("styling", {}),
                "visuals_data": report_data.get("visuals", {}),
                "products_data": report_data.get("products", {}),
                "pdf_url": pdf_url,
                "created_at": datetime.now().isoformat(),
                "status": "completed"
            }
            
            # Insérer dans la table reports - UTILISER supabase.insert_table()
            result = self.supabase.insert_table("reports", report_record)
            
            if result:
                report_id = result[0].get("id") if isinstance(result, list) else result.get("id")
                print(f"✅ Rapport sauvegardé: {report_id}")
                return {
                    "report_id": report_id,
                    "status": "success"
                }
            else:
                print("❌ Erreur insertion rapport")
                return {"status": "error"}
            
        except Exception as e:
            print(f"❌ Erreur sauvegarde rapport: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_user_reports(self, user_id: str) -> list:
        """Récupère tous les rapports d'un utilisateur"""
        try:
            response = self.supabase.query("reports", select_fields="*", filters={"user_id": user_id})
            return response.data or []
        except Exception as e:
            print(f"❌ Erreur récupération rapports: {e}")
            return []
    
    async def get_report_by_id(self, report_id: str) -> dict:
        """Récupère un rapport spécifique"""
        try:
            response = self.supabase.query("reports", select_fields="*", filters={"id": report_id})
            return response.data[0] if response.data else {}
        except Exception as e:
            print(f"❌ Erreur récupération rapport {report_id}: {e}")
            return {}

# Instance globale
supabase_reports_service = SupabaseReportsService()