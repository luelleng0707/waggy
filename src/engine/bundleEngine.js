'use strict';

const db = require('../api/db/queries');

const STAPLE_TYPES = new Set(['fresh_food', 'staple_food', 'kibble']);

function isStapleProduct(product) {
  return STAPLE_TYPES.has(product.product_type);
}

function getStapleProducts() {
  return db.getAllProducts().filter(isStapleProduct);
}

function getFeedingAmount(product, weightKg) {
  const rule = db.getFeedingRule(product.id, weightKg);
  if (rule) {
    return { daily: rule.daily_amount, unit: rule.daily_unit };
  }
  if (isStapleProduct(product)) {
    const grams = Math.round(weightKg * 20);
    return { daily: grams, unit: 'g' };
  }
  return { daily: 1, unit: product.unit_type || 'unit' };
}

function buildMonthlyPlan(products, weightKg, ageStage) {
  const staples = getStapleProducts();
  const supps = products.filter(p => p.product_type === 'supplement').slice(0, 2);
  const treats = products.filter(p =>
    p.product_type === 'treat' || p.product_type === 'homestyle_bakery'
  ).slice(0, 2);

  const bestStaple = staples.find(p => p.brand === 'Wagtopia' && p.subcategory === 'fresh_combo')
    || staples.find(p => p.brand === 'Wagtopia')
    || staples[0];
  const items = [];

  if (bestStaple) {
    const feed = getFeedingAmount(bestStaple, weightKg);
    const monthlyTotal = feed.daily * 30;
    const gramsPerBag = 200;
    const bags = Math.max(1, Math.ceil(monthlyTotal / gramsPerBag));
    const unitCost = bestStaple.unit_cost_per_bag
      || (bestStaple.price / (bestStaple.package_units || 1));
    items.push({
      product_name: bestStaple.product_name,
      product_type: bestStaple.product_type,
      daily: `${feed.daily}${feed.unit}/day`,
      monthly: `${monthlyTotal}${feed.unit}`,
      depletion: `${bags} bag(s) exactly`,
      quantity: bags,
      cost: Math.round(bags * unitCost),
      unit_cost_per_bag: unitCost,
      fresh_warning: bestStaple.shelf_life_days <= 60
        ? `Shelf life: ${bestStaple.shelf_life_days} days`
        : null
    });
  }

  for (const s of supps) {
    const feed = getFeedingAmount(s, weightKg);
    const monthlyUnits = Math.min(30, s.package_units || 30);
    items.push({
      product_name: s.product_name,
      product_type: 'supplement',
      daily: s.suggested_usage || `${feed.daily} ${feed.unit}/day`,
      monthly: `${monthlyUnits}/month`,
      depletion: '1 jar exactly',
      quantity: 1,
      cost: s.price,
      fresh_warning: null
    });
  }

  for (const t of treats) {
    const feed = getFeedingAmount(t, weightKg);
    const daily = feed.daily || 2;
    const monthly = daily * 30;
    const packs = Math.ceil(monthly / (t.package_units || 30));
    items.push({
      product_name: t.product_name,
      product_type: t.product_type,
      daily: `${daily}/day`,
      monthly: `${monthly}/month`,
      depletion: `${packs} pack(s)`,
      quantity: packs,
      cost: packs * t.price,
      fresh_warning: t.shelf_life_days <= 30
        ? `Shelf life: ${t.shelf_life_days} days · Use within ${t.shelf_life_days - 2} days`
        : null
    });
  }

  const total = Math.round(items.reduce((s, i) => s + i.cost, 0));

  return {
    title: 'Monthly Wellness Plan',
    duration_days: 30,
    items,
    total_cost: total,
    product_count: items.length
  };
}

function buildYearlyPlan(monthlyPlan, products) {
  const staples = getStapleProducts();
  const basic = staples.find(p => p.subcategory === 'fresh_single' || p.product_id === 'FF001');
  const premium = staples.find(p => p.subcategory === 'fresh_combo' && p.product_id === 'FF003')
    || staples.find(p => p.subcategory === 'fresh_combo');

  let stapleUpgrade = null;
  if (basic && premium) {
    stapleUpgrade = {
      current: basic.product_name,
      recommended: premium.product_name,
      reason: 'Higher variety combo pack · optimized omega profile for annual bundling'
    };
  }

  const items = monthlyPlan.items.map(item => {
    const yearlyQty = item.product_type === 'supplement'
      ? Math.ceil(365 / 60)
      : item.quantity * 12;
    return {
      ...item,
      quantity: yearlyQty,
      duration: '365 days',
      cost: Math.round(yearlyQty * (item.cost / item.quantity))
    };
  });

  const total = items.reduce((s, i) => s + i.cost, 0);
  const naive = monthlyPlan.total_cost * 12;
  const savings = Math.max(0, naive - total);

  return {
    title: 'Annual Optimized Plan',
    duration_days: 365,
    items,
    total_cost: total,
    monthly_equivalent: Math.round(total / 12),
    savings,
    savings_percent: naive > 0 ? Math.round((savings / naive) * 100) : 0,
    kibble_upgrade: stapleUpgrade,
    staple_upgrade: stapleUpgrade,
    bulk_notes: 'Supplement bottles optimized · combo fresh food packs · treat renewal schedule'
  };
}

module.exports = { buildMonthlyPlan, buildYearlyPlan, getFeedingAmount, getStapleProducts };
