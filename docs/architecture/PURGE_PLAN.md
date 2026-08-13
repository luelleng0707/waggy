# PURGE_PLAN

This is a phased non-execution purge plan for later approval.

## Batch A - Pure documentation/scaffolding
### Batch A execution status (Omega9.6B)
- Executed archive move for `repository/api/`, `repository/frontend/`, `repository/docs/`.
- Archived under `legacy/archive/omega9.6b/repository/...` with byte-hash parity.
- No runtime/config import dependencies detected at execution time.

- Files: README/scaffold-only directories from `SCAFFOLDING_AUDIT.csv` marked `ARCHIVE_CANDIDATE`.
- Checks: zero importers, no unique authoritative documentation.
- Tests: architecture checks plus smoke regression.
- Rollback: restore archived files via git.

## Batch B - Dead/unused legacy code
- Files: `LEGACY_AUDIT.csv` rows with `SAFE_ARCHIVE` and zero dependents.
- Checks: dependency graph and reference scan.
- Tests: full regression suites.
- Rollback: restore legacy files from git.

## Batch C - Duplicate architecture
- Files: duplicate concept rows with approved canonical targets.
- Checks: import replacement proof and behavior parity tests.
- Tests: formula/mathematics/math_debugger plus API contract checks.
- Rollback: revert migration batch commit.

## Batch D - app to repository cutover
- Files: app/runtime modules selected after runtime ownership approval.
- Checks: endpoint parity, payload parity, trace parity.
- Tests: full regression and health checks.
- Rollback: revert start command and adapters.

## Batch E - reasoning/mathematics consolidation
- Files: `REASONING_MATHEMATICS_MIGRATION.csv` approved rows.
- Checks: dependency parity and replay hash parity.
- Tests: mathematics/formulas/math_debugger suites mandatory.
- Rollback: revert package migration batch.

## Batch F - final legacy purge
- Files: residual legacy files with zero dependencies after prior batches.
- Checks: no active dependencies and documentation retained.
- Tests: full regression and warehouse validation baseline compare.
- Rollback: restore from git.
