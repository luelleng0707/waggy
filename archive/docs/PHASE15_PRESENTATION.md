# Phase 15 — Presentation Layer (Clinical Voice)

Presentation-only. Deterministic engine unchanged.

## Goals

- Hide CSV / engineering artifacts from the UI
- Surface peer-reviewed attribution and clinical language
- Remove app footer navigation — PPIE is an embedded Wagtopia module
- Keep sheets + progressive disclosure from Phase 14

## User-facing vs developer

| User | Developer (`?dev=1` or `localStorage.ppie_dev_mode=1`) |
|------|--------------------------------------------------------|
| Scientific references, clinical reasoning | CSV table names, calculation traces, schema/hash |

## Scrubbing

`StandardReportRenderer.scrub()` strips filenames, `CSV`, `PACKAGE_TIERS`, function-mapping jargon from any rendered string.

## Chrome

Module header: **Back to Wagtopia** · title · generated time · Search / Share / PDF  
No bottom tab bar.
