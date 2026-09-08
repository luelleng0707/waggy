"""Ω11 canonical agent data contracts.

Transport/typed-boundary layer only. Does not reason, optimize, or write
warehouse facts. Future tools (Ω13) will expose these models.
"""

from __future__ import annotations

from app.contracts.agent.versions import AGENT_CONTRACT_SCHEMA_VERSION

__all__ = ["AGENT_CONTRACT_SCHEMA_VERSION"]
