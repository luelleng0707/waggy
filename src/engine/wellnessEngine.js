'use strict';

const db = require('../api/db/queries');
const { conditionKey } = require('../api/db/normalize');
const { WELLNESS_GOALS, goalForCondition, friendlyTraitLabel } = require('./wellnessMap');

function buildBiologySummary(breeds, meta) {
  const traits = new Set();
  for (const b of breeds) {
    traits.add(b.size_class);
    traits.add(b.body_type);
    traits.add(b.coat_type);
    traits.add(b.energy_level);
    traits.add(b.weakness_group);
    traits.add(b.function_group);
  }
  return {
    breeds: meta.breeds,
    breed_count: meta.breedCount,
    age_years: meta.ageYears,
    age_stage: meta.ageStage,
    trait_summary: [...traits].filter(Boolean),
    descriptors: breeds.map(b => ({
      breed: b.breed_name,
      size: b.size_class,
      body_type: b.body_type,
      coat_type: b.coat_type,
      energy: b.energy_level,
      weakness_group: b.weakness_group,
      function_group: b.function_group
    }))
  };
}

function buildHealthInsights(risks, petName) {
  const grouped = {};

  for (const r of risks) {
    const goalId = goalForCondition(r.condition_key);
    if (!grouped[goalId]) {
      const goal = WELLNESS_GOALS[goalId] || {
        id: 'general_wellness',
        title: 'General Wellness',
        why_template: 'overall preventative nutrition may support long-term vitality'
      };
      grouped[goalId] = {
        goal_id: goalId,
        title: goal.title,
        priority_score: 0,
        biological_risk_percent: 0,
        observed_prevalence_percent: null,
        confidence_percent: 0,
        evidence_count: 0,
        supporting_conditions: [],
        supporting_traits: [],
        evidence_sources: [],
        groomer_priority: false
      };
    }

    const g = grouped[goalId];
    const bio = r.trait_risk_percent ?? r.estimated_risk_percent ?? r.risk_percent ?? 0;
    const obs = r.breed_prevalence_percent;

    g.priority_score = Math.max(g.priority_score, r.risk_percent ?? 0);
    g.biological_risk_percent = Math.max(g.biological_risk_percent, bio);
    if (obs != null) {
      g.observed_prevalence_percent = Math.max(g.observed_prevalence_percent ?? 0, obs);
    }
    g.confidence_percent = Math.max(g.confidence_percent, r.confidence_percent ?? 0);
    g.evidence_count = Math.max(g.evidence_count, r.evidence_count ?? 0);
    g.groomer_priority = g.groomer_priority || !!r.groomer_boosted;

    g.supporting_conditions.push(r.condition_name);
    for (const t of r.supporting_traits || []) {
      const label = friendlyTraitLabel(t.category, t.value);
      if (!g.supporting_traits.includes(label)) g.supporting_traits.push(label);
    }
    if (r.source_name) {
      g.evidence_sources.push({
        source_name: r.source_name,
        source_quote: r.source_quote,
        source_url: r.source_url
      });
    }
  }

  const insights = Object.values(grouped).map(g => {
    const goal = WELLNESS_GOALS[g.goal_id] || { why_template: 'preventative care may provide long-term benefit' };
    const observed = g.observed_prevalence_percent;
    const biological = g.biological_risk_percent;
    const difference = observed != null ? Math.round((biological - observed) * 10) / 10 : null;

    const goalTitle = goal.title || g.title || 'wellness';
    return {
      ...g,
      estimated_biological_risk_percent: Math.round(biological * 10) / 10,
      observed_breed_prevalence_percent: observed != null ? Math.round(observed * 10) / 10 : null,
      estimate_vs_observed_difference: difference,
      explanation: `Our veterinary research team estimates ${petName} may benefit from preventative ${goalTitle.toLowerCase()} support — ${goal.why_template}. This does NOT mean ${petName} will develop illness; it highlights areas where long-term wellness care may help most.`,
      why_this_matters: goal.why_template,
      peer_reviewed_study_count: g.evidence_sources.length
    };
  });

  return insights
    .sort((a, b) => {
      if (a.groomer_priority !== b.groomer_priority) return b.groomer_priority - a.groomer_priority;
      return b.priority_score - a.priority_score;
    })
    .slice(0, 8);
}

