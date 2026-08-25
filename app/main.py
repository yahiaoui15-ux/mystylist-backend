import json
import uuid
import sys
import logging
import os
from pydantic import BaseModel
from typing import Optional
from app.services.relance_service import relance_service

from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from app.services.wardrobe_analysis_service import wardrobe_analysis_service

import stripe
from fastapi import FastAPI, Request, BackgroundTasks, Header, Depends
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse
from app.utils.auth import get_current_user_id
from app.services import entitlements

from app.config_prod import settings
from app.services import (
    email_service,
    pdf_generation,
    report_generator,
    supabase_reports,
)
from app.services.pdf_storage_manager import PDFStorageManager
from app.utils.supabase_client import supabase
from app.services.search_recommendation_service import search_recommendation_service
from app.services.wardrobe_suggestions_service import wardrobe_suggestions_service
# =====================================================
# CONFIGURATION LOGGING FORCE
# =====================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def log(message: str):
    """Force l'affichage du log immediatement"""
    print(message, flush=True)
    logger.info(message)
    sys.stdout.flush()

# =====================================================
# MAPPING STRIPE PRODUCT → RAPPORT TYPE + PDFMONKEY
# =====================================================
STRIPE_PRODUCT_REPORT_TYPE = {
    "prod_UVCryuc1tCV03U":  "colorimetrie",
    "prod_UVCt4ANPFNtWDR":  "morphologie",
    "prod_TDbm2sXLsIH6fa":  "complet",
}

# AJOUT — correspondance FR (interne) -> EN (schéma payments.report_type)
REPORT_TYPE_FR_TO_EN = {
    "colorimetrie": "colorimetry",
    "morphologie": "morphology",
    "complet": "complete",
}

PDFMONKEY_TEMPLATES = {
    "colorimetrie": "0122AF49-B0B9-4D10-9F1A-A2528FFE0CDD",
    "morphologie":  "59236C09-5823-43A0-99F2-5C7DF689DD16",
    "complet":      "4D4A47D1-361F-4133-B998-188B6AB08A37",
}

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

stripe.api_key = settings.STRIPE_SECRET_KEY
RELANCE_CRON_SECRET = os.getenv("RELANCE_CRON_SECRET", "")
RELANCE_COUPON_ID = os.getenv("RELANCE_COUPON_ID", "")

# --- Logs au boot pour verifier l'env deploye ---
log(f"[BOOT] Using SUPABASE_URL (masked): ...{settings.SUPABASE_URL[-16:]}")
log(f"[BOOT] Webhook route ready: /api/webhook/stripe")


class RelanceRequest(BaseModel):
    user_id: str
    email: str
    email_number: int
    first_name: Optional[str] = None
    eye_color: Optional[str] = None
    hair_color: Optional[str] = None
    primary_style: Optional[str] = None
    personality_trait: Optional[str] = None
    reports_tab_url: str = "https://my-stylist.io/auth?redirect=/app%3Ftab%3Drapports"
    apercu_rapport_url: str = "https://my-stylist.io/apercu-rapport"

# =====================================================
# ENDPOINTS DEBUG
# =====================================================
@app.get("/debug/supabase/env")
async def debug_supabase_env():
    if not settings.DEBUG:
        return JSONResponse(status_code=404, content={"error": "not_found"})
    url = settings.SUPABASE_URL
    return {
        "supabase_url_tail": url[-32:],
        "has_service_key": bool(settings.SUPABASE_KEY and len(settings.SUPABASE_KEY) > 20),
    }

@app.post("/debug/supabase/write")
async def debug_supabase_write():
    if not settings.DEBUG:
        return JSONResponse(status_code=404, content={"error": "not_found"})
    try:
        supabase.insert_table("stripe_events", {
            "id": f"evt_debug_{uuid.uuid4().hex[:8]}",
            "type": "debug.test",
            "session_id": "sess_debug",
            "created_at": datetime.utcnow().isoformat()
        })
        supabase.insert_table("reports", {
            "id": str(uuid.uuid4()),
            "user_id": "00000000-0000-0000-0000-000000000000",
            "payment_id": f"pay_debug_{uuid.uuid4().hex[:8]}",
            "pdf_url": "https://example.com/test.pdf",
            "email_sent": False,
            "created_at": datetime.utcnow().isoformat()
        })
        return {"ok": True}
    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

