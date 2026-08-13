# PRESENTATION_CONTRACT

1. UI cannot implement scientific calculations.
2. UI cannot directly read warehouse CSVs.
3. UI cannot invent evidence.
4. UI cannot invent recommendation scores.
5. UI cannot duplicate optimization logic.
6. UI consumes API/application contracts only.
7. Presentation adapters translate request/response shapes only.
8. Developer trace may expose deeper internal provenance.
9. Customer UI presents simplified provenance from existing outputs.
10. Scientific runtime remains independently testable from presentation.
11. Remote gateway exposes presentation surface only.
12. Internal API/debug services remain local unless explicitly configured.
13. Developer trace must mark unavailable provenance explicitly and must not synthesize equations/citations/row IDs/replay outputs.
14. Execution status is independent from documentation, replay, scientific validation, and publication readiness.

## Enforced by tests

- `tests/interface/test_omega96f_presentation.py`
- `tests/interface/test_local_interface_routes.py`
- `tests/architecture/*` and scientific suite regressions
