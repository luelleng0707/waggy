'use strict';

const { resolveBreeds } = require('./breedResolver');
const { computeRisks, getAgeStage } = require('./riskEngine');
const { mapIngredients } = require('./ingredientEngine');
const { matchProducts } = require('./productEngine');
const { buildMonthlyPlan, buildYearlyPlan } = require('./bundleEngine');
const { sizeToWeightKg } = require('../api/db/normalize');
const db = require('../api/db/queries');
const { PIPELINE_STAGES, VARIABLE_MAP } = require('./variableMap');
const {
  buildBiologySummary,
  buildHealthInsights,
  buildNutritionalTargets,
  enrichProductRecommendations
} = require('./wellnessEngine');

function normalizeProfile(payload) {
  const breeds = payload.breeds || (payload.breed ? [payload.breed] : []);
  const birthday = payload.birthday || '2020-01-01';
  const { ageYears, stage } = getAgeStage(birthday);
  const weightKg = payload.weight_kg || payload.weight
    ? parseFloat(payload.weight_kg || payload.weight)
    : estimateWeight(breeds);

  return {
    pet_name: payload.pet_name || payload.petName || 'Pet',
    breeds,
    birthday,
    sex: payload.sex || payload.gender || null,
    bcs: payload.bcs != null ? parseFloat(payload.bcs) : null,
    activity_level: payload.activity_level || payload.activity || null,
    current_environment: payload.current_environment || payload.current_climate || payload.climate || null,
    weight_kg: weightKg,
    age_years: ageYears,
    age_stage: stage,
    observed_conditions: payload.observed_conditions || []
  };
}

function estimateWeight(breedNames) {
  const breeds = resolveBreeds(breedNames);
  if (!breeds.length) return 20;
  const avg = breeds.reduce((s, b) => s + sizeToWeightKg(b.size_class), 0) / breeds.length;
  return Math.round(avg);
}

function buildBiologyStage(profile) {
  const resolvedBreeds = resolveBreeds(profile.breeds);
  const traitPurposes = db.getTraitPurposes(resolvedBreeds);
  const environmental = db.getEnvironmentalCompatibility(resolvedBreeds, profile.current_environment);
  const mixedMatrix = db.getMixedBaselines(profile.breeds);
  const mixedInteractions = db.getMixedBreedInteractions(profile.breeds);

  const biology = buildBiologySummary(resolvedBreeds, {
    breeds: resolvedBreeds.map(b => b.breed_name),
    breedCount: resolvedBreeds.length,
    ageYears: profile.age_years,
    ageStage: profile.age_stage
  });

  return {
    resolved_breeds: resolvedBreeds,
    biology,
    trait_purposes: traitPurposes,
    environmental_compatibility: environmental,
    mixed_breed_matrix: mixedMatrix,
    mixed_breed_interactions: mixedInteractions,
    source_files: Object.keys(VARIABLE_MAP.biology.files)
  };
}

function buildManagementStage(risks, profile) {
  const activities = [];
  const benefits = [];

  for (const risk of risks) {
    const acts = db.getActivities(risk.condition_key || risk.condition_name);
    for (const act of acts) {
      activities.push({
        condition_name: risk.condition_name,
        condition_key: risk.condition_key,
        ...act
      });
    }
  }

  const resolved = resolveBreeds(profile.breeds);
  const traitBenefits = db.getTraitBenefits(resolved);
  for (const b of traitBenefits) {
    benefits.push({
      trait_a: b.trait_a,
      trait_b: b.trait_b,
      condition_name: b.condition_name,
      reduction_factor: b.reduction_factor,
      reason: b.reason,
      source: b.source
    });
  }

  return {
    management_considerations: risks.map(r => ({
      condition_name: r.condition_name,
      condition_key: r.condition_key,
      risk_percent: r.risk_percent,
      prevalence_percent: r.breed_prevalence_percent ?? r.risk_percent,
      confidence_percent: r.confidence_percent,
      logic: r.logic
    })),
    lifestyle_requirements: activities,
    trait_benefits: benefits,
    source_files: Object.keys(VARIABLE_MAP.management.files)
  };
}

