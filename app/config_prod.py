import os
from functools import lru_cache

class Settings:
    """Production settings"""
    # App
    APP_NAME = "MyStylist Backend"
    DEBUG = False
    API_V1_STR = "/api"
    
    # Database
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # External Services
    PDFMONKEY_API_KEY = os.getenv("PDFMONKEY_API_KEY")
    PDFMONKEY_TEMPLATE_ID = os.getenv("PDFMONKEY_TEMPLATE_ID")
    
    # Stripe
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    # Email
    RESEND_API_KEY = os.getenv("RESEND_API_KEY")
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    
    # CORS
    ALLOWED_ORIGINS = [
        "https://my-stylist.io",
        "https://www.my-stylist.io",
        "https://app.my-stylist.io"
    ]
    
    class Config:
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()