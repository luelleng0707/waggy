"""
PPIE inference layer — pure functions + CSV-backed knowledge.

Does not own API routes. Locked clinical formulas remain in app.agent.*;
this package wraps, traces, and hosts opt-in future formulas.
"""

from app.inference import breed, confidence, config, explanation, ingredient, nutrition, resolver, risk, score
from app.inference import formula_registry
from app.inference.models import InferredValue, ModifierStep, NOT_TRACEABLE

__all__ = [
    "InferredValue",
    "ModifierStep",
    "NOT_TRACEABLE",
    "breed",
    "confidence",
    "config",
    "explanation",
    "formula_registry",
    "ingredient",
    "nutrition",
    "resolver",
    "risk",
    "score",
]
