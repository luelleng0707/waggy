# Phase 14 — Embedded Module UX

PPIE is a Wagtopia module, not a standalone app. Deep exploration uses stacked sheets.

## Interaction model

```
Dashboard (stays underneath)
  → Package sheet (accordion workspace)
    → Product sheet
      → Ingredient sheet
```

- No full-screen package/product pages
- Parent scroll position restored on close
- Accordion sections: one open at a time
- Swipe handle / backdrop / Close / Escape to dismiss
- Breadcrumb stack in the top bar while sheets are open

## Files

| File | Role |
|------|------|
| `ppie-sheets.js` | Sheet stack + package/product/risk/breed/ingredient builders |
| `ppie-shell.js` | Concise tab pages; opens sheets instead of navigating |
| `report-renderer.js` | Widget HTML; `openPackage` / `openProduct` delegate to sheets |

## Constraints

- No backend or report-model changes
- Wagtopia palette / typography unchanged
