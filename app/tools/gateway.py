"""Allowlisted tool execution. Not a scientific engine and not an MCP server."""

from __future__ import annotations

from uuid import uuid4

from pydantic import ValidationError

from app.tools.adapters.compare import compare_analyses, get_recalculation_explanation
from app.tools.adapters.dogs import get_dog_profile
from app.tools.adapters.preference import propose_preference
from app.tools.adapters.products import CatalogLoader, get_products
from app.tools.adapters.slices import analyze_health, calculate_nutrition, get_package_options
from app.tools.auth import require_tool_role
from app.tools.errors import (
    INVALID_TOOL_INPUT,
    TOOL_EXECUTION_ERROR,
    TOOL_NOT_ALLOWED,
    ToolFailure,
    UNKNOWN_TOOL,
)
from app.tools.models import (
    ToolCaller,
    ToolEnvelope,
    ToolErrorItem,
    ToolMeta,
    ToolRequestMeta,
)
from app.tools.registry import (
    FORBIDDEN_ARGUMENT_KEYS,
    FORBIDDEN_TOOL_NAMES,
    REGISTERED_TOOLS,
    registered_tool,
)
from app.tools.version import TOOL_SCHEMA_VERSION, TOOL_VERSION, WAGGY_TOOL_RESULT_SCHEMA

_HANDLERS = {
    "get_dog_profile": get_dog_profile,
    "analyze_health": analyze_health,
    "calculate_nutrition": calculate_nutrition,
    "get_package_options": get_package_options,
    "get_recalculation_explanation": get_recalculation_explanation,
    "compare_analyses": compare_analyses,
    "propose_preference": propose_preference,
}


def _envelope(
    *,
    tool_name: str,
    request_id: str,
    status: str,
    data: dict | None,
    errors: list[ToolErrorItem],
    provenance: dict,
) -> ToolEnvelope:
    return ToolEnvelope(
        schema_name=WAGGY_TOOL_RESULT_SCHEMA,
        tool=ToolMeta(name=tool_name or "unknown", version=TOOL_VERSION, schema_version=TOOL_SCHEMA_VERSION),
        request=ToolRequestMeta(request_id=request_id),
        status=status,  # type: ignore[arg-type]
        data=data,
        provenance=provenance,
        errors=errors,
        scientific=False,
        llm_used=False,
    )


class WaggyToolGateway:
    def __init__(self, *, catalog_loader: CatalogLoader | None = None) -> None:
        self.catalog_loader = catalog_loader

    def list_registered_tools(self) -> list[dict]:
        return [
            {
                "name": spec.name,
                "version": spec.version,
                "schema_version": spec.schema_version,
                "description": spec.description,
                "mutates": spec.mutates,
                "roles": sorted(spec.roles),
            }
            for spec in REGISTERED_TOOLS.values()
        ]

    def invoke(
        self,
        name: str,
        arguments: dict | None,
        caller: ToolCaller | None = None,
        *,
        request_id: str | None = None,
    ) -> ToolEnvelope:
        rid = str(request_id or uuid4())
        caller = caller or ToolCaller()
        tool_name = str(name or "").strip()
        try:
            data = self._execute(tool_name, arguments, caller)
            return _envelope(
                tool_name=tool_name,
                request_id=rid,
                status="ok",
                data=data,
                errors=[],
                provenance={
                    "gateway": "WaggyToolGateway",
                    "source": "allowlisted_adapter",
                    "llm_used": False,
                },
            )
        except ToolFailure as exc:
            return _envelope(
                tool_name=tool_name,
                request_id=rid,
                status="error",
                data=None,
                errors=[ToolErrorItem.model_validate(exc.as_error_item())],
                provenance={"gateway": "WaggyToolGateway", "llm_used": False},
            )
        except ValidationError as exc:
            field = None
            if exc.errors():
                loc = exc.errors()[0].get("loc") or ()
                if loc:
                    field = str(loc[0])
            return _envelope(
                tool_name=tool_name,
                request_id=rid,
                status="error",
                data=None,
                errors=[
                    ToolErrorItem(
                        code=INVALID_TOOL_INPUT,
                        message="tool arguments failed schema validation",
                        field=field,
                    )
                ],
                provenance={"gateway": "WaggyToolGateway", "llm_used": False},
            )
        except Exception:
            return _envelope(
                tool_name=tool_name,
                request_id=rid,
                status="error",
                data=None,
                errors=[
                    ToolErrorItem(
                        code=TOOL_EXECUTION_ERROR,
                        message="tool execution failed",
                        field=None,
                    )
                ],
                provenance={"gateway": "WaggyToolGateway", "llm_used": False},
            )

    def _execute(self, name: str, arguments: dict | None, caller: ToolCaller) -> dict:
        if name in FORBIDDEN_TOOL_NAMES:
            raise ToolFailure(TOOL_NOT_ALLOWED, "tool is not allowed", field="tool", status=403)
        if name not in REGISTERED_TOOLS:
            raise ToolFailure(UNKNOWN_TOOL, f"tool {name!r} is not registered", field="tool")
        if arguments is None:
            arguments = {}
        if not isinstance(arguments, dict):
            raise ToolFailure(INVALID_TOOL_INPUT, "arguments must be an object", field="arguments")
        banned = FORBIDDEN_ARGUMENT_KEYS.intersection(arguments)
        if banned:
            raise ToolFailure(
                INVALID_TOOL_INPUT,
                "arguments contain disallowed query/execution fields",
                field=sorted(banned)[0],
            )
        spec = registered_tool(name)
        if spec is None:
            raise ToolFailure(UNKNOWN_TOOL, f"tool {name!r} is not registered", field="tool")
        require_tool_role(spec, caller)
        payload = spec.input_model.model_validate(arguments)
        if spec.mutates:
            raise ToolFailure(TOOL_NOT_ALLOWED, "mutation tools are not registered in Ω17.4", field="tool", status=403)
        if name == "get_products":
            return get_products(payload, caller, catalog_loader=self.catalog_loader)
        handler = _HANDLERS[spec.handler]
        return handler(payload, caller)


def invoke_tool(
    name: str,
    arguments: dict | None = None,
    caller: ToolCaller | None = None,
    *,
    gateway: WaggyToolGateway | None = None,
    request_id: str | None = None,
) -> ToolEnvelope:
    active = gateway or WaggyToolGateway()
    return active.invoke(name, arguments, caller, request_id=request_id)
