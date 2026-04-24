from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTabWidget,
)
from PySide6.QtCore import Qt

from view.analysis.overview_tab import OverviewTab
from view.analysis.risk_profile_tab import RiskProfileTab
from view.analysis.controls_tab import ControlsTab
from view.analysis.priority_risks_tab import PriorityRisksTab


class AnalysisView(QWidget):
    """
    Vista principal del módulo de Análisis de Riesgos (ERM / GRC).
    Orquesta las pestañas y gestiona el estado global del análisis.
    """

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        # --------------------------------------------------
        # Estado global
        # --------------------------------------------------
        self._risk_level_filter = None  # "BAJO" | "MEDIO" | "ALTO" | "CRÍTICO" | None

        # --------------------------------------------------
        # Layout principal
        # --------------------------------------------------
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(24, 20, 24, 20)

        title = QLabel("Risk Analysis")
        title.setStyleSheet("font-size:22px; font-weight:bold;")
        self.main_layout.addWidget(title)

        subtitle = QLabel(
            "Risk profile assessment, control effectiveness and action priorities"
        )
        subtitle.setStyleSheet("color:#666;")
        self.main_layout.addWidget(subtitle)

        # --------------------------------------------------
        # Estado vacío
        # --------------------------------------------------
        self.empty_container = QWidget()
        empty_layout = QVBoxLayout(self.empty_container)
        empty_layout.setAlignment(Qt.AlignCenter)

        empty_title = QLabel("Analysis unavailable")
        empty_title.setStyleSheet("font-size:18px; font-weight:bold;")

        empty_text = QLabel(
            "Complete the previous steps first:\n"
            "• Risk selection\n"
            "• Criticality editing\n"
            "• Control selection"
        )
        empty_text.setAlignment(Qt.AlignCenter)
        empty_text.setStyleSheet("color:#666;")

        empty_layout.addWidget(empty_title)
        empty_layout.addWidget(empty_text)

        self.main_layout.addWidget(self.empty_container)

        # --------------------------------------------------
        # Tabs
        # --------------------------------------------------
        self.tabs = QTabWidget()

        self.overview_tab = OverviewTab(controller)
        self.risk_profile_tab = RiskProfileTab(controller)
        self.controls_tab = ControlsTab(controller)
        self.priority_risks_tab = PriorityRisksTab(controller)

        self.tabs.addTab(self.overview_tab, "Overview")
        self.tabs.addTab(self.risk_profile_tab, "Risk Profile")
        self.tabs.addTab(self.controls_tab, "Controls & Mitigation")
        self.tabs.addTab(self.priority_risks_tab, "Priority Risks")

        self.main_layout.addWidget(self.tabs)

        # --------------------------------------------------
        # Primera carga
        # --------------------------------------------------
        self.refresh()

    # ==================================================
    # API DE FILTRO (usada por el donut)
    # ==================================================
    def set_risk_level_filter(self, level: str | None):
        """
        Fija o limpia el filtro de nivel de riesgo.
        level: "BAJO" | "MEDIO" | "ALTO" | "CRÍTICO" | None
        """
        self._risk_level_filter = level
        self.risk_profile_tab.donut_chart.set_active_level(level)
        self.refresh()

    # ==================================================
    # REFRESH GLOBAL
    # ==================================================
    def refresh(self):
        """
        Refresca todas las pestañas del módulo de análisis.
        """

        active = self.controller.company_assessment.get_active_risks()

        if not active:
            self.empty_container.show()
            self.tabs.hide()
            return
        else:
            self.empty_container.hide()
            self.tabs.show()

        # Tabs sin dependencia del filtro
        self.overview_tab.refresh()
        self.risk_profile_tab.refresh()
        self.controls_tab.refresh()

        # Priority Risks recibe el filtro
        self.priority_risks_tab.refresh(self._risk_level_filter)
