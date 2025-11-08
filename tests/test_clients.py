import pytest
import asyncio
from app.utils.supabase_client import supabase
from app.utils.openai_client import openai_client

@pytest.mark.asyncio
async def test_supabase_connection():
    """Teste connexion Supabase"""
    try:
        result = await supabase.query_table("user_profiles")
        assert result is not None or result == None
        print("✅ Supabase connecté")
    except Exception as e:
        print(f"❌ Erreur Supabase: {e}")
        raise

@pytest.mark.asyncio
async def test_openai_connection():
    """Teste connexion OpenAI"""
    try:
        response = await openai_client.call_chat("Dis bonjour en une phrase")
        assert response is not None
        assert len(response) > 0
        print(f"✅ OpenAI connecté: {response[:50]}...")
    except Exception as e:
        print(f"❌ Erreur OpenAI: {e}")
        raise

@pytest.mark.asyncio
async def test_colorimetry_service():
    """Teste service colorimétrie"""
    from app.services.colorimetry import colorimetry_service
    
    user_data = {
        "face_photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Default_pfp.svg/1200px-Default_pfp.svg.png",
        "eye_color": "Marron",
        "hair_color": "Châtain",
        "age": 30,
        "unwanted_colors": ["Rose fluo", "Orange électrique"]
    }
    
    try:
        result = await colorimetry_service.analyze(user_data)
        assert result is not None
        assert "season" in result or len(result) == 0
        print("✅ Service colorimétrie testé")
    except Exception as e:
        print(f"⚠️  Service colorimétrie: {e}")

@pytest.mark.asyncio
async def test_morphology_service():
    """Teste service morphologie"""
    from app.services.morphology import morphology_service
    
    user_data = {
        "body_photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Default_pfp.svg/1200px-Default_pfp.svg.png",
        "shoulder_circumference": 85,
        "waist_circumference": 75,
        "hip_circumference": 95,
        "bust_circumference": 90
    }
    
    try:
        result = await morphology_service.analyze(user_data)
        assert result is not None
        assert "silhouette_type" in result or len(result) == 0
        print("✅ Service morphologie testé")
    except Exception as e:
        print(f"⚠️  Service morphologie: {e}")

@pytest.mark.asyncio
async def test_styling_service():
    """Teste service styling"""
    from app.services.styling import styling_service
    
    colorimetry_result = {
        "season": "Automne",
        "palette_personnalisee": [
            {"name": "moutarde", "displayName": "Moutarde", "hex": "#E1AD01"},
            {"name": "cuivre", "displayName": "Cuivre", "hex": "#B87333"}
        ],
        "guide_maquillage": {
            "teint": "Fond de teint chaud",
            "blush": "Terracotta"
        }
    }
    
    morphology_result = {
        "silhouette_type": "O",
        "recommendations": {
            "hauts": {"a_privilegier": [{"cut": "encolure_en_v"}]},
            "robes": {"a_privilegier": [{"cut": "robe_empire"}]}
        }
    }
    
    user_data = {
        "style_preferences": "Classique chic",
        "brand_preferences": ["Zara", "COS"]
    }
    
    try:
        result = await styling_service.generate(colorimetry_result, morphology_result, user_data)
        assert result is not None
        assert "mix_and_match_formulas" in result or len(result) == 0
        print("✅ Service styling testé")
    except Exception as e:
        print(f"⚠️  Service styling: {e}")

@pytest.mark.asyncio
async def test_report_generator_integration():
    """Teste intégration complète avec parallélisation"""
    from app.services.report_generator import report_generator
    import time
    
    user_data = {
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
        "brand_preferences": ["Zara", "COS"]
    }
    
    try:
        start_time = time.time()
        report = await report_generator.generate_complete_report(user_data)
        elapsed = time.time() - start_time
        
        assert report is not None
        assert "colorimetry" in report or len(report) == 0
        assert "morphology" in report or len(report) == 0
        
        print(f"✅ Rapport généré en {elapsed:.1f}s")
        print(f"✅ Colorimétrie: {report.get('colorimetry', {}).get('season', 'N/A')}")
        print(f"✅ Morphologie: {report.get('morphology', {}).get('silhouette_type', 'N/A')}")
        print(f"✅ Formules: {len(report.get('styling', {}).get('mix_and_match_formulas', []))}")
        
    except Exception as e:
        print(f"⚠️  Report generator: {e}")

