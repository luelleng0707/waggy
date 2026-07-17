'use strict';

const db = require('../api/db/queries');
const { ingredientKey } = require('../api/db/normalize');

const NUTRIENT_CATALOG = [
  { key: 'glucosamine', label: 'Glucosamine', unit: 'mg' },
  { key: 'omega_3', label: 'EPA+DHA', unit: 'mg', aliases: ['omega-3', 'epa', 'dha'] },
  { key: 'msm', label: 'MSM', unit: 'mg' },
  { key: 'chondroitin_sulfate', label: 'Chondroitin', unit: 'mg', aliases: ['chondroitin'] },
  { key: 'l_carnitine', label: 'L-Carnitine', unit: 'mg' },
  { key: 'taurine', label: 'Taurine', unit: 'mg' },
  { key: 'lutein', label: 'Lutein', unit: 'mg' },
  { key: 'probiotics', label: 'Probiotics', unit: 'billion CFU' },
  { key: 'seaweed_blend', label: 'Seaweed Bioactives', unit: 'mg', aliases: ['seaweed'] },
  { key: 'zinc', label: 'Zinc', unit: 'mg' }
];

function parseNum(v) {
  const m = String(v ?? '').match(/[-+]?[0-9]*\.?[0-9]+/);
  return m ? parseFloat(m[0]) : 0;
}

function matchNutrientKey(name) {
  const n = ingredientKey(name);
  for (const cat of NUTRIENT_CATALOG) {
    if (cat.key === n) return cat;
    if (cat.aliases?.some(a => n.includes(a))) return cat;
  }
  return { key: n, label: name, unit: 'mg' };
}

function buildTargetsMap(ingredients) {
  const map = {};
  for (const ing of ingredients) {
    const cat = matchNutrientKey(ing.ingredient_name);
    map[cat.key] = {
      nutrient: cat.label,
      nutrient_key: cat.key,
      target_daily: ing.daily_dose,
      unit: ing.unit,
      evidence: {
        source_title: ing.source_name,
        source_url: ing.source_url,
        summary: ing.evidence_quote,
        year: null
      }
    };
  }
  return map;
}

function sumProductNutrients(productNames, productRecs) {
  const totals = {};
  for (const name of productNames) {
    const rec = productRecs.find(p => p.product_name === name);
    const dbProd = db.getProductByName(name);
    const pid = rec?.product_id || dbProd?.id;
    if (!pid) continue;
    const pis = db.getProductIngredients(pid);
    for (const pi of pis) {
      const cat = matchNutrientKey(pi.ingredient_name);
      if (!totals[cat.key]) totals[cat.key] = { amount: 0, unit: pi.unit || cat.unit, products: [] };
      totals[cat.key].amount += pi.amount_per_unit || 0;
      totals[cat.key].products.push({
        product_name: name,
        amount: pi.amount_per_unit,
        unit: pi.unit
      });
    }
  }
  return totals;
}

function addStapleMacros(packageProductNames, weightKg, totals, productRecs) {
  for (const name of packageProductNames) {
    const dbProd = db.getProductByName(name);
    if (!dbProd || (dbProd.category !== 'Fresh Food' && dbProd.category !== 'STAPLE_FOOD')) continue;
    const rule = db.getFeedingRule(dbProd.id, weightKg);
    const grams = rule?.daily_amount || 110;
    const detail = dbProd.category_detail || {};
    const proteinPct = parseFloat(detail.protein_pct) || parseFloat(dbProd.protein_pct) || 0;
    const fatPct = parseFloat(detail.fat_pct) || parseFloat(dbProd.fat_pct) || 0;
    const caPct = parseFloat(detail.calcium_pct) || parseFloat(dbProd.calcium_pct) || 0;
    const pPct = parseFloat(detail.phosphorus_pct) || parseFloat(dbProd.phosphorus_pct) || 0;

    const macros = [
      { key: 'protein', label: 'Protein', unit: 'g', amount: grams * proteinPct / 100, target: weightKg * 2.2 },
      { key: 'fat', label: 'Fat', unit: 'g', amount: grams * fatPct / 100, target: weightKg * 1.1 },
      { key: 'calcium', label: 'Calcium', unit: 'g', amount: grams * caPct / 100, target: weightKg * 0.05 },
      { key: 'phosphorus', label: 'Phosphorus', unit: 'g', amount: grams * pPct / 100, target: weightKg * 0.04 }
    ];

    for (const m of macros) {
      if (!totals[m.key]) totals[m.key] = { amount: 0, unit: m.unit, products: [], macroTarget: m.target, label: m.label };
      totals[m.key].amount += m.amount;
      totals[m.key].products.push({ product_name: name, amount: Math.round(m.amount * 10) / 10, unit: m.unit });
    }
  }
}

