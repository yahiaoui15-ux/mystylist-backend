import json
import uuid
from datetime import datetime

import stripe
from fastapi import FastAPI, Request, BackgroundTasks, Header
from fastapi.responses import JSONResponse

from app.config_prod import settings
from app.services import (
    email_service,
    pdf_generation,
    report_generator,
    supabase_reports,  # gardé si tu l'utilises ailleurs
)
from app.utils.supabase_client import supabase

app = FastAPI()
stripe.api_key = settings.STRIPE_SECRET_KEY

# --- Logs au boot pour vérifier l'env déployé ---
print(f"[BOOT] Using SUPABASE_URL (masked): ...{settings.SUPABASE_URL[-16:]}")
print(f"[BOOT] Webhook route ready: /api/webhook/stripe")


# =====================================================
# ENDPOINTS DEBUG (à supprimer quand tout est OK)
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
            "id": str(uuid.uuid4()),  # si ta colonne id est uuid pk avec default, tu peux retirer cette ligne
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
# WEBHOOK STRIPE — IDÉMPOTENT & ACK 200 IMMÉDIAT
# =====================================================
@app.post("/api/webhook/stripe")
async def handle_stripe_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    stripe_signature: str = Header(None, alias="Stripe-Signature")
):
    """
    On répond TOUJOURS 200 à Stripe pour éviter tout retry.
    - Vérif signature : si invalide, on ignore mais on ACK 200.
    - Dédup par event.id (table stripe_events).
    - On ne traite que checkout.session.completed.
    - Le job lourd (IA -> PDF -> Email) part en tâche de fond.
    """
    try:
        payload_bytes = await request.body()

        # 1) Vérif signature — si mauvaise, on ACK 200 mais on ne traite pas
        try:
            event = stripe.Webhook.construct_event(
                payload=payload_bytes,
                sig_header=stripe_signature,
                secret=settings.STRIPE_WEBHOOK_SECRET
            )
        except Exception as sig_err:
            print(f"[WEBHOOK] Signature invalide: {sig_err} — event ignoré (ACK 200).")
            return JSONResponse(status_code=200, content={"ok": True, "ignored": "bad_signature"})

        evt_id = event.get("id")
        evt_type = event.get("type")
        print(f"💬 Webhook reçu : {evt_type} ({evt_id})")

        # 2) Idempotence event Stripe
        try:
            existing_evt = supabase.query("stripe_events", select_fields="id", filters={"id": evt_id})
            if existing_evt.data:
                print("🛑 Événement Stripe déjà traité → stop (ACK 200).")
                return JSONResponse(status_code=200, content={"ok": True, "deduped": True})
            supabase.insert_table("stripe_events", {
                "id": evt_id,
                "type": evt_type,
                "session_id": event.get("data", {}).get("object", {}).get("id"),
                "created_at": datetime.utcnow().isoformat()
            })
        except Exception as e:
            # Ne jamais échouer le webhook → Stripe ne doit pas retenter
            print(f"⚠️ Échec log stripe_events (on continue quand même): {e}")

        # 3) On ne traite que checkout.session.completed
        if evt_type != "checkout.session.completed":
            return JSONResponse(status_code=200, content={"ok": True, "ignored": evt_type})

        session = event["data"]["object"]
        user_id = (session.get("metadata") or {}).get("userId")
        payment_id = session.get("id")

        if not user_id or not payment_id:
            print("[WEBHOOK] Missing userId/payment_id — ACK 200 et on ignore.")
            return JSONResponse(status_code=200, content={"ok": True, "ignored": "missing_fields"})

        # 4) Dédoublonnage par payment_id
        try:
            existing = supabase.query("reports", select_fields="id", filters={"payment_id": payment_id})
            if existing.data:
                print("🛑 Rapport déjà généré pour ce payment_id (ACK 200).")
                return JSONResponse(status_code=200, content={"ok": True, "already_processed": True})
        except Exception as e:
            print(f"[WEBHOOK] Lookup reports failed (on continue): {e}")

        # 5) Lancer le job asynchrone et ACK 200 tout de suite
        background_tasks.add_task(process_checkout_session_job, user_id, payment_id)
        print(f"🚀 Tâche asynchrone lancée user={user_id} payment={payment_id}")
        return JSONResponse(status_code=200, content={"ok": True})

    except Exception as e:
        # QUOI QU'IL ARRIVE : on ACK 200 pour stopper les retries Stripe
        print(f"❌ Webhook exception (ACK 200 quand même): {e}")
        return JSONResponse(status_code=200, content={"ok": True, "note": "exception_caught_but_acked"})