function buildNutritionStage(risks, weightKg, healthInsights) {
  const ingredients = mapIngredients(risks, weightKg);
  const nutritionalTargets = buildNutritionalTargets(ingredients, healthInsights);

  const orphanConditions = risks.filter(risk =>
    !ingredients.some(ing =>
      (ing.for_conditions || []).some(c =>
        String(c).toLowerCase() === String(risk.condition_name).toLowerCase()
      )
    ) && !db.getConditionIngredients(risk.condition_key || risk.condition_name).length
  ).map(r => r.condition_name);

  return {
    ingredient_requirements: ingredients,
    nutritional_targets: nutritionalTargets,
    orphan_conditions: orphanConditions,
    source_files: Object.keys(VARIABLE_MAP.nutrition.files)
  };
}

function buildProductsStage(ingredients, profile) {
  const rawProducts = matchProducts(
    ingredients,
    profile.past_products || [],
    profile.weight_kg
  );
  const productRecommendations = enrichProductRecommendations(
    rawProducts,
    ingredients,
    profile.pet_name
  );

  const unmappedIngredients = ingredients.filter(ing =>
    !rawProducts.some(p => p.ingredient_key === ing.ingredient_key
      || String(p.ingredient_name).toLowerCase() === String(ing.ingredient_name).toLowerCase())
  ).map(ing => ing.ingredient_name);

  return {
    raw_products: rawProducts,
    product_recommendations: productRecommendations,
    unmapped_ingredient_targets: unmappedIngredients,
    source_files: Object.keys(VARIABLE_MAP.products.files)
  };
}

function buildFeedingPlanStage(products, profile) {
  const monthly_plan = buildMonthlyPlan(products.raw_products, profile.weight_kg, profile.age_stage);
  const yearly_plan = buildYearlyPlan(monthly_plan, products.raw_products);

  return {
    monthly_plan,
    yearly_plan,
    unit_economics: (db.getAllProducts() || []).map(p => ({
      product_id: p.product_id,
      list_price_rmb: p.list_price_rmb ?? p.price ?? 0,
      package_units: p.package_units ?? 1,
      unit_cost_per_bag: p.unit_cost_per_bag ?? null
    }))
  };
}

function buildPipelineTrace(stages) {
  return PIPELINE_STAGES.map(stage => ({
    stage,
    label: VARIABLE_MAP[stage]?.label || stage,
    source_files: stages[stage]?.source_files || [],
    record_counts: {
      biology: stages.biology?.resolved_breeds?.length || 0,
      health_risk: stages.health_risk?.risks?.length || 0,
      management: stages.management?.lifestyle_requirements?.length || 0,
      nutrition: stages.nutrition?.ingredient_requirements?.length || 0,
      products: stages.products?.product_recommendations?.length || 0,
      feeding_plan: stages.feeding_plan?.monthly_plan?.items?.length || 0
    }[stage] ?? null,
    orphan_conditions: stage === 'nutrition' ? stages.nutrition?.orphan_conditions : undefined,
    unmapped_ingredients: stage === 'products' ? stages.products?.unmapped_ingredient_targets : undefined
  }));
}

function runPipeline(payload) {
  const profile = normalizeProfile(payload);

  // Stage 1: Biology
  const biologyStage = buildBiologyStage(profile);

  // Stage 2: Health Risk (never product-driven)
  const { risks, meta } = computeRisks({
    breeds: profile.breeds,
    birthday: profile.birthday,
    observed_conditions: profile.observed_conditions
  });
  const healthInsights = buildHealthInsights(risks, profile.pet_name);
  const healthRiskStage = { risks, meta, health_insights: healthInsights, source_files: Object.keys(VARIABLE_MAP.health_risk.files) };

  // Stage 3: Management
  const managementStage = buildManagementStage(risks, profile);

  // Stage 4: Nutrition (condition → ingredient, never product → condition)
  const nutritionStage = buildNutritionStage(risks, profile.weight_kg, healthInsights);

  // Stage 5: Products (fulfillment only)
  const productsStage = buildProductsStage(nutritionStage.ingredient_requirements, {
    ...profile,
    past_products: payload.past_products
  });

  // Stage 6: Feeding Plan
  const feedingPlanStage = buildFeedingPlanStage(productsStage, profile);

  const stages = {
    biology: biologyStage,
    health_risk: healthRiskStage,
    management: managementStage,
    nutrition: nutritionStage,
    products: productsStage,
    feeding_plan: feedingPlanStage
  };

  return {
    profile,
    pipeline_flow: PIPELINE_STAGES,
    variable_map_version: '1.0.0',
    stages,
    pipeline_trace: buildPipelineTrace(stages)
  };
}

module.exports = { runPipeline, normalizeProfile, PIPELINE_STAGES };
