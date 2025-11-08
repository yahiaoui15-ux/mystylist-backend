from pydantic import BaseModel
from typing import Optional

class ColorimetryOutput(BaseModel):
    """Output colorimétrie pour PDF"""
    season: str
    palette: list
    guide_maquillage: dict

class MorphologyOutput(BaseModel):
    """Output morphologie pour PDF"""
    silhouette_type: str
    recommendations_with_visuals: dict

class StylingOutput(BaseModel):
    """Output profil stylistique pour PDF"""
    capsule: list
    formulas: list
    guide: dict

class PDFPayload(BaseModel):
    """Payload envoyé à PDFMonkey"""
    user_name: str
    user_email: str
    colorimetry: ColorimetryOutput
    morphology: MorphologyOutput
    styling: StylingOutput
    visuals: dict
    products: dict

class APIResponse(BaseModel):
    """Réponse API générique"""
    status: str
    message: Optional[str] = None
    data: Optional[dict] = None

class WebhookResponse(BaseModel):
    """Réponse webhook Stripe"""
    status: str
    pdf_url: Optional[str] = None
    user_id: str