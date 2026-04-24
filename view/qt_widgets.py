from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QFrame,
    QSizePolicy
)
from PySide6.QtCore import Qt


class RiskCard(QWidget):
    """
    Card visual para representar un riesgo individual.
    """

    # Colores semánticos de nivel — dominio ERM, no decoración
    _LEVEL_COLORS = {
        "BAJO":     "#22c55e",
        "MEDIO":    "#eab308",
        "ALTO":     "#f97316",
        "CRÍTICO":  "#ef4444",
    }

    _LEVEL_EN = {
        "BAJO":    "LOW",
        "MEDIO":   "MEDIUM",
        "ALTO":    "HIGH",
        "CRÍTICO": "CRITICAL",
    }

    def __init__(self, company_risk):
        super().__init__()

        self.company_risk = company_risk

        value          = company_risk.calculate_residual_risk()
        level          = company_risk.risk_level(value)
        controls_count = len(company_risk.enabled_controls)

        level_color = self._LEVEL_COLORS.get(level, "#555555")

        self.setStyleSheet(f"""
            QWidget {{
                background-color: #141414;
                border: 1px solid #1e1e1e;
                border-left: 3px solid {level_color};
                border-radius: 8px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(12, 10, 12, 10)

        # ── Nombre ──────────────────────────────────────────────────────────
        name = QLabel(company_risk.base_risk.name)
        name.setStyleSheet(
            "font-size: 14px; font-weight: 700; color: #ffffff;"
            "border: none; background: transparent;"
        )
        layout.addWidget(name)

        # ── Tipo ─────────────────────────────────────────────────────────────
        risk_type = QLabel(f"Type: {company_risk.base_risk.risk_type.name}")
        risk_type.setStyleSheet(
            "color: #666666; font-size: 12px; border: none; background: transparent;"
        )
        layout.addWidget(risk_type)

        # ── Métricas ──────────────────────────────────────────────────────────
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(16)

        value_lbl    = QLabel(f"Residual: {value:.2f}")
        level_lbl    = QLabel(f"Level: {self._LEVEL_EN.get(level, level)}")
        controls_lbl = QLabel(f"Controls: {controls_count}")

        _base = "font-size: 12px; border: none; background: transparent;"
        value_lbl.setStyleSheet(f"color: #ffffff; {_base}")
        level_lbl.setStyleSheet(f"color: {level_color}; font-weight: 600; {_base}")
        controls_lbl.setStyleSheet(f"color: #888888; {_base}")

        for lbl in (value_lbl, level_lbl, controls_lbl):
            lbl.setAlignment(Qt.AlignLeft)
            metrics_layout.addWidget(lbl)

        layout.addLayout(metrics_layout)


class KpiCard(QWidget):
    """
    KPI Card profesional (ERM / GRC).
    """

    # Normal usa lima — es un KPI clave. Warning/critical mantienen semántica.
    STATUS_COLORS = {
        "normal":   "#aaff00",
        "warning":  "#f59e0b",
        "critical": "#ef4444",
    }

    def __init__(self, title: str, value: str, subtitle: str, status: str = "normal"):
        super().__init__()

        color = self.STATUS_COLORS.get(status, self.STATUS_COLORS["normal"])

        self.setMinimumWidth(220)
        self.setMaximumWidth(260)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        self.setStyleSheet(f"""
            QWidget {{
                background-color: #141414;
                border-radius: 8px;
                border-left: 4px solid {color};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(14, 12, 14, 12)

        # ── Título del KPI (etiqueta descriptiva)
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            "font-size: 11px; color: #888888; font-weight: 500;"
            "background: transparent; border: none;"
        )

        # ── Valor numérico — blanco para máxima legibilidad
        value_lbl = QLabel(value)
        value_lbl.setAlignment(Qt.AlignLeft)
        value_lbl.setStyleSheet(
            "font-size: 30px; font-weight: 700; color: #ffffff;"
            "background: transparent; border: none;"
        )

        # ── Subtítulo / contexto
        subtitle_lbl = QLabel(subtitle)
        subtitle_lbl.setStyleSheet(
            "font-size: 11px; color: #555555;"
            "background: transparent; border: none;"
        )

        layout.addWidget(title_lbl)
        layout.addWidget(value_lbl)
        layout.addWidget(subtitle_lbl)


class AlertCard(QWidget):
    """
    Alerta ERM con niveles semánticos.
    """

    LEVEL_STYLES = {
        "warning":  "#f59e0b",
        "critical": "#ef4444",
    }

    def __init__(self, title: str, text: str, level: str = "warning"):
        super().__init__()

        color = self.LEVEL_STYLES.get(level, "#f59e0b")

        self.setStyleSheet(f"""
            QWidget {{
                background-color: #141414;
                border-left: 3px solid {color};
                border-radius: 6px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(12, 10, 12, 10)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            "font-weight: 700; color: #ffffff; font-size: 13px;"
            "background: transparent; border: none;"
        )

        text_lbl = QLabel(text)
        text_lbl.setWordWrap(True)
        text_lbl.setStyleSheet(
            "color: #888888; font-size: 12px;"
            "background: transparent; border: none;"
        )

        layout.addWidget(title_lbl)
        layout.addWidget(text_lbl)
