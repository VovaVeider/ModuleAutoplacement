from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QPushButton, QTextEdit, QWidget
from workspace import Workspace
from position_item import PositionItem

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.length = None
        self.n = None
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.workspace = Workspace(self.central_widget)

        self.adjacency_matrix = []  # Матрица смежности
        self.positions_objects = []
        self.solution = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self.workspace)

        button = QPushButton("Добавить объект")
        button.setFixedSize(300,30)
        button_length1 = QPushButton("Найти суммарную длину связей для начальной схемы")
        button_length1.setFixedSize(400,30)
        button_length2 = QPushButton("Найти суммарную длину связей для конечной схемы")
        button_length2.setFixedSize(400, 30)
        self.length = QTextEdit()
        self.length.setFixedSize(300, 30)
        button.clicked.connect(self.add_object)
        button_length1.clicked.connect(self.display_length_1)
        button_length2.clicked.connect(self.display_length_2)

        solution = QPushButton("Решить")
        solution.clicked.connect(self.solute)
        solution.setFixedSize(300, 30)
        layout.addWidget(button)
        layout.addWidget(solution)
        layout.addWidget(button_length1)
        layout.addWidget(button_length2)
        layout.addWidget(self.length)
        self.central_widget.setLayout(layout)

    def add_object(self):
        # Пример добавления нового объекта на сцену
        x, y = 100, 100  # Координаты для нового объекта
        number = len(self.positions_objects) + 1
        element = number
        item = PositionItem(x, y, number, element, self.workspace)
        self.positions_objects.append(item)
        self.workspace.scene().addItem(item)

