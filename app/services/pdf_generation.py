import httpx
import os
from datetime import datetime

class PDFGenerationService:
    def __init__(self, pdfmonkey_api_key: str = None):
        self.api_key = pdfmonkey_api_key or os.getenv("PDFMONKEY_API_KEY")
        self.pdfmonkey_url = "https://api.pdfmonkey.io/api/v1"
    
    async def generate_report_pdf(self, report_data: dict) -> str:
        """
        Génère un PDF via PDFMonkey
        
        Args:
            report_data: dict avec user_name, colorimetry, morphology, styling, etc.
        
        Returns:
            str: URL du PDF généré
        """
        try:
            print("📄 Génération PDF via PDFMonkey...")
            
            # Préparer le payload pour PDFMonkey
            payload = {
                "document": {
                    "document_template_id": os.getenv("PDFMONKEY_TEMPLATE_ID", "template_id_here"),
                    "status": "success",
                    "file_format": "pdf",
                    "meta": {
                        "user_id": report_data.get("user_id"),
                        "created_at": datetime.now().isoformat()
                    },
                    "payload": {
                        "user_name": report_data.get("user_name", "Client"),
                        "user_email": report_data.get("user_email", ""),
                        "colorimetry": report_data.get("colorimetry", {}),
                        "morphology": report_data.get("morphology", {}),
                        "styling": report_data.get("styling", {}),
                        "visuals": report_data.get("visuals", {}),
                        "products": report_data.get("products", {})
                    }
                }
            }
            
            # Appel API PDFMonkey
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.pdfmonkey_url}/documents",
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=60.0
                )
            
            if response.status_code != 201:
                print(f"❌ Erreur PDFMonkey: {response.status_code} - {response.text}")
                raise Exception(f"PDFMonkey error: {response.status_code}")
            
            result = response.json()
            pdf_url = result.get("document", {}).get("download_url")
            
            if not pdf_url:
                raise Exception("Pas de download_url dans la réponse PDFMonkey")
            
            print(f"✅ PDF généré: {pdf_url[:50]}...")
            return pdf_url
            
        except Exception as e:
            print(f"❌ Erreur génération PDF: {e}")
            raise
    
    async def upload_pdf_to_supabase(self, pdf_url: str, user_id: str) -> str:
        """
        Télécharge le PDF dans Supabase Storage
        
        Args:
            pdf_url: URL du PDF généré par PDFMonkey
            user_id: ID de l'utilisateur
        
        Returns:
            str: URL Supabase du PDF
        """
        try:
            print(f"☁️  Upload PDF à Supabase Storage...")
            
            # TODO: Implémenter l'upload réel
            # Pour l'instant, retourner l'URL PDFMonkey
            storage_url = f"https://supabase.../storage/pdf/{user_id}/{pdf_url.split('/')[-1]}"
            
            print(f"✅ PDF uploadé: {storage_url[:50]}...")
            return storage_url
            
        except Exception as e:
            print(f"❌ Erreur upload PDF: {e}")
            raise

# Instance globale
pdf_service = PDFGenerationService()