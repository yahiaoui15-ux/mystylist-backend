/**
 * supabase/migrations/[TIMESTAMP]_create_report_tables.sql
 * 
 * Migration SQL pour créer les tables nécessaires
 * pour la génération automatique des rapports
 * 
 * Exécuter dans Supabase SQL Editor ou via CLI:
 * supabase db push
 */

-- ============================================
-- TABLE: reports (principal)
-- ============================================
CREATE TABLE IF NOT EXISTS public.reports (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- Status de génération
  status TEXT NOT NULL DEFAULT 'pending',
  -- Valeurs possibles: pending, processing, completed, failed
  
  -- Fichiers
  file_path TEXT,  -- Chemin dans Supabase Storage
  public_url TEXT,  -- URL publique du PDF
  
  -- Timestamps
  initiated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  generated_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  
  -- Métadonnées
  error TEXT,  -- Message d'erreur si failed
  generation_time_ms INTEGER,  -- Temps de génération en ms
  
  CONSTRAINT reports_user_id_idx UNIQUE (user_id, created_at)
);

-- Index pour les requêtes fréquentes
CREATE INDEX IF NOT EXISTS reports_user_id_idx ON public.reports(user_id);
CREATE INDEX IF NOT EXISTS reports_status_idx ON public.reports(status);
CREATE INDEX IF NOT EXISTS reports_created_at_idx ON public.reports(created_at DESC);

-- ============================================
-- TABLE: payments (historique paiements)
-- ============================================
CREATE TABLE IF NOT EXISTS public.payments (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- Info Stripe
  stripe_charge_id TEXT NOT NULL UNIQUE,
  stripe_payment_intent_id TEXT,
  
  -- Montant
  amount INTEGER NOT NULL,  -- en centimes
  currency TEXT NOT NULL DEFAULT 'eur',
  
  -- Status
  status TEXT NOT NULL,  -- succeeded, failed
  error TEXT,
  
  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  
  -- Métadonnées
  metadata JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS payments_user_id_idx ON public.payments(user_id);
CREATE INDEX IF NOT EXISTS payments_stripe_charge_id_idx ON public.payments(stripe_charge_id);
CREATE INDEX IF NOT EXISTS payments_status_idx ON public.payments(status);

-- ============================================
-- TABLE: user_profiles (données utilisateur)
-- ============================================
CREATE TABLE IF NOT EXISTS public.user_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- Infos personnelles
  first_name TEXT,
  last_name TEXT,
  email TEXT,
  
  -- Photos
  photos JSONB DEFAULT '[]',  -- Array de URLs
  
  -- Préférences
  preferred_brands JSONB DEFAULT '[]',  -- Array de marques préférées
  
  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  
  CONSTRAINT user_profiles_unique_email UNIQUE (email)
);

