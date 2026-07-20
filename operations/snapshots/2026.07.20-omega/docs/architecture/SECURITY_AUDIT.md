# Security Audit

Generated: `2026-07-20T22:13:35.088280+00:00`
Status: **PASS** (high=0)

- [medium] `default_demo_api_key` — Default demo API key is active; rotate API_KEYS in production
- [info] `csv_resolver_present` — resolve_csv_path used for CSV lookup
- [info] `no_request_path_open` — No open(request...) patterns in app/
- [info] `csv_integrity` — All manifest CSVs resolve
- [info] `profile_schema_enforced` — DogProfileInput rejects invalid age
- [info] `dependency_pinning` — Run pip-audit / safety in CI; requirements at requirements.txt
