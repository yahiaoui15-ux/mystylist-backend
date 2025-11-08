from pydantic import BaseModel
from typing import List, Dict, Optional

class UserProfileInput(BaseModel):
    """Données utilisateur reçues du webhook Stripe"""
    user_id: str
    user_email: str
    user_name: str
    first_name: str
    face_photo_url: str
    body_photo_url: str
    eye_color: str
    hair_color: str
    age: int
    shoulder_circumference: float
    waist_circumference: float
    hip_circumference: float
    bust_circumference: float
    style_preferences: Optional[Dict] = None
    unwanted_colors: Optional[List[str]] = None

class ColorimetryResult(BaseModel):
    """Résultat analyse colorimétrie"""
    season: str
    season_explanation: str
    palette_personnalisee: List[Dict]
    all_colors_evaluation: Dict
    associations_gagnantes: List[Dict]
    guide_maquillage: Dict

class MorphologyResult(BaseModel):
    """Résultat analyse morphologie"""
    silhouette_type: str
    silhouette_explanation: str
    body_analysis: Dict
    styling_objectives: List[str]
    recommendations: Dict

class StylingResult(BaseModel):
    """Résultat profil stylistique"""
    archetypes: List[str]
    capsule_wardrobe: List[Dict]
    mix_and_match_formulas: List[Dict]
    shopping_guide: Dict
    occasions: List[Dict]

class ReportData(BaseModel):
    """Données complètes pour génération PDF"""
    user_name: str
    user_email: str
    colorimetry: ColorimetryResult
    morphology: MorphologyResult
    styling: StylingResult
    visuals: Dict
    products: Dict