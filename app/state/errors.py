"""Typed dog-state errors. Do not leak stack traces."""

from __future__ import annotations

from typing import Any


class DogStateError(ValueError):
    def __init__(self, code: str, message: str, *, field: str | None = None, status: int = 400) -> None:
        self.code = code
        self.field = field
        self.status = status
        super().__init__(message)

    def to_http_body(self) -> dict[str, Any]:
        return {
            "error": {
                "code": self.code,
                "message": str(self),
                "field": self.field,
                "fields": [self.field] if self.field else [],
            }
        }


class DogNotFound(DogStateError):
    def __init__(self, dog_id: str) -> None:
        super().__init__("DOG_NOT_FOUND", f"dog {dog_id} was not found", field="dog_id", status=404)
