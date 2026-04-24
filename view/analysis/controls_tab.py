from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QScrollArea,
)
from PySide6.QtCore import Qt

from view.qt_widgets import KpiCard, RiskCard

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class ControlsTab(QWidget):
    """
    Controls & Mitigation (ERM / GRC)
    UI estable con scroll único.
    """

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        # ==================================================
        # ROOT LAYOUT (NO CONTIENE CONTENIDO DIRECTO)
        # ==================================================
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ==================================================
        # SCROLL ÚNICO PARA TODA LA PESTAÑA (CLAVE)
        # ==================================================
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        root_layout.addWidget(self.scroll)

        self.content = QWidget()
        self.scroll.setWidget(self.content)

        self.main_layout = QVBoxLayout(self.content)
        self.main_layout.setSpacing(16)
        self.main_layout.setContentsMargins(24, 20, 24, 20)

        # ==================================================
        # TÍTULO
        # ==================================================
        title = QLabel("Controls & Mitigation")
        title.setStyleSheet("font-size:16px; font-weight:bold;")
        self.main_layout.addWidget(title)

        subtitle = QLabel(
            "Assessment of control effectiveness, mitigation gaps and residual exposure."
        )
        subtitle.setStyleSheet("color:#777; font-size:12px;")
        self.main_layout.addWidget(subtitle)

        # ==================================================
        # EXECUTIVE INSIGHT
        # ==================================================
        self.insight_box = QFrame()
        self.insight_box.setStyleSheet("""
            QFrame {
                background-color: #1f1f1f;
                border-left: 4px solid #3498db;
                border-radius: 6px;
                padding: 12px;
            }
        """)
        insight_layout = QVBoxLayout(self.insight_box)

        self.insight_label = QLabel("")
        self.insight_label.setWordWrap(True)
        self.insight_label.setStyleSheet("color:#ddd; font-size:13px;")
        insight_layout.addWidget(self.insight_label)

        self.main_layout.addWidget(self.insight_box)

        # ==================================================
        # KPIs
        # ==================================================
        self.kpi_layout = QHBoxLayout()
        self.kpi_layout.setSpacing(14)
        self.main_layout.addLayout(self.kpi_layout)

        # ==================================================
        # GRÁFICO: INHERENT VS RESIDUAL (ALTURA FIJA)
        # ==================================================
        chart_container = QFrame()
        chart_container.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border-radius: 8px;
                padding: 14px;
            }
        """)
        chart_layout = QVBoxLayout(chart_container)

        chart_title = QLabel("Inherent vs Residual Risk")
        chart_title.setStyleSheet("font-size:14px; font-weight:bold;")
        chart_layout.addWidget(chart_title)

        self.figure = Figure(figsize=(6, 3))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(260)
        self.canvas.setMaximumHeight(300)
        chart_layout.addWidget(self.canvas)

        self.main_layout.addWidget(chart_container)

        # ==================================================
        # POORLY MITIGATED RISKS (ALTURA CONTROLADA)
        # ==================================================
        self.poor_container = QFrame()
        self.poor_container.setStyleSheet("""
            QFrame {
                background-color: #262626;
                border-left: 4px solid #e74c3c;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        poor_layout = QVBoxLayout(self.poor_container)

        poor_title = QLabel("Poorly Mitigated Risks")
        poor_title.setStyleSheet("font-size:14px; font-weight:bold;")
        poor_layout.addWidget(poor_title)

        poor_desc = QLabel(
            "Risks that remain HIGH or CRITICAL despite having controls applied."
        )
        poor_desc.setStyleSheet("color:#999; font-size:12px;")
        poor_layout.addWidget(poor_desc)

        self.poor_scroll = QScrollArea()
        self.poor_scroll.setWidgetResizable(True)
        self.poor_scroll.setMaximumHeight(240)

        self.poor_list_container = QWidget()
        self.poor_list_layout = QVBoxLayout(self.poor_list_container)
        self.poor_list_layout.setSpacing(12)

        self.poor_scroll.setWidget(self.poor_list_container)
        poor_layout.addWidget(self.poor_scroll)

        self.main_layout.addWidget(self.poor_container)

        self.main_layout.addStretch()

    # ==================================================
    # REFRESH
    # ==================================================
    def refresh(self):
        assessment = self.controller.company_assessment
        risks = assessment.get_active_risks()

        # LIMPIAR KPIs
        while self.kpi_layout.count():
            item = self.kpi_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        if not risks:
            self.insight_label.setText(
                "No active risks detected. Control assessment not applicable."
            )
            return

        avg_coverage = sum(cr.get_control_coverage() for cr in risks) / len(risks)
        avg_reduction = sum(cr.get_risk_reduction_percent() for cr in risks) / len(risks)
        poorly_mitigated = assessment.get_poorly_mitigated_risks()

        # INSIGHT
        if avg_coverage < 20:
            text = (
                "Control coverage is low, indicating a weak mitigation posture. "
                "Priority should be given to implementing key controls."
            )
            insight_color = "#e67e22"
        elif poorly_mitigated:
            text = (
                "Some risks remain at high residual levels despite controls, "
                "indicating mitigation gaps."
            )
            insight_color = "#e74c3c"
        else:
            text = (
                "Control effectiveness is acceptable and residual risks "
                "are within tolerance."
            )
            insight_color = "#2ecc71"

        self.insight_box.setStyleSheet(f"""
            QFrame {{
                background-color: #1f1f1f;
                border-left: 4px solid {insight_color};
                border-radius: 6px;
                padding: 12px;
            }}
        """)
        self.insight_label.setText(text)

        # Statuses semánticos por KPI (independientes del insight global)
        if avg_coverage < 20:
            coverage_status = "critical"
        elif avg_coverage < 50:
            coverage_status = "warning"
        else:
            coverage_status = "normal"

        if avg_reduction < 20:
            reduction_status = "critical"
        elif avg_reduction < 40:
            reduction_status = "warning"
        else:
            reduction_status = "normal"

        poorly_status = "critical" if poorly_mitigated else "normal"

        # KPIs
        self.kpi_layout.addWidget(
            KpiCard("Average Control Coverage", f"{avg_coverage:.1f} %", "Applied controls", coverage_status)
        )
        self.kpi_layout.addWidget(
            KpiCard("Average Risk Reduction", f"{avg_reduction:.1f} %", "Mitigation effectiveness", reduction_status)
        )
        self.kpi_layout.addWidget(
            KpiCard("Poorly Mitigated Risks", str(len(poorly_mitigated)), "High residual risk", poorly_status)
        )

        # GRÁFICO
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        names = [cr.base_risk.name for cr in risks]
        inh = [cr.calculate_inherent_risk() for cr in risks]
        res = [cr.calculate_residual_risk() for cr in risks]

        x = range(len(risks))
        ax.bar(x, inh, color="#bdc3c7", label="Inherent")
        ax.bar(x, res, color="#3498db", label="Residual")

        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=20, ha="right", fontsize=9)
        ax.set_ylabel("Risk score")
        ax.legend(frameon=False)
        ax.grid(axis="y", linestyle="--", alpha=0.2)

        self.figure.subplots_adjust(bottom=0.30)
        self.canvas.draw_idle()

        # LISTA
        while self.poor_list_layout.count():
            item = self.poor_list_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        if not poorly_mitigated:
            empty = QLabel("All risks are adequately mitigated.")
            empty.setStyleSheet("color:#bbb; font-style:italic; padding: 8px;")
            self.poor_list_layout.addWidget(empty)
            return

        for cr in poorly_mitigated:
            self.poor_list_layout.addWidget(RiskCard(cr))
