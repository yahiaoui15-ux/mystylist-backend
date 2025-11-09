import httpx
import os
from datetime import datetime

class PDFGenerationService:
    def __init__(self, pdfmonkey_api_key: str = None):
        self.api_key = pdfmonkey_api_key or os.getenv("PDFMONKEY_API_KEY")
        self.pdfmonkey_url = "https://api.pdfmonkey.io/api/v1"
        # Template ID fixé: 4D4A47D1-361F-4133-B998-188B6AB08A37
        self.template_id = "4D4A47D1-361F-4133-B998-188B6AB08A37"
    
    async def generate_report_pdf(self, pdfmonkey_payload: dict) -> str:
        """
        Génère un PDF via PDFMonkey
        
        Args:
            pdfmonkey_payload: dict mappé avec variables Liquid pour le template
        
        Returns:
            str: URL du PDF généré
        """
        try:
            print("📄 Génération PDF via PDFMonkey...")
            print(f"   Template ID: {self.template_id}")
            
            # Préparer le payload pour PDFMonkey
            payload = {
                "document": {
                    "document_template_id": self.template_id,
                    "status": "success",
                    "file_format": "pdf",
                    "meta": {
                        "user_id": pdfmonkey_payload.get("user", {}).get("email", "unknown"),
                        "created_at": datetime.now().isoformat()
                    },
                    "payload": pdfmonkey_payload  # Variables Liquid directement
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
            
            if response.status_code not in [200, 201]:
                print(f"❌ Erreur PDFMonkey: {response.status_code}")
                print(f"   Response: {response.text[:500]}")
                raise Exception(f"PDFMonkey error: {response.status_code}")
            
            result = response.json()
            document = result.get("document", {})
            pdf_url = document.get("download_url")
            doc_id = document.get("id", "unknown")
            
            if not pdf_url:
                print(f"❌ Pas de download_url dans la réponse PDFMonkey")
                print(f"   Response: {result}")
                raise Exception("Pas de download_url dans la réponse PDFMonkey")
            
            print(f"✅ PDF généré avec succès!")
            print(f"   ID: {doc_id}")
            print(f"   URL: {pdf_url[:80]}...")
            
            return pdf_url
            
        except Exception as e:
            print(f"❌ Erreur génération PDF: {e}")
            raise
    
    async def upload_pdf_to_supabase(self, pdf_url: str, user_id: str) -> str:
        """
        Télécharge le PDF dans Supabase Storage (optionnel pour MVP)
        
        Args:
            pdf_url: URL du PDF généré par PDFMonkey
            user_id: ID de l'utilisateur
        
        Returns:
            str: URL Supabase du PDF
        """
        try:
            print(f"☁️  Stockage PDF à Supabase Storage...")
            
            # Pour MVP: on peut directement utiliser l'URL PDFMonkey
            # TODO: Implémenter l'upload réel si besoin de persistance locale
            
            storage_url = pdf_url  # Pour l'instant, on utilise directement PDFMonkey
            
            print(f"✅ PDF accessible via: {storage_url[:50]}...")
            return storage_url
            
        except Exception as e:
            print(f"❌ Erreur stockage PDF: {e}")
            # Non-bloquant: on retourne l'URL PDFMonkey directement
            return pdf_url

# Instance globale
pdf_service = PDFGenerationService()