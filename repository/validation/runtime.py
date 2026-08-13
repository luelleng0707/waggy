"""Load validation datasets for future clinical evaluation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


class ValidationDatasetLoader:
    def load(self, relative_path: str) -> pd.DataFrame:
        root = Path(__file__).resolve().parents[2]
        target = root / relative_path
        return pd.read_csv(target, dtype=str, keep_default_na=False)
