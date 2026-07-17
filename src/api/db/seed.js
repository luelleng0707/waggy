'use strict';

const { randomUUID } = require('crypto');
function id() { return randomUUID(); }

const breeds = [
  { id: id(), breed_name: 'Labrador', size: 'large', body_type: 'athletic_heavy', coat_type: 'double_coat', energy_type: 'high', weakness_group: 'joint_heavy', lifespan_class: 'medium_long' },
  { id: id(), breed_name: 'Golden Retriever', size: 'large', body_type: 'athletic_heavy', coat_type: 'double_coat', energy_type: 'high', weakness_group: 'joint_heavy', lifespan_class: 'medium_long' },
  { id: id(), breed_name: 'Husky', size: 'medium', body_type: 'athletic_lean', coat_type: 'double_coat', energy_type: 'very_high', weakness_group: 'joint_moderate', lifespan_class: 'medium' },
  { id: id(), breed_name: 'Siberian Husky', size: 'medium', body_type: 'athletic_lean', coat_type: 'double_coat', energy_type: 'very_high', weakness_group: 'joint_moderate', lifespan_class: 'medium' },
  { id: id(), breed_name: 'Corgi', size: 'small', body_type: 'spine_heavy', coat_type: 'double_coat', energy_type: 'high', weakness_group: 'spine_heavy', lifespan_class: 'long' },
  { id: id(), breed_name: 'Pembroke Welsh Corgi', size: 'small', body_type: 'spine_heavy', coat_type: 'double_coat', energy_type: 'high', weakness_group: 'spine_heavy', lifespan_class: 'long' },
  { id: id(), breed_name: 'Samoyed', size: 'large', body_type: 'athletic_heavy', coat_type: 'double_coat', energy_type: 'high', weakness_group: 'joint_heavy', lifespan_class: 'medium_long' },
  { id: id(), breed_name: 'German Shepherd', size: 'large', body_type: 'athletic_heavy', coat_type: 'double_coat', energy_type: 'high', weakness_group: 'joint_heavy', lifespan_class: 'medium' },
  { id: id(), breed_name: 'French Bulldog', size: 'small', body_type: 'compact_brachy', coat_type: 'short_coat', energy_type: 'low', weakness_group: 'respiratory_skin', lifespan_class: 'medium' },
  { id: id(), breed_name: 'Shih Tzu', size: 'small', body_type: 'compact', coat_type: 'long_coat', energy_type: 'low', weakness_group: 'eye_skin', lifespan_class: 'long' }
];

const traitRisks = [
  { trait_type: 'size', trait_value: 'large', condition_name: 'hip_dysplasia', prevalence: 0.12, source_name: 'OFA Registry', source_quote: 'Large breeds show elevated hip dysplasia lifetime prevalence.', source_url: 'https://ofa.org/diseases/hip-dysplasia' },
  { trait_type: 'size', trait_value: 'large', condition_name: 'joint_sensitivity', prevalence: 0.08, source_name: 'Large Breed Study', source_quote: 'Large dogs accumulate joint stress earlier.', source_url: 'https://example.com/large-joint' },
  { trait_type: 'body_type', trait_value: 'athletic_heavy', condition_name: 'ccl_injury', prevalence: 0.07, source_name: 'Orthopedic Review', source_quote: 'Athletic heavy builds show increased CCL injury rates.', source_url: 'https://example.com/ccl' },
  { trait_type: 'body_type', trait_value: 'spine_heavy', condition_name: 'ivdd', prevalence: 0.18, source_name: 'Spine Research', source_quote: 'Long-backed breeds carry high IVDD predisposition.', source_url: 'https://example.com/ivdd' },
  { trait_type: 'weakness_group', trait_value: 'joint_heavy', condition_name: 'elbow_dysplasia', prevalence: 0.09, source_name: 'OFA Registry', source_quote: 'Joint-heavy breeds show elbow dysplasia clustering.', source_url: 'https://example.com/elbow' },
  { trait_type: 'weakness_group', trait_value: 'joint_heavy', condition_name: 'hip_dysplasia', prevalence: 0.11, source_name: 'OFA Registry', source_quote: 'Joint-heavy weakness group correlates with hip issues.', source_url: 'https://ofa.org/diseases/hip-dysplasia' },
  { trait_type: 'coat_type', trait_value: 'double_coat', condition_name: 'skin_barrier', prevalence: 0.06, source_name: 'Dermatology Journal', source_quote: 'Double coats may trap moisture causing skin issues.', source_url: 'https://example.com/skin' },
  { trait_type: 'weakness_group', trait_value: 'eye_skin', condition_name: 'tear_stains', prevalence: 0.14, source_name: 'Brachy Eye Study', source_quote: 'Eye-area breeds frequently develop tear staining.', source_url: 'https://example.com/tear' },
  { trait_type: 'weakness_group', trait_value: 'respiratory_skin', condition_name: 'skin_fold_dermatitis', prevalence: 0.16, source_name: 'Brachy Health', source_quote: 'Skin fold breeds show elevated dermatitis.', source_url: 'https://example.com/folds' },
  { trait_type: 'energy_type', trait_value: 'high', condition_name: 'joint_wear', prevalence: 0.05, source_name: 'Activity Study', source_quote: 'High energy dogs show earlier joint wear patterns.', source_url: 'https://example.com/wear' }
];

