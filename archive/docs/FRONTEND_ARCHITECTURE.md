# Frontend Architecture Report

**Mode:** UI analysis only — no redesign, no PPIE engine changes  
**Date:** 2026-07-18  
**Canonical algorithm:** Python PPIE under `app/agent/**` (frozen / production)  
**Related docs:** `FRONTEND_LAYOUT_SPEC.md` (aspirational mobile contract), `docs/PPIE_FRONTEND_QA_REPORT.md`, `docs/PPIE_RESPONSE_SCHEMA.md`

---

## 0. Executive summary

The repository has **two parallel frontends**, not one:

| Surface | How you run it | Live PPIE data? | Primary files |
|---------|----------------|-----------------|---------------|
| **A. Static investor demo** | Python API serves `/` on `:8000` | Partial — only package pricing via `POST /api/v1/analyze` | `index.html`, `app.js`, `styles.css` |
| **B. Streamlit + Jinja journey** | `streamlit run` / `run_demo.*` | Yes — full report in-process (not HTTP) | `app/ui/**` |

There are **no local image/icon/font asset files** in the repo. Imagery is remote Unsplash URLs. `app/ui/static/{css,js,icons,images}/` contain only `.gitkeep` placeholders.

`FRONTEND_LAYOUT_SPEC.md` describes a richer **canonical PPIE mobile UX** (login, multi-page nav, wellness feed) that is **not** what the committed `index.html` / `app.js` currently implement. Treat that spec as a target contract for future UI work, not as the live tree.

---

## 1. Complete frontend file map

```
Frontend/
│
├── HTML
│   ├── index.html                          # Static demo shell (browser @ :8000/)
│   ├── app/ui/templates/base/base.html     # Unused Streamlit base wrapper
│   ├── app/ui/templates/home/journey.html  # ACTIVE Streamlit single-scroll page
│   ├── app/ui/templates/wellness/
│   │   ├── nutrition_report.html           # Orphan (not rendered by router)
│   │   ├── package_detail.html             # Orphan
│   │   └── product_analysis.html           # Orphan
│   ├── app/ui/templates/shop/page.html     # Orphan
│   └── app/ui/templates/diary/page.html    # Orphan
│
├── CSS
│   ├── styles.css                          # Static demo global theme (~20 KB)
│   └── app/ui/templates/base/app_styles.css # Streamlit injected theme (~7.5 KB)
│
├── JavaScript
│   └── app.js                              # Static demo IIFE (grooming + shop + hydrate)
│
├── Python UI shell (presentation only — not algorithm)
│   ├── app/ui/demo_app.py                  # Streamlit entrypoint
│   ├── app/ui/__init__.py
│   └── app/ui/renderer/
│       ├── __init__.py                     # Public exports
│       ├── navigation.py                   # Session state + render orchestration
│       ├── journey.py                      # Assembles JourneyPageVM
│       ├── home.py                         # Home / profile VM
│       ├── wellness.py                     # Packages, nutrition, product analysis VMs
│       ├── shop.py                         # Shop catalog filter VM
│       ├── diary.py                        # Hardcoded diary VM
│       ├── formatters.py                   # ¥ / mass / % display helpers
│       ├── template_engine.py              # Jinja2 Environment + load_css
│       └── view_models.py                  # dataclass → dict for templates
│
├── Components (Jinja includes)
│   └── app/ui/templates/components/
│       ├── dog_profile_card.html           # USED by journey.html
│       ├── trait_card.html                 # USED
│       ├── trait_benefit_card.html         # USED
│       ├── trait_weakness_card.html        # USED
│       ├── nutrition_priority_card.html    # USED
│       ├── wellness_recommendation_card.html # USED
│       ├── package_card.html               # USED
│       ├── product_row.html                # USED
│       ├── nutrition_row.html              # USED
│       ├── evidence_card.html              # USED
│       ├── feeding_option.html             # USED
│       ├── ingredient_card.html            # USED
│       ├── shop_section.html               # USED
│       ├── diary_section.html              # USED
│       ├── macros.html                     # USED only by orphan wellness/shop pages
│       ├── activity_card.html              # UNUSED
│       ├── condition_card.html             # UNUSED
│       ├── metric_card.html                # UNUSED
│       ├── nav_status.html                 # UNUSED
│       ├── page_title.html                 # UNUSED
│       ├── sidebar_header.html             # UNUSED
│       ├── section_title.html              # UNUSED
│       ├── section_divider.html            # UNUSED (journey uses <hr class="section-divider">)
│       ├── detail_block.html               # UNUSED as include (profile inlines detail)
│       └── evidence_trace.html             # UNUSED
│
├── Assets
│   ├── app/ui/static/css/.gitkeep
│   ├── app/ui/static/js/.gitkeep
│   ├── app/ui/static/icons/.gitkeep
│   └── app/ui/static/images/.gitkeep
│   (No committed PNG/SVG/WOFF — fonts via Google Fonts CDN; images via Unsplash)
│
├── Icons / Images
│   └── Remote only (Unsplash URLs in index.html, app.js, home.py)
│
├── Spec / QA docs (not runtime)
│   ├── FRONTEND_LAYOUT_SPEC.md             # Target mobile PPIE layout contract
│   └── docs/PPIE_FRONTEND_QA_REPORT.md
│
└── API Calls (frontend-initiated)
    └── Static demo only:
        POST {origin}/api/v1/analyze
        Headers: Content-Type, Accept, x-api-key
        Used by: hydrateFromPPIE() → .package-price / .package-title
    Streamlit:
        No fetch() — calls PPIEWellnessAgent.generate_reproducible_report() in-process
```

