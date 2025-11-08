import os
from dotenv import load_dotenv

load_dotenv()

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# PDFMonkey
PDFMONKEY_API_KEY = os.getenv("PDFMONKEY_API_KEY")

# Stripe
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")

# App
DEBUG = os.getenv("DEBUG", "False") == "True"