function buildNutritionalTargets(ingredients, healthInsights) {
  return ingredients.map(ing => ({
    ingredient: ing.ingredient_name,
    ingredient_key: ing.ingredient_key,
    daily_target: `${ing.daily_dose}${ing.unit}`,
    monthly_target: `${ing.monthly_dose}${ing.unit}`,
    supports_goals: ing.for_conditions.map(c => {
      const goalId = goalForCondition(conditionKey(c));
      return WELLNESS_GOALS[goalId]?.title || 'General Wellness';
    }),
    evidence_quote: ing.evidence_quote,
    source_name: ing.source_name,
    source_url: ing.source_url
  }));
}

function enrichProductRecommendations(products, ingredients, petName) {
  const ingTargets = Object.fromEntries(
    ingredients.map(i => [i.ingredient_key, i])
  );

  const byProduct = {};
  for (const p of products) {
    if (!byProduct[p.product_name]) {
      byProduct[p.product_name] = { ...p, matched_ingredients: [], coverage_scores: [] };
    }
    const entry = byProduct[p.product_name];
    const ingKey = (p.ingredient_name || '').toLowerCase().replace(/[^a-z0-9]+/g, '_');
    const target = ingTargets[ingKey];
    entry.matched_ingredients.push({
      name: p.ingredient_name,
      amount_per_serving: `${p.amount_per_unit}${p.unit}`,
      daily_target: target ? `${target.daily_dose}${target.unit}` : null,
      coverage_percent: p.coverage_percent
    });
    entry.coverage_scores.push(p.coverage_percent);
  }

  return Object.values(byProduct).map(p => {
    const avgCoverage = p.coverage_scores.length
      ? Math.round(p.coverage_scores.reduce((s, v) => s + v, 0) / p.coverage_scores.length)
      : 0;
    const ingLines = p.matched_ingredients
      .map(m => `${m.amount_per_serving} ${m.name}`)
      .join(' · ');

    const why = avgCoverage >= 70
      ? `This product supplies approximately ${avgCoverage}% of ${petName}'s recommended daily nutritional targets for key active ingredients while supporting long-term preventative wellness.`
      : `This product contributes partial coverage (${avgCoverage}%) toward ${petName}'s nutritional targets and works best as part of a balanced wellness plan.`;

    const advantages = [];
    if (avgCoverage >= 85) advantages.push('High ingredient concentration');
    if (p.brand?.includes('Wagtopia')) advantages.push('Wagtopia curated formula');
    if ((p.units_needed_daily || 1) <= 2) advantages.push('Requires only one serving daily');
    if (p.price && avgCoverage >= 70) advantages.push('Excellent cost efficiency');

    return {
      product_id: p.product_id,
      product_name: p.product_name,
      brand: p.brand,
      product_type: p.product_type,
      price: p.price,
      serving_size: p.suggested_usage,
      active_ingredients: p.active_ingredients || p.matched_ingredients,
      coverage_percent: avgCoverage,
      monthly_cost_estimate: p.price,
      shelf_life_days: p.shelf_life_days,
      why_selected: why,
      advantages,
      ingredient_breakdown: ingLines,
      combined_coverage_note: `Combined with ${petName}'s daily diet this achieves ${avgCoverage}% of our recommended target for matched ingredients.`
    };
  }).sort((a, b) => b.coverage_percent - a.coverage_percent);
}

function buildWellnessCoverage(healthInsights, productRecs, ingredients) {
  const dimensions = {};
  const defaultGoals = ['joint_health', 'skin_health', 'dental_health', 'digestive_health', 'weight_management', 'immune_support', 'activity_support'];

  for (const gid of defaultGoals) {
    dimensions[gid] = { title: WELLNESS_GOALS[gid]?.title || gid, coverage_percent: 72 };
  }

  for (const insight of healthInsights) {
    const productsForGoal = productRecs.filter(p =>
      p.coverage_percent > 0
    );
    const base = Math.min(98, 60 + insight.priority_score * 0.8 + (insight.confidence_percent * 0.2));
    const productBoost = productsForGoal.length ? Math.min(15, productsForGoal[0].coverage_percent * 0.1) : 0;
    dimensions[insight.goal_id] = {
      title: insight.title,
      coverage_percent: Math.round(Math.min(98, base + productBoost))
    };
  }

  if (ingredients.length) {
    const avgIng = Math.min(95, 70 + ingredients.length * 4);
    dimensions.digestive_health = dimensions.digestive_health || { title: 'Digestive Health', coverage_percent: avgIng };
    dimensions.digestive_health.coverage_percent = Math.max(dimensions.digestive_health.coverage_percent, avgIng);
  }

  const values = Object.values(dimensions).map(d => d.coverage_percent);
  const overall = values.length
    ? Math.round(values.reduce((s, v) => s + v, 0) / values.length)
    : 75;

  return {
    overall_score: overall,
    max_score: 100,
    label: 'Overall Wellness Coverage',
    subtitle: 'Nutritional coverage across preventative health priorities',
    dimensions: Object.entries(dimensions).map(([id, d]) => ({
      goal_id: id,
      title: d.title,
      coverage_percent: d.coverage_percent
    }))
  };
}

