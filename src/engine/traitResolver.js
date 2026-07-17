'use strict';

const db = require('../api/db/queries');

function collectTraitRisks(breeds) {
  const all = [];
  for (const breed of breeds) {
    const risks = db.getTraitRisksForBreed(breed);
    for (const r of risks) {
      all.push({ ...r, source_breed: breed.breed_name });
    }
  }
  return all;
}

module.exports = { collectTraitRisks };
