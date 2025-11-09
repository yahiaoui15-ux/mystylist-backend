"""
Service d'envoi d'emails via Resend pour les rapports MyStylist
"""

import os
import httpx
from datetime import datetime
from typing import Optional, Dict, Any
from urllib.parse import urljoin

class EmailService:
    """
    Service pour envoyer les rapports par email via Resend
    """
    
    def __init__(self):
        # ✅ Stripper les newlines et espaces de la clé API
        self.api_key = os.getenv("RESEND_API_KEY", "").strip()
        self.base_url = "https://api.resend.com"
        self.sender_email = "noreply@my-stylist.io"
        
        if not self.api_key:
            print("⚠️ AVERTISSEMENT: RESEND_API_KEY non configurée")
        else:
            print(f"✅ RESEND_API_KEY configurée (première 20 chars: {self.api_key[:20]}...)")
    
    async def send_report_email(
        self,
        user_email: str,
        user_name: str,
        pdf_url: str,
        report_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Envoie le rapport PDF par email
        
        Args:
            user_email: Email du client
            user_name: Nom du client
            pdf_url: URL du PDF généré
            report_data: Données du rapport (optionnel, pour personnalisation email)
        
        Returns:
            Dict avec statut et email ID
        """
        try:
            print(f"📧 Envoi email à {user_email}...")
            
            # Construire le HTML de l'email
            html_content = self._build_email_html(
                user_name=user_name,
                pdf_url=pdf_url,
                report_data=report_data
            )
            
            # Préparer le payload
            payload = {
                "from": self.sender_email,
                "to": user_email,
                "subject": f"✨ Votre rapport MyStylist.io - Analyse personnalisée {user_name}",
                "html": html_content,
                "reply_to": "contact@my-stylist.io"
            }
            
            # Envoyer via Resend
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/emails",
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=30.0
                )
            
            if response.status_code not in [200, 201]:
                print(f"❌ Erreur Resend: {response.status_code} - {response.text}")
                raise Exception(f"Resend error: {response.status_code}")
            
            result = response.json()
            email_id = result.get("id")
            
            print(f"✅ Email envoyé: ID {email_id}")
            return {
                "status": "success",
                "email_id": email_id,
                "sent_to": user_email,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Erreur envoi email: {e}")
            raise
    
    def _build_email_html(
        self,
        user_name: str,
        pdf_url: str,
        report_data: Optional[dict] = None
    ) -> str:
        """
        Construit le HTML simple de l'email
        
        Args:
            user_name: Nom de l'utilisateur
            pdf_url: URL du PDF
            report_data: Données du rapport
        
        Returns:
            str: HTML de l'email
        """
        # Extraire données si disponibles
        season = ""
        body_type = ""
        if report_data:
            season = report_data.get("colorimetry", {}).get("season", "")
            body_type = report_data.get("morphology", {}).get("silhouette_type", "")
        
        html = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: 'Segoe UI', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 0;
                    background: #f5f5f5;
                }}
                .container {{
                    background: white;
                    max-width: 600px;
                    margin: 0 auto;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%);
                    color: white;
                    padding: 40px 20px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    font-weight: 600;
                }}
                .content {{
                    padding: 30px 20px;
                }}
                .content h2 {{
                    color: #9b59b6;
                    font-size: 20px;
                    margin-top: 0;
                }}
                .summary {{
                    background: #f9f9f9;
                    padding: 15px;
                    border-left: 4px solid #9b59b6;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
                .summary p {{
                    margin: 8px 0;
                    font-size: 14px;
                }}
                .button {{
                    display: inline-block;
                    background: #9b59b6;
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 4px;
                    font-weight: 600;
                    margin: 20px 0;
                }}
                .footer {{
                    background: #f5f5f5;
                    padding: 20px;
                    text-align: center;
                    font-size: 12px;
                    color: #999;
                    border-top: 1px solid #e5e7eb;
                }}
                .footer a {{
                    color: #9b59b6;
                    text-decoration: none;
                    margin: 0 5px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <!-- Header -->
                <div class="header">
                    <h1>✨ MyStylist.io</h1>
                    <p>Votre analyse personnalisée est prête!</p>
                </div>
                
                <!-- Content -->
                <div class="content">
                    <h2>Bonjour {user_name},</h2>
                    
                    <p>
                        Merci d'avoir choisi MyStylist.io! 🎉 Votre rapport d'analyse personnalisée 
                        est maintenant prêt à être consulté.
                    </p>
                    
                    <div class="summary">
                        <p><strong>📋 Votre rapport contient:</strong></p>
                        <p>✅ Analyse colorimétrique personnalisée {f'(Saison {season})' if season else ''}</p>
                        <p>✅ Analyse morphologique {f'(Type {body_type})' if body_type else ''}</p>
                        <p>✅ Recommandations vestimentaires adaptées</p>
                        <p>✅ Produits sélectionnés selon vos préférences</p>
                        <p>✅ Formules mix &amp; match pour votre garde-robe</p>
                    </div>
                    
                    <div style="text-align: center;">
                        <a href="{pdf_url}" class="button">📄 Télécharger mon rapport PDF</a>
                    </div>
                    
                    <p>
                        Vous pouvez également consulter votre rapport directement depuis votre compte 
                        MyStylist.io en vous connectant à votre espace client.
                    </p>
                    
                    <p>
                        Des questions? N'hésitez pas à nous écrire à 
                        <a href="mailto:contact@my-stylist.io" style="color: #9b59b6; text-decoration: none; font-weight: 600;">
                            contact@my-stylist.io
                        </a>
                    </p>
                </div>
                
                <!-- Footer -->
                <div class="footer">
                    <p style="margin: 0 0 10px 0;">
                        © 2025 <strong>MyStylist.io</strong> • La mode passe, le style reste ✨
                    </p>
                    <p style="margin: 10px 0;">
                        <a href="https://my-stylist.io">Visiter le site</a> • 
                        <a href="https://my-stylist.io/contact">Nous contacter</a> • 
                        <a href="https://my-stylist.io/privacy">Politique de confidentialité</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html


# Instance globale à exporter
email_service = EmailService()