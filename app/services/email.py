import os
from datetime import datetime

class EmailService:
    def __init__(self, provider: str = "resend"):
        """
        Service email avec support Resend ou SendGrid
        Chargement lazy des imports pour éviter les erreurs au démarrage
        
        Args:
            provider: "resend" ou "sendgrid"
        """
        self.provider = provider
        self.api_key = os.getenv("RESEND_API_KEY") if provider == "resend" else os.getenv("SENDGRID_API_KEY")
        self.client = None
    
    async def send_report_email(self, user_email: str, user_name: str, pdf_url: str, report_data: dict) -> dict:
        """
        Envoie le rapport PDF au client
        
        Args:
            user_email: Email du client
            user_name: Nom du client
            pdf_url: URL du PDF généré
            report_data: Données du rapport (pour personnalisation)
        
        Returns:
            dict avec status et message_id
        """
        try:
            print(f"📧 Envoi email à {user_email}...")
            
            season = report_data.get("colorimetry", {}).get("season", "Indéterminée")
            silhouette = report_data.get("morphology", {}).get("silhouette_type", "Indéterminée")
            
            # Template HTML de l'email
            html_content = f"""
            <html>
                <head>
                    <meta charset="UTF-8">
                    <style>
                        body {{ font-family: Arial, sans-serif; color: #333; }}
                        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }}
                        .section {{ background: #f9f9f9; padding: 20px; margin: 20px 0; border-radius: 8px; }}
                        .button {{ background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 4px; display: inline-block; margin: 20px 0; }}
                        .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 40px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>✨ Votre Profil Stylistique MyStylist</h1>
                            <p>Découvrez votre unique style personnel</p>
                        </div>
                        
                        <div class="section">
                            <h2>Bonjour {user_name}! 👋</h2>
                            <p>Nous sommes ravis de vous présenter votre rapport stylistique complet et personnalisé.</p>
                        </div>
                        
                        <div class="section">
                            <h3>📊 Vos Analyses</h3>
                            <ul>
                                <li><strong>Saison Colorimétrique:</strong> {season}</li>
                                <li><strong>Type de Silhouette:</strong> {silhouette}</li>
                                <li><strong>Formules Mix&Match:</strong> 10 complètes</li>
                                <li><strong>Guide Produits:</strong> 50+ recommandations</li>
                            </ul>
                        </div>
                        
                        <div style="text-align: center;">
                            <a href="{pdf_url}" class="button">📥 Télécharger Mon Rapport PDF</a>
                        </div>
                        
                        <div class="section">
                            <h3>📚 Votre Rapport Contient:</h3>
                            <ul>
                                <li>✅ Analyse colorimétrie détaillée + palette personnalisée</li>
                                <li>✅ Analyse morphologie + recommandations coupes</li>
                                <li>✅ Profil stylistique complet + archétypes</li>
                                <li>✅ 10 formules mix&match complètes</li>
                                <li>✅ Guide shopping avec 50+ produits</li>
                                <li>✅ Visuels pédagogiques pour chaque catégorie</li>
                            </ul>
                        </div>
                        
                        <div class="section" style="background: #fff3e0; border-left: 4px solid #FBC02D;">
                            <h3>💡 Conseil du jour</h3>
                            <p>Commencez par les pièces essentielles de votre capsule wardrobe, puis ajoutez progressivement les pièces tendance selon vos envies et votre budget.</p>
                        </div>
                        
                        <div class="footer">
                            <p>© 2025 MyStylist.io - Votre Assistant Personnel en Styling</p>
                            <p>Généré le {datetime.now().strftime('%d/%m/%Y')}</p>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            if self.provider == "resend":
                return await self._send_with_resend(user_email, user_name, html_content, pdf_url)
            elif self.provider == "sendgrid":
                return await self._send_with_sendgrid(user_email, user_name, html_content, pdf_url)
            else:
                print("⚠️  Provider email non configuré, email non envoyé")
                return {"status": "skipped", "message": "Email service not configured"}
            
        except Exception as e:
            print(f"❌ Erreur envoi email: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _send_with_resend(self, user_email: str, user_name: str, html_content: str, pdf_url: str) -> dict:
        """Envoie avec Resend"""
        try:
            from resend import Resend
            
            client = Resend(api_key=self.api_key)
            result = client.emails.send({
                "from": "reports@mystylist.io",
                "to": user_email,
                "subject": f"✨ Votre Profil Stylistique MyStylist - {user_name}",
                "html": html_content
            })
            
            print(f"✅ Email envoyé via Resend: {result.get('id', 'N/A')}")
            return {
                "status": "success",
                "message_id": result.get("id"),
                "provider": "resend"
            }
        except Exception as e:
            print(f"❌ Erreur Resend: {e}")
            raise
    
    async def _send_with_sendgrid(self, user_email: str, user_name: str, html_content: str, pdf_url: str) -> dict:
        """Envoie avec SendGrid"""
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail, Email, To, Content
            
            client = SendGridAPIClient(self.api_key)
            mail = Mail(
                from_email=Email("reports@mystylist.io"),
                to_emails=To(user_email),
                subject=f"✨ Votre Profil Stylistique MyStylist - {user_name}",
                html_content=Content("text/html", html_content)
            )
            
            response = client.send(mail)
            
            print(f"✅ Email envoyé via SendGrid: {response.status_code}")
            return {
                "status": "success",
                "status_code": response.status_code,
                "provider": "sendgrid"
            }
        except Exception as e:
            print(f"❌ Erreur SendGrid: {e}")
            raise

# Instance globale (chargement lazy)
email_service = EmailService(provider="resend")