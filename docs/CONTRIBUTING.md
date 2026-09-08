# Contributing

## Clinical / scientific safety

1. Do not change formula math or nutrient minima/maxima without tests and an explicit provenance note.
2. Warehouse edits are facts. Do not invent paper quotes, AAFCO tables, or breed-disease diagnoses.
3. Demo overlay data (`WAGTOPIA_DEMO_MODE`) is synthetic. Do not relabel it as warehouse evidence.
4. `PACKAGE_OPTIMIZER_V2_1` is the only package composer. Do not add a frontend or LLM composer.

## Day-to-day

```bash
py -3 -m pip install -r requirements.txt
py -3 scripts/run_dev.py
py -3 -m pytest -q
```

API module: `app.api.main:app` (shim: `app.main:app`).

## Docs

Read [docs/WAGGY_SYSTEM.md](WAGGY_SYSTEM.md). It is the only architecture specification.
