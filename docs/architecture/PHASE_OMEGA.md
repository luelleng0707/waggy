# Phase Ω — PPIE Platform Completion

Core clinical architecture is **frozen**:

```
Warehouse → Repository → ExecutionContext → FormulaGraph → AssessmentResult
```

Python package: **`ppie_platform`** (stdlib `platform` must not be shadowed). Layout pointer: `platform/README.md`.

## One command

```bash
py -3 -m ppie_platform.omega --quick
py -3 -m ppie_platform.omega
py -3 -m ppie_platform.omega --rollback 2026.07.20
```

## Self-inspection APIs

All require `x-api-key`:

- `GET /api/v1/platform/status`
- `GET /api/v1/platform/runtime`
- `GET /api/v1/platform/dependencies`
- `GET /api/v1/platform/formulas`
- `GET /api/v1/platform/science`
- `GET /api/v1/platform/performance`
- `GET /api/v1/platform/coverage`
- `GET /api/v1/platform/release`
- `GET /api/v1/platform/audit`

Dashboard: `/platform/dashboard` (after omega run)

## Artifacts

| Area | Path |
|------|------|
| Observatories | `ppie_platform/observability/reports/` |
| Meta docs | `meta/architecture/` |
| Quality | `quality/reports/` |
| Snapshots | `operations/snapshots/` |
| Security | `ppie_platform/security/SECURITY_AUDIT.md` |
| SDK | `ppie_platform/sdk/generated/` |
