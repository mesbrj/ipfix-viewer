import sys
from PySide6.QtWidgets import QApplication
from mainwindow import MainWindow


if __name__ == '__main__':
    app = QApplication(sys.argv)
    with open("Combinear.qss", "r") as style_file:
        app.setStyleSheet(style_file.read())
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
