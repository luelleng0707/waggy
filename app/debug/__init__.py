"""Clinical Execution Explorer / PPIE debug surface.

Sole backend owner: ``clinical_execution_debug``.
"""

from app.debug.clinical_execution_debug import (
    DEFAULT_PRESET_ID,
    NOT_TRACEABLE,
    BOOT_ID,
    build_clinical_execution_explorer,
    build_engine_trace,
    build_validation_console,
    compare_analyses,
    console_to_markdown,
    debug_status_payload,
    developer_banner,
    get_preset_body,
    is_engine_debug,
    is_local_dev_boot,
    list_presets,
    list_repository_tables,
    maybe_open_validation_console,
    preview_table,
    print_developer_banner,
)

__all__ = [
    "BOOT_ID",
    "DEFAULT_PRESET_ID",
    "NOT_TRACEABLE",
    "build_clinical_execution_explorer",
    "build_engine_trace",
    "build_validation_console",
    "compare_analyses",
    "console_to_markdown",
    "debug_status_payload",
    "developer_banner",
    "get_preset_body",
    "is_engine_debug",
    "is_local_dev_boot",
    "list_presets",
    "list_repository_tables",
    "maybe_open_validation_console",
    "preview_table",
    "print_developer_banner",
]
