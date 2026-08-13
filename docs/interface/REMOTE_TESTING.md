# REMOTE_TESTING

## Purpose

Expose only the customer presentation surface for interview/demo testing while keeping the API runtime local-only.

## Local launch (no tunnel)

```bash
py -3 scripts/run_wagtopia_remote.py --no-tunnel
```

What this does:

1. Reuses or starts API (`app.api.main`) on local port `8000` (or next open fallback).
2. Starts a customer-only gateway on local port `8080` (or next open fallback).
3. Verifies:
   - `GET /` returns 200.
   - `GET /health` via gateway returns 200.
   - Gateway proxy for customer API route works.

## Tunnel launch

```bash
py -3 scripts/run_wagtopia_remote.py
```

If `ngrok` is installed and authenticated, launcher runs:

```bash
ngrok http 8080
```

The launcher reads the runtime-generated HTTPS forwarding URL from ngrok local API and prints:

- public customer URL
- local customer URL
- local developer URL
- explicit API local-only boundary

## Exposure boundary

Public tunnel -> local gateway (`:8080`) only.

Gateway policy in remote launcher:

- **Allowed**:
  - `/`
  - static assets required by customer UI
  - `/health`
  - `/api/v1/clinical-report`
  - `/api/v1/store`
  - `/api/v1/catalog`
  - `/api/v1/analyze`
- **Blocked**:
  - `/debug/*`
  - `/api/v1/ppie/*`
  - `/api/v1/science/*`
  - `/api/v1/graph/*`
  - all other unapproved `/api/*` routes

`8000` is never the public tester URL.

## Shutdown

Use `Ctrl+C` in launcher terminal.

Shutdown behavior:

- stops gateway
- stops ngrok child process (if started by launcher)
- stops API process (if started by launcher)

## Security limitations

- Development/demo environment only.
- No production hardening claims.
- API key is demo-oriented and sent from presentation client.
- Tunnel URL is public if shared.

Optional hardening (recommended for demos):

- Require ngrok auth token/account setup.
- Use ngrok traffic policy/access controls if available in your ngrok plan.
- Rotate demo key outside interview windows.

## Test data policy

- Use synthetic dog profiles only for remote demos.
- No real PII or private clinical records.
- Canonical demo profile for Ω9.6F: `mixed_lab_golden` (`Dolly`).

## Synthetic demo policy

- Synthetic inputs are allowed for presentation UX.
- Scientific outputs must come from the existing runtime.
- UI must not fabricate evidence, formulas, or recommendation scores.