# =====================================================
# TÂCHE ASYNCHRONE : IA + PDF + MAIL
# =====================================================
async def process_checkout_session_job(user_id: str, payment_id: str):
    try:
        print("📄 Début de génération du rapport IA")

        # Récup infos utilisateur
        profile_response = supabase.query("user_profiles", select_fields="*", filters={"user_id": user_id})
        user_profile = profile_response.data[0] if profile_response.data else {}

        photos_response = supabase.query("user_photos", select_fields="*", filters={"user_id": user_id})
        photos = photos_response.data if photos_response.data else []

        auth_response = supabase.query("profiles", select_fields="*", filters={"id": user_id})
        auth = auth_response.data[0] if auth_response.data else {}

        user_email = auth.get("email")
        user_name = user_profile.get("first_name", "Client(e)")

        # Extraire les URLs des photos par type
        face_photo_url = None
        body_photo_url = None
        
        for photo in photos:
            photo_type = photo.get("type", "").lower()
            photo_url = photo.get("url", photo.get("photo_url", ""))
            
            if "face" in photo_type and not face_photo_url:
                face_photo_url = photo_url
            elif "body" in photo_type and not body_photo_url:
                body_photo_url = photo_url
        
        # Fallback: si pas de type, utiliser les deux premiers
        if not face_photo_url and len(photos) > 0:
            face_photo_url = photos[0].get("url", photos[0].get("photo_url", ""))
        if not body_photo_url and len(photos) > 1:
            body_photo_url = photos[1].get("url", photos[1].get("photo_url", ""))

        user_data = {
            "user_id": user_id,
            "user_email": user_email,
            "user_name": user_name,
            "profile": user_profile,
            "photos": photos,
            "face_photo_url": face_photo_url,
            "body_photo_url": body_photo_url,
            "eye_color": user_profile.get("eye_color", ""),
            "hair_color": user_profile.get("hair_color", ""),
            "age": user_profile.get("age", 0),
            "shoulder_circumference": user_profile.get("shoulder_circumference", 0),
            "waist_circumference": user_profile.get("waist_circumference", 0),
            "hip_circumference": user_profile.get("hip_circumference", 0),
            "bust_circumference": user_profile.get("bust_circumference", 0),
            "unwanted_colors": user_profile.get("unwanted_colors", [])
        }

        # Garde-fou email (au cas où Stripe re-tente malgré tout)
        existing = supabase.query("reports", select_fields="email_sent", filters={"payment_id": payment_id})
        if existing.data and existing.data[0].get("email_sent"):
            print("🛑 Email déjà envoyé → on arrête ici.")
            return

        # IA : Génération du rapport complet
        report = await report_generator.generate_complete_report(user_data)

        # PDF
        pdf_url = await pdf_generation.generate_report_pdf(report, user_data)
        print(f"✅ PDF généré : {pdf_url}")

        # Email
        if pdf_url:
            await email_service.send_report_email(
                user_email=user_email,
                user_name=user_name,
                pdf_url=pdf_url,
                report_data=report
            )
            print("📧 Email envoyé au client.")

        # Sauvegarde en base (clé métier = payment_id)
        supabase.insert_table("reports", {
            "user_id": user_id,
            "payment_id": payment_id,
            "pdf_url": pdf_url,
            "email_sent": True,
            "created_at": datetime.utcnow().isoformat()
        })
        print("💾 Rapport sauvegardé dans Supabase.")

    except Exception as e:
        print(f"❌ Erreur pendant la tâche de génération : {e}")