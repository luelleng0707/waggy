'use strict';

const { loadData } = require('./csvLoader');
const { encrypt } = require('../../security/encryption');

let store = null;
let pool = null;

const PROPRIETARY = ['traitConditions', 'traitBenefits', 'conditionIngredients', 'productRotationLogic'];
const GOAL_CONDITION_MAP = {
  joint_health: ['hip_dysplasia', 'ivdd', 'cruciate_ligament_rupture', 'osteoarthritis', 'luxating_patella', 'elbow_dysplasia'],
  skin_health: ['atopic_dermatitis', 'dry_skin', 'hot_spots', 'immune_mediated_dermatosis', 'pyoderma', 'otitis_externa'],
  dental_health: ['dental_disease', 'periodontal_disease'],
  digestive_health: ['chronic_enteropathy', 'ibd', 'food_sensitivities', 'colitis'],
  weight_management: ['obesity'],
  immune_support: ['immune_mediated_dermatosis'],
  respiratory_comfort: ['boas', 'heat_stress_syndrome', 'tracheal_collapse'],
  eye_health: ['cataracts', 'tear_staining', 'corneal_ulceration', 'progressive_retinal_atrophy'],
  cardiac_support: ['degenerative_valve_disease', 'dilated_cardiomyopathy', 'heart_murmur'],
  activity_support: ['exercise_induced_collapse', 'cruciate_ligament_rupture', 'hip_dysplasia']
};
const CONDITION_TO_GOAL = Object.entries(GOAL_CONDITION_MAP).reduce((acc, [goal, conditions]) => {
  for (const condition of conditions) acc[condition] = goal;
  return acc;
}, {});

function canonicalJoinKey(value) {
  return String(value || '').toLowerCase().replace(/[^a-z0-9]+/g, '');
}

function conditionCandidates(conditionName) {
  const normalized = String(conditionName || '').toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '');
  const directMapped = GOAL_CONDITION_MAP[normalized] || [];
  const goal = CONDITION_TO_GOAL[normalized];
  const siblingMapped = goal ? GOAL_CONDITION_MAP[goal] : [];
  return [normalized, ...directMapped, ...siblingMapped];
}

function conditionMatches(recordKey, recordName, candidates) {
  const rk = canonicalJoinKey(recordKey);
  const rn = canonicalJoinKey(recordName);
  return candidates.some(c => {
    const ck = canonicalJoinKey(c);
    return ck && (rk === ck || rn === ck);
  });
}

function initMemoryStore() {
  store = loadData();
  for (const key of PROPRIETARY) {
    if (store[key]?.length) {
      store[`_${key}`] = encrypt(store[key]);
    }
  }
  return store;
}

function getStore() {
  if (!store) initMemoryStore();
  return store;
}

async function initDb() {
  if (process.env.DATABASE_URL) {
    try {
      const { Pool } = require('pg');
      pool = new Pool({
        connectionString: process.env.DATABASE_URL,
        ssl: process.env.DATABASE_URL.includes('supabase') ? { rejectUnauthorized: false } : false
      });
      await pool.query('SELECT 1');
      console.log('[PPIE] PostgreSQL connected');
      return 'postgres';
    } catch (err) {
      console.warn('[PPIE] PostgreSQL unavailable, using CSV store:', err.message);
    }
  }
  initMemoryStore();
  const s = getStore();
  console.log('[PPIE] CSV intelligence store loaded');
  console.log(`[PPIE]   breeds: ${s.breeds.length}, trait_conditions: ${s.traitConditions.length}`);
  console.log(`[PPIE]   breed_conditions: ${s.breedConditions.length}, products: ${s.products.length}`);
  return 'memory';
}

function getBreeds(names) {
  const s = getStore();
  const aliases = {
    labrador: 'Labrador Retriever',
    golden: 'Golden Retriever',
    'golden retriever': 'Golden Retriever',
    husky: 'Siberian Husky',
    corgi: 'Pembroke Welsh Corgi',
    samoyed: 'Samoyed',
    poodle: 'Poodle',
    'french bulldog': 'French Bulldog',
    'german shepherd': 'German Shepherd Dog',
    beagle: 'Beagle',
    pug: 'Pug',
    dachshund: 'Smooth Dachshund'
  };

  return names.map(name => {
    const direct = s.breeds.find(b => b.breed_name.toLowerCase() === name.toLowerCase());
    if (direct) return direct;
    const alias = aliases[(name || '').toLowerCase()];
    if (alias) return s.breeds.find(b => b.breed_name === alias);
    return s.breeds.find(b => b.breed_name.toLowerCase().includes(name.toLowerCase()));
  }).filter(Boolean);
}

