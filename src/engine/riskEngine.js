'use strict';

const { resolveBreeds } = require('./breedResolver');
const { collectTraitRisks } = require('./traitResolver');
const { computeEvidenceScores, clampRisk, roundPct } = require('./overlapEngine');
const { applyBenefitReductions } = require('./benefitEngine');
const { applySignificanceLogic } = require('./significanceEngine');

function getAgeStage(birthday) {
  const birth = new Date(birthday);
  const ageYears = (Date.now() - birth.getTime()) / (365.25 * 24 * 60 * 60 * 1000);
  let stage = 'adult';
  if (ageYears < 1) stage = 'puppy';
  else if (ageYears >= 7) stage = 'senior';
  return { ageYears: Math.round(ageYears * 10) / 10, stage };
}

function computeRisks(payload) {
  const { breeds: breedNames, birthday, observed_conditions = [] } = payload;
  const breeds = resolveBreeds(breedNames);
  const { ageYears, stage } = getAgeStage(birthday);

  const traitRisks = collectTraitRisks(breeds);
  const evidenceScores = computeEvidenceScores(traitRisks, breeds);
  const withBenefits = applyBenefitReductions(evidenceScores, breeds);
  const finalRisks = applySignificanceLogic(
    breeds,
    breeds.map(b => b.breed_name),
    withBenefits,
    observed_conditions
  );

  if (stage === 'senior') {
    for (const r of finalRisks) {
      r.risk_decimal = clampRisk(r.risk_decimal * 1.05);
      r.risk_percent = roundPct(r.risk_decimal);
      r.age_adjusted = true;
    }
  }

  return {
    risks: finalRisks,
    meta: { ageYears, ageStage: stage, breedCount: breeds.length, breeds: breeds.map(b => b.breed_name) }
  };
}

module.exports = { computeRisks, getAgeStage };