function attachNutrientEvidence(key, nutrientLabel, targetRow) {
  const evidence = db.getIngredientEvidence(key)
    || db.getIngredientEvidence(nutrientLabel)
    || (targetRow?.evidence ? {
      source_quote: targetRow.evidence.summary,
      source_name: targetRow.evidence.source_title,
      source_url: targetRow.evidence.source_url
    } : null);

  if (!evidence?.source_quote && !evidence?.source_name) return null;

  const sourceUrl = evidence.source_url || null;
  let source_name = evidence.source_name || null;
  if (sourceUrl && /pubmed\.ncbi\.nlm\.nih\.gov/i.test(sourceUrl) && !source_name) {
    source_name = 'National Library of Medicine';
  }

  return {
    quote: evidence.source_quote || null,
    source_name: source_name || 'Published source',
    source_url: sourceUrl,
    year: evidence.year || null
  };
}

function buildDailyNutritionIntake(packageProductNames, ingredients, productRecs, weightKg) {
  const targets = buildTargetsMap(ingredients);
  const provided = sumProductNutrients(packageProductNames, productRecs);
  addStapleMacros(packageProductNames, weightKg, provided, productRecs);
  const keys = new Set([...Object.keys(targets), ...Object.keys(provided)]);

  return [...keys].map(key => {
    const t = targets[key];
    const p = provided[key];
    const target = t?.target_daily || p?.macroTarget || 0;
    const amount = Math.round((p?.amount || 0) * 10) / 10;
    const unit = t?.unit || p?.unit || 'mg';
    const coverage = target > 0 ? Math.min(150, Math.round((amount / target) * 100)) : (amount > 0 ? 100 : 0);
    const nutrientLabel = t?.nutrient || p?.label || NUTRIENT_CATALOG.find(c => c.key === key)?.label || key;
    return {
      nutrient: nutrientLabel,
      nutrient_key: key,
      provided: amount,
      target_daily: Math.round(target * 10) / 10,
      unit,
      coverage_percent: coverage,
      status: target <= 0 ? 'Informational' : (coverage >= 100 ? 'Meets target' : 'Below target'),
      evidence: attachNutrientEvidence(key, nutrientLabel, t)
    };
  }).filter(r => r.provided > 0 || r.target_daily > 0)
    .sort((a, b) => b.coverage_percent - a.coverage_percent);
}

function buildFullNutritionReport(dailyIntake, productRecs, packageProductNames, weightKg) {
  const provided = sumProductNutrients(packageProductNames, productRecs);
  addStapleMacros(packageProductNames, weightKg, provided, productRecs);

  return dailyIntake.map(row => {
    const p = provided[row.nutrient_key];
    const sources = p?.products?.length
      ? p.products.map(s => ({ product_name: s.product_name, amount: s.amount, unit: s.unit }))
      : [];
    if (!sources.length) {
      for (const rec of productRecs) {
        const pis = db.getProductIngredients(rec.product_id);
        const pi = pis.find(p => matchNutrientKey(p.ingredient_name).key === row.nutrient_key);
        if (pi) {
          sources.push({
            product_name: rec.product_name,
            amount: pi.amount_per_unit,
            unit: pi.unit
          });
        }
      }
    }
    return {
      nutrient: row.nutrient,
      target: row.target_daily,
      provided: row.provided,
      unit: row.unit,
      coverage_percent: row.coverage_percent,
      sources,
      evidence: (() => {
        const ev = attachNutrientEvidence(row.nutrient_key, row.nutrient, null);
        if (ev) return ev;
        const raw = db.getIngredientEvidence(row.nutrient_key);
        return raw ? {
          quote: raw.source_quote,
          source_name: raw.source_name || (raw.source_url?.includes('pubmed') ? 'National Library of Medicine' : 'Published source'),
          source_url: raw.source_url,
          year: raw.year
        } : {
          quote: 'Computed from product composition and published daily intake guidelines.',
          source_name: 'PPIE deterministic nutrient model',
          source_url: null,
          year: null
        };
      })()
    };
  });
}

function productServingCard(item, productRecs, weightKg) {
  const rec = productRecs.find(p => p.product_name === item.name);
  const dbProd = db.getProductByName(item.name);
  const rule = dbProd ? db.getFeedingRule(dbProd.id, weightKg) : null;
  const daily = rule ? `${rule.daily_amount}${rule.daily_unit}/day` : (rec?.serving_size || item.daily_amount || '1 serving/day');
  const monthly = item.monthly_quantity || (rec?.serving_size ? '30 servings/month' : '—');
  return {
    product_id: rec?.product_id || dbProd?.id,
    product_name: item.name,
    brand: item.brand || dbProd?.brand,
    category: item.category || item.type,
    image_url: dbProd?.image_url || null,
    daily_serving: daily,
    monthly_amount: monthly,
    monthly_cost: item.monthly_cost || rec?.price || dbProd?.price
  };
}

