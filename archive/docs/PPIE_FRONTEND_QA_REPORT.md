# PPIE Frontend QA Report

**Date:** 2026-07-17  
**Mode:** Frontend QA (algorithm frozen / read-only)  
**Surfaces tested:** Static demo at `http://127.0.0.1:8000/` (`index.html` + `app.js` + `styles.css`)  
**Backend:** Python FastAPI only (Node retired)

---

## Localhost verification

| Check | Result |
|-------|--------|
| `GET /health` | **200** — `runtime: python`, `algorithm_version: 2.1.0`, `breeds_loaded=48` |
| Static UI served by Python | **200** for `/`, `/app.js`, `/styles.css` |
| Node `:3000` | **Not used** — no production requests observed |
| `POST /api/v1/analyze` | **200** — Dolly wellness_score **89**, Balanced monthly **¥261** |

**Python backend (`app/agent/*`) was not modified during QA.**

---

## Architecture finding (critical for checklist)

The investor demo UI is a **phone-frame marketing shell**:

- Most wellness copy, prevalences, nutrition numbers, and shop catalog are **hardcoded**.
- There is **no dog intake form** and **no Analyze button**.
- After QA fixes, the demo **does** call Python `POST /api/v1/analyze` once on load to hydrate **package pricing** (was stuck at ¥0).

A second UI path exists: **Streamlit** (`app/ui/demo_app.py`) which runs the Python engine in-process on refresh. It was not the primary browser QA target for this pass.

---

## Screens / sections tested

| Section | Status | Notes |
|---------|--------|-------|
| Home / branding | Pass | Wagtopia mark, greeting, hero image load |
| Dog profile card | Pass (static) | Dolly 3 yrs / 28 kg / Female (demo age ≠ API birthday age) |
| Dog form | **Missing** | Cannot test puppy/senior/mixed/BCS flows |
| Analyze button | **Missing** | No spinner / double-submit UX |
| Wellness Analysis | Pass (static) | Sections render; values not live-bound |
| Trait / preventative / nutrition | Pass (static) | Cards render; sample prevalences hardcoded |
| Care packages | Pass after fix | Live hydrate → **¥261 / ¥2,881** |
| Grooming diary | Pass | Calendar day switch (12 → 18) updates report |
| Groomer recommendations | Pass | Product recs + Add to Cart affordances |
| Shop | Pass | Category filter (e.g. Supplements → 3 products) |
| Search | Limited | Input is `readonly` |
| Charts | N/A | No chart components in this shell |
| Calculation trace | **Missing** | Not rendered in static demo |
| Evidence / citations | **Missing** | No PubMed / source cards in static demo |
| Monthly / yearly plans | **Missing** | Only single package price line |
| Overall wellness score | **Missing** | Score 89 available from API but not displayed |

---

## Browser console

- No `undefined` / `null` / `NaN` strings in visible body text.
- No requests to `localhost:3000`.
- After hydrate: 1 successful `/api/v1/analyze` resource entry.
- Multiple **Unsplash image** URLs fail to load (broken remote assets).

---

## Network

| Allowed | Observed |
|---------|----------|
| Python `:8000` only | Yes |
| Legacy Node | None |
| `src/engine` / `server.js` | Not referenced by frontend |

---

## Responsive testing summary

Demo is a fixed **390px phone frame** centered on the page.

| Width intent | Observation |
|--------------|-------------|
| 320–414 | Frame scales via `max-width`; QA browser viewport ~300px showed mild document overflow before CSS fix |
| 768+ | Frame centered; large empty margin (intentional phone mock) |
| Charts / wide tables | N/A |

CSS updates applied: `overflow-x: hidden` on `html, body`; safer `max-width` on `.device-frame`.

---

## UI bugs found

| Severity | Bug | Disposition |
|----------|-----|-------------|
| High | Package price showed **¥0 / ¥0** (static) while API returns ¥261 | **Fixed** — hydrate from `/api/v1/analyze` |
| High | No form / analyze UX for multi-profile demos | Open — product gap |
| Medium | Hardcoded wellness metrics ≠ live PPIE output | Open — demo authenticity |
| Medium | Broken Unsplash images (several `naturalWidth=0`) | Open — asset reliability |
| Medium | Shop search readonly | Open |
| Low | Profile shows 3 yrs while Dolly birthday implies ~5.3 yrs | Open — static copy |
| Low | Currency mix: shop uses `$`, packages use `¥` | Open — consistency |
| Low | Horizontal overflow at very narrow viewport | **Mitigated** in CSS |

---

## UX improvement suggestions (UI only)

1. Surface **wellness score** and top health insights from the analyze response.
2. Add a **profile form + Analyze** flow (or wire Streamlit as the primary live demo).
3. Replace hardcoded prevalences/nutrition with API fields (presentation mapping only).
4. Show loading skeleton for package pricing (already briefly shows “Loading live pricing…”).
5. Use hosted product images from the catalog or stable CDN assets.
6. Align currency to RMB throughout for China demo audiences.
7. Add accessible labels for calendar days and shop category buttons.
8. Consider a desktop “expanded report” layout for investor screenshare (not only phone frame).

---

## Frontend fixes applied this session (allowed)

| File | Change |
|------|--------|
| `app.js` | Call `POST /api/v1/analyze` on load; hydrate package title/pricing |
| `styles.css` | Prevent horizontal overflow; tighten device-frame max-width |
| `index.html` | Cache-bust `app.js?v=ppie-qa-1` |
| `app/api/main.py` | `Cache-Control: no-cache` for static JS/CSS (serving only) |

**Not touched:** `app/agent/*`, formulas, CSV logic, golden fixtures.

---

## Acceptance criteria status

| Criterion | Status |
|-----------|--------|
| Python API starts /health 200 | ✓ |
| Frontend connects only to Python | ✓ |
| Analysis completes successfully | ✓ (hydrate path) |
| Results render completely | ✗ (partial static shell) |
| No console exceptions (critical) | ✓ for app logic; image failures remain |
| No failed API requests | ✓ for analyze |
| Mobile layout functional | ✓ phone frame |
| Desktop polished | Partial (phone mock only) |
| No Node references | ✓ |
| Suitable for live demo without backend changes | **Conditional** — grooming/shop story works; scientific results still mostly static |

---

## Verdict

**Frontend QA: PASS with gaps.**

Good for a **grooming + shop narrative demo** of Dolly.  
**Not yet** a full PPIE results experience (form → analyze → live insights / trace / evidence / plans).

Recommended next frontend work (still no algorithm changes): bind Streamlit or expand `app.js` to render the full analyze envelope.
