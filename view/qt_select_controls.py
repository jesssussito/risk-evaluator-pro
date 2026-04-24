from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
)
from PySide6.QtCore import Qt


class SelectControlsView(QWidget):
    """
    Paso 3 del flujo:
    Selección de fortalezas (controles reales) por riesgo.
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

        self.risk_list = QListWidget()
        self._load_active_risks()
        self.risk_list.currentRowChanged.connect(self._on_select_risk)

        left.addWidget(self.risk_list)
        main_layout.addLayout(left, 1)

        # ==================================================
        # DERECHA – Controles del riesgo seleccionado
        # ==================================================
        right = QVBoxLayout()
        right.setSpacing(12)

        self.controls_title = QLabel(
            "Select a risk to view its controls"
        )
        self.controls_title.setStyleSheet("font-size: 15px; font-weight: 700;")
        right.addWidget(self.controls_title)

        description = QLabel(
            "Check the controls that actually exist in the company "
            "for this risk. These controls will reduce the residual risk."
        )
        description.setWordWrap(True)
        description.setStyleSheet("color: #888888;")
        right.addWidget(description)

        # --------------------------
        # Lista de controles
        # --------------------------
        self.controls_list = QListWidget()
        right.addWidget(self.controls_list)

        # ==================================================
        # EXPLICACIÓN DE LAS FORTALEZAS DEL RIESGO (UX)
        # ==================================================
        self.control_help = QLabel("")
        self.control_help.setWordWrap(True)
        self.control_help.setStyleSheet("color: #888888; font-size: 12px;")
        right.addWidget(self.control_help)

        right.addStretch()

        # --------------------------
        # Botones
        # --------------------------
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

    # ==================================================
    # Lógica
    # ==================================================

    def _load_active_risks(self):
        self.risk_list.clear()
        self.active_risks = self.controller.company_assessment.get_active_risks()

        for cr in self.active_risks:
            item = QListWidgetItem(cr.base_risk.name)
            self.risk_list.addItem(item)

    def _on_select_risk(self, index: int):
        if index < 0:
            return

        # Guardar el estado del panel actual ANTES de cambiar de riesgo.
        # Sin esto, los controles modificados se pierden al seleccionar otro riesgo.
        self._save_current_controls()

        cr = self.active_risks[index]
        self.selected_risk = cr

        self.controls_title.setText(
            f"Controls for: {cr.base_risk.name}"
        )

        self._load_controls_for_risk(cr)

    def _load_controls_for_risk(self, cr):
        self.controls_list.clear()

        descriptions = []

        for control_id, control in cr.base_risk.controls.items():
            item = QListWidgetItem(
                f"{control.name}  (base effectiveness: {control.base_effectiveness:.2f})"
            )
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)

            checked = control_id in cr.enabled_controls
            item.setCheckState(
                Qt.Checked if checked else Qt.Unchecked
            )

            item.setData(Qt.UserRole, control)
            self.controls_list.addItem(item)

            # Acumular descripciones
            if control.description:
                descriptions.append(
                    f"• {control.name}:\n  {control.description}"
                )

        # Mostrar TODAS las descripciones automáticamente
        if descriptions:
            self.control_help.setText(
                "What do these controls consist of?\n\n" +
                "\n\n".join(descriptions)
            )
        else:
            self.control_help.setText(
                "No descriptions available for the controls of this risk."
            )

    def _save_current_controls(self):
        """
        Persiste los controles visibles en el panel al CompanyRisk seleccionado.
        Debe llamarse antes de cambiar de riesgo o de navegar.
        """
        if not self.selected_risk:
            return
        self.selected_risk.enabled_controls.clear()
        for i in range(self.controls_list.count()):
            item = self.controls_list.item(i)
            if item.checkState() == Qt.Checked:
                control = item.data(Qt.UserRole)
                self.selected_risk.enabled_controls[control.control_id] = control

    def _apply_and_next(self):
        self._save_current_controls()
        if self.on_next:
            self.on_next()

    def _go_back(self):
        self._save_current_controls()
        if self.on_back:
            self.on_back()

    def refresh(self):
        self._load_active_risks()
        self.controls_list.clear()
        self.control_help.setText("")
        self.controls_title.setText(
            "Select a risk to view its controls"
        )
        self.selected_risk = None
