"""Run canonical warehouse validation and emit validation_report.md."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from config import get_settings
from repository.warehouse import WarehouseInterface


def main() -> int:
    settings = get_settings()
    interface = WarehouseInterface(settings.warehouse_root)
    report = interface.validate()
    text = interface.render_validation_report(report)
    settings.validation_report_path.parent.mkdir(parents=True, exist_ok=True)
    settings.validation_report_path.write_text(text, encoding="utf-8")
    print(f"Wrote {settings.validation_report_path}")
    print("PASS" if report.ok else "FAIL")
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