# =====================================================
# RELANCE EMAIL - Appelé par le cron Supabase
# =====================================================
@app.post("/api/relance/send")
async def send_relance(
    payload: RelanceRequest,
    x_cron_secret: str = Header(None, alias="x-cron-secret"),
):
    if not RELANCE_CRON_SECRET or x_cron_secret != RELANCE_CRON_SECRET:
        log(f"[RELANCE] Secret invalide ou manquant.")
        return JSONResponse(status_code=401, content={"ok": False, "error": "invalid_cron_secret"})

    if payload.email_number not in (1, 2, 3):
        return JSONResponse(status_code=400, content={"ok": False, "error": "invalid_email_number"})

    promo_code = None
    if payload.email_number == 3:
        if not RELANCE_COUPON_ID:
            log("[RELANCE] RELANCE_COUPON_ID non configure.")
            return JSONResponse(status_code=500, content={"ok": False, "error": "missing_coupon_id"})
        try:
            promo_code = relance_service.generate_promo_code(RELANCE_COUPON_ID)
        except Exception as e:
            log(f"[RELANCE] Erreur generation code promo: {e}")
            return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

    try:
        result = await relance_service.send_relance_email(
            user_id=payload.user_id,
            user_email=payload.email,
            email_number=payload.email_number,
            first_name=payload.first_name,
            eye_color=payload.eye_color,
            hair_color=payload.hair_color,
            primary_style=payload.primary_style,
            personality_trait=payload.personality_trait,
            reports_tab_url=payload.reports_tab_url,
            apercu_rapport_url=payload.apercu_rapport_url,
            promo_code=promo_code,
        )
    except Exception as e:
        log(f"[RELANCE] Erreur envoi email {payload.email_number}: {e}")
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

    log(f"[RELANCE] Email {payload.email_number} envoye a {payload.email}")
    return {
        "ok": True,
        "email_id": result.get("email_id"),
        "user_id": payload.user_id,
        "email_number": payload.email_number,
        "promo_code": promo_code,
    }


@app.get("/api/relance/unsubscribe")
async def unsubscribe_get(u: str):
    """Lien cliquable dans le corps de l'email + clic manuel."""
    try:
        supabase.update_table("relance_tracking", {"unsubscribed": True}, filters={"user_id": u})
        log(f"[RELANCE] Desabonnement (GET) user_id={u}")
    except Exception as e:
        log(f"[RELANCE] Erreur desabonnement GET user_id={u}: {e}")
    return HTMLResponse("""
        <html><body style="font-family: Arial; text-align: center; padding: 60px 20px;">
        <h2 style="color: #1B3022;">Vous êtes désabonné(e)</h2>
        <p style="color: #555;">Vous ne recevrez plus d'emails de relance de MyStylist.io.</p>
        </body></html>
    """)


@app.post("/api/relance/unsubscribe")
async def unsubscribe_post(u: str):
    """Appelé automatiquement par le client mail (bouton natif Gmail/Outlook)."""
    try:
        supabase.update_table("relance_tracking", {"unsubscribed": True}, filters={"user_id": u})
        log(f"[RELANCE] Desabonnement (POST one-click) user_id={u}")
    except Exception as e:
        log(f"[RELANCE] Erreur desabonnement POST user_id={u}: {e}")
    return JSONResponse(status_code=200, content={"ok": True})

@app.get("/api/searches/{search_id}/recommendations")


async def get_search_recommendations(search_id: str, user_id: str = Depends(get_current_user_id)):
    owner_check = supabase.query("user_searches", select_fields="user_id", filters={"id": search_id})
    if not owner_check.data or owner_check.data[0].get("user_id") != user_id:
        return JSONResponse(status_code=403, content={"ok": False, "error": "forbidden"})
    """
    Retourne les recommandations déjà générées pour une recherche,
    sans relancer une nouvelle génération.
    """
    try:
        log(f"[SEARCH_RECO] Fetch existing recommendations for search_id={search_id}")
        result = await search_recommendation_service.get_saved_recommendations_for_search(search_id)
        log(
            f"[SEARCH_RECO] Existing recommendations result for search_id={search_id}: "
            f"ok={result.get('ok')} found={result.get('found')}"
        )

        if result.get("ok") and result.get("found"):
            return result

        return JSONResponse(
            status_code=404,
            content={
                "ok": False,
                "search_id": search_id,
                "error": "recommendations_not_found",
            },
        )

    except Exception as e:
        log(f"[SEARCH_RECO] GET exception for search_id={search_id}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "search_id": search_id,
                "error": str(e),
            },
        )

