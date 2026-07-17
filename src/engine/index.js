'use strict';

const { getAgeStage } = require('./riskEngine');
const { collectEvidence } = require('./evidenceEngine');
const { resolveBreeds } = require('./breedResolver');
const { sizeToWeightKg, conditionKey } = require('../api/db/normalize');
const db = require('../api/db/queries');
const {
  buildBiologySummary,
  buildHealthInsights,
  buildNutritionalTargets,
  enrichProductRecommendations,
  buildWellnessCoverage,
  buildWellnessPackages,
  buildActivityPlan,
  buildWellnessSummary,
  buildResearchSection,
  buildCalculationTrace
} = require('./wellnessEngine');
const {
  enrichPackageForDetail,
  buildProductAnalysis
} = require('./packageDetailEngine');
const { composePreventativeNarrative } = require('./narrativeEngine');
const { runPipeline, PIPELINE_STAGES } = require('./pipelineEngine');
const { VARIABLE_MAP } = require('./variableMap');

function inferClimateCompatibility(resolvedBreeds, currentClimate) {
  const climate = (currentClimate || '').toLowerCase();
  const rows = [];
  for (const b of resolvedBreeds) {
    const traitClimate = String(b.climate || '').toLowerCase();
    let score = 0.8;
    if (!climate) score = 0.75;
    else if (traitClimate.includes('cold') && climate.includes('cold')) score = 0.95;
    else if (traitClimate.includes('heat') && (climate.includes('hot') || climate.includes('heat'))) score = 0.95;
    else if (traitClimate.includes('temperate') && (climate.includes('temperate') || climate.includes('mild'))) score = 0.9;
    else if (traitClimate.includes('heat') && climate.includes('cold')) score = 0.62;
    else if (traitClimate.includes('cold') && (climate.includes('hot') || climate.includes('heat'))) score = 0.6;
    rows.push({
      breed: b.breed_name,
      trait_climate: b.climate,
      current_climate: currentClimate || 'unspecified',
      compatibility_score: Math.round(score * 1000) / 1000
    });
  }
  return rows;
}

