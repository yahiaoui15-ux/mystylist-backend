"""
Services module for MyStylist backend
"""

from app.services.email_service import email_service
from app.services.pdf_generation import pdf_service as pdf_generation
from app.services.report_generator import report_generator
from app.services.supabase_reports import supabase_reports_service as supabase_reports
from app.services.products import products_service
from app.services.visuals import visuals_service
from app.services.colorimetry import colorimetry_service
from app.services.morphology import morphology_service
from app.services.styling import styling_service

__all__ = [
    "email_service",
    "pdf_generation",
    "report_generator",
    "supabase_reports",
    "products_service",
    "visuals_service",
    "colorimetry_service",
    "morphology_service",
    "styling_service",
]