function getTraitRisksForBreed(breed) {
  const s = getStore();
  const traits = [
    { category: 'size', value: breed.size_class },
    { category: 'body_type', value: breed.body_type },
    { category: 'coat_type', value: breed.coat_type },
    { category: 'energy', value: breed.energy_level },
    { category: 'weakness_group', value: breed.weakness_group },
    { category: 'lifespan', value: breed.lifespan_class },
    { category: 'skull_type', value: breed.skull_type },
    { category: 'climate', value: breed.climate },
    { category: 'function_group', value: breed.function_group }
  ];
  return s.traitConditions.filter(tr =>
    traits.some(t => t.category === tr.trait_category && t.value === tr.trait_value)
  );
}

function getTraitInteractions(breeds) {
  const s = getStore();
  const traits = new Set();
  for (const breed of breeds) {
    [
      breed.size_class, breed.body_type, breed.coat_type, breed.energy_level,
      breed.weakness_group, breed.lifespan_class, breed.skull_type,
      breed.climate, breed.function_group
    ].forEach(v => { if (v) traits.add(v); });
  }
  return s.traitInteractions.filter(ti =>
    traits.has(ti.trait_a) && traits.has(ti.trait_b)
  );
}

function getTraitBenefits(breeds) {
  const s = getStore();
  const traits = new Set();
  for (const breed of breeds) {
    [
      breed.size_class, breed.body_type, breed.coat_type, breed.energy_level,
      breed.weakness_group, breed.lifespan_class, breed.skull_type,
      breed.climate, breed.function_group
    ].forEach(v => { if (v) traits.add(v); });
  }
  return s.traitBenefits.filter(tb => traits.has(tb.trait_a) && traits.has(tb.trait_b));
}

function getBreedObservedRisks(breedNames) {
  const s = getStore();
  return s.breedConditions.filter(r =>
    breedNames.some(n => n.toLowerCase() === r.breed_name.toLowerCase())
  );
}

function getMixedBaselines(breedNames) {
  const s = getStore();
  if (breedNames.length < 2) return [];
  const pairs = [];
  for (let i = 0; i < breedNames.length; i++) {
    for (let j = i + 1; j < breedNames.length; j++) {
      pairs.push([breedNames[i], breedNames[j]]);
    }
  }
  return s.mixedBreedMatrix.filter(mb =>
    pairs.some(([a, b]) =>
      (mb.breed_a.toLowerCase() === a.toLowerCase() && mb.breed_b.toLowerCase() === b.toLowerCase()) ||
      (mb.breed_a.toLowerCase() === b.toLowerCase() && mb.breed_b.toLowerCase() === a.toLowerCase())
    )
  );
}

function getMixedBreedInteractions(breedNames) {
  const s = getStore();
  return (s.mixedBreedInteractions || []).filter(row => {
    if (breedNames.length < 2) return true;
    const combo = String(row.condition_name || '').toLowerCase();
    return breedNames.every(name => combo.includes(name.toLowerCase()))
      || breedNames.length === 2;
  });
}

function collectBreedTraitValues(breed) {
  return [
    breed.size_class,
    breed.body_type,
    breed.coat_type,
    breed.energy_level,
    breed.weakness_group,
    breed.lifespan_class,
    breed.skull_type,
    breed.climate,
    breed.function_group
  ].filter(Boolean);
}

function getTraitPurposes(breeds) {
  const s = getStore();
  const traits = new Set();
  for (const breed of breeds) {
    for (const value of collectBreedTraitValues(breed)) traits.add(value);
  }
  return (s.traitPurposes || []).filter(row =>
    traits.has(row.trait_value) || traits.has(row.trait_category)
  );
}

