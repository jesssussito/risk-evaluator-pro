from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QHBoxLayout,
    QFrame,
    QMessageBox,
)
from PySide6.QtCore import Qt

from view.qt_select_risks import SelectRisksView
from view.qt_edit_criticities import EditCriticitiesView
from view.qt_select_controls import SelectControlsView
from view.analysis.analysis_view import AnalysisView
from view.qt_final import FinalizePanel


# ──────────────────────────────────────────────────────────────────────────────
# DESIGN SYSTEM – paleta única: #0b0b0b · #141414 · #ffffff · #aaff00
# Lima: encabezados, elementos interactivos (hover/activo), acentos de estado
# Blanco: texto general y valores numéricos (KPIs)
# ──────────────────────────────────────────────────────────────────────────────
APP_STYLESHEET = """
QWidget {
    background-color: #0b0b0b;
    color: #ffffff;
    font-family: 'Segoe UI', 'Inter', 'Arial', sans-serif;
    font-size: 13px;
}
QMainWindow { background-color: #0b0b0b; }

/* ── Scroll ─────────────────────────────────────────────────────────────── */
QScrollArea { border: none; background-color: transparent; }
QScrollBar:vertical {
    background: #0f0f0f;  width: 7px;  border-radius: 3px;  margin: 0;
}
QScrollBar::handle:vertical {
    background: #2a2a2a;  border-radius: 3px;  min-height: 24px;
}
QScrollBar::handle:vertical:hover { background: #aaff00; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal {
    background: #0f0f0f;  height: 7px;  border-radius: 3px;  margin: 0;
}
QScrollBar::handle:horizontal {
    background: #2a2a2a;  border-radius: 3px;  min-width: 24px;
}
QScrollBar::handle:horizontal:hover { background: #aaff00; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* ── Buttons ────────────────────────────────────────────────────────────── */
QPushButton {
    background-color: #141414;
    color: #aaaaaa;
    border: 1px solid #222222;
    border-radius: 6px;
    padding: 8px 14px;
    font-size: 13px;
    text-align: left;
}
QPushButton:hover:enabled  { border-color: #aaff00; color: #aaff00; }
QPushButton:pressed:enabled { background-color: #1a1a1a; border-color: #aaff00; color: #aaff00; }
QPushButton:disabled       { color: #2e2e2e; border-color: #181818; background-color: #0d0d0d; }

/* ── Labels ─────────────────────────────────────────────────────────────── */
QLabel { background-color: transparent; color: #ffffff; }

/* ── Table ──────────────────────────────────────────────────────────────── */
QTableWidget {
    background-color: #0f0f0f;
    gridline-color: #1a1a1a;
    border: 1px solid #1e1e1e;
    border-radius: 6px;
    selection-background-color: #172200;
    selection-color: #aaff00;
    outline: none;
}
QTableWidget::item               { padding: 6px 10px; color: #cccccc; }
QTableWidget::item:selected      { background-color: #172200; color: #aaff00; }
QTableWidget::item:hover         { background-color: #141414; }
QHeaderView::section {
    background-color: #141414;
    color: #aaff00;
    border: none;
    border-bottom: 1px solid #1e1e1e;
    border-right: 1px solid #1a1a1a;
    padding: 6px 10px;
    font-weight: 600;
    font-size: 12px;
    letter-spacing: 0.4px;
}
QTableCornerButton::section { background-color: #141414; border: none; }

/* ── Inputs ─────────────────────────────────────────────────────────────── */
QLineEdit, QSpinBox, QDoubleSpinBox {
    background-color: #141414;
    color: #ffffff;
    border: 1px solid #222222;
    border-radius: 5px;
    padding: 5px 10px;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus { border-color: #aaff00; }
QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    background-color: #1e1e1e;  border: none;  width: 16px;
}
QSpinBox::up-button:hover, QSpinBox::down-button:hover,
QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
    background-color: #2a2a2a;
}

/* ── ComboBox ───────────────────────────────────────────────────────────── */
QComboBox {
    background-color: #141414;
    color: #ffffff;
    border: 1px solid #222222;
    border-radius: 5px;
    padding: 5px 10px;
}
QComboBox:focus { border-color: #aaff00; }
QComboBox::drop-down { border: none; width: 22px; }
QComboBox QAbstractItemView {
    background-color: #141414;
    color: #ffffff;
    selection-background-color: #172200;
    selection-color: #aaff00;
    border: 1px solid #222222;
    outline: none;
}

/* ── CheckBox ───────────────────────────────────────────────────────────── */
QCheckBox { color: #cccccc; spacing: 8px; }
QCheckBox::indicator {
    width: 16px;  height: 16px;
    border: 1px solid #333333;
    border-radius: 3px;
    background-color: #141414;
}
QCheckBox::indicator:checked          { background-color: #aaff00; border-color: #aaff00; }
QCheckBox::indicator:unchecked:hover  { border-color: #aaff00; }

/* ── Tabs ───────────────────────────────────────────────────────────────── */
QTabWidget::pane {
    border: 1px solid #1e1e1e;
    background-color: #0b0b0b;
    border-radius: 0 6px 6px 6px;
}
QTabBar::tab {
    background-color: #0f0f0f;
    color: #555555;
    border: 1px solid #1e1e1e;
    border-bottom: none;
    padding: 8px 20px;
    font-size: 13px;
    margin-right: 2px;
    border-radius: 6px 6px 0 0;
}
QTabBar::tab:selected {
    background-color: #0b0b0b;
    color: #aaff00;
    border-bottom: 2px solid #aaff00;
    font-weight: 600;
}
QTabBar::tab:hover:!selected { color: #cccccc; }

/* ── GroupBox ───────────────────────────────────────────────────────────── */
QGroupBox {
    border: 1px solid #1e1e1e;
    border-radius: 6px;
    margin-top: 14px;
    padding-top: 8px;
}
QGroupBox::title {
    color: #aaff00;
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 6px;
    font-weight: 600;
    font-size: 12px;
}

/* ── Separators ─────────────────────────────────────────────────────────── */
QFrame[frameShape="4"], QFrame[frameShape="5"] { color: #1e1e1e; }

/* ── Splitter ───────────────────────────────────────────────────────────── */
QSplitter::handle { background-color: #1a1a1a; width: 1px; height: 1px; }

/* ── Tooltip ────────────────────────────────────────────────────────────── */
QToolTip {
    background-color: #141414;
    color: #ffffff;
    border: 1px solid #aaff00;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
}

/* ── Slider ─────────────────────────────────────────────────────────────── */
QSlider::groove:horizontal {
    background: #1e1e1e;  height: 4px;  border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #aaff00;
    width: 14px;  height: 14px;
    margin: -5px 0;  border-radius: 7px;
}
QSlider::sub-page:horizontal { background: #aaff00; border-radius: 2px; }
"""

