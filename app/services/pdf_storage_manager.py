"""
PDF Storage Manager - Sauvegarder les PDFs de manière permanente
Télécharge du lien S3 temporaire de PDFMonkey → Supabase Storage (permanent)
"""

import httpx
from typing import Optional, Tuple
from app.utils.supabase_client import supabase
import logging

logger = logging.getLogger(__name__)


class PDFStorageManager:
    """
    Gère le stockage permanent des PDFs
    
    PROBLÈME:
    - PDFMonkey envoie lien S3 présigné avec expiration 1h
    - Après 1h: AccessDenied
    - Clients ne peuvent plus télécharger après 1h
    
    SOLUTION:
    1. Télécharger le PDF du lien S3 temporaire
    2. Sauvegarder dans Supabase Storage (permanente)
    3. Envoyer lien Supabase au client
    """
    
    BUCKET_NAME = "reports"
    
    @staticmethod
    async def download_pdf_from_url(pdf_url: str) -> Optional[bytes]:
        """
        Télécharge le PDF depuis un URL (S3, HTTPS, etc.)
        
        Args:
            pdf_url: URL complète du PDF (ex: lien S3 de PDFMonkey)
            
        Returns:
            bytes: Contenu du PDF, ou None si erreur
        """
        try:
            print(f"📥 Téléchargement PDF depuis: {pdf_url[:80]}...")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(pdf_url)
                response.raise_for_status()
                
                pdf_content = response.content
                print(f"   ✅ PDF téléchargé: {len(pdf_content)} bytes")
                return pdf_content
                
        except httpx.HTTPError as e:
            print(f"   ❌ Erreur téléchargement HTTP: {e}")
            return None
        except Exception as e:
            print(f"   ❌ Erreur inattendue: {e}")
            return None
    
    @staticmethod
    async def save_pdf_to_supabase(
        pdf_content: bytes,
        user_id: str,
        report_id: str
    ) -> Optional[str]:
        """
        Sauvegarde le PDF dans Supabase Storage (permanent)
        
        Args:
            pdf_content: Contenu binaire du PDF
            user_id: ID utilisateur
            report_id: ID rapport (de PDFMonkey)
            
        Returns:
            str: URL publique du PDF (permanent), ou None si erreur
            
        Exemple de fichier créé:
        /reports/user_123/report_54446a1f-5cb8.pdf
        """
        try:
            print(f"💾 Sauvegarde dans Supabase Storage...")
            
            # Créer un chemin unique pour le PDF
            file_path = f"{user_id}/report_{report_id[:12]}.pdf"
            
            # Uploader dans le bucket "reports"
            response = supabase.storage.from_(PDFStorageManager.BUCKET_NAME).upload(
                path=file_path,
                file=pdf_content,
                file_options={"content-type": "application/pdf"}
            )
            
            print(f"   ✅ PDF sauvegardé: {file_path}")
            
            # Récupérer l'URL publique du PDF (permanent!)
            public_url = supabase.storage.from_(PDFStorageManager.BUCKET_NAME).get_public_url(file_path)
            
            print(f"   ✅ URL permanent: {public_url}")
            
            return public_url
            
        except Exception as e:
            print(f"   ❌ Erreur sauvegarde Supabase: {e}")
            return None
    
    @staticmethod
    async def download_and_save_pdf(
        pdf_url: str,
        user_id: str,
        report_id: str
    ) -> Optional[str]:
        """
        FONCTION PRINCIPALE: Télécharge et sauvegarde le PDF
        
        Workflow:
        1. Télécharge depuis lien S3 temporaire de PDFMonkey
        2. Sauvegarde dans Supabase Storage (permanent)
        3. Retourne l'URL permanente
        
        Args:
            pdf_url: URL du PDF depuis PDFMonkey (lien S3 avec expiration 1h)
            user_id: ID utilisateur
            report_id: ID rapport
            
        Returns:
            str: URL permanente du PDF dans Supabase Storage
            
        Exemple:
        >>> url_perm = await PDFStorageManager.download_and_save_pdf(
        ...     pdf_url="https://pdfmonkey-store.s3.eu-west-3.amazonaws.com/...",
        ...     user_id="user_123",
        ...     report_id="54446a1f-5cb8-4f84-921c-8e2c286646e1"
        ... )
        >>> # url_perm = "https://supabase-project.supabase.co/storage/v1/object/public/reports/user_123/report_54446a1f.pdf"
        """
        
        print("\n" + "="*70)
        print("🔄 PDF STORAGE MANAGER - Sauvegarder PDF de manière permanente")
        print("="*70)
        
        # ÉTAPE 1: Télécharger le PDF depuis lien temporaire
        print(f"\n📝 Rapport: {report_id[:12]}")
        print(f"👤 Utilisateur: {user_id}")
        
        pdf_content = await PDFStorageManager.download_pdf_from_url(pdf_url)
        
        if not pdf_content:
            print("❌ Impossible de télécharger le PDF")
            return None
        
        # ÉTAPE 2: Sauvegarder dans Supabase Storage
        permanent_url = await PDFStorageManager.save_pdf_to_supabase(
            pdf_content,
            user_id,
            report_id
        )
        
        if not permanent_url:
            print("❌ Impossible de sauvegarder le PDF")
            return None
        
        print("\n✅ PDF sauvegardé de manière permanente!")
        print(f"   URL temporaire (PDFMonkey): {pdf_url[:60]}...")
        print(f"   URL permanente (Supabase): {permanent_url}")
        
        return permanent_url
    
    @staticmethod
    def get_public_url(user_id: str, report_id: str) -> str:
        """
        Récupère l'URL publique d'un PDF stocké
        
        Args:
            user_id: ID utilisateur
            report_id: ID rapport (premiers 12 caractères)
            
        Returns:
            str: URL publique permanente
        """
        file_path = f"{user_id}/report_{report_id[:12]}.pdf"
        public_url = supabase.storage.from_(PDFStorageManager.BUCKET_NAME).get_public_url(file_path)
        return public_url


# Instance globale
pdf_storage_manager = PDFStorageManager()