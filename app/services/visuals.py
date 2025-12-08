from app.utils.supabase_client import supabase
import re
from difflib import SequenceMatcher


class VisualsService:
    def __init__(self):
        self.supabase = supabase
        self._cache = {}
        self._all_visuels = None  # Cache tous les visuels au startup
    
    @staticmethod
    def _normalize_cut_name(cut_name: str) -> str:
        """
        Transforme un nom de coupe en clé de recherche
        "Encolure en V" → "encolure_en_v"
        "Manches raglan ou kimono" → "manches_raglan"
        """
        if not cut_name:
            return ""
        
        normalized = cut_name.lower().strip()
        normalized = re.sub(r'\s+', '_', normalized)
        
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
        
        normalized = re.sub(r'[^a-z0-9_]', '', normalized)
        
        return normalized
    
    @staticmethod
    def _similarity_ratio(a: str, b: str) -> float:
        """Calcule la similarité entre 2 strings (0.0 à 1.0)"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    def _preload_all_visuels(self) -> dict:
        """Précharge TOUS les visuels au startup pour éviter requêtes répétées"""
        try:
            client = self.supabase._get_client()
            if client is None:
                return {}
            
            try:
                result = client.table("visuels").select("*").execute()
                if result and result.data:
                    organized = {}
                    for visual in result.data:
                        category = visual.get("type_vetement", "autre")
                        if category not in organized:
                            organized[category] = []
                        organized[category].append({
                            "coupe": visual.get("coupe", ""),
                            "nom_simplifie": visual.get("nom_simplifie", ""),
                            "url_image": visual.get("url_image", ""),
                            "nom_simplifie_normalized": self._normalize_cut_name(visual.get("nom_simplifie", ""))
                        })
                    print(f"✅ Visuels préchargés: {sum(len(v) for v in organized.values())} images")
                    return organized
            except Exception as e:
                print(f"⚠️  [PRELOAD] Erreur: {str(e)[:100]}")
                return {}
        
        except Exception as e:
            print(f"⚠️  [PRELOAD_GENERAL] {str(e)[:100]}")
            return {}
    
    def fetch_visual_for_cut(self, category: str, cut_name: str) -> dict:
        """
        Récupère UN visuel pour une coupe spécifique avec FUZZY MATCHING.
        
        Si le match exact échoue, cherche le match le plus proche!
        
        Args:
            category: "hauts", "bas", "robes", "vestes", etc.
            cut_name: "Encolure en V", "Manches raglan ou kimono", etc.
        
        Returns:
            dict avec {"url_image": "...", "nom_simplifie": "..."} ou vide {}
        """
        try:
            cut_key = self._normalize_cut_name(cut_name)
            if not cut_key:
                return {}
            
            # Vérifier le cache d'abord
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
                "accessoires": "accessoire",
                "Maillot de bain": "Maillot de bain",
                "manteau": "manteau"
            }
            
            type_vetement = type_vetement_map.get(category, category)
            
            # Précharger les visuels si pas fait
            if self._all_visuels is None:
                self._all_visuels = self._preload_all_visuels()
            
            # Chercher dans les visuels préchargés
            if not self._all_visuels or type_vetement not in self._all_visuels:
                return {}
            
            visuels_category = self._all_visuels.get(type_vetement, [])
            
            # 1️⃣ Chercher MATCH EXACT d'abord
            for visual in visuels_category:
                if visual["nom_simplifie_normalized"] == cut_key:
                    cached_visual = {
                        "url_image": visual.get("url_image", ""),
                        "nom_simplifie": visual.get("nom_simplifie", "")
                    }
                    self._cache[cache_key] = cached_visual
                    print(f"✅ Visuel EXACT: {category}/{cut_key}")
                    return cached_visual
            
            # 2️⃣ Si pas de match exact, chercher FUZZY MATCH (similarité > 0.6)
            best_match = None
            best_score = 0.6  # Seuil minimum de similarité
            
            for visual in visuels_category:
                score = self._similarity_ratio(cut_key, visual["nom_simplifie_normalized"])
                if score > best_score:
                    best_score = score
                    best_match = visual
            
            if best_match:
                cached_visual = {
                    "url_image": best_match.get("url_image", ""),
                    "nom_simplifie": best_match.get("nom_simplifie", "")
                }
                self._cache[cache_key] = cached_visual
                print(f"📊 Visuel FUZZY (score {best_score:.2f}): {category}/{cut_key} → {best_match['nom_simplifie']}")
                return cached_visual
            
            # 3️⃣ Si rien ne match, retourner vide (gracieusement)
            print(f"⚠️  Aucun visuel trouvé: {category}/{cut_key}")
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
    
    def fetch_for_recommendations(self, morphology_result: dict) -> dict:
        """
        Récupère visuels pour les recommandations morphologiques.
        
        ✅ Cherche dans morphology.morpho.categories
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
            print("🎨 Récupération visuels pour recommendations (FUZZY MATCHING)...")
            
            if not morphology_result:
                print("   ⚠️  morphology_result vide")
                return {}
            
            # Chercher dans morpho.categories
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
                    
                    # Fusionner "recommandes" + "a_eviter"
                    all_recs = []
                    
                    recommandes = category_data.get("recommandes", [])
                    if isinstance(recommandes, list):
                        all_recs.extend(recommandes)
                    
                    a_eviter = category_data.get("a_eviter", [])
                    if isinstance(a_eviter, list):
                        all_recs.extend(a_eviter)
                    
                    if len(all_recs) > 0:
                        enriched = self.fetch_visuals_for_category(category, all_recs)
                        enriched_visuals[category] = enriched
                        count = len(enriched)
                        total_enriched += count
                        
                        # Compter les visuels trouvés vs demandés
                        found = sum(1 for e in enriched if e.get("visual_url"))
                        print(f"   ✅ {category}: {found}/{count} visuels trouvés ({len(recommandes)} + {len(a_eviter)})")
                    else:
                        print(f"   ⚠️  {category}: aucune recommendation")
                        enriched_visuals[category] = []
                        
                except Exception as e:
                    print(f"   ⚠️  Erreur {category}: {str(e)[:100]}")
                    enriched_visuals[category] = []
            
            print(f"✅ Visuels récupérés: {total_enriched} recommendations enrichies")
            return enriched_visuals
            
        except Exception as e:
            print(f"❌ [FATAL] fetch_for_recommendations: {type(e).__name__}: {str(e)[:200]}")
            import traceback
            traceback.print_exc()
            return {}


# Instance globale
visuals_service = VisualsService()