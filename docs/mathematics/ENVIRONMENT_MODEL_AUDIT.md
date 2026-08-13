# ENVIRONMENT_MODEL_AUDIT

## Current implementation summary
- Resolver: `repository/pipeline/biological_runtime.py::WarehouseBackedEnvironmentResolver.resolve`
- Evidence ingestion: `WarehouseBackedEvidenceCollector.collect` with climate-based matching against `biology.environment_facts`.
- Mathematical use: environment edges are included in MAT-1002 non-observed pool with weight `0.70`.

## Inputs captured from user/runtime profile
- climate
- season
- urbanicity
- housing
- walking_environment
- environment text
- city/country

## Inputs currently used for evidence matching
- Primary key for environment evidence matching: `environment.climate` string compared to `environment_name`.
- If climate is empty, first token matching against free-text environment is attempted.

## Measured environmental fact vs assumed behavior
- Measured environmental fact (supported path): climate/environment labels present in `biology.environment_facts` rows.
- Assumed user behavior (not separately evidenced in current math path): walking duration/behavioral exposure implied by profile fields but not transformed through dedicated measured effect models.

## Hardcoded/heuristic elements
- Climate-string fallback and first-token matching.
- Evidence-type weight for environment in MAT-1002 (`0.70`) from hardcoded map.

## Shanghai-specific audit finding
- Current path does not prove city-specific epidemiological coefficients for Shanghai.
- City is captured in profile, but climate-string evidence matching is the direct mathematical trigger.
- Therefore, Shanghai effects should be interpreted as environment-label extrapolation unless explicit Shanghai-specific rows are added and selected.

## Risk classification
- ENVIRONMENT_DATA_STATUS: PARTIAL
- ENVIRONMENT_MODEL_STATUS: ENGINEERING_AUGMENTED
- PUBLICATION_RISK: HIGH when interpreted as city-specific causal prevalence effects.

## Recommendation for future redesign
- Separate measured environment facts (temperature/humidity/pollutants/seasonality) from assumed behavior inputs.
- Introduce explicit covariates with provenance, units, and evidence links.
- Preserve city and behavior inputs as metadata until evidence-backed transforms are available.
