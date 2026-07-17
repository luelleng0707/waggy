# PPIE JavaScript Import Audit

Generated before `legacy-node-final` tag and Node retirement.
Scan tool: `tools/import_audit_scan.py`.

Classification keys:

- **ACTIVE** — required by current production runtime
- **MIGRATE** — must move to Python before Node can be removed
- **DELETE** — safe to remove after migration verification
- **DOC-ONLY** — comment / historical reference, not a runtime import
- **KEEP** — non-engine frontend or tooling retained intentionally

---

## Production runtime (pre-migration)

| Path | References | Class | Evidence |
|------|------------|-------|----------|
| `server.js` | Express boot, `/health`, static, Socket.IO | **MIGRATE → DELETE** | `package.json` `"start": "node server.js"`; boots `src/api/routes` |
| `src/api/routes.js` | `require('../engine')`, evidence/products | **MIGRATE → DELETE** | Registers `/api/v1/analyze`, `/api/recommendations`, evidence, products, groomer |
| `src/engine/*` | Entire PPIE JS engine | **MIGRATE → DELETE** | Required by `src/api/routes.js` |
| `src/engine/evidenceEngine.js` | Condition evidence/products helpers | **MIGRATE → DELETE** | Used by routes |
| `src/api/db/*`, `src/db/*` | CSV loaders for Node engine | **DELETE** | Only consumed by `src/engine` |
| `src/api/middleware.js` | API key + HMAC | **MIGRATE → DELETE** | Replaced by FastAPI `require_api_key` |
| `src/security/*` | License / JWT / HMAC / keys | **DELETE** | Node-only boot path |
| `src/socket/socketServer.js` | Socket.IO pet rooms | **DELETE** | No groomer.html in repo; HTTP groomer routes ported without sockets |
| `server/index.js` | Legacy Express (`npm run legacy`) | **DELETE** | `package.json` `"legacy"` |
| `server/logic.js` | `computeRecommendations` | **DELETE** | Required by `server/routes.js` / `server/index.js` |
| `server/routes.js` | Legacy recommendations/breeds | **DELETE** | `require('./logic')` |
| `server/socket.js` | Legacy sockets | **DELETE** | Legacy server only |
| `server/import.js` | CSV import helper | **DELETE** | Legacy path |

---

## Python ports (canonical after migration)

| Former JS | Python |
|-----------|--------|
| `src/engine/index.js` `analyze` | `app/agent/engine.py` + `response_assembler.py` via `POST /api/v1/analyze` |
| `src/engine/evidenceEngine.js` | `app/api/evidence.py` |
| `mapLegacyResponse` | `app/api/payload_adapter.py` |
| Express static | FastAPI `FileResponse` for `/`, `/app.js`, `/styles.css` |
| API key middleware | `app/api/main.py` `require_api_key` |

---

## Non-runtime references

| Path | Class | Notes |
|------|-------|-------|
| `app/agent/*.py` docstrings mentioning `src/engine` | **DOC-ONLY** | Historical parity comments; not imports |
| `docs/PPIE_ALGORITHM.md` | **DOC-ONLY** | Mentions retired JS |
| `FRONTEND_LAYOUT_SPEC.md` | **DOC-ONLY** | Update pointers to Python |
| `app.js` / `index.html` / `styles.css` | **KEEP** | Static demo UI; no engine `require` |
| `tools/parity_suite.py` | **KEEP** | Golden regression (Python-only) |
| `tools/parity_harness.py` | **KEEP** (optional Node compare) | Historical; suite is canonical |

---

## Post-migration gate

Before deleting Node files, verify:

1. `GET http://127.0.0.1:8000/health` → 200
2. `POST /api/v1/analyze` with `x-api-key` → 200
3. `GET /api/v1/evidence/{condition}` → 200
4. `GET /api/v1/products/{condition}` → 200
5. `POST /api/recommendations` → 200 legacy shape
6. `py -3 tools/parity_suite.py --repeat 3` → 10/10 × 3

After deletion, re-run `tools/import_audit_scan.py` — production code paths must show **zero** `require('../engine')` / `server/logic` / `server.js` runtime boots.
