 'use strict';

const fs = require('fs');
const path = require('path');
const { randomUUID } = require('crypto');
const { conditionKey, ingredientKey } = require('./normalize');
const { PATH_ALIASES } = require('../../engine/variableMap');

// __dirname is src/api/db → project root data/ requires three levels up
// ../../data would resolve to src/data (missing). Verified via runtime path diag.
const DATA_DIR = path.join(__dirname, '../../../data');
const SUB_DB_DIRS = {
  breed_analysis: 'breed_analysis',
  preventative_ingredients: 'preventative_ingredients',
  product_portfolio: 'product_portfolio'
};

const FILE_TO_SUB_DB = {
  // Breed analysis - tiered architecture
  BREEDS: 'breed_analysis/1_biological_traits',
  MIXED_BREED_MATRIX: 'breed_analysis/1_biological_traits',
  MIXED_BREED_INTERACTIONS: 'breed_analysis/1_biological_traits',
  TRAIT_PURPOSES: 'breed_analysis/2_evolutionary_profiles',
  ENVIRONMENTAL_MATRICES: 'breed_analysis/2_evolutionary_profiles',
  SIZE_CONDITIONS: 'breed_analysis/3_management_considerations',
  BODYTYPE_CONDITIONS: 'breed_analysis/3_management_considerations',
  COATTYPE_CONDITIONS: 'breed_analysis/3_management_considerations',
  ENERGY_CONDITIONS: 'breed_analysis/3_management_considerations',
  SKULLTYPE_CONDITIONS: 'breed_analysis/3_management_considerations',
  CLIMATE_CONDITIONS: 'breed_analysis/3_management_considerations',
  LIFESPAN_CONDITIONS: 'breed_analysis/3_management_considerations',
  WEAKNESSGROUP_CONDITIONS: 'breed_analysis/3_management_considerations',
  FUNCTIONGROUP_CONDITIONS: 'breed_analysis/3_management_considerations',
  BREED_CONDITIONS: 'breed_analysis/3_management_considerations',
  TRAIT_INTERACTIONS: 'breed_analysis/3_management_considerations',
  TRAIT_BENEFITS: 'breed_analysis/4_preventative_interventions',
  CONDITION_ACTIVITIES: 'breed_analysis/4_preventative_interventions',
  ACTIVITY_EVIDENCE: 'breed_analysis/4_preventative_interventions',
  CONDITION_INGREDIENTS_SCI: 'breed_analysis/5_scientific_nutrition',
  INGREDIENT_EVIDENCE_SCI: 'breed_analysis/5_scientific_nutrition',
  CONDITION_INGREDIENTS: 'breed_analysis/5_scientific_nutrition',
  INGREDIENT_EVIDENCE: 'breed_analysis/5_scientific_nutrition',
  INGREDIENT_MECHANISMS: 'breed_analysis/5_scientific_nutrition',
  NATURAL_FOOD_SOURCES: 'breed_analysis/5_scientific_nutrition',
  NUTRIENT_PRIORITIES: 'breed_analysis/5_scientific_nutrition',
  CLINICAL_EVIDENCE_BASE: 'breed_analysis/5_scientific_nutrition',

  // Preventative ingredient analysis
  CONDITION_INGREDIENTS: SUB_DB_DIRS.preventative_ingredients,
  CONDITION_PROTOCOLS: SUB_DB_DIRS.preventative_ingredients,
  INGREDIENT_EVIDENCE: SUB_DB_DIRS.preventative_ingredients,

  // Product portfolio (canonical + architecture alias path)
  PRODUCT_CATALOG: SUB_DB_DIRS.product_portfolio,
  PRODUCT_PRICING: SUB_DB_DIRS.product_portfolio,
  PRODUCT_COMPONENTS: SUB_DB_DIRS.product_portfolio,
  EXT_TREATS_BAKERY: SUB_DB_DIRS.product_portfolio,
  EXT_SUPPLEMENTS: SUB_DB_DIRS.product_portfolio,
  PRODUCT_FUNCTIONS: SUB_DB_DIRS.product_portfolio,
  PRODUCT_FEEDING_RULES: SUB_DB_DIRS.product_portfolio,
  'BREED_ANALYSIS/PRODUCT_PORTFOLIO/PRODUCT_CATALOG': 'breed_analysis/product_portfolio',
  'BREED_ANALYSIS/PRODUCT_PORTFOLIO/PRODUCT_COMPONENTS': 'breed_analysis/product_portfolio',
  'BREED_ANALYSIS/PRODUCT_PORTFOLIO/PRODUCT_PRICING': 'breed_analysis/product_portfolio',
  'BREED_ANALYSIS/PRODUCT_PORTFOLIO/PRODUCT_FEEDING_RULES': 'breed_analysis/product_portfolio'
};

