# TARGET_ARCHITECTURE

## Runtime ownership (current and target)
- Current production entrypoint: `app/main.py -> app/api/main.py`.
- Target state: preserve API/frontend contracts while progressively consolidating domain runtime into `repository/`.

## Presentation ownership

### A. Customer-facing presentation
- `legacy/index.html`
- `legacy/app.js`
- `legacy/ppie-shell.js`
- customer route `/` on local gateway

### B. Developer-facing observability
- `legacy/debug/calculation.html`
- `legacy/ppie-validation-console.js`
- developer route `/debug/calculation?debug=1`
- debug APIs `/api/v1/ppie/*`

### C. Native desktop presentation
- `app/ui/cstc/*`
- launch `py -3 -m app.ui.cstc`

### D. Application runtime / transport
- `app/main.py`
- `app/api/main.py`
- gateway scripts (`scripts/run_wagtopia_local.py`, `scripts/run_wagtopia_remote.py`)

## Scientific layer (E/F/G/H)

### E. Scientific runtime
- `app/agent/*` (current runtime owner)
- parallel repository runtime modules for test/audit use

### F. Warehouse
- `warehouse/`
- `repository/warehouse/`
- `repository/science_graph/`

### G. QA / validation
- `repository/validation/`
- `repository/warehouse_qa/`
- `tests/warehouse_qa`

### H. Mathematical audit infrastructure
- `repository/mathematics/`
- `repository/formulas/`
- `repository/math_debugger/`
- `repository/benchmarks/`

## Biological layer
- `repository/pipeline/`
- `repository/models/`

## Reasoning and mathematical layer
- `repository/mathematics/` (current MAT runtime)
- `repository/formulas/` (formula-as-data)
- `repository/math_debugger/` (audit/replay/provenance)
- `repository/reasoning/` (transitional consolidation candidate)

## Nutrition and product layer
- `repository/optimization/`
- related mechanism/objective/source domains as dependency-proven modules

## Quality layer
- `repository/validation/`
- `repository/warehouse_qa/`
- `repository/benchmarks/`
- `tests/`

## Presentation layer
- `app/api/`
- `app/ui/`
- `legacy/`
- `scripts/run_wagtopia_local.py`
- `scripts/run_wagtopia_remote.py`

## Guardrails
- Preserve Omega 9.5 formula disposition boundaries.
- Preserve known warehouse blockers transparently.
- Do not purge scientific CSVs without explicit retention classification.
- Presentation layers consume API/application contracts only; no scientific logic duplication in UI.
