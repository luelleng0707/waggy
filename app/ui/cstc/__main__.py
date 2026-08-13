"""Module entrypoint for Wagtopia CSTC desktop shell."""

from __future__ import annotations

from .desktop import run_desktop


if __name__ == "__main__":
    raise SystemExit(run_desktop())