function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = '';
  let inQuotes = false;

  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (inQuotes) {
      if (ch === '"' && text[i + 1] === '"') {
        field += '"';
        i++;
      } else if (ch === '"') {
        inQuotes = false;
      } else {
        field += ch;
      }
    } else if (ch === '"') {
      inQuotes = true;
    } else if (ch === ',') {
      row.push(field);
      field = '';
    } else if (ch === '\n' || ch === '\r') {
      if (ch === '\r' && text[i + 1] === '\n') i++;
      if (field.length || row.length) {
        row.push(field);
        rows.push(row);
        row = [];
        field = '';
      }
    } else {
      field += ch;
    }
  }
  if (field.length || row.length) {
    row.push(field);
    rows.push(row);
  }
  return rows;
}

function resolveCsvPath(filename) {
  const clean = String(filename || '').replace(/\.csv$/i, '');
  const canonical = `${clean}.csv`;
  const preferredDb = FILE_TO_SUB_DB[clean.toUpperCase()];
  const candidates = [];

  if (preferredDb) {
    const dbPaths = [preferredDb];
    if (PATH_ALIASES[preferredDb]) dbPaths.push(PATH_ALIASES[preferredDb]);
    for (const dbPath of dbPaths) {
      candidates.push(path.join(DATA_DIR, dbPath, canonical));
      candidates.push(path.join(DATA_DIR, dbPath, canonical.toUpperCase()));
      candidates.push(path.join(DATA_DIR, dbPath, canonical.toLowerCase()));
    }
  }

  // Legacy fallback at data root.
  candidates.push(path.join(DATA_DIR, canonical));
  candidates.push(path.join(DATA_DIR, canonical.toUpperCase()));
  candidates.push(path.join(DATA_DIR, canonical.toLowerCase()));

  for (const candidate of candidates) {
    if (fs.existsSync(candidate)) return candidate;
  }

  throw new Error(`Missing data file: ${canonical}`);
}

function readCsv(filename) {
  const filePath = resolveCsvPath(filename);
  const raw = fs.readFileSync(filePath, 'utf8').replace(/^\uFEFF/, '');
  const table = parseCsv(raw.trim());
  const headers = table[0];
  return table.slice(1).filter(r => r.some(c => c && c.trim())).map(cells => {
    const obj = {};
    headers.forEach((h, i) => { obj[h] = (cells[i] || '').trim(); });
    return obj;
  });
}

function buildGroomerMap(conditions) {
  const map = {
    tear_stains: 'Tear Staining',
    limping: 'Hip Dysplasia',
    limps: 'Cruciate Ligament Rupture',
    itching: 'Atopic Dermatitis',
    scratching: 'Atopic Dermatitis',
    dry_skin: 'Dry Skin',
    eye_discharge: 'Cataracts',
    eyes: 'Tear Staining',
    bad_breath: 'Dental Disease',
    teeth: 'Dental Disease',
    ears: 'Ear Infection',
    shedding: 'Dry Skin',
    anal_gland: 'Anal Gland Impaction',
    skin: 'Dry Skin',
    odor: 'Ear Infection'
  };

  for (const c of conditions) {
    if (c.observable_by_groomer === 'true') {
      const key = conditionKey(c.condition_name);
      map[key] = c.condition_name;
    }
  }
  return map;
}

function parsePercent(raw) {
  const normalized = String(raw || '').replace('%', '').trim();
  const num = parseFloat(normalized);
  if (!Number.isFinite(num)) return 0;
  return num > 1 ? num / 100 : num;
}

function normalizeTraitRows(rows, traitCategory, traitColumn) {
  return rows.map(r => ({
    consideration_type: 'management_consideration',
    trait_category: traitCategory,
    trait_value: r[traitColumn],
    condition_name: r.condition,
    condition_key: conditionKey(r.condition),
    prevalence: parsePercent(r.prevalence),
    sample_population: r.sample_population,
    sample_size: parseInt(r.sample_size, 10),
    source_name: r.source_name,
    source_quote: r.source_quote,
    source_url: r.source_url,
    year: parseInt(r.year, 10),
    confidence_level: r.confidence_level,
    evidence: {
      prevalence: parsePercent(r.prevalence),
      sample_population: r.sample_population,
      sample_size: parseInt(r.sample_size, 10),
      source_name: r.source_name,
      source_quote: r.source_quote,
      source_url: r.source_url
    }
  }));
}

