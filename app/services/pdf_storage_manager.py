"""
PDF Storage Manager - Sauvegarder les PDFs de manière permanente
Télécharge du lien S3 temporaire de PDFMonkey → Supabase Storage (permanent)
v2 FIX: Download IMMÉDIATEMENT + meilleur error handling
"""

import httpx
from typing import Optional
from app.utils.supabase_client import supabase
import logging

logger = logging.getLogger(__name__)


class PDFStorageManager:
    """
    Gère le stockage permanent des PDFs
    
    PROBLÈME v1:
    - PDFMonkey envoie lien S3 prédéfini avec expiration 30min
    - Tentative de téléchargement APRÈS 30min → AccessDenied/404
    
    SOLUTION v2:
    1. Télécharger le PDF IMMÉDIATEMENT depuis lien temporaire
    2. Sauvegarder dans Supabase Storage (permanent)
    3. Envoyer lien Supabase au client
    4. Si échec download → utiliser URL temporaire avec avertissement
    """
    
    BUCKET_NAME = "reports"
    TIMEOUT = 30.0  # Timeout download en secondes
    
    @staticmethod
    async def download_pdf_from_url(pdf_url: str) -> Optional[bytes]:
        """
        Télécharge le PDF depuis un URL (temporaire ou pas)
        ⚠️ CRITIQUE: Doit s'exécuter dans les 30 premières minutes!
        
        Args:
            pdf_url: URL complète du PDF (lien PDFMonkey temporaire)
            
        Returns:
            bytes: Contenu du PDF, ou None si erreur
        """
        try:
            print(f"📥 Téléchargement PDF depuis: {pdf_url[:80]}...")
            
            async with httpx.AsyncClient(timeout=PDFStorageManager.TIMEOUT) as client:
                response = await client.get(pdf_url, follow_redirects=True)
                
                if response.status_code != 200:
                    print(f"   ❌ HTTP {response.status_code}")
                    return None
                
                pdf_content = response.content
                print(f"   ✅ PDF téléchargé: {len(pdf_content)} bytes")
                
                # Validation: vérifier que c'est bien un PDF
                if len(pdf_content) < 100:
                    print(f"   ⚠️  PDF trop petit ({len(pdf_content)} bytes) - probablement erreur")
                    return None
                
                return pdf_content
                
        except httpx.TimeoutException:
            print(f"   ❌ Timeout (>{PDFStorageManager.TIMEOUT}s) - URL peut-être expirée")
            return None
        except httpx.HTTPError as e:
            print(f"   ❌ Erreur HTTP: {e}")
            return None
        except Exception as e:
            print(f"   ❌ Erreur inattendue: {type(e).__name__}: {e}")
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
            report_id: ID rapport (payment_id)
            
        Returns:
            str: URL publique du PDF (permanent), ou None si erreur
        """
        try:
            print(f"💾 Sauvegarde dans Supabase Storage...")
            
            # Créer un chemin unique
            file_path = f"{user_id}/report_{report_id[:12]}.pdf"
            
            # Upload
            print(f"   Chemin: {file_path}")
            response = supabase.storage.from_(PDFStorageManager.BUCKET_NAME).upload(
                path=file_path,
                file=pdf_content,
                file_options={"content-type": "application/pdf"}
            )
            
            print(f"   ✅ Upload terminé")
            
            # Récupérer l'URL publique (permanente!)
            public_url = supabase.storage.from_(PDFStorageManager.BUCKET_NAME).get_public_url(file_path)
            
            if not public_url:
                print(f"   ❌ Impossible récupérer URL public")
                return None
            
            print(f"   ✅ URL permanente: {public_url[:80]}...")
            return public_url
            
        except Exception as e:
            print(f"   ❌ Erreur Supabase: {type(e).__name__}: {e}")
            return None
    
    @staticmethod
    async def download_and_save_pdf(
        pdf_url: str,
        user_id: str,
        report_id: str
    ) -> Optional[str]:
        """
        FONCTION PRINCIPALE: Télécharge et sauvegarde le PDF
        
        ⏱️  CRITIQUE: Doit s'exécuter IMMÉDIATEMENT!
        L'URL temporaire de PDFMonkey expire après 30 minutes.
        
        Workflow:
        1. Télécharge depuis lien temporaire (30min)
        2. Sauvegarde dans Supabase Storage (permanent)
        3. Retourne URL permanente
        
        Args:
            pdf_url: URL du PDF depuis PDFMonkey (temporaire!)
            user_id: ID utilisateur
            report_id: ID rapport (payment_id)
            
        Returns:
            str: URL permanente Supabase, ou None si tous les steps échouent
        """
        
        print("\n" + "="*70)
        print("🔄 PDF STORAGE MANAGER v2 - Sauvegarder PDF de manière permanente")
        print("="*70)
        print(f"⏱️  ⚠️  CRITIQUE: URL temporaire expire dans ~30 minutes!")
        
        print(f"\n📋 Rapport: {report_id[:12]}")
        print(f"👤 Utilisateur: {user_id}")
        print(f"🔗 URL temporaire: {pdf_url[:60]}...\n")
        
        # ÉTAPE 1: Télécharger IMMÉDIATEMENT
        print(">>> ÉTAPE 1: Téléchargement du PDF temporaire...")
        pdf_content = await PDFStorageManager.download_pdf_from_url(pdf_url)
        
        if not pdf_content:
            print("❌ Impossible de télécharger le PDF - URL probablement expirée!")
            print("   FALLBACK: Envoi URL temporaire au client")
            print("   ⚠️  ATTENTION: Client aura 30min pour télécharger avant 404!\n")
            return None  # Retourner None force main.py à utiliser pdf_url_temporary
        
        # ÉTAPE 2: Sauvegarder dans Supabase
        print("\n>>> ÉTAPE 2: Sauvegarde dans Supabase Storage...")
        permanent_url = await PDFStorageManager.save_pdf_to_supabase(
            pdf_content,
            user_id,
            report_id
        )
        
        if not permanent_url:
            print("❌ Impossible de sauvegarder - Supabase Storage peut être hors-ligne")
            print("   FALLBACK: Envoi URL temporaire au client\n")
            return None
        
        # SUCCÈS!
        print("\n" + "="*70)
        print("✅ PDF sauvegardé de manière PERMANENTE!")
        print("="*70)
        print(f"   📥 Téléchargé depuis: {pdf_url[:60]}...")
        print(f"   💾 Sauvegardé dans: Supabase Storage")
        print(f"   🔗 URL permanente: {permanent_url}")
        print("="*70 + "\n")
        
        return permanent_url
    
    @staticmethod
    def get_public_url(user_id: str, report_id: str) -> str:
        """Récupère l'URL publique d'un PDF stocké"""
        file_path = f"{user_id}/report_{report_id[:12]}.pdf"
        public_url = supabase.storage.from_(PDFStorageManager.BUCKET_NAME).get_public_url(file_path)
        return public_url


# Instance globale
pdf_storage_manager = PDFStorageManager()