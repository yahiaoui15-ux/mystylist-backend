"""
Service d'envoi d'emails via Resend pour les rapports MyStylist
"""

import os
import httpx
from datetime import datetime
from typing import Optional, Dict, Any


class EmailService:
    """
    Service pour envoyer les rapports par email via Resend
    """

    def __init__(self):
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
        report_type: str = "complet",
        report_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Envoie le rapport PDF par email

        Args:
            user_email: Email du client
            user_name: Nom du client
            pdf_url: URL du PDF généré
            report_type: Type de rapport ("colorimetrie" | "morphologie" | "complet")
            report_data: Données du rapport (optionnel)

        Returns:
            Dict avec statut et email ID
        """
        try:
            print(f"📧 Envoi email à {user_email} (type={report_type})...")

            html_content = self._build_email_html(
                user_name=user_name,
                pdf_url=pdf_url,
                report_type=report_type,
                report_data=report_data
            )

            subject_map = {
                "colorimetrie": f"✨ Votre analyse colorimétrique est prête — MyStylist.io",
                "morphologie":  f"✨ Votre analyse morphologique est prête — MyStylist.io",
                "complet":      f"✨ Votre rapport complet est prêt — MyStylist.io",
            }
            subject = subject_map.get(report_type, f"✨ Votre rapport MyStylist.io est prêt")

            payload = {
                "from": self.sender_email,
                "to": user_email,
                "subject": subject,
                "html": html_content,
                "reply_to": "contact@my-stylist.io"
            }

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

    def _get_report_content(self, report_type: str) -> dict:
        """
        Retourne le titre, sous-titre et liste d'items du rapport selon le type.
        Les items correspondent exactement à la page /rapports du site.
        """
        if report_type == "colorimetrie":
            return {
                "label":    "Rapport · 01",
                "title":    "Colorimétrie",
                "subtitle": "Découvrez les couleurs qui vous mettent en valeur",
                "items": [
                    "Identification de votre saison colorimétrique",
                    "Palettes de couleurs personnalisées",
                    "Notation des couleurs généralistes",
                    "Couleurs à manier avec prudence et à éviter",
                    "Associations de couleurs",
                    "Guide maquillage personnalisé",
                ]
            }
        elif report_type == "morphologie":
            return {
                "label":    "Rapport · 02",
                "title":    "Morphologie",
                "subtitle": "Comprenez votre silhouette et sublimez-la",
                "items": [
                    "Votre type de silhouette",
                    "Ce qui vous met en valeur",
                    "Ce qu'il faut éviter",
                    "Vos meilleures coupes",
                    "Trois formules de tenue personnalisées",
                    "Les matières et motifs à privilégier",
                ]
            }
        else:  # complet
            return {
                "label":    "Rapport · 03 — Signature",
                "title":    "Rapport Complet",
                "subtitle": "L'analyse complète pour une transformation totale",
                "items": [
                    "Tout le rapport Colorimétrie",
                    "Tout le rapport Morphologie",
                    "Votre personnalité vue par l'IA",
                    "Votre style personnalisé",
                    "Vos 10 pièces phares",
                    "Vos 20 articles de garde-robe capsule personnalisée",
                    "Vos 3 looks signatures",
                ]
            }

    def _build_email_html(
        self,
        user_name: str,
        pdf_url: str,
        report_type: str = "complet",
        report_data: Optional[dict] = None
    ) -> str:
        """
        Construit le HTML de l'email — charte graphique MyStylist 2026.
        Vert forêt #1B3022 · Taupe #8D8177 · Cream #F5F5F5
        Styles 100% inline pour compatibilité Gmail / Outlook.
        """

        content = self._get_report_content(report_type)
        first_name = user_name.split()[0] if user_name else "chère cliente"

        # Construire les lignes d'items
        items_rows = ""
        for item in content["items"]:
            items_rows += f"""
                        <tr>
                            <td style="padding: 9px 0; font-family: Arial, Helvetica, sans-serif; font-size: 14px; line-height: 1.5; color: #3a3a3a; border-bottom: 1px solid #eeeae6;">
                                <span style="display: inline-block; width: 16px; color: #8D8177; font-size: 10px; vertical-align: middle;">◆</span>{item}
                            </td>
                        </tr>"""

        html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>MyStylist.io — Votre rapport</title>
</head>
<body style="margin: 0; padding: 0; background-color: #F5F5F5; -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%;">

    <!--[if mso]><table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr><td><![endif]-->
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
           style="background-color: #F5F5F5; padding: 40px 16px;">
        <tr>
            <td align="center">

                <!-- ═══════════ CONTAINER ═══════════ -->
                <table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0"
                       style="max-width: 600px; width: 100%; background-color: #ffffff; border: 1px solid #d8d2cc;">

                    <!-- ══ HEADER ══ -->
                    <tr>
                        <td style="background-color: #1B3022; padding: 44px 48px 40px; text-align: center;">
                            <p style="margin: 0 0 10px 0; font-family: Arial, Helvetica, sans-serif;
                                      font-size: 10px; letter-spacing: 4px; text-transform: uppercase;
                                      color: #8D8177;">
                                L'ATELIER · ÉDITION 2026
                            </p>
                            <h1 style="margin: 0 0 12px 0; font-family: Georgia, 'Times New Roman', serif;
                                       font-size: 30px; font-weight: 400; color: #ffffff; letter-spacing: 2px;">
                                my-stylist.io
                            </h1>
                            <p style="margin: 0; font-family: Arial, Helvetica, sans-serif;
                                      font-size: 12px; letter-spacing: 1px; color: #a8beae;">
                                Votre analyse personnalisée est prête
                            </p>
                        </td>
                    </tr>

                    <!-- ══ BODY ══ -->
                    <tr>
                        <td style="padding: 48px 48px 16px;">

                            <!-- Greeting -->
                            <p style="margin: 0 0 4px 0; font-family: Arial, Helvetica, sans-serif;
                                      font-size: 10px; letter-spacing: 3px; text-transform: uppercase;
                                      color: #8D8177;">
                                Bonjour,
                            </p>
                            <h2 style="margin: 0 0 28px 0; font-family: Georgia, 'Times New Roman', serif;
                                       font-size: 28px; font-weight: 400; color: #1B3022;">
                                {first_name}
                            </h2>

                            <p style="margin: 0 0 36px 0; font-family: Arial, Helvetica, sans-serif;
                                      font-size: 15px; line-height: 1.75; color: #555555;">
                                Merci d'avoir fait confiance à MyStylist.io. Votre rapport d'analyse
                                personnalisée est maintenant prêt&nbsp;à&nbsp;être&nbsp;consulté.
                            </p>

                            <!-- ── Rapport content block ── -->
                            <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
                                   border="0" style="border: 1px solid #d8d2cc; margin-bottom: 36px;">

                                <!-- Block header -->
                                <tr>
                                    <td style="background-color: #f7f4f1; padding: 18px 24px 16px;
                                               border-bottom: 1px solid #d8d2cc;">
                                        <p style="margin: 0 0 4px 0; font-family: Arial, Helvetica, sans-serif;
                                                  font-size: 10px; letter-spacing: 3px; text-transform: uppercase;
                                                  color: #8D8177;">
                                            {content["label"]}
                                        </p>
                                        <p style="margin: 0 0 2px 0; font-family: Georgia, 'Times New Roman', serif;
                                                  font-size: 20px; font-weight: 400; color: #1B3022;">
                                            {content["title"]}
                                        </p>
                                        <p style="margin: 0; font-family: Arial, Helvetica, sans-serif;
                                                  font-size: 13px; font-style: italic; color: #8D8177;">
                                            {content["subtitle"]}
                                        </p>
                                    </td>
                                </tr>

                                <!-- Items list -->
                                <tr>
                                    <td style="padding: 8px 24px 16px;">
                                        <table role="presentation" width="100%" cellpadding="0"
                                               cellspacing="0" border="0">
                                            {items_rows}
                                        </table>
                                    </td>
                                </tr>
                            </table>

                            <!-- ── CTA Button ── -->
                            <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
                                   border="0" style="margin-bottom: 36px;">
                                <tr>
                                    <td align="center">
                                        <a href="{pdf_url}"
                                           style="display: inline-block; background-color: #1B3022;
                                                  color: #ffffff; text-decoration: none;
                                                  padding: 16px 44px;
                                                  font-family: Arial, Helvetica, sans-serif;
                                                  font-size: 11px; font-weight: 700;
                                                  letter-spacing: 2.5px; text-transform: uppercase;
                                                  border-radius: 2px;">
                                            Télécharger mon rapport PDF
                                        </a>
                                    </td>
                                </tr>
                            </table>

                            <!-- ── Secondary note ── -->
                            <p style="margin: 0 0 32px 0; font-family: Arial, Helvetica, sans-serif;
                                      font-size: 13px; line-height: 1.7; color: #8D8177; text-align: center;">
                                Retrouvez également votre rapport dans votre espace client sur
                                <a href="https://my-stylist.io"
                                   style="color: #1B3022; text-decoration: none; font-weight: 600;">
                                    my-stylist.io
                                </a>
                            </p>

                            <!-- ── Divider ── -->
                            <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
                                   border="0" style="margin-bottom: 28px;">
                                <tr>
                                    <td style="border-top: 1px solid #eeeae6; font-size: 0; line-height: 0;">
                                        &nbsp;
                                    </td>
                                </tr>
                            </table>

                            <!-- ── Contact ── -->
                            <p style="margin: 0 0 48px 0; font-family: Arial, Helvetica, sans-serif;
                                      font-size: 13px; line-height: 1.7; color: #8D8177; text-align: center;">
                                Une question&nbsp;? Écrivez-nous&nbsp;à
                                <a href="mailto:contact@my-stylist.io"
                                   style="color: #1B3022; text-decoration: none; font-weight: 600;">
                                    contact@my-stylist.io
                                </a>
                            </p>

                        </td>
                    </tr>

                    <!-- ══ FOOTER ══ -->
                    <tr>
                        <td style="background-color: #1B3022; padding: 28px 48px; text-align: center;">
                            <p style="margin: 0 0 14px 0; font-family: Arial, Helvetica, sans-serif;
                                      font-size: 10px; letter-spacing: 3px; text-transform: uppercase;
                                      color: #a8beae;">
                                La mode passe, le style reste.
                            </p>
                            <p style="margin: 0 0 12px 0; font-family: Arial, Helvetica, sans-serif;
                                      font-size: 11px; color: #6a8a72;">
                                <a href="https://my-stylist.io"
                                   style="color: #8D8177; text-decoration: none;">Visiter le site</a>
                                <span style="color: #3a5a42; margin: 0 8px;">·</span>
                                <a href="mailto:contact@my-stylist.io"
                                   style="color: #8D8177; text-decoration: none;">Nous contacter</a>
                                <span style="color: #3a5a42; margin: 0 8px;">·</span>
                                <a href="https://my-stylist.io/politique-confidentialite"
                                   style="color: #8D8177; text-decoration: none;">Confidentialité</a>
                            </p>
                            <p style="margin: 0; font-family: Arial, Helvetica, sans-serif;
                                      font-size: 10px; letter-spacing: 1px; color: #4a6a52;">
                                © 2026 MyStylist.io
                            </p>
                        </td>
                    </tr>

                </table>
                <!-- ═══════════ /CONTAINER ═══════════ -->

            </td>
        </tr>
    </table>
    <!--[if mso]></td></tr></table><![endif]-->

</body>
</html>"""

        return html


# Instance globale à exporter
email_service = EmailService()