# ── Estilos de estado de los botones del sidebar ──────────────────────────────

# Paso activo: borde lima + texto lima
_NAV_BTN_ACTIVE = """
    QPushButton:disabled {
        background-color: #141414;
        color: #aaff00;
        border: 1px solid #aaff00;
        border-radius: 6px;
        padding: 8px 14px;
        font-size: 13px;
        text-align: left;
        font-weight: 600;
    }
"""

# Paso completado: visible pero muted, con "✓" en el texto
_NAV_BTN_DONE = """
    QPushButton:disabled {
        background-color: #0f0f0f;
        color: #4a4a4a;
        border: 1px solid #1e1e1e;
        border-radius: 6px;
        padding: 8px 14px;
        font-size: 13px;
        text-align: left;
    }
"""

# Paso bloqueado: usa el estilo global QPushButton:disabled (#2e2e2e, casi invisible)
_NAV_BTN_LOCKED = ""

# Textos de cada paso (sin prefijo – el prefijo "✓" se añade dinámicamente)
_STEP_LABELS = [
    "1. Risk Selection",
    "2. Criticalities",
    "3. Controls",
    "4. Analysis",
]


class MainWindow(QMainWindow):
    """
    Ventana principal de la aplicación.
    Orquesta el flujo completo de vistas.

    Navegación:
    - El usuario avanza y retrocede SOLO mediante los botones "Siguiente" / "Atrás"
      de cada vista. Los botones del sidebar son indicadores visuales de progreso,
      no controles de navegación.
    - Estado interno: _current_step (paso visible) y _max_reached (máximo alcanzado).
    """

    def __init__(self, controller):
        super().__init__()

        self.controller = controller
        self.setWindowTitle("Risk Evaluator Pro")
        self.resize(1200, 700)
        self.setStyleSheet(APP_STYLESHEET)

        # ── Estado de progreso ────────────────────────────────────────────────
        # _current_step : paso que se está mostrando ahora (0-3)
        # _max_reached  : paso más avanzado al que el usuario ha llegado
        self._current_step: int = 0
        self._max_reached: int = 0

        # ==================================================
        # Layout base
        # ==================================================
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ==================================================
        # Sidebar – indicador visual de progreso (no navegable)
        # ==================================================
        sidebar_widget = QWidget()
        sidebar_widget.setObjectName("Sidebar")
        sidebar_widget.setStyleSheet("""
            QWidget#Sidebar {
                background-color: #0f0f0f;
                border-right: 1px solid #1a1a1a;
            }
        """)

        sidebar = QVBoxLayout(sidebar_widget)
        sidebar.setSpacing(6)
        sidebar.setContentsMargins(14, 18, 14, 18)

        title = QLabel("Workflow")
        title.setStyleSheet(
            "font-size: 14px; font-weight: 700; color: #aaff00;"
            "padding-bottom: 4px; background: transparent;"
        )
        sidebar.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #1e1e1e; margin-bottom: 6px;")
        sidebar.addWidget(sep)

        self.btn_select = QPushButton(_STEP_LABELS[0])
        self.btn_crit   = QPushButton(_STEP_LABELS[1])
        self.btn_ctrl   = QPushButton(_STEP_LABELS[2])
        self.btn_dash   = QPushButton(_STEP_LABELS[3])

        self._nav_buttons = [self.btn_select, self.btn_crit, self.btn_ctrl, self.btn_dash]

        for btn in self._nav_buttons:
            btn.setEnabled(False)   # siempre deshabilitados: no son controles de nav
            btn.setMinimumHeight(40)
            sidebar.addWidget(btn)

        sidebar.addStretch()
        main_layout.addWidget(sidebar_widget, 1)

        # ==================================================
        # Área de contenido
        # ==================================================
        self.content = QVBoxLayout()
        self.content.setContentsMargins(0, 0, 0, 0)

        content_wrapper = QWidget()
        content_wrapper.setLayout(self.content)
        main_layout.addWidget(content_wrapper, 4)

        # ==================================================
        # Panel Finalizar (lado derecho)
        # ==================================================
        self.finalize_panel = FinalizePanel(self.controller)
        self.finalize_panel.setVisible(False)
        main_layout.addWidget(self.finalize_panel, 1)

        # ==================================================
        # Vistas – los callbacks on_next / on_back son la
        # única vía de navegación entre pasos.
        # ==================================================
        # on_next usa métodos de avance con validación.
        # on_back usa métodos de show directos (sin validación al retroceder).
        self.select_risks_view = SelectRisksView(
            self.controller,
            on_next=self._advance_to_step2,
        )

        self.edit_criticities_view = EditCriticitiesView(
            self.controller,
            on_back=self._show_select_risks,
            on_next=self._advance_to_step3,
        )

        self.select_controls_view = SelectControlsView(
            self.controller,
            on_back=self._show_edit_criticities,
            on_next=self._advance_to_step4,
        )

        self.analysis_view = AnalysisView(self.controller)

        # ==================================================
        # Estado inicial
        # ==================================================
        self._show_select_risks()

    # ── Helpers internos ──────────────────────────────────────────────────────

    def _clear_content(self):
        while self.content.count():
            item = self.content.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

    def _load_view(self, view: QWidget):
        """Vacía el área de contenido y muestra la vista indicada."""
        self._clear_content()
        view.refresh()
        self.content.addWidget(view)

    def _update_sidebar(self):
        """
        Sincroniza el sidebar con el estado de progreso actual.

        Tres estados visuales:
          active  → paso en pantalla ahora           (lima, borde lima)
          done    → paso completado y superado        (muted, prefijo ✓)
          locked  → paso al que aún no se ha llegado  (casi invisible)
        """
        for idx, btn in enumerate(self._nav_buttons):
            if idx == self._current_step:
                btn.setText(_STEP_LABELS[idx])
                btn.setStyleSheet(_NAV_BTN_ACTIVE)
            elif idx <= self._max_reached:
                btn.setText("✓  " + _STEP_LABELS[idx])
                btn.setStyleSheet(_NAV_BTN_DONE)
            else:
                btn.setText(_STEP_LABELS[idx])
                btn.setStyleSheet(_NAV_BTN_LOCKED)

    # ── Validación y avance ───────────────────────────────────────────────────
    # Los métodos _advance_to_* son los únicos callbacks de on_next.
    # Validan las precondiciones del paso destino; si no se cumplen,
    # muestran un error y NO navegan. Los _show_* nunca validan.

    def _show_error(self, title: str, message: str) -> None:
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QMessageBox.Warning)
        msg.setStyleSheet("""
            QMessageBox  { background-color: #141414; }
            QLabel       { color: #ffffff; font-size: 13px; }
            QPushButton  {
                background-color: #141414;
                color: #aaff00;
                border: 1px solid #aaff00;
                border-radius: 6px;
                padding: 6px 20px;
                min-width: 80px;
                text-align: center;
            }
            QPushButton:hover { background-color: #1a1a1a; }
        """)
        msg.exec()

    def _advance_to_step2(self) -> None:
        """Paso 1 → 2: exige al menos un riesgo seleccionado."""
        if not self.controller.company_assessment.get_active_risks():
            self._show_error(
                "Selection required",
                "At least one risk must be selected to continue.\n\n"
                "Check one or more risks in the list and click Next.",
            )
            return
        self._show_edit_criticities()

    def _advance_to_step3(self) -> None:
        """Paso 2 → 3: comprueba que siguen existiendo riesgos activos."""
        if not self.controller.company_assessment.get_active_risks():
            self._show_error(
                "No active risks",
                "No active risks. Go back to step 1 and select at least one.",
            )
            return
        self._show_select_controls()

    def _advance_to_step4(self) -> None:
        """Paso 3 → 4: garantiza que el dashboard tiene datos para mostrar."""
        if not self.controller.company_assessment.get_active_risks():
            self._show_error(
                "No data for analysis",
                "No active risks to analyze.\n\n"
                "Go back to step 1 and select at least one risk.",
            )
            return
        self._show_analysis()

    # ── Navegación controlada ─────────────────────────────────────────────────
    # Los _show_* solo actualizan estado y cargan la vista. Sin validación.
    # Son invocados por los _advance_to_* (avance) y directamente (retroceso).

    def _show_select_risks(self):
        self._current_step = 0
        self._max_reached = max(self._max_reached, 0)
        self._update_sidebar()
        self._load_view(self.select_risks_view)
        self.finalize_panel.setVisible(False)

    def _show_edit_criticities(self):
        self._current_step = 1
        self._max_reached = max(self._max_reached, 1)
        self._update_sidebar()
        self._load_view(self.edit_criticities_view)
        self.finalize_panel.setVisible(False)

    def _show_select_controls(self):
        self._current_step = 2
        self._max_reached = max(self._max_reached, 2)
        self._update_sidebar()
        self._load_view(self.select_controls_view)
        self.finalize_panel.setVisible(False)

    def _show_analysis(self):
        self._current_step = 3
        self._max_reached = max(self._max_reached, 3)
        self._update_sidebar()
        self._load_view(self.analysis_view)
        self.finalize_panel.setVisible(True)