const traitBenefits = [
  { trait_a: 'athletic_lean', trait_b: 'spine_heavy', condition_name: 'ivdd', reduction_factor: 0.70, source_name: 'Hybrid Morphology Study', source_quote: 'Athletic lean build reduces IVDD expression in long-backed mixes.', source_url: 'https://example.com/ivdd-benefit' },
  { trait_a: 'double_coat', trait_b: 'high', condition_name: 'skin_barrier', reduction_factor: 0.85, source_name: 'Coat Health Review', source_quote: 'Active double-coated dogs show better skin oil distribution.', source_url: 'https://example.com/coat-benefit' }
];

const breedObservedRisks = [
  { breed_name: 'Labrador', condition_name: 'hip_dysplasia', prevalence: 0.21, source_name: 'OFA Registry', source_quote: 'Labradors show elevated lifetime hip dysplasia prevalence.', source_url: 'https://ofa.org/diseases/hip-dysplasia' },
  { breed_name: 'Labrador', condition_name: 'obesity', prevalence: 0.18, source_name: 'AKC Health', source_quote: 'Labradors are among breeds with highest obesity risk.', source_url: 'https://example.com/obesity' },
  { breed_name: 'Golden Retriever', condition_name: 'hip_dysplasia', prevalence: 0.20, source_name: 'OFA Registry', source_quote: 'Golden Retrievers demonstrate significant hip dysplasia rates.', source_url: 'https://ofa.org/diseases/hip-dysplasia' },
  { breed_name: 'Golden Retriever', condition_name: 'skin_barrier', prevalence: 0.16, source_name: 'Dermatology Journal', source_quote: 'Goldens frequently present with atopic dermatitis.', source_url: 'https://example.com/golden-skin' },
  { breed_name: 'Husky', condition_name: 'hip_dysplasia', prevalence: 0.18, source_name: 'OFA Registry', source_quote: 'Northern breeds show moderate hip dysplasia prevalence.', source_url: 'https://ofa.org/diseases/hip-dysplasia' },
  { breed_name: 'Husky', condition_name: 'cataracts', prevalence: 0.12, source_name: 'ACVO Registry', source_quote: 'Huskies carry elevated hereditary cataract risk.', source_url: 'https://example.com/husky-eye' },
  { breed_name: 'Siberian Husky', condition_name: 'hip_dysplasia', prevalence: 0.18, source_name: 'OFA Registry', source_quote: 'Siberian Huskies show moderate hip dysplasia rates.', source_url: 'https://ofa.org/diseases/hip-dysplasia' },
  { breed_name: 'Corgi', condition_name: 'ivdd', prevalence: 0.30, source_name: 'Orthopedic Foundation', source_quote: 'Corgis carry high intervertebral disc disease risk.', source_url: 'https://example.com/corgi-ivdd' },
  { breed_name: 'Corgi', condition_name: 'hip_dysplasia', prevalence: 0.22, source_name: 'OFA Registry', source_quote: 'Corgis show elevated hip dysplasia relative to size.', source_url: 'https://ofa.org/diseases/hip-dysplasia' },
  { breed_name: 'Samoyed', condition_name: 'hip_dysplasia', prevalence: 0.19, source_name: 'OFA Registry', source_quote: 'Hip dysplasia remains common in large northern breeds.', source_url: 'https://ofa.org/diseases/hip-dysplasia' },
  { breed_name: 'Samoyed', condition_name: 'diabetes', prevalence: 0.08, source_name: 'Breed Health Survey', source_quote: 'Samoyeds show above-average diabetes prevalence.', source_url: 'https://example.com/samoyed-diabetes' }
];

