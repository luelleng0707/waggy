#!/usr/bin/env python3
"""Materialize warehouse/ science tables from live data/ (Phase 2)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.data.repository import DataPlatform
from app.data.warehouse.legacy import LegacyCompatibilityLayer
from app.data.warehouse.materialize import materialize_warehouse, persist_warehouse


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data")
    ap.add_argument("--warehouse", default="warehouse")
    args = ap.parse_args()
    data = ROOT / args.data if not Path(args.data).is_absolute() else Path(args.data)
    wh = ROOT / args.warehouse if not Path(args.warehouse).is_absolute() else Path(args.warehouse)

    legacy = DataPlatform(data, strict=True)
    warehouse = materialize_warehouse(legacy)
    persist_warehouse(warehouse, wh)
    report = LegacyCompatibilityLayer(warehouse).compare_to_legacy(legacy._tables)
    out = wh / "generated" / "phase2_parity_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Persisted warehouse -> {wh}")
    print(f"Parity ok={report['ok']} tables={len(report['tables'])}")
    if not report["ok"]:
        bad = {k: v for k, v in report["tables"].items() if not v.get("ok")}
        print("Failures:", json.dumps(bad, indent=2)[:2000])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