### Explicitly out of scope for UI edits

Do **not** treat these as frontend:

- `app/agent/**` — PPIE algorithm  
- `app/api/**` — HTTP API (except static file serving of `index.html` / `app.js` / `styles.css`)  
- `data/**` — CSV corpus  
- `tests/golden/**`, parity tools — regression locks  
- Retired Node tree (if present on disk; recovered via `legacy-node-final` tag)

---

## 2. Rendering pipelines

### 2.1 Surface A — Static demo (browser)

```
Browser
  ↓
GET /  →  index.html
  ↓
<link> styles.css
  ↓
<script> app.js?v=…  (IIFE)
  ↓
Initialization (no router; single #page-home)
  ├── renderReport('jul12')           → #grooming-report.innerHTML
  ├── calendar .cal-day.has-session   → click → renderReport(sessionId)
  ├── renderShop('all')               → #product-grid.innerHTML
  ├── .cat-btn click                  → renderShop(category)
  └── hydrateFromPPIE()              → fetch POST /api/v1/analyze
                                        → update .package-price / .package-title
                                        → stash window.__PPIE_LAST__
  ↓
DOM (mostly server-rendered static HTML + two dynamic islands)
```

**Important:** Wellness copy (traits, nutrition numbers, prevalence, etc.) is **baked into `index.html`**. Only package price text is live.

### 2.2 Surface B — Streamlit + Jinja

```
streamlit run app/ui/demo_app.py
  ↓
configure_streamlit()
  ↓
NavigationRouter.run()
  ├── ensure_state()
  │     └── run_engine(DogProfileInput)   # asyncio → PPIEWellnessAgent
  │           → st.session_state.demo_report  (full PPIE JSON dict)
  ├── inject_css()  → load_css('app_styles.css') → st.markdown(<style>)
  ├── render_sidebar()  → Refresh button re-runs engine
  └── render_journey()
        ├── Streamlit selectboxes (package / product / diary day)
        ├── JourneyRenderer.build(report, profile, …)
        │     ├── HomeRenderer.build
        │     ├── WellnessRenderer.build_home / build_package_detail /
        │     │                     build_full_nutrition_report / build_product_analysis
        │     ├── ShopRenderer.build
        │     └── DiaryRenderer.build
        ├── vm_to_dict(JourneyPageVM)
        └── render_template("home/journey.html", …)
              ├── includes components/*.html
              └── st.markdown(html, unsafe_allow_html=True)
  ↓
Browser (Streamlit iframe / document)
```

### 2.3 Complete rendering tree (Streamlit journey)

