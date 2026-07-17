-- Wagtopia PPIE — Portable Pet Intelligence Engine Schema
-- PostgreSQL / Supabase compatible

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Master breed definitions
CREATE TABLE IF NOT EXISTS breeds (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  breed_name TEXT UNIQUE NOT NULL,
  size TEXT NOT NULL,
  body_type TEXT NOT NULL,
  coat_type TEXT NOT NULL,
  energy_type TEXT NOT NULL,
  weakness_group TEXT NOT NULL,
  lifespan_class TEXT NOT NULL
);

-- Trait-specific problem prevalence
CREATE TABLE IF NOT EXISTS trait_risks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  trait_type TEXT NOT NULL,
  trait_value TEXT NOT NULL,
  condition_name TEXT NOT NULL,
  prevalence DECIMAL(6,4) NOT NULL,
  source_name TEXT NOT NULL,
  source_quote TEXT NOT NULL,
  source_url TEXT NOT NULL,
  UNIQUE(trait_type, trait_value, condition_name)
);

-- Protective trait interactions
CREATE TABLE IF NOT EXISTS trait_benefits (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  trait_a TEXT NOT NULL,
  trait_b TEXT NOT NULL,
  condition_name TEXT NOT NULL,
  reduction_factor DECIMAL(4,2) NOT NULL,
  source_name TEXT NOT NULL,
  source_quote TEXT NOT NULL,
  source_url TEXT NOT NULL
);

-- Observed purebred prevalence
CREATE TABLE IF NOT EXISTS breed_observed_risks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  breed_name TEXT NOT NULL,
  condition_name TEXT NOT NULL,
  prevalence DECIMAL(6,4) NOT NULL,
  source_name TEXT NOT NULL,
  source_quote TEXT NOT NULL,
  source_url TEXT NOT NULL,
  UNIQUE(breed_name, condition_name)
);

-- Mixed-breed baseline observations
CREATE TABLE IF NOT EXISTS mixed_breed_baselines (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  breed_a TEXT NOT NULL,
  breed_b TEXT NOT NULL,
  condition_name TEXT NOT NULL,
  prevalence DECIMAL(6,4) NOT NULL,
  source_name TEXT NOT NULL,
  source_quote TEXT NOT NULL,
  source_url TEXT NOT NULL
);

-- Condition → ingredient dosing
CREATE TABLE IF NOT EXISTS condition_ingredients (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  condition_name TEXT NOT NULL,
  ingredient_name TEXT NOT NULL,
  dose_basis TEXT NOT NULL,
  dose_min DECIMAL(10,2) NOT NULL,
  dose_max DECIMAL(10,2) NOT NULL,
  unit TEXT NOT NULL,
  source_name TEXT NOT NULL,
  source_quote TEXT NOT NULL,
  source_url TEXT NOT NULL,
  UNIQUE(condition_name, ingredient_name)
);

-- Ingredient evidence
CREATE TABLE IF NOT EXISTS ingredient_evidence (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ingredient_name TEXT UNIQUE NOT NULL,
  source_name TEXT NOT NULL,
  source_quote TEXT NOT NULL,
  source_url TEXT NOT NULL
);

-- Product inventory
CREATE TABLE IF NOT EXISTS products (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_name TEXT UNIQUE NOT NULL,
  brand TEXT DEFAULT 'Wagtopia',
  product_type TEXT NOT NULL,
  package_units INTEGER NOT NULL DEFAULT 30,
  shelf_life_days INTEGER NOT NULL DEFAULT 365,
  price DECIMAL(10,2) NOT NULL
);

-- Product composition
CREATE TABLE IF NOT EXISTS product_ingredients (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id UUID REFERENCES products(id) ON DELETE CASCADE,
  ingredient_name TEXT NOT NULL,
  amount_per_unit DECIMAL(10,2) NOT NULL,
  unit TEXT NOT NULL DEFAULT 'mg',
  UNIQUE(product_id, ingredient_name)
);

-- Treat rotation logic
CREATE TABLE IF NOT EXISTS product_rotation_logic (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_a UUID REFERENCES products(id),
  product_b UUID REFERENCES products(id),
  rotation_type TEXT NOT NULL
);

-- Customer product weighting
CREATE TABLE IF NOT EXISTS product_preferences (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id UUID REFERENCES products(id),
  priority_score DECIMAL(4,2) NOT NULL DEFAULT 1.0
);

-- Non-product activity recommendations
CREATE TABLE IF NOT EXISTS activity_recommendations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  condition_name TEXT NOT NULL,
  activity_name TEXT NOT NULL,
  frequency TEXT NOT NULL,
  duration_minutes INTEGER NOT NULL DEFAULT 30
);

-- API clients (HMAC)
CREATE TABLE IF NOT EXISTS api_clients (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id TEXT UNIQUE NOT NULL,
  client_secret TEXT NOT NULL,
  name TEXT NOT NULL,
  active BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_trait_risks_trait ON trait_risks(trait_type, trait_value);
CREATE INDEX IF NOT EXISTS idx_breed_observed ON breed_observed_risks(breed_name);
CREATE INDEX IF NOT EXISTS idx_condition_ingredients ON condition_ingredients(condition_name);