const mixedBreedBaselines = [
  { breed_a: 'Husky', breed_b: 'Corgi', condition_name: 'hip_dysplasia', prevalence: 0.16, source_name: 'Mixed Breed Study', source_quote: 'Husky-Corgi mixes show intermediate hip dysplasia rates.', source_url: 'https://example.com/husky-corgi-hip' },
  { breed_a: 'Husky', breed_b: 'Corgi', condition_name: 'ivdd', prevalence: 0.14, source_name: 'Mixed Breed Study', source_quote: 'IVDD risk moderated in Husky-Corgi crosses.', source_url: 'https://example.com/husky-corgi-ivdd' },
  { breed_a: 'Golden Retriever', breed_b: 'Labrador', condition_name: 'hip_dysplasia', prevalence: 0.20, source_name: 'Retriever Cross Study', source_quote: 'Goldador crosses maintain high hip dysplasia prevalence.', source_url: 'https://example.com/goldador' }
];

const conditionIngredients = [
  { condition_name: 'hip_dysplasia', ingredient_name: 'glucosamine', dose_basis: 'mg_per_kg', dose_min: 15, dose_max: 30, unit: 'mg', source_name: 'Vet Joint Research', source_quote: 'Glucosamine at 15-30mg/kg improves mobility scores.', source_url: 'https://example.com/glucosamine' },
  { condition_name: 'hip_dysplasia', ingredient_name: 'omega_3', dose_basis: 'mg_per_kg', dose_min: 10, dose_max: 20, unit: 'mg', source_name: 'Nutraceutical Science', source_quote: 'Omega-3 reduces inflammatory markers in joints.', source_url: 'https://example.com/omega3' },
  { condition_name: 'ivdd', ingredient_name: 'glucosamine', dose_basis: 'mg_per_kg', dose_min: 12, dose_max: 25, unit: 'mg', source_name: 'Spine Support Study', source_quote: 'Glucosamine supports spinal joint health.', source_url: 'https://example.com/ivdd-gluc' },
  { condition_name: 'cataracts', ingredient_name: 'lutein', dose_basis: 'fixed_mg', dose_min: 10, dose_max: 20, unit: 'mg', source_name: 'Ocular Nutrition', source_quote: 'Lutein supports retinal antioxidant defense.', source_url: 'https://example.com/lutein' },
  { condition_name: 'tear_stains', ingredient_name: 'lutein', dose_basis: 'fixed_mg', dose_min: 5, dose_max: 15, unit: 'mg', source_name: 'Eye Care Review', source_quote: 'Lutein may reduce oxidative tear staining.', source_url: 'https://example.com/tear-lutein' },
  { condition_name: 'skin_barrier', ingredient_name: 'omega_3', dose_basis: 'mg_per_kg', dose_min: 15, dose_max: 25, unit: 'mg', source_name: 'Dermatology Nutrition', source_quote: 'Omega-3 improves skin barrier in atopic dogs.', source_url: 'https://example.com/skin-omega' },
  { condition_name: 'obesity', ingredient_name: 'probiotics', dose_basis: 'fixed_mg', dose_min: 200, dose_max: 500, unit: 'mg', source_name: 'Gut Health Review', source_quote: 'Probiotics support healthy weight metabolism.', source_url: 'https://example.com/probiotics' },
  { condition_name: 'joint_sensitivity', ingredient_name: 'collagen', dose_basis: 'mg_per_kg', dose_min: 5, dose_max: 10, unit: 'mg', source_name: 'Connective Tissue Study', source_quote: 'Collagen peptides support tendon maintenance.', source_url: 'https://example.com/collagen' }
];