```
home/journey.html
├── Header (brand, greeting from home.*)
├── Hero image (home.hero_url)
├── dog_profile_card.html
│     └── detail blocks / tags from home.*
├── Breed × Environment Matrix
│     └── trait_card.html × environment_rows[]
├── Trait Analysis tags (trait_labels[])
├── Trait Benefits
│     └── trait_benefit_card.html × trait_benefits[]
├── Trait Weaknesses
│     └── trait_weakness_card.html × trait_weaknesses[]
├── Preventative Wellness (inline module-card × priorities[])
├── Nutrition Priorities
│     └── nutrition_priority_card.html × nutrition_priorities[]
├── Evidence-backed Recommendations
│     └── wellness_recommendation_card.html × wellness_recommendations[]
├── Recommended Care Packages
│     └── package_card.html × packages[]
├── Package Detail (inline + package_detail.*)
├── Products
│     └── product_row.html × package_detail.products[]
├── Daily Nutrition Intake
│     └── nutrition_row.html × package_detail.nutrients[]
├── Full Nutrition Report
│     └── evidence_card.html × nutrition_traces[]
├── Feeding Guide
│     └── feeding_option.html × package_detail.feeding_options[]
├── Scientific Evidence (inline module-card × nutrition_traces[])
├── Product Analysis (if selected)
│     ├── ingredient_card.html × actives[]
│     └── cost rows (inline)
├── shop_section.html ← shop_items[]
└── diary_section.html ← diary_selected_label, diary_logs[]
```

### 2.4 Static demo rendering tree

```
index.html (#page-home continuous scroll)
├── Header / Hero / Profile (static HTML)
├── Wellness sections (static HTML placeholders)
├── .package-price  ← hydrateFromPPIE() only live binding
├── Grooming Diary calendar (static HTML)
│     └── #grooming-report ← renderReport() via productCardHTML()
└── Shop
      └── #product-grid ← renderShop()
```

---

## 3. Every screen / page

### 3.1 Static demo — one screen

| Screen | Purpose | HTML | JS | CSS | API | Data model |
|--------|---------|------|----|-----|-----|------------|
| **Continuous wellness report** | Investor phone-frame demo for Dolly | `index.html` `#page-home` | `renderReport`, `renderShop`, `hydrateFromPPIE` | `styles.css` | `POST /api/v1/analyze` (pricing only) | Hardcoded sessions + shop arrays; packages from `wellnessPackages[]` |

There is **no** multi-page bottom nav in the committed static shell (unlike `FRONTEND_LAYOUT_SPEC.md`).

### 3.2 Streamlit — one logical page, many sections

| Screen / section | Purpose | Template | Renderer | CSS | Data source |
|------------------|---------|----------|----------|-----|-------------|
| **Wellness journey** | Full PPIE narrative scroll | `home/journey.html` | `JourneyRenderer` + `NavigationRouter` | `app_styles.css` | In-process `demo_report` |
| Sidebar controls | Package / product / diary focus + refresh | Streamlit widgets (not Jinja) | `navigation.py` | Streamlit default + injected CSS | Session state |
| Orphan page templates | Legacy multi-page layout | `wellness/*`, `shop/page`, `diary/page` | None wired | same | N/A |

---

## 4. Render / display functions inventory

### 4.1 `app.js` (static)

| Function | Renders | Inputs | Outputs / DOM | Dependencies |
|----------|---------|--------|---------------|--------------|
| `productCardHTML(p, idx)` | Product card markup | product `{name,brand,desc,price}`, index | HTML string | `productImgs[]` |
| `renderReport(sessionId)` | Full grooming report | session key (`jul12`…) | `#grooming-report` `innerHTML` | `sessions`, `dogClean`/`dogMessy`, `recCategories`, `productCardHTML` |
| `renderShop(category)` | Shop grid | category string / `'all'` | `#product-grid` `innerHTML` | `shopProducts` |
| `hydrateFromPPIE()` | Package price line | hardcoded Dolly payload | `.package-price`, `.package-title`, `window.__PPIE_LAST__` | `fetch`, `API_KEY` |

**Event listeners**

- `.cal-day.has-session` → `renderReport`
- `.cat-btn` → `renderShop`
- Boot: `renderReport('jul12')`, `renderShop('all')`, `hydrateFromPPIE()`

**DOM patterns used:** `innerHTML`, template literals, `querySelector` / `querySelectorAll`, `classList`, `scrollIntoView`. No `appendChild`, no axios, no framework.

### 4.2 Streamlit Python “renderers” (view-model builders)

These do **not** write DOM; they build dataclasses consumed by Jinja.