@app.post("/api/searches/{search_id}/generate-recommendations")
async def generate_search_recommendations(search_id: str, user_id: str = Depends(get_current_user_id)):
    """
    Génère les recommandations affiliées pour une recherche sauvegardée.
    Remplace le pipeline Make.com.
    """
    owner_check = supabase.query("user_searches", select_fields="user_id", filters={"id": search_id})
    if not owner_check.data or owner_check.data[0].get("user_id") != user_id:
        return JSONResponse(status_code=403, content={"ok": False, "error": "forbidden"})

    allowed, reason = entitlements.check_search_access(user_id)
    if not allowed:
        return JSONResponse(status_code=402, content={"ok": False, "error": reason, "upgrade_url": "/auth"})


    try:
        log(f"[SEARCH_RECO] Start generation for search_id={search_id}")
        result = await search_recommendation_service.generate_for_search(search_id)
        log(f"[SEARCH_RECO] Result for search_id={search_id}: {result}")

        if result.get("status") == "success":
            entitlements.consume_search(user_id)
            return {
                "ok": True,
                "search_id": search_id,
                "run_id": result.get("run_id"),
                "recommendations_inserted": result.get("recommendations_inserted", 0),
            }

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "search_id": search_id,
                "run_id": result.get("run_id"),
                "error": result.get("error", "unknown_error"),
            },
        )
    except Exception as e:
        log(f"[SEARCH_RECO] Unhandled exception for search_id={search_id}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "search_id": search_id,
                "error": str(e),
            },
        )

@app.post("/api/wardrobe/{item_id}/analyze")
async def analyze_wardrobe_item(item_id: str, user_id: str = Depends(get_current_user_id)):
    """
    Analyse un vêtement uploadé dans wardrobe_items et remplit les colonnes IA.
    """
    owner_check = supabase.query("wardrobe_items", select_fields="user_id", filters={"id": item_id})
    if not owner_check.data or owner_check.data[0].get("user_id") != user_id:
        return JSONResponse(status_code=403, content={"ok": False, "error": "forbidden"})

    allowed, reason = entitlements.check_upload_access(user_id)
    if not allowed:
        return JSONResponse(status_code=402, content={"ok": False, "error": reason, "upgrade_url": "/auth"})


    try:
        log(f"[WARDROBE] Start analysis for item_id={item_id}")
        result = await wardrobe_analysis_service.analyze_item(item_id)
        log(f"[WARDROBE] Result for item_id={item_id}: {result}")

        if result.get("status") == "success":
            entitlements.consume_upload(user_id)
            return {
                "ok": True,
                "item_id": item_id,
                "category_key": result.get("category_key"),
                "ai_label": result.get("ai_label"),
            }

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "item_id": item_id,
                "error": result.get("error", "unknown_error"),
            },
        )
    except Exception as e:
        log(f"[WARDROBE] Unhandled exception for item_id={item_id}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "item_id": item_id,
                "error": str(e),
            },
        )

@app.get("/api/wardrobe/{item_id}/suggestions")
async def get_wardrobe_suggestions(item_id: str, user_id: str = Depends(get_current_user_id)):
    owner_check = supabase.query("wardrobe_items", select_fields="user_id", filters={"id": item_id})
    if not owner_check.data or owner_check.data[0].get("user_id") != user_id:
        return JSONResponse(status_code=403, content={"ok": False, "error": "forbidden"})
    """
    Retourne les suggestions déjà générées pour un vêtement central,
    sans relancer une nouvelle génération.
    """
    try:
        log(f"[WARDROBE_SUGGESTIONS] Fetch existing suggestions for item_id={item_id}")
        result = await wardrobe_suggestions_service.get_saved_suggestions_for_item(item_id)
        log(
            f"[WARDROBE_SUGGESTIONS] Existing suggestions result for item_id={item_id}: "
            f"ok={result.get('ok')} found={result.get('found')}"
        )

        if result.get("ok") and result.get("found"):
            return result

        return JSONResponse(
            status_code=404,
            content={
                "ok": False,
                "item_id": item_id,
                "error": "suggestions_not_found",
            },
        )

    except Exception as e:
        log(f"[WARDROBE_SUGGESTIONS] GET exception for item_id={item_id}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "item_id": item_id,
                "error": str(e),
            },
        )  

