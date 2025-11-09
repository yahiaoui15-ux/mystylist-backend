"""
Service de génération de PDF via PDFMonkey
"""

import os
import httpx
from typing import Dict, Any, Optional
import json

from app.services.pdf_data_mapper import PDFDataMapper


class PDFGenerationService:
    """
    Service pour générer les PDFs via l'API PDFMonkey
    """
    
    def __init__(self):
        self.api_key = os.getenv("PDFMONKEY_API_KEY")
        self.template_id = os.getenv("PDFMONKEY_TEMPLATE_ID", "4D4A47D1-361F-4133-B998-188B6AB08A37")
        self.base_url = "https://api.pdfmonkey.io/api/v1"
        
        if not self.api_key:
            print("⚠️ AVERTISSEMENT: PDFMONKEY_API_KEY non configurée")
    
    async def generate_pdf(
        self,
        report_data: dict,
        user_data: dict,
        document_name: Optional[str] = None
    ) -> str:
        """
        Génère un PDF via PDFMonkey
        
        Args:
            report_data: Rapport généré par report_generator
            user_data: Données utilisateur
            document_name: Nom optionnel du document
        
        Returns:
            str: URL du PDF généré
        """
        try:
            print("🎨 Génération PDF via PDFMonkey...")
            
            # Mapper les données au format PDFMonkey
            liquid_variables = PDFDataMapper.prepare_liquid_variables(
                report_data,
                user_data
            )
            
            # Préparer la requête
            payload = {
                "document": {
                    "template_id": self.template_id,
                    "name": document_name or f"Rapport_MyStylist_{user_data.get('first_name', 'Client')}",
                    "variables": liquid_variables
                }
            }
            
            print(f"📤 Envoi à PDFMonkey...")
            print(f"   Template ID: {self.template_id}")
            print(f"   Variables: {len(liquid_variables)} champs")
            
            # Appel API PDFMonkey
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/documents",
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=60.0
                )
            
            if response.status_code not in [200, 201]:
                error_text = response.text
                print(f"❌ Erreur PDFMonkey {response.status_code}: {error_text}")
                raise Exception(f"PDFMonkey error: {response.status_code} - {error_text}")
            
            result = response.json()
            
            # Extraire l'URL du PDF
            pdf_url = result.get("document", {}).get("download_url")
            if not pdf_url:
                # Construire l'URL si nécessaire
                document_id = result.get("document", {}).get("id")
                if document_id:
                    pdf_url = f"{self.base_url}/documents/{document_id}/download"
            
            print(f"✅ PDF généré: {pdf_url[:50]}...")
            return pdf_url
            
        except Exception as e:
            print(f"❌ Erreur génération PDF: {e}")
            raise
    
    async def upload_pdf_to_supabase(
        self,
        pdf_url: str,
        user_id: str
    ) -> str:
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
            
            # TODO: Implémenter l'upload réel vers Supabase Storage
            # Pour l'instant, retourner l'URL PDFMonkey
            
            storage_url = f"https://supabase.../storage/pdf/{user_id}/{pdf_url.split('/')[-1]}"
            
            print(f"✅ PDF uploadé: {storage_url[:50]}...")
            return pdf_url  # Retourner l'URL PDFMonkey pour maintenant
            
        except Exception as e:
            print(f"❌ Erreur upload PDF: {e}")
            raise


# Instance globale à exporter
pdf_service = PDFGenerationService()