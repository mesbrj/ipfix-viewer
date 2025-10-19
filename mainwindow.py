import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QAbstractItemView, QApplication, QMainWindow, QTreeView, QWidget
    )
from PySide6.QtTest import QAbstractItemModelTester

from treemodel import TreeModel


class MainWindow(QMainWindow):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.resize(573, 468)

        self.view = QTreeView()
        self.view.setAlternatingRowColors(True)
        self.view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.view.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.view.setAnimated(False)
        self.view.setAllColumnsShowFocus(True)
        self.setCentralWidget(self.view)

        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")
        self.exit_action = file_menu.addAction("E&xit")
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(self.close)
        help_menu = menubar.addMenu("&Help")
        about_qt_action = help_menu.addAction("About Qt", QApplication.instance().aboutQt)
        about_qt_action.setShortcut("F1")

        self.setWindowTitle("Simple IPFIX Viewer")

        headers = ["Title", "Description"]

        file = Path(__file__).parent / sys.argv[1]
        self.model = TreeModel(headers, file, self)

        if "-t" in sys.argv:
            QAbstractItemModelTester(self.model, self)
        self.view.setModel(self.model)
        self.view.expandAll()

        for column in range(self.model.columnCount()):
            self.view.resizeColumnToContents(column)
