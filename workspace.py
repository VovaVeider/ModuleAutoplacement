from PySide6.QtGui import QPainter, QPen, Qt
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QInputDialog
from connection import Connection
from settings import GRID_SPACING, SCENE_WIDTH, SCENE_HEIGHT

class Workspace(QGraphicsView):
    def __init__(self, parent):
        super(Workspace, self).__init__(parent)
        self.setScene(QGraphicsScene(self))
        self.setSceneRect(0, 0, SCENE_WIDTH, SCENE_HEIGHT)
        self.setRenderHint(QPainter.Antialiasing)
        self.main_window = None
        self.selected_connectors = []

    def prepare_connection(self, connector):
        if self.selected_connectors.__contains__(connector):
            return
        self.selected_connectors.append(connector)
        if len(self.selected_connectors) == 2:
            connector1 = self.selected_connectors[0]
            connector2 = self.selected_connectors[1]

            if connector1.parentItem() == connector2.parentItem():
                self.selected_connectors = []
                return

            el1 = connector1.parentItem().element
            el2 = connector2.parentItem().element

            if self.main_window.adjacency_matrix[el1][el2] != 0:
                self.selected_connectors = []
                return

            weight, ok = QInputDialog.getInt(self, "Введите вес связи", "Вес связи:")
            if ok:
                self.make_connection(connector1, connector2, weight)

            self.selected_connectors = []