| Class / method | What it prepares | Key inputs |
|----------------|------------------|------------|
| `HomeRenderer.build` | Greeting, hero, profile, tags, detail blocks | `report["profile"]` (+ hardcoded tags/copy) |
| `WellnessRenderer.build_home` | Environment rows + package cards | `wellnessPackages`, profile/biology |
| `WellnessRenderer.build_package_detail` | Package summary, products, nutrients, feeding | `packageDetails`, `wellnessPackages`, CSV feeding rules |
| `WellnessRenderer.build_full_nutrition_report` | Nutrition traces + evidence quotes | report + catalog evidence helpers |
| `WellnessRenderer.build_product_analysis` | Actives, evidence, cost rows | `packageDetails`, product components CSV, `wellness_reports` |
| `ShopRenderer.build` | Filtered shop items | `packageDetails.product_cards`, catalog + pricing DFs |
| `DiaryRenderer.build` | Day picker + logs | **Hardcoded** `_LOGS` (no PPIE) |
| `JourneyRenderer.build` | Full `JourneyPageVM` | All of the above + epidemiology / nutrition / wellness_summary slices |
| `render_template` | HTML string | Jinja name + context |
| `NavigationRouter.render_journey` | Injects HTML into Streamlit | session state |

---

## 5. API request map

### 5.1 Frontend `fetch` (static demo only)

```
POST /api/v1/analyze
Headers:
  Content-Type: application/json
  Accept: application/json
  x-api-key: wagtopia-demo-key
Payload (hardcoded Dolly):
  name, pet_name, breeds[], birthday, weight, sex,
  activity_level, current_environment, observed_conditions[]
Response (consumed fields only):
  wellnessPackages[].tier | title | monthly_cost | yearly_cost
  (also stored: wellness_score, version — not rendered)
Render path:
  hydrateFromPPIE()
    → .package-price text
    → .package-title text
```

No other `fetch` / `XMLHttpRequest` / axios usage exists in frontend JS.

### 5.2 Streamlit data path (not HTTP)

```
NavigationRouter.ensure_state / Refresh button
  → PPIEWellnessAgent.generate_reproducible_report(DogProfileInput)
  → full analyze-equivalent JSON in st.session_state.demo_report
  → JourneyRenderer → Jinja
```

Available HTTP endpoints exist on the Python API (`/health`, `/api/v2/wellness/evaluate`, breeds, evidence, products, groomer sessions) but **are not called by either current UI shell** except static hydrate’s `/api/v1/analyze`.

### 5.3 Spec-era APIs (not wired in committed static UI)

`FRONTEND_LAYOUT_SPEC.md` documents intended calls such as breed search `GET /api/breeds`, recommendations refresh, Socket.io groomer updates. Those belong to the **target** mobile UX, not the current `app.js`.

---

## 6. Component hierarchy

### 6.1 Static demo

```
Device frame (.device-frame)
└── Phone app (.phone-app)
    └── #page-home.journey-scroll
        ├── Header (brand, greeting)
        ├── Hero
        ├── Profile card
        ├── Wellness Analysis (static cards)
        ├── Care package (hydrate price)
        ├── Grooming Diary
        │   ├── Calendar
        │   └── #grooming-report (dynamic)
        │         ├── Before / After grids
        │         ├── Problem / Result cards
        │         ├── Products used carousel
        │         ├── Groomer note
        │         └── Recommended categories
        └── Shop
              ├── Category chips
              └── #product-grid (dynamic)
```

### 6.2 Streamlit journey (engine-backed)

```
Journey
├── Header
├── Hero
├── Pet Summary (dog_profile_card)
├── Wellness Analysis intro
├── Breed × Environment Matrix
├── Trait Analysis
├── Trait Benefits
├── Trait Weaknesses
├── Preventative Wellness (priority conditions)
├── Nutrition Priorities
├── Evidence-backed Recommendations
├── Care Packages
├── Package Detail
│   ├── Cost / summary
│   ├── Products
│   ├── Daily Nutrition Intake
│   ├── Full Nutrition Report (evidence cards)
│   └── Feeding Guide
├── Scientific Evidence
├── Product Analysis
│   ├── Serving meta
│   ├── Active ingredients
│   └── Cost breakdown
├── Shop
└── Diary
```

---

## 7. CSS organization

### 7.1 Global themes

| File | Used by | Notes |
|------|---------|-------|
| `styles.css` | Static `index.html` | Full phone-frame, calendar, shop, grooming report, cards |
| `app_styles.css` | Streamlit via `load_css` | Subset mirroring tokens + journey modules; smaller |

