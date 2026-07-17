"""Diary page view-model builder."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class DiaryDayVM:
    key: str
    label: str
    logs: list[dict[str, str]]


@dataclass
class DiaryPageVM:
    days: list[DiaryDayVM]
    selected_key: str
    selected_label: str
    selected_logs: list[dict[str, str]]


class DiaryRenderer:
    _LOGS = {
        "jul12": {"Coat": "Soft and glossy", "Tears": "Mild stain", "Mood": "Playful", "Weight": "29.8 kg"},
        "jul18": {"Coat": "Hydration improving", "Tears": "Stable", "Mood": "Very active", "Weight": "30.1 kg"},
        "aug2": {"Coat": "Excellent", "Tears": "Reduced", "Mood": "Calm", "Weight": "30.0 kg"},
        "aug15": {"Coat": "Stable", "Tears": "Minimal", "Mood": "Bright", "Weight": "30.0 kg"},
    }

    def build(self, selected_key: str = "jul12") -> DiaryPageVM:
        days = [
            DiaryDayVM(key=k, label=k.upper(), logs=[{"metric": m, "observation": v} for m, v in logs.items()])
            for k, logs in self._LOGS.items()
        ]
        selected = self._LOGS.get(selected_key, self._LOGS["jul12"])
        return DiaryPageVM(
            days=days,
            selected_key=selected_key,
            selected_label=selected_key.upper(),
            selected_logs=[{"metric": m, "observation": v} for m, v in selected.items()],
        )