const PRIORITY_LABELS = {
  joint_health: 'Joint Support',
  skin_health: 'Skin Health',
  dental_health: 'Dental Care',
  weight_management: 'Healthy Weight',
  digestive_health: 'Digestive Support',
  immune_support: 'Immune Support',
  activity_support: 'Activity Support',
  cardiac_support: 'Cardiac Support',
  eye_health: 'Eye Health',
  respiratory_comfort: 'Respiratory Comfort',
  general_wellness: 'General Wellness'
};

function priorityLabel(goalId, fallbackTitle) {
  return PRIORITY_LABELS[goalId] || fallbackTitle || 'Wellness Support';
}

function getTimeGreeting() {
  const h = new Date().getHours();
  if (h < 12) return 'Good morning';
  if (h < 17) return 'Good afternoon';
  return 'Good evening';
}

function buildWellnessSummary(petName, biology, healthInsights, wellnessCoverage) {
  const priorities = healthInsights.slice(0, 4).map(h =>
    priorityLabel(h.goal_id, h.title)
  );
  const focusList = priorities.slice(0, 3);
  const focusText = focusList.length > 1
    ? focusList.slice(0, -1).join(', ') + ' and ' + focusList[focusList.length - 1]
    : (focusList[0] || 'core wellness');

  return {
    greeting: getTimeGreeting(),
    intro: `Based on ${petName}'s breed, age, body size and biological characteristics, our veterinary research team estimates that preventative ${focusText.toLowerCase()} care will provide the greatest long-term health benefit.`,
    closing: 'We created several personalized wellness plans that balance health coverage and monthly cost.',
    wellness_score: wellnessCoverage.overall_score,
    score_label: 'Estimated Wellness Score',
    primary_priorities: priorities,
    traits_analysed: biology.trait_summary || [],
    analysis_detail: healthInsights.slice(0, 6).map(h => ({
      goal_id: h.goal_id,
      title: priorityLabel(h.goal_id, h.title),
      biological_estimate_percent: h.estimated_biological_risk_percent,
      observed_prevalence_percent: h.observed_breed_prevalence_percent,
      difference_percent: h.estimate_vs_observed_difference,
      supporting_traits: h.supporting_traits,
      explanation: h.explanation
    }))
  };
}

function enrichPackageProduct(item, productRecs) {
  const rec = productRecs.find(p => p.product_name === item.name);
  const dbProd = db.getProductByName(item.name);
  const daily = rec?.serving_size || '1 serving/day';
  const unitsDaily = rec?.units_needed_daily || 1;
  const monthlyQty = Math.round(unitsDaily * 30);

  return {
    ...item,
    product_id: rec?.product_id || dbProd?.id,
    brand: rec?.brand || dbProd?.brand || 'Wagtopia',
    category: item.type,
    serving_size: daily,
    daily_amount: daily,
    monthly_quantity: `${monthlyQty} ${dbProd?.unit_type || 'units'}/month`,
    price: rec?.price || dbProd?.price,
    coverage_percent: rec?.coverage_percent || 0,
    why_selected: rec?.why_selected || '',
    combined_coverage_note: rec?.combined_coverage_note || '',
    advantages: rec?.advantages || [],
    active_ingredients: rec?.active_ingredients || [],
    nutrition_contribution: rec?.goal_coverage || []
  };
}

function buildPackageNutritionCoverage(wellnessCoverage, tier) {
  const mult = tier === 'essential' ? 0.82 : tier === 'balanced' ? 1 : 1.12;
  const dims = (wellnessCoverage.dimensions || []).slice(0, 6);
  return dims.map(d => ({
    goal_id: d.goal_id,
    title: priorityLabel(d.goal_id, d.title),
    coverage_percent: Math.min(100, Math.round(d.coverage_percent * mult))
  }));
}

