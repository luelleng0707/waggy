# Formulas

Every formula ID, production flag, and scoring rule for the current engine.

**Policy:** Proprietary equation *text* is not exposed in public APIs. Traces and the Validation Console use **formula IDs** only (`equation_exposed: false`).

**Registry SoT:** `app/inference/formula_registry.py` (`FORMULA_REGISTRY`). Do not redefine ID strings elsewhere.

---

## Registry (current)

| Formula ID | Production | Owner (typical) | Purpose |
|------------|------------|-----------------|---------|
| `PROFILE_NORMALIZE_V2_1` | Yes | `payload_adapter` | Normalize request → profile |
| `BREED_RESOLVE_V2_1` | Yes | `biological` | Aliases → breed rows |
| `TRAIT_BLEND_V2_1` | Yes | `biological` | Mixed-breed trait blend |
| `RISK_V2_1` | Yes | `health_risk` | Condition ranking (locked parity) |
| `RISK_TRACE_V1` | No | inference / console | Observability ledger helper |
| `NUTRIENT_TARGET_V2_1` | Yes | `nutrition` | Condition → daily targets |
| `NUTRIENT_EST_V1` | No | `inference.ingredient` | Estimate nutrient from composition (`enabled=False`) |
| `ING_FRAC_ORDER_V1` | No | `inference.ingredient` | Fractions from ingredient order (`enabled=False`) |
| `ACTIVITY_V2_1` | Yes | management / activity | Activity prescription |
| `PRODUCT_MATCH_V2_1` | Yes | optimization | Catalog matching |
| `COVERAGE_V2_1` | Yes | optimizer / package_detail | provided ÷ recommended |
| `PACKAGE_OPTIMIZER_V2_1` | Yes | `package_optimizer` | Tier packages + overall score |
| `CONDITION_SUPPORT_V1` | No | inference | Opt-in support blend (`enabled=False`) |
| `EVIDENCE_RANK_V2_1` | Yes | assembler / evidence | Attach & rank evidence |
| `VALIDATION_V2_1` | Yes | validation slots | Benchmarks when available |
| `ASSESSMENT_PROJECT_V1` | Yes | `clinical_assessment` | Project analyze → modules (no recompute) |
| `CONF_V1` | No | `inference.confidence` | Ladder metadata; does not overwrite production confidence |

---

## Dependency sketch

```text
PROFILE_NORMALIZE
    → BREED_RESOLVE → TRAIT_BLEND
        → RISK_V2_1 → NUTRIENT_TARGET / EVIDENCE_RANK / ACTIVITY
            → PRODUCT_MATCH → COVERAGE → PACKAGE_OPTIMIZER
                → ASSESSMENT_PROJECT
```

Opt-in: `NUTRIENT_EST_V1`, `ING_FRAC_ORDER_V1`, `CONDITION_SUPPORT_V1`, `RISK_TRACE_V1`, `CONF_V1`.

---

## RISK_V2_1

| | |
|--|--|
| **Status** | Production / PARTIAL vs full multiplicative ledger |
| **Owner** | `app/agent/stages/health_risk.py` |
| **Purpose** | Rank preventative conditions for a dog |
| **Intended shape** | baseline × trait × interaction × climate × age × weight × activity (− benefits) |
| **Current** | Trait evidence scores, benefits, mixed-breed nudge, significance / confidence (JS parity). Per-modifier intermediates often not emitted |
| **CSV** | `*_CONDITIONS.csv`, trait interactions / benefits, mixed matrices |
| **Outputs** | risk %, confidence %, supporting traits |
| **Debug** | Validation Console Risk tab expands chain slots; missing steps = `NOT CURRENTLY TRACEABLE` |

Changing risk math requires approval + golden/parity suites.

---

## NUTRIENT_TARGET_V2_1