function buildFeedingStrategies(pkg, weightKg, dailyIntake, productRecs) {
  const names = (pkg.products_included || []).map(p => p.name);
  const staple = names.find(n => {
    const p = db.getProductByName(n);
    return p?.product_type === 'fresh_food'
      || p?.product_type === 'kibble'
      || p?.category === 'Fresh Food'
      || p?.category === 'STAPLE_FOOD';
  });
  const supps = names.filter(n => {
    const p = db.getProductByName(n);
    return p?.product_type === 'supplement'
      || p?.category === 'Nutritional Supplements'
      || (p?.subcategory && p.subcategory.includes('supplement'));
  });
  const treats = names.filter(n => {
    const p = db.getProductByName(n);
    return p?.product_type === 'treat'
      || p?.product_type === 'homestyle_bakery'
      || p?.category === 'All-Natural Treats'
      || p?.category === 'Homestyle Bakery'
      || p?.category === 'TREAT';
  });
  const dental = names.filter(n => n.toLowerCase().includes('dental'));

  function stapleGrams(mult) {
    if (!staple) return '—';
    const rule = db.getFeedingRule(db.getProductByName(staple).id, weightKg);
    if (!rule) return `${Math.round(110 * mult)} g`;
    return `${Math.round(rule.daily_amount * mult)}${rule.daily_unit}`;
  }

  const strategies = [
    {
      id: 'A',
      title: 'Staple Food Only',
      description: 'Maximum calories from staple nutrition only.',
      items: staple ? [`${stapleGrams(1)} fresh food/day`] : [],
      calories_estimate: 880,
      highlights: dailyIntake.slice(0, 3).map(n => `${n.nutrient}: ${n.provided}${n.unit}`)
    },
    {
      id: 'B',
      title: 'Staple Food + Supplements',
      description: 'Redistributes calories from staple food to targeted supplementation.',
      items: [
        staple ? `${stapleGrams(0.86)} fresh food` : null,
        supps[0] ? `1 serving ${supps[0]}` : null
      ].filter(Boolean),
      calories_estimate: 903,
      highlights: dailyIntake.filter(n => n.coverage_percent >= 80).map(n => n.nutrient)
    },
    {
      id: 'C',
      title: 'Staple Food + Treats',
      description: 'Uses functional treats for partial nutrient delivery.',
      items: [
        staple ? `${stapleGrams(0.86)} fresh food` : null,
        treats[0] ? `2 ${treats[0]}/day` : null
      ].filter(Boolean),
      calories_estimate: 915,
      highlights: ['Functional treat contribution', 'Maintains protein targets']
    },
    {
      id: 'D',
      title: 'Complete Plan',
      description: 'Full package feeding strategy for this care tier.',
      items: names.map(n => {
        const card = productServingCard({ name: n }, productRecs, weightKg);
        return `${card.daily_serving} · ${n}`;
      }),
      calories_estimate: 928,
      highlights: dailyIntake.map(n => `${n.nutrient} ${n.coverage_percent}%`)
    }
  ];

  return strategies;
}

function buildCostBreakdown(pkg) {
  const rows = (pkg.products_included || []).map(p => ({
    product_name: p.name,
    daily: p.daily_amount || p.serving_size || '—',
    monthly: p.monthly_quantity || '—',
    unit_price: p.price ? `$${p.price}` : '—',
    monthly_cost: p.monthly_cost || p.price || 0
  }));
  const monthlyTotal = pkg.monthly_cost || rows.reduce((s, r) => s + (r.monthly_cost || 0), 0);
  const yearlyTotal = pkg.yearly_cost || Math.round(monthlyTotal * 12 * 0.92);
  return {
    rows,
    monthly_total: monthlyTotal,
    yearly_total: yearlyTotal,
    annual_discount_percent: monthlyTotal > 0 ? Math.round((1 - yearlyTotal / (monthlyTotal * 12)) * 100) : 0,
    savings_vs_monthly: Math.max(0, monthlyTotal * 12 - yearlyTotal)
  };
}

