# Phase 5 Governance & Developer Platform

## One-command release

```bash
py -3 -m science_pipeline.release
# faster iteration:
py -3 -m science_pipeline.release --dogs 10 --skip-parity
```

## Research queries

```bash
py -3 developer_tools/research/queries.py papers-by-condition "Hip Dysplasia"
py -3 developer_tools/research/queries.py ingredients-by-mechanism "cartilage"
py -3 developer_tools/research/queries.py conditions-by-breed "Labrador"
py -3 developer_tools/research/queries.py recs-by-paper paper_018
py -3 developer_tools/research/queries.py products-by-condition "Hip"
py -3 developer_tools/research/queries.py compare warehouse/releases/2026.07.21 warehouse/draft/2026.07.21
```

## Dashboard

Open `developer_tools/dashboards/index.html` after a release run.

## Principles

- No clinical formula changes
- No recommendation logic changes
- Every change answers who / why / paper / formulas / breeds / recommendations / parity / confidence / rollback
