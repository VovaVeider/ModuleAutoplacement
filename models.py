"""
Models.py
Модуль, содержащий классы данных для схемы.
"""

from typing import Dict, List


class Node:
    """
    Node представляет узел схемы.

    Attributes:
        element_number (int): Уникальный номер узла (используется для матрицы смежности).
        grid_position (int): Порядковый номер узла в сетке (определяет расположение на холсте).
    """
    def __init__(self, element_number: int, grid_position: int) -> None:
        self.element_number = element_number
        self.grid_position = grid_position


class SchemaData:
    """
    Класс SchemaData хранит данные схемы:
    - nodes (Dict[int, Node]): словарь узлов (element_number -> Node)
    - adjacency_matrix (List[List[int]]): матрица смежности
    - cols, rows: размеры сетки
    """

    def __init__(self, nodes: Dict[int, Node], adjacency_matrix: List[List[int]],
                 cols: int, rows: int) -> None:
        self.nodes = nodes
        self.adjacency_matrix = adjacency_matrix
        self.cols = cols
        self.rows = rows

    def clone(self) -> "SchemaData":
        """
        Создаёт глубокую копию (clone) объекта SchemaData.
        1) Копируем все узлы (создавая новые объекты Node).
        2) Копируем матрицу смежности, если предполагается её менять.
           Иначе можно оставить ссылку, если матрица не будет изменяться.
        3) cols, rows копируем как есть (примитивные типы).
        """
        # Копируем узлы
        new_nodes = {
            num: Node(node.element_number, node.grid_position)
            for num, node in self.nodes.items()
        }
        # Копируем матрицу смежности (построчное копирование)
        new_matrix = [row[:] for row in self.adjacency_matrix]
        return SchemaData(new_nodes, new_matrix, self.cols, self.rows)