# Data Migration V2 (Plan Only)

**Status:** Planning — **do not execute** until explicitly approved  
**Hard constraint:** Zero clinical output change. Same risks, packages, nutrition targets, API contracts, goldens, parity.

---

## 1. Goals

1. Land the [DATA_NORMALIZATION.md](DATA_NORMALIZATION.md) schema under `data/`  
2. Keep `DataRepository` method semantics stable via adapters  
3. Delete parallel / parser / unused CSVs after cutover  
4. Update manifest + Validation Console browser only  

**Out of scope:** formula changes, optimizer weights, inference enablement, frontend redesign.

---

## 2. Current schema snapshot

| Item | Value |
|------|-------|
| Manifest version | `2.1.0` |
| Manifested tables | 45 |
| Live CSV files | 47 (+ unmanifested staple/treats) |
| Modules | `breed_analysis`, `preventative_ingredients`, `product_portfolio` |

See [DATA_DICTIONARY.md](DATA_DICTIONARY.md) and [DATA_ARCHITECTURE_REVIEW.md](DATA_ARCHITECTURE_REVIEW.md).

---

## 3. Target schema snapshot

| Item | Value |
|------|-------|
| Domains | `breeds`, `traits`, `clinical`, `care`, `nutrition`, `products` |
| Approx tables | 22–26 (3NF) |
| Evidence | Single `EVIDENCE` hub |
| Aliases / defaults | Python only |

See [DATA_ARCHITECTURE_V2.md](DATA_ARCHITECTURE_V2.md).

---

## 4. Migration order (risk-ordered)

### M0 — Freeze
- Ban new algorithmic CSVs and new parallel ingredient files.  
- Document edit rules for interns (one home per upcoming target).  
- **Risk:** None. **Rollback:** N/A.

### M1 — Dead weight (lowest risk)
- Stop loading or delete unused: `mixed_breed_interactions`, `activity_evidence`, `condition_protocols`, `product_defaults` **after** confirming no string dependencies in reports.  
- Drop `source_csv` / duplicate `trait` columns.  
- Manifest or merge `STAPLE_FOOD` / `TREATS`.  
- **Verify:** pipeline + console boot.  
- **Rollback:** restore files from git.

### M2 — Evidence hub backfill
- Create `EVIDENCE.csv`; assign `evidence_id`s; map existing `source_*` rows.  
- Add `evidence_id` columns **alongside** old `source_*` (dual-write).  
- **Verify:** reports still render citations.  
- **Rollback:** ignore new column.

### M3 — Nutrition unification (highest intern value)
- Build `CONDITION_NUTRIENTS` from sci∪prev∪priorities∪protocols (deterministic dedupe rules).  
- Single `INGREDIENT_EVIDENCE`.  
- Adapter: `condition_ingredients()` reads new table; keep old files until green.  
- Delete `preventative_ingredients/` when unused.  
- **Verify:** nutritionalTargets parity byte-for-byte (or approved float eps).  
- **Rollback:** point accessor back to sci∪prev.

### M4 — Trait prevalence unification
- Build `TRAIT_PREVALENCE` from nine files.  
- Adapter: `trait_condition_tables()` reads one file.  
- **Verify:** healthInsights / risk ranking identical.  
- **Rollback:** restore nine-file union.

### M5 — Trait profiles / interactions
- Merge purposes+explanations; merge benefits into interactions.  
- **Verify:** report sections + risk benefit reductions unchanged.

### M6 — Ingredient 3NF split
- `INGREDIENT_MASTER` + nutrients + mechanisms + food sources.  
- Move product-tied amounts to `PRODUCT_COMPONENTS`.  
- Aliases → Python (parity on coverage matching).  
- **Verify:** coverage matrices / package scores identical.

### M7 — Product attributes + folder rename
- Merge EXT/STAPLE/TREATS → `PRODUCT_ATTRIBUTES`.  
- Rename paths in manifest; keep table names stable initially.  
- Drop `PRODUCT_FUNCTIONS.confidence` only if scores unchanged (compute in code if required).

### M8 — Citation-only cutover
- Remove inline `source_*` from fact tables once all consumers use `evidence_id`.  
- **Verify:** reports + console evidence tabs.

### M9 — Docs cutover
- Rewrite [DATA.md](DATA.md) to current target.  
- Archive or mark [DATA_ARCHITECTURE_REVIEW.md](DATA_ARCHITECTURE_REVIEW.md) historical.  
- Update Validation Console CSV usage map.

---

## 5. Required backend changes (when implementing)

| Area | Change | Clinical impact |
|------|--------|-----------------|
| `manifest.yaml` | New paths/tables | None if accessors stable |
| `DataPlatform` / loader | Load new tables | None |
| `DataRepository` | Adapters / SQL-equivalent filters | None if outputs equal |
| Alias indexes | Read Python maps | None if maps identical |
| Report builders | Prefer `evidence_id` join | Presentation only if quotes match |
| Console | CSV map + browser | Debug only |

**Forbidden during migration:** edits to `health_risk` math, `package_optimizer` scoring, nutrient target formulas.

---

## 6. Parity verification strategy

1. Freeze goldens before M3+.  
2. For each M-step: run  
   `py -3 -m pytest tests/test_agent_pipeline.py tests/test_inference_parity.py -q`  
   and `py -3 tools/parity_suite.py` as applicable.  
3. Diff analyze JSON for Dolly + golden breeds: `healthInsights`, `nutritionalTargets`, `wellnessPackages` scores/products.  
4. Fail migration step on any ranking/score drift.  
5. Console tests must pass but are not clinical gates.

---

## 7. Rollback plan

| Step | Rollback |
|------|----------|
| Any M1–M8 | `git checkout` data files + manifest; revert accessor PR |
| Dual-write phases | Feature-flag accessor to old tables |
| Python aliases | Keep CSV aliases until flag flipped |

Always retain pre-migration CSV snapshot under `archive/data/pre-normalization-v2/` before deleting parallels.

---

## 8. Risk assessment

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Silent join key mismatch after rename | Med | Dual columns then delete; golden diff |
| Sci vs prev dose conflict on merge | Med | Explicit precedence doc (sci wins today) |
| Alias move breaks coverage | Med | Export CSV→Python 1:1; coverage tests |
| Report citation regression | Low | Dual-write evidence hub |
| Scope creep into formulas | Med | Refuse formula PRs in migration branches |

---

## 9. Success criteria

- [ ] One home for condition→dose  
- [ ] One trait prevalence table  
- [ ] One ingredient evidence table  
- [ ] Evidence hub used for citations  
- [ ] No alias/defaults CSVs under `data/`  
- [ ] No unused manifested tables  
- [ ] Parity/goldens green without algorithm version bump  
- [ ] Intern can answer “where do I edit X?” in one filename  

---

## Related

[DATA_NORMALIZATION.md](DATA_NORMALIZATION.md) · [DATA_CONSUMERS.md](DATA_CONSUMERS.md) · [DATA_ARCHITECTURE_V2.md](DATA_ARCHITECTURE_V2.md) · [ROADMAP.md](ROADMAP.md)
