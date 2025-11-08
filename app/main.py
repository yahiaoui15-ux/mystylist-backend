from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
from app.services.report_generator import report_generator
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
    Webhook Stripe - Déclenche la génération du rapport
    
    Reçoit un paiement de client et génère:
    1. Analyses IA (colorimétrie, morphologie, styling)
    2. Récupération visuels et produits
    3. Génération PDF
    4. Envoi email
    """
    try:
        # Récupérer le payload
        payload = await request.json()
        print(f"📨 Webhook Stripe reçu: {payload.get('type', 'unknown')}")
        
        # Vérifier que c'est un événement de paiement réussi
        event_type = payload.get("type")
        if event_type != "charge.succeeded":
            print(f"⏭️  Event ignoré: {event_type}")
            return {"received": True}
        
        # Récupérer les données de paiement
        charge = payload.get("data", {}).get("object", {})
        user_id = charge.get("metadata", {}).get("user_id")
        user_email = charge.get("billing_details", {}).get("email")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id manquant")
        
        print(f"✅ Paiement confirmé pour user: {user_id}")
        
        # TEMPORAIRE: Récupérer les données utilisateur depuis le webhook
        # (En prod, tu les récupéreras de Supabase avec user_id)
        user_data = {
            "user_id": user_id,
            "user_email": user_email or "noreply@mystylist.io",
            "user_name": charge.get("metadata", {}).get("user_name", "Client"),
            "face_photo_url": charge.get("metadata", {}).get("face_photo_url", ""),
            "body_photo_url": charge.get("metadata", {}).get("body_photo_url", ""),
            "eye_color": charge.get("metadata", {}).get("eye_color", ""),
            "hair_color": charge.get("metadata", {}).get("hair_color", ""),
            "age": int(charge.get("metadata", {}).get("age", 0)),
            "shoulder_circumference": float(charge.get("metadata", {}).get("shoulder_circumference", 0)),
            "waist_circumference": float(charge.get("metadata", {}).get("waist_circumference", 0)),
            "hip_circumference": float(charge.get("metadata", {}).get("hip_circumference", 0)),
            "bust_circumference": float(charge.get("metadata", {}).get("bust_circumference", 0)),
            "unwanted_colors": json.loads(charge.get("metadata", {}).get("unwanted_colors", "[]")),
            "style_preferences": charge.get("metadata", {}).get("style_preferences", ""),
            "brand_preferences": json.loads(charge.get("metadata", {}).get("brand_preferences", "[]"))
        }
        
        # Générer le rapport complet
        print("🚀 Génération du rapport MyStylist...")
        report = await report_generator.generate_complete_report(user_data)
        
        if not report:
            raise HTTPException(status_code=500, detail="Erreur génération rapport")
        
        print(f"✅ Rapport généré: {len(report)} sections")
        
        # TODO: Jour 7
        # - Générer PDF avec PDFMonkey
        # - Upload à Supabase Storage
        # - Envoyer email au client
        
        return {
            "status": "success",
            "user_id": user_id,
            "message": "Rapport en génération..."
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
        "style_preferences": "Classique chic",
        "brand_preferences": ["Zara"]
    }
    
    try:
        report = await report_generator.generate_complete_report(test_data)
        return {
            "status": "success",
            "report": report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))# Endpoints pour rapports
from app.services.supabase_reports import supabase_reports_service
from app.services.email import email_service

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

@app.post("/api/test/send-email")
async def test_send_email(user_email: str, user_name: str):
    """Endpoint test pour envoyer un email (DEV ONLY)"""
    try:
        test_report = {
            "colorimetry": {"season": "Automne"},
            "morphology": {"silhouette_type": "O"}
        }
        
        result = await email_service.send_report_email(
            user_email=user_email,
            user_name=user_name,
            pdf_url="https://example.com/report.pdf",
            report_data=test_report
        )
        
        return {
            "status": "success",
            "message": "Email envoyé",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))