from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QSpinBox,
    QPushButton,
    QGroupBox,
)
from PySide6.QtCore import Qt


class EditCriticitiesView(QWidget):
    """
    Paso 2 del flujo:
    Edición de criticidades de los riesgos activos.
    """

    def __init__(self, controller, on_back=None, on_next=None):
        super().__init__()
        self.controller = controller
        self.on_back = on_back
        self.on_next = on_next

        self.selected_risk = None

        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(24)
        main_layout.setContentsMargins(24, 20, 24, 20)

        # ==================================================
        # IZQUIERDA – Lista de riesgos activos
        # ==================================================
        left = QVBoxLayout()
        left.setSpacing(10)

        title = QLabel("Active Risks")
        title.setStyleSheet("font-size: 15px; font-weight: 700;")
        left.addWidget(title)

        self.list_widget = QListWidget()
        self._load_active_risks()
        self.list_widget.currentItemChanged.connect(self._on_select_risk)

        left.addWidget(self.list_widget)

        main_layout.addLayout(left, 1)

        # ==================================================
        # DERECHA – Editor
        # ==================================================
        right = QVBoxLayout()
        right.setSpacing(12)

        self.editor_title = QLabel("Select a risk to edit")
        self.editor_title.setStyleSheet("font-size: 15px; font-weight: 700;")
        right.addWidget(self.editor_title)

        self.spin_p = self._spinbox("Probability", right)
        self.spin_if = self._spinbox("Financial Impact", right)
        self.spin_io = self._spinbox("Operational Impact", right)
        self.spin_ir = self._spinbox("Reputational Impact", right)
        self.scale_help = self._build_scale_help()
        right.addWidget(self.scale_help)

        # ==================================================
        # EXPLICACIÓN DE TIPOS DE IMPACTO (UX)
        # ==================================================
        impact_help = QLabel(
            "• Financial impact:\n"
            "  Direct or indirect financial losses: fines, fraud, "
            "revenue disruption, recovery costs.\n\n"
            "• Operational impact:\n"
            "  Disruption to normal business operations: system outages, "
            "service interruptions, loss of productivity.\n\n"
            "• Reputational impact:\n"
            "  Damage to company image: loss of customer trust, "
            "brand impact, negative media exposure.\n\n"
        )
        impact_help.setWordWrap(True)
        impact_help.setStyleSheet("color: #888888; font-size: 12px;")

        right.addWidget(impact_help)

        right.addStretch()

        # Botones
        buttons = QHBoxLayout()

        back_btn = QPushButton("Back")
        back_btn.setMinimumHeight(36)
        back_btn.clicked.connect(self._go_back)

        next_btn = QPushButton("Next")
        next_btn.setMinimumHeight(36)
        next_btn.clicked.connect(self._apply_and_next)

        buttons.addWidget(back_btn)
        buttons.addStretch()
        buttons.addWidget(next_btn)

        right.addLayout(buttons)

        main_layout.addLayout(right, 2)

        self._set_editor_enabled(False)

    # ==================================================
    # Construcción de componentes
    # ==================================================

    def _spinbox(self, label, parent_layout):
        box = QGroupBox(label)
        layout = QVBoxLayout(box)

        spin = QSpinBox()
        spin.setRange(1, 5)
        spin.setEnabled(False)

        layout.addWidget(spin)
        parent_layout.addWidget(box)

        return spin

    def _build_scale_help(self):
        help_box = QGroupBox("Scale Guide (1–5)")
        layout = QVBoxLayout(help_box)

        text = QLabel(
            "1 – Very low / unlikely\n"
            "2 – Low\n"
            "3 – Moderate\n"
            "4 – High\n"
            "5 – Critical / very likely"
        )
        text.setStyleSheet("color: #888888;")
        layout.addWidget(text)

        return help_box

    

    # ==================================================
    # Lógica
    # ==================================================

    def _load_active_risks(self):
        self.list_widget.clear()
        self.active_risks = []

        for cr in self.controller.company_assessment.get_active_risks():
            item = QListWidgetItem(cr.base_risk.name)
            self.list_widget.addItem(item)
            self.active_risks.append(cr)

    def _on_select_risk(self, current, previous):
        if not current:
            return

        # 🔴 GUARDAR ANTES DE CAMBIAR DE RIESGO
        self._save_current_edits()

        index = self.list_widget.currentRow()
        cr = self.active_risks[index]

        self.selected_risk = cr
        self.editor_title.setText(f"Editing: {cr.base_risk.name}")

        self.spin_p.setValue(cr.custom_probability)
        self.spin_if.setValue(cr.custom_impact_financial)
        self.spin_io.setValue(cr.custom_impact_operational)
        self.spin_ir.setValue(cr.custom_impact_reputational)

        self._set_editor_enabled(True)

    def _set_editor_enabled(self, enabled: bool):
        for spin in (self.spin_p, self.spin_if, self.spin_io, self.spin_ir):
            spin.setEnabled(enabled)
    def _save_current_edits(self):
        """
        Guarda los valores actuales en el riesgo seleccionado (si existe).
        """
        if not self.selected_risk:
            return

        self.selected_risk.set_custom_scores(
            self.spin_p.value(),
            self.spin_if.value(),
            self.spin_io.value(),
            self.spin_ir.value(),
        )

    def _apply_and_next(self):
        self._save_current_edits()

        if self.on_next:
            self.on_next()

    def _go_back(self):
        self._save_current_edits()

        if self.on_back:
            self.on_back()
    def refresh(self):
        """
        Refresca la lista de riesgos activos sin perder ediciones.
        """
        self._load_active_risks()

        # No forzar reset del editor
        self.selected_risk = None
        self.editor_title.setText("Select a risk to edit")
        self._set_editor_enabled(False)

