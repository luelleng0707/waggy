# tests/golden

Frozen PPIE response fixtures for algorithm version **2.1.0**.

These are the permanent regression baseline. Compare live
`POST /api/v1/analyze` output via:

```bash
py -3 tools/parity_suite.py --repeat 3
```

Do **not** regenerate casually. Intentional updates:

1. Bump `app/agent/version.py`
2. Document the change
3. `py -3 tools/parity_suite.py --freeze`
4. Commit the new JSON files with a clear “why”