const ingredientEvidence = [
  { ingredient_name: 'glucosamine', source_name: 'Vet Joint Research', source_quote: 'Daily glucosamine improved mobility in 67% of dogs over 90 days.', source_url: 'https://example.com/glucosamine-evidence' },
  { ingredient_name: 'omega_3', source_name: 'Nutraceutical Science', source_quote: 'Omega-3 fatty acids reduce inflammatory markers in canine studies.', source_url: 'https://example.com/omega3-evidence' },
  { ingredient_name: 'lutein', source_name: 'Ocular Nutrition Journal', source_quote: 'Lutein supports retinal health and reduces oxidative eye damage.', source_url: 'https://example.com/lutein-evidence' },
  { ingredient_name: 'probiotics', source_name: 'Gut Health Review', source_quote: 'Probiotic strains improve digestive resilience and immune modulation.', source_url: 'https://example.com/probiotic-evidence' },
  { ingredient_name: 'collagen', source_name: 'Connective Tissue Study', source_quote: 'Collagen peptides support tendon and ligament maintenance.', source_url: 'https://example.com/collagen-evidence' }
];

const products = [
  { id: id(), product_name: 'Wagtopia Joint Support Chew', brand: 'Wagtopia', product_type: 'supplement', package_units: 60, shelf_life_days: 365, price: 38 },
  { id: id(), product_name: 'Hip & Joint Advanced', brand: 'Wagtopia Wellness', product_type: 'supplement', package_units: 30, shelf_life_days: 365, price: 42 },
  { id: id(), product_name: 'Omega-3 Fish Oil Capsule', brand: 'PurePet', product_type: 'supplement', package_units: 90, shelf_life_days: 365, price: 28 },
  { id: id(), product_name: 'Eye Care Lutein Chew', brand: 'ClearEye', product_type: 'supplement', package_units: 60, shelf_life_days: 365, price: 26 },
  { id: id(), product_name: 'Skin Barrier Omega Bites', brand: 'DermaCoat', product_type: 'supplement', package_units: 45, shelf_life_days: 270, price: 30 },
  { id: id(), product_name: 'Probiotic Daily Chew', brand: 'GutGuard', product_type: 'supplement', package_units: 60, shelf_life_days: 365, price: 30 },
  { id: id(), product_name: 'Wagtopia Silk Kibble', brand: 'Wagtopia', product_type: 'kibble', package_units: 1, shelf_life_days: 180, price: 58 },
  { id: id(), product_name: 'Premium Joint Formula Kibble', brand: 'Wagtopia', product_type: 'kibble', package_units: 1, shelf_life_days: 180, price: 72 },
  { id: id(), product_name: 'Freeze-Dried Duck Treats', brand: 'Wagtopia Bakery', product_type: 'treat', package_units: 40, shelf_life_days: 30, price: 15 },
  { id: id(), product_name: 'Frozen Yogurt Bites', brand: 'Wagtopia Bakery', product_type: 'treat', package_units: 24, shelf_life_days: 14, price: 10 },
  { id: id(), product_name: 'Basic Chicken Blend Kibble', brand: 'NutriPaw', product_type: 'kibble', package_units: 1, shelf_life_days: 150, price: 45 }
];

