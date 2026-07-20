"""WarehouseDataPlatform — DataPlatform-compatible, fed by adapters."""

from __future__ import annotations

import logging
from pathlib import Path

from app.data.cache import build_meta
from app.data.repository import DataPlatform
from app.data.warehouse.legacy import LegacyCompatibilityLayer
from app.data.warehouse.materialize import (
    load_persisted_warehouse,
    materialize_warehouse,
    persist_warehouse,
)

logger = logging.getLogger(__name__)


class WarehouseDataPlatform(DataPlatform):
    """
    Same public surface as DataPlatform.

    Internally: legacy data/ → warehouse materialization → LegacyCompatibilityLayer
    → identical `_tables` → existing accessors / formulas.
    """

    def __init__(
        self,
        data_root: str | Path,
        warehouse_root: str | Path | None = None,
        *,
        strict: bool = True,
        persist: bool = False,
        require_parity: bool = True,
    ):
        self.data_root = Path(data_root)
        self.warehouse_root = Path(warehouse_root) if warehouse_root else (
            self.data_root.parent / "warehouse"
        )

        # Always materialize from live legacy so Phase 2 stays bit-identical
        # even if warehouse/ on disk is schema stubs.
        legacy = DataPlatform(self.data_root, strict=strict)
        warehouse = materialize_warehouse(legacy)

        if persist:
            persist_warehouse(warehouse, self.warehouse_root)
            logger.info("Persisted warehouse materialization to %s", self.warehouse_root)

        # Optional: if disk warehouse exists, prefer it only when parity holds
        disk = load_persisted_warehouse(self.warehouse_root)
        if disk is not None and "trait_condition_risk" in disk and len(disk["trait_condition_risk"]) > 0:
            layer_disk = LegacyCompatibilityLayer(disk)
            disk_report = layer_disk.compare_to_legacy(legacy._tables)
            if disk_report["ok"]:
                warehouse = disk
                logger.info("Using persisted warehouse (parity ok)")
            else:
                logger.warning(
                    "Persisted warehouse failed parity — using in-memory materialization"
                )

        layer = LegacyCompatibilityLayer(warehouse)
        self.parity_report = layer.compare_to_legacy(legacy._tables)
        if require_parity and not self.parity_report["ok"]:
            bad = {
                k: v for k, v in self.parity_report["tables"].items() if not v.get("ok")
            }
            raise RuntimeError(
                f"Warehouse↔legacy parity failed for {len(bad)} tables: "
                f"{list(bad)[:5]} … detail={bad and next(iter(bad.values()))}"
            )

        # Install DataPlatform state without re-reading CSVs via super().__init__
        self.manifest = legacy.manifest
        self._tables = layer.to_legacy_tables()
        paths = []
        for spec in self.manifest.files:
            from app.data.loader import resolve_csv_path

            paths.append(resolve_csv_path(self.data_root, spec.path))
        self.meta = build_meta(self.manifest.version, self.data_root, paths)
        self._indexes = {}
        self._build_indexes()
        self._warehouse = warehouse
        self._legacy_layer = layer
        self.backend = "warehouse_adapter"

    @property
    def warehouse_tables(self) -> dict:
        return self._warehouse
