"""Backward-compatible API shim — prefer app.api.main for new integrations."""

from app.api.main import app

__all__ = ["app"]