const productIngredients = [
  { product_name: 'Wagtopia Joint Support Chew', ingredient_name: 'glucosamine', amount_per_unit: 250, unit: 'mg' },
  { product_name: 'Wagtopia Joint Support Chew', ingredient_name: 'omega_3', amount_per_unit: 100, unit: 'mg' },
  { product_name: 'Hip & Joint Advanced', ingredient_name: 'glucosamine', amount_per_unit: 300, unit: 'mg' },
  { product_name: 'Hip & Joint Advanced', ingredient_name: 'collagen', amount_per_unit: 100, unit: 'mg' },
  { product_name: 'Omega-3 Fish Oil Capsule', ingredient_name: 'omega_3', amount_per_unit: 300, unit: 'mg' },
  { product_name: 'Eye Care Lutein Chew', ingredient_name: 'lutein', amount_per_unit: 15, unit: 'mg' },
  { product_name: 'Skin Barrier Omega Bites', ingredient_name: 'omega_3', amount_per_unit: 200, unit: 'mg' },
  { product_name: 'Probiotic Daily Chew', ingredient_name: 'probiotics', amount_per_unit: 250, unit: 'mg' },
  { product_name: 'Wagtopia Silk Kibble', ingredient_name: 'omega_3', amount_per_unit: 50, unit: 'mg' },
  { product_name: 'Premium Joint Formula Kibble', ingredient_name: 'glucosamine', amount_per_unit: 80, unit: 'mg' },
  { product_name: 'Premium Joint Formula Kibble', ingredient_name: 'omega_3', amount_per_unit: 65, unit: 'mg' },
  { product_name: 'Basic Chicken Blend Kibble', ingredient_name: 'omega_3', amount_per_unit: 30, unit: 'mg' },
  { product_name: 'Freeze-Dried Duck Treats', ingredient_name: 'omega_3', amount_per_unit: 20, unit: 'mg' }
];

const activityRecommendations = [
  { condition_name: 'hip_dysplasia', activity_name: 'Hydrotherapy sessions', frequency: 'weekly', duration_minutes: 30 },
  { condition_name: 'ivdd', activity_name: 'Core stability exercises', frequency: 'daily', duration_minutes: 15 },
  { condition_name: 'skin_barrier', activity_name: 'Post-bath coat conditioning', frequency: 'weekly', duration_minutes: 20 },
  { condition_name: 'tear_stains', activity_name: 'Daily eye area cleaning', frequency: 'daily', duration_minutes: 5 },
  { condition_name: 'obesity', activity_name: 'Structured leash walks', frequency: 'daily', duration_minutes: 45 }
];

const GROOMER_CONDITION_MAP = {
  tear_stains: 'tear_stains',
  limping: 'hip_dysplasia',
  limps: 'hip_dysplasia',
  itching: 'skin_barrier',
  scratching: 'skin_barrier',
  dry_skin: 'skin_barrier',
  eye_discharge: 'cataracts',
  eyes: 'tear_stains',
  bad_breath: 'obesity',
  teeth: 'obesity',
  ears: 'skin_barrier',
  shedding: 'skin_barrier'
};

function getSeedData() {
  const productMap = Object.fromEntries(products.map(p => [p.product_name, p]));
  const pi = productIngredients.map(row => ({
    id: id(),
    product_id: productMap[row.product_name].id,
    ...row
  }));

  return {
    breeds,
    traitRisks,
    traitBenefits,
    breedObservedRisks,
    mixedBreedBaselines,
    conditionIngredients,
    ingredientEvidence,
    products,
    productIngredients: pi,
    productRotationLogic: [],
    productPreferences: products.slice(0, 3).map(p => ({ id: id(), product_id: p.id, priority_score: 1.2 })),
    activityRecommendations,
    groomerConditionMap: GROOMER_CONDITION_MAP
  };
}

module.exports = { getSeedData, GROOMER_CONDITION_MAP };