function loadData() {
  const breeds = readCsv('BREEDS.csv').map(b => ({
    id: randomUUID(),
    breed_name: b.breed,
    size_class: b.size,
    body_type: b.body_type,
    coat_type: b.coat_type,
    energy_level: b.energy,
    weakness_group: b.weakness_group,
    lifespan_class: b.lifespan,
    skull_type: b.skull_type,
    climate: b.climate,
    function_group: b.function_group
  }));

  const traitConditions = [
    ...normalizeTraitRows(readCsv('SIZE_CONDITIONS.csv'), 'size', 'size'),
    ...normalizeTraitRows(readCsv('BODYTYPE_CONDITIONS.csv'), 'body_type', 'body_type'),
    ...normalizeTraitRows(readCsv('COATTYPE_CONDITIONS.csv'), 'coat_type', 'coat_type'),
    ...normalizeTraitRows(readCsv('ENERGY_CONDITIONS.csv'), 'energy', 'energy'),
    ...normalizeTraitRows(readCsv('SKULLTYPE_CONDITIONS.csv'), 'skull_type', 'skull_type'),
    ...normalizeTraitRows(readCsv('CLIMATE_CONDITIONS.csv'), 'climate', 'climate'),
    ...normalizeTraitRows(readCsv('LIFESPAN_CONDITIONS.csv'), 'lifespan', 'lifespan'),
    ...normalizeTraitRows(readCsv('WEAKNESSGROUP_CONDITIONS.csv'), 'weakness_group', 'weakness_group'),
    ...normalizeTraitRows(readCsv('FUNCTIONGROUP_CONDITIONS.csv'), 'function_group', 'function_group')
  ];

  const breedConditions = readCsv('BREED_CONDITIONS.csv').map(r => ({
    consideration_type: 'management_consideration',
    breed_name: r.breed,
    condition_name: r.condition,
    condition_key: conditionKey(r.condition),
    prevalence: parsePercent(r.prevalence),
    sample_population: r.sample_population,
    sample_size: parseInt(r.sample_size, 10),
    source_name: r.source_name,
    source_quote: r.source_quote,
    source_url: r.source_url,
    year: parseInt(r.year, 10),
    confidence_level: r.confidence_level,
    evidence: {
      prevalence: parsePercent(r.prevalence),
      sample_population: r.sample_population,
      sample_size: parseInt(r.sample_size, 10),
      source_name: r.source_name,
      source_quote: r.source_quote,
      source_url: r.source_url
    }
  }));

  const traitInteractions = readCsv('TRAIT_INTERACTIONS.csv').map(r => ({
    trait_a: r.trait_a,
    trait_b: r.trait_b,
    condition_name: r.condition,
    condition_key: conditionKey(r.condition),
    interaction: r.interaction,
    factor: parseFloat(r.factor),
    reason: r.reason,
    source: r.source
  }));

  const traitBenefits = readCsv('TRAIT_BENEFITS.csv').map(r => ({
    trait_a: r.trait_a,
    trait_b: r.trait_b,
    condition_name: r.condition,
    condition_key: conditionKey(r.condition),
    reduction_factor: parseFloat(r.reduction_factor),
    reason: r.reason,
    source: r.source
  }));

  const conditionIngredients = readCsv('CONDITION_INGREDIENTS.csv').map(r => ({
    condition_name: r.condition,
    condition_key: conditionKey(r.condition),
    nutrient_name: r.ingredient_name,
    ingredient_name: r.ingredient_name,
    ingredient_key: ingredientKey(r.ingredient_name),
    recommended_daily_dose: parseFloat(r.recommended_daily_dose),
    dose_unit: r.dose_unit,
    dose_basis: 'fixed',
    dose_min: parseFloat(r.recommended_daily_dose),
    dose_max: parseFloat(r.recommended_daily_dose),
    unit: r.dose_unit,
    source_name: r.source_name,
    source_quote: r.source_quote,
    source_url: r.source_url,
    priority_rank: parseInt(r.priority_rank, 10)
  }));

  const ingredientEvidence = readCsv('INGREDIENT_EVIDENCE.csv').map(r => ({
    ingredient_name: r.ingredient_name,
    ingredient_key: ingredientKey(r.ingredient_name),
    source_name: r.source_name,
    source_quote: r.source_quote,
    source_url: r.source_url,
    year: parseInt(r.year, 10),
    evidence_level: r.evidence_level || null,
    mechanism: r.mechanism || null
  }));

  const ingredientMechanisms = readCsv('INGREDIENT_MECHANISMS.csv').map(r => ({
    nutrient_name: r.nutrient_name,
    nutrient_key: ingredientKey(r.nutrient_name),
    ingredient_name: r.ingredient_name,
    ingredient_key: ingredientKey(r.ingredient_name),
    source_product_id: r.source_product_id || null,
    amount_per_serving: parseFloat(r.amount_per_serving || 0),
    unit: r.unit || null,
    mechanism_summary: r.mechanism_summary || null,
    evidence_level: r.evidence_level || null
  }));

  const naturalFoodSources = readCsv('NATURAL_FOOD_SOURCES.csv').map(r => ({
    ingredient_name: r.ingredient_name,
    ingredient_key: ingredientKey(r.ingredient_name),
    food_source: r.food_source,
    amount_per_100g: parseFloat(r.amount_per_100g || 0),
    unit: r.unit,
    bioavailability_notes: r.bioavailability_notes || null
  }));

  const products = buildProductCatalog();
  const productMap = Object.fromEntries(products.map(p => [p.product_id, p]));
  const productIngredients = buildActiveIngredients(products);
  const productFunctions = buildProductFunctions(products);

  const productFeedingRules = readCsv('PRODUCT_FEEDING_RULES.csv').map(r => ({
    product_id: r.product_id,
    product_name: productMap[r.product_id]?.product_name,
    weight_min_kg: parseFloat(r.weight_min_kg || r.min_weight_kg),
    weight_max_kg: parseFloat(r.weight_max_kg || r.max_weight_kg),
    daily_amount: parseFloat(r.daily_amount),
    daily_unit: r.daily_unit
  })).filter(r => r.product_id && productMap[r.product_id]);

  const mixedBreedInteractions = readCsv('MIXED_BREED_INTERACTIONS.csv').map(r => ({
    trait_a: r.trait_a || r.dominant_trait,
    trait_b: r.trait_b || r.suppressed_trait,
    condition_name: r.condition || r.breed_combination,
    condition_key: conditionKey(r.condition || r.breed_combination),
    interaction: r.interaction,
    factor: parseFloat(r.factor || r.suppressed_trait) || 1,
    reason: r.reason,
    source: r.source
  }));

  const traitPurposes = readCsv('TRAIT_PURPOSES.csv').map(r => ({
    trait_category: r.trait_category || r.trait,
    trait_value: r.trait_value || r.trait,
    biological_purpose: r.biological_purpose || r.evolutionary_function,
    advantage_summary: r.advantage_summary || r.biological_advantages,
    adaptive_behavior: r.adaptive_behavior || null,
    original_working_purpose: r.original_working_purpose || null,
    source_name: r.source_name,
    source_quote: r.source_quote,
    source_url: r.source_url
  }));

  const environmentalMatrices = readCsv('ENVIRONMENTAL_MATRICES.csv').map(r => ({
    trait: r.trait,
    environment: r.environment,
    compatibility_score: parseFloat(r.compatibility_score) || null,
    benefits: r.benefits || null,
    management_requirements: r.management_requirements || null,
    scientific_source: r.scientific_source || r.source_name || null
  }));

  const activityRecommendations = readCsv('CONDITION_ACTIVITIES.csv').map(r => ({
    requirement_type: 'lifestyle_requirement',
    condition_name: r.condition,
    condition_key: conditionKey(r.condition),
    activity_name: r.activity_name,
    frequency: r.frequency,
    duration_minutes: parseInt(r.duration_minutes, 10),
    source_name: r.source_name,
    source_quote: r.source_quote,
    source_url: r.source_url
  }));

  const nutrientPriorities = readCsv('NUTRIENT_PRIORITIES.csv').map(r => ({
    condition_name: r.condition,
    condition_key: conditionKey(r.condition),
    nutrient_name: r.nutrient_name,
    nutrient_key: ingredientKey(r.nutrient_name),
    target_dose: parseFloat(r.target_dose || 0),
    target_unit: r.target_unit,
    priority_rank: parseInt(r.priority_rank || '999', 10),
    evidence_level: r.evidence_level || null,
    source_name: r.source_name || null,
    source_quote: r.source_quote || null,
    source_url: r.source_url || null
  }));

  const clinicalEvidenceBase = readCsv('CLINICAL_EVIDENCE_BASE.csv').map(r => ({
    evidence_id: r.evidence_id || randomUUID(),
    domain: r.domain,
    condition_name: r.condition,
    condition_key: conditionKey(r.condition),
    nutrient_or_activity: r.nutrient_or_activity,
    mechanism: r.mechanism,
    evidence_level: r.evidence_level,
    source_name: r.source_name,
    source_quote: r.source_quote,
    source_url: r.source_url,
    year: parseInt(r.year || '0', 10) || null
  }));

  const groomerConditionMap = buildGroomerMap(
    activityRecommendations.map(a => ({ condition_name: a.condition_name, observable_by_groomer: 'true' }))
  );

  const breedAnalysis = {
    breeds,
    traitConditions,
    traitInteractions,
    traitBenefits,
    breedConditions
  };

  const preventativeIngredientAnalysis = {
    conditionIngredients,
    ingredientEvidence,
    ingredientMechanisms,
    naturalFoodSources,
    nutrientPriorities,
    clinicalEvidenceBase,
    activityRecommendations
  };

  const productPortfolio = {
    products,
    productIngredients,
    productFunctions,
    productFeedingRules
  };

  return {
    breeds,
    traitConditions,
    traitInteractions,
    traitBenefits,
    breedConditions,
    mixedBreedMatrix: readCsv('MIXED_BREED_MATRIX.csv').map(r => ({
      breed_a: r.breed_a || r.primary_breed,
      breed_b: r.breed_b || r.secondary_breed,
      condition_name: r.condition || r.inherited_traits,
      condition_key: conditionKey(r.condition || r.inherited_traits),
      factor: parseFloat(r.factor || r.breed_split_pct) || 1,
      source_name: r.source_name,
      source_quote: r.source_quote,
      source_url: r.source_url
    })),
    mixedBreedInteractions,
    traitPurposes,
    environmentalMatrices,
    conditionIngredients,
    ingredientEvidence,
    ingredientMechanisms,
    naturalFoodSources,
    nutrientPriorities,
    clinicalEvidenceBase,
    products,
    productIngredients,
    productFunctions,
    productFeedingRules,
    productRotationLogic: [],
    productPreferences: products.filter(p => p.brand?.includes('Wagtopia')).slice(0, 5).map(p => ({
      id: p.id,
      product_id: p.id,
      priority_score: 1.2
    })),
    activityRecommendations,
    groomerConditionMap,

    // Explicit domain-level database split for deterministic platform auditing.
    breedAnalysis,
    preventativeIngredientAnalysis,
    productPortfolio
  };
}

