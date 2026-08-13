# EVIDENCE_PROVENANCE_ARCHITECTURE

## Canonical provenance chain (current)

`paper -> warehouse evidence row -> runtime evidence payload/lookup -> condition or formula context -> output field -> presentation projection`

## Current implementation path

1. **Paper/source metadata** is stored in warehouse evidence-related datasets (including citation fields where present).
2. **Warehouse row retrieval** occurs through `app.data.repository.DataRepository` (production) and `repository.warehouse.WarehouseInterface` (parallel/test/audit).
3. **Evidence context** is assembled in app agent nodes and optionally enriched by `app.science.attach`.
4. **Formula execution context** appears in developer/debug payloads from `app.debug.clinical_execution_debug`.
5. **Presentation projection**:
   - Customer/business receive summarized evidence-facing values only.
   - Developer receives expanded provenance fields when debug trace data is available.

## Provenance checklist per scientific claim

For each scientific number, the target audit path is:

- warehouse dataset + row identity (or fact id)
- citation fields (`paper_name`, `paper_link`, quote text if present)
- formula/stage that consumed the value
- parameters/intermediate values where available
- final output field(s)

If any part is missing, classify as:

- `PROVENANCE_UNAVAILABLE`
- or developer-facing `EVIDENCE INCOMPLETE`

## Current gaps

- Not all production customer/business values carry row-level evidence identity.
- Mixed app/runtime schemas create partial provenance continuity across layers.
- Developer trace is strongest provenance surface but debug-gated.
- Some evidence chains are qualitative summaries rather than fully normalized row lineage.

## Non-fabrication requirement

- Never synthesize papers, quotes, fact IDs, or prevalence values.
- Missing provenance must remain explicitly marked unavailable/incomplete.
