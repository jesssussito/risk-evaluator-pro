from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QHBoxLayout,
)
from PySide6.QtCore import Qt


class SelectRisksView(QWidget):
    """
    Paso 1 del flujo:
    Selección de riesgos aplicables a la empresa.
    """

    def __init__(self, controller, on_next=None):
        super().__init__()
        self.controller = controller
        self.on_next = on_next

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(14)
        main_layout.setContentsMargins(24, 20, 24, 20)

        title = QLabel("Company Risk Selection")
        title.setStyleSheet("font-size: 20px; font-weight: 700;")
        main_layout.addWidget(title)

        description = QLabel(
            "Select the risks applicable to your company. "
            "This selection defines the scope of the subsequent analysis."
        )
        description.setWordWrap(True)
        description.setStyleSheet("color: #888888;")
        main_layout.addWidget(description)

        self.list_widget = QListWidget()
        self.list_widget.setSpacing(4)
        self.list_widget.setMinimumHeight(220)
        main_layout.addWidget(self.list_widget)

        main_layout.addSpacing(6)

        buttons = QHBoxLayout()
        buttons.addStretch()
        next_btn = QPushButton("Next")
        next_btn.setFixedWidth(140)
        next_btn.setMinimumHeight(36)
        next_btn.clicked.connect(self._apply_and_next)
        buttons.addWidget(next_btn)
        main_layout.addLayout(buttons)

    # ==========================================================
    # Lógica
    # ==========================================================

    def _save_to_model(self):
        """Persiste el estado actual de los checkboxes en CompanyAssessment."""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            self.controller.company_assessment.set_risk_active(
                item.data(Qt.UserRole),
                item.checkState() == Qt.Checked,
            )

    def _apply_and_next(self):
        self._save_to_model()
        if self.on_next:
            self.on_next()

    def refresh(self):
        """
        Reconstruye la lista leyendo el estado desde el modelo.
        Las selecciones previas (guardadas con _save_to_model) se recuperan aquí.
        """
        self.list_widget.clear()
        for risk_id, risk in self.controller.risks.items():
            cr = self.controller.company_assessment.company_risks[risk_id]
            item = QListWidgetItem(f"{risk.name}  ({risk.risk_type.name})")
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if cr.active else Qt.Unchecked)
            item.setData(Qt.UserRole, risk_id)
            self.list_widget.addItem(item)
