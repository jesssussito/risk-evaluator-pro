from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QPushButton,
    QFrame,
    QScrollArea,
)

from models.companyRisk import CompanyRisk
from view.qt_widgets import RiskCard


class PriorityRisksTab(QWidget):
    """
    Priority Risks View.

    Objetivo:
    - Mostrar el ranking de riesgos residuales
    - Permitir filtrado por nivel (desde el donut)
    - Facilitar identificación de riesgos prioritarios
    """

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self._current_filter = None

        # ==================================================
        # LAYOUT PRINCIPAL
        # ==================================================
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(15)
        self.main_layout.setContentsMargins(24, 20, 24, 20)

        title = QLabel("Priority Risks")
        title.setStyleSheet("font-size:16px; font-weight:bold;")
        self.main_layout.addWidget(title)

        subtitle = QLabel(
            "Ranked list of risks based on residual exposure. "
            "Use filters to focus on specific risk levels."
        )
        subtitle.setStyleSheet("color:#666;")
        self.main_layout.addWidget(subtitle)

        # ==================================================
        # BARRA DE FILTRO ACTIVO
        # ==================================================
        self.filter_bar = QFrame()
        self.filter_bar.setStyleSheet("""
            QFrame {
                background-color: #1f1f1f;
                border-radius: 6px;
                padding: 8px 10px;
            }
        """)
        self.filter_bar.hide()

        filter_layout = QHBoxLayout(self.filter_bar)
        filter_layout.setSpacing(10)

        self.filter_label = QLabel("")
        self.filter_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: #f1c40f;
            }
        """)
        filter_layout.addWidget(self.filter_label)

        self.clear_filter_btn = QPushButton("Clear filter")
        self.clear_filter_btn.setFixedHeight(24)
        self.clear_filter_btn.clicked.connect(self._clear_filter)
        filter_layout.addWidget(self.clear_filter_btn)

        filter_layout.addStretch()

        self.main_layout.addWidget(self.filter_bar)

        # ==================================================
        # CONTENEDOR DEL RANKING (SCROLL)
        # ==================================================
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.ranking_container = QWidget()
        self.ranking_layout = QVBoxLayout(self.ranking_container)
        self.ranking_layout.setSpacing(12)

        self.scroll.setWidget(self.ranking_container)
        self.main_layout.addWidget(self.scroll)

        self.main_layout.addStretch()

    # ==================================================
    # REFRESH
    # ==================================================
    def refresh(self, risk_level_filter: str | None = None):
        """
        Refresca el ranking de riesgos prioritarios.
        Puede recibir un filtro de nivel desde el donut.
        """

        self._current_filter = risk_level_filter

        # --------------------------------------------------
        # BARRA DE FILTRO
        # --------------------------------------------------
        if risk_level_filter:
            self.filter_label.setText(f"Filtered by level: {risk_level_filter}")
            self.filter_bar.show()
        else:
            self.filter_bar.hide()

        # --------------------------------------------------
        # LIMPIAR RANKING
        # --------------------------------------------------
        while self.ranking_layout.count():
            item = self.ranking_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        # --------------------------------------------------
        # OBTENER RANKING BASE
        # --------------------------------------------------
        ranking = self.controller.company_assessment.get_risk_ranking(residual=True)

        # --------------------------------------------------
        # APLICAR FILTRO (SI EXISTE)
        # --------------------------------------------------
        if risk_level_filter:
            ranking = [
                cr for cr in ranking
                if CompanyRisk.risk_level(cr.calculate_residual_risk()) == risk_level_filter
            ]

        # --------------------------------------------------
        # CASO SIN RESULTADOS
        # --------------------------------------------------
        if not ranking:
            empty = QLabel("No risks match the selected criteria.")
            empty.setStyleSheet("color:#999; font-style:italic;")
            self.ranking_layout.addWidget(empty)
            self.ranking_layout.addStretch()
            return

        # --------------------------------------------------
        # MOSTRAR RANKING
        # --------------------------------------------------
        for cr in ranking:
            self.ranking_layout.addWidget(RiskCard(cr))

        self.ranking_layout.addStretch()

    # ==================================================
    # CLEAR FILTER
    # ==================================================
    def _clear_filter(self):
        """
        Limpia el filtro activo solicitándolo al AnalysisView.
        """
        parent = self.parent()
        if parent and hasattr(parent, "set_risk_level_filter"):
            parent.set_risk_level_filter(None)
