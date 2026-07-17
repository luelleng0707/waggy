'use strict';

const db = require('../api/db/queries');

const BREED_ALIASES = {
  labrador: 'Labrador Retriever',
  golden: 'Golden Retriever',
  husky: 'Siberian Husky',
  corgi: 'Pembroke Welsh Corgi',
  samoyed: 'Samoyed',
  poodle: 'Poodle',
  beagle: 'Beagle',
  pug: 'Pug',
  dachshund: 'Smooth Dachshund',
  'german shepherd': 'German Shepherd Dog',
  'french bulldog': 'French Bulldog',
  'border collie': 'Border Collie',
  'shiba inu': 'Shiba Inu',
  maltese: 'Maltese'
};

function resolveBreeds(breedNames) {
  const expanded = (breedNames || [])
    .flatMap(name => String(name || '')
      .replace(/\bmix(ed)?\b/gi, '')
      .split(/[x×,/+&]| and /i)
      .map(s => s.trim())
      .filter(Boolean));
  const input = expanded.length ? expanded : (breedNames || []);

  const resolved = db.getBreeds(input);
  if (resolved.length) return resolved;

  const aliased = input.map(name => {
    const key = (name || '').toLowerCase();
    return BREED_ALIASES[key] || name;
  });
  return db.getBreeds(aliased);
}

module.exports = { resolveBreeds, BREED_ALIASES };
