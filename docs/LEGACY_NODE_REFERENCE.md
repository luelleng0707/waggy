# Legacy Node PPIE Reference

**Migration completion date:** 2026-07-17  
**Status:** Node runtime **retired**. Python is the sole production implementation.  
**Archive tag:** `legacy-node-final`  
**Archive commit:** `8575606`  
**Retirement commit:** `0976b82`

---

## Why Node was retired

1. Runtime, formula, CSV, and output-contract parity reached **0 diffs** on Dolly.
2. A **10-profile** regression matrix passed, including three consecutive zero-diff runs.
3. Production HTTP routes were re-hosted on FastAPI with identical contracts.
4. Golden JSON fixtures replaced live Node comparison as the regression baseline.

Node is historical reference material only. Do not resurrect it for production.

---

## How to recover the legacy tree

```bash
git checkout legacy-node-final
# or inspect without switching:
git show legacy-node-final:src/engine/index.js
```

Git history is the archive. Do **not** paste JavaScript into Python comments.

---

## Final parity summary (pre-retirement)

| Check | Result |
|-------|--------|
| Dolly runtime diffs | 0 |
| Profiles matched | 10/10 |
| Consecutive suite runs | 3 × 0 diffs |
| Pricing / confidence / PNS / packages | Identical within tolerance |
| Output top-level keys | Identical |

---

## Module mapping (Node → Python)

| Legacy Node | Canonical Python |
|-------------|------------------|
| `src/engine/index.js` (`analyze`) | `app/agent/engine.py` + `app/agent/response_assembler.py` |
| `src/engine/breedResolver.js` | `app/agent/stages/biological.py`, `app/agent/utils.py` |
| `src/engine/traitResolver.js` | `app/agent/stages/health_risk.py` (`collect_trait_risks`) |
| `src/engine/overlapEngine.js` | `app/agent/stages/health_risk.py` (evidence / confidence) |
| `src/engine/benefitEngine.js` | `app/agent/stages/health_risk.py` (`apply_benefit_reductions`) |
| `src/engine/significanceEngine.js` | `app/agent/stages/health_risk.py` (`apply_significance_logic`) |
| `src/engine/riskEngine.js` | `app/agent/stages/health_risk.py` (`compute_risks`) |
| Epidemiology CSV union | `app/agent/stages/epidemiology.py` (legacy path; overridden by health_risk) |
| `src/engine/ingredientEngine.js` | `app/agent/ingredient_engine.py` |
| `src/engine/dosageEngine.js` | `app/agent/ingredient_engine.py` |
| `src/engine/productEngine.js` | `app/api/evidence.py` + `app/agent/stages/optimization.py` |
| `src/engine/wellnessEngine.js` | `app/agent/response_assembler.py` |
| `src/engine/wellnessMap.js` | `app/agent/wellness_map.py` |
| `src/engine/packageDetailEngine.js` | `app/agent/package_detail.py` |
| `src/engine/bundleEngine.js` | `app/agent/bundle_engine.py` |
| `src/engine/pipelineEngine.js` | `app/agent/pipeline_trace.py` |
| `src/engine/variableMap.js` | `app/agent/variable_map.py` |
| `src/engine/evidenceEngine.js` | `app/api/evidence.py` |
| `src/api/routes.js` | `app/api/main.py` |
| `server.js` | `uvicorn app.main:app` |
| `server/logic.js` (`computeRecommendations`) | `/api/recommendations` → `map_legacy_response` |

---

## What remains in the working tree

| Asset | Role |
|-------|------|
| `app.js` / `index.html` / `styles.css` | Static demo UI (no engine `require`) |
| `tests/parity/*/js_response.json` | Forensic Node snapshots (optional) |
| `docs/*` | Algorithm / CSV / schema / migration docs |
| `tests/golden/*.json` | Canonical regression fixtures |

---

## Future development

- Change algorithms only in `app/agent/`.
- Bump `app/agent/version.py` (`ALGORITHM_VERSION`) when behavior changes.
- Freeze fixtures: `py -3 tools/parity_suite.py --freeze`.
- Never reintroduce `src/engine` or `server.js` into production paths.
