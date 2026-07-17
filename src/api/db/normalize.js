'use strict';

function conditionKey(name) {
  return (name || '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_|_$/g, '');
}

function ingredientKey(name) {
  return (name || '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_|_$/g, '');
}

function productTypeKey(type) {
  return (type || '').toLowerCase().replace(/\s+/g, '_');
}

function sizeToWeightKg(sizeClass) {
  const map = { Toy: 4, Small: 10, Medium: 20, Large: 30, Giant: 45 };
  return map[sizeClass] || 20;
}

function collectBreedTraitValues(breed) {
  return [
    breed.size_class,
    breed.body_type,
    breed.coat_type,
    breed.energy_level,
    breed.weakness_group,
    breed.lifespan_class,
    breed.chest_shape,
    breed.joint_load_class,
    breed.metabolism_class
  ].filter(Boolean);
}

function collectProfileTraits(breeds) {
  const set = new Set();
  for (const breed of breeds) {
    for (const v of collectBreedTraitValues(breed)) set.add(v);
  }
  return set;
}

module.exports = {
  conditionKey,
  ingredientKey,
  productTypeKey,
  sizeToWeightKg,
  collectBreedTraitValues,
  collectProfileTraits
};
