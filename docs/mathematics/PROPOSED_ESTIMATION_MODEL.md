# PROPOSED_ESTIMATION_MODEL

This is a design comparison for future replacement/revision of MAT-1002/MAT-1003. No production implementation changes are made in Omega 9.5.

## Candidate A - Weighted deterministic trait model
- Required data: trait-condition effects, environment-condition effects, interaction effects with calibrated scales.
- Assumptions: linear/additive or multiplicative deterministic effects approximate prevalence shifts.
- Mathematical form: `P_est = f(P_obs, sum(w_i * effect_i))`.
- Advantages: simple, interpretable, deterministic.
- Limitations: can overfit engineering assumptions; weak uncertainty semantics.
- Mixed breeds: requires explicit breed-mixture or phenotype weighting extension.
- Environment: direct covariates possible if measured values exist.
- Interactions: explicit terms straightforward.
- New studies: manual reparameterization required.
- Uncertainty intervals: heuristic unless extra variance model added.
- Interpretability: high.
- Publication defensibility: medium only if weights are empirically estimated.

## Candidate B - Log-odds model
- Required data: prevalence-like inputs translatable to probabilities.
- Assumptions: logit space is appropriate; weighted average of logits is meaningful.
- Mathematical form: `logit(P_est) = alpha + sum(beta_i * x_i)` or weighted blend.
- Advantages: handles bounded probabilities naturally.
- Limitations: requires defensible coefficient estimation; sensitivity near bounds.
- Mixed breeds: can integrate ancestry/phenotype covariates.
- Environment: include as covariates with measured data.
- Interactions: pairwise or structured terms.
- New studies: coefficient re-estimation needed.
- Uncertainty intervals: available with variance estimation.
- Interpretability: medium-high.
- Publication defensibility: medium-high if coefficients estimated from traceable datasets.

## Candidate C - Bayesian model
- Required data: explicit prior definition, likelihood model P(E|H), and evidence noise assumptions.
- Assumptions: prior and likelihood are mathematically justified and calibrated.
- Mathematical form: `P(H|E) propto P(E|H) * P(H)` with normalized posterior.
- Advantages: explicit uncertainty and update semantics.
- Limitations: data intensive; model misspecification risk.
- Mixed breeds: priors can be mixture distributions.
- Environment: modeled as likelihood covariates or hierarchical effects.
- Interactions: encoded in likelihood structure.
- New studies: natural posterior update path.
- Uncertainty intervals: direct posterior credible intervals.
- Interpretability: medium (requires statistical literacy).
- Publication defensibility: high only if priors/likelihoods are explicit and evidence-backed.

## Candidate D - Generalized linear model (GLM)
- Required data: curated training table with outcomes and predictors.
- Assumptions: link function correctness, feature independence structure as specified.
- Mathematical form: `g(E[Y]) = beta_0 + beta^T x`.
- Advantages: standard, well-understood, testable.
- Limitations: needs labeled datasets with coverage.
- Mixed breeds: predictor engineering required.
- Environment: direct predictors possible.
- Interactions: explicit interaction terms.
- New studies: periodic retraining/refit.
- Uncertainty intervals: standard errors/confidence intervals available.
- Interpretability: medium-high.
- Publication defensibility: high when dataset and diagnostics are transparent.

## Candidate E - Hierarchical/multilevel model
- Required data: grouped observations (breed, region, study), enough samples per group.
- Assumptions: partial pooling structure valid.
- Mathematical form: group-level random effects around global parameters.
- Advantages: handles sparse groups and mixed populations better.
- Limitations: complexity and computational cost.
- Mixed breeds: can model breed-level partial pooling and latent mixture effects.
- Environment: region/climate random effects possible.
- Interactions: hierarchical interaction modeling possible.
- New studies: posterior or refit updates.
- Uncertainty intervals: rich and explicit.
- Interpretability: medium.
- Publication defensibility: high if model spec and data are robust.

## Candidate F - Evidence-weighted probabilistic graphical model
- Required data: mechanism graph, conditional probability tables or learned factors.
- Assumptions: graph structure and conditional independencies are defensible.
- Mathematical form: factorized joint distribution over evidence/mechanism/condition states.
- Advantages: explicit dependency structure and explainability.
- Limitations: high data demand and curation burden.
- Mixed breeds: latent phenotype nodes possible.
- Environment: separate observed and behavioral nodes.
- Interactions: natural multi-path representation.
- New studies: update factors incrementally.
- Uncertainty intervals: probabilistic by design.
- Interpretability: medium-high with good tooling.
- Publication defensibility: high if graph assumptions are validated.

## Selection guidance under current data reality
- Current warehouse supports deterministic evidence retrieval and traceability, but not yet a fully specified likelihood model.
- Near-term defensible path: calibrated log-odds/GLM hybrid with explicit coefficient estimation and uncertainty channels.
- Longer-term path: hierarchical Bayesian or probabilistic graphical model once mechanism and validation datasets are expanded and cleaned.