function buildIncludesSummary(items, tier) {
  const counts = {};
  for (const i of items) counts[i.type] = (counts[i.type] || 0) + 1;
  const lines = [];
  if (counts.fresh_food || counts.kibble || counts.staple_food) {
    lines.push(tier === 'essential' ? '1 fresh food' : 'Premium fresh food');
  }
  if (counts.supplement) {
    lines.push(`${counts.supplement} supplement${counts.supplement > 1 ? 's' : ''}`);
  }
  if (counts.treat) {
    lines.push(`${counts.treat} functional treat${counts.treat > 1 ? 's' : ''}`);
  }
  if (counts.dental) {
    lines.push(tier === 'essential' ? '1 dental product' : 'Dental support');
  }
  if (tier === 'optimal' && counts.supplement >= 3) {
    lines.push('Complete supplement stack');
  }
  return lines;
}

function buildWellnessPackages(productRecs, monthlyPlan, yearlyPlan, healthInsights, weightKg, petName, wellnessCoverage) {
  const staples = db.getAllProducts().filter(p =>
    p.product_type === 'fresh_food' || p.product_type === 'staple_food' || p.product_type === 'kibble'
  );
  const supps = productRecs.filter(p => p.product_type === 'supplement').slice(0, 3);
  const treats = productRecs.filter(p => p.product_type === 'treat').slice(0, 2);
  const dental = productRecs.filter(p =>
    p.subcategory === 'dental_chew' || p.product_name?.includes('Dental')
  ).slice(0, 1);

  const topGoals = healthInsights.slice(0, 3).map(h =>
    priorityLabel(h.goal_id, h.title)
  ).join(', ');

  const tierMeta = {
    essential: {
      suppCount: 1, treatCount: 1, dental: true, mult: 0.72, coverage: 72,
      best_for: 'Budget-conscious owners.',
      description: `Provides the minimum evidence-supported nutritional coverage for ${petName}'s biological needs while keeping monthly cost as low as possible.`,
      includes_extra: []
    },
    balanced: {
      suppCount: 2, treatCount: 2, dental: true, mult: 1, coverage: 88,
      best_for: null,
      description: `Our recommended balance between health coverage and affordability. Provides strong support for ${petName}'s highest-priority health needs without unnecessary spending.`,
      includes_extra: []
    },
    optimal: {
      suppCount: 3, treatCount: 2, dental: true, mult: 1.08, coverage: 97,
      best_for: null,
      description: 'Designed for owners who want the highest possible nutritional coverage with minimal compromises.',
      includes_extra: ['Skin support', 'Joint support', 'Digestive support']
    }
  };

  function makePackage(tier) {
    const meta = tierMeta[tier];
    const items = [];
    const staple = tier === 'essential'
      ? (staples.find(p => p.subcategory === 'fresh_single') || staples[staples.length - 1])
      : (staples.find(p => p.brand === 'Wagtopia' && p.subcategory === 'fresh_combo') || staples[0]);
    if (staple) {
      const unitCost = staple.unit_cost_per_bag || staple.price;
      items.push({
        type: 'fresh_food',
        name: staple.product_name,
        monthly_cost: Math.round(unitCost * 7.5)
      });
    }
    supps.slice(0, meta.suppCount).forEach(s => items.push({ type: 'supplement', name: s.product_name, monthly_cost: s.price }));
    treats.slice(0, meta.treatCount).forEach(t => items.push({ type: 'treat', name: t.product_name, monthly_cost: t.price }));
    if (meta.dental && dental[0]) items.push({ type: 'dental', name: dental[0].product_name, monthly_cost: dental[0].price });

    const enriched = items.map(i => enrichPackageProduct(i, productRecs));
    const monthly = Math.round(enriched.reduce((s, i) => s + (i.monthly_cost || 0), 0) * meta.mult);
    const yearly = Math.round(monthly * 12 * (tier === 'optimal' ? 0.88 : tier === 'balanced' ? 0.92 : 0.95));
    const nutrition = buildPackageNutritionCoverage(wellnessCoverage, tier);
    const coverageScore = Math.round(nutrition.reduce((s, n) => s + n.coverage_percent, 0) / Math.max(nutrition.length, 1));

    return {
      tier,
      title: tier === 'essential' ? 'Essential Care' : tier === 'balanced' ? 'Balanced Care' : 'Optimal Care',
      recommended: tier === 'balanced',
      best_for: meta.best_for,
      tagline: meta.description.split('.')[0] + '.',
      description: meta.description,
      coverage_score: Math.min(100, Math.max(meta.coverage, coverageScore)),
      monthly_cost: monthly,
      yearly_cost: yearly,
      includes_summary: [...buildIncludesSummary(items, tier), ...meta.includes_extra],
      products_included: enriched,
      nutrition_coverage: nutrition,
      overview: `Our biological model estimates that ${petName} would benefit most from long-term ${topGoals.toLowerCase() || 'preventative wellness'} support. This plan provides approximately ${Math.min(100, Math.max(meta.coverage, coverageScore))}% nutritional coverage across those priority areas${tier === 'essential' ? ' while remaining budget-friendly' : tier === 'balanced' ? ' while remaining cost efficient' : ''}.`,
      activities_included: healthInsights.slice(0, 2).flatMap(h =>
        db.getActivities(h.supporting_conditions[0] || '').slice(0, 1).map(a => a.activity_name)
      ),
      why_fits: `Designed for ${weightKg}kg biology with focus on ${topGoals || 'core preventative wellness'}.`,
      subscribe_cta: `Subscribe to ${tier === 'essential' ? 'Essential' : tier === 'balanced' ? 'Balanced' : 'Optimal'} Care`
    };
  }

  return [makePackage('essential'), makePackage('balanced'), makePackage('optimal')];
}

