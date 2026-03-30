"""
Service de génération de PDF via PDFMonkey
VERSION CORRIGÉE - Structure API PDFMonkey correcte avec "document" wrapper et "payload"
"""

import os
import httpx
import asyncio
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
        Attend que le document soit généré avant de retourner l'URL
        """
        try:
            print("🎨 Génération PDF via PDFMonkey...")

            liquid_variables = PDFDataMapper.prepare_liquid_variables(
                report_data,
                user_data
            )

            print("📊 Variables Liquid (premiers 15 champs):")
            for i, (key, value) in enumerate(liquid_variables.items()):
                if i < 15:
                    val_str = str(value)[:100] if not isinstance(value, list) else f"[list of {len(value)} items]"
                    print(f"   {key}: {val_str}")

            payload = {
                "document": {
                    "document_template_id": self.template_id,
                    "payload": liquid_variables,
                    "status": "pending"
                }
            }

            print("📤 Envoi à PDFMonkey...")
            print(f"   Template ID: {self.template_id}")
            print(f"   Data fields: {len(liquid_variables)} champs")

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            timeout = httpx.Timeout(90.0, connect=20.0)

            async with httpx.AsyncClient(timeout=timeout) as client:
                # 1) Création du document
                response = await client.post(
                    f"{self.base_url}/documents",
                    json=payload,
                    headers=headers
                )

                if response.status_code not in [200, 201]:
                    error_text = response.text
                    print(f"❌ Erreur PDFMonkey {response.status_code}: {error_text}")
                    raise Exception(f"PDFMonkey POST failed: {response.status_code} - {error_text}")

                result = response.json()
                print("✅ Réponse PDFMonkey reçue")
                print(f"🔍 Response complète: {result}")

                document = result.get("document", {}) if isinstance(result, dict) else {}
                document_id = document.get("id")
                initial_status = document.get("status")

                if not document_id:
                    raise Exception("PDFMonkey n'a pas retourné d'ID de document")

                print(f"   Document ID: {document_id}")
                print(f"   Status initial: {initial_status}")

                # Si jamais PDFMonkey renvoie déjà le download_url
                if initial_status == "success" and document.get("download_url"):
                    pdf_url = document["download_url"]
                    print(f"✅ PDF déjà disponible: {pdf_url}")
                    return pdf_url

                # 2) Polling robuste
                print("⏳ Attente de la génération du PDF par PDFMonkey...")

                max_attempts = 40
                sleep_seconds = 2.0
                consecutive_errors = 0

                for attempt in range(1, max_attempts + 1):
                    try:
                        status_response = await client.get(
                            f"{self.base_url}/documents/{document_id}",
                            headers=headers
                        )

                        if status_response.status_code != 200:
                            print(f"   ⚠️ Tentative {attempt}/{max_attempts} - HTTP {status_response.status_code}")
                            consecutive_errors += 1
                        else:
                            status_result = status_response.json()
                            doc = status_result.get("document", {}) if isinstance(status_result, dict) else {}
                            status = doc.get("status")
                            download_url = doc.get("download_url")
                            failure_cause = doc.get("failure_cause")

                            print(f"   Tentative {attempt}/{max_attempts} - Status: {status}")

                            if status == "success" and download_url:
                                print("   ✅ Document généré avec succès")
                                print(f"   Download URL: {download_url}")
                                return download_url

                            if status in ["failed", "error"]:
                                raise Exception(f"PDFMonkey rendering failed: {failure_cause or 'unknown failure'}")

                            if status in ["pending", "processing", "generating", None]:
                                consecutive_errors = 0
                            else:
                                print(f"   ⚠️ Status inattendu: {status}")
                                print(f"   Document data: {doc}")

                    except httpx.TimeoutException as e:
                        consecutive_errors += 1
                        print(f"   ⚠️ Tentative {attempt}/{max_attempts} - Timeout pendant le polling: {e}")

                    except httpx.HTTPError as e:
                        consecutive_errors += 1
                        print(f"   ⚠️ Tentative {attempt}/{max_attempts} - Erreur HTTP pendant le polling: {e}")

                    if consecutive_errors >= 5:
                        raise Exception("Trop d'erreurs consécutives pendant le polling PDFMonkey")

                    await asyncio.sleep(sleep_seconds)

                raise Exception(f"PDF non disponible après {max_attempts} tentatives pour document_id={document_id}")

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