function buildPreventativeSystemOutput({
  name,
  profile,
  resolvedBreeds,
  risks,
  currentClimate,
  nutritionalTargets
}) {
  const priorities = risks.slice(0, 8).map(r => ({
    condition_name: r.condition_name,
    condition_key: r.condition_key,
    management_consideration: true,
    prevalence_percent: r.breed_prevalence_percent ?? r.risk_percent,
    confidence_percent: r.confidence_percent,
    source_name: r.source?.source_name || null,
    source_quote: r.source?.source_quote || null,
    source_url: r.source?.source_url || null
  }));

  const diseaseRiskModifiers = risks.slice(0, 10).map(r => ({
    condition_name: r.condition_name,
    condition_key: r.condition_key,
    risk_percent: r.risk_percent,
    trait_risk_percent: r.trait_risk_percent,
    prevalence_percent: r.breed_prevalence_percent,
    interaction_factor: r.trait_explanation?.interaction_factor || 1,
    benefit_factor: r.trait_explanation?.benefit_factor || 1,
    mixed_breed_factor: r.mixed_breed_factor || 1,
    supporting_sources: (r.trait_explanation?.trait_evidence || []).map(e => ({
      trait_category: e.trait_category,
      trait_value: e.trait_value,
      prevalence: e.prevalence,
      source_name: e.source_name,
      source_quote: e.source_quote,
      source_url: e.source_url
    }))
  }));

  const lifestyleRequirements = priorities.flatMap(p =>
    db.getActivities(p.condition_name).map(a => ({
      condition_name: p.condition_name,
      activity_name: a.activity_name,
      frequency: a.frequency,
      duration_minutes: a.duration_minutes,
      source_name: a.source_name,
      source_quote: a.source_quote,
      source_url: a.source_url,
      requirement_type: 'lifestyle_requirement'
    }))
  );

  const nutritionPriorities = priorities.flatMap(p => {
    const nutrientRows = db.getNutrientPriorities(p.condition_name);
    if (nutrientRows.length) {
      return nutrientRows.map(n => ({
        condition_name: p.condition_name,
        nutrient_name: n.nutrient_name,
        target_dose: n.target_dose,
        target_unit: n.target_unit,
        priority_rank: n.priority_rank,
        evidence_level: n.evidence_level,
        source_name: n.source_name,
        source_quote: n.source_quote,
        source_url: n.source_url,
        mechanisms: db.getIngredientMechanisms(n.nutrient_name).slice(0, 4).map(m => ({
          ingredient_name: m.ingredient_name,
          amount_per_serving: m.amount_per_serving,
          unit: m.unit,
          mechanism_summary: m.mechanism_summary,
          source_product_id: m.source_product_id
        }))
      }));
    }

    const conditionRows = db.getConditionIngredients(p.condition_name);
    if (conditionRows.length) {
      return conditionRows.map(t => ({
        condition_name: p.condition_name,
        nutrient_name: t.ingredient_name,
        target_dose: t.recommended_daily_dose,
        target_unit: t.dose_unit,
        priority_rank: t.priority_rank || 999,
        evidence_level: 'condition_specific',
        source_name: t.source_name,
        source_quote: t.source_quote,
        source_url: t.source_url,
        mechanisms: db.getIngredientMechanisms(t.ingredient_name).slice(0, 4).map(m => ({
          ingredient_name: m.ingredient_name,
          amount_per_serving: m.amount_per_serving,
          unit: m.unit,
          mechanism_summary: m.mechanism_summary,
          source_product_id: m.source_product_id
        }))
      }));
    }

    return nutritionalTargets
      .filter(t => (t.supports_goals || []).some(g => String(g).toLowerCase().includes(String(p.condition_name).toLowerCase())))
      .map(t => ({
        condition_name: p.condition_name,
        nutrient_name: t.ingredient,
        target_dose: t.daily_target,
        target_unit: '',
        priority_rank: 999,
        evidence_level: null,
        source_name: t.source_name,
        source_quote: t.evidence_quote,
        source_url: t.source_url,
        mechanisms: db.getIngredientMechanisms(t.ingredient).slice(0, 4)
      }));
  });

  const environmentalCompatibilityMatrix = inferClimateCompatibility(resolvedBreeds, currentClimate);

  const wholeFoodContracts = priorities.map((p, idx) => {
    const nutrient = nutritionPriorities.find(n => n.condition_name === p.condition_name);
    const activity = lifestyleRequirements.find(a => a.condition_name === p.condition_name);
    if (!nutrient) return null;

    const targetDoseNumeric = parseFloat(
      String(nutrient.target_dose || '').match(/[-+]?[0-9]*\.?[0-9]+/)?.[0] || '0'
    );
    const targetDoseUnit = nutrient.target_unit || String(nutrient.target_dose || '').replace(/[-+]?[0-9]*\.?[0-9]+/, '').trim();
    const naturalFoods = db.getNaturalFoodSources(nutrient.nutrient_name)
      .filter(f => f.amount_per_100g > 0)
      .map(f => {
        // Food Dose (g) = (Target Daily Dose / Amount per 100g) * 100
        const grams = targetDoseNumeric > 0 ? Math.round((targetDoseNumeric / f.amount_per_100g) * 100) : 0;
        return {
          food_item: f.food_source,
          estimated_yield_per_100g: `${f.amount_per_100g} ${f.unit}`,
          calculated_daily_addition: `${grams}g`,
          clinical_note: f.bioavailability_notes
        };
      });

    return {
      condition: p.condition_name,
      priority_rank: idx + 1,
      targeted_intervention: {
        active_ingredient: nutrient.nutrient_name,
        required_dosage: nutrient.target_dose && nutrient.target_unit
          ? `${nutrient.target_dose} ${nutrient.target_unit}`.trim()
          : String(nutrient.target_dose || ''),
        scientific_validation: {
          study: nutrient.source_name || 'Clinical evidence dataset',
          verbatim_finding: nutrient.source_quote || 'Evidence-mapped nutrient support for condition management.',
          url: nutrient.source_url || null
        },
        natural_food_alternatives: naturalFoods,
        lifestyle_requirement: activity ? {
          activity_name: activity.activity_name,
          frequency: activity.frequency,
          duration_minutes: activity.duration_minutes,
          source_name: activity.source_name,
          source_quote: activity.source_quote,
          source_url: activity.source_url
        } : null
      }
    };
  }).filter(Boolean);

  const primary = priorities[0];
  const firstActivity = lifestyleRequirements.find(a => a.condition_name === primary?.condition_name);
  const firstNutrition = nutritionPriorities.find(n => n.condition_name === primary?.condition_name);
  const firstBreed = resolvedBreeds[0];
  const firstTrait = firstBreed?.coat_type || firstBreed?.body_type || firstBreed?.size_class || 'biological trait';
  const firstPurpose = 'environmental adaptation and physiological resilience';
  const samplePopulation = risks[0]?.source?.breed || 'breed-specific observational cohorts';
  const prevalence = primary?.prevalence_percent != null ? primary.prevalence_percent : (risks[0]?.risk_percent ?? 0);
  const sourceName = primary?.source_name || 'Veterinary comparative epidemiology dataset';
  const activityName = firstActivity?.activity_name || 'structured preventative exercise';
  const nutrientName = firstNutrition?.nutrient_name || 'targeted nutrient support';
  const dose = firstNutrition?.target_dose || 'clinically mapped dose';

  const narrative = composePreventativeNarrative({
    dogName: name,
    trait: firstTrait,
    breed: firstBreed?.breed_name || 'mixed-breed',
    biologicalPurpose: firstPurpose,
    currentClimate: currentClimate || 'current',
    prevalencePercent: prevalence,
    condition: primary?.condition_name || 'priority condition',
    samplePopulation,
    sourceName,
    activityName,
    nutrient: nutrientName,
    targetDose: dose
  });

  return {
    pipeline_flow: [
      'Dog Profile',
      'Biological Traits',
      'Management Considerations',
      'Lifestyle Interventions',
      'Nutritional Synthesis',
      'Whole-Food Feeding Equivalents'
    ],
    dog_profile: profile,
    biological_traits: resolvedBreeds.map(b => ({
      breed: b.breed_name,
      size: b.size_class,
      body_type: b.body_type,
      coat_type: b.coat_type,
      energy: b.energy_level,
      climate: b.climate,
      skull_type: b.skull_type,
      function_group: b.function_group,
      weakness_group: b.weakness_group,
      lifespan: b.lifespan_class
    })),
    management_considerations: priorities,
    lifestyle_interventions: lifestyleRequirements,
    nutritional_synthesis: nutritionPriorities,
    whole_food_feeding_equivalents: wholeFoodContracts,
    trait_analysis: priorities,
    preventative_health_priorities: priorities,
    standardized_outputs: {
      disease_risk_modifiers: diseaseRiskModifiers,
      environmental_compatibility_matrix: environmentalCompatibilityMatrix,
      lifestyle_requirements: lifestyleRequirements,
      nutrition_priorities: nutritionPriorities
    },
    output_contracts: wholeFoodContracts,
    narrative_synthesis: narrative
  };
}