### 7.2 Design tokens (`:root`)

Shared palette (both files, cream / burgundy family):

| Token | Value (approx.) |
|-------|-----------------|
| `--bg-start` / `--bg-end` | `#FBF9F6` → `#FFF0F5` |
| `--primary` | `#7A1C4B` |
| `--accent` | `#A12568` |
| `--button` | `#E53A7F` |
| `--text` / `--text-muted` | `#3D3429` / rgba |
| `--card-bg` / `--card-border` | frosted white + pink border |
| `--radius-*` | 16–28px |
| Fonts | **DM Sans** (UI) + **Noto Serif** (display), Google Fonts CDN |

`styles.css` also aliases legacy names (`--cream`, `--brown`, `--gold`, `--font`).

### 7.3 What controls what (static)

| UI area | Typical classes / regions in `styles.css` |
|---------|-------------------------------------------|
| Phone chrome | `.device-frame`, `.device-notch`, `.phone-app` |
| Header / hero | `.home-header`, `.hero-dog`, `.hero-overlay` |
| Profile | `.profile-card`, `.tag`, `.detail-block` |
| Wellness cards | `.voucher-card`, `.section-header`, `.package-price` |
| Diary / calendar | `.calendar-*`, `.cal-day`, `.grooming-report` |
| Report cards | `.problem-card`, `.result-card`, `.status-pill`, `.product-card` |
| Shop | `.cat-btn`, `.shop-product`, `.product-grid` |
| Motion | `.loaded` transitions; limited keyframes if present |

### 7.4 Streamlit CSS (`app_styles.css`)

Controls `.device-frame` journey inside Streamlit markdown HTML: headers, `.module-card`, package/product/nutrition/ingredient/shop/diary module classes. Streamlit chrome (sidebar, selectboxes) uses Streamlit’s own CSS — not fully themed.

### 7.5 Gaps

- **No `@media` breakpoints** in either CSS file (desktop = phone frame centered; Streamlit = centered layout).
- Duplicate token/theme maintenance across two CSS files.
- Many inline `style=` attributes in Jinja templates.
- No dedicated chart/progress-bar component CSS beyond simple coverage % text.

---

## 8. Asset inventory

| Asset type | Location | Usage |
|------------|----------|--------|
| **Fonts** | Google Fonts CDN (`index.html`; Streamlit inherits via CSS `font-family`) | DM Sans, Noto Serif |
| **Hero / avatar** | Unsplash URLs in `index.html`, `home.py` (`UNSPLASH_HERO` / `UNSPLASH_AVATAR`) | Profile + hero |
| **Grooming photos** | `dogClean`, `dogMessy`, `detailShots` in `app.js` | Before/after, problems, results |
| **Product images** | `productImgs` + per-item Unsplash in `shopProducts` | Carousels + shop grid |
| **Local images / SVG / icons / logos** | **None committed** | Placeholders only under `app/ui/static/**` |
| **Backgrounds** | CSS gradients on `body` / cards | Atmosphere |

Broken or flaky remote images were noted in prior QA; treat external URLs as a reliability risk for redesign.

---

## 9. JavaScript / Streamlit architecture

### 9.1 Static demo (`app.js`)

| Concern | Behavior |
|---------|----------|
| **Entry** | IIFE on script load |
| **Global state** | Module-scoped consts (`sessions`, `shopProducts`, image pools); `window.__PPIE_LAST__` after hydrate |
| **Page lifecycle** | Single page always “active”; no `showPage` in current commit |
| **Navigation** | Calendar session + shop category only |
| **Loading** | `.package-price` text + `dataset.state` = `loading` \| `ready` \| `error` |
| **Errors** | `console.error` + fallback price text |
| **DOM updates** | Full `innerHTML` replace for report/shop islands |

### 9.2 Streamlit

| Concern | Behavior |
|---------|----------|
| **Entry** | `app/ui/demo_app.py` → `NavigationRouter.run()` |
| **State** | `st.session_state`: `demo_profile`, `demo_report`, `selected_package`, `selected_product`, `diary_selected_day` |
| **Init** | First visit runs engine once (`@st.cache_resource` agent/repo/renderer) |
| **Navigation** | Single scroll page; sidebar refresh; selectboxes change focus sections |
| **Loading** | Streamlit native rerun; no skeleton UI |
| **Errors** | Unhandled engine errors surface as Streamlit exceptions |
| **DOM updates** | Full HTML re-emit each rerun via `st.markdown` |

