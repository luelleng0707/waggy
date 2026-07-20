# Roadmap

Future work only. No implementation history.

---

## Data architecture redesign

Planning pack (no silent migration): start at [DATA_ARCHITECTURE_V2.md](DATA_ARCHITECTURE_V2.md) and [DATA_MIGRATION_V2.md](DATA_MIGRATION_V2.md).

1. M1 dead weight / metadata cleanup  
2. Evidence hub dual-write  
3. Unify `CONDITION_NUTRIENTS`; remove parallel `preventative_ingredients/`  
4. Collapse nine trait prevalence CSVs  
5. Ingredient 3NF + aliases → Python  
6. Product attributes merge + domain folders  
7. Rewrite [DATA.md](DATA.md) after cutover  

Clinical parity must stay green throughout.

---

## Engine facade

1. Introduce `PPIEEngine.assess(profile) → ClinicalAssessment` as the stable Python entry (additive wiring).  
2. Point demo and partners at assess-only mounts.  
3. Stop emitting transitional megadict report blobs (`clinicalReport` / widget models) once demo no longer needs them.  
4. Optionally relocate root demo assets under `demo/` (ops-heavy — plan carefully).

Non-goal for facade batches: changing `RISK_V2_1`, package optimizer, or nutrient target math.

---

## Data provider

1. Real `IDataProvider` protocol + CSV adapter (repository already behaves as CSV provider).  
2. Later: SQL / Wagtopia catalog / lab result providers without formula edits.  
3. Unify parallel `preventative_ingredients/*` vs `5_scientific_nutrition/*` if redundant.  
4. Decide fate of unmanifested staple/treat sheets.

---

## Observability instrumentation

Emit named debug fields (no equation text) for remaining gaps:

- CSV row provenance (matched key, ignored rows, joins)  
- Optimizer `optimization_passes[]` (per-candidate trial scores)  
- Data-layer cache hits / lookup counts  
- `CONF_V1` breakdown without overwriting production confidence until approved  

Risk applied-modifier traces, stage timings, and package reject lists are already emitted (see [DEBUGGING.md](DEBUGGING.md)).

---

## Opt-in formulas

Wire or formally reject for production:

- `NUTRIENT_EST_V1` / `ING_FRAC_ORDER_V1`  
- `CONDITION_SUPPORT_V1`  
- `CONF_V1` as production confidence source  

Each needs approval + goldens if enabled.

---

## API hygiene

- Tighten API-key coverage before public exposure.  
- Replace demo keys in real environments.  
- Align leftover `ALGORITHM_VERSION` / engine_name labels in report schema with `app/agent/version.py`.

---

## Cleanup (human approval)

- Delete or further archive approved legacy JS/HTML/tools under `archive/` when no longer referenced.  
- Retire Streamlit if HTTP-only is enough.  
- Keep LOCKED engine paths and goldens.
