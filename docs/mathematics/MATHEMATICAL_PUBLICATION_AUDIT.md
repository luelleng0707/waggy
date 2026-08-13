# MATHEMATICAL_PUBLICATION_AUDIT

Production behavior was not modified by this audit. Findings below describe current mathematical provenance and publication risk.

## 1. Scientifically supported formulas
- MAT-1001: Observed epidemiology aggregation from direct observed edges. (implementation traced; provenance quality varies by inputs/parameters).
- MAT-1002: Trait/environment evidence aggregation using weighted log-odds. (implementation traced; provenance quality varies by inputs/parameters).
- MAT-1003: Bayesian-style prevalence update from prior and evidence aggregate. (implementation traced; provenance quality varies by inputs/parameters).
- MAT-1004: Agreement and prediction error mathematics. (implementation traced; provenance quality varies by inputs/parameters).
- MAT-1005: Confidence from evidence depth, study breadth, and agreement quality. (implementation traced; provenance quality varies by inputs/parameters).
- MAT-1006: Novelty scoring and emerging concern detection. (implementation traced; provenance quality varies by inputs/parameters).
- MAT-1007: Priority ranking from prevalence burden, certainty, and novelty. (implementation traced; provenance quality varies by inputs/parameters).
- MAT-1008: Uncertainty and confidence interval calculation. (implementation traced; provenance quality varies by inputs/parameters).

## 2. Scientifically supported parameters
- Count with direct numeric evidence linkage: 0

## 3. Empirically derived parameters
- Classified EMPIRICALLY_DERIVED rows: 0

## 4. Engineering assumptions
- ENGINEERING_PARAMETER rows: 23
- ENGINEERING_THRESHOLD rows: 89380

## 5. Unsupported constants
- REVIEW_REQUIRED constants in code audit: 0

## 6. Methodological ambiguities
- MAT-1003 uses a logit-space weighted blend of prior/evidence and is Bayesian-inspired, not a full posterior with explicit likelihood model: `METHODOLOGICAL_REVIEW_REQUIRED`.
- MAT-1005 confidence score is a composite model score (evidence volume, study count, agreement), not pure scientific confidence.

## 7. Missing evidence
- UNKNOWN classification rows: 309 (all flagged REVIEW_REQUIRED).
- INVALID_PARAMETER_PROVENANCE rows: 0

## 8. Formula/code mismatches
- No deterministic mismatches observed in O9.3 replay checks for active MAT-1001..MAT-1008 traces on warehouse-backed sample run.

## 9. Formula/replay mismatches
- Mismatches detected: 0

## 10. Publication-critical issues
- Unsupported numerical parameters must be explicitly labeled as engineering assumptions in any scientific communication.
- `METHODOLOGICAL_REVIEW_REQUIRED`: MAT-1003 naming and interpretation require explicit caveats before publication.
- Confidence terminology in developer docs should avoid implying direct epistemic certainty from heterogeneous components.