function estimateWeight(breedNames, providedWeight) {
  if (providedWeight) return parseFloat(providedWeight);
  const breeds = resolveBreeds(breedNames);
  if (!breeds.length) return 20;
  const avg = breeds.reduce((s, b) => s + sizeToWeightKg(b.size_class), 0) / breeds.length;
  return Math.round(avg);
}

function buildGroomerStatus(observed) {
  const fields = [
    { key: 'eyes', label: 'Eyes', match: ['eyes', 'eye_discharge', 'tear_stains'] },
    { key: 'ears', label: 'Ears', match: ['ears', 'ear_redness', 'odor'] },
    { key: 'skin', label: 'Skin', match: ['skin', 'dry_skin', 'scratching', 'itching'] },
    { key: 'teeth', label: 'Teeth', match: ['teeth', 'bad_breath'] },
    { key: 'limps', label: 'Limps', match: ['limps', 'limping'] },
    { key: 'shedding', label: 'Shedding', match: ['shedding'] },
    { key: 'anal_gland', label: 'Anal Gland', match: ['anal_gland'] }
  ];
  const norm = observed.map(o => (o || '').toLowerCase().replace(/\s+/g, '_'));
  return fields.map(f => ({
    ...f,
    status: f.match.some(m => norm.includes(m)) ? 'flagged' : 'clear',
    live: f.match.some(m => norm.includes(m))
  }));
}

