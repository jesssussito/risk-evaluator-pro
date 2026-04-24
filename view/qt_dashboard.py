from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QFrame,
)
from PySide6.QtCore import Qt

from view.qt_charts import InherentVsResidualChart, RiskMatrixChart, RiskLevelDonutChart
from view.qt_widgets import RiskCard, KpiCard, AlertCard


# ── Helpers de layout ─────────────────────────────────────────────────────────

def _section_header(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(
        "font-size: 11px; font-weight: 600; color: #aaff00;"
        "letter-spacing: 1px; background: transparent;"
    )
    return lbl


def _separator() -> QFrame:
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setStyleSheet("color: #1e1e1e; margin: 2px 0;")
    return line


def _card_section() -> tuple:
    """Devuelve (widget contenedor, layout interno) con estilo de tarjeta."""
    w = QWidget()
    w.setStyleSheet("QWidget { background-color: #141414; border-radius: 10px; }")
    layout = QVBoxLayout(w)
    layout.setSpacing(10)
    layout.setContentsMargins(18, 14, 18, 16)
    return w, layout


# ── Vista principal ───────────────────────────────────────────────────────────

class DashboardView(QWidget):
    """
    Vista principal del dashboard de análisis de riesgos.

    Responsabilidades:
    - Mostrar métricas ejecutivas (KPIs)
    - Mostrar alertas y ranking de riesgos
    - Contener gráficas de análisis

    IMPORTANTE:
    - Esta vista NO calcula riesgos
    - Solo consume datos del modelo (CompanyAssessment)
    """

    def __init__(self, controller):
        super().__init__()

        self.controller = controller
        self.filter_top_n = 5
        self.filter_type = None

        # ── Scroll principal ──────────────────────────────────────────────────
        # Todo el contenido vive dentro de un QScrollArea para evitar
        # que los elementos se solapen al redimensionar la ventana.
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        main_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        root_layout.addWidget(main_scroll)

        content_widget = QWidget()
        self.main_layout = QVBoxLayout(content_widget)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(24, 20, 24, 24)
        main_scroll.setWidget(content_widget)

        # ── Cabecera ──────────────────────────────────────────────────────────
        title = QLabel("Risk Dashboard")
        title.setStyleSheet(
            "font-size: 22px; font-weight: 700; color: #ffffff;"
            "background: transparent;"
        )
        self.main_layout.addWidget(title)

        subtitle = QLabel("Visual summary of the company's residual risk")
        subtitle.setStyleSheet(
            "color: #555555; font-size: 13px; background: transparent;"
        )
        self.main_layout.addWidget(subtitle)
        self.main_layout.addSpacing(6)

        # ── Estado vacío ──────────────────────────────────────────────────────
        self.empty_container = QWidget()
        empty_layout = QVBoxLayout(self.empty_container)
        empty_layout.setAlignment(Qt.AlignCenter)
        empty_layout.setSpacing(12)

        empty_title = QLabel("Analysis unavailable")
        empty_title.setAlignment(Qt.AlignCenter)
        empty_title.setStyleSheet(
            "font-size: 18px; font-weight: 700; color: #ffffff;"
            "background: transparent;"
        )

        empty_text = QLabel(
            "To view the risk analysis, complete\n"
            "the previous steps:\n\n"
            "• Risk selection\n"
            "• Criticality editing\n"
            "• Control selection"
        )
        empty_text.setAlignment(Qt.AlignCenter)
        empty_text.setStyleSheet("color: #555555; background: transparent;")

        empty_layout.addWidget(empty_title)
        empty_layout.addWidget(empty_text)
        self.main_layout.addWidget(self.empty_container)

        # ══════════════════════════════════════════════════════════════════════
        # SECCIÓN 1 · KPIs PRINCIPALES
        # ══════════════════════════════════════════════════════════════════════
        self.kpi_section, kpi_inner = _card_section()

        kpi_inner.addWidget(_section_header("KEY INDICATORS"))
        kpi_inner.addWidget(_separator())

        self.kpi_layout = QHBoxLayout()
        self.kpi_layout.setSpacing(16)
        self.kpi_layout.setAlignment(Qt.AlignLeft)
        kpi_inner.addLayout(self.kpi_layout)

        self.main_layout.addWidget(self.kpi_section)

        # ══════════════════════════════════════════════════════════════════════
        # SECCIÓN 2 · ALERTAS
        # Se oculta completamente si no hay alertas activas.
        # ══════════════════════════════════════════════════════════════════════
        self.alerts_section, alerts_inner = _card_section()

        alerts_inner.addWidget(_section_header("ALERTS"))
        alerts_inner.addWidget(_separator())

        self.alerts_layout = QVBoxLayout()
        self.alerts_layout.setSpacing(8)
        alerts_inner.addLayout(self.alerts_layout)

        self.main_layout.addWidget(self.alerts_section)

        # ══════════════════════════════════════════════════════════════════════
        # SECCIÓN 3 · GRÁFICOS
        # Fila superior: barras (60 %) + donut (40 %)
        # Fila inferior: matriz de riesgo (ancho completo)
        # ══════════════════════════════════════════════════════════════════════
        self.charts_section, charts_inner = _card_section()

        charts_inner.addWidget(_section_header("VISUAL ANALYSIS"))
        charts_inner.addWidget(_separator())

        charts_top = QHBoxLayout()
        charts_top.setSpacing(14)

        self.chart = InherentVsResidualChart(self.controller)
        self.chart.setMinimumHeight(280)
        charts_top.addWidget(self.chart, 3)

        self.donut_chart = RiskLevelDonutChart(self.controller)
        self.donut_chart.setMinimumHeight(280)
        charts_top.addWidget(self.donut_chart, 2)

        charts_inner.addLayout(charts_top)
        charts_inner.addWidget(_separator())

        self.risk_matrix = RiskMatrixChart(self.controller)
        self.risk_matrix.setMinimumHeight(280)
        charts_inner.addWidget(self.risk_matrix)

        self.main_layout.addWidget(self.charts_section)

        # ══════════════════════════════════════════════════════════════════════
        # SECCIÓN 4 · RANKING DE RIESGOS
        # ══════════════════════════════════════════════════════════════════════
        self.ranking_section, ranking_inner = _card_section()

        ranking_inner.addWidget(_section_header("RISK RANKING · RESIDUAL RISK"))
        ranking_inner.addWidget(_separator())

        self.ranking_layout = QVBoxLayout()
        self.ranking_layout.setSpacing(10)
        ranking_inner.addLayout(self.ranking_layout)

        self.main_layout.addWidget(self.ranking_section)

        # Primera carga
        self.refresh()

    # ── Lógica de filtrado (sin cambios) ─────────────────────────────────────

    def _get_filtered_ranking(self):
        ranking = self.controller.company_assessment.get_risk_ranking(residual=True)

        if self.filter_type:
            ranking = [
                cr for cr in ranking
                if cr.base_risk.risk_type.name == self.filter_type
            ]

        return ranking[:self.filter_top_n]

    # ── Refresh ───────────────────────────────────────────────────────────────

    def refresh(self):
        """
        Refresca completamente el dashboard.
        Se llama cada vez que el usuario entra en 'Análisis'.
        """

        active = self.controller.company_assessment.get_active_risks()

        if not active:
            self.empty_container.show()
            self.kpi_section.hide()
            self.alerts_section.hide()
            self.charts_section.hide()
            self.ranking_section.hide()
            return

        self.empty_container.hide()
        self.kpi_section.show()
        self.charts_section.show()
        self.ranking_section.show()

        # ── Alertas ───────────────────────────────────────────────────────────
        while self.alerts_layout.count():
            item = self.alerts_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)

        unacceptable = self.controller.company_assessment.get_unacceptable_risks()
        poor_controls = self.controller.company_assessment.get_poorly_mitigated_risks()

        if unacceptable:
            self.alerts_layout.addWidget(AlertCard(
                "Unacceptable risks detected",
                f"There are {len(unacceptable)} risks at HIGH or CRITICAL level.",
                "critical",
            ))

        if poor_controls:
            self.alerts_layout.addWidget(AlertCard(
                "Insufficient controls",
                f"{len(poor_controls)} risks remain at high levels despite having controls.",
                "warning",
            ))

        self.alerts_section.setVisible(bool(unacceptable or poor_controls))

        # ── KPIs ──────────────────────────────────────────────────────────────
        while self.kpi_layout.count():
            item = self.kpi_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)

        kpis = self.controller.company_assessment.get_kpis()

        self.kpi_layout.addWidget(KpiCard(
            "Maximum Residual Risk",
            f"{kpis['max']:.2f}",
            "Worst active risk",
            "critical",
        ))
        self.kpi_layout.addWidget(KpiCard(
            "Average Residual Risk",
            f"{kpis['avg']:.2f}",
            "Average exposure",
            "warning",
        ))
        self.kpi_layout.addWidget(KpiCard(
            "Critical Risks",
            str(kpis["critical_count"]),
            "CRITICAL level",
            "critical",
        ))
        self.kpi_layout.addWidget(KpiCard(
            "Average Reduction",
            f"{kpis['reduction_pct']:.1f} %",
            "Control effectiveness",
            "normal",
        ))
        self.kpi_layout.addStretch()

        # ── Gráficos ──────────────────────────────────────────────────────────
        self.chart.refresh()
        self.donut_chart.refresh()
        self.risk_matrix.refresh()

        # ── Ranking ───────────────────────────────────────────────────────────
        while self.ranking_layout.count():
            item = self.ranking_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)

        for cr in self._get_filtered_ranking():
            self.ranking_layout.addWidget(RiskCard(cr))
