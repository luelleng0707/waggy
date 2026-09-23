"""Internal Waggy tool gateway. AI may call these; it may not import the engine."""

from app.tools.gateway import WaggyToolGateway, invoke_tool
from app.tools.models import ToolCaller, ToolEnvelope, ToolInvokeRequest
from app.tools.registry import REGISTERED_TOOLS, registered_names
from app.tools.version import TOOL_SCHEMA_VERSION, TOOL_VERSION, WAGGY_TOOL_RESULT_SCHEMA

__all__ = [
    "REGISTERED_TOOLS",
    "TOOL_SCHEMA_VERSION",
    "TOOL_VERSION",
    "WAGGY_TOOL_RESULT_SCHEMA",
    "ToolCaller",
    "ToolEnvelope",
    "ToolInvokeRequest",
    "WaggyToolGateway",
    "invoke_tool",
    "registered_names",
]
