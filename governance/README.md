# Phase 5 — Data Governance

This tree holds **reviewable artifacts**, not clinical execution code.

| Path | Purpose |
|------|---------|
| `review/` | Scientific review checklists & decisions |
| `releases/` | Per-release `YYYY.MM.DD.json` metadata + version tags |
| `migrations/` | Planned science data migrations |
| `changelogs/` | Human + generated CHANGELOG |
| `validation/` | `SCIENCE_VALIDATION_REPORT.md` |
| `reports/` | Benchmark, health, performance, impact, release summaries |

## Workflow

```
Draft → Validation → Scientific Review → Approved → Published → Production
```

Never edit production science directly. Use:

```bash
py -3 -m science_pipeline.release
```

Clinical formulas and recommendation logic must remain unchanged across governance releases.
