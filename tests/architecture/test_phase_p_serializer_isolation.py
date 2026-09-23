"""Phase P — HTTP evidence contract cannot import the Phase L profile serializer."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_payload_serializers_no_longer_share_a_name():
    profile = (ROOT / "app" / "state" / "evidence.py").read_text(encoding="utf-8")
    report = (ROOT / "app" / "state" / "evidence_report.py").read_text(encoding="utf-8")
    adapter = (ROOT / "app" / "api" / "evidence_report.py").read_text(encoding="utf-8")
    assert "def evidence_profile_payload" in profile
    assert "def evidence_report_payload" not in profile
    assert "def evidence_report_payload" in report
    assert "def evidence_profile_payload" not in report
    assert "evidence_profile_payload" not in adapter
    assert "from app.state.evidence import" not in adapter
    assert "from app.state.evidence_report import build_evidence_report, evidence_report_payload" in adapter
