import json
import uuid
import sys
import logging
from datetime import datetime

import stripe
from fastapi import FastAPI, Request, BackgroundTasks, Header
from fastapi.responses import JSONResponse

from app.config_prod import settings
from app.services import (
    email_service,
    pdf_generation,
    report_generator,
    supabase_reports,
)
from app.services.pdf_storage_manager import PDFStorageManager
from app.utils.supabase_client import supabase

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

app = FastAPI()
stripe.api_key = settings.STRIPE_SECRET_KEY

# --- Logs au boot pour verifier l'env deploye ---
log(f"[BOOT] Using SUPABASE_URL (masked): ...{settings.SUPABASE_URL[-16:]}")
log(f"[BOOT] Webhook route ready: /api/webhook/stripe")


# =====================================================
# ENDPOINTS DEBUG
# =====================================================
@app.get("/debug/supabase/env")
async def debug_supabase_env():
    url = settings.SUPABASE_URL
    return {
        "supabase_url_tail": url[-32:],
        "has_service_key": bool(settings.SUPABASE_KEY and len(settings.SUPABASE_KEY) > 20),
    }


@app.post("/debug/supabase/write")
async def debug_supabase_write():
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

        # 5) Lancer le job asynchrone et ACK 200 tout de suite
        log(f">>> LANCEMENT TACHE ASYNC user={user_id} payment={payment_id}")
        background_tasks.add_task(process_checkout_session_job, user_id, payment_id)
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
async def process_checkout_session_job(user_id: str, payment_id: str):
    """Tache de generation de rapport - logs forces"""
    log(f"========== DEBUT TACHE ASYNC ==========")
    log(f">>> user_id={user_id}")
    log(f">>> payment_id={payment_id}")
    
    try:
        log(">>> Etape 1: Recuperation profil utilisateur...")

        # Recup infos utilisateur
        profile_response = supabase.query("user_profiles", select_fields="*", filters={"user_id": user_id})
        user_profile = profile_response.data[0] if profile_response.data else {}
        log(f">>> Profile trouve: {bool(user_profile)}")

        photos_response = supabase.query("user_photos", select_fields="*", filters={"user_id": user_id})
        photos = photos_response.data if photos_response.data else []
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

        # Extraire les donnees du JSONB
        onboarding_data = user_profile.get("onboarding_data", {})
        personal_info = onboarding_data.get("personal_info", {})
        measurements = onboarding_data.get("measurements", {})
        color_prefs = onboarding_data.get("color_preferences", {})

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
            "unwanted_colors": color_prefs.get("disliked_colors", [])
        }

        log(f">>> User data extrait:")
        log(f">>>    age: {user_data['age']}")
        log(f">>>    height: {user_data['height']}")
        log(f">>>    eye_color: {user_data['eye_color']}")
        log(f">>>    hair_color: {user_data['hair_color']}")

        # Garde-fou email
        existing = supabase.query("reports", select_fields="email_sent", filters={"payment_id": payment_id})
        if existing.data and existing.data[0].get("email_sent"):
            log(">>> Email deja envoye -> on arrete ici.")
            return

        # IA : Generation du rapport complet
        log(">>> Etape 2: GENERATION RAPPORT IA...")
        report = await report_generator.generate_complete_report(user_data)
        log(f">>> Rapport IA genere!")

        # PDF - Generer via PDFMonkey
        log(">>> Etape 3: GENERATION PDF...")
        pdf_url_temporary = await pdf_generation.generate_report_pdf(report, user_data)
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
                report_data=report
            )
            log(">>> Email envoye!")

        # Sauvegarde en base
        supabase.insert_table("reports", {
            "user_id": user_id,
            "payment_id": payment_id,
            "pdf_url": pdf_url,
            "email_sent": True,
            "created_at": datetime.utcnow().isoformat()
        })
        log(">>> Rapport sauvegarde dans Supabase.")
        log(f"========== FIN TACHE ASYNC (SUCCES) ==========")

    except Exception as e:
        log(f">>> ERREUR TACHE ASYNC: {e}")
        import traceback
        traceback.print_exc()
        log(f"========== FIN TACHE ASYNC (ECHEC) ==========")