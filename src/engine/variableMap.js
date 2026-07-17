'use strict';

/**
 * Master variable-map for the PPIE deterministic pipeline.
 * Biology → Health Risk → Management → Nutrition → Products → Feeding Plan
 */
const PIPELINE_STAGES = [
  'biology',
  'health_risk',
  'management',
  'nutrition',
  'products',
  'feeding_plan'
];

const PROFILE_INPUTS = [
  'breed',
  'age_years',
  'weight_kg',
  'sex',
  'bcs',
  'activity_level',
  'current_environment'
];

const VARIABLE_MAP = {
  pipeline_flow: PIPELINE_STAGES,
  profile_inputs: PROFILE_INPUTS,

  biology: {
    stage: 1,
    label: 'Recognition Destructuring & Ancestry',
    files: {
      BREEDS: {
        path: 'data/breed_analysis/1_biological_traits/BREEDS.csv',
        schema: ['breed', 'body_size', 'body_type', 'coat_type', 'skull_type', 'energy_level', 'climate_adaptation', 'lifespan_profile'],
        runtime_aliases: { size: 'body_size', energy: 'energy_level', climate: 'climate_adaptation', lifespan: 'lifespan_profile' }
      },
      MIXED_BREED_MATRIX: {
        path: 'data/breed_analysis/1_biological_traits/MIXED_BREED_MATRIX.csv',
        schema: ['primary_breed', 'secondary_breed', 'breed_split_pct', 'inherited_traits'],
        runtime_aliases: { breed_a: 'primary_breed', breed_b: 'secondary_breed', condition: 'inherited_traits', factor: 'breed_split_pct' }
      },
      MIXED_BREED_INTERACTIONS: {
        path: 'data/breed_analysis/1_biological_traits/MIXED_BREED_INTERACTIONS.csv',
        schema: ['breed_combination', 'dominant_trait', 'suppressed_trait'],
        runtime_aliases: { trait_a: 'dominant_trait', trait_b: 'suppressed_trait', condition: 'breed_combination', factor: 'suppressed_trait' }
      },
      TRAIT_PURPOSES: {
        path: 'data/breed_analysis/2_evolutionary_traits/TRAIT_PURPOSES.csv',
        schema: ['trait', 'evolutionary_function', 'biological_advantages', 'adaptive_behavior', 'original_working_purpose']
      },
      ENVIRONMENTAL_MATRICES: {
        path: 'data/breed_analysis/2_evolutionary_traits/ENVIRONMENTAL_MATRICES.csv',
        schema: ['trait', 'environment', 'compatibility_score', 'benefits', 'management_requirements', 'scientific_source']
      }
    }
  },

  health_risk: {
    stage: 2,
    label: 'Epidemiology Pools & Interaction Codes',
    formula: 'final_priority = sum(prevalence_traits) * multiplier_effect',
    files: {
      BREED_CONDITIONS: {
        path: 'data/breed_analysis/3_management_considerations/BREED_CONDITIONS.csv',
        schema: ['breed', 'condition', 'prevalence', 'sample_size', 'confidence', 'study', 'source_url', 'year']
      },
      BODYTYPE_CONDITIONS: {
        path: 'data/breed_analysis/3_management_considerations/BODYTYPE_CONDITIONS.csv',
        schema: ['body_type', 'condition', 'prevalence', 'sample_size', 'confidence', 'study', 'source_url', 'year']
      },
      COATTYPE_CONDITIONS: {
        path: 'data/breed_analysis/3_management_considerations/COATTYPE_CONDITIONS.csv',
        schema: ['coat_type', 'condition', 'prevalence', 'sample_size', 'confidence', 'study', 'source_url', 'year']
      },
      TRAIT_INTERACTIONS: {
        path: 'data/breed_analysis/3_management_considerations/TRAIT_INTERACTIONS.csv',
        schema: ['trait_1', 'trait_2', 'target_condition', 'multiplier_effect'],
        runtime_aliases: { trait_a: 'trait_1', trait_b: 'trait_2', condition: 'target_condition', factor: 'multiplier_effect' }
      }
    }
  },

  management: {
    stage: 3,
    label: 'Preventative Management',
    files: {
      TRAIT_BENEFITS: {
        path: 'data/breed_analysis/4_preventative_management/TRAIT_BENEFITS.csv',
        schema: ['trait', 'recommendation', 'benefit', 'environment', 'source']
      },
      CONDITION_ACTIVITIES: {
        path: 'data/breed_analysis/4_preventative_management/CONDITION_ACTIVITIES.csv',
        schema: ['condition', 'activity', 'priority_tier']
      },
      ACTIVITY_EVIDENCE: {
        path: 'data/breed_analysis/4_preventative_management/ACTIVITY_EVIDENCE.csv',
        schema: ['activity', 'frequency', 'duration', 'mechanism', 'study', 'quote', 'source_url']
      }
    }
  },

  nutrition: {
    stage: 4,
    label: 'Clinical Ingredient Conversion',
    files: {
      CONDITION_INGREDIENTS: {
        path: 'data/breed_analysis/5_scientific_nutrition/CONDITION_INGREDIENTS.csv',
        schema: ['condition', 'ingredient_name', 'target_daily_dose', 'unit'],
        runtime_aliases: { recommended_daily_dose: 'target_daily_dose', dose_unit: 'unit' }
      },
      INGREDIENT_EVIDENCE: {
        path: 'data/breed_analysis/5_scientific_nutrition/INGREDIENT_EVIDENCE.csv',
        schema: ['ingredient_name', 'mechanism', 'evidence_level', 'clinical_study', 'doi', 'source_url']
      },
      INGREDIENT_MECHANISMS: {
        path: 'data/breed_analysis/5_scientific_nutrition/INGREDIENT_MECHANISMS.csv',
        schema: ['ingredient_name', 'biological_action', 'evidence_strength']
      },
      NATURAL_FOOD_SOURCES: {
        path: 'data/breed_analysis/5_scientific_nutrition/NATURAL_FOOD_SOURCES.csv',
        schema: ['ingredient_name', 'source_food_item', 'educational_notes']
      },
      NUTRIENT_PRIORITIES: {
        path: 'data/breed_analysis/5_scientific_nutrition/NUTRIENT_PRIORITIES.csv',
        schema: ['product_id', 'ingredient_name', 'target_intake', 'current_intake', 'required_intake', 'coverage_pct']
      }
    }
  },

  products: {
    stage: 5,
    label: 'Inventory Fulfillment',
    formula: 'unit_cost_per_bag = list_price_rmb / package_units',
    files: {
      PRODUCT_CATALOG: {
        path: 'data/breed_analysis/product_portfolio/PRODUCT_CATALOG.csv',
        schema: ['product_id', 'brand', 'category', 'subcategory', 'product_name', 'status', 'image_url', 'purchase_url']
      },
      PRODUCT_COMPONENTS: {
        path: 'data/breed_analysis/product_portfolio/PRODUCT_COMPONENTS.csv',
        schema: ['product_id', 'component_type', 'component_name', 'value', 'unit', 'evidence_level', 'notes']
      },
      PRODUCT_PRICING: {
        path: 'data/breed_analysis/product_portfolio/PRODUCT_PRICING.csv',
        schema: ['product_id', 'list_price_rmb', 'package_units', 'unit_label']
      },
      PRODUCT_FEEDING_RULES: {
        path: 'data/breed_analysis/product_portfolio/PRODUCT_FEEDING_RULES.csv',
        schema: ['product_id', 'weight_min_kg', 'weight_max_kg', 'daily_amount', 'daily_unit'],
        runtime_aliases: { min_weight_kg: 'weight_min_kg', max_weight_kg: 'weight_max_kg' }
      }
    }
  },

  feeding_plan: {
    stage: 6,
    label: 'Feeding Plan Assembly',
    depends_on: ['nutrition', 'products']
  }
};

const PATH_ALIASES = {
  'breed_analysis/2_evolutionary_traits': 'breed_analysis/2_evolutionary_profiles',
  'breed_analysis/4_preventative_management': 'breed_analysis/4_preventative_interventions',
  'breed_analysis/product_portfolio': 'product_portfolio'
};

module.exports = {
  PIPELINE_STAGES,
  PROFILE_INPUTS,
  VARIABLE_MAP,
  PATH_ALIASES
};
