'use strict';

const db = require('../api/db/queries');
const { conditionKey } = require('../api/db/normalize');
const { clampRisk, roundPct } = require('./overlapEngine');

function resolveGroomerBoosts(observedConditions) {
  const groomerBoosts = {};
  const map = db.getStore().groomerConditionMap || {};

  for (const obs of observedConditions) {
    const raw = (obs || '').toLowerCase().replace(/\s+/g, '_');
    const condition = map[raw];
    if (condition) {
      const key = conditionKey(condition);
      groomerBoosts[key] = true;
    }
  }
  return groomerBoosts;
}

function buildTraitContext(traitScores, conditionKeyVal) {
  const trait = traitScores.find(t =>
    t.condition_key === conditionKeyVal || t.condition_name === conditionKeyVal
  );
  if (!trait) return null;

  const interactionPct = Math.round((trait.interaction_factor - 1) * 1000) / 10;
  const benefitPct = trait.benefit_applied
    ? Math.round((1 - trait.benefit_factor) * 1000) / 10
    : 0;

  return {
    trait_risk_percent: trait.final_trait_risk_percent,
    trait_risk_decimal: trait.final_trait_risk,
    confidence_percent: trait.confidence_percent,
    evidence_count: trait.evidence_count,
    supporting_traits: trait.supporting_traits,
    trait_evidence: trait.trait_evidence,
    interaction_adjustment_percent: interactionPct,
    benefit_adjustment_percent: benefitPct,
    interaction_factor: trait.interaction_factor,
    benefit_factor: trait.benefit_factor
  };
}

function applyMixedBreedNudge(traitRiskDecimal, conditionKeyVal, breedNames) {
  const matrix = db.getMixedBaselines(breedNames).filter(m =>
    m.condition_key === conditionKeyVal
  );

  if (!matrix.length) {
    return { risk: traitRiskDecimal, mixed_breed_factor: 1, mixed_breed_sources: [] };
  }

  let factor = 1;
  for (const row of matrix) {
    const f = parseFloat(row.factor) || 1;
    factor *= Math.min(1.20, Math.max(0.80, f));
  }
  factor = Math.min(1.20, Math.max(0.80, factor));

  return {
    risk: clampRisk(traitRiskDecimal * factor),
    mixed_breed_factor: factor,
    mixed_breed_sources: matrix
  };
}

