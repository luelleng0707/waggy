# CSTC_WAGTOPIA_INTEGRATION_RECOMMENDATION

## 1. What CSTC actually is
- A PySide6 desktop clinic-management application using direct SQLAlchemy ORM over SQLite.
- It is not a browser SPA and has no built-in web API backend.

## 2. What its UI architecture actually is
- `QMainWindow` shell with sidebar + `QStackedWidget`.
- One implemented data-rich dashboard and many placeholders.
- Inline style-driven components; minimal abstraction.

## 3. What parts are reusable
- Shell/navigation UX pattern.
- Card/section rendering patterns.
- Modal/error interaction patterns.

## 4. What parts are not reusable
- Direct ORM data-access-in-UI pattern.
- CSTC clinic-specific business models/flows as intelligence layer.

## 5. What Wagtopia already has
- Production API + agent runtime path (`app.main` -> `app.api.main` -> `PPIEWellnessAgent`).
- Structured analysis output, recommendation outputs, store/product endpoints.
- Trace/provenance channels and debug trace routes.

## 6. What is missing
- A dedicated presentation adapter contract between CSTC-style UI requests and Wagtopia agent outputs.
- Consistent UI-facing response model normalization.

## 7. Exact integration boundary
- Presentation shell (CSTC style)
- -> `WagtopiaPresentationAdapter`
- -> Wagtopia API/agent endpoint(s)
- -> Existing Wagtopia runtime

## 8. Minimal adapter required
- Request mapper: UI profile input -> canonical analysis request.
- Response mapper: analysis payload -> UI view models (risk/evidence/recommendation/package/financial).
- Error/loading/provenance/trace normalization.

## 9. First implementation milestone
- Deliver one vertical slice: select synthetic dog -> run analysis -> show priorities + evidence + package + cost + trace panel.

## 10. What NOT to touch
- Wagtopia scientific/optimization/formula/warehouse canonical boundaries.
- CSTC source internals beyond presentation-level integration scaffolding.
- No formula or warehouse data changes.

## 11. Estimated implementation complexity
- Medium for presentation adapter + UI remap.
- High only if attempting immediate deep runtime consolidation/cutover.

## 12. Risk areas
- Data contract mismatch (profile fields and response shape expectations).
- Session semantics mismatch (desktop persistence vs API stateless patterns).
- Existing app/repository dual-runtime boundary in Wagtopia.

## 13. Interview-demo path
- Open shell -> select dog -> call Wagtopia endpoint -> render scientific insights + evidence + recommendation/package/financial outputs -> inspect trace.
