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
        self.sender_email = "MyStylist.io <contact@my-stylist.io>"

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

            subject_map = {
                1: "ton profil MyStylist est prêt",
                2: "voici ce que ton rapport va changer concrètement",
                3: "-20% sur ton rapport pendant 48h",
            }
            subject = subject_map.get(email_number, "Ton profil MyStylist")

            preheader_map = {
                1: "Il ne reste qu'à choisir l'analyse que tu souhaites recevoir.",
                2: "Ton rapport n'est que le début de ton expérience MyStylist.",
                3: "Une dernière offre avant qu'on n'en reparle plus.",
            }
            preheader = preheader_map.get(email_number, "")

            html_content = self._build_relance_html(
                user_id=user_id,
                email_number=email_number,
                preheader=preheader,
                first_name=first_name,
                eye_color=eye_color,
                hair_color=hair_color,
                primary_style=primary_style,
                personality_trait=personality_trait,
                reports_tab_url=reports_tab_url,
                apercu_rapport_url=apercu_rapport_url,
                promo_code=promo_code,
            )

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
        preheader: str,
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
            cta_label = "Choisir mon analyse"
            cta_url = reports_tab_url
            post_cta_html = """
                <p style="margin: 0 0 8px 0; font-family: Arial, Helvetica, sans-serif;
                          font-size: 13px; line-height: 1.7; color: #8D8177; text-align: center;">
                    Et avec le Rapport Complet, ton profil alimente aussi Recherche et
                    Garde-robe en illimité : deux outils pour trouver des vêtements
                    adaptés à toi et composer des tenues avec ce que tu possèdes déjà.
                    Les autres rapports donnent droit à un premier essai gratuit.
                </p>
            """
        elif email_number == 2:
            body_html = self._email_2_body(apercu_rapport_url)
            cta_label = "Voir ce que mon analyse peut révéler"
            cta_url = reports_tab_url
            post_cta_html = ""
        else:  # email 3
            body_html = self._email_3_body(promo_code)
            cta_label = "Profiter de -20% sur mon rapport"
            cta_url = reports_tab_url
            post_cta_html = ""



        html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MyStylist.io</title>
