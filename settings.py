import random
from PySide6.QtGui import QColor

SCENE_WIDTH = 2000
SCENE_HEIGHT = 1000
GRID_SPACING = 15
POSITION_SIZE = 5

def rounded(coord):
    return round(coord / GRID_SPACING) * GRID_SPACING

def random_color():
    predefined_colors = [
        QColor("red"), QColor("green"), QColor("blue"), QColor("yellow"),
        QColor("purple"), QColor("orange"), QColor("pink"), QColor("cyan"),
        QColor("brown"), QColor("black"), QColor("#ffd700"), QColor("gray"),
    ]
    return random.choice(predefined_colors)
