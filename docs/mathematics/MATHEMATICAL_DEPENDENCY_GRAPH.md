# MATHEMATICAL_DEPENDENCY_GRAPH

## Current dependency flow (actual runtime order)

EvidenceGraph edges and citations
  -> MAT-1001 Observed prevalence
  -> MAT-1002 Aggregated evidence prevalence
  -> MAT-1003 Estimated prevalence (logit blend + interaction delta)
  -> MAT-1004 Agreement (observed vs estimated)
  -> MAT-1005 Confidence (edge volume + citation count + agreement)
  -> MAT-1006 Novelty (estimated-observed scaled by confidence)
  -> MAT-1008 Uncertainty (stddev of non-observed values scaled by confidence)
  -> MAT-1007 Priority (estimated x confidence x novelty x agreement scale)

## Double-counting / multi-path findings

1. Interaction evidence path duplication
- Path A: interaction edges contribute to MAT-1002 weighted logit aggregate.
- Path B: same interaction edges contribute again in MAT-1003 via additive `interaction_delta`.
- Classification: POTENTIAL_DOUBLE_COUNTING
- Flag: DOUBLE_COUNTING_RISK

2. Evidence volume reuse
- Path A: trait/environment/life/activity/ingredient edges determine MAT-1002 output.
- Path B: the same edge classes are counted again in MAT-1005 evidence component.
- Classification: POTENTIAL_DOUBLE_COUNTING
- Flag: DOUBLE_COUNTING_RISK

3. Confidence reuse downstream
- MAT-1006 novelty includes confidence scaling.
- MAT-1007 multiplies by confidence again.
- Classification: POTENTIAL_DOUBLE_COUNTING
- Flag: DOUBLE_COUNTING_RISK

4. Uncertainty channel overlap
- MAT-1008 uses non-observed evidence values already used by MAT-1002.
- Classification: VALID_MULTI_PATH_USE (same evidence reused for different target: dispersion proxy), with interpretability risk.

5. Life-stage and global prevention channels
- Life-stage evidence rows are attached to all condition nodes in evidence collector.
- Activity/ingredient rows are added from full datasets and can inflate edge counts per condition.
- Classification: CONFIRMED_DOUBLE_COUNTING risk at data-assembly layer for count-based downstream metrics.

## Evidence contribution map

- Observed edges -> MAT-1001 -> MAT-1003 prior -> MAT-1004 -> MAT-1005 -> MAT-1006 -> MAT-1007
- Trait/env/interaction/life/activity/ingredient edges -> MAT-1002 -> MAT-1003 -> MAT-1004/5/6/7/8
- Citation IDs -> MAT-1005 study_count
- MAT-1005 confidence -> MAT-1006, MAT-1007, MAT-1008

## Interaction dependency table

| interaction_fact | MAT formula | path | contribution | duplicate_path | risk |
|---|---|---|---|---|---|
| `interaction` edge `value_number` | MAT-1002 | interaction -> weighted logits | influences `evidence_percent` | yes, also used in MAT-1003 | POTENTIAL_DOUBLE_COUNTING |
| `interaction` edge `factor` + `value_number` | MAT-1003 | interaction -> `interaction_adjustment` | additive `interaction_delta` to posterior | yes, base interaction edge already in MAT-1002 | POTENTIAL_DOUBLE_COUNTING |

## Risk labels used
- VALID_MULTI_PATH_USE: same evidence used for different non-duplicative semantic role.
- POTENTIAL_DOUBLE_COUNTING: same evidence likely influences multiple mathematically overlapping signals.
- CONFIRMED_DOUBLE_COUNTING: implementation path duplicates contribution in a way likely to inflate impact.
