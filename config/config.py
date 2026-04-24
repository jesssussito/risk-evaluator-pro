"""Application-wide constants, colour palette, NIST taxonomy and QSS stylesheet."""

from typing import Dict, List, Tuple

# ---------------------------------------------------------------------------
# Application metadata
# ---------------------------------------------------------------------------
APP_NAME = "Risk Evaluator Pro"
APP_VERSION = "2.0.0"
APP_DESCRIPTION = "Sistema Profesional de Evaluación Cuantitativa de Riesgos · NIST CSF v1.1"

# ---------------------------------------------------------------------------
# Scoring scales
# ---------------------------------------------------------------------------
PROBABILITY_SCALE: Dict[int, str] = {
    1: "Muy Improbable",
    2: "Improbable",
    3: "Posible",
    4: "Probable",
    5: "Casi Seguro",
}

IMPACT_SCALE: Dict[int, str] = {
    1: "Insignificante",
    2: "Menor",
    3: "Moderado",
    4: "Mayor",
    5: "Catastrófico",
}

# ---------------------------------------------------------------------------
# Risk level classification  (residual_risk thresholds)
# ---------------------------------------------------------------------------
RISK_LEVELS_ORDER: List[str] = ["Muy Bajo", "Bajo", "Medio", "Alto", "Crítico"]

RISK_LEVEL_COLORS: Dict[str, str] = {
    "Muy Bajo": "#2ECC71",
    "Bajo":     "#A8D44A",
    "Medio":    "#F9E04B",
    "Alto":     "#F39C12",
    "Crítico":  "#E74C3C",
}

CRITICAL_THRESHOLD: float = 20.0   # residual_risk >= this → Crítico

MIN_RISKS_FOR_ANALYSIS: int = 3

# ---------------------------------------------------------------------------
# NIST CSF v1.1 taxonomy
# ---------------------------------------------------------------------------
NIST_CATEGORIES: Dict[str, str] = {
    "ID": "Identify",
    "PR": "Protect",
    "DE": "Detect",
    "RS": "Respond",
    "RC": "Recover",
}

NIST_SUBCATEGORIES: Dict[str, str] = {
    "ID.AM": "Asset Management",
    "ID.BE": "Business Environment",
    "ID.GV": "Governance",
    "ID.RA": "Risk Assessment",
    "ID.RM": "Risk Management Strategy",
    "PR.AC": "Access Control",
    "PR.AT": "Awareness and Training",
    "PR.DS": "Data Security",
    "PR.IP": "Information Protection",
    "PR.MA": "Maintenance",
    "PR.PT": "Protective Technology",
    "DE.AE": "Anomalies and Events",
    "DE.CM": "Security Continuous Monitoring",
    "DE.DP": "Detection Processes",
    "RS.RP": "Response Planning",
    "RS.CO": "Communications",
    "RS.AN": "Analysis",
    "RS.MI": "Mitigation",
    "RS.IM": "Improvements",
    "RC.RP": "Recovery Planning",
    "RC.IM": "Improvements",
    "RC.CO": "Communications",
}

NIST_CATEGORY_COLORS: Dict[str, str] = {
    "ID": "#3498DB",
    "PR": "#27AE60",
    "DE": "#F39C12",
    "RS": "#E74C3C",
    "RC": "#9B59B6",
}

TIME_HORIZONS: List[str] = ["Corto plazo", "Medio plazo", "Largo plazo"]

# ---------------------------------------------------------------------------
# CSV schema
# ---------------------------------------------------------------------------
CSV_REQUIRED_FIELDS: List[str] = [
    "risk_id", "risk_name", "risk_category", "risk_subcategory",
    "probability", "impact", "current_controls", "control_effectiveness",
    "risk_owner", "mitigation_cost", "time_horizon", "nist_reference",
]

# ---------------------------------------------------------------------------
# Professional colour palette
# ---------------------------------------------------------------------------
COLORS: Dict[str, str] = {
    "primary":        "#1A237E",
    "secondary":      "#283593",
    "accent":         "#3F51B5",
    "accent_light":   "#7986CB",
    "background":     "#F0F2F5",
    "surface":        "#FFFFFF",
    "text_primary":   "#212121",
    "text_secondary": "#616161",
    "border":         "#E0E0E0",
    "success":        "#2ECC71",
    "warning":        "#F39C12",
    "danger":         "#E74C3C",
    "info":           "#3498DB",
    "header_bg":      "#1A237E",
    "header_text":    "#FFFFFF",
    "tab_active":     "#3F51B5",
    "tab_inactive":   "#283593",
}

# ---------------------------------------------------------------------------
# Chart settings
# ---------------------------------------------------------------------------
CHART_DPI: int = 100
CHART_FONT_FAMILY: str = "DejaVu Sans"

# Matplotlib style overrides applied globally in main.py
MPL_PARAMS: Dict = {
    "font.family":          "DejaVu Sans",
    "font.size":            10,
    "axes.spines.top":      False,
    "axes.spines.right":    False,
    "axes.grid":            True,
    "grid.alpha":           0.3,
    "grid.color":           "#CCCCCC",
    "figure.facecolor":     "white",
    "axes.facecolor":       "#FAFAFA",
}