async function analyze(payload) {
  const pipeline = runPipeline(payload);
  const profile = {
    pet_name: pipeline.profile.pet_name,
    breeds: pipeline.stages.health_risk.meta.breeds,
    birthday: pipeline.profile.birthday,
    gender: pipeline.profile.sex,
    sex: pipeline.profile.sex,
    bcs: pipeline.profile.bcs,
    activity_level: pipeline.profile.activity_level,
    current_environment: pipeline.profile.current_environment,
    weight_kg: pipeline.profile.weight_kg,
    height_cm: payload.height ? parseFloat(payload.height) : null,
    age_years: pipeline.profile.age_years,
    age_stage: pipeline.profile.age_stage
  };

  const resolvedBreeds = pipeline.stages.biology.resolved_breeds;
  const meta = pipeline.stages.health_risk.meta;
  const risks = pipeline.stages.health_risk.risks;
  const biology = pipeline.stages.biology.biology;
  const healthInsights = pipeline.stages.health_risk.health_insights;
  const rawIngredients = pipeline.stages.nutrition.ingredient_requirements;
  const nutritionalTargets = pipeline.stages.nutrition.nutritional_targets;
  const rawProducts = pipeline.stages.products.raw_products;
  const productRecommendations = pipeline.stages.products.product_recommendations;
  const monthly_plan = pipeline.stages.feeding_plan.monthly_plan;
  const yearly_plan = pipeline.stages.feeding_plan.yearly_plan;
  const name = profile.pet_name;
  const weightKg = profile.weight_kg;
  const wellnessCoverage = buildWellnessCoverage(healthInsights, productRecommendations, rawIngredients);
  const wellnessSummary = buildWellnessSummary(name, biology, healthInsights, wellnessCoverage);
  const wellnessPackages = buildWellnessPackages(
    productRecommendations, monthly_plan, yearly_plan, healthInsights, weightKg, name, wellnessCoverage
  ).map(pkg => enrichPackageForDetail(pkg, rawIngredients, productRecommendations, name, weightKg));

  const packageDetails = Object.fromEntries(
    wellnessPackages.map(p => [p.tier, p])
  );

  const productAnalyses = {};
  for (const pkg of wellnessPackages) {
    for (const card of pkg.product_cards || []) {
      productAnalyses[card.product_id || card.product_name] = buildProductAnalysis(
        card.product_name, pkg, rawIngredients, productRecommendations, name, weightKg
      );
    }
  }
  const activityRecommendations = buildActivityPlan(resolvedBreeds, healthInsights, meta, name);
  const scientificEvidence = collectEvidence(risks, rawIngredients);
  const researchSection = buildResearchSection(biology, healthInsights, scientificEvidence, nutritionalTargets);
  const calculationTrace = buildCalculationTrace({
    profile: {
      pet_name: name,
      breeds: meta.breeds,
      age_years: meta.ageYears,
      weight_kg: weightKg
    },
    biology,
    healthInsights,
    nutritionalTargets,
    productRecommendations
  });
  const groomer = buildGroomerStatus(pipeline.profile.observed_conditions);

  const preventativeNutritionSystem = buildPreventativeSystemOutput({
    name,
    profile,
    resolvedBreeds,
    risks,
    currentClimate: profile.current_environment,
    nutritionalTargets
  });

  return {
    engine: 'PPIE',
    version: '2.1.0',
    pipeline_flow: PIPELINE_STAGES,
    variable_map: VARIABLE_MAP,
    pipeline_trace: pipeline.pipeline_trace,
    profile,
    biology,
    wellness_summary: wellnessSummary,
    wellness_coverage: wellnessCoverage,
    healthInsights,
    nutritionalTargets,
    ingredientRequirements: nutritionalTargets,
    productRecommendations,
    wellnessPackages,
    packageDetails,
    productAnalyses,
    activityRecommendations,
    scientificEvidence,
    researchSection,
    calculationTrace,
    groomer,
    preventativeNutritionSystem,

    // Legacy fields for backward compatibility
    pet: profile,
    wellness_score: wellnessCoverage.overall_score,
    risks: healthInsights.map(h => ({
      condition: h.title,
      condition_key: h.goal_id,
      risk_percent: h.priority_score,
      estimated_risk_percent: h.estimated_biological_risk_percent,
      trait_risk_percent: h.estimated_biological_risk_percent,
      breed_prevalence_percent: h.observed_breed_prevalence_percent,
      confidence_percent: h.confidence_percent,
      evidence_count: h.evidence_count,
      supporting_traits: h.supporting_traits.map(t => ({ category: 'trait', value: t })),
      logic: 'wellness_insight',
      groomer_boosted: h.groomer_priority,
      why: h.explanation,
      source_name: h.evidence_sources[0]?.source_name,
      source_quote: h.evidence_sources[0]?.source_quote,
      source_url: h.evidence_sources[0]?.source_url
    })),
    ingredients: nutritionalTargets.map(t => ({
      ingredient: t.ingredient,
      ingredient_key: t.ingredient_key,
      daily_dose: t.daily_target,
      monthly_dose: t.monthly_target,
      for_conditions: t.supports_goals,
      evidence_quote: t.evidence_quote,
      source_name: t.source_name,
      source_url: t.source_url
    })),
    products: productRecommendations,
    monthly_plan,
    yearly_plan,
    activities: activityRecommendations.condition_specific,
    evidence: scientificEvidence
  };
}

module.exports = { analyze, runPipeline, PIPELINE_STAGES, VARIABLE_MAP };