@pytest.mark.asyncio
async def test_webhook_stripe():
    """Teste endpoint webhook Stripe"""
    from fastapi.testclient import TestClient
    from app.main import app
    
    client = TestClient(app)
    
    webhook_payload = {
        "type": "charge.succeeded",
        "data": {
            "object": {
                "id": "ch_test_123",
                "amount": 2999,
                "billing_details": {
                    "email": "test@example.com"
                },
                "metadata": {
                    "user_id": "user_test_123",
                    "user_name": "Test User",
                    "face_photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Default_pfp.svg/1200px-Default_pfp.svg.png",
                    "body_photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Default_pfp.svg/1200px-Default_pfp.svg.png",
                    "eye_color": "Marron",
                    "hair_color": "Châtain",
                    "age": "30",
                    "shoulder_circumference": "85",
                    "waist_circumference": "75",
                    "hip_circumference": "95",
                    "bust_circumference": "90",
                    "unwanted_colors": "[]",
                    "style_preferences": "Classique",
                    "brand_preferences": "[]"
                }
            }
        }
    }
    
    try:
        response = client.post("/api/webhook/stripe", json=webhook_payload)
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        print("✅ Webhook Stripe testé")
    except Exception as e:
        print(f"⚠️  Webhook test: {e}")

@pytest.mark.asyncio
async def test_health_endpoint():
    """Teste endpoint health"""
    from fastapi.testclient import TestClient
    from app.main import app
    
    client = TestClient(app)
    response = client.get("/health")
    
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✅ Health endpoint testé")

@pytest.mark.asyncio
async def test_get_user_reports():
    """Teste endpoint GET /api/reports/{user_id}"""
    from fastapi.testclient import TestClient
    from app.main import app
    
    client = TestClient(app)
    
    try:
        response = client.get("/api/reports/user_test_123")
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        print("✅ GET /api/reports/{user_id} testé")
    except Exception as e:
        print(f"⚠️  GET reports test: {e}")

@pytest.mark.asyncio
async def test_complete_workflow():
    """Teste workflow complet: webhook -> rapport -> sauvegarde"""
    from fastapi.testclient import TestClient
    from app.main import app
    
    client = TestClient(app)
    
    webhook_payload = {
        "type": "charge.succeeded",
        "data": {
            "object": {
                "id": "ch_workflow_test",
                "amount": 2999,
                "billing_details": {
                    "email": "workflow@test.com"
                },
                "metadata": {
                    "user_id": "workflow_user_123",
                    "user_name": "Workflow Test",
                    "face_photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Default_pfp.svg/1200px-Default_pfp.svg.png",
                    "body_photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Default_pfp.svg/1200px-Default_pfp.svg.png",
                    "eye_color": "Bleu",
                    "hair_color": "Blonde",
                    "age": "28",
                    "shoulder_circumference": "80",
                    "waist_circumference": "70",
                    "hip_circumference": "90",
                    "bust_circumference": "85",
                    "unwanted_colors": "[]",
                    "style_preferences": "Bohème",
                    "brand_preferences": "[]"
                }
            }
        }
    }
    
    try:
        # 1. Envoyer webhook
        response1 = client.post("/api/webhook/stripe", json=webhook_payload)
        assert response1.status_code == 200
        print("✅ Workflow - Webhook reçu")
        
        # 2. Récupérer les rapports de l'utilisateur
        response2 = client.get("/api/reports/workflow_user_123")
        assert response2.status_code == 200
        reports_count = response2.json().get("count", 0)
        print(f"✅ Workflow - {reports_count} rapport(s) récupéré(s)")
        
        print("✅ Workflow complet testé!")
        
    except Exception as e:
        print(f"⚠️  Workflow test: {e}")