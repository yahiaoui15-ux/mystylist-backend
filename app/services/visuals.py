from app.utils.supabase_client import supabase
import re
from difflib import SequenceMatcher


class VisualsService:
    def __init__(self):
        self.supabase = supabase
        self._cache = {}
        self._all_visuels = None
    
    @staticmethod
    def _normalize_cut_name(cut_name: str) -> str:
        """Normalise nom de coupe en clé de recherche"""
        if not cut_name:
            return ""
        
        normalized = cut_name.lower().strip()
        
        # Supprimer les conjonctions et mots vides
        remove_words = ['ou', 'et', 'de', 'des', 'la', 'le', 'très', 'tres', 'trop']
        for word in remove_words:
            normalized = re.sub(r'\b' + word + r'\b', '', normalized)
        
        # Espaces → underscores
        normalized = re.sub(r'\s+', '_', normalized)
        
        # Accents (UTF-8 correct)
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
        
        # Caractères spéciaux
        normalized = re.sub(r'[^a-z0-9_]', '', normalized)
        
        # Supprimer underscores multiples
        normalized = re.sub(r'_+', '_', normalized).strip('_')
        
        return normalized
    
    @staticmethod
    def _similarity_ratio(a: str, b: str) -> float:
        """Calcule similarité entre 2 strings"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    def _preload_all_visuels(self) -> dict:
        """Précharge TOUS les visuels au startup"""
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
        Récupère visuel pour coupe avec FUZZY MATCHING RELAXE (score ≥ 0.45).
        
        Stratégie:
        1. Match EXACT (nom_simplifie exact)
        2. Match FUZZY (score ≥ 0.45)
        3. Match par MOTS-CLÉS (cherche mots importants dans nom_simplifie)
        4. Retour vide gracieux
        """
        try:
            cut_key = self._normalize_cut_name(cut_name)
            if not cut_key:
                return {}
            
            # Cache
            cache_key = f"{category}:{cut_key}"
            if cache_key in self._cache:
                return self._cache[cache_key]
            
            # Map category
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
            
            # Précharger
            if self._all_visuels is None:
                self._all_visuels = self._preload_all_visuels()
            
            if not self._all_visuels or type_vetement not in self._all_visuels:
                return {}
            
            visuels_category = self._all_visuels.get(type_vetement, [])
            
            # 1️⃣ MATCH EXACT
            for visual in visuels_category:
                if visual["nom_simplifie_normalized"] == cut_key:
                    cached_visual = {
                        "url_image": visual.get("url_image", ""),
                        "nom_simplifie": visual.get("nom_simplifie", "")
                    }
                    self._cache[cache_key] = cached_visual
                    print(f"✅ EXACT: {category}/{cut_key}")
                    return cached_visual
            
            # 2️⃣ FUZZY MATCH (score ≥ 0.45)
            best_match = None
            best_score = 0.45  # RELAXE: 0.6 → 0.45 pour trouver plus!
            
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
                print(f"🔍 FUZZY ({best_score:.2f}): {category}/{cut_key} → {best_match['nom_simplifie']}")
                return cached_visual
            
            # 3️⃣ MATCH PAR MOTS-CLÉS (alternative if fuzzy failed)
            # Chercher si des mots importants de cut_name matchent
            keywords = [word for word in cut_key.split('_') if len(word) > 2]  # Mots > 2 chars
            
            if keywords:
                for visual in visuels_category:
                    visual_words = visual["nom_simplifie_normalized"].split('_')
                    # Si au moins 1 mot-clé match
                    if any(kw in visual_words for kw in keywords):
                        cached_visual = {
                            "url_image": visual.get("url_image", ""),
                            "nom_simplifie": visual.get("nom_simplifie", "")
                        }
                        self._cache[cache_key] = cached_visual
                        print(f"🔑 KEYWORD: {category}/{cut_key} → {visual['nom_simplifie']}")
                        return cached_visual
            
            # 4️⃣ Retour vide gracieux
            print(f"⚠️  Aucun visuel: {category}/{cut_name}")
            return {}
                
        except Exception as e:
            print(f"⚠️  [ERROR] {type(e).__name__}: {str(e)[:50]}")
            return {}
    
    def fetch_visuals_for_category(self, category: str, recommendations: list) -> list:
        """Enrichit recommandations avec visuels"""
        try:
            enriched = []
            
            for rec in recommendations:
                try:
                    # ✅ FIX: Chercher "cut_display" EN PREMIER (OpenAI Part 2)
                    cut_name = rec.get("cut_display") or rec.get("name") or rec.get("coupe", "")
                    
                    if not cut_name:
                        enriched.append({**rec, "visual_url": "", "visual_key": ""})
                        continue
                    
                    visual = self.fetch_visual_for_cut(category, cut_name)
                    
                    enriched_rec = {
                        **rec,
                        "visual_url": visual.get("url_image", ""),
                        "visual_key": visual.get("nom_simplifie", "")
                    }
                    enriched.append(enriched_rec)
                except Exception as e:
                    print(f"⚠️  [REC] {str(e)[:50]}")
                    enriched.append({**rec, "visual_url": "", "visual_key": ""})
            
            return enriched
            
        except Exception as e:
            print(f"⚠️  [CAT] {str(e)[:50]}")
            return [{**rec, "visual_url": "", "visual_key": ""} for rec in (recommendations or [])]
    
    def fetch_for_recommendations(self, morphology_result: dict) -> dict:
        """Récupère visuels pour morphologie"""
        try:
            print("🎨 Récupération visuels (FUZZY MATCHING RELAXE 0.45)...")
            
            if not morphology_result:
                return {}
            
            morpho = morphology_result.get("morpho", {})
            if not morpho:
                return {}
            
            categories = morpho.get("categories", {})
            if not categories:
                return {}
            
            enriched_visuals = {}
            total_enriched = 0
            
            for category, category_data in categories.items():
                try:
                    if not isinstance(category_data, dict):
                        continue
                    
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
                        found = sum(1 for e in enriched if e.get("visual_url"))
                        total_enriched += found
                        print(f"   ✅ {category}: {found}/{len(enriched)} visuels")
                    else:
                        enriched_visuals[category] = []
                        
                except Exception as e:
                    print(f"   ⚠️  {category}: {str(e)[:50]}")
                    enriched_visuals[category] = []
            
            print(f"✅ Total: {total_enriched} visuels trouvés")
            return enriched_visuals
            
        except Exception as e:
            print(f"❌ [FATAL] {type(e).__name__}: {str(e)[:100]}")
            return {}


# Instance globale
visuals_service = VisualsService()