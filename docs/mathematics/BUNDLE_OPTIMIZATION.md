# BUNDLE_OPTIMIZATION

## Formula identity
- Formula ID: `OPT-712`
- Module: `repository/optimization/optimizer.py`

## Purpose
Selects highest harmony candidate subject to feasibility, deterministically.

## Equation
`OptimizedBundle = argmax(HarmonyScore) over feasible candidates`
Tie-break: `constraint_satisfaction desc`, then `candidate_id asc`.

## Inputs
- evaluated `OptimizedBundle` candidates from `OptimizationRuntime._evaluate_candidates`.

## ILLUSTRATIVE MATHEMATICAL EXAMPLE
- Candidate A: harmony 84.2 (feasible)
- Candidate B: harmony 84.2 (feasible)
- Candidate IDs `CAND_0003`, `CAND_0007`
- Winner: `CAND_0003` (stable lexicographic tie-break)
