'use strict';

const db = require('../api/db/queries');
const { conditionKey } = require('../api/db/normalize');

function collectEvidence(risks, ingredients) {
  const evidence = [];
  const seen = new Set();

  for (const risk of risks) {
    if (risk.source) {
      const key = risk.source.source_url + risk.source.source_quote;
      if (!seen.has(key)) {
        seen.add(key);
        evidence.push({
          type: 'breed',
          condition: risk.condition_name,
          breed: risk.source.breed,
          source_name: risk.source.source_name,
          quote: risk.source.source_quote,
          url: risk.source.source_url
        });
      }
    }
  }

  for (const ing of ingredients) {
    const key = ing.source_url + ing.evidence_quote;
    if (!seen.has(key)) {
      seen.add(key);
      evidence.push({
        type: 'ingredient',
        condition: ing.ingredient_name,
        breed: null,
        source_name: ing.source_name,
        quote: ing.evidence_quote,
        url: ing.source_url
      });
    }
  }

  return evidence;
}

function getEvidenceForCondition(conditionName) {
  const s = db.getStore();
  const key = conditionKey(conditionName);
  const results = [];

  for (const obs of s.breedConditions) {
    if (obs.condition_key === key || obs.condition_name.toLowerCase() === conditionName.toLowerCase()) {
      results.push({ type: 'breed_observed', ...obs });
    }
  }
  for (const ci of s.conditionIngredients) {
    if (ci.condition_key === key || ci.condition_name.toLowerCase() === conditionName.toLowerCase()) {
      results.push({ type: 'ingredient_dose', ...ci });
    }
  }
  return results;
}

function getProductsForCondition(conditionName, weightKg = 20) {
  const { mapIngredients } = require('./ingredientEngine');
  const { matchProducts } = require('./productEngine');
  const fakeRisk = [{ condition_name: conditionName, condition_key: conditionKey(conditionName), risk_percent: 50 }];
  const ings = mapIngredients(fakeRisk, weightKg);
  return matchProducts(ings, [], weightKg);
}

module.exports = { collectEvidence, getEvidenceForCondition, getProductsForCondition };
