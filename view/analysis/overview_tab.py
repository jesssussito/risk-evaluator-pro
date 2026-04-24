from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLabel
)
from PySide6.QtCore import Qt
from models.companyRisk import CompanyRisk
from view.qt_widgets import KpiCard, AlertCard


class OverviewTab(QWidget):
    """
    Executive Risk Overview (ERM / GRC).

    Objetivo:
    - Proporcionar una visión ejecutiva del estado de riesgo
    - Detectar incumplimientos de apetito
    - Evaluar eficacia global de controles

    NO contiene análisis detallado ni gráficos complejos.
    """

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        # ==================================================
        # LAYOUT PRINCIPAL
        # ==================================================
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(25)
        self.main_layout.setContentsMargins(24, 20, 24, 20)

        # ==================================================
        # CONTENEDOR EJECUTIVO DE KPIs
        # ==================================================
        self.kpi_layout = QHBoxLayout()
        self.kpi_layout.setSpacing(20)
        self.kpi_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.kpi_container = QFrame()
        self.kpi_container.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border-radius: 10px;
                padding: 24px;
            }
        """)
        self.kpi_container.setLayout(self.kpi_layout)

        # ==================================================
        # TEXTO DE RESUMEN EJECUTIVO (DEBAJO DE KPIs)
        # ==================================================
        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        self.summary_label.setStyleSheet("""
            QLabel {
                color: #ccc;
                font-size: 13px;
                padding: 10px 4px;
            }
        """)

        # ==================================================
        # ORDEN CORRECTO EN EL LAYOUT
        # ==================================================
        self.main_layout.addWidget(self.kpi_container)   # KPIs arriba
        self.main_layout.addWidget(self.summary_label)   # Texto debajo

        # ==================================================
        # ALERTAS
        # ==================================================
        self.alerts_layout = QVBoxLayout()
        self.alerts_layout.setSpacing(12)
        self.main_layout.addLayout(self.alerts_layout)

        # Aire visual inferior
        self.main_layout.addStretch()


    # ==================================================
    # REFRESH
    # ==================================================
    def refresh(self):
        """
        Refresca el resumen ejecutivo de riesgos.
        """

        assessment = self.controller.company_assessment
        kpis = assessment.get_kpis()
        unacceptable_count = len(assessment.get_unacceptable_risks())

        # --------------------------------------------------
        # LIMPIAR KPIs
        # --------------------------------------------------
        while self.kpi_layout.count():
            item = self.kpi_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        # --------------------------------------------------
        # KPIs (semántica ERM)
        # --------------------------------------------------
        self.kpi_layout.addWidget(
            KpiCard(
                title="Overall Residual Risk",
                value=f"{kpis['avg']:.2f}",
                subtitle="Average exposure",
                status=self._risk_level_status(kpis["avg"]),
            )
        )

        self.kpi_layout.addWidget(
            KpiCard(
                title="Risks Above Appetite",
                value=str(unacceptable_count),
                subtitle="HIGH or CRITICAL level",
                status="critical" if unacceptable_count > 0 else "normal",
            )
        )

        self.kpi_layout.addWidget(
            KpiCard(
                title="Critical Risks",
                value=str(kpis["critical_count"]),
                subtitle="Immediate attention",
                status="critical" if kpis["critical_count"] > 0 else "normal",
            )
        )

        self.kpi_layout.addWidget(
            KpiCard(
                title="Control Effectiveness",
                value=f"{kpis['reduction_pct']:.1f} %",
                subtitle="Average mitigation",
                status=self._effectiveness_status(kpis["reduction_pct"]),
            )
        )

        self.kpi_layout.addStretch()

        # --------------------------------------------------
        # LIMPIAR ALERTAS
        # --------------------------------------------------
        while self.alerts_layout.count():
            item = self.alerts_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        # --------------------------------------------------
        # ALERTAS ERM
        # --------------------------------------------------
        unacceptable = assessment.get_unacceptable_risks()
        poorly_mitigated = assessment.get_poorly_mitigated_risks()
        priority_risks = assessment.get_priority_risks()


        if unacceptable:
            cr = unacceptable[0]  # riesgo más grave fuera de apetito

            frame = QFrame()
            frame.setStyleSheet("""
                QFrame {
                    background-color: #1f1f1f;
                    border-left: 4px solid #c0392b;
                    border-radius: 6px;
                    padding: 14px;
                }
            """)

            main = QVBoxLayout(frame)
            main.setSpacing(8)

            # ==================================================
            # BARRA 1 — MENSAJE PRINCIPAL
            # ==================================================
            title = QLabel(f"⛔ Risk Appetite Breach: {cr.base_risk.name}")
            title.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    font-weight: bold;
                    color: #e74c3c;
                }
            """)
            main.addWidget(title)

            # ==================================================
            # BARRA 2 — METADATA
            # ==================================================
            level = CompanyRisk.risk_level(cr.calculate_residual_risk())
            meta = QLabel(
                f"Type: {cr.base_risk.risk_type.name} | "
                f"Residual Level: {level}"
            )
            meta.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #bbb;
                }
            """)
            main.addWidget(meta)

            # ==================================================
            # FILA 3 — MÉTRICAS (3 COLUMNAS)
            # ==================================================
            metrics = QHBoxLayout()
            metrics.setSpacing(12)

            def metric(title, value):
                box = QFrame()
                box.setStyleSheet("""
                    QFrame {
                        background-color: #2b2b2b;
                        border-radius: 4px;
                        padding: 8px;
                    }
                """)
                l = QVBoxLayout(box)
                l.setSpacing(2)

                t = QLabel(title)
                t.setStyleSheet("font-size:11px; color:#aaa;")

                v = QLabel(value)
                v.setStyleSheet("font-size:13px; font-weight:bold; color:#eee;")

                l.addWidget(t)
                l.addWidget(v)
                return box

            inh = cr.calculate_inherent_risk()
            res = cr.calculate_residual_risk()
            red = inh - res

            metrics.addWidget(metric("Inherent Risk", f"{inh:.1f}"))
            metrics.addWidget(metric("Residual Risk", f"{res:.1f}"))
            metrics.addWidget(metric("Risk Reduction", f"{red:.1f}"))

            main.addLayout(metrics)

            self.alerts_layout.addWidget(frame)
        if priority_risks:
            cr = priority_risks[0]  # riesgo prioritario principal

            frame = QFrame()
            frame.setStyleSheet("""
                QFrame {
                    background-color: #1f1f1f;
                    border-left: 4px solid #f1c40f;
                    border-radius: 6px;
                    padding: 14px;
                }
            """)

            main = QVBoxLayout(frame)
            main.setSpacing(8)

            # ==================================================
            # BARRA 1 — MENSAJE PRINCIPAL
            # ==================================================
            title = QLabel(f"⚠ Priority Risk: {cr.base_risk.name}")
            title.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    font-weight: bold;
                    color: #f1c40f;
                }
            """)
            main.addWidget(title)

            # ==================================================
            # BARRA 2 — METADATA
            # ==================================================
            level = CompanyRisk.risk_level(cr.calculate_residual_risk())
            meta = QLabel(
                f"Type: {cr.base_risk.risk_type.name} | "
                f"Residual Level: {level}"
            )
            meta.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #bbb;
                }
            """)
            main.addWidget(meta)

            # ==================================================
            # FILA 3 — MÉTRICAS (3 COLUMNAS)
            # ==================================================
            metrics = QHBoxLayout()
            metrics.setSpacing(12)

            def metric(title, value):
                box = QFrame()
                box.setStyleSheet("""
                    QFrame {
                        background-color: #2b2b2b;
                        border-radius: 4px;
                        padding: 8px;
                    }
                """)
                l = QVBoxLayout(box)
                l.setSpacing(2)

                t = QLabel(title)
                t.setStyleSheet("font-size:11px; color:#aaa;")

                v = QLabel(value)
                v.setStyleSheet("font-size:13px; font-weight:bold; color:#eee;")

                l.addWidget(t)
                l.addWidget(v)
                return box

            inh = cr.calculate_inherent_risk()
            res = cr.calculate_residual_risk()
            red = inh - res

            metrics.addWidget(metric("Inherent Risk", f"{inh:.1f}"))
            metrics.addWidget(metric("Residual Risk", f"{res:.1f}"))
            metrics.addWidget(metric("Risk Reduction", f"{red:.1f}"))

            main.addLayout(metrics)

            # ==================================================
            # INDICADOR DE CONTEXTO
            # ==================================================
            if len(priority_risks) > 1:
                more = QLabel(f"+ {len(priority_risks) - 1} additional priority risks")
                more.setStyleSheet("font-size:11px; color:#999;")
                main.addWidget(more)

            self.alerts_layout.addWidget(frame)

        if poorly_mitigated:
            cr = poorly_mitigated[0]  # mostramos el riesgo más crítico

            frame = QFrame()
            frame.setStyleSheet("""
                QFrame {
                    background-color: #1f1f1f;
                    border-left: 4px solid #e67e22;
                    border-radius: 6px;
                    padding: 14px;
                }
            """)

            main = QVBoxLayout(frame)
            main.setSpacing(8)

            # ==================================================
            # BARRA 1 — MENSAJE PRINCIPAL
            # ==================================================
            title = QLabel(f"⚠ Poorly Mitigated Risk: {cr.base_risk.name}")
            title.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    font-weight: bold;
                    color: #f1c40f;
                }
            """)
            main.addWidget(title)

            # ==================================================
            # BARRA 2 — METADATA
            # ==================================================
            level = CompanyRisk.risk_level(cr.calculate_residual_risk())
            meta = QLabel(
                f"Type: {cr.base_risk.risk_type.name} | "
                f"Residual Level: {level}"
            )
            meta.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #bbb;
                }
            """)
            main.addWidget(meta)

            # ==================================================
            # FILA 3 — MÉTRICAS (3 COLUMNAS)
            # ==================================================
            metrics = QHBoxLayout()
            metrics.setSpacing(12)

            def metric(title, value):
                box = QFrame()
                box.setStyleSheet("""
                    QFrame {
                        background-color: #2b2b2b;
                        border-radius: 4px;
                        padding: 8px;
                    }
                """)
                l = QVBoxLayout(box)
                l.setSpacing(2)

                t = QLabel(title)
                t.setStyleSheet("font-size:11px; color:#aaa;")

                v = QLabel(value)
                v.setStyleSheet("font-size:13px; font-weight:bold; color:#eee;")

                l.addWidget(t)
                l.addWidget(v)
                return box

            inh = cr.calculate_inherent_risk()
            res = cr.calculate_residual_risk()
            red = inh - res

            metrics.addWidget(metric("Inherent Risk", f"{inh:.1f}"))
            metrics.addWidget(metric("Residual Risk", f"{res:.1f}"))
            metrics.addWidget(metric("Risk Reduction", f"{red:.1f}"))

            main.addLayout(metrics)

            self.alerts_layout.addWidget(frame)

        self.summary_label.setText(
            self._build_executive_summary(kpis)
        )


    # ==================================================
    # HELPERS DE SEMÁNTICA DE RIESGO
    # ==================================================
    def _risk_level_status(self, avg_risk: float) -> str:
        if avg_risk >= 0.7:
            return "critical"
        elif avg_risk >= 0.4:
            return "warning"
        return "normal"

    def _effectiveness_status(self, reduction_pct: float) -> str:
        if reduction_pct < 30:
            return "critical"
        elif reduction_pct < 60:
            return "warning"
        return "normal"
    
    def _build_executive_summary(self, kpis: dict) -> str:
        if kpis["critical_count"] > 0:
            return (
                "The organization exceeds its defined risk appetite. "
                "Immediate mitigation actions are required for critical risks."
            )

        if kpis["reduction_pct"] < 30:
            return (
                "Overall risk exposure remains within acceptable levels. "
                "However, control effectiveness is low, indicating limited mitigation impact."
            )

        return (
            "The organization operates within acceptable risk levels. "
            "No critical risks exceed the defined risk appetite."
        )

