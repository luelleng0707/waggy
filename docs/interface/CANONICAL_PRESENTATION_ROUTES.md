# CANONICAL_PRESENTATION_ROUTES

## Route contract

| Route | Purpose | Access | Backend dependency | Data visibility | Read/write |
|---|---|---|---|---|---|
| `/` | Customer presentation | Public | `PPIEWellnessAgent` via `/api/v1/clinical-report` | Customer-safe analysis output only | Read-only |
| `/business` | Executive/business presentation | Optional key gate (`WAGTOPIA_BUSINESS_ACCESS_KEY`) | Same runtime via `/api/v1/presentation/three-surfaces` | Runtime-backed business projection, no developer internals | Read-only |
| `/developer` | Canonical developer presentation | Optional key gate (`WAGTOPIA_DEVELOPER_ACCESS_KEY`) + debug APIs require debug mode | Same runtime via `/api/v1/ppie/validation-console` | Execution provenance and debug trace details | Read-only |

## Compatibility route

| Route | Classification | Notes |
|---|---|---|
| `/debug/calculation` | `INTERNAL_DEBUG_ENDPOINT` + `ACTIVE_COMPATIBILITY` | Preserved for compatibility; serves same HTML shell as `/developer`; not canonical in docs or launcher output. |

## Reference classification (Ω9.7A audit)

| Reference | Classification | Action |
|---|---|---|
| `legacy/ppie-dev-menu.js` old `/debug/calculation?debug=1` links | `REQUIRED_UPDATE` | Updated to `/developer` anchors. |
| `legacy/ppie-shell.js` console link | `REQUIRED_UPDATE` | Updated to `/developer`. |
| `legacy/ppie-trace.js` explorer link | `REQUIRED_UPDATE` | Updated to `/developer`. |
| `tests/interface/test_debug_calculation_runtime.py` | `ACTIVE_COMPATIBILITY` | Kept to assert compatibility route still works. |
| `docs/architecture/OMEGA9.6F_REPORT.md` historical references | `STALE_DOCUMENTATION` | Left as historical report, not canonical source. |
