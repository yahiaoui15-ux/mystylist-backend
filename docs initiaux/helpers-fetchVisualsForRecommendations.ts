/**
 * fetchVisualsForRecommendations.ts
 * 
 * Chercher les visuels pédagogiques correspondant aux recommandations
 * 
 * Flow:
 * 1. Pour chaque recommandation (ex: "encolure_v")
 * 2. Chercher en BD: visuels_pedagogiques WHERE category="haut" AND type="encolure_v"
 * 3. Filtrer par morpho type
 * 4. Retourner URLs + descriptions
 * 5. Fallback si rien trouvé: visuel générique de la catégorie
 */

import type { MorphoRecommendations } from "./parseOpenAIMorphology";

export interface VisualData {
  id?: string;
  image_url: string;
  thumbnail_url?: string;
  description: string;
  style_tags: string[];
  type: string;
  category: string;
}

export interface CategoryVisualsMap {
  hauts_visuels: VisualData[];
  robes_visuels: VisualData[];
  bas_visuels: VisualData[];
  vestes_visuels?: VisualData[];
  maillots_visuels?: VisualData[];
  lingerie_visuels?: VisualData[];
}

/**
 * Chercher les visuels pour une recommandation spécifique
 */
async function fetchVisualForType(
  supabase: any,
  category: string,
  type: string,
  morphoType: string,
  fallbackToGeneric: boolean = true
): Promise<VisualData | null> {
  try {
    // 1️⃣ Chercher le visuel EXACT: catégorie + type + morpho
    const { data, error } = await supabase
      .from("visuels_pedagogiques")
      .select("id, image_url, thumbnail_url, description, style_tags, type, category")
      .eq("category", category)
      .eq("type", type)
      .contains("morpho_types", [morphoType])
      .limit(1)
      .single();

    if (data) {
      return {
        ...data,
        style_tags: data.style_tags || []
      };
    }

    if (error && !fallbackToGeneric) {
      return null;
    }

    // 2️⃣ Fallback: Chercher le même type, n'importe quelle morpho
    if (fallbackToGeneric) {
      const { data: fallback1 } = await supabase
        .from("visuels_pedagogiques")
        .select("id, image_url, thumbnail_url, description, style_tags, type, category")
        .eq("category", category)
        .eq("type", type)
        .limit(1)
        .single();

      if (fallback1) {
        return {
          ...fallback1,
          style_tags: fallback1.style_tags || []
        };
      }

      // 3️⃣ Fallback ultime: Chercher n'importe quel visuel de cette catégorie
      const { data: fallback2 } = await supabase
        .from("visuels_pedagogiques")
        .select("id, image_url, thumbnail_url, description, style_tags, type, category")
        .eq("category", category)
        .order("created_at", { ascending: false })
        .limit(1)
        .single();

      if (fallback2) {
        return {
          ...fallback2,
          style_tags: fallback2.style_tags || []
        };
      }
    }

    return null;
  } catch (error) {
    console.warn(`Erreur recherche visuel ${category}/${type}:`, error);
    return null;
  }
}

/**
 * Chercher TOUS les visuels pour les recommandations
 * 
 * Retourne une map: { hauts_visuels: [...], robes_visuels: [...], ... }
 */
export async function fetchVisualsForRecommendations(
  supabase: any,
  recommendations: MorphoRecommendations
): Promise<CategoryVisualsMap> {
  
  const result: CategoryVisualsMap = {
    hauts_visuels: [],
    robes_visuels: [],
    bas_visuels: []
  };

  // Mapping catégories TypeScript → clés de résultat
  const categoryMapping = [
    { key: "hauts", dbCategory: "haut", resultKey: "hauts_visuels" },
    { key: "robes", dbCategory: "robe", resultKey: "robes_visuels" },
    { key: "bas", dbCategory: "bas", resultKey: "bas_visuels" },
    { key: "vestes", dbCategory: "veste", resultKey: "vestes_visuels" },
    { key: "maillots", dbCategory: "maillot", resultKey: "maillots_visuels" },
    { key: "lingerie", dbCategory: "lingerie", resultKey: "lingerie_visuels" }
  ] as const;

  // Pour chaque catégorie
  for (const { key, dbCategory, resultKey } of categoryMapping) {
    const categoryRecommendations = recommendations[key as keyof MorphoRecommendations];
    
    if (!categoryRecommendations || !("recommended" in categoryRecommendations)) {
      continue;
    }

    const visuels: VisualData[] = [];

    // Pour chaque recommandation dans cette catégorie
    for (const rec of categoryRecommendations.recommended) {
      console.log(`🔍 Cherchant visuel: ${dbCategory}/${rec.type}`);

      const visual = await fetchVisualForType(
        supabase,
        dbCategory,
        rec.type,
        recommendations.morpho_type,
        true // Fallback activé
      );

      if (visual) {
        // Dédupliquer (éviter 2x le même visuel)
        const isDuplicate = visuels.some(v => v.id === visual.id);
        if (!isDuplicate) {
          visuels.push(visual);
          console.log(`✅ Trouvé: ${visual.description}`);
        }
      } else {
        console.warn(`⚠️ Pas de visuel trouvé pour ${dbCategory}/${rec.type}`);
      }
    }

    // Limiter à 5 visuels par catégorie (pour éviter PDF trop lourd)
    result[resultKey as keyof CategoryVisualsMap] = visuels.slice(0, 5);
  }

  return result;
}

/**
 * Chercher les visuels en PARALLÈLE (plus rapide)
 * 
 * Au lieu d'attendre chaque requête, les lancer toutes ensemble
 */
