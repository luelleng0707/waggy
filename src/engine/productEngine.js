'use strict';

const db = require('../api/db/queries');
const { ingredientKey } = require('../api/db/normalize');

const INGREDIENT_PRODUCT_TYPES = new Set([
  'supplement', 'treat', 'homestyle_bakery', 'fresh_food', 'staple_food', 'kibble'
]);

const INGREDIENT_KEY_ALIASES = {
  omega_3: ['omega_3', 'epa_dha'],
  probiotics: ['probiotics', 'brady_yeast_probiotics'],
  glucosamine: ['glucosamine', 'joint_health_formula'],
  immunity: ['immunity', 'lf_mag_300']
};

const COMPATIBLE_UNITS = {
  mg: ['mg'],
  g: ['g', 'mg'],
  '%': ['%'],
  capsules: ['capsules', 'capsule'],
  'billion cfu': ['billion cfu', 'cfu']
};

function ingredientKeysMatch(targetKey, productKey) {
  if (targetKey === productKey) return true;
  for (const aliases of Object.values(INGREDIENT_KEY_ALIASES)) {
    if (aliases.includes(targetKey) && aliases.includes(productKey)) return true;
  }
  return false;
}

function unitsCompatible(targetUnit, productUnit) {
  const t = String(targetUnit || '').toLowerCase().trim();
  const p = String(productUnit || '').toLowerCase().trim();
  if (!t || !p) return false;
  if (t === p) return true;
  const allowed = COMPATIBLE_UNITS[t];
  return allowed ? allowed.includes(p) : false;
}

function computeCoverage(dailyDose, amountPerUnit, targetUnit, productUnit) {
  if (!dailyDose || !amountPerUnit || amountPerUnit <= 0) return 0;
  if (!unitsCompatible(targetUnit, productUnit)) return 0;
  return Math.min(100, Math.round((amountPerUnit / dailyDose) * 100));
}

function matchProducts(ingredients, pastProducts = [], weightKg = 20) {
  const allProducts = db.getAllProducts();
  const results = [];
  const pastNames = new Set((pastProducts || []).map(p => (p.product_name || p).toLowerCase()));

  for (const ing of ingredients) {
    const ingKey = ingredientKey(ing.ingredient_key || ing.ingredient_name);

    for (const product of allProducts) {
      if (!INGREDIENT_PRODUCT_TYPES.has(product.product_type)) continue;

      const pis = db.getProductIngredients(product.id);
      const pi = pis.find(p => ingredientKeysMatch(ingKey, p.ingredient_key));
      if (!pi || pi.amount_per_unit <= 0) continue;

      const coverage = computeCoverage(
        ing.daily_dose,
        pi.amount_per_unit,
        ing.unit,
        pi.unit
      );
      if (coverage <= 0) continue;

      const feedingRule = db.getFeedingRule(product.id, weightKg);
      const unitsNeeded = Math.ceil(ing.daily_dose / pi.amount_per_unit);
      const daysToFinish = product.package_units > 0
        ? product.package_units / Math.max(unitsNeeded, 1)
        : 0;

      let score = coverage / 100;
      if (daysToFinish > product.shelf_life_days) score *= 0.6;
      if (product.brand?.includes('Wagtopia')) score += 0.15;
      if (pastNames.has(product.product_name.toLowerCase()) && coverage >= 70) score += 0.25;

      const isPast = pastNames.has(product.product_name.toLowerCase());
      results.push({
        product_id: product.id,
        product_name: product.product_name,
        brand: product.brand,
        product_type: product.product_type,
        price: parseFloat(product.price),
        list_price_rmb: product.list_price_rmb ?? product.price,
        package_units: product.package_units,
        unit_cost_per_bag: product.unit_cost_per_bag ?? null,
        shelf_life_days: product.shelf_life_days,
        ingredient_name: ing.ingredient_name,
        ingredient_key: ingKey,
        amount_per_unit: pi.amount_per_unit,
        unit: pi.unit,
        feeding_rule: feedingRule
          ? `${feedingRule.daily_amount}${feedingRule.daily_unit}/day`
          : null,
        active_ingredients: pis
          .sort((a, b) => a.ingredient_order_rank - b.ingredient_order_rank)
          .map(p => ({ name: p.ingredient_name, amount: p.amount_per_unit, unit: p.unit })),
        units_needed_daily: unitsNeeded,
        suggested_usage: feedingRule
          ? `${feedingRule.daily_amount} ${feedingRule.daily_unit}/day`
          : `${unitsNeeded}/${product.unit_type || 'unit'}/day`,
        days_to_finish: Math.round(daysToFinish),
        coverage_percent: coverage,
        score: Math.round(score * 1000) / 1000,
        recommendation_note: isPast && coverage >= 70
          ? 'Based on your previous purchase — maintaining proven coverage.'
          : coverage < 70
            ? 'For optimal coverage, we recommend this upgraded formula.'
            : 'Best match for your dog\'s profile.'
      });
    }
  }

  const seen = new Set();
  return results
    .filter(r => {
      const k = r.product_name + r.ingredient_name;
      if (seen.has(k)) return false;
      seen.add(k);
      return true;
    })
    .sort((a, b) => b.score - a.score);
}

module.exports = { matchProducts };