function componentIngredientKey(name) {
  const key = ingredientKey(name);
  if (key === 'epa_dha') return 'omega_3';
  if (key === 'brady_yeast_probiotics') return 'probiotics';
  if (key === 'joint_health_formula') return 'glucosamine';
  if (key === 'lf_mag_300') return 'immunity';
  return key;
}

function componentDisplayName(name) {
  if (name === 'EPA+DHA') return 'Omega-3';
  if (name === 'Brady Yeast Probiotics') return 'Probiotics';
  if (name === 'Joint Health Formula') return 'Glucosamine';
  return name;
}

function macroDetailFromComponents(components) {
  const detail = {};
  for (const c of components || []) {
    const name = (c.component_name || '').toLowerCase();
    if (name.includes('crude protein') || name === 'protein') {
      detail.protein_pct = parseFloat(c.value);
    } else if (name.includes('crude fat') || name === 'fat') {
      detail.fat_pct = parseFloat(c.value);
    } else if (name.includes('calcium')) {
      detail.calcium_pct = parseFloat(c.value);
    } else if (name.includes('phosphorus')) {
      detail.phosphorus_pct = parseFloat(c.value);
    } else if (name.includes('epa') || name.includes('dha') || name.includes('omega')) {
      detail.omega_pct = parseFloat(c.value);
    }
  }
  return detail;
}

