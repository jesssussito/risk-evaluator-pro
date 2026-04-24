import sys
from PySide6.QtWidgets import QApplication

from controller.app_controller import AppController
from view.qt_main_window import MainWindow


def main():
    # ==============================
    # Inicialización del controlador
    # ==============================
    controller = AppController()
    controller.load_all_data()

    # ==============================
    # Inicialización de la app Qt
    # ==============================
    app = QApplication(sys.argv)

    window = MainWindow(controller)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
