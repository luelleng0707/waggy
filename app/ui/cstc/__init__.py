"""CSTC-style desktop presentation shell for Wagtopia."""

from .adapter import WagtopiaPresentationAdapter
from .api_client import WagtopiaApiClient
from .desktop import run_desktop
from .models import AnalyzeDogRequest

__all__ = [
    "AnalyzeDogRequest",
    "WagtopiaApiClient",
    "WagtopiaPresentationAdapter",
    "run_desktop",
]