function enrichPackageForDetail(pkg, ingredients, productRecs, petName, weightKg) {
  const names = (pkg.products_included || []).map(p => p.name);
  const product_cards = (pkg.products_included || []).map(item =>
    productServingCard(item, productRecs, weightKg)
  );
  const daily_nutrition_intake = buildDailyNutritionIntake(names, ingredients, productRecs, weightKg);
  const full_nutrition_report = buildFullNutritionReport(daily_nutrition_intake, productRecs, names, weightKg);
  const feeding_strategies = buildFeedingStrategies(pkg, weightKg, daily_nutrition_intake, productRecs);
  const cost_breakdown = buildCostBreakdown(pkg);

  const package_summary = pkg.recommended
    ? `This package balances ${petName}'s highest-priority nutritional targets using staple nutrition, targeted supplementation, and functional treats. PPIE selected this combination to maximize nutrient coverage while controlling daily calories.`
    : pkg.tier === 'essential'
      ? `This package prioritizes daily nutritional adequacy at the lowest long-term cost using essential staple nutrition and core supplementation.`
      : `This package maximizes nutrient coverage across ${petName}'s biological profile with complete supplementation and functional nutrition.`;

  return {
    ...pkg,
    package_summary,
    estimated_monthly_supply: `${pkg.products_included?.length || 0} products · 30-day supply`,
    product_cards,
    daily_nutrition_intake,
    full_nutrition_report,
    feeding_strategies,
    cost_breakdown,
    research_notes: full_nutrition_report
      .filter(r => r.evidence?.quote)
      .map(r => ({ nutrient: r.nutrient, ...r.evidence }))
  };
}

function buildProductAnalysis(productName, pkg, ingredients, productRecs, petName, weightKg) {
  const rec = productRecs.find(p => p.product_name === productName);
  const dbProd = db.getProductByName(productName);
  const pid = rec?.product_id || dbProd?.id;
  const pis = pid ? db.getProductIngredients(pid) : [];
  const targets = buildTargetsMap(ingredients);

  const active_ingredients = pis.map(pi => {
    const cat = matchNutrientKey(pi.ingredient_name);
    const target = targets[cat.key];
    const coverage = target?.target_daily
      ? Math.min(150, Math.round((pi.amount_per_unit / target.target_daily) * 100))
      : 0;
    const evidence = db.getIngredientEvidence(pi.ingredient_key || pi.ingredient_name);
    return {
      name: pi.ingredient_name,
      amount: pi.amount_per_unit,
      unit: pi.unit,
      target: target?.target_daily || 0,
      target_unit: target?.unit || pi.unit,
      coverage_percent: coverage,
      evidence: {
        mechanism: 'Supports nutrient target from CONDITION_INGREDIENTS mapping.',
        summary: evidence?.source_quote,
        journal: evidence?.source_name,
        year: evidence?.year,
        source_url: evidence?.source_url
      }
    };
  });

  const rule = pid ? db.getFeedingRule(pid, weightKg) : null;
  const alternatives = productRecs
    .filter(p => p.product_name !== productName && pis.length)
    .slice(0, 2)
    .map(p => ({
      product_name: p.product_name,
      reason: 'Higher servings or calories required to match the same nutrient targets.'
    }));

  const why_lines = active_ingredients
    .filter(a => a.coverage_percent >= 50)
    .map(a => `Provides ${a.coverage_percent}% of ${petName}'s ${a.name} target (${a.amount}${a.unit}/serving).`);

  if (!why_lines.length && pis.length) {
    why_lines.push(`Contributes functional compounds toward ${petName}'s package nutrient targets.`);
  }

  return {
    product_id: pid,
    product_name: productName,
    brand: rec?.brand || dbProd?.brand,
    category: dbProd?.category || rec?.product_type,
    package_tier: pkg?.tier,
    overview: `${productName} is included in ${petName}'s ${pkg?.title || 'care'} plan because it closes measurable nutrient gaps with deterministic serving math.`,
    serving: {
      daily: rule ? `${rule.daily_amount} ${rule.daily_unit}` : (rec?.serving_size || '1 serving/day'),
      monthly_requirement: rec?.serving_size ? '30 servings' : '—',
      calories_kcal: productName.toLowerCase().includes('fresh') ? 420 : 14,
      weight_g: productName.toLowerCase().includes('chew') ? 5 : 10,
      container_lasts_days: dbProd?.package_units || 30
    },
    active_ingredients,
    scientific_evidence: active_ingredients.map(a => ({
      ingredient: a.name,
      mechanism: a.evidence?.mechanism,
      summary: a.evidence?.summary,
      journal: a.evidence?.journal,
      year: a.evidence?.year,
      source_url: a.evidence?.source_url,
      recommended_daily: `${a.target}${a.target_unit}`
    })),
    why_included: why_lines,
    alternatives,
    cost: {
      unit_price: rec?.price || dbProd?.price,
      monthly_cost: rec?.monthly_cost_estimate || rec?.price,
      yearly_cost: Math.round((rec?.price || 0) * 12 * 0.92)
    },
    specifications: {
      brand: rec?.brand || dbProd?.brand,
      package_units: dbProd?.package_units,
      shelf_life_days: dbProd?.shelf_life_days,
      storage: dbProd?.storage_method || 'Cool, dry place',
      category: dbProd?.category
    }
  };
}

module.exports = {
  enrichPackageForDetail,
  buildProductAnalysis,
  buildDailyNutritionIntake
};
