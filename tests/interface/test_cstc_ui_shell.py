from __future__ import annotations

import sys

import pytest


def _qt():
    return pytest.importorskip("PySide6.QtWidgets")


class _FakeAdapter:
    def __init__(self):
        self.analysis_count = 0
        self.last_result = None

    def run_analysis(self, request):
        from app.ui.cstc.view_models import build_presentation

        self.analysis_count += 1
        analyze = {
            "profile": {
                "pet_name": request.name,
                "breeds": [request.primary_breed],
                "age_years": request.age_years,
                "weight_kg": request.weight_kg,
                "current_environment": request.current_environment,
            },
            "productRecommendations": [],
            "wellnessPackages": [],
            "scientificEvidence": [],
            "calculationTrace": [],
            "debug": {"formula_executions": []},
        }
        self.last_result = build_presentation(analyze, assessment={})
        return self.last_result

    def fetch_trace(self, request):
        del request
        return {"trace": "ok"}


def test_ui_shell_starts_and_profile_flow():
    qt = _qt()
    from app.ui.cstc.desktop import MainWindow

    app = qt.QApplication.instance() or qt.QApplication(sys.argv)
    window = MainWindow(adapter=_FakeAdapter(), debug_trace=True)
    assert window.menu.count() == 9
    window._load_demo_profile()
    req = window._collect_profile()
    assert req.primary_breed
    window._run_analysis()
    assert window.current_result is not None
    window.close()
    app.quit()
