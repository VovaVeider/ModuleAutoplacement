from PySide6.QtGui import QPen, QPainterPath, QFont, QColor
from PySide6.QtWidgets import QGraphicsPathItem, QGraphicsTextItem
from settings import rounded
import random

class Connection(QGraphicsPathItem):
    def __init__(self, start_pos, end_pos, weight, workspace, connectors):
        color = self.random_color()
        self.start_pos = start_pos
        super(Connection, self).__init__()
        self.path = QPainterPath()
        self.path.moveTo(self.start_pos)
        self.scene = workspace.scene()
        self.main_window = workspace.main_window
        self.setPen(QPen(color, 1.75))
        self.scene.addItem(self)
        self.connectors = connectors

    def random_color(self):
        colors = ["red", "green", "blue", "yellow", "purple", "orange", "pink", "cyan", "brown", "black"]
        return QColor(random.choice(colors))