function categoryToProductType(category) {
  switch (category) {
    case 'Homestyle Bakery': return 'homestyle_bakery';
    case 'All-Natural Treats': return 'treat';
    case 'Snacks': return 'snack';
    case 'Fresh Food': return 'fresh_food';
    case 'Nutritional Supplements': return 'supplement';
    case 'Staple Food': return 'staple_food';
    case 'STAPLE_FOOD': return 'kibble';
    case 'SUPPLEMENT': return 'supplement';
    case 'TREAT': return 'treat';
    case 'HOMESTYLE_BAKERY': return 'homestyle_bakery';
    default: return (category || '').toLowerCase().replace(/\s+/g, '_');
  }
}

function buildProductCatalog() {
  const catalog = readCsv('PRODUCT_CATALOG.csv').filter(p => p.status === 'active' || !p.status);
  const pricing = Object.fromEntries(
    readCsv('PRODUCT_PRICING.csv').map(p => [p.product_id, p])
  );
  const treatById = Object.fromEntries(readCsv('EXT_TREATS_BAKERY.csv').map(r => [r.product_id, r]));
  const suppById = Object.fromEntries(readCsv('EXT_SUPPLEMENTS.csv').map(r => [r.product_id, r]));
  const componentsByProduct = {};
  for (const row of readCsv('PRODUCT_COMPONENTS.csv')) {
    (componentsByProduct[row.product_id] = componentsByProduct[row.product_id] || []).push(row);
  }

  return catalog.map(row => {
    const priceRow = pricing[row.product_id] || {};
    const listPriceRmb = parseFloat(priceRow.list_price_rmb) || parseFloat(priceRow.list_price_usd) || 0;
    const packageUnits = parseFloat(priceRow.package_units) || 1;
    const category = row.category;
    const extension = treatById[row.product_id] || suppById[row.product_id] || {};
    const macros = macroDetailFromComponents(componentsByProduct[row.product_id]);

    return {
      id: row.product_id,
      product_id: row.product_id,
      product_name: row.product_name,
      brand: row.brand,
      category,
      subcategory: row.subcategory,
      product_type: categoryToProductType(category),
      status: row.status || 'active',
      image_url: row.image_url || null,
      purchase_url: row.purchase_url || null,
      list_price_rmb: listPriceRmb,
      price: listPriceRmb,
      currency: priceRow.list_price_rmb ? 'RMB' : 'USD',
      package_units: packageUnits,
      unit_cost_per_bag: packageUnits > 0
        ? Math.round((listPriceRmb / packageUnits) * 100) / 100
        : listPriceRmb,
      unit_type: priceRow.unit_label || 'unit',
      shelf_life_days: parseInt(extension.shelf_life_days, 10) || 365,
      storage_method: extension.storage_method || null,
      protein_pct: macros.protein_pct,
      fat_pct: macros.fat_pct,
      calcium_pct: macros.calcium_pct,
      phosphorus_pct: macros.phosphorus_pct,
      category_detail: { ...extension, ...macros },
      components: componentsByProduct[row.product_id] || []
    };
  });
}

