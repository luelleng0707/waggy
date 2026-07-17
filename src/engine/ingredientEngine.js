'use strict';

const db = require('../api/db/queries');
const { calculateDose } = require('./dosageEngine');

function mapIngredients(risks, weightKg) {
  const ingredientMap = new Map();

  // Use the full evaluated risk set so lower-ranked but clinically relevant
  // conditions (e.g., hip dysplasia in mixed profiles) are not dropped.
  for (const risk of risks) {
    const links = db.getConditionIngredients(risk.condition_key || risk.condition_name);
    for (const link of links) {
      const dose = calculateDose(link, weightKg);
      const evidence = db.getIngredientEvidence(link.ingredient_key || link.ingredient_name);
      const mechanisms = db.getIngredientMechanisms(link.ingredient_key || link.ingredient_name);
      const key = link.ingredient_key || link.ingredient_name;
      if (!ingredientMap.has(key)) {
        ingredientMap.set(key, {
          ingredient_name: link.ingredient_name,
          ingredient_key: key,
          for_conditions: [],
          daily_dose: dose.daily,
          monthly_dose: dose.monthly,
          yearly_dose: dose.yearly,
          unit: link.dose_unit || link.unit,
          dose_basis: link.dose_basis,
          evidence_quote: evidence?.source_quote || link.source_quote,
          source_name: evidence?.source_name || link.source_name,
          source_url: evidence?.source_url || link.source_url,
          mechanism_summary: mechanisms?.[0]?.mechanism_summary || evidence?.mechanism || null
        });
      }
      const ing = ingredientMap.get(key);
      const cond = risk.condition_name || risk.condition_key;
      if (!ing.for_conditions.includes(cond)) ing.for_conditions.push(cond);
      ing.daily_dose = Math.max(ing.daily_dose, dose.daily);
      ing.monthly_dose = ing.daily_dose * 30;
      ing.yearly_dose = ing.daily_dose * 365;
    }
  }

  return [...ingredientMap.values()].sort((a, b) => b.daily_dose - a.daily_dose);
}

module.exports = { mapIngredients };
