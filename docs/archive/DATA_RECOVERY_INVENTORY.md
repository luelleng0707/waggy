# Data recovery inventory

Forensic inventory of intern / legacy / canonical datasets. **Nothing was deleted.**

Generated: 2026-09-03 09:15 UTC

Preservation copies (read-only; do not edit):

- `warehouse/recovery_original/intern_a122a83/` — git `a122a83` intern trees
- `warehouse/recovery_original/snapshot_d6384a0/` — git `d6384a0` warehouse snapshot
- `warehouse/recovery_original/canonical_before_recovery/` — canonical CSVs as they existed before append-only recovery
- `warehouse/recovery_original/RECOVERY_MAPPING.csv` — every recovered row with `source_legacy_file` / `source_legacy_row`

## Classification counts

| STATUS | FILES |
|---|---:|
| POPULATED LEGACY DATA | 107 |
| POPULATED SCIENTIFIC DATA | 83 |
| UNKNOWN | 57 |
| EMPTY TEMPLATE | 41 |
| DERIVED DATA | 30 |
| POPULATED COMMERCIAL DATA | 23 |

## How intern data disappeared from the working tree

The intern CSVs were **not missing from git**. They were deleted from the working tree by commit `76984c5` (`full architecture reconstruction`).

| Commit | What it contained |
|---|---|
| `a122a83` | `data/breed_analysis/**`, `data/preventative_ingredients/**`, `data/product_portfolio/**`, `archive/data/legacy-parity-csv/**` |
| `d6384a0` | `operations/snapshots/2026.07.20-omega/warehouse/**` including `reference/papers.csv` |
| `76984c5` | Removed those paths from the working tree during architecture reconstruction |

Canonical `warehouse/biology/observed_breed_conditions.csv` already held the intern Labrador/Golden prevalence rows. Runtime still looked at missing `warehouse/science/` (`CANONICAL_MANIFEST.json` / `is_native_warehouse`), so Health Analysis never loaded them.

## Dataset inventory

For every scanned CSV (and keyword-matching JSON/MD/TXT/SQL):

