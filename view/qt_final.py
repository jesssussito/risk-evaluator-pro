from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
)
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog


class FinalizePanel(QWidget):
    """
    Final action panel.
    Forces a conscious decision before closing the application.
    """

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        self.setStyleSheet("""
            QWidget {
                border-left: 1px solid #1a1a1a;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(16)
        layout.setContentsMargins(14, 18, 14, 18)

        title = QLabel("Finalize")
        title.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #ccc;
                margin-bottom: 8px;
            }
        """)
        layout.addWidget(title)

        self.generate_btn = QPushButton("Generate PDF & Exit")
        self.generate_btn.clicked.connect(self._generate_and_exit)
        layout.addWidget(self.generate_btn)

        self.exit_btn = QPushButton("Exit without Report")
        self.exit_btn.clicked.connect(self._exit_only)
        layout.addWidget(self.exit_btn)

        layout.addStretch()

    def _generate_and_exit(self):
        reply = QMessageBox.question(
            self,
            "Finalize Analysis",
            "Generate the Cost of Inaction report and exit?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply != QMessageBox.Yes:
            return

        # 1. Elegir dónde guardar el PDF
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Cost of Inaction Report",
            "Cost_of_Inaction_Report.pdf",
            "PDF Files (*.pdf)",
        )

        if not file_path:
            return  # El usuario canceló

        try:
            # 2. Generar el PDF en la ruta elegida
            self.controller.generate_cost_of_inaction_report(file_path)

            QMessageBox.information(
                self,
                "Report generated",
                "The Cost of Inaction report was generated successfully.",
            )

            # 3. Cerrar la aplicación
            self.window().close()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Report generation failed",
                f"An error occurred while generating the report:\n\n{e}",
            )

            # Rehabilitar botones si algo falla
            self.generate_btn.setEnabled(True)
            self.exit_btn.setEnabled(True)



    def _exit_only(self):
        reply = QMessageBox.question(
            self,
            "Exit",
            "Exit without generating a report?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.window().close()
