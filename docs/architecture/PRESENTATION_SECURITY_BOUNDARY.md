# PRESENTATION_SECURITY_BOUNDARY

## Access model

- Customer route `/`: public access
- Business route `/business`: optional server-side gate via `WAGTOPIA_BUSINESS_ACCESS_KEY`
- Developer route `/developer`: optional server-side gate via `WAGTOPIA_DEVELOPER_ACCESS_KEY`
- Compatibility route `/debug/calculation`: same developer gate behavior

## Authentication channels

- Optional API auth via `API_KEYS` and `x-api-key`
- Surface access via `x-wagtopia-access-key`, optional query key, or server cookie handoff
- Debug APIs additionally require debug mode (`PPIE_DEBUG` / request debug flag)

## Secret handling requirements

- No secrets embedded in frontend source files
- No hardcoded demo key fallback in production-facing JS
- No access key values in repository docs or reports
- Environment variables are server-owned configuration

## Environment variables (names only)

- `API_KEYS`
- `WAGTOPIA_BUSINESS_ACCESS_KEY`
- `WAGTOPIA_DEVELOPER_ACCESS_KEY`
- `PPIE_DEBUG`
- `DEBUG_ENGINE`

## Security status (current)

- Frontend hardcoded default keys removed
- Business/developer optional gates implemented
- Debug endpoints protected by debug gate plus developer key gate (when configured)
- CORS remains permissive and should be hardened in a dedicated production security phase
