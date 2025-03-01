"""
Models.py
Модуль, содержащий классы данных для схемы.
"""

from typing import Dict

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
    SchemaData хранит данные схемы: узлы, матрица связей и размеры сетки.

    Attributes:
        nodes (Dict[int, Node]): Словарь узлов, где ключ – element_number.
        adjacency_matrix (List[List[int]]): Матрица смежности (строки соответствуют узлам с element_number - 1).
        cols (int): Количество колонок в сетке.
        rows (int): Количество строк в сетке.
    """
    def __init__(self, nodes: Dict[int, Node], adjacency_matrix: list, cols: int, rows: int) -> None:
        self.nodes = nodes
        self.adjacency_matrix = adjacency_matrix
        self.cols = cols
        self.rows = rows