function buildActivityPlan(breeds, healthInsights, meta, petName) {
  const energy = breeds.map(b => b.energy_level);
  const isHighDrive = energy.some(e => e === 'Extreme' || e === 'High');
  const isLow = energy.some(e => e === 'Low');
  const hasWorking = breeds.some(b =>
    ['Working', 'Sporting', 'Herding'].includes(b.function_group)
  );

  let dailyMinutes = isHighDrive ? 75 : isLow ? 45 : 60;
  if (meta.ageStage === 'senior') dailyMinutes = Math.round(dailyMinutes * 0.75);
  if (meta.ageStage === 'puppy') dailyMinutes = Math.round(dailyMinutes * 0.85);

  const physical = isHighDrive
    ? ['Walking', 'Swimming', 'Fetch', 'Puzzle Toys']
    : ['Walking', 'Gentle play', 'Sniff walks'];

  const mental = ['Puzzle feeders', 'Training', 'Scent games', 'Mental enrichment'];

  const lifestyleTip = hasWorking
    ? `Because ${petName} has working-breed ancestry, regular exercise and mental stimulation may support healthy weight and positive behaviour.`
    : `Regular activity tailored to ${petName}'s energy level supports long-term mobility and overall wellness.`;

  return {
    recommended_daily_exercise: `${dailyMinutes}–${dailyMinutes + 15} minutes`,
    suggested_physical: physical,
    suggested_mental: mental,
    lifestyle_tip: lifestyleTip,
    condition_specific: [],
    future_personalization_note: 'Once walking history and activity logs are available, recommendations will automatically adapt.'
  };
}

function buildResearchSection(biology, healthInsights, scientificEvidence, nutritionalTargets) {
  return {
    title: 'Why did we recommend these products?',
    biological_traits: biology.trait_summary || [],
    health_priorities: healthInsights.slice(0, 6).map(h => ({
      title: priorityLabel(h.goal_id, h.title),
      biological_estimate_percent: h.estimated_biological_risk_percent,
      observed_prevalence_percent: h.observed_breed_prevalence_percent,
      supporting_traits: h.supporting_traits
    })),
    ingredient_evidence: (nutritionalTargets || []).slice(0, 6).map(t => ({
      ingredient: t.ingredient,
      supports: t.supports_goals,
      quote: t.evidence_quote,
      source_name: t.source_name,
      source_url: t.source_url
    })),
    literature: (scientificEvidence || []).slice(0, 8)
  };
}

function parseDoseValue(raw) {
  const m = String(raw || '').match(/[-+]?[0-9]*\.?[0-9]+/);
  return m ? parseFloat(m[0]) : 0;
}

function parseDoseUnit(raw) {
  const m = String(raw || '').match(/[a-zA-Z%]+(?:\s?[a-zA-Z%]+)?$/);
  return m ? m[0] : '';
}

