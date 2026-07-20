# PPIE JavaScript Import Audit (Final)

**Date:** 2026-07-17  
**Scan tool:** `tools/import_audit_scan.py`  
**Working tree status:** Node runtime **REMOVED**.

## Classification legend

| Class | Meaning |
|-------|---------|
| **ACTIVE** | Required by current Python production runtime |
| **REMOVED** | Deleted from working tree; recoverable via `legacy-node-final` |
| **ARCHIVED** | Present only in Git history / tag |
| **DOCUMENTATION ONLY** | Mentions in docs or comments; not a runtime import |
| **KEEP** | Non-engine asset retained intentionally |

## Production runtime files

| Path | Class | Evidence |
|------|-------|----------|
| `app/api/main.py` | **ACTIVE** | FastAPI production entry |
| `app/agent/**` | **ACTIVE** | Canonical algorithm |
| `data/**` | **ACTIVE** | CSV knowledge base |
| `server.js` | **REMOVED** / **ARCHIVED** | Deleted; tag `legacy-node-final` |
| `server/**` | **REMOVED** / **ARCHIVED** | Deleted |
| `src/engine/**` | **REMOVED** / **ARCHIVED** | Deleted |
| `src/api/**`, `src/db/**`, `src/socket/**`, `src/security/**` | **REMOVED** / **ARCHIVED** | Deleted |
| `package.json` | **KEEP** | Scripts delegate to Python only; no Express deps |
| `app.js` / `index.html` / `styles.css` | **KEEP** | Static demo UI |

## Scan hits (post-retirement)

All remaining string hits for `src/engine`, `server.js`, `server/logic`, `computeRecommendations` are:

- **DOCUMENTATION ONLY** (`docs/*`, `FRONTEND_LAYOUT_SPEC.md`, `PYTHON_AGENT.md`)
- **DOCUMENTATION ONLY** (Python module docstrings noting historical ports)
- The scan tool needle list itself

**Zero** production `require('../engine')`, Express boots, or `npm run legacy` remain.

## Gate checklist

- [x] `GET /health` on Python → 200
- [x] Node not required for suite
- [x] `server.js` / `src/engine` absent from working tree
- [x] Tag `legacy-node-final` exists
