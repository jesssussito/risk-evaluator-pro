from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QScrollArea
)
from PySide6.QtCore import Qt

from view.qt_charts import RiskMatrixChart, RiskLevelDonutChart
from models.companyRisk import CompanyRisk


class RiskProfileTab(QWidget):
    """
    Risk Profile View (ERM).

    Objetivo:
    - Visualizar la exposición al riesgo
    - Identificar concentraciones de riesgo
    - Analizar riesgos fuera del apetito

    Esta vista se centra en el *dónde* del riesgo.
    """

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        # ==================================================
        # SCROLL GLOBAL (ANTI-DESPLAZAMIENTOS)
        # ==================================================
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)

        self.container = QWidget()
        self.scroll.setWidget(self.container)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(self.scroll)

        # ==================================================
        # LAYOUT PRINCIPAL
        # ==================================================
        self.main_layout = QVBoxLayout(self.container)
        self.main_layout.setSpacing(25)
        self.main_layout.setContentsMargins(24, 20, 24, 20)

        # ==================================================
        # TEXTO CONTEXTUAL
        # ==================================================
        self.context_label = QLabel(
            "The risk heatmap illustrates the distribution of risks based on their "
            "inherent impact and likelihood, highlighting areas of higher exposure."
        )
        self.context_label.setWordWrap(True)
        self.context_label.setStyleSheet("""
            QLabel {
                color: #ccc;
                font-size: 13px;
                padding: 6px 2px;
            }
        """)
        self.main_layout.addWidget(self.context_label)

        # ==================================================
        # CONTENEDOR MATRIZ + PANEL LATERAL
        # ==================================================
        self.matrix_container = QFrame()
        self.matrix_container.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border-radius: 10px;
                padding: 20px;
            }
        """)

        matrix_container_layout = QVBoxLayout(self.matrix_container)
        matrix_container_layout.setSpacing(15)

        # Layout horizontal: matriz + detalle
        matrix_and_detail_layout = QHBoxLayout()
        matrix_and_detail_layout.setSpacing(20)

        # ------------------------------
        # MATRIZ DE RIESGO
        # ------------------------------
        self.risk_matrix = RiskMatrixChart(self.controller)
        matrix_and_detail_layout.addWidget(self.risk_matrix, 3)

        # ------------------------------
        # PANEL LATERAL DE DETALLE
        # ------------------------------
        self.detail_panel = QFrame()
        self.detail_panel.setMinimumWidth(260)
        self.detail_panel.setStyleSheet("""
            QFrame {
                background-color: #1f1f1f;
                border-radius: 8px;
                padding: 12px;
            }
        """)

        detail_layout = QVBoxLayout(self.detail_panel)
        detail_layout.setSpacing(10)

        self.detail_title = QLabel("Risk details")
        self.detail_title.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
            }
        """)
        detail_layout.addWidget(self.detail_title)

        self.detail_body = QLabel("Click on a risk in the matrix to view details.")
        self.detail_body.setWordWrap(True)
        self.detail_body.setStyleSheet("color: #ccc;")
        detail_layout.addWidget(self.detail_body)

        detail_layout.addStretch()

        matrix_and_detail_layout.addWidget(self.detail_panel, 1)

        matrix_container_layout.addLayout(matrix_and_detail_layout)
        self.main_layout.addWidget(self.matrix_container)

        # ==================================================
        # DISTRIBUCIÓN DE RIESGOS (DONUT)
        # ==================================================
        self.distribution_container = QFrame()
        self.distribution_container.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border-radius: 10px;
                padding: 20px;
            }
        """)

        self.distribution_layout = QVBoxLayout(self.distribution_container)
        self.distribution_layout.setSpacing(15)

        dist_label = QLabel("Risk Distribution by Level")
        dist_label.setStyleSheet("font-size:14px; font-weight:bold;")

        self.donut_chart = RiskLevelDonutChart(self.controller)

        self.distribution_layout.addWidget(dist_label)
        self.distribution_layout.addWidget(self.donut_chart)

        self.main_layout.addWidget(self.distribution_container)

        self.main_layout.addStretch()

        # ==================================================
        # CONEXIÓN CLICK MATRIZ → PANEL
        # ==================================================
        self.risk_matrix.riskClicked.connect(self._show_risk_detail)

    # ==================================================
    # REFRESH
    # ==================================================
    def refresh(self):
        """
        Refresca la vista de perfil de riesgo.
        """
        self.risk_matrix.refresh()
        self.donut_chart.refresh()

    # ==================================================
    # PANEL DE DETALLE
    # ==================================================
    def _show_risk_detail(self, cr):
        """
        Muestra información del riesgo seleccionado en el panel lateral.
        """

        residual = cr.calculate_residual_risk()
        level = CompanyRisk.risk_level(residual)

        text = (
            f"<b>Name:</b> {cr.base_risk.name}<br><br>"
            f"<b>Residual risk:</b> {residual:.2f}<br>"
            f"<b>Level:</b> {level}<br><br>"
            f"<b>Probability:</b> {cr.custom_probability}<br>"
            f"<b>Impact (Financial):</b> {cr.custom_impact_financial}<br>"
            f"<b>Impact (Operational):</b> {cr.custom_impact_operational}<br>"
            f"<b>Impact (Reputational):</b> {cr.custom_impact_reputational}"
        )

        self.detail_body.setText(text)
