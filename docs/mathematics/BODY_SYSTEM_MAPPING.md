# BODY_SYSTEM_MAPPING

## Formula identity
- Formula ID: `SYS-001`
- Version: `1.0.0`
- Module: `repository/reasoning/systems/aggregator.py`

## Purpose
Maps condition IDs to body systems via direct lookup.

## Equation
`BodySystem(condition_id) = lookup(reference.condition_systems.csv)`

## Inputs
- `condition_id` from `ConditionAssessment`
- mapping rows from `warehouse/reference/condition_systems.csv`

## ILLUSTRATIVE MATHEMATICAL EXAMPLE
- condition `COND_653473C1`
- mapped to body system `musculoskeletal`
