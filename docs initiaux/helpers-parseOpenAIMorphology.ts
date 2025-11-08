/**
 * parseOpenAIMorphology.ts
 * 
 * Parser le texte OpenAI en recommandations structurées
 * 
 * Input: Texte brut de OpenAI
 * Output: Structure JSON avec types de vêtements recommandés
 * 
 * Exemple:
 * Input: "HAUTS: Encolure V, coupes fluides, qui drapent"
 * Output: { hauts: { recommended: [{ type: "encolure_v", description: "..." }] } }
 */

export interface Recommendation {
  type: string;
  description: string;
  confidence?: number; // 0-1, confiance du matching
}

export interface CategoryRecommendations {
  recommended: Recommendation[];
  avoid: string[];
}

export interface MorphoRecommendations {
  morpho_type: string;
  morpho_description: string;
  hauts: CategoryRecommendations;
  robes: CategoryRecommendations;
  bas: CategoryRecommendations;
  vestes?: CategoryRecommendations;
  maillots?: CategoryRecommendations;
  lingerie?: CategoryRecommendations;
}

/**
 * Patterns de reconnaissance pour chaque type de vêtement
 * Utilisé pour matcher le texte OpenAI aux types en BD
 */
const RECOGNITION_PATTERNS = {
  hauts: {
    encolure_v: {
      patterns: /encolure\s+v|col\s+v|v\s+profonde|v\s+plongeant/i,
      keywords: ["encolure V", "col V", "V profonde"]
    },
    fluide: {
      patterns: /fluide|ample|loose|drapant|qui\s+drap|souple/i,
      keywords: ["fluide", "ample", "drapant"]
    },
    cache_ventre: {
      patterns: /cache[- ]ventre|volumineux|qui\s+cache|oversize/i,
      keywords: ["cache-ventre", "volumineux"]
    },
    structuree: {
      patterns: /structuré|ajusté|cintré|moulant|fitted/i,
      keywords: ["structuré", "ajusté", "cintré"]
    },
    col_rond: {
      patterns: /col\s+rond|rond|crew\s+neck/i,
      keywords: ["col rond"]
    },
    debardeur: {
      patterns: /débardeur|tank\s+top|camisole|sans\s+manches/i,
      keywords: ["débardeur", "camisole"]
    },
    rayures: {
      patterns: /rayures?|striped|horizontal/i,
      keywords: ["rayures"]
    },
    transparent: {
      patterns: /transparent|voile|dentelle|semi[- ]transparent/i,
      keywords: ["transparent", "voile"]
    }
  },
  
  robes: {
    empire: {
      patterns: /empire|taille\s+marquée|sous[- ]poitrine|taille\s+haute\s+robe/i,
      keywords: ["empire", "taille marquée"]
    },
    portefeuille: {
      patterns: /portefeuille|wrap\s+dress|enroulée/i,
      keywords: ["portefeuille", "wrap"]
    },
    chemisier: {
      patterns: /chemisier|shirt\s+dress|robe\s+chemise/i,
      keywords: ["chemisier", "shirt dress"]
    },
    moulante: {
      patterns: /moulante|ajustée|slim|fitted|bodycon/i,
      keywords: ["moulante", "ajustée"]
    },
    fluide: {
      patterns: /fluide|ample|loose|évasée/i,
      keywords: ["fluide", "ample"]
    },
    longueur_genou: {
      patterns: /genou|midi|knee|length/i,
      keywords: ["genou", "midi"]
    },
    cache_ventre: {
      patterns: /cache[- ]ventre|qui\s+cache|volumineux/i,
      keywords: ["cache-ventre"]
    },
    fourreau: {
      patterns: /fourreau|pencil|gaine/i,
      keywords: ["fourreau", "pencil"]
    }
  },
  
  bas: {
    taille_haute: {
      patterns: /taille\s+haute|high\s+waist|taille\s+fine/i,
      keywords: ["taille haute"]
    },
    taille_normale: {
      patterns: /taille\s+normale|classique|mid[\s-]rise/i,
      keywords: ["taille normale"]
    },
    droit: {
      patterns: /droit|straight|bootcut|droit\s+jambe/i,
      keywords: ["droit", "straight"]
    },
    evasee: {
      patterns: /évasée|flare|bootcut|bell\s+bottom|patte\s+d[\'e]ph/i,
      keywords: ["évasée", "flare"]
    },
    skinny: {
      patterns: /skinny|slim|ajusté|tight|jegging/i,
      keywords: ["skinny", "slim"]
    },
    ample: {
      patterns: /ample|large|wide\s+leg|palazzo|carotte/i,
      keywords: ["ample", "large"]
    },
    taille_basse: {
      patterns: /taille\s+basse|low[\s-]rise/i,
      keywords: ["taille basse"]
    },
    legging: {
      patterns: /legging|jegging|collant\s+fashion/i,
      keywords: ["legging"]
    }
  },
  
  vestes: {
    structuree: {
      patterns: /structurée|blazer|veste\s+tailleur|veste\s+structurée/i,
      keywords: ["structurée", "blazer"]
    },
    oversize: {
      patterns: /oversize|boyfriend|ample|loose|long/i,
      keywords: ["oversize", "boyfriend"]
    },
    cintrée: {
      patterns: /cintrée|ajustée|sculptée|fitted/i,
      keywords: ["cintrée", "ajustée"]
    },
    cuir: {
      patterns: /cuir|leather|perfecto/i,
      keywords: ["cuir"]
    },
    denim: {
      patterns: /denim|jean|jeans/i,
      keywords: ["denim"]
    }
  }
};

/**
 * Parser le texte OpenAI en recommandations structurées
 */
export function parseOpenAIMorphology(
  openaiText: string
): MorphoRecommendations {
  
  // 1️⃣ Extraire le type de morphologie
  const morphoMatch = openaiText.match(
    /(?:MORPHOLOGIE|Type|Silhouette)\s*:\s*([OXIVAHoxi]+)/i
  );
  const morphoType = morphoMatch?.[1]?.toUpperCase() || "UNKNOWN";
  
  // Décrire le type de morphologie
  const morphoDescriptions: Record<string, string> = {
    O: "Silhouette ronde (volume centré)",
    X: "Silhouette sablier (formes marquées)",
    I: "Silhouette droite (épaulettes alignées)",
    V: "Silhouette inversée (épaules larges)",
    A: "Silhouette pyramide (hanches larges)",
    H: "Silhouette rectangulaire"
  };
  const morphoDescription = morphoDescriptions[morphoType] || "Morphologie non identifiée";

  // 2️⃣ Initialiser la structure de résultat
  const result: MorphoRecommendations = {
    morpho_type: morphoType,
    morpho_description: morphoDescription,
    hauts: { recommended: [], avoid: [] },
    robes: { recommended: [], avoid: [] },
    bas: { recommended: [], avoid: [] }
  };

  // 3️⃣ Parser chaque catégorie
  const categories = ["hauts", "robes", "bas", "vestes", "maillots", "lingerie"] as const;
  
  for (const category of categories) {
    // Extraire la section de cette catégorie
    const categoryRegex = new RegExp(
      `${category.toUpperCase()}[\\s:]*([^]*?)(?=${categories.map(c => c.toUpperCase()).join("|")}|$)`,
      "i"
    );
    const categorySection = openaiText.match(categoryRegex)?.[1] || "";

    if (!categorySection) continue;

    // Parser les recommandations dans cette section
    const patterns = RECOGNITION_PATTERNS[category as keyof typeof RECOGNITION_PATTERNS];
    if (!patterns) continue;

    for (const [type, patternInfo] of Object.entries(patterns)) {
      // Chercher si ce type est recommandé
      if (patternInfo.patterns.test(categorySection)) {
        // Chercher la phrase correspondante pour plus de contexte
        const contextMatch = categorySection.match(
          new RegExp(`.{0,50}${patternInfo.patterns.source}.{0,50}`, "i")
        );
        const description = contextMatch?.[0]?.trim() 
          || `${category.slice(0, -1)} ${type.replace(/_/g, " ")}`;

        // Vérifier si c'est pas dans "à éviter"
        const isAvoided = categorySection.match(/éviter|pas|non|avoid/i) &&
                         categorySection.match(new RegExp(patternInfo.keywords[0], "i"));

        if (!isAvoided) {
          result[category] = result[category] || { recommended: [], avoid: [] };
          result[category].recommended.push({
            type,
            description,
            confidence: 0.8 // Score de confiance du matching
          });
        }
      }

      // Chercher aussi explicitement dans la section "à éviter"
      if (categorySection.match(/éviter|pas|non|avoid/i)) {
        const avoidMatch = categorySection.match(
          new RegExp(`(?:éviter|pas|non|avoid)[^.]*${patternInfo.keywords[0]}`, "i")
        );
        if (avoidMatch) {
          result[category] = result[category] || { recommended: [], avoid: [] };
          if (!result[category].avoid.includes(type)) {
            result[category].avoid.push(type);
          }
        }
      }
    }

    // Limiter à 5 recommandations par catégorie pour éviter trop de visuels
    if (result[category]?.recommended) {
      result[category].recommended = result[category].recommended.slice(0, 5);
    }
  }

  return result;
}

/**
 * Extraire toutes les recommandations "à faire" de OpenAI
 * Utilisé pour créer une liste de types à chercher en BD
 */
export function extractRecommendationTypes(
  recommendations: MorphoRecommendations
): Array<{ category: string; type: string; description: string }> {
  
  const types: Array<{ category: string; type: string; description: string }> = [];

  const categories = ["hauts", "robes", "bas", "vestes", "maillots", "lingerie"] as const;
  
  for (const category of categories) {
    const catRecommendations = recommendations[category];
    if (!catRecommendations?.recommended) continue;

    for (const rec of catRecommendations.recommended) {
      types.push({
        category,
        type: rec.type,
        description: rec.description
      });
    }
  }

  return types;
}

/**
 * Helper: Tester le parser avec un exemple
 */
export function testParser() {
  const exampleOpenAI = `
    MORPHOLOGIE: O (Silhouette ronde)
    
    HAUTS RECOMMANDÉS:
    - Encolure en V profonde pour allonger
    - Coupes fluides qui ne marquent pas
    - Matières qui drapent
    
    HAUTS À ÉVITER:
    - Cols ronds qui élargissent
    - Cols bateau
    
    ROBES RECOMMANDÉES:
    - Robe empire (structure sous poitrine)
    - Robe portefeuille
    
    BAS RECOMMANDÉS:
    - Taille haute pour affiner
    - Coupes droites
    
    VESTES RECOMMANDÉES:
    - Veste structurée pour cadrer
  `;

  const result = parseOpenAIMorphology(exampleOpenAI);
  console.log("Parser result:", JSON.stringify(result, null, 2));
  return result;
}