# ---------------------------------------------------------------------------
# Application stylesheet (QSS)
# ---------------------------------------------------------------------------
APP_STYLESHEET = """
/* ── Global ────────────────────────────────────────────── */
QMainWindow, QWidget {
    background-color: #F0F2F5;
    font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    font-size: 13px;
    color: #212121;
}

/* ── Header bar ────────────────────────────────────────── */
#headerBar {
    background-color: #1A237E;
    border-bottom: 2px solid #3F51B5;
}
#headerTitle {
    color: #FFFFFF;
    font-size: 20px;
    font-weight: bold;
    letter-spacing: 0.5px;
}
#headerSubtitle {
    color: #9FA8DA;
    font-size: 11px;
}

/* ── Tab widget ────────────────────────────────────────── */
QTabWidget::pane {
    border: none;
    background-color: #F0F2F5;
}
QTabBar {
    background-color: #283593;
}
QTabBar::tab {
    background-color: #283593;
    color: #9FA8DA;
    padding: 14px 26px;
    font-size: 13px;
    font-weight: 500;
    border: none;
    min-width: 180px;
}
QTabBar::tab:selected {
    background-color: #3F51B5;
    color: #FFFFFF;
    font-weight: bold;
    border-bottom: 3px solid #82B1FF;
}
QTabBar::tab:hover:!selected {
    background-color: #303F9F;
    color: #E8EAF6;
}

/* ── KPI Card ──────────────────────────────────────────── */
#kpiCard {
    background-color: #FFFFFF;
    border-radius: 10px;
    border: 1px solid #E0E0E0;
}
#kpiTitle {
    color: #616161;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}
#kpiValue {
    font-size: 28px;
    font-weight: bold;
    color: #1A237E;
}
#kpiSubtitle {
    color: #9E9E9E;
    font-size: 11px;
}

/* ── Section headers ───────────────────────────────────── */
#sectionTitle {
    color: #1A237E;
    font-size: 14px;
    font-weight: bold;
    padding-bottom: 4px;
    border-bottom: 2px solid #3F51B5;
}

/* ── Tables ────────────────────────────────────────────── */
QTableView, QTableWidget {
    background-color: #FFFFFF;
    gridline-color: #EEEEEE;
    selection-background-color: #E8EAF6;
    selection-color: #1A237E;
    border: 1px solid #E0E0E0;
    border-radius: 6px;
    font-size: 12px;
    alternate-background-color: #F8F9FF;
}
QHeaderView::section {
    background-color: #283593;
    color: #FFFFFF;
    padding: 8px 10px;
    border: none;
    border-right: 1px solid #3949AB;
    font-weight: bold;
    font-size: 12px;
}
QHeaderView::section:last {
    border-right: none;
}
QHeaderView::section:hover {
    background-color: #3F51B5;
}

/* ── Buttons ───────────────────────────────────────────── */
QPushButton {
    background-color: #3F51B5;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 10px 22px;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.3px;
}
QPushButton:hover {
    background-color: #303F9F;
}
QPushButton:pressed {
    background-color: #1A237E;
}
QPushButton#btnDanger {
    background-color: #E74C3C;
}
QPushButton#btnDanger:hover {
    background-color: #C0392B;
}
QPushButton#btnSuccess {
    background-color: #27AE60;
}
QPushButton#btnSuccess:hover {
    background-color: #1E8449;
}

/* ── Combo Boxes ───────────────────────────────────────── */
QComboBox {
    background-color: #FFFFFF;
    border: 1px solid #BDBDBD;
    border-radius: 5px;
    padding: 6px 12px;
    font-size: 12px;
    min-width: 155px;
    color: #212121;
}
QComboBox:hover {
    border-color: #3F51B5;
}
QComboBox:focus {
    border-color: #3F51B5;
    border-width: 2px;
}
QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}
QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    selection-background-color: #E8EAF6;
    selection-color: #1A237E;
    border: 1px solid #E0E0E0;
}

/* ── Line Edit ─────────────────────────────────────────── */
QLineEdit {
    background-color: #FFFFFF;
    border: 1px solid #BDBDBD;
    border-radius: 5px;
    padding: 6px 12px;
    font-size: 12px;
    color: #212121;
}
QLineEdit:focus {
    border-color: #3F51B5;
    border-width: 2px;
}

/* ── Scroll Bars ───────────────────────────────────────── */
QScrollBar:vertical {
    background: #F0F2F5;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #9FA8DA;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #3F51B5;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar:horizontal {
    background: #F0F2F5;
    height: 8px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background: #9FA8DA;
    border-radius: 4px;
    min-width: 30px;
}

/* ── Status Bar ────────────────────────────────────────── */
QStatusBar {
    background-color: #1A237E;
    color: #9FA8DA;
    font-size: 11px;
    padding: 2px 8px;
}

/* ── ToolTip ───────────────────────────────────────────── */
QToolTip {
    background-color: #212121;
    color: #FFFFFF;
    border: none;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 12px;
}

/* ── Label tweaks ──────────────────────────────────────── */
QLabel {
    color: #212121;
}
"""
