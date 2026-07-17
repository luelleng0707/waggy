'use strict';

const { ingredientKey } = require('../api/db/normalize');

function calculateDose(link, weightKg) {
  const dose = parseFloat(link.recommended_daily_dose ?? link.dose_min);
  const unit = link.dose_unit || link.unit;

  let daily;
  if (link.dose_basis === 'mg_per_kg') {
    daily = Math.round(weightKg * dose);
  } else {
    daily = Math.round(dose);
  }

  return { daily, monthly: daily * 30, yearly: daily * 365, unit };
}

module.exports = { calculateDose, ingredientKey };
