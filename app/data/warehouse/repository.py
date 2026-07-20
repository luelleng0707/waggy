"""WarehouseRepository — DataRepository pinned to WarehouseDataPlatform."""

from __future__ import annotations

from pathlib import Path

from app.data.repository import DataRepository
from app.data.warehouse.platform import WarehouseDataPlatform


class WarehouseRepository(DataRepository):
    """
    Drop-in DataRepository whose platform is adapter-backed.

    Formulas call the same methods; frames are rebuilt from warehouse shape.
    """

    def __init__(
        self,
        data_root: str | Path = "data",
        warehouse_root: str | Path | None = None,
        *,
        strict: bool = True,
        persist: bool = False,
        require_parity: bool = True,
    ):
        platform = WarehouseDataPlatform(
            data_root,
            warehouse_root=warehouse_root,
            strict=strict,
            persist=persist,
            require_parity=require_parity,
        )
        super().__init__(data_root, platform=platform)
        self.warehouse_platform = platform
