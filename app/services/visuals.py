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
        
        Args:
            category: "hauts", "bas", "robes", "vestes", "chaussures", "accessoires"
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
            
            # Map category vers type_vetement
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
            
            try:
                client = self.supabase._get_client()
                if client is None:
                    return {}
                
                # Gestion robuste des erreurs Supabase 500
                try:
                    result = client.table("visuels").select("*").eq(
                        "type_vetement", type_vetement
                    ).ilike(
                        "nom_simplifie", f"%{cut_key}%"
                    ).execute()
                except Exception as supabase_query_error:
                    print(f"⚠️  [SUPABASE_QUERY] {category}/{cut_name}: Erreur requête")
                    return {}
                
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
                
            except Exception as supabase_error:
                print(f"⚠️  [SUPABASE_ERROR] {category}/{cut_name}: {type(supabase_error).__name__}")
                return {}
            
        except Exception as general_error:
            print(f"⚠️  [GENERAL_ERROR] fetch_visual_for_cut: {type(general_error).__name__}")
            return {}
    
    def fetch_visuals_for_category(self, category: str, recommendations: list) -> list:
        """
        Enrichit une liste de recommandations avec les visuels
        
        Args:
            category: "hauts", "bas", etc.
            recommendations: [{"name": "Encolure en V", "why": "..."}, ...]
        
        Returns:
            [{"name": "Encolure en V", "why": "...", "visual_url": ""}, ...]
        """
        try:
            enriched = []
            
            for rec in recommendations:
                try:
                    # ✅ Utiliser "name" au lieu de "cut_display"
                    cut_name = rec.get("name", "")
                    visual = self.fetch_visual_for_cut(category, cut_name)
                    
                    enriched_rec = {
                        **rec,
                        "visual_url": visual.get("url_image", ""),
                        "visual_key": visual.get("nom_simplifie", "")
                    }
                    enriched.append(enriched_rec)
                except Exception as e:
                    print(f"⚠️  [REC_ERROR] {category}: {str(e)[:100]}")
                    enriched.append({
                        **rec,
                        "visual_url": "",
                        "visual_key": ""
                    })
            
            return enriched
            
        except Exception as e:
            print(f"⚠️  [CATEGORY_ERROR] {category}: {str(e)[:100]}")
            return [
                {
                    **rec,
                    "visual_url": "",
                    "visual_key": ""
                }
                for rec in (recommendations or [])
            ]
    
    def fetch_all_visuals_by_category(self) -> dict:
        """Récupère TOUS les visuels organisés par catégorie"""
        try:
            try:
                client = self.supabase._get_client()
                if client is None:
                    return {}
                
                result = client.table("visuels").select("*").execute()
                
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
                print(f"⚠️  [SUPABASE] fetch_all_visuals: {str(e)[:100]}")
                return {}
            
        except Exception as e:
            print(f"⚠️  [GENERAL] fetch_all_visuals: {str(e)[:100]}")
            return {}
    
    def fetch_for_recommendations(self, morphology_result: dict) -> dict:
        """
        Récupère visuels pour les recommandations morphologiques.
        
        ✅ FIX FINAL: Cherche dans morphology.morpho.categories
        Structure réelle du payload:
        {
          "morpho": {
            "categories": {
              "hauts": {
                "recommandes": [{name, why, visual_url, visual_key}, ...],
                "a_eviter": [{name, why, visual_url, visual_key}, ...]
              }
            }
          }
        }
        
        Args:
            morphology_result: Dict avec morpho.categories
        
        Returns:
            Dict organisé avec visuels enrichis
        """
        try:
            print("🎨 Récupération visuels pour recommendations...")
            
            if not morphology_result:
                print("   ⚠️  morphology_result vide")
                return {}
            
            # ✅ FIX: Chercher dans morpho.categories (vraie structure!)
            morpho = morphology_result.get("morpho", {})
            if not morpho:
                print("   ⚠️  Pas de 'morpho' trouvé")
                return {}
            
            categories = morpho.get("categories", {})
            if not categories:
                print("   ⚠️  Pas de 'categories' trouvées")
                return {}
            
            enriched_visuals = {}
            total_enriched = 0
            
            # Pour chaque catégorie (hauts, bas, robes, etc.)
            for category, category_data in categories.items():
                try:
                    if not isinstance(category_data, dict):
                        print(f"   ⚠️  {category}: structure invalide")
                        continue
                    
                    # ✅ Fusionner "recommandes" + "a_eviter"
                    all_recs = []
                    
                    # Ajouter les recommandations
                    recommandes = category_data.get("recommandes", [])
                    if isinstance(recommandes, list):
                        all_recs.extend(recommandes)
                    
                    # Ajouter les recommandations à éviter
                    a_eviter = category_data.get("a_eviter", [])
                    if isinstance(a_eviter, list):
                        all_recs.extend(a_eviter)
                    
                    if len(all_recs) > 0:
                        # Enrichir avec visuels
                        enriched = self.fetch_visuals_for_category(category, all_recs)
                        enriched_visuals[category] = enriched
                        count = len(enriched)
                        total_enriched += count
                        print(f"   ✅ {category}: {count} recommendations enrichies ({len(recommandes)} + {len(a_eviter)})")
                    else:
                        print(f"   ⚠️  {category}: aucune recommendation")
                        enriched_visuals[category] = []
                        
                except Exception as e:
                    print(f"   ⚠️  Erreur {category}: {str(e)[:100]}")
                    enriched_visuals[category] = []
            
            print(f"✅ Visuels récupérés: {total_enriched} enrichies")
            return enriched_visuals
            
        except Exception as e:
            print(f"❌ [FATAL] fetch_for_recommendations: {type(e).__name__}: {str(e)[:200]}")
            import traceback
            traceback.print_exc()
            return {}


# Instance globale
visuals_service = VisualsService()