function buildCalculationTrace({
  profile,
  biology,
  healthInsights,
  nutritionalTargets,
  productRecommendations
}) {
  const breeds = profile.breeds || [];
  const breedEvidenceAll = db.getBreedObservedRisks(breeds);

  return healthInsights.slice(0, 6).map(insight => {
    const observed_inputs = {
      age: `${profile.age_years} years`,
      weight: `${profile.weight_kg}kg`,
      body_size: biology.descriptors?.[0]?.size || null,
      body_type: biology.descriptors?.[0]?.body_type || null,
      coat_type: biology.descriptors?.[0]?.coat_type || null,
      skull: biology.descriptors?.[0]?.skull_type || null,
      activity: biology.descriptors?.[0]?.energy || null,
      breed_mix: breeds
    };

    const published_evidence = breedEvidenceAll
      .filter(row => {
        const goalId = goalForCondition(row.condition_key || conditionKey(row.condition_name));
        return goalId === insight.goal_id;
      })
      .map(row => ({
        breed: row.breed_name,
        condition: row.condition_name,
        observed_prevalence_percent: Math.round((row.prevalence || 0) * 1000) / 10,
        study_population: row.sample_population,
        sample_size: row.sample_size,
        source_title: row.source_name,
        source_journal: row.source_name,
        source_year: row.year,
        source_url: row.source_url
      }));

    const trait_contributions = (insight.supporting_traits || []).map((trait, idx) => ({
      trait,
      role: idx < 2 ? 'primary' : 'supporting',
      explanation: 'Matched against normalized epidemiology tables in deterministic trait aggregation.'
    }));

    const nutrient_targets = (nutritionalTargets || [])
      .filter(t => (t.supports_goals || []).includes(insight.title))
      .map(t => ({
        nutrient: t.ingredient,
        target_daily_value: parseDoseValue(t.daily_target),
        unit: parseDoseUnit(t.daily_target),
        reason: `Supports ${insight.title.toLowerCase()} requirements from deterministic profile-to-nutrient mapping.`,
        evidence: {
          source_title: t.source_name,
          source_url: t.source_url,
          summary: t.evidence_quote
        }
      }));

    const product_contributions = (productRecommendations || []).map(p => {
      const matching = (p.active_ingredients || []).filter(ai =>
        nutrient_targets.some(t =>
          String(ai.name || '').toLowerCase() === String(t.nutrient || '').toLowerCase()
        )
      );

      const nutrient_lines = matching.map(ai => {
        const target = nutrient_targets.find(t =>
          String(t.nutrient || '').toLowerCase() === String(ai.name || '').toLowerCase()
        );
        const amount = parseFloat(ai.amount || ai.amount_per_serving || 0);
        const pct = target && target.target_daily_value > 0
          ? Math.round((amount / target.target_daily_value) * 100)
          : 0;
        return {
          nutrient: ai.name,
          provided_value: amount,
          unit: ai.unit || target?.unit || '',
          target_value: target?.target_daily_value || 0,
          target_unit: target?.unit || '',
          percent_of_target: pct,
          source_title: target?.evidence?.source_title || null,
          source_url: target?.evidence?.source_url || null
        };
      });

      return {
        product_id: p.product_id,
        product_name: p.product_name,
        serving_size: p.serving_size,
        daily_amount: p.serving_size,
        active_ingredient_count: (p.active_ingredients || []).length,
        active_ingredients: (p.active_ingredients || []).map(ai => ({
          name: ai.name,
          amount: ai.amount,
          unit: ai.unit
        })),
        nutrient_lines
      };
    }).filter(p => p.nutrient_lines.length);

    const decision_log = [
      `PPIE compared ${profile.pet_name}'s observed profile with deterministic trait-risk tables.`,
      `Published breed epidemiology for ${insight.title.toLowerCase()} was matched across ${breeds.length} breed input(s).`,
      `Nutrient targets were generated from CONDITION_INGREDIENTS and INGREDIENT_EVIDENCE mappings.`,
      product_contributions.length
        ? `Selected products close key nutrient gaps for ${insight.title.toLowerCase()} with serving-feasible daily use.`
        : `No direct nutrient-mapped product was selected for this priority.`
    ];

    return {
      condition: insight.title,
      observed_inputs,
      published_evidence,
      trait_contributions,
      nutrient_targets,
      product_contributions,
      decision_log
    };
  });
}

module.exports = {
  buildBiologySummary,
  buildHealthInsights,
  buildNutritionalTargets,
  enrichProductRecommendations,
  buildWellnessCoverage,
  buildWellnessPackages,
  buildActivityPlan,
  buildWellnessSummary,
  buildResearchSection,
  buildCalculationTrace,
  priorityLabel
};