export async function fetchVisualsForRecommendationsParallel(
  supabase: any,
  recommendations: MorphoRecommendations
): Promise<CategoryVisualsMap> {
  
  const result: CategoryVisualsMap = {
    hauts_visuels: [],
    robes_visuels: [],
    bas_visuels: []
  };

  // Créer toutes les promesses
  const categoryMapping = [
    { key: "hauts", dbCategory: "haut", resultKey: "hauts_visuels" },
    { key: "robes", dbCategory: "robe", resultKey: "robes_visuels" },
    { key: "bas", dbCategory: "bas", resultKey: "bas_visuels" },
    { key: "vestes", dbCategory: "veste", resultKey: "vestes_visuels" },
    { key: "maillots", dbCategory: "maillot", resultKey: "maillots_visuels" },
    { key: "lingerie", dbCategory: "lingerie", resultKey: "lingerie_visuels" }
  ] as const;

  // Créer un array de promesses
  const allPromises: Array<{
    resultKey: keyof CategoryVisualsMap;
    promise: Promise<VisualData | null>;
  }> = [];

  for (const { key, dbCategory, resultKey } of categoryMapping) {
    const categoryRecommendations = recommendations[key as keyof MorphoRecommendations];
    
    if (!categoryRecommendations || !("recommended" in categoryRecommendations)) {
      continue;
    }

    for (const rec of categoryRecommendations.recommended) {
      allPromises.push({
        resultKey,
        promise: fetchVisualForType(
          supabase,
          dbCategory,
          rec.type,
          recommendations.morpho_type,
          true
        )
      });
    }
  }

  // Lancer TOUTES les requêtes en parallèle
  console.log(`📸 Lancement de ${allPromises.length} recherches de visuels en parallèle...`);
  const visuals = await Promise.allSettled(allPromises.map(p => p.promise));

  // Traiter les résultats
  for (let i = 0; i < visuals.length; i++) {
    const { resultKey } = allPromises[i];
    const settlement = visuals[i];

    if (settlement.status === "fulfilled" && settlement.value) {
      const visual = settlement.value;
      
      // Dédupliquer
      const isDuplicate = (result[resultKey] || []).some(v => v.id === visual.id);
      if (!isDuplicate) {
        (result[resultKey] || []).push(visual);
      }
    }
  }

  // Limiter chaque catégorie à 5 visuels
  for (const key of Object.keys(result) as (keyof CategoryVisualsMap)[]) {
    if (result[key]) {
      result[key] = result[key]!.slice(0, 5);
    }
  }

  console.log(`✅ ${Object.values(result).reduce((sum, arr) => sum + (arr?.length || 0), 0)} visuels chargés`);
  return result;
}

/**
 * Formater les visuels pour PDFMonkey
 * 
 * Convertir la structure CategoryVisualsMap en format PDFMonkey
 */
export function formatVisualsForPDFMonkey(
  visualsMap: CategoryVisualsMap
): Record<string, any> {
  
  const formatted: Record<string, any> = {};

  for (const [key, visuels] of Object.entries(visualsMap)) {
    if (!visuels) continue;

    // Formater chaque visuel
    formatted[key] = visuels.map(v => ({
      image_url: v.image_url,
      thumbnail_url: v.thumbnail_url || v.image_url,
      description: v.description,
      style_tags: v.style_tags || [],
      type: v.type
    }));
  }

  return formatted;
}

/**
 * Fonction utilitaire: Vérifier la couverture des visuels
 * 
 * Enregistrer les visuels non trouvés pour analyse
 */
export async function logMissingVisuals(
  supabase: any,
  recommendations: MorphoRecommendations
): Promise<void> {
  
  const missing: Array<{ category: string; type: string; morpho: string }> = [];

  const categoryMapping = [
    { key: "hauts", dbCategory: "haut" },
    { key: "robes", dbCategory: "robe" },
    { key: "bas", dbCategory: "bas" },
    { key: "vestes", dbCategory: "veste" },
    { key: "maillots", dbCategory: "maillot" },
    { key: "lingerie", dbCategory: "lingerie" }
  ] as const;

  for (const { key, dbCategory } of categoryMapping) {
    const categoryRecommendations = recommendations[key as keyof MorphoRecommendations];
    
    if (!categoryRecommendations || !("recommended" in categoryRecommendations)) {
      continue;
    }

    for (const rec of categoryRecommendations.recommended) {
      const { data } = await supabase
        .from("visuels_pedagogiques")
        .select("id")
        .eq("category", dbCategory)
        .eq("type", rec.type)
        .limit(1)
        .single();

      if (!data) {
        missing.push({
          category: dbCategory,
          type: rec.type,
          morpho: recommendations.morpho_type
        });
      }
    }
  }

  // Enregistrer les manquantes
  if (missing.length > 0) {
    console.warn(`⚠️ ${missing.length} visuels manquants:`, missing);

    try {
      await supabase.from("visual_search_logs").insert(
        missing.map(m => ({
          category: m.category,
          type: m.type,
          morpho_type: m.morpho,
          found: false,
          timestamp: new Date().toISOString()
        }))
      );
    } catch (error) {
      console.error("Erreur enregistrement visuels manquants:", error);
    }
  }
}

/**
 * Statistiques: Quels visuels manquent le plus?
 */
export async function getMissingVisualStats(supabase: any) {
  const { data } = await supabase
    .from("visual_search_logs")
    .select("category, type, COUNT(*) as count")
    .eq("found", false)
    .group_by("category, type")
    .order("count", { ascending: false });

  return data || [];
}
