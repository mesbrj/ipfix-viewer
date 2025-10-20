import sys
from PySide6.QtWidgets import QApplication
from mainwindow import MainWindow


if __name__ == '__main__':
    app = QApplication(sys.argv)

    try:
        with open("Combinear.qss", "r") as style_file:
            app.setStyleSheet(style_file.read())
    except FileNotFoundError:
        print("Warning: Combinear.qss stylesheet not found, using default styling")
    except Exception as e:
        print(f"Warning: Could not load stylesheet: {e}")

    try:
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error: Failed to start application: {e}")
        sys.exit(1)
