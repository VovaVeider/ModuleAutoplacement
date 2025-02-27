from PySide6.QtGui import QPen, QBrush, Qt, QFont
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem
from settings import GRID_SPACING, POSITION_SIZE, rounded

class PositionItem(QGraphicsRectItem):
    def __init__(self, x, y, number, element, workspace):
        super(PositionItem, self).__init__()
        self.grid_spacing = GRID_SPACING
        self.size = POSITION_SIZE * self.grid_spacing
        self.setCursor(Qt.SizeAllCursor)

        self.workspace = workspace
        self.number = number
        self.element = element

        self.setRect(rounded(x), rounded(y), self.size, self.size)
        self.setPen(QPen(Qt.black))
        self.setBrush(QBrush(Qt.white))