---

## 10. Backend dependency map (JSON → UI)

### 10.1 Static demo

| UI section | JSON fields used |
|------------|------------------|
| Package price / title | `wellnessPackages[].tier`, `title`, `monthly_cost`, `yearly_cost` |
| Everything else | **None** (hardcoded HTML / JS) |
| Debug stash | `wellness_score`, `version` → `window.__PPIE_LAST__` only |

### 10.2 Streamlit journey

| UI section | Primary report / CSV fields |
|------------|----------------------------|
| **Pet summary** | `profile.pet_name`, `breeds`, `age_years`, `weight_kg`, `sex` (+ hardcoded tags/detail copy) |
| **Breed × Environment** | `profile.*`, `biology.*` (via `_environment_matrix`) |
| **Trait labels** | `biology.trait_summary[]` |
| **Trait benefits** | `healthInsights[].title`, `why_this_matters` / `explanation` |
| **Trait weaknesses** | `epidemiology.breed_evidence_detail[]` (`breed`, `condition`, prevalence) |
| **Preventative wellness** | `epidemiology.priority_conditions[]` |
| **Nutrition priorities** | `nutritionalTargets[]` (`ingredient`, `daily_target`, `monthly_target`, supports) |
| **Recommendations** | `wellness_summary.analysis_detail[]` or `primary_priorities[]` |
| **Package cards** | `wellnessPackages[]` (`tier`, `title`, `monthly_cost`, `yearly_cost`) |
| **Package detail** | `packageDetails[tier].*`, package summary/products; feeding from CSV rules |
| **Daily nutrition / traces** | Package detail nutrients + nutrition report builders (targets, coverage, quotes) |
| **Product analysis** | Product components CSV + `wellness_reports[].targeted_intervention` coverage; pricing DF |
| **Shop** | `packageDetails.*.product_cards[].product_id` ∪ allowlist + `PRODUCT_CATALOG` / `PRODUCT_PRICING` |
| **Diary** | **No PPIE fields** — hardcoded presentation data |

Presentation formatters (`fmt_rmb`, etc.) only change display strings; they do not change algorithm outputs.

---

## 11. UI modernization / technical debt analysis

### Strengths

- Clear **presentation vs algorithm** split on Streamlit (`renderer/` + Jinja).
- Shared visual language (tokens, serif/sans, burgundy cream) across both surfaces.
- Streamlit path already consumes a **broad** slice of the real PPIE response.
- Static demo is a strong **narrative / investor** phone mock with grooming storytelling.
- Safe hydrate pattern for live pricing without touching the engine.

### Weaknesses

- **Two UIs diverge**: static mostly fake; Streamlit mostly live — redesign must pick a primary surface.
- Static wellness metrics **claim** PPIE traceability but are hardcoded.
- Currency inconsistency: static shop/grooming uses `$`; packages use `¥`.
- No dog profile form / Analyze CTA on static demo.
- Streamlit diary + home personality blocks are partially mock.
- Orphan templates/components increase cognitive load.
- `FRONTEND_LAYOUT_SPEC.md` describes a richer app than what ships.

### Technical debt

| Item | Detail |
|------|--------|
| Duplicate CSS themes | `styles.css` vs `app_styles.css` |
| Duplicate section markup | Static HTML ≈ Streamlit journey structure |
| Unused Jinja pages/components | Listed in file map |
| Hardcoded Unsplash dependency | No local asset pipeline |
| Hardcoded API key in `app.js` | Demo-only; must not ship as production auth |
| Inline styles in templates | Harder theming |
| Full `innerHTML` rebuilds | Fine for demo; weak for incremental UX |
| Engine import from UI | Streamlit UI **imports** `app.agent` — fine for demo; production SPA should use HTTP only |

### Unused / low-use

- **CSS:** Likely dead rules for multi-page nav / login from older shells (verify before deleting).
- **JS:** No unused exports (single IIFE); large static data blobs dominate.
- **Templates:** Orphan `wellness/*`, `shop/page`, `diary/page`, `base.html`, unused components listed above.
- **Static dirs:** Empty asset folders.

