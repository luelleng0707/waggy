"""ΩL Plugin SDK — extensions without touching the clinical core."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable


class FormulaPlugin(ABC):
    """Optional FormulaNode factory. Core graph remains default_nodes() unless explicitly composed."""

    @abstractmethod
    def formula_id(self) -> str: ...

    @abstractmethod
    def create_node(self) -> Any: ...


class RepositoryPlugin(ABC):
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def extend_tables(self, tables: dict[str, Any]) -> dict[str, Any]: ...


class GraphPlugin(ABC):
    @abstractmethod
    def enrich(self, graph: Any) -> Any: ...


class DashboardPlugin(ABC):
    @abstractmethod
    def panel_html(self) -> str: ...


class ValidatorPlugin(ABC):
    @abstractmethod
    def validate(self, platform: Any) -> dict[str, Any]: ...


class ExporterPlugin(ABC):
    @abstractmethod
    def export(self, assessment: Any) -> Any: ...


class PluginRegistry:
    def __init__(self) -> None:
        self.formula: list[FormulaPlugin] = []
        self.repository: list[RepositoryPlugin] = []
        self.graph: list[GraphPlugin] = []
        self.dashboard: list[DashboardPlugin] = []
        self.validator: list[ValidatorPlugin] = []
        self.exporter: list[ExporterPlugin] = []

    def summary(self) -> dict[str, int]:
        return {
            "formula": len(self.formula),
            "repository": len(self.repository),
            "graph": len(self.graph),
            "dashboard": len(self.dashboard),
            "validator": len(self.validator),
            "exporter": len(self.exporter),
        }


REGISTRY = PluginRegistry()
