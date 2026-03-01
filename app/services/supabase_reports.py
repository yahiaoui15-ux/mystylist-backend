# app/services/supabase_reports.py

from datetime import datetime, timezone
from app.utils.supabase_client import supabase

class SupabaseReportsService:
    def __init__(self):
        self.supabase = supabase

    async def save_report_metadata(self, user_id: str, payment_id: str, report_data: dict, pdf_url: str = None) -> dict:
        try:
            print("💾 Sauvegarde rapport à Supabase...")

            color = report_data.get("colorimetry", {}) or {}
            morph = report_data.get("morphology", {}) or {}
            style = report_data.get("styling", {}) or {}

            report_record = {
                "user_id": user_id,
                "payment_id": payment_id,  # ✅ IMPORTANT (idempotence et lookup)
                "user_email": report_data.get("user_email"),
                "user_name": report_data.get("user_name"),

                # ✅ clés correctes
                "season": color.get("saison_confirmee"),
                "silhouette_type": morph.get("silhouette_type"),

                # ✅ JSON complets
                "colorimetry_data": color,
                "morphology_data": morph,
                "styling_data": style,
                "visuals_data": report_data.get("visuals", {}) or {},
                "products_data": report_data.get("products", {}) or {},

                "pdf_url": pdf_url,
                "status": "completed",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "email_sent": True,
            }

            result = self.supabase.insert_table("reports", report_record)

            if result:
                report_id = result[0].get("id") if isinstance(result, list) else result.get("id")
                print(f"✅ Rapport sauvegardé: {report_id}")
                return {"report_id": report_id, "status": "success"}

            print("❌ Erreur insertion rapport")
            return {"status": "error"}

        except Exception as e:
            print(f"❌ Erreur sauvegarde rapport: {e}")
            return {"status": "error", "error": str(e)}

supabase_reports_service = SupabaseReportsService()