"""PPIE agent package."""

from __future__ import annotations

from typing import Any

__all__ = ["PPIEWellnessAgent", "DogProfileInput", "WellnessReportPayload"]


def __getattr__(name: str) -> Any:
    if name == "PPIEWellnessAgent":
        from app.agent.engine import PPIEWellnessAgent

        return PPIEWellnessAgent
    if name in ("DogProfileInput", "WellnessReportPayload"):
        from app.agent import state

        return getattr(state, name)
    raise AttributeError(name)
