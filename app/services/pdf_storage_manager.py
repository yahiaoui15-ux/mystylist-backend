"""
PDF Storage Manager FIXED v3 - REST API Supabase
✅ Utilise REST API HTTP directe (pas la lib Python cassée)
✅ Upload permanent vers Supabase Storage
✅ Gère les erreurs correctement
"""

import httpx
import logging
from typing import Optional
from app.config_prod import settings

logger = logging.getLogger(__name__)


class PDFStorageManager:
    """
    Sauvegarde PDF de maniére permanente via REST API Supabase
    
    ❌ ANCIEN: Tentait d'utiliser client.storage (n'existe pas en Python)
    ✅ NOUVEAU: Utilise REST API HTTP directement
    
    Workflow:
    1. Télécharger PDF depuis lien temporaire PDFMonkey (30min)
    2. Upload vers Supabase Storage via REST API HTTP (permanent)
    3. Retourner URL permanente Supabase
    """
    
    BUCKET_NAME = "reports"
    TIMEOUT = 30.0
    
    @staticmethod
    async def download_pdf_from_url(pdf_url: str) -> Optional[bytes]:
        """
        Télécharge le PDF depuis URL temporaire
        ⏰ CRITIQUE: Exécuter immédiatement! (URL expire 30min)
        """
        try:
            print(f"🔥 Téléchargement PDF depuis: {pdf_url[:80]}...")
            
            async with httpx.AsyncClient(timeout=PDFStorageManager.TIMEOUT) as client:
                response = await client.get(pdf_url, follow_redirects=True)
                
                if response.status_code != 200:
                    print(f"   ❌ HTTP {response.status_code}")
                    return None
                
                pdf_content = response.content
                
                # Validation
                if len(pdf_content) < 100:
                    print(f"   ⚠️  PDF trop petit ({len(pdf_content)} bytes) - erreur probable")
                    return None
                
                print(f"   ✅ PDF téléchargé: {len(pdf_content)} bytes")
                return pdf_content
                
        except httpx.TimeoutException:
            print(f"   ❌ Timeout (>{PDFStorageManager.TIMEOUT}s) - URL probablement expirée")
            return None
        except Exception as e:
            print(f"   ❌ Erreur download: {type(e).__name__}: {e}")
            return None
    
    @staticmethod
    async def save_pdf_to_supabase(
        pdf_content: bytes,
        user_id: str,
        report_id: str
    ) -> Optional[str]:
        """
        Upload PDF vers Supabase Storage via REST API HTTP
        
        Utilise: POST {SUPABASE_URL}/storage/v1/object/{bucket}/{file_path}
        Documentation: https://supabase.com/docs/reference/api/post-object
        
        Returns:
            str: URL permanente du PDF (genre: https://...supabase.co/storage/v1/object/public/reports/...)
        """
        try:
            print(f"💾 Sauvegarde dans Supabase Storage...")
            
            # Créer chemin unique
            file_path = f"{user_id}/report_{report_id[:12]}.pdf"
            
            # URL REST API Supabase
            upload_url = f"{settings.SUPABASE_URL}/storage/v1/object/{PDFStorageManager.BUCKET_NAME}/{file_path}"
            
            print(f"   📍 Bucket: {PDFStorageManager.BUCKET_NAME}")
            print(f"   📝 Chemin: {file_path}")
            print(f"   🔗 URL: {upload_url[:80]}...")
            
            # ✅ FIX: Utiliser REST API HTTP au lieu de client.storage
            async with httpx.AsyncClient(timeout=PDFStorageManager.TIMEOUT) as client:
                response = await client.post(
                    upload_url,
                    content=pdf_content,
                    headers={
                        "Authorization": f"Bearer {settings.SUPABASE_KEY}",
                        "Content-Type": "application/pdf",
                        "x-upsert": "true"  # Overwrite si exists
                    }
                )
            
            if response.status_code not in [200, 201]:
                error_msg = response.text[:200] if response.text else f"HTTP {response.status_code}"
                print(f"   ❌ Erreur upload: {error_msg}")
                return None
            
            print(f"   ✅ Upload réussi!")
            
            # Construire URL permanente Supabase
            permanent_url = f"{settings.SUPABASE_URL}/storage/v1/object/public/{PDFStorageManager.BUCKET_NAME}/{file_path}"
            
            print(f"   🔗 URL permanente: {permanent_url[:80]}...")
            
            return permanent_url
            
        except httpx.TimeoutException:
            print(f"   ❌ Timeout lors upload")
            return None
        except Exception as e:
            print(f"   ❌ Erreur Supabase: {type(e).__name__}: {e}")
            logger.error(f"PDF Storage error: {e}")
            return None
    
    @staticmethod
    async def download_and_save_pdf(
        pdf_url: str,
        user_id: str,
        report_id: str
    ) -> Optional[str]:
        """
        FONCTION PRINCIPALE: Télécharge + sauvegarde PDF
        
        ⏰ CRITIQUE: Doit s'exécuter IMMÉDIATEMENT!
        L'URL temporaire de PDFMonkey expire après 30 minutes.
        
        Workflow:
        1. Télécharge depuis lien temporaire (30min window)
        2. Sauvegarde dans Supabase Storage (permanent)
        3. Retourne URL permanente
        
        Args:
            pdf_url: URL du PDF depuis PDFMonkey (temporaire!)
            user_id: ID utilisateur
            report_id: ID rapport (payment_id)
            
        Returns:
            str: URL permanente Supabase, ou None si erreur
        """
        
        print("\n" + "="*70)
        print("📄 PDF STORAGE MANAGER FIXED - Supabase REST API")
        print("="*70)
        print(f"⏰ ⚠️  URL temporaire expire dans ~30 minutes!")
        print(f"📋 Rapport: {report_id[:12]}")
        print(f"👤 Utilisateur: {user_id}\n")
        
        # ÉTAPE 1: Télécharger IMMÉDIATEMENT
        print(">>> ÉTAPE 1: Téléchargement du PDF (URL temporaire)...")
        pdf_content = await PDFStorageManager.download_pdf_from_url(pdf_url)
        
        if not pdf_content:
            print("❌ Impossible de télécharger - URL probablement expirée!")
            print("   FALLBACK: Client recevra URL temporaire (30min)\n")
            return None
        
        # ÉTAPE 2: Upload permanent
        print("\n>>> ÉTAPE 2: Upload permanent vers Supabase Storage...")
        permanent_url = await PDFStorageManager.save_pdf_to_supabase(
            pdf_content,
            user_id,
            report_id
        )
        
        if not permanent_url:
            print("❌ Impossible de sauvegarder")
            print("   FALLBACK: Client recevra URL temporaire (30min)\n")
            return None
        
        # SUCCÈS!
        print("\n" + "="*70)
        print("✅ PDF SAUVEGARDÉ DE MANIÈRE PERMANENTE!")
        print("="*70)
        print(f"   📥 Téléchargé depuis: {pdf_url[:60]}...")
        print(f"   💾 SauvegardÃ© dans: Supabase Storage")
        print(f"   🔗 URL permanente: {permanent_url}")
        print("   ⏰ Validité: 2+ mois (pas d'expiration)")
        print("="*70 + "\n")
        
        return permanent_url
    
    @staticmethod
    def get_public_url(user_id: str, report_id: str) -> str:
        """Récupère l'URL publique d'un PDF déjà stocké"""
        file_path = f"{user_id}/report_{report_id[:12]}.pdf"
        public_url = f"{settings.SUPABASE_URL}/storage/v1/object/public/{PDFStorageManager.BUCKET_NAME}/{file_path}"
        return public_url


# Instance globale
pdf_storage_manager = PDFStorageManager()