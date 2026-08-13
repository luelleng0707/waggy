"""PySide6 desktop presentation shell for Wagtopia integration."""

from __future__ import annotations

import json
import os
from typing import Any

from .adapter import WagtopiaPresentationAdapter
from .api_client import WagtopiaApiClient
from .demo_profiles import SYNTHETIC_DEMO_PROFILES
from .errors import AdapterError
from .models import AnalysisPresentation, AnalyzeDogRequest
from .suite_utils import DEBUG_TRACE_UNAVAILABLE, default_demo_profile

try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QApplication,
        QCheckBox,
        QComboBox,
        QDoubleSpinBox,
        QFormLayout,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QListWidget,
        QListWidgetItem,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QSpinBox,
        QStackedWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
except Exception:  # noqa: BLE001
    QApplication = None


def run_desktop() -> int:
    """Desktop app entrypoint."""
    if QApplication is None:
        raise RuntimeError("PySide6 is required. Install with: py -3 -m pip install PySide6")
    app = QApplication([])
    app.setApplicationName("Wagtopia CSTC Shell")
    window = LoginWindow()
    window.show()
    return app.exec()


class LoginWindow(QWidget):
    """Lightweight shell login to preserve CSTC interaction pattern."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wagtopia CSTC Shell - Login")
        self.setMinimumWidth(460)
        layout = QVBoxLayout(self)
        title = QLabel("Wagtopia CSTC Presentation Shell")
        title.setStyleSheet("font-size: 18px; font-weight: 600; margin-bottom: 12px;")
        layout.addWidget(title)

        form = QFormLayout()
        self.url_input = QLineEdit(os.getenv("WAGTOPIA_API_BASE_URL", "http://127.0.0.1:8000"))
        self.key_input = QLineEdit(os.getenv("WAGTOPIA_API_KEY", ""))
        self.key_input.setEchoMode(QLineEdit.Password)
        self.trace_checkbox = QCheckBox("Request debug trace when available")
        self.trace_checkbox.setChecked(True)
        form.addRow("API base URL", self.url_input)
        form.addRow("API key", self.key_input)
        form.addRow("", self.trace_checkbox)
        layout.addLayout(form)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #b00020;")
        layout.addWidget(self.status_label)

        row = QHBoxLayout()
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self._connect)
        row.addWidget(self.connect_button)
        layout.addLayout(row)

    def _connect(self):
        self.connect_button.setEnabled(False)
        self.status_label.setText("Checking API health...")
        api = WagtopiaApiClient(self.url_input.text().strip(), self.key_input.text().strip())
        try:
            health = api.health()
            adapter = WagtopiaPresentationAdapter(api)
            self.status_label.setText(f"Connected: status={health.get('status')}")
            self.main = MainWindow(adapter=adapter, debug_trace=self.trace_checkbox.isChecked())
            self.main.show()
            self.close()
        except Exception as exc:  # noqa: BLE001
            self.status_label.setText(str(exc))
            self.connect_button.setEnabled(True)


class MainWindow(QMainWindow):
    """CSTC-style shell: sidebar + stacked pages."""

    MENU = (
        "Dashboard",
        "Dog Profile",
        "Wellness Analysis",
        "Health & Evidence",
        "Products",
        "Care Packages",
        "Financial Model",
        "Calculation Trace",
        "About / System",
    )

    def __init__(self, adapter: WagtopiaPresentationAdapter, debug_trace: bool):
        super().__init__()
        self.adapter = adapter
        self.debug_trace = debug_trace
        self.default_demo_key, demo_profile = default_demo_profile()
        self.current_profile = demo_profile
        self.current_result: AnalysisPresentation | None = None
        self.current_trace: dict[str, Any] | None = None
        self.demo_mode = str(os.getenv("WAGTOPIA_DEMO_MODE", "")).strip().lower() in {"1", "true", "yes", "on"}

        self.setWindowTitle("Wagtopia CSTC Presentation Shell")
        self.resize(1260, 820)

        root = QWidget()
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)

        self.menu = QListWidget()
        self.menu.setMaximumWidth(240)
        self.menu.addItems(self.MENU)
        self.menu.currentRowChanged.connect(self._switch_page)
        layout.addWidget(self.menu)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)

        self.dashboard_page = self._build_dashboard_page()
        self.profile_page = self._build_profile_page()
        self.analysis_page = self._build_text_page("Wellness Analysis")
        self.evidence_page = self._build_text_page("Health & Evidence")
        self.products_page = self._build_text_page("Products")
        self.packages_page = self._build_text_page("Care Packages")
        self.financial_page = self._build_text_page("Financial Model")
        self.trace_page = self._build_text_page("Calculation Trace")
        self.about_page = self._build_about_page()

        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.profile_page)
        self.stack.addWidget(self.analysis_page)
        self.stack.addWidget(self.evidence_page)
        self.stack.addWidget(self.products_page)
        self.stack.addWidget(self.packages_page)
        self.stack.addWidget(self.financial_page)
        self.stack.addWidget(self.trace_page)
        self.stack.addWidget(self.about_page)
        self.menu.setCurrentRow(0)
        self._refresh_dashboard()
        if self.demo_mode:
            self._run_demo_mode()

    def _switch_page(self, idx: int):
        if idx >= 0:
            self.stack.setCurrentIndex(idx)

    def _build_dashboard_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 20px; font-weight: 600;")
        layout.addWidget(title)

        grid = QGridLayout()
        self.metric_labels: dict[str, QLabel] = {}
        for i, key in enumerate(
            (
                "Dogs analyzed",
                "Recommendations generated",
                "Products recommended",
                "Packages generated",
                "Average confidence",
                "Last analysis",
            )
        ):
            box = QGroupBox(key)
            box_layout = QVBoxLayout(box)
            value = QLabel("-")
            value.setStyleSheet("font-size: 22px; font-weight: 600;")
            value.setAlignment(Qt.AlignCenter)
            box_layout.addWidget(value)
            grid.addWidget(box, i // 3, i % 3)
            self.metric_labels[key] = value
        layout.addLayout(grid)

        self.status_area = QLabel("No analysis yet.")
        self.status_area.setWordWrap(True)
        layout.addWidget(self.status_area)
        return page

    def _build_profile_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        title = QLabel("Dog Profile")
        title.setStyleSheet("font-size: 20px; font-weight: 600;")
        layout.addWidget(title)

        profile_select = QHBoxLayout()
        self.demo_selector = QComboBox()
        self.demo_selector.addItems(
            [
                "SYNTHETIC DEMO PROFILE - Golden Retriever",
                "SYNTHETIC DEMO PROFILE - Husky",
                "SYNTHETIC DEMO PROFILE - Mixed Lab/Golden",
            ]
        )
        idx_map = {"golden_retriever": 0, "husky": 1, "mixed_lab_golden": 2}
        self.demo_selector.setCurrentIndex(idx_map.get(self.default_demo_key, 0))
        load_btn = QPushButton("Load synthetic profile")
        load_btn.clicked.connect(self._load_demo_profile)
        profile_select.addWidget(self.demo_selector, 1)
        profile_select.addWidget(load_btn)
        layout.addLayout(profile_select)

        form = QFormLayout()
        self.name_input = QLineEdit(self.current_profile.name)
        self.primary_input = QLineEdit(self.current_profile.primary_breed)
        self.secondary_input = QLineEdit(self.current_profile.secondary_breed or "")
        self.split_input = QDoubleSpinBox()
        self.split_input.setRange(0.0, 100.0)
        self.split_input.setValue(self.current_profile.breed_split_pct)
        self.split_input.setSuffix(" %")
        self.age_input = QDoubleSpinBox()
        self.age_input.setRange(0.1, 30.0)
        self.age_input.setValue(float(self.current_profile.age_years or 5.0))
        self.age_input.setSuffix(" years")
        self.birthday_input = QLineEdit(self.current_profile.birthday or "")
        self.weight_input = QDoubleSpinBox()
        self.weight_input.setRange(0.1, 120.0)
        self.weight_input.setValue(self.current_profile.weight_kg)
        self.weight_input.setSuffix(" kg")
        self.height_input = QDoubleSpinBox()
        self.height_input.setRange(0.0, 150.0)
        self.height_input.setValue(float(self.current_profile.height_cm or 0.0))
        self.height_input.setSuffix(" cm")
        self.sex_input = QLineEdit(self.current_profile.sex or "")
        self.activity_input = QLineEdit(self.current_profile.activity_level)
        self.env_input = QLineEdit(self.current_profile.current_environment)
        self.bcs_input = QDoubleSpinBox()
        self.bcs_input.setRange(0.0, 9.0)
        self.bcs_input.setValue(float(self.current_profile.bcs or 0.0))
        self.conditions_input = QLineEdit(", ".join(self.current_profile.observed_conditions))
        form.addRow("Name", self.name_input)
        form.addRow("Primary breed", self.primary_input)
        form.addRow("Secondary breed", self.secondary_input)
        form.addRow("Breed split", self.split_input)
        form.addRow("Age", self.age_input)
        form.addRow("Birthday (YYYY-MM-DD)", self.birthday_input)
        form.addRow("Weight", self.weight_input)
        form.addRow("Height", self.height_input)
        form.addRow("Sex", self.sex_input)
        form.addRow("Activity level", self.activity_input)
        form.addRow("Environment", self.env_input)
        form.addRow("BCS", self.bcs_input)
        form.addRow("Observed conditions (comma-separated)", self.conditions_input)
        layout.addLayout(form)

        actions = QHBoxLayout()
        analyze_btn = QPushButton("Run Wagtopia Analysis")
        analyze_btn.clicked.connect(self._run_analysis)
        actions.addWidget(analyze_btn)
        demo_btn = QPushButton("DEMO MODE: Load synthetic and run")
        demo_btn.clicked.connect(self._run_demo_mode)
        actions.addWidget(demo_btn)
        layout.addLayout(actions)

        self.profile_status = QLabel("")
        self.profile_status.setWordWrap(True)
        layout.addWidget(self.profile_status)
        return page

    def _build_text_page(self, title_text: str) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        title = QLabel(title_text)
        title.setStyleSheet("font-size: 20px; font-weight: 600;")
        layout.addWidget(title)
        text = QTextEdit()
        text.setReadOnly(True)
        layout.addWidget(text, 1)
        setattr(self, f"{title_text.lower().replace(' ', '_').replace('&', 'and')}_text", text)
        return page

    def _build_about_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        title = QLabel("About / System")
        title.setStyleSheet("font-size: 20px; font-weight: 600;")
        layout.addWidget(title)
        self.about_text = QTextEdit()
        self.about_text.setReadOnly(True)
        self.about_text.setText(
            "CSTC shell integrated with Wagtopia API.\n"
            "Computation owner: existing Wagtopia agent/runtime.\n"
            "No scientific calculations are performed in this UI."
        )
        layout.addWidget(self.about_text, 1)
        return page

    def _load_demo_profile(self):
        idx = self.demo_selector.currentIndex()
        key = ("golden_retriever", "husky", "mixed_lab_golden")[idx]
        self._set_profile(SYNTHETIC_DEMO_PROFILES[key])
        self.profile_status.setText(f"Loaded SYNTHETIC DEMO PROFILE: {key}")

    def _set_profile(self, profile: AnalyzeDogRequest):
        self.current_profile = profile
        self.name_input.setText(profile.name)
        self.primary_input.setText(profile.primary_breed)
        self.secondary_input.setText(profile.secondary_breed or "")
        self.split_input.setValue(float(profile.breed_split_pct))
        self.age_input.setValue(float(profile.age_years or 5.0))
        self.birthday_input.setText(profile.birthday or "")
        self.weight_input.setValue(float(profile.weight_kg))
        self.height_input.setValue(float(profile.height_cm or 0.0))
        self.sex_input.setText(profile.sex or "")
        self.activity_input.setText(profile.activity_level)
        self.env_input.setText(profile.current_environment)
        self.bcs_input.setValue(float(profile.bcs or 0.0))
        self.conditions_input.setText(", ".join(profile.observed_conditions))

    def _collect_profile(self) -> AnalyzeDogRequest:
        if not self.name_input.text().strip():
            raise ValueError("Name is required")
        if not self.primary_input.text().strip():
            raise ValueError("Primary breed is required")
        conds = tuple(
            x.strip() for x in self.conditions_input.text().split(",")
            if x.strip()
        )
        return AnalyzeDogRequest(
            name=self.name_input.text().strip(),
            primary_breed=self.primary_input.text().strip(),
            secondary_breed=self.secondary_input.text().strip() or None,
            breed_split_pct=float(self.split_input.value()),
            age_years=float(self.age_input.value()),
            birthday=self.birthday_input.text().strip() or None,
            weight_kg=float(self.weight_input.value()),
            height_cm=float(self.height_input.value()) if self.height_input.value() > 0 else None,
            sex=self.sex_input.text().strip() or None,
            activity_level=self.activity_input.text().strip() or "Moderate",
            current_environment=self.env_input.text().strip() or "Temperate Indoor",
            bcs=float(self.bcs_input.value()) if self.bcs_input.value() > 0 else None,
            observed_conditions=conds,
        )

    def _run_analysis(self):
        try:
            request = self._collect_profile()
        except ValueError as exc:
            QMessageBox.warning(self, "Profile validation", str(exc))
            return

        self.profile_status.setText("Running Wagtopia analysis...")
        QApplication.processEvents()
        try:
            result = self.adapter.run_analysis(request)
            self.current_profile = request
            self.current_result = result
            self.current_trace = None
            if self.debug_trace:
                try:
                    self.current_trace = self.adapter.fetch_trace(request)
                except AdapterError:
                    self.current_trace = {"message": DEBUG_TRACE_UNAVAILABLE}
            self._render_result(result)
            self.profile_status.setText("Analysis complete.")
            self.menu.setCurrentRow(2)
        except AdapterError as exc:
            QMessageBox.critical(self, "API error", str(exc))
            self.profile_status.setText(str(exc))

    def _render_result(self, result: AnalysisPresentation):
        self._refresh_dashboard()
        self.wellness_analysis_text.setPlainText(_json(result.raw_analyze))
        self.health_and_evidence_text.setPlainText(
            _json(
                {
                    "health_insights": result.health.insights,
                    "evidence": result.evidence.evidence,
                    "confidence": result.confidence.payload,
                    "validation": result.validation.payload or "Not available from current runtime",
                }
            )
        )
        self.products_text.setPlainText(_json({"products": result.products.products}))
        self.care_packages_text.setPlainText(_json({"packages": result.packages.packages}))
        self.financial_model_text.setPlainText(
            _json(
                {
                    "monthly_plan": result.financial.monthly_plan or "Not available from current runtime",
                    "yearly_plan": result.financial.yearly_plan or "Not available from current runtime",
                    "package_economics": result.financial.package_economics or "Not available from current runtime",
                }
            )
        )
        trace_payload = {
            "calculation_trace": result.trace.trace or "Trace field unavailable from current runtime",
            "formula_executions": result.trace.debug_formula_executions or "Trace field unavailable from current runtime",
            "debug_trace_endpoint": self.current_trace or DEBUG_TRACE_UNAVAILABLE,
        }
        self.calculation_trace_text.setPlainText(_json(trace_payload))
        self._update_about()

    def _run_demo_mode(self):
        idx = self.demo_selector.currentIndex()
        key = ("golden_retriever", "husky", "mixed_lab_golden")[idx]
        self._set_profile(SYNTHETIC_DEMO_PROFILES[key])
        self.profile_status.setText(f"DEMO MODE active. Loaded SYNTHETIC DEMO PROFILE: {key}")
        self._run_analysis()

    def _refresh_dashboard(self):
        self.metric_labels["Dogs analyzed"].setText(str(self.adapter.analysis_count))
        products = len(self.current_result.products.products) if self.current_result else 0
        packages = len(self.current_result.packages.packages) if self.current_result else 0
        recs = products + packages
        confidence = "-"
        if self.current_result:
            score = self.current_result.confidence.payload.get("wellness_score")
            confidence = str(score) if score is not None else "Not available from current runtime"
        self.metric_labels["Recommendations generated"].setText(str(recs))
        self.metric_labels["Products recommended"].setText(str(products))
        self.metric_labels["Packages generated"].setText(str(packages))
        self.metric_labels["Average confidence"].setText(confidence)
        self.metric_labels["Last analysis"].setText(self.current_result.dog.name if self.current_result else "-")
        self.status_area.setText(
            "Runtime source: existing Wagtopia API -> PPIEWellnessAgent. "
            "This dashboard displays only returned runtime values."
        )

    def _update_about(self):
        trace_mode = "enabled" if self.debug_trace else "disabled"
        self.about_text.setPlainText(
            "\n".join(
                [
                    "CSTC-style sidebar shell integrated with Wagtopia API transport.",
                    f"Debug trace requests: {trace_mode}",
                    "Displayed results originate from existing Wagtopia app runtime endpoints.",
                    "Repository runtime modules remain test/documentation pathways.",
                ]
            )
        )


def _json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=True, indent=2, default=str)