@app.post("/api/wardrobe/{item_id}/suggestions")
async def generate_wardrobe_suggestions(item_id: str, user_id: str = Depends(get_current_user_id)):
    owner_check = supabase.query("wardrobe_items", select_fields="user_id", filters={"id": item_id})
    if not owner_check.data or owner_check.data[0].get("user_id") != user_id:
        return JSONResponse(status_code=403, content={"ok": False, "error": "forbidden"})
    """
    Régénère les suggestions de produits affiliés complémentaires
    autour d'un vêtement central de la garde-robe
    et remplace la version sauvegardée.
    """
    try:
        log(f"[WARDROBE_SUGGESTIONS] Start generation for item_id={item_id}")
        result = await wardrobe_suggestions_service.generate_for_item(item_id)
        log(f"[WARDROBE_SUGGESTIONS] Result for item_id={item_id}: ok={result.get('ok')}")

        return result

    except Exception as e:
        log(f"[WARDROBE_SUGGESTIONS] Unhandled exception for item_id={item_id}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "item_id": item_id,
                "error": str(e),
            },
        )
# =====================================================
# WEBHOOK STRIPE - IDEMPOTENT & ACK 200 IMMEDIAT
# =====================================================
@app.post("/api/webhook/stripe")
async def handle_stripe_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    stripe_signature: str = Header(None, alias="Stripe-Signature")
):
    """
    On repond TOUJOURS 200 a Stripe pour eviter tout retry.
    """
    try:
        payload_bytes = await request.body()

        # 1) Verif signature
        try:
            event = stripe.Webhook.construct_event(
                payload=payload_bytes,
                sig_header=stripe_signature,
                secret=settings.STRIPE_WEBHOOK_SECRET
            )
        except Exception as sig_err:
            log(f"[WEBHOOK] Signature invalide: {sig_err} - event ignore (ACK 200).")
            return JSONResponse(status_code=200, content={"ok": True, "ignored": "bad_signature"})

        evt_id = event.get("id")
        evt_type = event.get("type")
        log(f">>> WEBHOOK RECU : {evt_type} ({evt_id})")

        # 2) Idempotence event Stripe
        try:
            existing_evt = supabase.query("stripe_events", select_fields="id", filters={"id": evt_id})
            if existing_evt.data:
                log(">>> Event Stripe deja traite -> stop (ACK 200).")
                return JSONResponse(status_code=200, content={"ok": True, "deduped": True})
            supabase.insert_table("stripe_events", {
                "id": evt_id,
                "type": evt_type,
                "session_id": event.get("data", {}).get("object", {}).get("id"),
                "created_at": datetime.utcnow().isoformat()
            })
        except Exception as e:
            log(f">>> Echec log stripe_events (on continue): {e}")

        # 3) On ne traite que checkout.session.completed
        if evt_type != "checkout.session.completed":
            return JSONResponse(status_code=200, content={"ok": True, "ignored": evt_type})

        session = event["data"]["object"]
        user_id = (session.get("metadata") or {}).get("userId")
        payment_id = session.get("id")

        if not user_id or not payment_id:
            log("[WEBHOOK] Missing userId/payment_id - ACK 200 et on ignore.")
            return JSONResponse(status_code=200, content={"ok": True, "ignored": "missing_fields"})

        # 4) Dedoublonnage par payment_id
        try:
            existing = supabase.query("reports", select_fields="id", filters={"payment_id": payment_id})
            if existing.data:
                log(">>> Rapport deja genere pour ce payment_id (ACK 200).")
                return JSONResponse(status_code=200, content={"ok": True, "already_processed": True})
        except Exception as e:
            log(f"[WEBHOOK] Lookup reports failed (on continue): {e}")

        # 5) Identifier le type de rapport depuis le produit Stripe acheté
        report_type = "complet"  # fallback par défaut
        template_id = PDFMONKEY_TEMPLATES["complet"]

        try:
            line_items = stripe.checkout.Session.list_line_items(payment_id, limit=1)
            if line_items.data:
                product_id = line_items.data[0].price.product
                log(f">>> Produit Stripe détecté: {product_id}")
                report_type = STRIPE_PRODUCT_REPORT_TYPE.get(product_id, "complet")
                template_id = PDFMONKEY_TEMPLATES.get(report_type, PDFMONKEY_TEMPLATES["complet"])
                log(f">>> Type rapport: {report_type} | Template PDFMonkey: {template_id}")
        except Exception as e:
            log(f"[WEBHOOK] Impossible de lire les line_items (fallback complet): {e}")

        # 5bis) Enregistrer le paiement dans payments (source de vérité des achats)
        try:
            report_type_en = REPORT_TYPE_FR_TO_EN.get(report_type, "complete")
            supabase.insert_table("payments", {
                "user_id": user_id,
                "stripe_session_id": payment_id,
                "stripe_payment_id": session.get("payment_intent"),
                "report_type": report_type_en,
                "amount": session.get("amount_total"),
                "currency": (session.get("currency") or "eur").upper(),
                "status": "completed",
            })
            log(f">>> payments: ligne inserée ({report_type_en}, session={payment_id})")
        except Exception as e:
            log(f"[WEBHOOK] Echec insertion payments (on continue): {e}")

        # 6) Lancer le job asynchrone et ACK 200 tout de suite
        log(f">>> LANCEMENT TACHE ASYNC user={user_id} payment={payment_id} type={report_type}")
        background_tasks.add_task(
            process_checkout_session_job,
            user_id,
            payment_id,
            report_type,
            template_id
        )
        log(f">>> Tache ajoutee, retour 200 a Stripe")
        return JSONResponse(status_code=200, content={"ok": True})

    except Exception as e:
        log(f">>> WEBHOOK EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=200, content={"ok": True, "note": "exception_caught_but_acked"})


# =====================================================
# TACHE ASYNCHRONE : IA + PDF + MAIL
# =====================================================
async def process_checkout_session_job(
    user_id: str,
    payment_id: str,
    report_type: str = "complet",
    template_id: str = None
):
    """Tache de generation de rapport - logs forces"""
    log(f"========== DEBUT TACHE ASYNC ==========")
    log(f">>> user_id={user_id}")
    log(f">>> payment_id={payment_id}")
    log(f">>> report_type={report_type}")
    log(f">>> template_id={template_id}")
    
    try:
        log(">>> Etape 1: Recuperation profil utilisateur...")

        # Recup infos utilisateur
        profile_response = supabase.query("user_profiles", select_fields="*", filters={"user_id": user_id})
        user_profile = profile_response.data[0] if profile_response.data else {}
        log(f">>> Profile trouve: {bool(user_profile)}")

        photos_response = supabase.query("user_photos", select_fields="*", filters={"user_id": user_id})
        photos = photos_response.data if photos_response.data else []
        photos.sort(key=lambda p: p.get("created_at") or "", reverse=True)
        log(f">>> Photos trouvees: {len(photos)}")

        auth_response = supabase.query("profiles", select_fields="*", filters={"id": user_id})
        auth = auth_response.data[0] if auth_response.data else {}

        user_email = auth.get("email")
        first_name = auth.get("first_name", "Client(e)")
        last_name = auth.get("last_name", "")
        user_name = f"{first_name} {last_name}".strip()
        
        log(f">>> Email: {user_email}")
        log(f">>> Nom: {user_name}")

        # Extraire les URLs des photos par type
        face_photo_url = None
        body_photo_url = None
        
        log(f">>> Traitement de {len(photos)} photo(s)...")
        
        for photo in photos:
            photo_type = photo.get("photo_type", "").lower()
            photo_url = photo.get("cloudinary_url", "")
            
            log(f">>>    Photo: type='{photo_type}'")
            
            if "face" in photo_type and not face_photo_url:
                face_photo_url = photo_url
                log(f">>>    -> Assigne comme FACE")
            elif "body" in photo_type and not body_photo_url:
                body_photo_url = photo_url
                log(f">>>    -> Assigne comme BODY")
        
        # Fallback
        if not face_photo_url and len(photos) > 0:
            face_photo_url = photos[0].get("cloudinary_url", "")
            log(f">>> Fallback: 1ere photo comme FACE")
        if not body_photo_url and len(photos) > 1:
            body_photo_url = photos[1].get("cloudinary_url", "")
            log(f">>> Fallback: 2eme photo comme BODY")

        log(f">>> face_photo_url: {face_photo_url[:50] if face_photo_url else 'NONE'}...")
        log(f">>> body_photo_url: {body_photo_url[:50] if body_photo_url else 'NONE'}...")

        # ✅ EXTRAIRE LES DONNEES DU JSONB
        onboarding_data = user_profile.get("onboarding_data", {})
        personal_info = onboarding_data.get("personal_info", {})
        measurements = onboarding_data.get("measurements", {})
        color_prefs = onboarding_data.get("color_preferences", {})
        morphology_goals = onboarding_data.get("morphology_goals", {})  # ✅ NOUVEAU

        # ✅ EXTRAIRE clothing_size
        clothing_size = measurements.get("clothing_size", "")
        log(f">>> Clothing size extrait: {clothing_size}")

        user_data = {
            "user_id": user_id,
            "user_email": user_email,
            "user_name": user_name,
            "first_name": first_name,
            "last_name": last_name,
            "profile": user_profile,
            "photos": photos,
            "face_photo_url": face_photo_url,
            "body_photo_url": body_photo_url,
            "eye_color": onboarding_data.get("eye_color", ""),
            "hair_color": onboarding_data.get("hair_color", ""),
            "age": personal_info.get("age", 0),
            "height": personal_info.get("height", 0),
            "weight": personal_info.get("weight", 0),
            "shoulder_circumference": measurements.get("shoulder_circumference", 0),
            "waist_circumference": measurements.get("waist_circumference", 0),
            "hip_circumference": measurements.get("hip_circumference", 0),
            "bust_circumference": measurements.get("shoulder_circumference", 0),
            "clothing_size": clothing_size,  # ✅ NOUVEAU
            "morphology_goals": morphology_goals,  # ✅ NOUVEAU
            "unwanted_colors": color_prefs.get("disliked_colors", [])
        }

        log(f">>> User data extrait:")
        log(f">>>    age: {user_data['age']}")
        log(f">>>    height: {user_data['height']}")
        log(f">>>    clothing_size: {user_data['clothing_size']}")  # ✅ NOUVEAU
        log(f">>>    eye_color: {user_data['eye_color']}")
        log(f">>>    hair_color: {user_data['hair_color']}")
        log(f">>>    morphology_goals: {user_data['morphology_goals']}")  # ✅ NOUVEAU

        # Garde-fou email
        existing = supabase.query("reports", select_fields="email_sent", filters={"payment_id": payment_id})
        if existing.data and existing.data[0].get("email_sent"):
            log(">>> Email deja envoye -> on arrete ici.")
            return

        # IA : Generation du rapport selon le type acheté
        log(f">>> Etape 2: GENERATION RAPPORT IA (type={report_type})...")
        if report_type == "colorimetrie":
            report = await report_generator.generate_colorimetry_report(user_data)
        elif report_type == "morphologie":
            report = await report_generator.generate_morphology_report(user_data)
        else:
            report = await report_generator.generate_complete_report(user_data)
        log(f">>> Rapport IA genere!")

        # PDF - Generer via PDFMonkey
        log(">>> Etape 3: GENERATION PDF...")
        pdf_url_temporary = await pdf_generation.generate_report_pdf(
            report, user_data, template_id=template_id
        )
        log(f">>> PDF genere (temporaire): {pdf_url_temporary[:60]}...")

        # Sauvegarder dans Supabase (lien PERMANENT)
        log(">>> Etape 4: SAUVEGARDE PDF PERMANENT...")
        try:
            pdf_url_permanent = await PDFStorageManager.download_and_save_pdf(
                pdf_url=pdf_url_temporary,
                user_id=user_id,
                report_id=payment_id
            )
            
            if pdf_url_permanent:
                pdf_url = pdf_url_permanent
                log(f">>> PDF sauvegarde permanemment!")
            else:
                log(">>> Erreur sauvegarde, utilisation lien temporaire")
                pdf_url = pdf_url_temporary
                
        except Exception as e:
            log(f">>> Exception sauvegarde PDF: {e}")
            pdf_url = pdf_url_temporary

        # Email
        if pdf_url:
            log(f">>> Etape 5: ENVOI EMAIL...")
            await email_service.send_report_email(
                user_email=user_email,
                user_name=user_name,
                pdf_url=pdf_url,
                report_type=report_type,
                report_data=report
            )
            log(">>> Email envoye!")

        # Sauvegarde en base
        # ✅ nouveau : stocke les JSON IA (color/morph/style)
        await supabase_reports.save_report_metadata(
            user_id=user_id,
            payment_id=payment_id,
            report_data=report,
            pdf_url=pdf_url,
            report_type=report_type
        )
        log(">>> Rapport sauvegarde dans Supabase.")
        log(f"========== FIN TACHE ASYNC (SUCCES) ==========")

    except Exception as e:
        log(f">>> ERREUR TACHE ASYNC: {e}")
        import traceback
        traceback.print_exc()
        log(f"========== FIN TACHE ASYNC (ECHEC) ==========")