### Duplicate rendering logic

- Package cards / nutrition / evidence exist as both static HTML and Jinja+VM.
- Product cards: `productCardHTML` vs Jinja `product_row` / shop section.
- Diary: static calendar+report vs Streamlit `DiaryRenderer` mock logs.

### Hardcoded values (high impact)

- Dolly profile everywhere.
- Nutrition/prevalence numbers in `index.html`.
- Shop catalog in `app.js`.
- Diary logs in `diary.py`.
- Home tags / personality in `home.py`.
- Some evidence quote fallbacks and calorie/lifespan strings in `wellness.py` presentation layer.

### Layout / a11y / mobile / performance

| Area | Finding |
|------|---------|
| **Layout** | Fixed ~390px phone frame; not a responsive web app |
| **Mobile** | Frame is mobile-shaped; no breakpoint system; Streamlit controls sit outside frame |
| **A11y** | Some `aria-label` on calendar buttons; emoji in headings; color-only status pills; `unsafe_allow_html` in Streamlit |
| **Performance** | Many remote images; full report HTML rewrite; Streamlit full rerun on selectbox change; no image CDN/cache strategy in-repo |
| **Bottlenecks** | Engine run on Streamlit first load / refresh; Unsplash latency; large `innerHTML` strings |

---

## 12. Safe locations for future UI edits

### Always safe (UI-only)

| Path | Role |
|------|------|
| `index.html` | Static structure, copy, section layout |
| `styles.css` | Static theme, motion, layout |
| `app.js` | Client rendering, events, **display** of API fields already returned |
| `app/ui/templates/**` | Jinja markup / includes |
| `app/ui/templates/base/app_styles.css` | Streamlit journey theme |
| `app/ui/renderer/*.py` | View-model mapping & formatting **only** (no formula changes) |
| `app/ui/demo_app.py` | Streamlit shell wiring |
| `app/ui/static/**` | Future local images/icons/css/js |
| New files under `docs/` for UI specs | Documentation |

### Edit with care

| Path | Why |
|------|-----|
| `app/api/main.py` static routes only | Serving `index.html` / cache headers — do **not** change analyze handlers or schemas |
| Presentation fallbacks in `wellness.py` / `home.py` | Changing copy is OK; inventing new required JSON fields is **not** |

### Never modify for UI work

| Path | Why |
|------|-----|
| `app/agent/**` | Frozen PPIE algorithm |
| Analyze / evaluate route logic & response shape | Production contract |
| `data/**` | Corpus |
| `tests/golden/**`, parity suite | Regression locks |

### Rule when a UI ask needs backend change

Stop and explain. Examples that require backend (do not invent):

- New computed metrics not in response schema  
- Different package pricing formulas  
- New CSV-driven fields not emitted today  
- Changing `/api/v1/analyze` body or response keys  

Allowed alternative: render only fields already documented in `docs/PPIE_RESPONSE_SCHEMA.md`, or keep presentation mock clearly labeled as non-PPIE.

---

## 13. Recommended primary surface for redesign (decision aid)

| Goal | Prefer |
|------|--------|
| Investor phone demo / marketing | Evolve **Surface A** (`index.html` + `app.js` + `styles.css`), progressively binding more `/api/v1/analyze` fields |
| Internal full-report QA / veterinary narrative | Evolve **Surface B** (Jinja journey), keep engine in-process or switch to HTTP later |
| Production consumer app | New SPA/shell against HTTP API — do not grow Streamlit as production shell |

Do not redesign until product picks the primary surface; this document is the map for confident edits without touching PPIE production code.

---

## 14. Quick reference — “where do I change X?”

| Change | File(s) |
|--------|---------|
| Static colors / typography | `styles.css` |
| Streamlit journey colors | `app_styles.css` |
| Static section order / copy | `index.html` |
| Streamlit section order | `home/journey.html` + components |
| Grooming report UI | `app.js` `renderReport` + CSS report classes |
| Shop grid UI | `app.js` `renderShop` + CSS shop classes |
| Live package price binding | `app.js` `hydrateFromPPIE` |
| Map new existing JSON field → Streamlit UI | `journey.py` / `wellness.py` / `home.py` + template |
| Add local logo | `app/ui/static/images/` + HTML/CSS reference |

---

*End of architecture report. No UI redesign performed. PPIE engine untouched.*
