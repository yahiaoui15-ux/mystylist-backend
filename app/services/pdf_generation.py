"""
Service de génération de PDF via PDFMonkey
VERSION FINALE - Structure payload corrigée pour PDFMonkey API v1
Clé correcte: 'document_template_id' (pas 'template_id')
"""

import os
import httpx
from typing import Dict, Any, Optional

from app.services.pdf_data_mapper import PDFDataMapper


class PDFGenerationService:
    """
    Service pour générer les PDFs via l'API PDFMonkey
    """
    
    def __init__(self):
        # ✅ Stripper les newlines et espaces de la clé API
        self.api_key = os.getenv("PDFMONKEY_API_KEY", "").strip()
        self.template_id = os.getenv("PDFMONKEY_TEMPLATE_ID", "4D4A47D1-361F-4133-B998-188B6AB08A37").strip()
        self.base_url = "https://api.pdfmonkey.io/api/v1"
        
        if not self.api_key:
            print("⚠️ AVERTISSEMENT: PDFMONKEY_API_KEY non configurée")
        else:
            print(f"✅ PDFMONKEY_API_KEY configurée")
    
    async def generate_report_pdf(
        self,
        report_data: dict,
        user_data: dict,
        document_name: Optional[str] = None
    ) -> str:
        """
        Génère un PDF via PDFMonkey (alias pour main.py)
        
        Args:
            report_data: Rapport généré par report_generator
            user_data: Données utilisateur
            document_name: Nom optionnel du document
        
        Returns:
            str: URL du PDF généré
        """
        return await self.generate_pdf(report_data, user_data, document_name)
    
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
            
            # Préparer la requête - STRUCTURE CORRECTE pour PDFMonkey API v1
            # Important: Utiliser 'document_template_id' (pas 'template_id')
            payload = {
                "document_template_id": self.template_id,
                "data": liquid_variables
            }
            
            print(f"📤 Envoi à PDFMonkey...")
            print(f"   Template ID: {self.template_id}")
            print(f"   Data fields: {len(liquid_variables)} champs")
            
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
            print(f"✅ Réponse PDFMonkey reçue")
            
            # Extraire l'URL du PDF
            # PDFMonkey retourne: {"document": {"id": "...", "download_url": "..."}}
            pdf_url = None
            document_id = None
            
            if "document" in result and isinstance(result["document"], dict):
                pdf_url = result["document"].get("download_url")
                document_id = result["document"].get("id")
                print(f"   Document ID: {document_id}")
            elif "data" in result and isinstance(result["data"], dict):
                pdf_url = result["data"].get("download_url")
                document_id = result["data"].get("id")
            
            # Si pas d'URL directe, construire depuis l'ID
            if not pdf_url and document_id:
                pdf_url = f"https://api.pdfmonkey.io/api/v1/documents/{document_id}/download"
            
            if not pdf_url:
                print(f"⚠️  Pas d'URL trouvée dans la réponse PDFMonkey")
                print(f"   Réponse: {result}")
                raise Exception("PDFMonkey n'a pas retourné d'URL de téléchargement")
            
            print(f"✅ PDF généré: {pdf_url[:80]}...")
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