function buildActiveIngredients(products) {
  const idSet = new Set(products.map(p => p.id));
  const grouped = {};
  return readCsv('PRODUCT_COMPONENTS.csv')
    .filter(r => idSet.has(r.product_id) && r.component_type === 'active_ingredient')
    .map((r) => {
      grouped[r.product_id] = (grouped[r.product_id] || 0) + 1;
      const ingredientKeyValue = componentIngredientKey(r.component_name);
      return {
        id: `${r.product_id}-${ingredientKeyValue}`,
        product_id: r.product_id,
        product_name: products.find(p => p.id === r.product_id)?.product_name,
        ingredient_name: componentDisplayName(r.component_name),
        ingredient_key: ingredientKeyValue,
        amount_per_unit: parseFloat(r.value) || 0,
        unit: r.unit || '%',
        evidence_level: r.evidence_level,
        ingredient_order_rank: grouped[r.product_id]
      };
    });
}

function buildProductFunctions(products) {
  const idSet = new Set(products.map(p => p.id));
  return readCsv('PRODUCT_FUNCTIONS.csv')
    .filter(r => idSet.has(r.product_id))
    .map(r => ({
      product_id: r.product_id,
      function: r.function,
      confidence: r.confidence
    }));
}

module.exports = { loadData, readCsv, DATA_DIR };
