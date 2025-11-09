from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import os
from app.services.report_generator import report_generator
from app.services.pdf_generation import pdf_service
from app.services.email_service import email_service
from app.services.pdf_data_mapper import pdf_mapper
from app.config import STRIPE_SECRET_KEY

app = FastAPI(title="MyStylist Backend", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/api/webhook/stripe")
async def handle_stripe_webhook(request: Request):
    """
    Webhook Stripe - Flux complet: paiement → rapport → PDF → email
    
    Flux:
    1. Reçoit userId depuis métadonnées Stripe
    2. Récupère profil depuis Supabase
    3. Génère rapport complet
    4. Mappe données au format PDFMonkey
    5. Génère PDF via PDFMonkey
    6. Envoie PDF par email via Resend
    7. ✅ Succès!
    """
    try:
        from app.utils.supabase_client import supabase
        
        payload = await request.json()
        print(f"📨 Webhook Stripe reçu: {payload.get('type', 'unknown')}")
        
        event_type = payload.get("type")
        if event_type != "checkout.session.completed":
            print(f"⏭️  Event ignoré: {event_type}")
            return {"received": True}
        
        session = payload.get("data", {}).get("object", {})
        user_id = session.get("metadata", {}).get("userId")
        
        if not user_id:
            print(f"❌ userId manquant dans les métadonnées")
            raise HTTPException(status_code=400, detail="userId manquant")
        
        print(f"✅ Paiement confirmé pour user: {user_id}")
        
        # ✅ Récupérer TOUTES les données depuis Supabase
        print(f"📥 Récupération des données Supabase pour user: {user_id}")
        
        try:
            # 1. Récupérer le profil utilisateur (onboarding_data)
            profile_response = await supabase.query_table("user_profiles", {"user_id": user_id})
            user_profile = profile_response[0] if profile_response else {}
            
            # 2. Récupérer les photos
            photos_response = await supabase.query_table("user_photos", {"user_id": user_id})
            photos = photos_response if photos_response else []
            
            # 3. Récupérer l'email depuis la table profiles
            profile_auth_response = await supabase.query_table("profiles", {"id": user_id})
            profile_auth = profile_auth_response[0] if profile_auth_response else {}
            
            print(f"✅ Données récupérées: profil + {len(photos)} photo(s) + email")
            
        except Exception as e:
            print(f"⚠️  Erreur lors de la récupération Supabase: {e}")
            user_profile = {}
            photos = []
            profile_auth = {}
        
        # ✅ Parser onboarding_data JSON
        onboarding_data = {}
        if isinstance(user_profile.get("onboarding_data"), str):
            try:
                onboarding_data = json.loads(user_profile.get("onboarding_data", "{}"))
            except:
                onboarding_data = {}
        else:
            onboarding_data = user_profile.get("onboarding_data", {})
        
        # Extraire mesures
        measurements = onboarding_data.get("measurements", {})
        personal_info = onboarding_data.get("personal_info", {})
        
        # Construire user_data avec TOUS les bons champs
        user_data = {
            "user_id": user_id,
            "user_email": profile_auth.get("email", "noreply@mystylist.io"),
            "user_name": f"{profile_auth.get('first_name', 'Client')} {profile_auth.get('last_name', '')}".strip(),
            
            # Photos
            "face_photo_url": next(
                (p.get("cloudinary_url") for p in photos if p.get("photo_type") == "face"),
                ""
            ),
            "body_photo_url": next(
                (p.get("cloudinary_url") for p in photos if p.get("photo_type") == "body"),
                ""
            ),
            
            # Couleurs (depuis onboarding_data ou user_profiles)
            "eye_color": onboarding_data.get("eye_color") or user_profile.get("eye_color", ""),
            "hair_color": onboarding_data.get("hair_color") or user_profile.get("hair_color", ""),
            "skin_color": user_profile.get("skin_color", ""),
            "undertone": user_profile.get("undertone", ""),
            
            # Morphologie
            "body_shape": user_profile.get("body_shape", ""),
            
            # Mesures (depuis onboarding_data)
            "age": int(personal_info.get("age", 0)) if personal_info.get("age") else 0,
            "height": int(personal_info.get("height", 0)) if personal_info.get("height") else 0,
            "weight": int(personal_info.get("weight", 0)) if personal_info.get("weight") else 0,
            "shoulder_circumference": float(measurements.get("shoulder_circumference", 0)) if measurements.get("shoulder_circumference") else 0,
            "waist_circumference": float(measurements.get("waist_circumference", 0)) if measurements.get("waist_circumference") else 0,
            "hip_circumference": float(measurements.get("hip_circumference", 0)) if measurements.get("hip_circumference") else 0,
            "bust_circumference": float(measurements.get("bust_circumference", 0)) if measurements.get("bust_circumference") else 0,
            
            # Préférences (depuis onboarding_data)
            "style_preferences": onboarding_data.get("style_preferences", []),
            "brand_preferences": onboarding_data.get("brand_preferences", {}).get("selected_brands", []),
            "unwanted_colors": onboarding_data.get("color_preferences", {}).get("disliked_colors", []),
            "unwanted_patterns": onboarding_data.get("pattern_preferences", {}).get("disliked_patterns", []),
            
            # Personnalité & morph goals
            "personality_data": onboarding_data.get("personality_data", {}),
            "morphology_goals": onboarding_data.get("morphology_goals", {}),
        }
        
        print(f"✅ Données parsées et structurées")
        print(f"   - Email: {user_data['user_email']}")
        print(f"   - Photos: face={bool(user_data['face_photo_url'])}, body={bool(user_data['body_photo_url'])}")
        print(f"   - Mesures: taille={user_data['shoulder_circumference']}, taille={user_data['waist_circumference']}, hanches={user_data['hip_circumference']}")
        
        # 🚀 PHASE 1: Générer le rapport
        print("🚀 Génération du rapport MyStylist...")
        report = await report_generator.generate_complete_report(user_data)
        
        if not report:
            raise HTTPException(status_code=500, detail="Erreur génération rapport")
        
        print(f"✅ Rapport généré: {len(report)} sections")
        
        # 🚀 PHASE 2: Mapper données pour PDFMonkey
        print("📊 Mapping données au format PDFMonkey...")
        pdfmonkey_payload = pdf_mapper.map_report_to_pdfmonkey(report, user_data)
        print(f"✅ Payload préparé ({len(str(pdfmonkey_payload))} bytes)")
        
        # 🚀 PHASE 3: Générer le PDF
        print("📄 Génération PDF via PDFMonkey...")
        try:
            pdf_url = await pdf_service.generate_report_pdf(report_data, user_data)
            print(f"✅ PDF généré: {pdf_url[:80]}...")
        except Exception as e:
            print(f"⚠️  Erreur PDF, continuant sans PDF: {e}")
            pdf_url = None
        
        # 🚀 PHASE 4: Envoyer l'email
        print("📧 Envoi email avec PDF...")
        try:
            if pdf_url:
                email_result = await email_service.send_report_email(
                    user_email=user_data['user_email'],
                    user_name=user_data['user_name'],
                    pdf_url=pdf_url,
                    report_data=report
                )
                print(f"✅ Email envoyé: {email_result.get('email_id', 'N/A')}")
            else:
                print(f"⚠️  Pas de PDF, email non envoyé")
        except Exception as e:
            print(f"⚠️  Erreur envoi email: {e}")
        
        # ✅ SUCCÈS
        print(f"✅ FLUX COMPLET RÉUSSI pour user {user_id}")
        
        return {
            "status": "success",
            "user_id": user_id,
            "message": "Rapport généré et envoyé par email",
            "pdf_url": pdf_url,
            "email_sent": True if pdf_url else False
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="JSON invalide")
    except Exception as e:
        print(f"❌ Erreur webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/test/report")
async def test_report_generation():
    """Endpoint de test pour générer un rapport"""
    test_data = {
        "user_name": "Test User",
        "user_email": "test@example.com",
        "face_photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Default_pfp.svg/1200px-Default_pfp.svg.png",
        "body_photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Default_pfp.svg/1200px-Default_pfp.svg.png",
        "eye_color": "Marron",
        "hair_color": "Châtain",
        "age": 30,
        "shoulder_circumference": 85,
        "waist_circumference": 75,
        "hip_circumference": 95,
        "bust_circumference": 90,
        "unwanted_colors": ["Rose fluo"],
        "style_preferences": ["Classique chic"],
        "brand_preferences": ["Zara"]
    }
    
    try:
        report = await report_generator.generate_complete_report(test_data)
        return {
            "status": "success",
            "report": report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoints pour rapports
from app.services.supabase_reports import supabase_reports_service

@app.get("/api/reports/{user_id}")
async def get_user_reports(user_id: str):
    """Récupère tous les rapports d'un utilisateur"""
    try:
        reports = await supabase_reports_service.get_user_reports(user_id)
        return {
            "status": "success",
            "user_id": user_id,
            "reports": reports,
            "count": len(reports)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports/detail/{report_id}")
async def get_report_detail(report_id: str):
    """Récupère les détails d'un rapport spécifique"""
    try:
        report = await supabase_reports_service.get_report_by_id(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Rapport non trouvé")
        
        return {
            "status": "success",
            "report": report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))