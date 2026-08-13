# OMEGA9.6F_REPORT

## 1) Customer UI architecture

- Customer presentation remains `legacy/index.html` + `legacy/app.js` + `legacy/ppie-shell.js`.
- UI now includes explicit controls for:
  - `Load Demo Dog`
  - `Analyze`
  - `Dog Profile` editor
- Customer profile submission posts to existing `/api/v1/clinical-report`; no scientific math was added in frontend.

## 2) Developer UI architecture

- Developer route remains canonical: `/debug/calculation?debug=1`.
- Developer page uses existing `legacy/debug/calculation.html` + `legacy/ppie-validation-console.js`.
- No typo route endpoint was added.

## 3) Desktop architecture

- Native CSTC shell remains `py -3 -m app.ui.cstc`.
- Presentation adapter boundary remains `app/ui/cstc/adapter.py`.

## 4) Gateway architecture

- Local suite gateway: `scripts/run_wagtopia_local.py`.
- Remote customer-only gateway: `scripts/run_wagtopia_remote.py`.
- Remote gateway permits only customer-facing API routes and blocks debug/internal paths.

## 5) Remote testing architecture

Remote tester -> HTTPS tunnel -> local gateway `:8080` -> proxied customer API routes -> local API `:8000` -> `PPIEWellnessAgent`.

Public URL observed during execution:

- `https://lien-neighbourless-apollo.ngrok-free.dev/`

## 6) Runtime ownership

- Current runtime owner remains app path:
  - `app.main -> app.api.main -> app.agent.engine.PPIEWellnessAgent`
- Repository v2 remains parallel/test-focused.

## 7) Presentation adapter boundary

- Adapter remains translation-only:
  - request mapping (`AnalyzeDogRequest` -> API payload)
  - response normalization (`AnalysisPresentation`)
- No scientific/runtime replacement performed.

## 8) Demo profile

- Canonical deterministic demo profile: `mixed_lab_golden` (`Dolly`).
- Customer UI `Load Demo Dog` now sets this profile explicitly.

## 9) Routes

- Customer: `http://127.0.0.1:8080/`
- Developer: `http://127.0.0.1:8080/debug/calculation?debug=1`
- API: `http://127.0.0.1:8000/`
- Health: `/health` local and proxied

## 10) Public exposure boundary

- Remote launcher exposes only gateway port `8080`.
- API `8000` is explicitly local-only in remote output block.
- Blocked in remote mode: `/debug/*`, `/api/v1/ppie/*`, `/api/v1/science/*`, `/api/v1/graph/*`.

## 11) Security limitations

- Development/test setup only, not production-secure.
- Tunnel URL is public if shared.
- Optional ngrok account/auth controls documented in `docs/interface/REMOTE_TESTING.md`.

## 12) Claim coverage

- New matrix: `docs/interface/CUSTOMER_UI_CLAIM_COVERAGE.csv`.
- VERIFIED claims are surfaced from real runtime outputs.
- PARTIAL and NOT_IMPLEMENTED claims are explicitly labeled; no fabricated features.

## 13) Tests

- `pytest tests/interface -q` -> 22 passed
- `pytest tests/architecture -q` -> 28 passed
- `pytest tests/mathematics -q` -> 13 passed
- `pytest tests/formulas -q` -> 3 passed
- `pytest tests/math_debugger -q` -> 20 passed
- `pytest tests/optimization -q` -> 6 passed
- `pytest tests/science_graph -q` -> 6 passed
- `pytest tests/warehouse_qa -q` -> 6 passed

## 14) Benchmark hash

- Pre-change hash: `77ca5815c5e8c59c647912de1c9413e157411448405ccf8e1c802ebfd9348cee`
- Post-change hash: `77ca5815c5e8c59c647912de1c9413e157411448405ccf8e1c802ebfd9348cee`
- Result: unchanged.

## 15) Known limitations

- Some evidence entries have no URL and are marked as curated/pending by runtime.
- Observed vs estimated prevalence is partial for conditions lacking published benchmark fields.
- Customer UI still depends on current legacy shell framework (intentional in Ω9.6F).

## 16) Remaining architectural work

- If/when cutover is approved, migrate runtime ownership from app path to repository path behind unchanged presentation/API contracts.
- Expand non-computational adapter projections for richer mechanism/evidence labeling where runtime fields exist.
- Keep debug/developer surfaces local by default for future remote demos.

## Warehouse blocker status

- `py -3 scripts/validate_warehouse.py` -> FAIL (expected).
- Known 8 broken references remain unchanged and visible in `docs/validation_report.md`.
