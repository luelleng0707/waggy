'use strict';

const db = require('../api/db/queries');

const CATEGORY_WEIGHTS = {
  weakness_group: 3.0,
  body_type: 2.5,
  skull_type: 2.5,
  function_group: 2.0,
  size: 2.0,
  energy: 1.5,
  lifespan: 1.5,
  coat_type: 1.0,
  climate: 1.0
};

const TOTAL_TRAIT_CATEGORIES = Object.keys(CATEGORY_WEIGHTS).length;
const INTERACTION_MIN = 0.80;
const INTERACTION_MAX = 1.20;

function clampRisk(decimal) {
  return Math.min(1, Math.max(0, decimal));
}

function clampInteractionFactor(factor) {
  const f = parseFloat(factor) || 1;
  return Math.min(INTERACTION_MAX, Math.max(INTERACTION_MIN, f));
}

function roundPct(decimal) {
  return Math.round(clampRisk(decimal) * 1000) / 10;
}

function groupTraitEvidence(traitRisks) {
  const byCondition = {};

  for (const row of traitRisks) {
    const key = row.condition_key || row.condition_name;
    if (!byCondition[key]) {
      byCondition[key] = { condition_name: row.condition_name, byCategory: {} };
    }
    const cat = row.trait_category;
    const prev = parseFloat(row.prevalence);
    const weight = CATEGORY_WEIGHTS[cat] || 1.0;

    const existing = byCondition[key].byCategory[cat];
    if (!existing || prev > existing.prevalence) {
      byCondition[key].byCategory[cat] = {
        trait_category: cat,
        trait_value: row.trait_value,
        prevalence: prev,
        weight,
        source_name: row.source_name,
        source_quote: row.source_quote,
        source_url: row.source_url
      };
    }
  }

  return byCondition;
}

function computeSummedPrevalence(traitEvidence) {
  if (!traitEvidence.length) return 0;
  const sum = traitEvidence.reduce((total, e) => total + (parseFloat(e.prevalence) || 0), 0);
  return clampRisk(sum);
}

function computeWeightedBaseRisk(traitEvidence) {
  return computeSummedPrevalence(traitEvidence);
}

function computeConfidence(supportingCount) {
  return Math.round((supportingCount / TOTAL_TRAIT_CATEGORIES) * 1000) / 10;
}

function applyInteractionFactor(baseRisk, conditionKey, conditionName, breeds) {
  const interactions = db.getTraitInteractions(breeds).filter(i =>
    i.condition_key === conditionKey || i.condition_name === conditionName
  );

  if (!interactions.length) {
    return { risk: baseRisk, interaction_factor: 1, interactions_applied: [] };
  }

  let factor = 1;
  for (const match of interactions) {
    if (match.interaction === 'neutral') continue;
    factor *= clampInteractionFactor(match.factor);
  }
  factor = clampInteractionFactor(factor);

  return {
    risk: clampRisk(baseRisk * factor),
    interaction_factor: factor,
    interactions_applied: interactions
  };
}

function computeEvidenceScores(traitRisks, breeds = []) {
  const grouped = groupTraitEvidence(traitRisks);
  const results = [];

  for (const [key, { condition_name, byCategory }] of Object.entries(grouped)) {
    const trait_evidence = Object.values(byCategory);
    const base_risk = clampRisk(computeWeightedBaseRisk(trait_evidence));
    const confidence_percent = computeConfidence(trait_evidence.length);

    const { risk: afterInteraction, interaction_factor, interactions_applied } =
      applyInteractionFactor(base_risk, key, condition_name, breeds);

    results.push({
      condition_name,
      condition_key: key,
      trait_evidence,
      base_risk: Math.round(base_risk * 10000) / 10000,
      base_risk_percent: roundPct(base_risk),
      confidence_percent,
      evidence_count: trait_evidence.length,
      supporting_traits: trait_evidence.map(e => ({
        category: e.trait_category,
        value: e.trait_value,
        prevalence_percent: roundPct(e.prevalence)
      })),
      interaction_factor,
      interactions_applied,
      risk_after_interaction: afterInteraction,
      risk_after_interaction_percent: roundPct(afterInteraction)
    });
  }

  return results.sort((a, b) => b.risk_after_interaction - a.risk_after_interaction);
}

module.exports = {
  CATEGORY_WEIGHTS,
  TOTAL_TRAIT_CATEGORIES,
  clampRisk,
  clampInteractionFactor,
  roundPct,
  computeEvidenceScores,
  computeSummedPrevalence,
  computeWeightedBaseRisk,
  computeConfidence
};
