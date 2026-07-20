# Onboarding — Scientific Platform

1. Read `docs/PROJECT_STATUS.md` (generated).
2. Read `PROJECT_ARCHITECTURE.md` for clinical path.
3. Open `developer_tools/dashboards/index.html`.
4. Run `py -3 -m science_pipeline.release --dogs 5 --skip-parity` to see artifacts.
5. Use `developer_tools/research/queries.py` for deterministic lookups.
6. Never edit `warehouse/production/` by hand.

Clinical math lives in `app/agent/stages/*` and FormulaGraph nodes that wrap them.
Phase 5 only adds governance around `data/` + `warehouse/`.
