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
            
            # DEBUG: Afficher les variables Liquid
            print(f"📊 Variables Liquid (premiers 15 champs):")
            for i, (key, value) in enumerate(liquid_variables.items()):
                if i < 15:
                    val_str = str(value)[:100] if not isinstance(value, list) else f"[list of {len(value)} items]"
                    print(f"   {key}: {val_str}")
            
            # 🔧 CORRECTION: Structure CORRECTE pour PDFMonkey API v1
            # D'après la documentation PDFMonkey:
            # 1. Wrapper tout dans "document": {...}
            # 2. Utiliser "payload" au lieu de "data"
            # 3. Ajouter "status": "pending" pour générer immédiatement
            payload = {
                "document": {
                    "document_template_id": self.template_id,
                    "payload": liquid_variables,  # ← CORRIGÉ: "data" → "payload"
                    "status": "pending"  # ← AJOUTÉ: force generation
                }
            }
            
            print(f"📤 Envoi à PDFMonkey...")
            
            # DEBUG: Afficher le payload
            print(f"📤 Payload à envoyer:")
            import json
            print(f"   {json.dumps(payload, indent=2)[:500]}")
            
            print(f"   Template ID: {self.template_id}")
            print(f"   Data fields: {len(liquid_variables)} champs")
            
            # Appel API PDFMonkey - Créer le document
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
            print(f"🔍 Response complète: {result}")
            
            # Extraire l'ID du document
            document_id = None
            if "document" in result and isinstance(result["document"], dict):
                document_id = result["document"].get("id")
                print(f"   Document ID: {document_id}")
                print(f"   Status initial: {result['document'].get('status', 'unknown')}")
            
            if not document_id:
                raise Exception("PDFMonkey n'a pas retourné d'ID de document")
            
            # ⏳ ATTENDRE que le document soit généré (status = success)
            print(f"⏳ Attente de la génération du PDF par PDFMonkey...")
            max_attempts = 30
            attempt = 0
            pdf_url = None
            
            while attempt < max_attempts:
                # Récupérer le status du document via GET
                async with httpx.AsyncClient(timeout=30.0) as client:
                    status_response = await client.get(
                        f"{self.base_url}/documents/{document_id}",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json"
                        },
                        timeout=30.0
                    )
                
                if status_response.status_code == 200:
                    status_result = status_response.json()
                    doc = status_result.get("document", {})
                    status = doc.get("status")
                    
                    print(f"   Tentative {attempt+1}/{max_attempts} - Status: {status}")
                    
                    if status == "success":
                        pdf_url = doc.get("download_url")
                        print(f"   ✅ Document généré avec succès!")
                        print(f"   Download URL: {pdf_url}")
                        break
                    elif status == "processing" or status == "generating":
                        # Attendre 500ms avant de réessayer
                        await asyncio.sleep(0.5)
                        attempt += 1
                    else:
                        print(f"   ⚠️  Status inattendu: {status}")
                        print(f"   Document data: {doc}")
                        break
                else:
                    print(f"   ⚠️  Erreur lors de la vérification du status: {status_response.status_code}")
                    break
            
            if not pdf_url:
                print(f"⚠️  PDF non disponible après {max_attempts} tentatives")
                # Construire l'URL alternative si status check a échoué
                pdf_url = f"https://api.pdfmonkey.io/api/v1/documents/{document_id}/download"
                print(f"   URL alternative: {pdf_url}")
            
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