# PPIE Algorithm Versioning

**Current:** PPIE **v2.1.0** (`app/agent/version.py` → `ALGORITHM_VERSION`)

Exposed on:

- Response envelope `version`
- `GET /health` → `version` / `algorithm_version`
- Response header `X-PPIE-Algorithm-Version`

## When to bump

| Change | Version style |
|--------|---------------|
| Bugfix matching locked goldens (no intentional behavior change) | patch optional / usually none |
| Intentional formula or ranking change | **minor** (2.2.0) |
| Breaking response contract | **major** (3.0.0) |

## Required workflow after a behavioral change

1. Edit Python under `app/agent/` only.
2. Update `docs/PPIE_ALGORITHM.md` (and CSV/schema docs if needed).
3. Set `ALGORITHM_VERSION` in `app/agent/version.py`.
4. Run `py -3 tools/parity_suite.py --freeze`.
5. Commit `tests/golden/*.json` with a message explaining **why** fixtures changed.
6. Run `py -3 tools/parity_suite.py --repeat 3`.

Do not regenerate goldens casually.
