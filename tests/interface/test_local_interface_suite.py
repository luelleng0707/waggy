from __future__ import annotations

from argparse import Namespace
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading

from app.ui.cstc.adapter import WagtopiaPresentationAdapter
from app.ui.cstc.demo_profiles import SYNTHETIC_DEMO_PROFILES
from app.ui.cstc.suite_utils import (
    DEBUG_TRACE_UNAVAILABLE,
    default_demo_profile,
    find_open_port,
    health_check,
    snapshot_from_analyze,
    snapshot_from_presentation,
    wait_for_health,
)
from scripts.run_wagtopia_local import LocalInterfaceSuite


class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        if self.path == "/health":
            body = json.dumps({"status": "ok"}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):  # noqa: A003
        del format, args


class _FakeClient:
    def analyze(self, payload):
        return {
            "profile": {
                "pet_name": payload["pet_name"],
                "breeds": payload["breeds"],
                "age_years": payload.get("age_years"),
                "weight_kg": payload.get("weight"),
            },
            "healthInsights": [{"title": "Joint", "priority_score": 70}],
            "productRecommendations": [{"product_id": "P1"}],
            "wellnessPackages": [{"tier": "essential", "price_rmb": 200}],
            "monthly_plan": {"total_cost": 300},
            "yearly_plan": {"total_cost": 3000},
            "scientificEvidence": [{"source_name": "Paper"}],
            "debug": {"formula_executions": [{"formula_id": "MAT-1005"}]},
        }

    def assess(self, payload):
        del payload
        return {"validation": {"ok": True}, "confidence": {"score": 0.8}}

    def health(self):
        return {"status": "ok"}

    def breeds(self, query=None):
        del query
        return ["Golden Retriever"]

    def trace(self, payload):
        del payload
        return {"trace": "ok"}


def _run_health_server():
    server = ThreadingHTTPServer(("127.0.0.1", 0), _HealthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def test_demo_profile_is_deterministic_default():
    key, profile = default_demo_profile()
    assert key == "mixed_lab_golden"
    assert profile == SYNTHETIC_DEMO_PROFILES["mixed_lab_golden"]


def test_api_health_detection_and_wait():
    server = _run_health_server()
    try:
        host, port = server.server_address
        base = f"http://{host}:{port}"
        ok, detail = health_check(base)
        assert ok is True
        assert detail == "ok"
        ok_wait, detail_wait = wait_for_health(base, timeout_seconds=1.5, interval_seconds=0.1)
        assert ok_wait is True
        assert detail_wait == "ok"
    finally:
        server.shutdown()
        server.server_close()


def test_endpoint_unavailable_is_reported():
    ok, detail = health_check("http://127.0.0.1:9")
    assert ok is False
    assert detail


def test_cross_interface_snapshot_consistency():
    adapter = WagtopiaPresentationAdapter(client=_FakeClient())
    request = SYNTHETIC_DEMO_PROFILES["golden_retriever"]
    payload = adapter.to_api_payload(request)
    analyze = adapter.client.analyze(payload)
    presentation = adapter.run_analysis(request)
    snap_analyze = snapshot_from_analyze(analyze)
    snap_present = snapshot_from_presentation(presentation)
    assert snap_analyze.dog_name == snap_present.dog_name
    assert snap_analyze.primary_breed == snap_present.primary_breed
    assert snap_analyze.product_count == snap_present.product_count
    assert snap_analyze.package_count == snap_present.package_count
    assert snap_analyze.monthly_total == snap_present.monthly_total
    assert snap_analyze.yearly_total == snap_present.yearly_total
    assert snap_analyze.evidence_count == snap_present.evidence_count
    assert snap_analyze.formula_ids == snap_present.formula_ids


def test_missing_trace_graceful_degradation_message_constant():
    assert "Debug trace unavailable" in DEBUG_TRACE_UNAVAILABLE


def test_launcher_configuration_validation_and_ports():
    open_port = find_open_port("127.0.0.1", 8000)
    args = Namespace(
        api_host="127.0.0.1",
        api_port=open_port,
        ui_port=8080,
        api_key="wagtopia-demo-key",
        no_browser=True,
        no_desktop=True,
        demo_mode=True,
        api_debug=True,
        smoke_seconds=1,
    )
    suite = LocalInterfaceSuite(args)
    assert suite.api_base_url.startswith("http://127.0.0.1:")
    assert suite.customer_url.endswith("/")
    assert suite.business_url.endswith("/business")
    assert suite.developer_url.endswith("/developer")