function getEnvironmentalCompatibility(breeds, currentEnvironment) {
  const s = getStore();
  const traits = new Set();
  for (const breed of breeds) {
    for (const value of collectBreedTraitValues(breed)) traits.add(value);
  }
  const env = String(currentEnvironment || '').toLowerCase();
  return (s.environmentalMatrices || [])
    .filter(row => traits.has(row.trait))
    .map(row => {
      const matrixEnv = String(row.environment || '').toLowerCase();
      let score = row.compatibility_score;
      if (score == null && env) {
        if (!matrixEnv) score = null;
        else if (matrixEnv.includes(env) || env.includes(matrixEnv)) score = 0.9;
        else score = 0.65;
      }
      return {
        trait: row.trait,
        environment: row.environment,
        current_environment: currentEnvironment || null,
        compatibility_score: score,
        benefits: row.benefits,
        management_requirements: row.management_requirements,
        scientific_source: row.scientific_source
      };
    });
}

function getConditionIngredients(conditionName) {
  const s = getStore();
  const candidates = conditionCandidates(conditionName);
  return s.conditionIngredients.filter(ci =>
    conditionMatches(ci.condition_key, ci.condition_name, candidates)
  );
}

function getIngredientEvidence(name) {
  const s = getStore();
  const key = (name || '').toLowerCase().replace(/[^a-z0-9]+/g, '_');
  return s.ingredientEvidence.find(ie =>
    ie.ingredient_key === key ||
    ie.ingredient_name.toLowerCase() === (name || '').toLowerCase()
  );
}

function getIngredientMechanisms(name) {
  const s = getStore();
  const key = (name || '').toLowerCase().replace(/[^a-z0-9]+/g, '_');
  return (s.ingredientMechanisms || []).filter(im =>
    im.nutrient_key === key ||
    im.ingredient_key === key ||
    im.nutrient_name?.toLowerCase() === (name || '').toLowerCase() ||
    im.ingredient_name?.toLowerCase() === (name || '').toLowerCase()
  );
}

function getNutrientPriorities(conditionName) {
  const s = getStore();
  const candidates = conditionCandidates(conditionName);
  return (s.nutrientPriorities || []).filter(n =>
    conditionMatches(n.condition_key, n.condition_name, candidates)
  ).sort((a, b) => (a.priority_rank || 999) - (b.priority_rank || 999));
}

function getClinicalEvidence(conditionName) {
  const s = getStore();
  const candidates = conditionCandidates(conditionName);
  return (s.clinicalEvidenceBase || []).filter(e =>
    conditionMatches(e.condition_key, e.condition_name, candidates)
  );
}

function getNaturalFoodSources(name) {
  const s = getStore();
  const key = (name || '').toLowerCase().replace(/[^a-z0-9]+/g, '_');
  return (s.naturalFoodSources || []).filter(f =>
    f.ingredient_key === key ||
    f.ingredient_name?.toLowerCase() === (name || '').toLowerCase()
  );
}

function getAllProducts() {
  return getStore().products;
}

function getProductIngredients(productId) {
  const s = getStore();
  return s.productIngredients.filter(pi => pi.product_id === productId);
}

function getFeedingRule(productId, weightKg) {
  const s = getStore();
  return s.productFeedingRules.find(r =>
    r.product_id === productId &&
    weightKg >= r.weight_min_kg &&
    weightKg <= r.weight_max_kg
  );
}

function getActivities(conditionName) {
  const s = getStore();
  const candidates = conditionCandidates(conditionName);
  return s.activityRecommendations.filter(a =>
    conditionMatches(a.condition_key, a.condition_name, candidates)
  );
}

function getProductByName(name) {
  return getStore().products.find(p => p.product_name === name);
}

function getProductFunctions(productId) {
  const s = getStore();
  return s.productFunctions.filter(f => f.product_id === productId);
}

function getProductsByCategory(category) {
  return getStore().products.filter(p => p.category === category);
}


function getProprietaryDecrypted(tableKey) {
  const s = getStore();
  return s[tableKey] || require('../../security/encryption').decrypt(s[`_${tableKey}`]);
}

module.exports = {
  initDb,
  getStore,
  getBreeds,
  getTraitRisksForBreed,
  getTraitInteractions,
  getTraitBenefits,
  getBreedObservedRisks,
  getMixedBaselines,
  getMixedBreedInteractions,
  getTraitPurposes,
  getEnvironmentalCompatibility,
  getConditionIngredients,
  getIngredientEvidence,
  getIngredientMechanisms,
  getNutrientPriorities,
  getClinicalEvidence,
  getNaturalFoodSources,
  getAllProducts,
  getProductIngredients,
  getFeedingRule,
  getActivities,
  getProductByName,
  getProductFunctions,
  getProductsByCategory,
  getProprietaryDecrypted
};
