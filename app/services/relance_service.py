"""
Service de relance email pour les comptes ayant terminé l'onboarding
sans avoir acheté de rapport.

Réutilise le même provider (Resend) et la même charte graphique que
email_service.py (rapport après paiement), mais avec un template et
un expéditeur dédiés à la relance.
"""

import os
import httpx
import stripe
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from app.config_prod import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


class RelanceService:
    """
    Service dédié aux 3 emails de relance (J+1, J+3, J+7).
    Séparé de EmailService (rapport après paiement) pour ne jamais
    risquer de casser l'envoi du rapport payant en modifiant ce fichier.
    """

    def __init__(self):
        self.api_key = os.getenv("RESEND_API_KEY", "").strip()
        self.base_url = "https://api.resend.com"
        self.sender_email = "contact@my-stylist.io"

        if not self.api_key:
            print("⚠️ AVERTISSEMENT: RESEND_API_KEY non configurée (relance)")

    # ------------------------------------------------------------------
    # Génération du code promo Stripe (email 3 uniquement)
    # ------------------------------------------------------------------

    def generate_promo_code(self, coupon_id: str) -> str:
        """
        Génère un promotion_code à usage unique, valable 48h, rattaché
        à un coupon déjà existant dans Stripe (créé manuellement une
        seule fois, ex: -20% permanent).

        Args:
            coupon_id: ID du coupon Stripe existant (ex: "PROMO20-STYLE")

        Returns:
            Le code promo généré (string), à insérer dans l'email.
        """
        expires_at = int((datetime.utcnow() + timedelta(hours=48)).timestamp())

        promotion_code = stripe.PromotionCode.create(
            coupon=coupon_id,
            max_redemptions=1,
            expires_at=expires_at,
        )

        print(f"✅ Code promo généré: {promotion_code.code} (expire {expires_at})")
        return promotion_code.code

    # ------------------------------------------------------------------
    # Envoi de l'email de relance
    # ------------------------------------------------------------------

    async def send_relance_email(
        self,
        user_id: str,
        user_email: str,
        email_number: int,
        first_name: Optional[str] = None,
        eye_color: Optional[str] = None,
        hair_color: Optional[str] = None,
        primary_style: Optional[str] = None,
        personality_trait: Optional[str] = None,
        reports_tab_url: str = "https://my-stylist.io/auth?redirect=/app%3Ftab%3Drapports",
        apercu_rapport_url: str = "https://my-stylist.io/apercu-rapport",
        promo_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Envoie l'email de relance n°1, 2 ou 3.

        Args:
            user_email: destinataire
            email_number: 1, 2 ou 3
            first_name: prénom si disponible (repli automatique sinon)
            eye_color, hair_color, primary_style, personality_trait:
                données de personnalisation (voir mapping onboarding_data)
            reports_tab_url: lien de connexion + redirection vers l'onglet Rapports
            apercu_rapport_url: lien vers /apercu-rapport (email 2 uniquement)
            promo_code: code Stripe déjà généré (email 3 uniquement)

        Returns:
            Dict avec statut et email_id
        """
        try:
            print(f"📧 Relance email {email_number} → {user_email}...")

            html_content = self._build_relance_html(
                user_id=user_id,
                email_number=email_number,
                first_name=first_name,
                eye_color=eye_color,
                hair_color=hair_color,
                primary_style=primary_style,
                personality_trait=personality_trait,
                reports_tab_url=reports_tab_url,
                apercu_rapport_url=apercu_rapport_url,
                promo_code=promo_code,
            )

            subject_map = {
                1: "Ton profil MyStylist est prêt",
                2: "Ton rapport ne s'arrête pas à la lecture",
                3: "-20% sur ton rapport, valable 48h",
            }
            subject = subject_map.get(email_number, "Ton profil MyStylist")
            if first_name:
                subject = f"{first_name}, {subject[0].lower()}{subject[1:]}"

            unsubscribe_url = f"https://mystylist-backend-production.up.railway.app/api/relance/unsubscribe?u={user_id}"

            payload = {
                "from": self.sender_email,
                "to": user_email,
                "subject": subject,
                "html": html_content,
                "reply_to": "contact@my-stylist.io",
                "headers": {
                    "List-Unsubscribe": f"<{unsubscribe_url}>",
                    "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
                },
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/emails",
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    timeout=30.0,
                )

            if response.status_code not in (200, 201):
                print(f"❌ Erreur Resend (relance {email_number}): {response.status_code} - {response.text}")
                raise Exception(f"Resend error: {response.status_code}")

            result = response.json()
            email_id = result.get("id")

            print(f"✅ Relance {email_number} envoyée: ID {email_id}")
            return {
                "status": "success",
                "email_id": email_id,
                "sent_to": user_email,
                "email_number": email_number,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            print(f"❌ Erreur envoi relance {email_number}: {e}")
            raise

    # ------------------------------------------------------------------
    # Construction du HTML — même charte graphique que email_service.py
    # ------------------------------------------------------------------

    def _build_relance_html(
        self,
        user_id: str,
        email_number: int,
        first_name: Optional[str],
        eye_color: Optional[str],
        hair_color: Optional[str],
        primary_style: Optional[str],
        personality_trait: Optional[str],
        reports_tab_url: str,
        apercu_rapport_url: str,
        promo_code: Optional[str],
    ) -> str:
        """
        Vert forêt #1B3022 · Taupe #8D8177 · Cream #F5F5F5
        Styles 100% inline, même structure que email_service.py.
        """

        greeting = f"Bonjour {first_name}," if first_name else "Bonjour,"

        # ---- Contenu spécifique à chaque email ----
        if email_number == 1:
            body_html = self._email_1_body(eye_color, hair_color, primary_style, personality_trait)
            cta_label = "Voir mes rapports"
            cta_url = reports_tab_url
        elif email_number == 2:
            body_html = self._email_2_body(apercu_rapport_url)
            cta_label = "Découvrir mes rapports personnalisés"
            cta_url = reports_tab_url
        else:  # email 3
            body_html = self._email_3_body(promo_code)
            cta_label = "Utiliser mon code maintenant"
            cta_url = reports_tab_url



        html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MyStylist.io</title>
</head>
<body style="margin: 0; padding: 0; background-color: #F5F5F5;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
           style="background-color: #F5F5F5; padding: 40px 16px;">
        <tr>
            <td align="center">
                <table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0"
                       style="max-width: 600px; width: 100%; background-color: #ffffff; border: 1px solid #d8d2cc;">

                    <tr>
                        <td style="background-color: #1B3022; padding: 36px 48px 32px; text-align: center;">
                            <p style="margin: 0 0 16px 0; font-family: Arial, Helvetica, sans-serif;
                                    font-size: 10px; letter-spacing: 4px; text-transform: uppercase;
                                    color: #8D8177;">L'ATELIER · ÉDITION 2026</p>
                            <a href="https://my-stylist.io" style="text-decoration: none; display: inline-block;
                                    background-color: #F5F5F5; padding: 14px 28px; border-radius: 4px;">
                                <img src="https://eqtovvjueqsralaprsvm.supabase.co/storage/v1/object/public/documents/Professional%20logo%20with%20elegant%20design%20elements%20(1).png"
                                    alt="my-stylist.io" width="160" style="display: block; max-width: 160px; height: auto; border: 0;" />
                            </a>
                        </td>
                    </tr>

                    <tr>
                        <td style="padding: 48px 48px 16px;">
                            <p style="margin: 0 0 4px 0; font-family: Arial, Helvetica, sans-serif;
                                      font-size: 10px; letter-spacing: 3px; text-transform: uppercase;
                                      color: #8D8177;">{greeting}</p>

                            {body_html}

                            <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
                                   border="0" style="margin: 32px 0;">
                                <tr>
                                    <td align="center">
                                        <a href="{cta_url}"
                                           style="display: inline-block; background-color: #1B3022;
                                                  color: #ffffff; text-decoration: none; padding: 16px 44px;
                                                  font-family: Arial, Helvetica, sans-serif; font-size: 11px;
                                                  font-weight: 700; letter-spacing: 2.5px; text-transform: uppercase;
                                                  border-radius: 2px;">{cta_label}</a>
                                    </td>
                                </tr>
                            </table>

                            {self._unsubscribe_line(user_id)}
                        </td>
                    </tr>

                    <tr>
                        <td style="background-color: #1B3022; padding: 28px 48px; text-align: center;">
                            <p style="margin: 0; font-family: Arial, Helvetica, sans-serif;
                                      font-size: 10px; letter-spacing: 1px; color: #4a6a52;">
                                © 2026 MyStylist.io</p>
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""
        return html
    
    def _unsubscribe_line(self, user_id: str) -> str:
        unsubscribe_url = f"https://mystylist-backend-production.up.railway.app/api/relance/unsubscribe?u={user_id}"
        return f"""
            <p style="margin: 24px 0 0 0; font-family: Arial, Helvetica, sans-serif;
                      font-size: 11px; line-height: 1.6; color: #a8a29a; text-align: center;">
                Tu ne souhaites plus recevoir ces emails ?
                <a href="{unsubscribe_url}" style="color: #8D8177;">Te désabonner ici.</a>
            </p>
        """
    
    def _email_1_body(self, eye_color, hair_color, primary_style, personality_trait) -> str:
        eye = eye_color or "vos yeux"
        hair = hair_color or "vos cheveux"
        style = primary_style or "votre style"
        trait = personality_trait or "votre personnalité"

        return f"""
            <p style="margin: 0 0 28px 0; font-family: Arial, Helvetica, sans-serif;
                      font-size: 15px; line-height: 1.75; color: #555555;">
                Ton profil MyStylist est complet et toutes tes réponses sont bien
                enregistrées.<br><br>
                D'après ce que tu nous as confié — une personnalité plutôt {trait},
                un style {style}, ta colorimétrie de base (yeux {eye}, cheveux {hair})
                — on a déjà tout ce qu'il faut pour personnaliser ton analyse.<br><br>
                Il ne te reste plus qu'à choisir le rapport que tu souhaites recevoir.<br><br>
                Et ce n'est que le début : une fois ton rapport en main, tu débloques
                aussi <strong>Recherche</strong> (des suggestions shopping filtrées selon
                TON profil) et <strong>Garde-robe</strong> (des tenues composées à partir
                de tes propres vêtements).
            </p>
        """

    def _email_2_body(self, apercu_rapport_url) -> str:
        recherche_img = "https://my-stylist.io/__l5e/assets-v1/b1ab15c7-802b-421e-abf4-ab6fd4fc5f6f/shot-recherche-articles.webp"
        garde_robe_img = "https://my-stylist.io/__l5e/assets-v1/7596a74b-a8c8-47ec-9a50-00b3c83d4b62/shot-suggestions.webp"

        return f"""
            <p style="margin: 0 0 24px 0; font-family: Arial, Helvetica, sans-serif;
                    font-size: 15px; line-height: 1.75; color: #555555;">
                On a tendance à présenter le rapport MyStylist comme un document à lire.
                C'est réducteur : une fois généré, il devient le moteur de deux outils
                que tu retrouves ensuite dans ton espace, à chaque fois que tu as besoin
                de shopper.
            </p>

            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
                style="margin-bottom: 24px; border: 1px solid #d8d2cc;">
                <tr>
                    <td style="padding: 0;">
                        <img src="{recherche_img}" alt="Recherche MyStylist" width="504"
                            style="display: block; width: 100%; max-width: 504px; height: auto;" />
                    </td>
                </tr>
                <tr>
                    <td style="padding: 18px 20px;">
                        <p style="margin: 0 0 6px 0; font-family: Georgia, serif; font-size: 17px;
                                color: #1B3022;">Recherche</p>
                        <p style="margin: 0; font-family: Arial, Helvetica, sans-serif; font-size: 14px;
                                line-height: 1.6; color: #555;">
                            Fini de scroller au hasard parmi des centaines d'articles. Tu tapes
                            ce que tu cherches, on filtre automatiquement selon ta colorimétrie,
                            ta morphologie et ton style — tu ne vois que ce qui te va vraiment.
                        </p>
                    </td>
                </tr>
            </table>

            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
                style="margin-bottom: 28px; border: 1px solid #d8d2cc;">
                <tr>
                    <td style="padding: 0;">
                        <img src="{garde_robe_img}" alt="Garde-robe MyStylist" width="504"
                            style="display: block; width: 100%; max-width: 504px; height: auto;" />
                    </td>
                </tr>
                <tr>
                    <td style="padding: 18px 20px;">
                        <p style="margin: 0 0 6px 0; font-family: Georgia, serif; font-size: 17px;
                                color: #1B3022;">Garde-robe</p>
                        <p style="margin: 0; font-family: Arial, Helvetica, sans-serif; font-size: 14px;
                                line-height: 1.6; color: #555;">
                            Prends en photo ce que tu as déjà dans ton dressing. MyStylist te
                            propose des tenues complètes à partir de tes propres vêtements,
                            selon ton profil — plus besoin de racheter pour te sentir bien habillée.
                        </p>
                    </td>
                </tr>
            </table>

            <p style="margin: 0 0 28px 0; font-family: Arial, Helvetica, sans-serif;
                    font-size: 15px; line-height: 1.75; color: #555555;">
                <a href="{apercu_rapport_url}" style="color: #1B3022; font-weight: 600;">
                Voir un vrai extrait de rapport →</a>
            </p>
        """


    def _email_3_body(self, promo_code) -> str:
        code_block = f"""
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
                style="margin: 24px 0; border: 1px solid #8D8177; background-color: #f7f4f1;">
                <tr>
                    <td style="padding: 20px; text-align: center;">
                        <p style="margin: 0 0 6px 0; font-family: Arial, Helvetica, sans-serif;
                                font-size: 10px; letter-spacing: 2px; text-transform: uppercase;
                                color: #8D8177;">Ton code, valable 48h</p>
                        <p style="margin: 0; font-family: Georgia, serif; font-size: 22px;
                                color: #1B3022; font-weight: 700; letter-spacing: 1px;">
                            {promo_code or "CODE_INDISPONIBLE"}</p>
                    </td>
                </tr>
            </table>
        """
        return f"""
            <p style="margin: 0 0 20px 0; font-family: Arial, Helvetica, sans-serif;
                    font-size: 15px; line-height: 1.75; color: #555555;">
                Se faire accompagner par un styliste personnel coûte généralement
                plusieurs centaines d'euros pour une seule consultation.<br><br>
                Ton analyse MyStylist t'offre l'équivalent — ta colorimétrie, ta
                morphologie, ton style, construits à partir de tes propres réponses —
                pour une fraction de ce prix. Et aujourd'hui, on te propose de l'obtenir
                encore moins cher.
            </p>
            <p style="margin: 0 0 4px 0; font-family: Arial, Helvetica, sans-serif;
                    font-size: 15px; line-height: 1.75; color: #555555;">
                Voici un code à usage unique, valable 48h :
            </p>
            {code_block}
            <p style="margin: 0 0 28px 0; font-family: Arial, Helvetica, sans-serif;
                    font-size: 14px; line-height: 1.7; color: #8D8177;">
                Passé ce délai, ce code ne sera plus utilisable et on ne te
                recontactera plus à ce sujet.<br><br>
                Une dernière chose, si tu as deux secondes : qu'est-ce qui te retient
                encore ? Tu peux répondre directement à cet email — on lit chaque
                réponse.
            </p>
        """

# Instance globale à exporter
relance_service = RelanceService()