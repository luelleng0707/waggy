'use strict';

const db = require('../api/db/queries');
const { clampRisk, roundPct } = require('./overlapEngine');

function applyBenefitReductions(evidenceScores, breeds) {
  const benefits = db.getTraitBenefits(breeds);

  return evidenceScores.map(risk => {
    const key = risk.condition_key || risk.condition_name;
    const benefit = benefits.find(b =>
      b.condition_key === key || b.condition_name === risk.condition_name
    );

    if (!benefit) {
      return {
        ...risk,
        benefit_factor: 1,
        benefit_applied: null,
        final_trait_risk: risk.risk_after_interaction,
        final_trait_risk_percent: risk.risk_after_interaction_percent
      };
    }

    const factor = parseFloat(benefit.reduction_factor) || 1;
    const final = clampRisk(risk.risk_after_interaction * factor);

    return {
      ...risk,
      benefit_factor: factor,
      benefit_applied: benefit,
      final_trait_risk: final,
      final_trait_risk_percent: roundPct(final)
    };
  });
}

module.exports = { applyBenefitReductions };