| | |
|--|--|
| **Status** | Production |
| **Purpose** | Daily nutrient / ingredient targets from conditions |
| **CSV** | `NUTRIENT_PRIORITIES.csv`, `CONDITION_INGREDIENTS.csv`, protocols |
| **Outputs** | targets with units for coverage |

---

## COVERAGE_V2_1

| | |
|--|--|
| **Status** | Production |
| **Equation** | `coverage = provided_amount / recommended_amount` (often ×100 for display) |
| **Inputs** | Nutrition targets; food + supplement contributions |
| **Confidence** | Follows whether `provided` is declared vs estimated |

---

## PACKAGE_OPTIMIZER_V2_1

| | |
|--|--|
| **Status** | Production (locked weights) |
| **Owner** | `app/agent/package_optimizer.py` |
| **Live weights** (`SCORE_WEIGHTS`) | coverage **0.35** · clinical_function **0.25** · evidence **0.20** · cost_efficiency **0.15** · diversity **0.05** (− surplus penalty) |
| **Not adopted** | 9-term alternate blend (quality / breed / age / …) — would need approval + goldens |
| **Rule** | Catalog joins only — no hardcoded product IDs in the formula |

---

## PRODUCT_MATCH_V2_1

Matches catalog products to nutrient / condition needs via composition and evidence. Rejected-candidate ledgers are not fully emitted to debug yet.

---

## Opt-in: NUTRIENT_EST_V1 (F1)

| | |
|--|--|
| **Status** | Implemented, `enabled=False` |
| **Equation** | `estimated_nutrient = Σ (ingredient_fraction × nutrient_density)` |
| **Data** | `INGREDIENT_NUTRIENT_ESTIMATES.csv` (scientific densities) |
| **Confidence** | ~80% declared fractions · ~70% order-estimated · ~60% taxonomy |

---

## Opt-in: ING_FRAC_ORDER_V1 (F2)

| | |
|--|--|
| **Status** | Implemented, `enabled=False` |
| **Purpose** | Estimate mass fractions from descending ingredient order |
| **Default profile** | 35%, 22%, 16%, 10%, 6%, remainder split (Python `INGREDIENT_ORDER_PERCENTS`) |
| **Confidence** | ~70% |

---

## Opt-in: CONDITION_SUPPORT_V1 (F5)

Proposed: `support = Σ (coverage_i × evidence_weight_i × priority_i)`. Production packages fold clinical_function + evidence into overall score instead.

---

## CONF_V1 (ladder — not production overwrite)

| Source class | Confidence |
|--------------|------------|
| Declared laboratory value | 100% |
| Manufacturer guaranteed analysis | 95% |
| Calculated from guaranteed analysis | 90% |
| Calculated from ingredient percentages | 80% |
| Estimated from ingredient order | 70% |
| Estimated from taxonomy | 60% |
| Estimated from similar ingredient | 45% |
| Unknown | 0% |

Target shape for inferred fields: `{ value, confidence, source, formula_id }`. Production risk confidence still comes from the locked health_risk path until wired.

---

## EVIDENCE_RANK_V2_1 / VALIDATION_V2_1

- Evidence: attach literature rows; never fabricate PMIDs or citations.  
- Validation: benchmark object or explicit `unavailable` + reason.  
- Levels used in contracts: `high` | `moderate` | `emerging` | `guideline` | `pending`.

---

## ASSESSMENT_PROJECT_V1

Projects frozen analyze into ClinicalAssessment modules. **No formula re-entry.** If a module looks wrong, fix the upstream stage — not the projector.

---

## Change control

1. Changing **production** clinical risk, nutrition targets, or package scores → approval batch + golden/parity tests + algorithm version bump.  
2. Algorithmic weights stay in **Python** (`app/inference/config.py`, optimizer). Do not move scoring coefficients into CSV.  
3. Scientific baselines, densities, and evidence stay in **CSV**.  
4. New formula IDs must be added to `FORMULA_REGISTRY` in the same change as the code.