function applySignificanceLogic(breeds, breedNames, traitScores, observedConditions = []) {
  const observed = db.getBreedObservedRisks(breedNames);
  const isPurebred = breedNames.length === 1;
  const groomerBoosts = resolveGroomerBoosts(observedConditions);
  const traitMap = Object.fromEntries(
    traitScores.map(t => [t.condition_key, t])
  );

  if (isPurebred) {
    return observed
      .map(obs => {
        const ctx = buildTraitContext(traitScores, obs.condition_key);
        const groomer_boosted = !!groomerBoosts[obs.condition_key];

        return {
          condition_name: obs.condition_name,
          condition_key: obs.condition_key,
          risk_percent: roundPct(obs.prevalence),
          risk_decimal: clampRisk(obs.prevalence),
          breed_prevalence_percent: roundPct(obs.prevalence),
          trait_risk_percent: ctx?.trait_risk_percent ?? null,
          confidence_percent: ctx?.confidence_percent ?? 0,
          evidence_count: ctx?.evidence_count ?? 0,
          supporting_traits: ctx?.supporting_traits ?? [],
          interaction_adjustment_percent: ctx?.interaction_adjustment_percent ?? 0,
          benefit_adjustment_percent: ctx?.benefit_adjustment_percent ?? 0,
          mixed_breed_adjustment_percent: 0,
          logic: 'purebred_observed',
          groomer_boosted,
          trait_explanation: traitMap[obs.condition_key] || null,
          source: {
            source_name: obs.source_name,
            source_quote: obs.source_quote,
            source_url: obs.source_url,
            breed: obs.breed_name
          }
        };
      })
      .sort((a, b) => {
        if (a.groomer_boosted !== b.groomer_boosted) return b.groomer_boosted - a.groomer_boosted;
        return b.risk_percent - a.risk_percent;
      });
  }

  const results = [];
  const merged = new Map();

  for (const trait of traitScores) {
    const { risk: nudged, mixed_breed_factor, mixed_breed_sources } =
      applyMixedBreedNudge(trait.final_trait_risk, trait.condition_key, breedNames);

    const groomer_boosted = !!groomerBoosts[trait.condition_key];
    const mixedPct = Math.round((mixed_breed_factor - 1) * 1000) / 10;
    const breedEvidence = observed.filter(o => o.condition_key === trait.condition_key);

    merged.set(trait.condition_key, {
      condition_name: trait.condition_name,
      condition_key: trait.condition_key,
      risk_percent: roundPct(nudged),
      risk_decimal: nudged,
      trait_risk_percent: trait.final_trait_risk_percent,
      breed_prevalence_percent: breedEvidence.length
        ? roundPct(Math.max(...breedEvidence.map(b => b.prevalence)))
        : null,
      confidence_percent: trait.confidence_percent,
      evidence_count: trait.evidence_count,
      supporting_traits: trait.supporting_traits,
      interaction_adjustment_percent: Math.round((trait.interaction_factor - 1) * 1000) / 10,
      benefit_adjustment_percent: trait.benefit_applied
        ? Math.round((1 - trait.benefit_factor) * 1000) / 10
        : 0,
      mixed_breed_adjustment_percent: mixedPct,
      mixed_breed_factor,
      logic: 'mixed_trait_estimate',
      groomer_boosted,
      trait_explanation: trait,
      mixed_breed_sources,
      breed_evidence: breedEvidence,
      source: breedEvidence[0]
        ? {
            source_name: breedEvidence[0].source_name,
            source_quote: breedEvidence[0].source_quote,
            source_url: breedEvidence[0].source_url,
            breed: breedEvidence.map(b => b.breed_name).join(' × ')
          }
        : null
    });
  }

  // Multi-breed union (OR): include breed liabilities even when trait aggregation missed them.
  for (const obs of observed) {
    const groomer_boosted = !!groomerBoosts[obs.condition_key];
    const existing = merged.get(obs.condition_key);
    if (existing) {
      const unionPrevalence = Math.max(existing.risk_decimal, obs.prevalence);
      existing.risk_decimal = clampRisk(unionPrevalence);
      existing.risk_percent = roundPct(existing.risk_decimal);
      existing.breed_prevalence_percent = Math.max(
        existing.breed_prevalence_percent ?? 0,
        roundPct(obs.prevalence)
      );
      existing.breed_evidence = [...(existing.breed_evidence || []), obs];
      existing.logic = 'mixed_breed_union';
      existing.groomer_boosted = existing.groomer_boosted || groomer_boosted;
      continue;
    }

    const ctx = buildTraitContext(traitScores, obs.condition_key);
    merged.set(obs.condition_key, {
      condition_name: obs.condition_name,
      condition_key: obs.condition_key,
      risk_percent: roundPct(obs.prevalence),
      risk_decimal: clampRisk(obs.prevalence),
      trait_risk_percent: ctx?.trait_risk_percent ?? null,
      breed_prevalence_percent: roundPct(obs.prevalence),
      confidence_percent: ctx?.confidence_percent ?? 0,
      evidence_count: ctx?.evidence_count ?? 0,
      supporting_traits: ctx?.supporting_traits ?? [],
      interaction_adjustment_percent: ctx?.interaction_adjustment_percent ?? 0,
      benefit_adjustment_percent: ctx?.benefit_adjustment_percent ?? 0,
      mixed_breed_adjustment_percent: 0,
      mixed_breed_factor: 1,
      logic: 'mixed_breed_union',
      groomer_boosted,
      trait_explanation: traitMap[obs.condition_key] || null,
      mixed_breed_sources: [],
      breed_evidence: [obs],
      source: {
        source_name: obs.source_name,
        source_quote: obs.source_quote,
        source_url: obs.source_url,
        breed: obs.breed_name
      }
    });
  }

  const anchor = Math.min(
    ...traitScores.map(t => t.final_trait_risk).filter(v => v > 0),
    1
  ) || 0.05;

  return [...merged.values()]
    .filter(r => r.risk_decimal >= anchor || r.groomer_boosted)
    .sort((a, b) => {
      if (a.groomer_boosted !== b.groomer_boosted) return b.groomer_boosted - a.groomer_boosted;
      return b.risk_percent - a.risk_percent;
    });
}

module.exports = { applySignificanceLogic };