-- ============================================
-- TABLE: colorimetry (analyse colorimétrique)
-- ============================================
CREATE TABLE IF NOT EXISTS public.colorimetry (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- Analyse
  season TEXT NOT NULL,  -- Automne, Printemps, Été, Hiver
  undertone TEXT NOT NULL,  -- Chaud, Froid, Neutre
  
  -- Palette
  colors JSONB NOT NULL DEFAULT '[]',  -- Array de couleurs
  
  -- Détails
  notes TEXT,
  
  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS colorimetry_user_id_idx ON public.colorimetry(user_id);

-- ============================================
-- TABLE: morphology (analyse morphologique)
-- ============================================
CREATE TABLE IF NOT EXISTS public.morphology (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- Type
  type TEXT NOT NULL,  -- O, X, I, V, A, etc.
  
  -- Mesures (en cm)
  measurements JSONB NOT NULL DEFAULT '{}',
  --{
  --  "bust": 95,
  --  "waist": 80,
  --  "hips": 100,
  --  "shoulders": 40,
  --  "height": 165
  --}
  
  -- Détails
  notes TEXT,
  
  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS morphology_user_id_idx ON public.morphology(user_id);
CREATE INDEX IF NOT EXISTS morphology_type_idx ON public.morphology(type);

-- ============================================
-- TABLE: styling (profil stylistique)
-- ============================================
CREATE TABLE IF NOT EXISTS public.styling (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- Archétypes
  archetypes JSONB NOT NULL DEFAULT '[]',
  --[
  --  {
  --    "name": "Classique",
  --    "percentage": 40,
  --    "description": "..."
  --  }
  --]
  
  -- Préférences
  preferred_style TEXT,
  avoided_style TEXT,
  
  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS styling_user_id_idx ON public.styling(user_id);

-- ============================================
-- TABLE: wardrobe (garde-robe capsule)
-- ============================================
CREATE TABLE IF NOT EXISTS public.wardrobe (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- Type
  item_type TEXT NOT NULL,  -- haut, bas, robe, veste, chaussure, accessoire
  category TEXT NOT NULL,  -- basic, statement
  
  -- Produit
  product_name TEXT NOT NULL,
  brand TEXT NOT NULL,
  price DECIMAL(10, 2),
  url TEXT,
  image_url TEXT,
  
  -- Description
  description TEXT,
  style_tips JSONB DEFAULT '[]',  -- Array de conseils
  
  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  
  CONSTRAINT wardrobe_unique_user_item UNIQUE (user_id, product_name, brand)
);

CREATE INDEX IF NOT EXISTS wardrobe_user_id_idx ON public.wardrobe(user_id);
CREATE INDEX IF NOT EXISTS wardrobe_category_idx ON public.wardrobe(category);
CREATE INDEX IF NOT EXISTS wardrobe_item_type_idx ON public.wardrobe(item_type);

-- ============================================
-- TABLE: mix_match (formules mix & match)
-- ============================================
CREATE TABLE IF NOT EXISTS public.mix_match_formulas (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- Formule
  title TEXT NOT NULL,  -- Élégance décontractée, etc.
  occasion TEXT NOT NULL,  -- quotidien, soirée, etc.
  
  -- Produits
  items JSONB NOT NULL DEFAULT '[]',
  --[
  --  {
  --    "wardrobe_item_id": "uuid",
  --    "product_name": "...",
  --    "brand": "...",
  --    "image_url": "..."
  --  }
  --]
  
  -- Description
  description TEXT,
  why_it_works TEXT,
  variations JSONB DEFAULT '[]',  -- Array de variantes
  
  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  
  CONSTRAINT mix_match_unique_user_occasion UNIQUE (user_id, occasion)
);

CREATE INDEX IF NOT EXISTS mix_match_user_id_idx ON public.mix_match_formulas(user_id);
CREATE INDEX IF NOT EXISTS mix_match_occasion_idx ON public.mix_match_formulas(occasion);

-- ============================================
-- TABLE: recommendations (marques recommandées)
-- ============================================
CREATE TABLE IF NOT EXISTS public.recommendations (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- Marque
  brand_name TEXT NOT NULL,
  description TEXT,
  price_range TEXT,  -- affordable, mid, luxury
  
  -- Détails
  website_url TEXT,
  physical_locations TEXT,  -- JSON ou string séparé par virgules
  suggested_items JSONB DEFAULT '[]',  -- 3 items phares
  
  -- Raison de la recommandation
  why_recommended TEXT,
  
  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  
  CONSTRAINT recommendations_unique_user_brand UNIQUE (user_id, brand_name)
);

CREATE INDEX IF NOT EXISTS recommendations_user_id_idx ON public.recommendations(user_id);
CREATE INDEX IF NOT EXISTS recommendations_price_range_idx ON public.recommendations(price_range);

-- ============================================
-- TRIGGER: Mettre à jour updated_at
-- ============================================

-- Pour user_profiles
CREATE OR REPLACE FUNCTION update_user_profiles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_user_profiles_updated_at
BEFORE UPDATE ON public.user_profiles
FOR EACH ROW
EXECUTE PROCEDURE update_user_profiles_updated_at();

-- Pour colorimetry
CREATE OR REPLACE FUNCTION update_colorimetry_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_colorimetry_updated_at
BEFORE UPDATE ON public.colorimetry
FOR EACH ROW
EXECUTE PROCEDURE update_colorimetry_updated_at();

-- Pour morphology
CREATE OR REPLACE FUNCTION update_morphology_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_morphology_updated_at
BEFORE UPDATE ON public.morphology
FOR EACH ROW
EXECUTE PROCEDURE update_morphology_updated_at();

-- Pour styling
CREATE OR REPLACE FUNCTION update_styling_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_styling_updated_at
BEFORE UPDATE ON public.styling
FOR EACH ROW
EXECUTE PROCEDURE update_styling_updated_at();

-- ============================================
-- RLS (Row Level Security) POLICIES
-- ============================================

-- Permettre aux users de voir leurs propres données
ALTER TABLE public.reports ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can read their own reports"
  ON public.reports FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own reports"
  ON public.reports FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Permettre à l'Edge Function de modifier les rapports
CREATE POLICY "Service role can update reports"
  ON public.reports FOR UPDATE
  USING (true) -- Seulement avec service_role_key
  WITH CHECK (true);

-- Même pattern pour les autres tables
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can read their own profile"
  ON public.user_profiles FOR SELECT
  USING (auth.uid() = id);

ALTER TABLE public.colorimetry ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can read their own colorimetry"
  ON public.colorimetry FOR SELECT
  USING (auth.uid() = user_id);

ALTER TABLE public.morphology ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can read their own morphology"
  ON public.morphology FOR SELECT
  USING (auth.uid() = user_id);

-- ============================================
-- VUE: Reports complète
-- ============================================

CREATE OR REPLACE VIEW public.reports_with_data AS
SELECT
  r.id,
  r.user_id,
  r.status,
  r.file_path,
  r.public_url,
  r.initiated_at,
  r.generated_at,
  r.error,
  r.generation_time_ms,
  up.first_name,
  up.email,
  c.season,
  m.type AS morphology_type
FROM public.reports r
LEFT JOIN public.user_profiles up ON r.user_id = up.id
LEFT JOIN public.colorimetry c ON r.user_id = c.user_id
LEFT JOIN public.morphology m ON r.user_id = m.user_id;

-- ============================================
-- SEED DATA (optionnel - pour tester)
-- ============================================

-- Décommenter pour tester
/*
INSERT INTO public.user_profiles (id, first_name, email)
VALUES ('xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx', 'Jane', 'jane@example.com')
ON CONFLICT DO NOTHING;

INSERT INTO public.colorimetry (user_id, season, undertone, colors)
VALUES (
  'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
  'Automne',
  'Chaud',
  '["#8B4513", "#D2691E", "#CD853F"]'
)
ON CONFLICT DO NOTHING;
*/
