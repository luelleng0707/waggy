"""Load formula configuration datasets from warehouse/formulas."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from repository.warehouse import WarehouseInterface
from repository.warehouse.warehouse_interface import CANONICAL_DATASETS


FORMULA_DATASETS: dict[str, str] = {
    "formulas.formulas": "formulas/formulas.csv",
    "formulas.formula_versions": "formulas/formula_versions.csv",
    "formulas.parameter_sets": "formulas/parameter_sets.csv",
    "formulas.parameters": "formulas/parameters.csv",
    "formulas.coefficients": "formulas/coefficients.csv",
    "formulas.benchmarks": "formulas/benchmarks.csv",
    "formulas.validation_sets": "formulas/validation_sets.csv",
}


def register_formula_datasets() -> None:
    for dataset_name, relative_path in FORMULA_DATASETS.items():
        if dataset_name not in CANONICAL_DATASETS:
            CANONICAL_DATASETS[dataset_name] = Path(relative_path)


class FormulaWarehouseLoader:
    def __init__(self, warehouse: WarehouseInterface):
        register_formula_datasets()
        self.warehouse = warehouse

    def load(self) -> dict[str, pd.DataFrame]:
        return {name: self.warehouse.load_dataset(name) for name in FORMULA_DATASETS}
