"""Prototype permission and dog-scope checks. Production auth is deferred."""

from __future__ import annotations

import re

from app.state.errors import DogNotFound
from app.state.models import PersistentDog
from app.state.store import get_dog
from app.tools.errors import (
    DOG_ACCESS_DENIED,
    DOG_NOT_FOUND,
    INVALID_TOOL_INPUT,
    TOOL_NOT_ALLOWED,
    ToolFailure,
)
from app.tools.models import ToolCaller
from app.tools.registry import RegisteredTool

_SAFE_ID = re.compile(r"^[A-Za-z0-9._:-]{1,80}$")


def require_safe_id(value: str, *, field: str) -> str:
    text = str(value or "").strip()
    if not text or not _SAFE_ID.match(text):
        raise ToolFailure(INVALID_TOOL_INPUT, f"malformed {field}", field=field)
    return text


def require_tool_role(tool: RegisteredTool, caller: ToolCaller) -> None:
    if caller.role not in tool.roles:
        raise ToolFailure(
            TOOL_NOT_ALLOWED,
            f"role {caller.role} cannot invoke {tool.name}",
            field="role",
            status=403,
        )


def authorize_dog(caller: ToolCaller, dog_id: str) -> PersistentDog:
    token = require_safe_id(dog_id, field="dog_id")
    dog = get_dog(token)
    if dog is None:
        raise ToolFailure(DOG_NOT_FOUND, f"dog {token} was not found", field="dog_id", status=404)
    if caller.authorized_dog_ids is not None:
        allowed = {str(item) for item in caller.authorized_dog_ids}
        if token not in allowed:
            raise ToolFailure(
                DOG_ACCESS_DENIED,
                "dog_id is outside the authorized session",
                field="dog_id",
                status=403,
            )
        return dog
    owner = caller.owner_id or "prototype-local"
    if dog.owner_id and dog.owner_id != owner:
        raise ToolFailure(
            DOG_ACCESS_DENIED,
            "dog is not in the authorized owner context",
            field="dog_id",
            status=403,
        )
    return dog


def map_dog_not_found(exc: DogNotFound) -> ToolFailure:
    return ToolFailure(DOG_NOT_FOUND, str(exc), field="dog_id", status=404)