| FILE | ROWS | COLUMNS | NONEMPTY_ROWS | NONEMPTY_EVIDENCE_ROWS | SCIENTIFIC_QUOTES | PAPER_NAMES | PAPER_LINKS | BREED_DATA | CONDITION_DATA | PREVALENCE_DATA | NUTRIENT_DATA | STATUS | LIKELY_ORIGIN |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| `docs/architecture/ADAPTER_REQUIREMENTS.csv` | 5 | 11 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | working tree |
<!-- columns: concept, source_contract, target_contract, field_mapping, semantic_mapping, lossy, loss_reason, adapter_required, adapter_location_candidate, test_required, migration_risk -->
| `docs/architecture/APP_REPOSITORY_DUPLICATES.csv` | 6 | 14 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | working tree |
<!-- columns: concept, app_path, repository_path, app_importers, repository_importers, app_entrypoints, repository_entrypoints, behavior_difference, data_difference, canonical_candidate, migr... -->
| `docs/architecture/ARCHITECTURAL_DEBT_REGISTER.csv` | 12 | 12 | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | working tree |
<!-- columns: ID, problem, layer, severity, scientific_risk, runtime_risk, security_risk, migration_risk, current_owner, recommended_action, blocked_by, status -->
| `docs/architecture/BATCH_A_ARCHIVE_MANIFEST.csv` | 3 | 9 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | working tree |
<!-- columns: original_path, archived_path, file_hash_before, file_hash_after, size_before, size_after, archive_timestamp, reason, rollback_path -->
| `docs/architecture/BATCH_A_PREMOVE.csv` | 3 | 10 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | working tree |
<!-- columns: path, file_count, executable_files, importers, runtime_references, test_references, config_references, unique_information, archive_decision, verification_evidence -->
| `docs/architecture/CANONICAL_LAYER_OWNERSHIP.csv` | 20 | 8 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | working tree |
<!-- columns: concept, canonical_owner, current_owner, production_status, duplicate_locations, adapter_required, migration_status, reason -->
| `docs/architecture/CANONICAL_OWNERSHIP_MATRIX.csv` | 6 | 12 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | working tree |
<!-- columns: concept, current_owner, duplicate_owner, canonical_owner, canonical_reason, production_dependency, repository_dependency, adapter_required, migration_required, migration_risk, c... -->
| `docs/architecture/DATA_CONTRACT_GRAPH.csv` | 17 | 12 | 17 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | working tree |
<!-- columns: source_type, destination_type, producer, consumer, serialization, required_fields, optional_fields, lossy_conversion, adapter_required, trace_preserved, evidence_preserved, status -->
| `docs/architecture/DEPENDENCY_GRAPH.csv` | 1563 | 6 | 1563 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | working tree |
<!-- columns: source, dependency, resolution_status, classification, source_package, target_package -->
| `docs/architecture/FORMULA_EXECUTION_PARITY.csv` | 19 | 9 | 19 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | working tree |
<!-- columns: formula_id, version, runtime_owner, execution_source, documentation_source, registry_source, replay_source, status, notes -->
| `docs/architecture/FORMULA_REGISTRY_AUDIT.csv` | 18 | 8 | 18 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | working tree |
<!-- columns: path, formula_ids, authoritative, referenced_by, duplicate_of, current_vs_historical, target_location, action -->
| `docs/architecture/FORMULA_STATUS.csv` | 8 | 12 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | working tree |
<!-- columns: formula_id, implementation_path, current_behavior, scientific_status, publication_status, keep_current, revise, replace, double_counting_risk, warehouse_dependencies, debugger_d... -->
| `docs/architecture/FRONTEND_DEPENDENCY_AUDIT.csv` | 29 | 7 | 29 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | working tree |
<!-- columns: frontend_file, backend_dependency, API_or_direct_access, repository_dependency, legacy_dependency, migration_required, risk -->
| `docs/architecture/LEGACY_AUDIT.csv` | 87 | 4 | 87 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | working tree |
<!-- columns: path, status, dependent_count, notes -->
| `docs/architecture/MIGRATION_MANIFEST.csv` | 633 | 16 | 633 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | working tree |
<!-- columns: current_path, target_path, action, reason, phase_origin, dependency_count, risk, requires_import_change, requires_test_change, requires_data_change, safe_to_execute, dependency_... -->
| `docs/architecture/MIGRATION_READINESS_9.6C.csv` | 6 | 3 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | working tree |
<!-- columns: concept, readiness, notes -->
| `docs/architecture/OMEGA9.6C_VERIFICATION.csv` | 36 | 21 | 36 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | working tree |
<!-- columns: concept, implementation_path, implementation_type, public_classes, public_functions, imports, importers, runtime_consumers, test_consumers, data_inputs, data_outputs, side_effec... -->
| `docs/architecture/OMEGA9.8_ARCHITECTURE_SCORECARD.csv` | 11 | 4 | 11 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | working tree |
<!-- columns: domain, status, evidence, notes -->
| `docs/architecture/OMEGA_TO_ARCHITECTURE_MAP.csv` | 19 | 2 | 19 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | working tree |
<!-- columns: omega_phase, target_architecture_domain -->
| `docs/architecture/PACKAGE_RESPONSIBILITY_MATRIX.csv` | 22 | 12 | 22 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | working tree |
<!-- columns: package, responsibility, inputs, outputs, upstream, downstream, public_api, formula_domain, scientific_domain, duplicate_of, target_package, status -->
| `docs/architecture/PURGE_MANIFEST.csv` | 87 | 8 | 87 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | working tree |
<!-- columns: path, reason, evidence, dependents, replacement, risk, safe_to_delete, approval_required -->
| `docs/architecture/REASONING_MATHEMATICS_MIGRATION.csv` | 18 | 11 | 18 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | working tree |
<!-- columns: current_path, mathematics_equivalent, imports, importers, unique_logic, duplicate_logic, formula_role, scientific_role, target_path, action, migration_risk -->
| `docs/architecture/REPOSITORY_INVENTORY.csv` | 654 | 16 | 654 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | working tree |
<!-- columns: path, file_type, size_bytes, directory, phase_origin, runtime_role, scientific_role, warehouse_role, imported_by, imports, referenced_by, status, disposition, reason, replacemen... -->
| `docs/architecture/SCAFFOLDING_AUDIT.csv` | 12 | 10 | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | working tree |
<!-- columns: directory, files, executable_files, imported_files, authoritative_docs, duplicate_docs, unique_information, target_location, action, reason -->
| `docs/architecture/SCIENTIFIC_DATA_RETENTION.csv` | 70 | 8 | 70 | 70 | 0 | 70 | 0 | 0 | 0 | 0 | 0 | POPULATED SCIENTIFIC DATA | working tree |
<!-- columns: dataset, active_consumer, scientific_value, citation_completeness, validation_state, blocker_state, duplicate_candidate, proposed_action -->
| `docs/architecture/UNKNOWN_RESOLUTION.csv` | 65 | 13 | 65 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | working tree |
<!-- columns: path, why_unknown, imported_by, referenced_by, executable, generated, scientific_data, documentation, unique_logic, duplicate_of, final_status, recommended_action, evidence -->
| `docs/architecture/VALIDATION_ARCHITECTURE_AUDIT.csv` | 5 | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | working tree |
<!-- columns: validation_type, owner_paths, scope, mutates_data, status -->
| `docs/architecture/WAREHOUSE_ACCESS_AUDIT.csv` | 83 | 8 | 83 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | working tree |
<!-- columns: path, access_method, dataset, caller, direct_csv_read, canonical_interface, migration_action, risk -->
| `docs/architecture/WAREHOUSE_BLOCKER_MAP.csv` | 8 | 10 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | working tree |
<!-- columns: source_dataset, source_row, foreign_key, target_dataset, target_key, error_type, dependent_runtime, scientific_impact, safe_action, status -->
| `docs/architecture/WAREHOUSE_DOMAIN_MAP.csv` | 14 | 9 | 14 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | working tree |
<!-- columns: warehouse_domain, dataset, consumer, formula, scientific_role, source_provenance, fk_dependencies, validation_status, blocker_status -->
| `docs/architecture/WAREHOUSE_STRUCTURE_AUDIT.csv` | 70 | 10 | 70 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | working tree |
<!-- columns: dataset, domain, purpose, fact_or_runtime, used_by, foreign_keys, duplicate_of, validation_status, intern_validation_priority, target_domain -->
| `docs/interface/CUSTOMER_UI_CLAIM_COVERAGE.csv` | 16 | 7 | 16 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | working tree |
<!-- columns: claim, runtime_source, ui_section, status, evidence_source, missing_reason, implementation_required -->
| `docs/mathematics/FORMULA_DEPENDENCIES.csv` | 27 | 9 | 27 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | working tree |
<!-- columns: formula_id, input_name, input_type, input_source, provenance_class, parameter_value, unit, transformation, downstream_variable -->
| `docs/mathematics/FORMULA_REGISTRY.csv` | 8 | 27 | 8 | 0 | 0 | 0 | 0 | 0 | 8 | 0 | 0 | POPULATED LEGACY DATA | working tree |
<!-- columns: formula_id, formula_name, source_file, source_function, line_reference, purpose, input_variables, input_units, intermediate_variables, output_variable, output_units, mathematica... -->
| `docs/mathematics/FORMULA_REPLAY.csv` | 8 | 8 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | working tree |
<!-- columns: formula_id, production_output, replay_output, absolute_error, relative_error, tolerance, status, notes -->
| `docs/mathematics/MAT1002_PARAMETER_AUDIT.csv` | 12 | 11 | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | working tree |
<!-- columns: formula_id, parameter, value, unit, source, paper, paper_link, scientific_quote, classification, justification, status -->
| `docs/mathematics/MAT1007_DEPENDENCY_AUDIT.csv` | 5 | 8 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | working tree |
<!-- columns: formula_id, upstream_variable, source_formula_or_data, role, propagation, uncertainty_channel, double_counting_risk, notes -->
| `docs/mathematics/NUMERICAL_PROVENANCE.csv` | 31838 | 19 | 31838 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | working tree |
<!-- columns: provenance_id, value, unit, classification, formula_id, formula_version, file, function, line, variable, description, source_type, source_id, paper_name, paper_link, scientific_... -->
| `docs/WAGTOPIA_SYSTEM_ARCHITECTURE.md` |  |  | 28296 |  | 2 | 2 | 2 | 1 |  | 4 |  | UNKNOWN | working tree |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 2, 'source_quote': 0, 'paper_name': 2, 'paper_link': 2, 'prevalence': 4, 'PubMed': 0, 'DOI': 0, 'Labrador': 1, 'Golden Retriever': 1} -->
| `legacy/authoring/drafts/draft-0140bb7711.json` |  |  | 530 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 1, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/drafts/draft-0dae669195.json` |  |  | 571 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 1, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/drafts/draft-1028ed62b8.json` |  |  | 571 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 1, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/drafts/draft-1094c418bd.json` |  |  | 530 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 1, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/drafts/draft-129bd9c068.json` |  |  | 530 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 1, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/drafts/draft-1b25c581a2.json` |  |  | 571 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 1, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/drafts/draft-1f7cbdc5c9.json` |  |  | 571 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 1, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/drafts/draft-24d0388dff.json` |  |  | 530 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 1, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/drafts/draft-29ab489b53.json` |  |  | 530 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 1, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/drafts/draft-2f2735093a.json` |  |  | 571 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 1, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/drafts/draft-39b135b7a4.json` |  |  | 530 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 1, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/drafts/draft-3a65ff44bb.json` |  |  | 530 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 1, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/drafts/draft-41f737765e.json` |  |  | 790 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 1, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/drafts/draft-4905aabb41.json` |  |  | 530 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 1, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/drafts/draft-5ab71769bd.json` |  |  | 571 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 1, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/drafts/draft-5ff1fea851.json` |  |  | 571 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 1, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/drafts/draft-63a2f44caf.json` |  |  | 530 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 1, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/drafts/draft-7436284cb8.json` |  |  | 530 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 1, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/drafts/draft-823e66ef7f.json` |  |  | 571 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 1, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/drafts/draft-8640919d10.json` |  |  | 571 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 1, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/drafts/draft-9eb5049221.json` |  |  | 571 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 1, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/drafts/draft-a630246c9b.json` |  |  | 530 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 1, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/drafts/draft-b2a2364c5a.json` |  |  | 530 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 1, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/drafts/draft-c62a2ff88a.json` |  |  | 571 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 1, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/drafts/draft-c872f02df6.json` |  |  | 530 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 1, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/drafts/draft-d559816c1e.json` |  |  | 571 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 1, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/drafts/draft-dc6f6260da.json` |  |  | 571 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 1, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/drafts/draft-ea89aed9d4.json` |  |  | 530 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 1, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/drafts/draft-ecbb05ecc7.json` |  |  | 530 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 1, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/drafts/draft-f6c5feaf0c.json` |  |  | 530 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 1, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/drafts/draft-f95c717002.json` |  |  | 571 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 1, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/published/draft-0dae669195.json` |  |  | 2222 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 1, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 3, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/published/draft-1028ed62b8.json` |  |  | 2222 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 1, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 3, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/published/draft-1b25c581a2.json` |  |  | 2222 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 1, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 3, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/published/draft-1f7cbdc5c9.json` |  |  | 2222 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 1, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 3, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/published/draft-2f2735093a.json` |  |  | 2222 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 1, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 3, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/published/draft-41f737765e.json` |  |  | 3734 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 2, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 2, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/published/draft-5ab71769bd.json` |  |  | 2222 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 1, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 3, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/published/draft-5ff1fea851.json` |  |  | 2222 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 1, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 3, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/published/draft-823e66ef7f.json` |  |  | 2222 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 1, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 3, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/published/draft-8640919d10.json` |  |  | 2222 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 1, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 3, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/published/draft-9eb5049221.json` |  |  | 2222 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 1, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 3, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/published/draft-c62a2ff88a.json` |  |  | 2222 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 1, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 3, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/published/draft-d559816c1e.json` |  |  | 2222 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 1, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 3, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/published/draft-dc6f6260da.json` |  |  | 2222 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 1, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 3, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/published/draft-f95c717002.json` |  |  | 2222 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 1, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 3, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/authoring/studio/explorer_data.json` |  |  | 19099 |  | 0 | 0 | 0 | 2 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 0, 'Labrador': 2, 'Golden Retriever': 2} -->
| `legacy/authoring/templates/evidence_entry.template.json` |  |  | 795 |  | 0 | 0 | 0 | 0 |  | 0 |  | POPULATED LEGACY DATA | legacy UI / ontology / drafts (on disk) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 0, 'PubMed': 0, 'DOI': 1, 'Labrador': 0, 'Golden Retriever': 0} -->
| `legacy/warehouse/draft/authoring_staging/ingredient_evidence.csv` | 15 | 24 | 15 | 15 | 1 | 15 | 1 | 0 | 15 | 0 | 15 | POPULATED LEGACY DATA | legacy authoring staging (on disk) |
<!-- columns: evidence_id, paper_id, condition, ingredient_name, dose, dose_unit, mechanism, population, effect, effect_direction, effect_size, evidence_level, source_name, source_quote, sour... -->
| `legacy/warehouse/draft/authoring_staging/papers.csv` | 15 | 14 | 15 | 15 | 0 | 15 | 1 | 0 | 0 | 0 | 0 | POPULATED LEGACY DATA | legacy authoring staging (on disk) |
<!-- columns: paper_id, title, doi, url, year, study_type, created_by, created_date, modified_by, modified_date, review_status, approval_date, change_reason, evidence_level -->
| `repository/mathematics/FORMULA_REGISTRY.md` |  |  | 789 |  | 0 | 0 | 0 | 0 |  | 2 |  | UNKNOWN | working tree |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 2, 'PubMed': 0, 'DOI': 0, 'Labrador': 0, 'Golden Retriever': 0} -->
| `repository/mechanisms/FORMULA_REGISTRY.md` |  |  | 1542 |  | 0 | 0 | 0 | 0 |  | 1 |  | UNKNOWN | working tree |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 1, 'PubMed': 0, 'DOI': 0, 'Labrador': 0, 'Golden Retriever': 0} -->
| `repository/objectives/FORMULA_REGISTRY.md` |  |  | 884 |  | 0 | 0 | 0 | 0 |  | 1 |  | UNKNOWN | working tree |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 1, 'PubMed': 0, 'DOI': 0, 'Labrador': 0, 'Golden Retriever': 0} -->
| `repository/reasoning/mathematics/FORMULA_REGISTRY.md` |  |  | 1561 |  | 0 | 0 | 0 | 0 |  | 3 |  | UNKNOWN | working tree |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 3, 'PubMed': 0, 'DOI': 0, 'Labrador': 0, 'Golden Retriever': 0} -->
| `warehouse/benchmarks/golden_retriever.json` |  |  | 1883 |  | 4 | 4 | 4 | 0 |  | 1 |  | POPULATED LEGACY DATA | current canonical warehouse |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 4, 'source_quote': 0, 'paper_name': 4, 'paper_link': 4, 'prevalence': 1, 'PubMed': 0, 'DOI': 0, 'Labrador': 0, 'Golden Retriever': 0} -->
| `warehouse/benchmarks/husky.json` |  |  | 1152 |  | 2 | 2 | 2 | 0 |  | 1 |  | POPULATED LEGACY DATA | current canonical warehouse |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 2, 'source_quote': 0, 'paper_name': 2, 'paper_link': 2, 'prevalence': 1, 'PubMed': 0, 'DOI': 0, 'Labrador': 0, 'Golden Retriever': 0} -->
| `warehouse/benchmarks/mixed_lab_golden.json` |  |  | 1955 |  | 3 | 3 | 3 | 0 |  | 3 |  | POPULATED LEGACY DATA | current canonical warehouse |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 3, 'source_quote': 0, 'paper_name': 3, 'paper_link': 3, 'prevalence': 3, 'PubMed': 0, 'DOI': 0, 'Labrador': 0, 'Golden Retriever': 0} -->
| `warehouse/biology/breed_traits.csv` | 432 | 15 | 432 | 0 | 0 | 0 | 0 | 432 | 0 | 0 | 0 | POPULATED SCIENTIFIC DATA | current canonical warehouse |
<!-- columns: fact_id, breed_id, breed_name, trait_name, trait_value, value_number, unit, population_description, scientific_quote, paper_name, paper_link, publication_year, study_type, speci... -->
| `warehouse/biology/breeds.csv` | 48 | 12 | 48 | 0 | 0 | 0 | 0 | 48 | 0 | 0 | 0 | POPULATED SCIENTIFIC DATA | current canonical warehouse |
<!-- columns: breed_id, breed_name, breed_group, external_standard, external_id, scientific_quote, paper_name, paper_link, publication_year, study_type, species, status -->
| `warehouse/biology/conditions.csv` | 34 | 13 | 34 | 0 | 0 | 0 | 0 | 0 | 34 | 0 | 0 | POPULATED SCIENTIFIC DATA | current canonical warehouse |
<!-- columns: condition_id, condition_name, condition_class, body_system, external_standard, external_id, scientific_quote, paper_name, paper_link, publication_year, study_type, species, status -->
| `warehouse/biology/environment_facts.csv` | 10 | 17 | 10 | 10 | 10 | 10 | 10 | 0 | 0 | 10 | 0 | POPULATED SCIENTIFIC DATA | current canonical warehouse |
<!-- columns: fact_id, environment_id, environment_name, metric_name, value_number, unit, statistic, season_or_period, population_description, method_note, scientific_quote, paper_name, paper... -->
| `warehouse/biology/life_stage_health_NEEDS_VALIDATION.csv` | 10 | 11 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | POPULATED LEGACY DATA | current canonical warehouse |
<!-- columns: fact_id, stage, core_health_problems, brief_explanation, scientific_quote, paper_name, paper_link, publication_year, study_type, species, status -->
| `warehouse/biology/mixed_breed_NEEDS_VALIDATION.csv` | 10 | 15 | 10 | 10 | 0 | 10 | 0 | 0 | 10 | 0 | 0 | POPULATED LEGACY DATA | current canonical warehouse |
<!-- columns: fact_id, trait_a, trait_b, condition, interaction, factor, reason, source, scientific_quote, paper_name, paper_link, publication_year, study_type, species, status -->
| `warehouse/biology/observed_breed_conditions.csv` | 16 | 19 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 0 | POPULATED SCIENTIFIC DATA | current canonical warehouse |
<!-- columns: fact_id, breed_id, breed_name, condition_id, condition_name, measure_type, value_number, unit, numerator_count, denominator_count, population_description, observation_period, sc... -->
| `warehouse/biology/size_risk_NEEDS_VALIDATION.csv` | 4 | 11 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | POPULATED LEGACY DATA | current canonical warehouse |
<!-- columns: fact_id, size_category, average_lifespan, core_health_risks, scientific_quote, paper_name, paper_link, publication_year, study_type, species, status -->
| `warehouse/biology/trait_condition_associations.csv` | 90 | 20 | 90 | 90 | 90 | 90 | 90 | 0 | 90 | 90 | 0 | POPULATED SCIENTIFIC DATA | current canonical warehouse |
<!-- columns: fact_id, trait_name, trait_value, modifier_trait_name, modifier_trait_value, condition_id, condition_name, association_type, effect_direction, effect_measure_type, effect_value,... -->
| `warehouse/commercial/product_declared_nutrition.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | current canonical warehouse |
<!-- columns:  -->
| `warehouse/commercial/product_feeding_guide.csv` | 23 | 8 | 23 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | POPULATED COMMERCIAL DATA | current canonical warehouse |
<!-- columns: product_id, min_weight_kg, max_weight_kg, daily_amount, daily_unit, source_legacy_file, source_legacy_row, status -->
| `warehouse/commercial/product_functions_NEEDS_VALIDATION.csv` | 10 | 6 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | POPULATED LEGACY DATA | current canonical warehouse |
<!-- columns: product_id, function, confidence, status, source_legacy_file, source_legacy_row -->
| `warehouse/commercial/product_master.csv` | 16 | 17 | 16 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | POPULATED COMMERCIAL DATA | current canonical warehouse |
<!-- columns: product_id, product_name, brand, product_category, recipe_version, product_status, product_url, manufacturer_declaration_source, manufacturer_declaration_url, effective_date, sc... -->
| `warehouse/commercial/product_pricing_NEEDS_VALIDATION.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | current canonical warehouse |
<!-- columns:  -->
| `warehouse/commercial/product_recipe.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | current canonical warehouse |
<!-- columns:  -->
| `warehouse/commercial/product_recipe_NEEDS_VALIDATION.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | current canonical warehouse |
<!-- columns:  -->
| `warehouse/current/README.md` |  |  | 1598 |  | 0 | 0 | 0 | 0 |  | 1 |  | UNKNOWN | current canonical warehouse |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 1, 'PubMed': 0, 'DOI': 0, 'Labrador': 0, 'Golden Retriever': 0} -->
| `warehouse/formulas/benchmarks.csv` | 3 | 5 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | DERIVED DATA | current canonical warehouse |
<!-- columns: benchmark_id, dataset_path, target_component, description, status -->
| `warehouse/formulas/coefficients.csv` | 23 | 7 | 23 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | DERIVED DATA | current canonical warehouse |
<!-- columns: formula_id, version, parameter_set_id, parameter_name, value, unit, description -->
| `warehouse/formulas/formula_versions.csv` | 9 | 6 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | DERIVED DATA | current canonical warehouse |
<!-- columns: formula_id, version, status, publication_date, description, parameter_set_id -->
| `warehouse/formulas/formulas.csv` | 8 | 4 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | DERIVED DATA | current canonical warehouse |
<!-- columns: formula_id, formula_name, latest_version, description -->
| `warehouse/formulas/parameter_sets.csv` | 9 | 5 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | DERIVED DATA | current canonical warehouse |
<!-- columns: parameter_set_id, formula_id, version, status, description -->
| `warehouse/formulas/parameters.csv` | 14 | 5 | 14 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | DERIVED DATA | current canonical warehouse |
<!-- columns: formula_id, version, parameter_name, parameter_type, description -->
| `warehouse/formulas/validation_sets.csv` | 1 | 4 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | DERIVED DATA | current canonical warehouse |
<!-- columns: validation_set_id, dataset_path, description, status -->
| `warehouse/mechanisms/absorption_factors.csv` | 5 | 7 | 5 | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 5 | DERIVED DATA | current canonical warehouse |
<!-- columns: ingredient_id, required_factor, interaction_type, effect_size, quote, paper, link -->
| `warehouse/mechanisms/condition_mechanisms.csv` | 11 | 6 | 11 | 11 | 11 | 11 | 11 | 0 | 11 | 0 | 0 | DERIVED DATA | current canonical warehouse |
<!-- columns: condition_id, mechanism_id, importance_weight, scientific_quote, paper_name, paper_link -->
| `warehouse/mechanisms/dose_response.csv` | 9 | 9 | 9 | 9 | 9 | 0 | 0 | 0 | 0 | 0 | 9 | DERIVED DATA | current canonical warehouse |
<!-- columns: ingredient, dose, unit, observed_effect, population, duration, quote, paper, link -->
| `warehouse/mechanisms/food_mechanisms.csv` | 5 | 8 | 5 | 5 | 5 | 5 | 5 | 0 | 0 | 0 | 5 | DERIVED DATA | current canonical warehouse |
<!-- columns: food_id, ingredient_id, amount, unit, basis, scientific_quote, paper_name, paper_link -->
| `warehouse/mechanisms/ingredient_mechanisms.csv` | 9 | 8 | 9 | 9 | 9 | 9 | 9 | 0 | 0 | 0 | 9 | DERIVED DATA | current canonical warehouse |
<!-- columns: ingredient_id, mechanism_id, observed_effect, effect_size, unit, scientific_quote, paper_name, paper_link -->
| `warehouse/mechanisms/mechanism_conflicts.csv` | 3 | 7 | 3 | 3 | 3 | 3 | 3 | 0 | 0 | 0 | 3 | DERIVED DATA | current canonical warehouse |
<!-- columns: ingredient_A, ingredient_B, interaction_type, effect_strength, scientific_quote, paper_name, paper_link -->
| `warehouse/mechanisms/mechanism_interactions.csv` | 5 | 7 | 5 | 5 | 5 | 5 | 5 | 0 | 0 | 0 | 5 | DERIVED DATA | current canonical warehouse |
<!-- columns: ingredient_A, ingredient_B, interaction_type, effect_strength, scientific_quote, paper_name, paper_link -->
| `warehouse/mechanisms/mechanism_synergies.csv` | 3 | 7 | 3 | 3 | 3 | 3 | 3 | 0 | 0 | 0 | 3 | DERIVED DATA | current canonical warehouse |
<!-- columns: ingredient_A, ingredient_B, interaction_type, effect_strength, scientific_quote, paper_name, paper_link -->
| `warehouse/mechanisms/mechanisms.csv` | 9 | 6 | 9 | 9 | 9 | 9 | 9 | 0 | 0 | 0 | 0 | DERIVED DATA | current canonical warehouse |
<!-- columns: mechanism_id, mechanism_name, description, scientific_quote, paper_name, paper_link -->
| `warehouse/MIGRATION_REPORT.csv` | 40 | 3 | 40 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | current canonical warehouse |
<!-- columns: old_csv, new_csv, migration_reason -->
| `warehouse/MIGRATION_SUMMARY.csv` | 14 | 7 | 14 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | current canonical warehouse |
<!-- columns: old_file, rows_found, rows_migrated, rows_validation, rows_duplicated, rows_discarded, reason -->
| `warehouse/nutrition/food_composition.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | current canonical warehouse |
<!-- columns:  -->
| `warehouse/nutrition/ingredient_composition.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | current canonical warehouse |
<!-- columns:  -->
| `warehouse/nutrition/ingredient_composition_NEEDS_VALIDATION.csv` | 12 | 19 | 12 | 12 | 12 | 12 | 12 | 0 | 0 | 12 | 12 | POPULATED LEGACY DATA | current canonical warehouse |
<!-- columns: fact_id, ingredient_id, ingredient_name, compound_id, compound_name, measure_type, value_number, unit, basis_quantity, basis_unit, preparation_state, analytical_method, scientif... -->
| `warehouse/nutrition/ingredients.csv` | 9 | 12 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | POPULATED SCIENTIFIC DATA | current canonical warehouse |
<!-- columns: ingredient_id, ingredient_name, ingredient_class, external_standard, external_id, scientific_quote, paper_name, paper_link, publication_year, study_type, species, status -->
| `warehouse/nutrition/units.csv` | 2 | 10 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | current canonical warehouse |
<!-- columns: unit_id, unit_symbol, dimension, scientific_quote, paper_name, paper_link, publication_year, study_type, species, status -->
| `warehouse/objectives/condition_objectives.csv` | 12 | 6 | 12 | 12 | 12 | 12 | 12 | 0 | 12 | 0 | 0 | DERIVED DATA | current canonical warehouse |
<!-- columns: condition_id, objective_id, importance, scientific_quote, paper_name, paper_link -->
| `warehouse/objectives/objective_conflicts.csv` | 2 | 7 | 2 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | DERIVED DATA | current canonical warehouse |
<!-- columns: objective_A, objective_B, relationship, effect, quote, paper, link -->
| `warehouse/objectives/objective_mechanisms.csv` | 8 | 6 | 8 | 8 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | DERIVED DATA | current canonical warehouse |
<!-- columns: objective_id, mechanism_id, importance, quote, paper, link -->
| `warehouse/objectives/objective_priorities.csv` | 7 | 8 | 7 | 7 | 7 | 7 | 7 | 0 | 0 | 0 | 0 | DERIVED DATA | current canonical warehouse |
<!-- columns: objective_id, life_stage, activity_level, environment_context, priority_multiplier, scientific_quote, paper_name, paper_link -->
| `warehouse/objectives/objective_synergies.csv` | 3 | 7 | 3 | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | DERIVED DATA | current canonical warehouse |
<!-- columns: objective_A, objective_B, relationship, effect, quote, paper, link -->
| `warehouse/objectives/objectives.csv` | 8 | 6 | 8 | 8 | 8 | 8 | 8 | 0 | 0 | 0 | 0 | DERIVED DATA | current canonical warehouse |
<!-- columns: objective_id, objective_name, objective_description, scientific_quote, paper_name, paper_link -->
| `warehouse/optimization/calorie_density.csv` | 4 | 6 | 4 | 4 | 4 | 4 | 4 | 0 | 0 | 0 | 0 | DERIVED DATA | current canonical warehouse |
<!-- columns: calorie_id, product_id, kcal_per_serving, scientific_quote, paper_name, paper_link -->
| `warehouse/optimization/feeding_constraints.csv` | 2 | 10 | 2 | 2 | 2 | 2 | 2 | 0 | 0 | 0 | 0 | DERIVED DATA | current canonical warehouse |
<!-- columns: feeding_constraint_id, life_stage, weight_min_kg, weight_max_kg, max_daily_calories, max_treat_calorie_percent, max_total_servings, scientific_quote, paper_name, paper_link -->
| `warehouse/optimization/ingredient_conflicts.csv` | 2 | 7 | 2 | 2 | 2 | 2 | 2 | 0 | 0 | 0 | 2 | DERIVED DATA | current canonical warehouse |
<!-- columns: conflict_id, ingredient_A, ingredient_B, penalty_strength, scientific_quote, paper_name, paper_link -->
| `warehouse/optimization/ingredient_interactions.csv` | 3 | 8 | 3 | 3 | 3 | 3 | 3 | 0 | 0 | 0 | 3 | DERIVED DATA | current canonical warehouse |
<!-- columns: interaction_id, ingredient_A, ingredient_B, interaction_type, effect_factor, scientific_quote, paper_name, paper_link -->
| `warehouse/optimization/ingredient_synergies.csv` | 3 | 7 | 3 | 3 | 3 | 3 | 3 | 0 | 0 | 0 | 3 | DERIVED DATA | current canonical warehouse |
<!-- columns: synergy_id, ingredient_A, ingredient_B, effect_strength, scientific_quote, paper_name, paper_link -->
| `warehouse/optimization/package_constraints.csv` | 4 | 8 | 4 | 4 | 4 | 4 | 4 | 0 | 0 | 0 | 0 | DERIVED DATA | current canonical warehouse |
<!-- columns: package_constraint_id, product_id, max_packages_per_day, min_packages_per_day, availability, scientific_quote, paper_name, paper_link -->
| `warehouse/optimization/product_compositions.csv` | 11 | 8 | 11 | 11 | 11 | 11 | 11 | 0 | 0 | 0 | 11 | DERIVED DATA | current canonical warehouse |
<!-- columns: composition_id, product_id, ingredient_id, amount_per_serving, unit, scientific_quote, paper_name, paper_link -->
| `warehouse/optimization/product_servings.csv` | 4 | 13 | 4 | 4 | 4 | 4 | 4 | 0 | 0 | 0 | 0 | DERIVED DATA | current canonical warehouse |
<!-- columns: product_id, product_name, serving_unit, min_servings_per_day, max_servings_per_day, life_stage_min, life_stage_max, weight_min_kg, weight_max_kg, availability, scientific_quote,... -->
| `warehouse/prevention/condition_activities.csv` | 20 | 19 | 20 | 20 | 20 | 20 | 20 | 0 | 10 | 0 | 0 | POPULATED SCIENTIFIC DATA | current canonical warehouse |
<!-- columns: fact_id, condition_id, condition_name, activity_name, exposure_description, outcome_name, effect_direction, effect_measure_type, effect_value, effect_unit, population_descriptio... -->
| `warehouse/prevention/condition_ingredients.csv` | 12 | 22 | 12 | 12 | 12 | 12 | 12 | 0 | 12 | 0 | 12 | POPULATED SCIENTIFIC DATA | current canonical warehouse |
<!-- columns: fact_id, condition_id, condition_name, ingredient_id, ingredient_name, exposure_amount, exposure_unit, exposure_basis, observed_effect_name, effect_direction, effect_measure_typ... -->
| `warehouse/recipes/recipe_components.csv` | 9 | 5 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | current canonical warehouse |
<!-- columns: recipe_id, component, percentage, scientific_basis, manufacturer_source -->
| `warehouse/recipes/recipes.csv` | 3 | 4 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | current canonical warehouse |
<!-- columns: recipe_id, recipe_name, scientific_basis, manufacturer_source -->
| `warehouse/recovery_original/canonical_before_recovery/biology/breed_traits.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | canonical warehouse snapshot taken before this recovery run |
<!-- columns:  -->
| `warehouse/recovery_original/canonical_before_recovery/biology/breeds.csv` | 9 | 12 | 9 | 0 | 0 | 0 | 0 | 9 | 0 | 0 | 0 | POPULATED SCIENTIFIC DATA | canonical warehouse snapshot taken before this recovery run |
<!-- columns: breed_id, breed_name, breed_group, external_standard, external_id, scientific_quote, paper_name, paper_link, publication_year, study_type, species, status -->
| `warehouse/recovery_original/canonical_before_recovery/biology/conditions.csv` | 34 | 13 | 34 | 0 | 0 | 0 | 0 | 0 | 34 | 0 | 0 | POPULATED SCIENTIFIC DATA | canonical warehouse snapshot taken before this recovery run |
<!-- columns: condition_id, condition_name, condition_class, body_system, external_standard, external_id, scientific_quote, paper_name, paper_link, publication_year, study_type, species, status -->
| `warehouse/recovery_original/canonical_before_recovery/biology/environment_facts.csv` | 10 | 17 | 10 | 10 | 10 | 10 | 10 | 0 | 0 | 10 | 0 | POPULATED SCIENTIFIC DATA | canonical warehouse snapshot taken before this recovery run |
<!-- columns: fact_id, environment_id, environment_name, metric_name, value_number, unit, statistic, season_or_period, population_description, method_note, scientific_quote, paper_name, paper... -->
| `warehouse/recovery_original/canonical_before_recovery/biology/life_stage_health_NEEDS_VALIDATION.csv` | 10 | 11 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | POPULATED LEGACY DATA | canonical warehouse snapshot taken before this recovery run |
<!-- columns: fact_id, stage, core_health_problems, brief_explanation, scientific_quote, paper_name, paper_link, publication_year, study_type, species, status -->
| `warehouse/recovery_original/canonical_before_recovery/biology/mixed_breed_NEEDS_VALIDATION.csv` | 10 | 15 | 10 | 10 | 0 | 10 | 0 | 0 | 10 | 0 | 0 | POPULATED LEGACY DATA | canonical warehouse snapshot taken before this recovery run |
<!-- columns: fact_id, trait_a, trait_b, condition, interaction, factor, reason, source, scientific_quote, paper_name, paper_link, publication_year, study_type, species, status -->
| `warehouse/recovery_original/canonical_before_recovery/biology/observed_breed_conditions.csv` | 16 | 19 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 0 | POPULATED SCIENTIFIC DATA | canonical warehouse snapshot taken before this recovery run |
<!-- columns: fact_id, breed_id, breed_name, condition_id, condition_name, measure_type, value_number, unit, numerator_count, denominator_count, population_description, observation_period, sc... -->
| `warehouse/recovery_original/canonical_before_recovery/biology/size_risk_NEEDS_VALIDATION.csv` | 4 | 11 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | POPULATED LEGACY DATA | canonical warehouse snapshot taken before this recovery run |
<!-- columns: fact_id, size_category, average_lifespan, core_health_risks, scientific_quote, paper_name, paper_link, publication_year, study_type, species, status -->
| `warehouse/recovery_original/canonical_before_recovery/biology/trait_condition_associations.csv` | 90 | 20 | 90 | 90 | 90 | 90 | 90 | 0 | 90 | 90 | 0 | POPULATED SCIENTIFIC DATA | canonical warehouse snapshot taken before this recovery run |
<!-- columns: fact_id, trait_name, trait_value, modifier_trait_name, modifier_trait_value, condition_id, condition_name, association_type, effect_direction, effect_measure_type, effect_value,... -->
| `warehouse/recovery_original/canonical_before_recovery/commercial/product_declared_nutrition.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | canonical warehouse snapshot taken before this recovery run |
<!-- columns:  -->
| `warehouse/recovery_original/canonical_before_recovery/commercial/product_feeding_guide.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | canonical warehouse snapshot taken before this recovery run |
<!-- columns:  -->
| `warehouse/recovery_original/canonical_before_recovery/commercial/product_functions_NEEDS_VALIDATION.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | canonical warehouse snapshot taken before this recovery run |
<!-- columns:  -->
| `warehouse/recovery_original/canonical_before_recovery/commercial/product_master.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | canonical warehouse snapshot taken before this recovery run |
<!-- columns:  -->
| `warehouse/recovery_original/canonical_before_recovery/commercial/product_pricing_NEEDS_VALIDATION.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | canonical warehouse snapshot taken before this recovery run |
<!-- columns:  -->
| `warehouse/recovery_original/canonical_before_recovery/commercial/product_recipe.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | canonical warehouse snapshot taken before this recovery run |
<!-- columns:  -->
| `warehouse/recovery_original/canonical_before_recovery/commercial/product_recipe_NEEDS_VALIDATION.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | canonical warehouse snapshot taken before this recovery run |
<!-- columns:  -->
| `warehouse/recovery_original/canonical_before_recovery/MIGRATION_REPORT.csv` | 40 | 3 | 40 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | canonical warehouse snapshot taken before this recovery run |
<!-- columns: old_csv, new_csv, migration_reason -->
| `warehouse/recovery_original/canonical_before_recovery/MIGRATION_SUMMARY.csv` | 14 | 7 | 14 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | canonical warehouse snapshot taken before this recovery run |
<!-- columns: old_file, rows_found, rows_migrated, rows_validation, rows_duplicated, rows_discarded, reason -->
| `warehouse/recovery_original/canonical_before_recovery/nutrition/food_composition.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | canonical warehouse snapshot taken before this recovery run |
<!-- columns:  -->
| `warehouse/recovery_original/canonical_before_recovery/nutrition/ingredient_composition.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | canonical warehouse snapshot taken before this recovery run |
<!-- columns:  -->
| `warehouse/recovery_original/canonical_before_recovery/nutrition/ingredient_composition_NEEDS_VALIDATION.csv` | 12 | 19 | 12 | 12 | 12 | 12 | 12 | 0 | 0 | 12 | 12 | POPULATED LEGACY DATA | canonical warehouse snapshot taken before this recovery run |
<!-- columns: fact_id, ingredient_id, ingredient_name, compound_id, compound_name, measure_type, value_number, unit, basis_quantity, basis_unit, preparation_state, analytical_method, scientif... -->
| `warehouse/recovery_original/canonical_before_recovery/nutrition/ingredients.csv` | 9 | 12 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | POPULATED SCIENTIFIC DATA | canonical warehouse snapshot taken before this recovery run |
<!-- columns: ingredient_id, ingredient_name, ingredient_class, external_standard, external_id, scientific_quote, paper_name, paper_link, publication_year, study_type, species, status -->
| `warehouse/recovery_original/canonical_before_recovery/nutrition/units.csv` | 2 | 10 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | canonical warehouse snapshot taken before this recovery run |
<!-- columns: unit_id, unit_symbol, dimension, scientific_quote, paper_name, paper_link, publication_year, study_type, species, status -->
| `warehouse/recovery_original/canonical_before_recovery/prevention/condition_activities.csv` | 20 | 19 | 20 | 20 | 20 | 20 | 20 | 0 | 10 | 0 | 0 | POPULATED SCIENTIFIC DATA | canonical warehouse snapshot taken before this recovery run |
<!-- columns: fact_id, condition_id, condition_name, activity_name, exposure_description, outcome_name, effect_direction, effect_measure_type, effect_value, effect_unit, population_descriptio... -->
| `warehouse/recovery_original/canonical_before_recovery/prevention/condition_ingredients.csv` | 12 | 22 | 12 | 12 | 12 | 12 | 12 | 0 | 12 | 0 | 12 | POPULATED SCIENTIFIC DATA | canonical warehouse snapshot taken before this recovery run |
<!-- columns: fact_id, condition_id, condition_name, ingredient_id, ingredient_name, exposure_amount, exposure_unit, exposure_basis, observed_effect_name, effect_direction, effect_measure_typ... -->
| `warehouse/recovery_original/canonical_before_recovery/reference/body_systems.csv` | 11 | 4 | 11 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | canonical warehouse snapshot taken before this recovery run |
<!-- columns: system_id, body_system, description, status -->
| `warehouse/recovery_original/canonical_before_recovery/reference/condition_mechanisms.csv` | 39 | 5 | 39 | 0 | 0 | 0 | 0 | 0 | 39 | 0 | 0 | POPULATED LEGACY DATA | canonical warehouse snapshot taken before this recovery run |
<!-- columns: condition_id, condition_name, mechanism_id, mechanism_name, status -->
| `warehouse/recovery_original/canonical_before_recovery/reference/condition_systems.csv` | 34 | 5 | 34 | 0 | 0 | 0 | 0 | 0 | 34 | 0 | 0 | POPULATED LEGACY DATA | canonical warehouse snapshot taken before this recovery run |
<!-- columns: condition_id, condition_name, system_id, body_system, status -->
| `warehouse/recovery_original/canonical_before_recovery/reference/mechanisms.csv` | 16 | 4 | 16 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | canonical warehouse snapshot taken before this recovery run |
<!-- columns: mechanism_id, mechanism_name, description, status -->
| `warehouse/recovery_original/intern_a122a83/archive/data/legacy-parity-csv/ACTIVITY_EVIDENCE.csv` | 10 | 5 | 10 | 10 | 10 | 10 | 10 | 0 | 0 | 0 | 0 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: activity_name, source_name, source_quote, source_url, year -->
| `warehouse/recovery_original/intern_a122a83/archive/data/legacy-parity-csv/BODYTYPE_CONDITIONS.csv` | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 0 | 10 | 10 | 0 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: body_type, condition, prevalence, sample_population, sample_size, source_name, source_quote, source_url, year, confidence_level -->
| `warehouse/recovery_original/intern_a122a83/archive/data/legacy-parity-csv/BREED_CONDITIONS.csv` | 16 | 10 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 0 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: breed, condition, prevalence, sample_population, sample_size, source_name, source_quote, source_url, year, confidence_level -->
| `warehouse/recovery_original/intern_a122a83/archive/data/legacy-parity-csv/BREEDS.csv` | 48 | 10 | 48 | 0 | 0 | 0 | 0 | 48 | 0 | 0 | 0 | POPULATED LEGACY DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: breed, size, body_type, coat_type, energy, weakness_group, skull_type, climate, lifespan, function_group -->
| `warehouse/recovery_original/intern_a122a83/archive/data/legacy-parity-csv/CLIMATE_CONDITIONS.csv` | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 0 | 10 | 10 | 0 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: climate, condition, prevalence, sample_population, sample_size, source_name, source_quote, source_url, year, confidence_level -->
| `warehouse/recovery_original/intern_a122a83/archive/data/legacy-parity-csv/CONDITION_ACTIVITIES.csv` | 10 | 7 | 10 | 10 | 10 | 10 | 10 | 0 | 10 | 0 | 0 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: condition, activity_name, frequency, duration_minutes, source_name, source_quote, source_url -->
| `warehouse/recovery_original/intern_a122a83/archive/data/legacy-parity-csv/CONDITION_INGREDIENTS.csv` | 12 | 8 | 12 | 12 | 12 | 12 | 12 | 0 | 12 | 0 | 12 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: condition, ingredient_name, recommended_daily_dose, dose_unit, source_name, source_quote, source_url, priority_rank -->
| `warehouse/recovery_original/intern_a122a83/archive/data/legacy-parity-csv/ENERGY_CONDITIONS.csv` | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 0 | 10 | 10 | 0 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: energy, condition, prevalence, sample_population, sample_size, source_name, source_quote, source_url, year, confidence_level -->
| `warehouse/recovery_original/intern_a122a83/archive/data/legacy-parity-csv/FUNCTIONGROUP_CONDITIONS.csv` | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 0 | 10 | 10 | 0 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: function_group, condition, prevalence, sample_population, sample_size, source_name, source_quote, source_url, year, confidence_level -->
| `warehouse/recovery_original/intern_a122a83/archive/data/legacy-parity-csv/HOMESTYLE_BAKERY.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns:  -->
| `warehouse/recovery_original/intern_a122a83/archive/data/legacy-parity-csv/INGREDIENT_EVIDENCE.csv` | 10 | 5 | 10 | 10 | 10 | 10 | 10 | 0 | 0 | 0 | 10 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: ingredient_name, source_name, source_quote, source_url, year -->
| `warehouse/recovery_original/intern_a122a83/archive/data/legacy-parity-csv/LIFESPAN_CONDITIONS(1).csv` | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 0 | 10 | 10 | 0 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: lifespan, condition, prevalence, sample_population, sample_size, source_name, source_quote, source_url, year, confidence_level -->
| `warehouse/recovery_original/intern_a122a83/archive/data/legacy-parity-csv/LIFESPAN_CONDITIONS.csv` | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 0 | 10 | 10 | 0 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: lifespan, condition, prevalence, sample_population, sample_size, source_name, source_quote, source_url, year, confidence_level -->
| `warehouse/recovery_original/intern_a122a83/archive/data/legacy-parity-csv/MIXED_BREED_INTERACTIONS(1)(1).csv` | 10 | 7 | 10 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | POPULATED LEGACY DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: trait_a, trait_b, condition, interaction, factor, reason, source -->
| `warehouse/recovery_original/intern_a122a83/archive/data/legacy-parity-csv/MIXED_BREED_INTERACTIONS(1).csv` | 10 | 7 | 10 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | POPULATED LEGACY DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: trait_a, trait_b, condition, interaction, factor, reason, source -->
| `warehouse/recovery_original/intern_a122a83/archive/data/legacy-parity-csv/MIXED_BREED_INTERACTIONS.csv` | 10 | 7 | 10 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | POPULATED LEGACY DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: trait_a, trait_b, condition, interaction, factor, reason, source -->
| `warehouse/recovery_original/intern_a122a83/archive/data/legacy-parity-csv/MIXED_BREED_MATRIX.csv` | 5 | 7 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 0 | 0 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: breed_a, breed_b, condition, factor, source_name, source_quote, source_url -->
| `warehouse/recovery_original/intern_a122a83/archive/data/legacy-parity-csv/PRODUCT_ACTIVE_INGREDIENTS.csv` | 20 | 5 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | POPULATED COMMERCIAL DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: product_id, ingredient_name, estimated_amount_per_serving, unit, evidence_level -->
| `warehouse/recovery_original/intern_a122a83/archive/data/legacy-parity-csv/PRODUCT_FEEDING_RULES.csv` | 41 | 5 | 41 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | POPULATED COMMERCIAL DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: product_id, weight_min_kg, weight_max_kg, daily_amount, daily_unit -->
| `warehouse/recovery_original/intern_a122a83/archive/data/legacy-parity-csv/PRODUCT_FUNCTIONS.csv` | 23 | 3 | 23 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | POPULATED COMMERCIAL DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: product_id, function, confidence -->
| `warehouse/recovery_original/intern_a122a83/archive/data/legacy-parity-csv/PRODUCT_PRICING.csv` | 15 | 4 | 15 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | POPULATED COMMERCIAL DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: product_id, list_price_usd, package_units, unit_label -->
| `warehouse/recovery_original/intern_a122a83/archive/data/legacy-parity-csv/PRODUCTS.csv` | 15 | 8 | 15 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | POPULATED COMMERCIAL DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: product_id, brand, category, subcategory, product_name, status, image_url, purchase_url -->
| `warehouse/recovery_original/intern_a122a83/archive/data/legacy-parity-csv/SIZE_CONDITIONS.csv` | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 0 | 10 | 10 | 0 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: size, condition, prevalence, sample_population, sample_size, source_name, source_quote, source_url, year, confidence_level -->
| `warehouse/recovery_original/intern_a122a83/archive/data/legacy-parity-csv/SKULLTYPE_CONDITIONS.csv` | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 0 | 10 | 10 | 0 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: skull_type, condition, prevalence, sample_population, sample_size, source_name, source_quote, source_url, year, confidence_level -->
| `warehouse/recovery_original/intern_a122a83/archive/data/legacy-parity-csv/STAPLE_FOOD.csv` | 5 | 17 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | POPULATED LEGACY DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: product_id, food_type, life_stage, size_support, protein_source, package_weight_g, daily_feeding_chart, energy_kcal_per_kg, protein_pct, fat_pct, fiber_pct, ash_pct, calcium_pct... -->
| `warehouse/recovery_original/intern_a122a83/archive/data/legacy-parity-csv/SUPPLEMENTS.csv` | 8 | 6 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | POPULATED LEGACY DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: product_id, supplement_type, serving_size_g, servings_per_pack, storage_method, shelf_life_days -->
| `warehouse/recovery_original/intern_a122a83/archive/data/legacy-parity-csv/TRAIT_BENEFITS.csv` | 10 | 6 | 10 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | POPULATED LEGACY DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: trait_a, trait_b, condition, reduction_factor, reason, source -->
| `warehouse/recovery_original/intern_a122a83/archive/data/legacy-parity-csv/TREATS.csv` | 2 | 8 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | POPULATED LEGACY DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: product_id, treat_type, protein_source, texture, weight_g, feeding_recommendation, storage_method, shelf_life_days -->
| `warehouse/recovery_original/intern_a122a83/archive/data/legacy-parity-csv/WEAKNESSGROUP_CONDITIONS.csv` | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 0 | 10 | 10 | 0 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: weakness_group, condition, prevalence, sample_population, sample_size, source_name, source_quote, source_url, year, confidence_level -->
| `warehouse/recovery_original/intern_a122a83/data/breed_analysis/1_biological_traits/BREED_ALIASES.csv` | 4 | 2 | 4 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | POPULATED LEGACY DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: alias, canonical_breed -->
| `warehouse/recovery_original/intern_a122a83/data/breed_analysis/1_biological_traits/BREEDS.csv` | 48 | 10 | 48 | 0 | 0 | 0 | 0 | 48 | 0 | 0 | 0 | POPULATED LEGACY DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: breed, size, body_type, coat_type, energy, weakness_group, skull_type, climate, lifespan, function_group -->
| `warehouse/recovery_original/intern_a122a83/data/breed_analysis/1_biological_traits/MIXED_BREED_INTERACTIONS.csv` | 10 | 7 | 10 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | POPULATED LEGACY DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: trait_a, trait_b, condition, interaction, factor, reason, source -->
| `warehouse/recovery_original/intern_a122a83/data/breed_analysis/1_biological_traits/MIXED_BREED_MATRIX.csv` | 5 | 7 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 0 | 0 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: breed_a, breed_b, condition, factor, source_name, source_quote, source_url -->
| `warehouse/recovery_original/intern_a122a83/data/breed_analysis/2_evolutionary_profiles/ENVIRONMENTAL_MATRICES.csv` | 6 | 10 | 6 | 6 | 6 | 6 | 6 | 0 | 0 | 0 | 0 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: trait_category, trait_value, trait, climate_context, dimension, compatibility_score, management_note, source_name, source_quote, source_url -->
| `warehouse/recovery_original/intern_a122a83/data/breed_analysis/2_evolutionary_profiles/TRAIT_ATTRIBUTE_EXPLANATIONS.csv` | 10 | 10 | 10 | 10 | 0 | 10 | 10 | 0 | 10 | 0 | 0 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: trait_category, trait_value, card_title, explanation, related_conditions, evidence_level, evidence_id, source_csv, source_name, source_url -->
| `warehouse/recovery_original/intern_a122a83/data/breed_analysis/2_evolutionary_profiles/TRAIT_PURPOSES.csv` | 5 | 7 | 5 | 5 | 5 | 5 | 5 | 0 | 0 | 0 | 0 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: trait_category, trait_value, biological_purpose, advantage_summary, source_name, source_quote, source_url -->
| `warehouse/recovery_original/intern_a122a83/data/breed_analysis/3_management_considerations/BODYTYPE_CONDITIONS.csv` | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 0 | 10 | 10 | 0 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: body_type, condition, prevalence, sample_population, sample_size, source_name, source_quote, source_url, year, confidence_level -->
| `warehouse/recovery_original/intern_a122a83/data/breed_analysis/3_management_considerations/BREED_CONDITIONS.csv` | 16 | 10 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 0 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: breed, condition, prevalence, sample_population, sample_size, source_name, source_quote, source_url, year, confidence_level -->
| `warehouse/recovery_original/intern_a122a83/data/breed_analysis/3_management_considerations/CLIMATE_CONDITIONS.csv` | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 0 | 10 | 10 | 0 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: climate, condition, prevalence, sample_population, sample_size, source_name, source_quote, source_url, year, confidence_level -->
| `warehouse/recovery_original/intern_a122a83/data/breed_analysis/3_management_considerations/CLINICAL_RISK_TIMELINE.csv` | 6 | 7 | 6 | 0 | 0 | 0 | 0 | 6 | 6 | 0 | 0 | POPULATED LEGACY DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: age_stage, trait_or_breed, condition, risk_level, monitoring, prevention, evidence_id -->
| `warehouse/recovery_original/intern_a122a83/data/breed_analysis/3_management_considerations/COATTYPE_CONDITIONS.csv` | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 0 | 10 | 10 | 0 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: coat_type, condition, prevalence, sample_population, sample_size, source_name, source_quote, source_url, year, confidence_level -->
| `warehouse/recovery_original/intern_a122a83/data/breed_analysis/3_management_considerations/ENERGY_CONDITIONS.csv` | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 0 | 10 | 10 | 0 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: energy, condition, prevalence, sample_population, sample_size, source_name, source_quote, source_url, year, confidence_level -->
| `warehouse/recovery_original/intern_a122a83/data/breed_analysis/3_management_considerations/FUNCTIONGROUP_CONDITIONS.csv` | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 0 | 10 | 10 | 0 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: function_group, condition, prevalence, sample_population, sample_size, source_name, source_quote, source_url, year, confidence_level -->
| `warehouse/recovery_original/intern_a122a83/data/breed_analysis/3_management_considerations/LIFESPAN_CONDITIONS.csv` | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 0 | 10 | 10 | 0 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: lifespan, condition, prevalence, sample_population, sample_size, source_name, source_quote, source_url, year, confidence_level -->
| `warehouse/recovery_original/intern_a122a83/data/breed_analysis/3_management_considerations/SIZE_CONDITIONS.csv` | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 0 | 10 | 10 | 0 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: size, condition, prevalence, sample_population, sample_size, source_name, source_quote, source_url, year, confidence_level -->
| `warehouse/recovery_original/intern_a122a83/data/breed_analysis/3_management_considerations/SKULLTYPE_CONDITIONS.csv` | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 0 | 10 | 10 | 0 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: skull_type, condition, prevalence, sample_population, sample_size, source_name, source_quote, source_url, year, confidence_level -->
| `warehouse/recovery_original/intern_a122a83/data/breed_analysis/3_management_considerations/TRAIT_CONTRIBUTION_WEIGHTS.csv` | 7 | 8 | 7 | 0 | 0 | 0 | 0 | 0 | 7 | 0 | 0 | POPULATED LEGACY DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: trait_category, trait_value, condition, risk_delta, unit, source_csv, evidence_id, mechanism_note -->
| `warehouse/recovery_original/intern_a122a83/data/breed_analysis/3_management_considerations/TRAIT_INTERACTIONS.csv` | 10 | 7 | 10 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | POPULATED LEGACY DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: trait_a, trait_b, condition, interaction, factor, reason, source -->
| `warehouse/recovery_original/intern_a122a83/data/breed_analysis/3_management_considerations/WEAKNESSGROUP_CONDITIONS.csv` | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 0 | 10 | 10 | 0 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: weakness_group, condition, prevalence, sample_population, sample_size, source_name, source_quote, source_url, year, confidence_level -->
| `warehouse/recovery_original/intern_a122a83/data/breed_analysis/4_preventative_interventions/ACTIVITY_EVIDENCE.csv` | 10 | 5 | 10 | 10 | 10 | 10 | 10 | 0 | 0 | 0 | 0 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: activity_name, source_name, source_quote, source_url, year -->
| `warehouse/recovery_original/intern_a122a83/data/breed_analysis/4_preventative_interventions/ACTIVITY_PRESCRIPTION_RULES.csv` | 4 | 15 | 4 | 4 | 0 | 4 | 4 | 0 | 0 | 0 | 0 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: energy, size, body_type, age_stage, daily_km, walk_morning_min, walk_evening_min, weekly_km, mental_enrichment, swimming, fetch, training, recovery_note, source_name, source_url -->
| `warehouse/recovery_original/intern_a122a83/data/breed_analysis/4_preventative_interventions/CONDITION_ACTIVITIES.csv` | 10 | 7 | 10 | 10 | 10 | 10 | 10 | 0 | 10 | 0 | 0 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: condition, activity_name, frequency, duration_minutes, source_name, source_quote, source_url -->
| `warehouse/recovery_original/intern_a122a83/data/breed_analysis/4_preventative_interventions/GROOMING_OBSERVATION_DEFS.csv` | 10 | 8 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | POPULATED LEGACY DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: observation_key, label, normal_criteria, monitor_criteria, attention_criteria, severity_scale, recommendation_template, source_csv -->
| `warehouse/recovery_original/intern_a122a83/data/breed_analysis/4_preventative_interventions/TRAIT_BENEFITS.csv` | 10 | 6 | 10 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | POPULATED LEGACY DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: trait_a, trait_b, condition, reduction_factor, reason, source -->
| `warehouse/recovery_original/intern_a122a83/data/breed_analysis/5_scientific_nutrition/CLINICAL_EVIDENCE_BASE.csv` | 7 | 10 | 7 | 7 | 7 | 7 | 6 | 0 | 7 | 0 | 7 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: evidence_id, domain, condition, nutrient_or_activity, mechanism, evidence_level, source_name, source_quote, source_url, year -->
| `warehouse/recovery_original/intern_a122a83/data/breed_analysis/5_scientific_nutrition/CONDITION_INGREDIENTS.csv` | 12 | 9 | 12 | 12 | 12 | 12 | 12 | 0 | 12 | 0 | 12 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: condition, ingredient_name, recommended_daily_dose, dose_unit, source_name, source_quote, source_url, priority_rank, evidence_type -->
| `warehouse/recovery_original/intern_a122a83/data/breed_analysis/5_scientific_nutrition/INGREDIENT_ALIASES.csv` | 6 | 4 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | POPULATED LEGACY DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: canonical_key, alias_key, category, parent_key -->
| `warehouse/recovery_original/intern_a122a83/data/breed_analysis/5_scientific_nutrition/INGREDIENT_EVIDENCE.csv` | 10 | 9 | 10 | 10 | 10 | 10 | 10 | 0 | 0 | 0 | 10 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: ingredient_name, source_name, source_quote, source_url, year, supports_joint, supports_skin, supports_gut, anti_inflammatory -->
| `warehouse/recovery_original/intern_a122a83/data/breed_analysis/5_scientific_nutrition/INGREDIENT_MECHANISMS.csv` | 8 | 7 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 8 | POPULATED LEGACY DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: nutrient_name, ingredient_name, source_product_id, amount_per_serving, unit, mechanism_summary, evidence_level -->
| `warehouse/recovery_original/intern_a122a83/data/breed_analysis/5_scientific_nutrition/INGREDIENT_NUTRIENT_ESTIMATES.csv` | 8 | 12 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 8 | POPULATED LEGACY DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: ingredient, canonical_ingredient, nutrient, amount_per_100g, unit, confidence, source, is_estimated, category, parent, property_tags, notes -->
| `warehouse/recovery_original/intern_a122a83/data/breed_analysis/5_scientific_nutrition/NATURAL_FOOD_SOURCES.csv` | 15 | 5 | 15 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 15 | POPULATED LEGACY DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: ingredient_name, food_source, amount_per_100g, unit, bioavailability_notes -->
| `warehouse/recovery_original/intern_a122a83/data/breed_analysis/5_scientific_nutrition/NUTRIENT_PRIORITIES.csv` | 5 | 9 | 5 | 5 | 5 | 5 | 5 | 0 | 5 | 0 | 5 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: condition, nutrient_name, target_dose, target_unit, priority_rank, evidence_level, source_name, source_quote, source_url -->
| `warehouse/recovery_original/intern_a122a83/data/preventative_ingredients/CONDITION_INGREDIENTS.csv` | 12 | 8 | 12 | 12 | 12 | 12 | 12 | 0 | 12 | 0 | 12 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: condition, ingredient_name, recommended_daily_dose, dose_unit, source_name, source_quote, source_url, priority_rank -->
| `warehouse/recovery_original/intern_a122a83/data/preventative_ingredients/CONDITION_PROTOCOLS.csv` | 12 | 10 | 12 | 12 | 12 | 12 | 12 | 0 | 12 | 0 | 12 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: condition, ingredient_name, recommended_daily_dose, dose_unit, priority_rank, source_name, source_quote, source_url, year, evidence_type -->
| `warehouse/recovery_original/intern_a122a83/data/preventative_ingredients/INGREDIENT_EVIDENCE.csv` | 10 | 5 | 10 | 10 | 10 | 10 | 10 | 0 | 0 | 0 | 10 | POPULATED SCIENTIFIC DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: ingredient_name, source_name, source_quote, source_url, year -->
| `warehouse/recovery_original/intern_a122a83/data/product_portfolio/EXT_SUPPLEMENTS.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns:  -->
| `warehouse/recovery_original/intern_a122a83/data/product_portfolio/EXT_TREATS_BAKERY.csv` | 12 | 9 | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | POPULATED COMMERCIAL DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: product_id, treat_type, bakery_type, protein_source, texture, weight_g, feeding_recommendation, storage_method, shelf_life_days -->
| `warehouse/recovery_original/intern_a122a83/data/product_portfolio/PACKAGE_TIERS.csv` | 3 | 5 | 3 | 3 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | POPULATED COMMERCIAL DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: tier_id, title, yearly_discount_factor, staple_product_id, sort_order -->
| `warehouse/recovery_original/intern_a122a83/data/product_portfolio/PRODUCT_CATALOG.csv` | 16 | 16 | 16 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | POPULATED COMMERCIAL DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: product_id, brand, category, subcategory, product_name, status, image_url, purchase_url, description, short_description, featured, tags, display_order, inventory_status, rating,... -->
| `warehouse/recovery_original/intern_a122a83/data/product_portfolio/PRODUCT_COMPONENTS.csv` | 59 | 7 | 59 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | POPULATED COMMERCIAL DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: product_id, component_type, component_name, value, unit, evidence_level, notes -->
| `warehouse/recovery_original/intern_a122a83/data/product_portfolio/PRODUCT_DEFAULTS.csv` | 5 | 2 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | POPULATED COMMERCIAL DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: key, product_id -->
| `warehouse/recovery_original/intern_a122a83/data/product_portfolio/PRODUCT_FEEDING_RULES.csv` | 23 | 5 | 23 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | POPULATED COMMERCIAL DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: product_id, min_weight_kg, max_weight_kg, daily_amount, daily_unit -->
| `warehouse/recovery_original/intern_a122a83/data/product_portfolio/PRODUCT_FUNCTIONS.csv` | 10 | 3 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | POPULATED COMMERCIAL DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: product_id, function, confidence -->
| `warehouse/recovery_original/intern_a122a83/data/product_portfolio/PRODUCT_PRICING.csv` | 16 | 4 | 16 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | POPULATED COMMERCIAL DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: product_id, list_price_rmb, package_units, unit_label -->
| `warehouse/recovery_original/intern_a122a83/data/product_portfolio/STAPLE_FOOD.csv` | 4 | 17 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | POPULATED COMMERCIAL DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: product_id, food_type, life_stage, size_support, protein_source, package_weight_g, daily_feeding_chart, energy_kcal_per_kg, protein_pct, fat_pct, fiber_pct, ash_pct, calcium_pct... -->
| `warehouse/recovery_original/intern_a122a83/data/product_portfolio/TREATS.csv` | 12 | 8 | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | POPULATED COMMERCIAL DATA | git a122a83 intern tree (deleted from working tree by 76984c5) |
<!-- columns: product_id, treat_type, protein_source, texture, weight_g, feeding_recommendation, storage_method, shelf_life_days -->
| `warehouse/recovery_original/RECOVERY_MAPPING.csv` | 719 | 6 | 719 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | POPULATED LEGACY DATA | current canonical warehouse |
<!-- columns: source_legacy_file, source_legacy_row, canonical_file, canonical_fact_id, recovery_status, note -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/generated/coverage_report.json` |  |  | 5965 |  | 0 | 0 | 4 | 0 |  | 1 |  | POPULATED LEGACY DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 20, 'paper_name': 0, 'paper_link': 4, 'prevalence': 1, 'PubMed': 0, 'DOI': 0, 'Labrador': 0, 'Golden Retriever': 0} -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/generated/formula_trace/risk_engine.md` |  |  | 1517 |  | 0 | 0 | 0 | 0 |  | 2 |  | UNKNOWN | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 2, 'PubMed': 0, 'DOI': 0, 'Labrador': 0, 'Golden Retriever': 0} -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/generated/migration_report.json` |  |  | 73115 |  | 0 | 0 | 0 | 0 |  | 29 |  | POPULATED LEGACY DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 22, 'paper_name': 0, 'paper_link': 0, 'prevalence': 29, 'PubMed': 0, 'DOI': 0, 'Labrador': 0, 'Golden Retriever': 0} -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/graph/edges.json` |  |  | 201656 |  | 0 | 0 | 0 | 26 |  | 106 |  | POPULATED LEGACY DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 106, 'PubMed': 0, 'DOI': 0, 'Labrador': 26, 'Golden Retriever': 0} -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/graph/nodes.json` |  |  | 58511 |  | 0 | 0 | 0 | 4 |  | 9 |  | POPULATED LEGACY DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: non-csv; keyword_hits={'scientific_quote': 0, 'source_quote': 0, 'paper_name': 0, 'paper_link': 0, 'prevalence': 9, 'PubMed': 40, 'DOI': 0, 'Labrador': 4, 'Golden Retriever': 3} -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/reference/activities.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns:  -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/reference/body_sizes.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns:  -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/reference/body_types.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns:  -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/reference/breeds.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns:  -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/reference/climates.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns:  -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/reference/coat_types.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns:  -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/reference/conditions.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns:  -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/reference/foods.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns:  -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/reference/ingredients.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns:  -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/reference/nutrients.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns:  -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/reference/papers.csv` | 199 | 13 | 199 | 199 | 188 | 199 | 198 | 0 | 0 | 0 | 0 | POPULATED SCIENTIFIC DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: paper_id, title, authors, journal, year, doi, pmid, url, sample_size, study_type, country, species, quote -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/reference/prevention_methods.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns:  -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/reference/skull_types.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns:  -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/reference/traits.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns:  -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/aliases.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns:  -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/activity_evidence.csv` | 10 | 7 | 10 | 10 | 10 | 10 | 10 | 0 | 0 | 0 | 0 | POPULATED SCIENTIFIC DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: activity_name, source_name, source_quote, source_url, year, _csv_row, _csv_file -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/activity_prescription_rules.csv` | 4 | 17 | 4 | 4 | 0 | 4 | 4 | 0 | 0 | 0 | 0 | POPULATED SCIENTIFIC DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: energy, size, body_type, age_stage, daily_km, walk_morning_min, walk_evening_min, weekly_km, mental_enrichment, swimming, fetch, training, recovery_note, source_name, source_url... -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/breed_aliases.csv` | 4 | 4 | 4 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | POPULATED LEGACY DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: alias, canonical_breed, _csv_row, _csv_file -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/breeds.csv` | 48 | 12 | 48 | 0 | 0 | 0 | 0 | 48 | 0 | 0 | 0 | POPULATED LEGACY DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: breed, size, body_type, coat_type, energy, weakness_group, skull_type, climate, lifespan, function_group, _csv_row, _csv_file -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/clinical_evidence_base.csv` | 7 | 12 | 7 | 7 | 7 | 7 | 6 | 0 | 7 | 0 | 7 | POPULATED SCIENTIFIC DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: evidence_id, domain, condition, nutrient_or_activity, mechanism, evidence_level, source_name, source_quote, source_url, year, _csv_row, _csv_file -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/clinical_risk_timeline.csv` | 6 | 9 | 6 | 0 | 0 | 0 | 0 | 6 | 6 | 0 | 0 | POPULATED LEGACY DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: age_stage, trait_or_breed, condition, risk_level, monitoring, prevention, evidence_id, _csv_row, _csv_file -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/condition_activities.csv` | 10 | 9 | 10 | 10 | 10 | 10 | 10 | 0 | 10 | 0 | 0 | POPULATED SCIENTIFIC DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: condition, activity_name, frequency, duration_minutes, source_name, source_quote, source_url, _csv_row, _csv_file -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/condition_ingredients_prev.csv` | 12 | 10 | 12 | 12 | 12 | 12 | 12 | 0 | 12 | 0 | 12 | POPULATED SCIENTIFIC DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: condition, ingredient_name, recommended_daily_dose, dose_unit, source_name, source_quote, source_url, priority_rank, _csv_row, _csv_file -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/condition_ingredients_sci.csv` | 12 | 11 | 12 | 12 | 12 | 12 | 12 | 0 | 12 | 0 | 12 | POPULATED SCIENTIFIC DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: condition, ingredient_name, recommended_daily_dose, dose_unit, source_name, source_quote, source_url, priority_rank, evidence_type, _csv_row, _csv_file -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/condition_protocols.csv` | 12 | 12 | 12 | 12 | 12 | 12 | 12 | 0 | 12 | 0 | 12 | POPULATED SCIENTIFIC DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: condition, ingredient_name, recommended_daily_dose, dose_unit, priority_rank, source_name, source_quote, source_url, year, evidence_type, _csv_row, _csv_file -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/environmental_matrices.csv` | 6 | 12 | 6 | 6 | 6 | 6 | 6 | 0 | 0 | 0 | 0 | POPULATED SCIENTIFIC DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: trait_category, trait_value, trait, climate_context, dimension, compatibility_score, management_note, source_name, source_quote, source_url, _csv_row, _csv_file -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/ext_supplements.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns:  -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/ext_treats_bakery.csv` | 12 | 11 | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | POPULATED LEGACY DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: product_id, treat_type, bakery_type, protein_source, texture, weight_g, feeding_recommendation, storage_method, shelf_life_days, _csv_row, _csv_file -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/grooming_observation_defs.csv` | 10 | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | POPULATED LEGACY DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: observation_key, label, normal_criteria, monitor_criteria, attention_criteria, severity_scale, recommendation_template, source_csv, _csv_row, _csv_file -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/ingredient_aliases.csv` | 6 | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | POPULATED LEGACY DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: canonical_key, alias_key, category, parent_key, _csv_row, _csv_file -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/ingredient_evidence_prev.csv` | 10 | 7 | 10 | 10 | 10 | 10 | 10 | 0 | 0 | 0 | 10 | POPULATED SCIENTIFIC DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: ingredient_name, source_name, source_quote, source_url, year, _csv_row, _csv_file -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/ingredient_evidence_sci.csv` | 10 | 11 | 10 | 10 | 10 | 10 | 10 | 0 | 0 | 0 | 10 | POPULATED SCIENTIFIC DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: ingredient_name, source_name, source_quote, source_url, year, supports_joint, supports_skin, supports_gut, anti_inflammatory, _csv_row, _csv_file -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/ingredient_mechanisms.csv` | 8 | 9 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 8 | POPULATED LEGACY DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: nutrient_name, ingredient_name, source_product_id, amount_per_serving, unit, mechanism_summary, evidence_level, _csv_row, _csv_file -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/ingredient_nutrient_estimates.csv` | 8 | 14 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 8 | POPULATED LEGACY DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: ingredient, canonical_ingredient, nutrient, amount_per_100g, unit, confidence, source, is_estimated, category, parent, property_tags, notes, _csv_row, _csv_file -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/mixed_breed_interactions.csv` | 10 | 9 | 10 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | POPULATED LEGACY DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: trait_a, trait_b, condition, interaction, factor, reason, source, _csv_row, _csv_file -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/mixed_breed_matrix.csv` | 5 | 9 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 0 | 0 | POPULATED SCIENTIFIC DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: breed_a, breed_b, condition, factor, source_name, source_quote, source_url, _csv_row, _csv_file -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/natural_food_sources.csv` | 15 | 7 | 15 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 15 | POPULATED LEGACY DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: ingredient_name, food_source, amount_per_100g, unit, bioavailability_notes, _csv_row, _csv_file -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/nutrient_priorities.csv` | 5 | 11 | 5 | 5 | 5 | 5 | 5 | 0 | 5 | 0 | 5 | POPULATED SCIENTIFIC DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: condition, nutrient_name, target_dose, target_unit, priority_rank, evidence_level, source_name, source_quote, source_url, _csv_row, _csv_file -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/package_tiers.csv` | 3 | 7 | 3 | 3 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | POPULATED SCIENTIFIC DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: tier_id, title, yearly_discount_factor, staple_product_id, sort_order, _csv_row, _csv_file -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/product_components.csv` | 59 | 9 | 59 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | POPULATED COMMERCIAL DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: product_id, component_type, component_name, value, unit, evidence_level, notes, _csv_row, _csv_file -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/product_defaults.csv` | 5 | 4 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | POPULATED COMMERCIAL DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: key, product_id, _csv_row, _csv_file -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/product_feeding_rules.csv` | 23 | 7 | 23 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | POPULATED COMMERCIAL DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: product_id, min_weight_kg, max_weight_kg, daily_amount, daily_unit, _csv_row, _csv_file -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/product_functions.csv` | 10 | 5 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | POPULATED COMMERCIAL DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: product_id, function, confidence, _csv_row, _csv_file -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/product_pricing.csv` | 16 | 6 | 16 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | POPULATED COMMERCIAL DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: product_id, list_price_rmb, package_units, unit_label, _csv_row, _csv_file -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/products.csv` | 16 | 18 | 16 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | POPULATED COMMERCIAL DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: product_id, brand, category, subcategory, product_name, status, image_url, purchase_url, description, short_description, featured, tags, display_order, inventory_status, rating,... -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/trait_attribute_explanations.csv` | 10 | 12 | 10 | 10 | 0 | 10 | 10 | 0 | 10 | 0 | 0 | POPULATED SCIENTIFIC DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: trait_category, trait_value, card_title, explanation, related_conditions, evidence_level, evidence_id, source_csv, source_name, source_url, _csv_row, _csv_file -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/trait_benefits.csv` | 10 | 8 | 10 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | POPULATED LEGACY DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: trait_a, trait_b, condition, reduction_factor, reason, source, _csv_row, _csv_file -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/trait_contribution_weights.csv` | 7 | 10 | 7 | 0 | 0 | 0 | 0 | 0 | 7 | 0 | 0 | POPULATED LEGACY DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: trait_category, trait_value, condition, risk_delta, unit, source_csv, evidence_id, mechanism_note, _csv_row, _csv_file -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/trait_interactions.csv` | 10 | 9 | 10 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | POPULATED LEGACY DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: trait_a, trait_b, condition, interaction, factor, reason, source, _csv_row, _csv_file -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/trait_purposes.csv` | 5 | 9 | 5 | 5 | 5 | 5 | 5 | 0 | 0 | 0 | 0 | POPULATED SCIENTIFIC DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: trait_category, trait_value, biological_purpose, advantage_summary, source_name, source_quote, source_url, _csv_row, _csv_file -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/lookup_maps.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns:  -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/parameter_defaults.csv` | 18 | 5 | 18 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | POPULATED LEGACY DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: param_group, key, value, unit, notes -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/runtime/unit_conversion.csv` | 14 | 4 | 14 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | POPULATED LEGACY DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: unit, canonical_unit, multiplier, notes -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/science/breed_condition_risk.csv` | 16 | 13 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 0 | POPULATED SCIENTIFIC DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: breed, condition, prevalence, sample_population, sample_size, source_name, source_quote, source_url, year, confidence_level, _csv_row, _csv_file, paper_id -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/science/food_nutrients.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns:  -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/science/ingredient_evidence.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns:  -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/science/ingredient_food_sources.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns:  -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/science/mixed_trait_interactions.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns:  -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/science/nutrient_targets.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns:  -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/science/prevention_effectiveness.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns:  -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/science/product_composition.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | EMPTY TEMPLATE | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns:  -->
| `warehouse/recovery_original/snapshot_d6384a0/operations/snapshots/2026.07.20-omega/warehouse/science/trait_condition_risk.csv` | 90 | 14 | 90 | 90 | 90 | 90 | 90 | 0 | 90 | 90 | 0 | POPULATED SCIENTIFIC DATA | git d6384a0 operations snapshot (deleted from working tree by 76984c5) |
<!-- columns: condition, prevalence, sample_population, sample_size, source_name, source_quote, source_url, year, confidence_level, _csv_row, _csv_file, trait_category, trait_value, paper_id -->
| `warehouse/reference/body_systems.csv` | 11 | 4 | 11 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | current canonical warehouse |
<!-- columns: system_id, body_system, description, status -->
| `warehouse/reference/condition_mechanisms.csv` | 39 | 5 | 39 | 0 | 0 | 0 | 0 | 0 | 39 | 0 | 0 | POPULATED LEGACY DATA | current canonical warehouse |
<!-- columns: condition_id, condition_name, mechanism_id, mechanism_name, status -->
| `warehouse/reference/condition_systems.csv` | 34 | 5 | 34 | 0 | 0 | 0 | 0 | 0 | 34 | 0 | 0 | POPULATED LEGACY DATA | current canonical warehouse |
<!-- columns: condition_id, condition_name, system_id, body_system, status -->
| `warehouse/reference/mechanisms.csv` | 16 | 4 | 16 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | current canonical warehouse |
<!-- columns: mechanism_id, mechanism_name, description, status -->
| `warehouse/reference/papers.csv` | 199 | 16 | 199 | 199 | 188 | 199 | 198 | 0 | 0 | 0 | 0 | POPULATED SCIENTIFIC DATA | current canonical warehouse |
<!-- columns: paper_id, paper_name, authors, journal, publication_year, doi, pmid, paper_link, sample_size, study_type, country, species, scientific_quote, status, source_legacy_file, source_... -->
| `warehouse/science_graph/ingredient_aliases.csv` | 8 | 6 | 8 | 8 | 8 | 8 | 8 | 0 | 0 | 0 | 8 | POPULATED SCIENTIFIC DATA | current canonical warehouse |
<!-- columns: alias_ingredient_id, canonical_ingredient_id, alias_name, scientific_quote, paper_name, paper_link -->
| `warehouse/science_graph/recipe_products.csv` | 4 | 5 | 4 | 4 | 4 | 4 | 4 | 0 | 0 | 0 | 0 | POPULATED SCIENTIFIC DATA | current canonical warehouse |
<!-- columns: recipe_id, product_id, scientific_quote, paper_name, paper_link -->
| `warehouse/science_graph/source_recipes.csv` | 9 | 5 | 9 | 9 | 9 | 9 | 9 | 0 | 0 | 0 | 0 | POPULATED SCIENTIFIC DATA | current canonical warehouse |
<!-- columns: source_id, recipe_id, scientific_quote, paper_name, paper_link -->
| `warehouse/sources/ingredient_sources.csv` | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 0 | 0 | 0 | 8 | POPULATED SCIENTIFIC DATA | current canonical warehouse |
<!-- columns: source_id, ingredient_id, natural_amount, unit, bioavailability, scientific_quote, paper_name, paper_link -->
| `warehouse/sources/source_bioavailability.csv` | 6 | 7 | 6 | 6 | 6 | 6 | 6 | 0 | 0 | 0 | 6 | POPULATED SCIENTIFIC DATA | current canonical warehouse |
<!-- columns: source_id, ingredient_id, bioavailability_factor, context, scientific_quote, paper_name, paper_link -->
| `warehouse/sources/source_composition.csv` | 5 | 8 | 5 | 5 | 5 | 5 | 5 | 0 | 0 | 0 | 0 | POPULATED SCIENTIFIC DATA | current canonical warehouse |
<!-- columns: source_id, component_id, component_name, percentage, unit, scientific_quote, paper_name, paper_link -->
| `warehouse/validation/actual_clinical_cases.csv` | 2 | 5 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 2 | 0 | POPULATED SCIENTIFIC DATA | current canonical warehouse |
<!-- columns: case_id, dog_id, condition_id, observed_prevalence, notes -->
| `warehouse/VALIDATION_SUMMARY.csv` | 7 | 4 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | current canonical warehouse |
<!-- columns: validation_dataset, rows, reason, recommended_manual_action -->
| `warehouse/WAREHOUSE_GUIDE.csv` | 16 | 5 | 16 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | UNKNOWN | current canonical warehouse |
<!-- columns: dataset_path, research_task, one_row_means, required_evidence_or_declaration, never_store -->

## Recovery actions this run

```json
{
  "breeds": {
    "added_breeds": 39,
    "added_traits": 432,
    "intern_breed_rows": 48
  },
  "observed": {
    "intern_rows": 16,
    "already_present": 16,
    "appended": 0
  },
  "traits": {
    "intern_rows": 90,
    "already_present": 90,
    "appended": 0
  },
  "ingredients": {
    "intern_rows": 12,
    "already_present": 12,
    "appended": 0
  },
  "mixed": {
    "intern_rows": 10,
    "already_present": 10,
    "appended": 0
  },
  "papers": {
    "intern_rows": 199,
    "already_present": 0,
    "appended": 199,
    "created": true
  },
  "commercial": {
    "intern_rows": 16,
    "already_present": 0,
    "appended": 16,
    "functions_appended": 10,
    "feeding_appended": 23
  }
}
```

No files were deleted. Existing populated canonical scientific rows were not overwritten.

