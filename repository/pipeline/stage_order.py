"""Canonical stage order for the permanent Waggy runtime pipeline."""

PIPELINE_STAGE_ORDER: tuple[str, ...] = (
    "Dog Resolver",
    "Life Stage Resolver",
    "Environment Resolver",
    "Trait Resolver",
    "Observation Resolver",
    "Resolved Dog Validator",
    "Evidence Collector",
    "Evidence Graph Builder",
)
