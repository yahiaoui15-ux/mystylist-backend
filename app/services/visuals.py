from app.utils.supabase_client import supabase
import re


class VisualsService:
    def __init__(self):
        self.supabase = supabase
        # Cache les visuels pour éviter requêtes répétées
        self._cache = {}
    
    @staticmethod
    def _normalize_cut_name(cut_name: str) -> str:
        """
        Transforme un nom de coupe en clé de recherche
        "Encolure en V" → "encolure_en_v"
        "Manches raglan ou kimono" → "manches_raglan"
        """
        if not cut_name:
            return ""
        
        # Lowercase + remplacer espaces par underscores
        normalized = cut_name.lower().strip()
        
        # Remplacer les espaces par underscores
        normalized = re.sub(r'\s+', '_', normalized)
        
        # Remplacer les accents
        accents = {
            'à': 'a', 'â': 'a', 'ä': 'a', 'á': 'a',
            'è': 'e', 'é': 'e', 'ê': 'e', 'ë': 'e',
            'ì': 'i', 'î': 'i', 'ï': 'i',
            'ò': 'o', 'ô': 'o', 'ö': 'o', 'ó': 'o',
            'ù': 'u', 'û': 'u', 'ü': 'u', 'ú': 'u',
            'ç': 'c', 'œ': 'oe'
        }
        for accent, replacement in accents.items():
            normalized = normalized.replace(accent, replacement)
        
        # Supprimer les caractères spéciaux sauf underscores
        normalized = re.sub(r'[^a-z0-9_]', '', normalized)
        
        return normalized
    
    def fetch_visual_for_cut(self, category: str, cut_name: str) -> dict:
        """
        Récupère UN visuel pour une coupe spécifique
        Synchrone (pas async)
        
        Args:
            category: "hauts", "bas", "robes", "vestes", "maillot_lingerie", "chaussures", "accessoires"
            cut_name: "Encolure en V", "Tailles hautes", etc.
        
        Returns:
            dict avec {"url_image": "...", "nom_simplifie": "..."} ou vide {}
        """
        try:
            # Normaliser le nom
            cut_key = self._normalize_cut_name(cut_name)
            if not cut_key:
                return {}
            
            # Vérifier le cache
            cache_key = f"{category}:{cut_key}"
            if cache_key in self._cache:
                return self._cache[cache_key]
            
            # Map category vers type_vetement (si besoin)
            type_vetement_map = {
                "hauts": "haut",
                "bas": "bas",
                "robes": "robe",
                "vestes": "veste",
                "maillot_lingerie": "lingerie",
                "chaussures": "chaussure",
                "accessoires": "accessoire"
            }
            
            type_vetement = type_vetement_map.get(category, category)
            
            # ✅ UTILISER LA VRAIE API SUPABASE
            result = self.supabase.table("visuels").select("*").eq(
                "type_vetement", type_vetement
            ).ilike(
                "nom_simplifie", f"%{cut_key}%"  # Utiliser ilike pour flexibility
            ).execute()
            
            if result and result.data and len(result.data) > 0:
                visual = result.data[0]
                cached_visual = {
                    "url_image": visual.get("url_image", ""),
                    "nom_simplifie": visual.get("nom_simplifie", ""),
                    "coupe": visual.get("coupe", "")
                }
                
                # Mettre en cache
                self._cache[cache_key] = cached_visual
                
                print(f"✅ Visuel trouvé: {category}/{cut_key} → {visual.get('nom_simplifie')}")
                return cached_visual
            
            return {}
            
        except Exception as e:
            print(f"⚠️  Erreur visuel {category}/{cut_name}: {e}")
            return {}
    
    def fetch_visuals_for_category(self, category: str, recommendations: list) -> list:
        """
        Enrichit une liste de recommandations avec les visuels
        
        Args:
            category: "hauts", "bas", etc.
            recommendations: [{"name": "Encolure en V", "why": "..."}, ...]
        
        Returns:
            [{"name": "Encolure en V", "why": "...", "visual_url": "..."}, ...]
        """
        enriched = []
        
        for rec in recommendations:
            cut_name = rec.get("name", "")
            visual = self.fetch_visual_for_cut(category, cut_name)
            
            enriched_rec = {
                **rec,
                "visual_url": visual.get("url_image", ""),
                "visual_key": visual.get("nom_simplifie", "")
            }
            enriched.append(enriched_rec)
        
        return enriched
    
    def fetch_all_visuals_by_category(self) -> dict:
        """Récupère TOUS les visuels organisés par catégorie"""
        try:
            result = self.supabase.table("visuels").select("*").execute()
            
            if not result or not result.data:
                return {}
            
            organized = {}
            for visual in result.data:
                category = visual.get("type_vetement", "autre")
                if category not in organized:
                    organized[category] = []
                organized[category].append(visual)
            
            print(f"✅ Tous les visuels chargés: {sum(len(v) for v in organized.values())} images")
            return organized
            
        except Exception as e:
            print(f"❌ Erreur fetch all visuals: {e}")
            return {}


# Instance globale
visuals_service = VisualsService()