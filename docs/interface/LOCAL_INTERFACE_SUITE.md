# LOCAL_INTERFACE_SUITE

## 1) Architecture diagram

```text
                    WAGTOPIA
                       |
                 PPIEWellnessAgent
                       |
                 Existing FastAPI
                       |
          +------------+------------+
          |                         |
   Legacy static gateway      CSTC desktop shell
  (customer + business +      (PySide6 operator shell)
        developer)
          |                         |
          +------------+------------+
                       |
                 SAME ANALYSIS
```

## 2) Interface inventory
- See `docs/interface/LOCAL_INTERFACE_INVENTORY.md`.

## 3) Launch commands
- One-click suite:
  - `py -3 scripts/run_wagtopia_local.py`
- Customer-only remote suite:
  - `py -3 scripts/run_wagtopia_remote.py`
- API only:
  - `py -3 -m uvicorn app.api.main:app --host 127.0.0.1 --port 8000`
- Desktop only:
  - `py -3 -m app.ui.cstc`
- Streamlit journey (optional existing interface):
  - `py -3 -m streamlit run app/ui/demo_app.py --server.port 8501`

## 4) Ports
- API default: `127.0.0.1:8000` (auto-fallback to next open port if occupied)
- Legacy customer/developer gateway default: `127.0.0.1:8080` (auto-fallback)
- Remote customer-only gateway default: `127.0.0.1:8080` (auto-fallback)
- CSTC desktop: native window (no port)

## 5) Startup order
1. Detect API health on preferred API port.
2. Reuse API if healthy, otherwise start API process.
3. Wait until `GET /health` succeeds.
4. Start legacy static gateway (serves customer/business/developer web surfaces, proxies `/api/*` to API).
5. Verify customer, business, and developer URLs load.
6. Open browser tabs (unless disabled).
7. Launch CSTC desktop with API URL + key in environment.

## 6) API dependency
- All launched presentation surfaces consume the same API runtime:
  - `app.main` -> `app.api.main` -> `app.agent.engine.PPIEWellnessAgent`

## 7) Synthetic demo profile
- Canonical interview profile source:
  - `app/ui/cstc/demo_profiles.py`
- Stable default used by suite:
  - key: `mixed_lab_golden` (Dolly)
  - label: `SYNTHETIC DEMO PROFILE`

## 8) Customer workflow
1. Open customer URL (`/` on gateway).
2. Load synthetic dog scenario (preconfigured static shell request).
3. Trigger analysis against API.
4. Review wellness result, recommendations, products, package, financial details from runtime payloads.

## 9) Operator workflow (CSTC desktop)
1. Open native desktop shell.
2. Load synthetic profile.
3. Run Wagtopia analysis.
4. Navigate pages: profile, analysis, health/evidence, products, package, financial, trace.

## 10) Developer workflow
1. Open developer URL (`/developer` on gateway).
2. Run preset analysis.
3. Inspect validation, repository lookups, formula details, evidence chain, timing, and trace output.
4. If debug unavailable, UI/API reports debug mode limitation.

## 11) Cross-interface consistency
- The launcher and tests enforce a same-input -> same-analysis contract:
  - same dog identity/breed
  - same health output counts
  - same product/package counts
  - same financial totals where present
  - same evidence count
  - same formula ID set where exposed

## 12) Known limitations
- Streamlit interface remains optional and dependency-sensitive.
- Developer trace depth depends on API debug mode (`PPIE_DEBUG=true`).
- Legacy static shell presents a fixed synthetic scenario; full dynamic profile UX remains strongest in CSTC desktop.
- Repository v2 runtime remains parallel/test-focused; demo outputs come from current `app` runtime path.
- Remote URL exposure depends on local `ngrok` availability/authentication and is runtime-generated.
