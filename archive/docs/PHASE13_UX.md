# Phase 13 — UX & Information Architecture

UI/UX only. Clinical calculations and report models are unchanged. The frontend maps `report` / `analyze` / `reportModels` into progressive pages.

## Shell

| Tab | Purpose | Report sections |
|-----|---------|-----------------|
| Today (Dashboard) | What should I do today? | summary snippets, top risks, recommended package, activity |
| Breed | Why is my dog like this? | `breed_analysis`, `trait_analysis`, `environment_analysis` |
| Health | What should I watch out for? | `risk_analysis`, `activity_analysis` |
| Nutrition | What does my dog need? | `nutrition_analysis` |
| Plan | What should I buy? | `package_analysis` + package/product overlays |
| Diary | How is my dog changing? | `grooming_analysis` + session timeline |

## Entry points

- `index.html` — app chrome (topbar, pages, bottom tabbar, search)
- `ppie-shell.js` — page router, dashboard cards, search index, hash nav
- `report-renderer.js` — widget rendering + `#/packages/{tier}` / `#/products/{id}` overlays
- `app.js` — loads `/api/v1/clinical-report`, calls `PpieShell.mount(...)`, diary sessions

## Navigation

- Primary: bottom tabs → `#/dashboard|breed|health|nutrition|plan|diary`
- Detail: `#/packages/{tier}`, `#/products/{id}`
- Global search: products, conditions, traits, sections (client-side over report payload)

## Constraints

- No clinical math in the browser
- No fabricated citations
- Wagtopia palette / tokens unchanged (`theme.css`)
