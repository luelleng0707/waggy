"""Error types for CSTC Wagtopia presentation adapter."""

from __future__ import annotations


class AdapterError(RuntimeError):
    """Base adapter error."""


class TransportError(AdapterError):
    """Raised when HTTP transport fails."""


class ApiResponseError(AdapterError):
    """Raised when API returns an error response."""

    def __init__(self, status_code: int, detail: str):
        super().__init__(f"API error {status_code}: {detail}")
        self.status_code = status_code
        self.detail = detail


class MappingError(AdapterError):
    """Raised when response cannot be mapped to presentation models."""
