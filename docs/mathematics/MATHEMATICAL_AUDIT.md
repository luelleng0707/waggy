# MATHEMATICAL_AUDIT

## 1. Executive Summary
- Active formula scope audited: MAT-1001, MAT-1002, MAT-1003, MAT-1004, MAT-1005, MAT-1006, MAT-1007, MAT-1008.
- Production mathematics was analyzed in-place with no formula behavior modification.
- Baseline benchmark output hash (SHA256): `b2b200753bc955b6568cbc52c83e88151db65370c58159e9d718a7e0a75b9303`.

## 2. Formula Inventory
- Machine-readable registry: `docs/mathematics/FORMULA_REGISTRY.csv` (8 formulas).
- Dependency graph: `docs/mathematics/FORMULA_DEPENDENCIES.csv` (27 dependency rows).

## 3. Provenance Findings
- A Direct scientific observation: 5
- B Scientifically derived parameter/value: 9
- C Engineering assumption: 8
- D Mathematical constant: 0
- E Unit/normalization constant: 1
- F Computational tolerance: 4
- G Legacy/unresolved: 0
- Most active coefficients in MAT-1002/1005/1006/1007/1008 are engineering assumptions unless explicit numeric evidence is added.

## 4. Replay Results
- MATCH formulas: 8
- MISMATCH formulas: 0
- SKIP formulas: 0
- Detailed replay table: `docs/mathematics/FORMULA_REPLAY.csv`.

## 5. Sensitivity Findings
- MAT-1005:agreement_weight baseline=0.300000, max_relative_change=0.052025
- MAT-1005:evidence_denominator baseline=20.000000, max_relative_change=0.026818
- MAT-1005:study_denominator baseline=10.000000, max_relative_change=0.026487
- MAT-1005:evidence_weight baseline=0.450000, max_relative_change=0.024137
- MAT-1005:study_weight baseline=0.250000, max_relative_change=0.023839
- MAT-1005:observed_multiplier baseline=1.500000, max_relative_change=0.008046
- MAT-1002:max_strength baseline=0.900000, max_relative_change=0.000000
- MAT-1002:min_strength baseline=0.200000, max_relative_change=0.000000

## 6. Double-Counting Risks
- Interaction evidence contributes both to MAT-1002 weighted aggregation and MAT-1003 additive interaction delta.
- Confidence composites (MAT-1005) reuse evidence volume signals already used in prevalence estimation.
- Priority (MAT-1007) multiplies novelty where novelty already includes confidence scaling.

## 7. Mixed-Breed Risks
- Biological resolver currently uses only `profile.breeds[0]` for breed resolution; additional breeds are ignored.
- Mixed-breed dataset contributions are trait-match driven and can overlap with parent-breed and trait evidence channels.

## 8. Environmental Assumptions
- Environment matching is climate-string based and does not independently validate city-specific epidemiological effects.
- Environmental evidence acts as weighted inputs in MAT-1002, with engineering weight assignment.

## 9. Publication Risks
- MAT-1001: MEDIUM - Observed evidence may be sparse or absent for many conditions.
- MAT-1002: HIGH - Output strongly controlled by engineering weights and strength bounds.
- MAT-1003: BLOCKED - Methodological ambiguity: Bayesian-inspired blend, not explicit posterior model.
- MAT-1004: MEDIUM - Agreement is deterministic model-observation score, not statistical confidence.
- MAT-1005: HIGH - Dominant weights are unsupported by direct scientific numeric evidence.
- MAT-1006: HIGH - Emerging concern flag is threshold-based and assumption-sensitive.
- MAT-1007: HIGH - Multiplicative compounding of model-derived signals can amplify assumptions.
- MAT-1008: HIGH - Dispersion heuristic is not a formal epidemiological uncertainty model.

## 10. Required Changes Before Scientific Inference Engine
- Provide explicit numeric provenance for currently engineering-only coefficients.
- Resolve methodological labeling for MAT-1003 Bayesian semantics.
- Address overlap/double-counting across trait/environment/interaction and downstream confidence/priority composition.
- Define mixed-breed blending mathematics explicitly instead of single-breed fallback.
- Separate scientific uncertainty, model uncertainty, and data absence in reporting terminology.