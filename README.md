# PPIE — Portable Pet Intelligence Engine

**Clinical intelligence for Wagtopia.**  
Python engine · Stable API · Replaceable UI

PPIE turns a dog profile into a structured clinical assessment: breed biology, health priorities, nutrition targets, activity guidance, product matches, and care pathways — backed by curated veterinary evidence.

Wagtopia owns the experience (apps, shop, CRM).  
PPIE owns the clinical calculations.

The frontend in this repository is a **demonstration** of engine output. It is not the product.

---

## Architecture

```
DogProfile  →  PPIE Engine  →  ClinicalAssessment  →  Wagtopia UI
```

| Layer | Owner | Change policy |
|-------|--------|----------------|
| **A — Clinical engine** | PPIE | Versioned; regression-tested; rare |
| **B — Clinical wording** | PPIE / content | Copy only; never numbers |
| **C — Experience** | Wagtopia | Fully replaceable |
| **Business data** | Wagtopia | Catalog, pricing, profiles — data only |

Integration contract: **DogProfile in → ClinicalAssessment out**.  
See [docs/API.md](docs/API.md).

---

## Repository layout

```
app/agent/          # Layer A — clinical engines
app/inference/      # Formula registry + opt-in helpers
app/data/           # Repository, assessment, debug console
app/api/            # HTTP API
data/               # Scientific + catalog CSV archive
tests/              # Golden + parity
docs/               # Eight living documents
archive/            # Historical material
index.html + *.js   # Demo UI only
```

**Edit freely (business data):** `data/product_portfolio/**`, customer profiles in your systems, pricing.  
**Do not edit casually:** `app/agent/**` formulas — requires algorithm version bump + goldens.

`data/` is a scientific archive, not an optimizer config folder. See [docs/DATA.md](docs/DATA.md).

---

## Quick start

```bash
py -3 -m pip install -r requirements.txt
py -3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

| URL | Purpose |
|-----|---------|
| http://127.0.0.1:8000/health | Engine status |
| http://127.0.0.1:8000/ | Demo UI |
| http://127.0.0.1:8000/docs | OpenAPI |
| http://127.0.0.1:8000/debug/calculation?debug=1 | Validation Console |

Default API key: `wagtopia-demo-key` (header `x-api-key`). Override with `API_KEYS`.

Optional Streamlit journey demo: `.\run_demo.ps1` / `./run_demo.sh`.

---

## API overview

| Method | Path | Notes |
|--------|------|-------|
| `GET` | `/health` | Algorithm + data version + content hash |
| `POST` | `/api/v1/ppie/assess` | **Preferred** → ClinicalAssessment |
| `POST` | `/api/v2/wellness/evaluate` | Typed profile → analyze envelope |
| `POST` | `/api/v1/analyze` | Same pipeline (API key) |
| `POST` | `/api/v1/clinical-report` | Demo megadict + assessment |
| `GET` | `/api/v1/store` | Active catalog for demo UI |

Full field guide: [docs/API.md](docs/API.md).

---

## Input / output

**In:** dog identity, breed composition, age/weight, lifestyle, environment, diet, known conditions, goals.  
**Out:** ClinicalAssessment modules — profile, breed, traits, health, nutrition, activity, grooming, packages, products, evidence, validation, confidence.

Frontends should **render objects**, not parse prose for logic.

---

## Business data

Wagtopia can update without Python formula changes:

- Product catalog, components, feeding rules, pricing, package tiers  
- Scientific evidence rows (curated)  
- Dog profiles (stored in Wagtopia; passed at assess time)

See [docs/DATA.md](docs/DATA.md).

---

## Versioning

| Axis | Bumps when |
|------|------------|
| Algorithm | Clinical math / ranking changes |
| Data | Catalog, evidence, or clinical tables change |
| Presentation | Optional UI projection schema |

UI redesign and price promos do **not** bump the algorithm version.

---

## Regression

```bash
py -3 tools/parity_suite.py --repeat 3
```

Refresh goldens only after intentional algorithm changes (and bump `ALGORITHM_VERSION` in `app/agent/version.py`).

---

## Documentation

Start at [docs/README.md](docs/README.md).

| Doc | Owns |
|-----|------|
| [docs/BACKEND_ARCHITECTURE.md](docs/BACKEND_ARCHITECTURE.md) | Pipeline, stages, ownership |
| [docs/FORMULAS.md](docs/FORMULAS.md) | Formula IDs and scores |
| [docs/DATA.md](docs/DATA.md) | CSV archive & philosophy |
| [docs/API.md](docs/API.md) | Endpoints & contracts |
| [docs/DEBUGGING.md](docs/DEBUGGING.md) | Validation Console / traces |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Future work |
| [docs/CHANGELOG.md](docs/CHANGELOG.md) | Chronological record |

Historical material: [archive/](archive/).

**Policy:** Do not add new markdown files for features. Update the matching living doc and delete obsolete notes.

---

## Integration philosophy

1. Persist **DogProfile** in Wagtopia.  
2. Call PPIE to obtain **ClinicalAssessment**.  
3. Render with Wagtopia UI.  
4. Drive commerce from `product_id`s — do not re-rank clinically in the client.  
5. Never invent citations; use Evidence objects from the engine.

---

## License / contact

Internal Wagtopia engineering deliverable. Contact the PPIE platform owners for algorithm change requests and data stewardship.
