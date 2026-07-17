"""One-shot import reference scan for PPIE JS retirement audit."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXTS = {".js", ".ts", ".py", ".md", ".html", ".ps1", ".sh", ".toml", ".json"}
SKIP_PARTS = {"node_modules", "__pycache__", "parity", ".git"}
NEEDLES = [
    "src/engine",
    "server/logic",
    "server.js",
    "computeRecommendations",
    "require('../engine",
    'require("../engine',
    "require('./logic",
    'require("./logic',
    "require('../logic",
    'require("../logic',
]


def main() -> None:
    hits: dict[str, list[str]] = {}
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in EXTS:
            continue
        if any(p in SKIP_PARTS for p in path.parts):
            continue
        if path.suffix == ".json" and path.stat().st_size > 200_000:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        found = [n for n in NEEDLES if n in text]
        if found:
            hits[str(path.relative_to(ROOT)).replace("\\", "/")] = found
    for key in sorted(hits):
        print(f"{key}: {', '.join(hits[key])}")


if __name__ == "__main__":
    main()
