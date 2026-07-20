# Debugging

**Full Assessment Developer Report** — one continuous page. No feature tabs.

| | |
|--|--|
| **URL** | `/debug/calculation?debug=1` |
| **Schema** | `validation_console.v7` |
| **UI** | `ppie-validation-console.js` (`?v=p10`) |

## What it is

A single vertically scrollable developer report in execution order:

0 Summary → 1 Raw request → 2 Normalization → 3 Repository lookups → 4 Formula execution → 5 Modifiers → 6 Confidence → 7 Nutrition → 8 Products → 9 Packages → 10 Assembly → 11 Final response → 12 Timeline → 13 Dependencies → 14 Runtime → 15 Validation

Sidebar TOC only jumps within this page.

## Rules

1. Engine-emitted ledgers only — never a second engine.  
2. Missing instrumentation shows `NOT CURRENTLY TRACEABLE` **on the page** (not on another tab).  
3. Step expressions from the engine are shown as the executed algorithm.  
4. The page is allowed to be thousands of lines long.

## Gates

`PPIE_DEBUG=1` or `?debug=1`. Otherwise 403.