</head>
<body style="margin: 0; padding: 0; background-color: #F5F5F5;">
    <div style="display:none; max-height:0; overflow:hidden; mso-hide:all; font-size:1px; line-height:1px; color:#F5F5F5;">{preheader}</div>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
           style="background-color: #F5F5F5; padding: 40px 16px;">
        <tr>
            <td align="center">
                <table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0"
                       style="max-width: 600px; width: 100%; background-color: #ffffff; border: 1px solid #d8d2cc;">

                    <tr>
                        <td style="background-color: #1B3022; padding: 18px 48px 16px; text-align: center;">
                            <a href="https://my-stylist.io" style="text-decoration: none; display: inline-block;
                                    background-color: #F5F5F5; padding: 8px 16px; border-radius: 4px;">
                                <img src="https://eqtovvjueqsralaprsvm.supabase.co/storage/v1/object/public/documents/Professional%20logo%20with%20elegant%20design%20elements%20(1).png"
                                    alt="my-stylist.io" width="90" style="display: block; max-width: 90px; height: auto; border: 0;" />
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
                                   border="0" style="margin: 28px 0;">
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

                            {post_cta_html}

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
        return """
            <p style="margin: 0 0 20px 0; font-family: Arial, Helvetica, sans-serif;
                      font-size: 15px; line-height: 1.75; color: #555555;">
                Ton profil MyStylist est complet et toutes tes réponses sont bien
                enregistrées.<br><br>
                Tu as pris le temps de nous parler de tes goûts, de ton style et
                de ce que tu souhaites mettre en valeur. On a maintenant tout ce
                qu'il faut pour personnaliser ton analyse.
            </p>
        """

    def _email_2_body(self, apercu_rapport_url) -> str:
        palette_img = "https://my-stylist.io/__l5e/assets-v1/c82b019f-ade7-4c59-b0b3-496bf1609ee7/er-page-palette.webp"
        coupes_img = "https://my-stylist.io/__l5e/assets-v1/3d6f22ae-795f-4af7-bf01-24028ea425f0/er-page-coupes.webp"
        looks_img = "https://my-stylist.io/__l5e/assets-v1/cb9aae89-a7d3-475d-85b3-4f230f75c20c/er-page-looks.webp"
        recherche_img = "https://my-stylist.io/__l5e/assets-v1/b1ab15c7-802b-421e-abf4-ab6fd4fc5f6f/shot-recherche-articles.webp"
        garde_robe_img = "https://my-stylist.io/__l5e/assets-v1/7596a74b-a8c8-47ec-9a50-00b3c83d4b62/shot-suggestions.webp"

        def report_page(img_url, alt):
            return f"""
                <td style="padding: 4px;">
                    <img src="{img_url}" alt="{alt}" width="164"
                        style="display: block; width: 100%; max-width: 164px; height: auto;
                                border: 1px solid #d8d2cc;" />
                </td>
            """

        return f"""
            <p style="margin: 0 0 20px 0; font-family: Arial, Helvetica, sans-serif;
                    font-size: 15px; line-height: 1.75; color: #555555;">
                Ton rapport ne s'arrête pas à une saison ou à un type de silhouette.<br><br>
                Il transforme les informations de ton profil en recommandations
                concrètes que tu peux réellement utiliser pour t'habiller et
                acheter plus facilement.
            </p>

            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
                style="margin-bottom: 24px;">
                <tr>
                    {report_page(palette_img, "Palette personnalisée")}
                    {report_page(coupes_img, "Recommandations morphologie")}
                    {report_page(looks_img, "Style et looks")}
                </tr>
            </table>

            <p style="margin: 0 0 28px 0; font-family: Arial, Helvetica, sans-serif;
                    font-size: 15px; line-height: 1.75; color: #555555;">
                <a href="{apercu_rapport_url}" style="color: #1B3022; font-weight: 600;">
                Voir un vrai extrait de rapport →</a>
            </p>

            <p style="margin: 0 0 20px 0; font-family: Arial, Helvetica, sans-serif;
                    font-size: 15px; line-height: 1.75; color: #555555;">
                Et l'analyse continue après le rapport :
            </p>

            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
                style="margin-bottom: 18px; border: 1px solid #d8d2cc;">
                <tr>
                    <td style="padding: 0;">
                        <img src="{recherche_img}" alt="Recherche MyStylist" width="504"
                            style="display: block; width: 100%; max-width: 504px; height: auto;" />
                    </td>
                </tr>
                <tr>
                    <td style="padding: 16px 20px;">
                        <p style="margin: 0 0 6px 0; font-family: Georgia, serif; font-size: 16px;
                                color: #1B3022;">Recherche</p>
                        <p style="margin: 0; font-family: Arial, Helvetica, sans-serif; font-size: 14px;
                                line-height: 1.6; color: #555;">
                            Les résultats sont filtrés selon ton profil, plutôt que des
                            centaines de résultats génériques.
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
                    <td style="padding: 16px 20px;">
                        <p style="margin: 0 0 6px 0; font-family: Georgia, serif; font-size: 16px;
                                color: #1B3022;">Garde-robe</p>
                        <p style="margin: 0; font-family: Arial, Helvetica, sans-serif; font-size: 14px;
                                line-height: 1.6; color: #555;">
                            Des idées de tenues pour mieux exploiter les vêtements que
                            tu possèdes déjà.
                        </p>
                    </td>
                </tr>
            </table>
        """


    REPORT_PRICES = {"colorimetrie": 39, "morphologie": 59, "complet": 79}

    def _email_3_body(self, promo_code) -> str:
        discounted = {k: round(v * 0.8, 2) for k, v in self.REPORT_PRICES.items()}

        code_block = f"""
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
                style="margin: 20px 0; border: 1px solid #8D8177; background-color: #f7f4f1;">
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

        prices_block = f"""
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom: 20px;">
                <tr>
                    <td style="font-family: Arial, Helvetica, sans-serif; font-size: 14px; color: #555; padding: 4px 0;">
                        Rapport Complet : <strong>{discounted['complet']}€</strong> au lieu de 79€
                    </td>
                </tr>
                <tr>
                    <td style="font-family: Arial, Helvetica, sans-serif; font-size: 13px; color: #8D8177; padding: 2px 0;">
                        Colorimétrie : {discounted['colorimetrie']}€ au lieu de 39€ · Morphologie : {discounted['morphologie']}€ au lieu de 59€
                    </td>
                </tr>
            </table>
        """

        return f"""
            <p style="margin: 0 0 16px 0; font-family: Arial, Helvetica, sans-serif;
                    font-size: 15px; line-height: 1.75; color: #555555;">
                Un dernier message au sujet de ton analyse MyStylist.<br><br>
                Si tu hésites encore, on t'a réservé une dernière offre : -20% sur
                le rapport de ton choix, pendant 48h.
            </p>
            {code_block}
            {prices_block}
            <p style="margin: 0 0 28px 0; font-family: Arial, Helvetica, sans-serif;
                    font-size: 14px; line-height: 1.7; color: #8D8177;">
                Passé ce délai, ce code ne sera plus utilisable.<br><br>
                Une dernière chose, si tu as deux secondes : qu'est-ce qui te retient
                encore ? Tu peux répondre directement à cet email — on lit chaque
                réponse.
            </p>
        """

# Instance globale à exporter
relance_service = RelanceService()