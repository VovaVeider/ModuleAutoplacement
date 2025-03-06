import logging
from tkinter import simpledialog, messagebox
from typing import Tuple, List, Set, Optional
from autoplacement.AbstractAutoPlacement import AbstractAutoPlacement
from autoplacement.utils import get_directive_nodes
from models import SchemaData, Node
import math

# Настройка логгера (при необходимости можно настроить формат, уровень и т.д.)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Если еще нет обработчиков, добавляем консольный (можно настроить в основном модуле)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


class SequentialConnectivityPlacement(AbstractAutoPlacement):
    """
    Последовательный алгоритм (3.3.*) с директивным вводом:
      - Пользователь вводит директивные пары "элемент,позиция; ..." – эти узлы фиксируются.
      - Узлы с grid_position == 0 (не директивные) размещаются последовательно,
        выбирая сначала модуль с максимальной оценкой J, затем позицию с минимальным F.
      - На вход алгоритму передается имя вкладки, для которой он запускается.
    """

    def get_name(self) -> str:
        return "Послед. алгоритм размещения по связности"

    def run(self, schema_data: SchemaData, tab_name: str) -> List[Tuple[SchemaData, str]]:
        cols, rows = schema_data.cols, schema_data.rows
        # Получаем директивно размещённые узлы; max_id = cols*rows
        placed_nodes = get_directive_nodes(cols * rows)
        if placed_nodes is None:
            return []

        # Создаем матрицу позиций (индексы с 0) для отслеживания размещения
        position_matrix: List[List[Optional[int]]] = [[None] * cols for _ in range(rows)]
        placed_nums: Set[int] = set()
        unplaced_nums: Set[int] = set()
        for node in placed_nodes:
            row, column = self._pos_to_rc(node.grid_position, rows, cols)
            position_matrix[row][column] = node.element_number
            placed_nums.add(node.element_number)

        # Все узлы, которых нет в placed_nums, считаем неразмещёнными
        for node in schema_data.nodes.values():
            if node.element_number not in placed_nums:
                unplaced_nums.add(node.element_number)

        # Последовательный алгоритм размещения для неразмещённых узлов
        while unplaced_nums:
            # Выбираем элемент с максимальным значением J (формула 3.3.1)
            max_j: Optional[int] = None
            selected_elem: Optional[int] = None
            for unplaced in unplaced_nums:
                cur_j = self._compute_J(
                    unplaced, placed_nums, unplaced_nums, schema_data.adjacency_matrix
                )
                logger.info(f"Элемент {unplaced} имеет J = {cur_j}")
                if selected_elem is None or cur_j > max_j:
                    selected_elem = unplaced
                    max_j = cur_j
            logger.info(f"Выбран элемент с max J: {selected_elem} (J = {max_j})")

            # Находим свободные соседние позиции (Rk)
            neighbors = self._find_neighbors_positions(placed_nodes, position_matrix, rows, cols)
            logger.info(f"Свободные соседние позиции: {neighbors}")

            best_pos: Optional[int] = None
            min_f: Optional[float] = None
            for pos_candidate in sorted(neighbors):
                cur_f = self._compute_F(
                    pos_candidate, selected_elem, placed_nodes,
                    schema_data.adjacency_matrix, rows, cols
                )
                if min_f is None or cur_f < min_f:
                    min_f = cur_f
                    best_pos = pos_candidate
            logger.info(f"Выбрана позиция: {best_pos} с F = {min_f}")

            # Размещаем выбранный элемент
            placed_nodes.append(Node(selected_elem, best_pos))
            placed_nums.add(selected_elem)
            unplaced_nums.remove(selected_elem)
            row, col = self._pos_to_rc(best_pos, rows, cols)
            position_matrix[row][col] = selected_elem
            logger.info("=" * 10)

        logger.info("Итоговая матрица позиций:")
        for r in position_matrix:
            logger.info(r)

        # Собираем новую модель данных на основе списка placed_nodes
        new_nodes = {node.element_number: node for node in placed_nodes}
        new_schema = SchemaData(new_nodes, schema_data.adjacency_matrix, cols, rows)
        return [(new_schema, f"{tab_name} послед. размещ.")]

    @staticmethod
    def _compute_J(element_number: int,
                   placed_nums: Set[int],
                   unplaced_nums: Set[int],
                   adjacency_matrix: List[List[int]]
                   ) -> int:
        """
        Вычисляет оценку J для элемента (формула 3.3.1):
            J = sum_{j in placed_nums} c(i,j) - sum_{j in unplaced_nums} c(i,j)
        """
        return (sum(adjacency_matrix[element_number - 1][p - 1] for p in placed_nums) -
                sum(adjacency_matrix[element_number - 1][u - 1] for u in unplaced_nums))

    def _compute_F(self, pos: int, elem_num: int, placed_nodes: List[Node],
                   adjacency_matrix: List[List[int]], rows: int, cols: int) -> float:
        """
        Вычисляет оценку F для элемента elem_num, если он разместится в позиции pos (формула 3.3.2):
            F = sum_{j in placed_nodes} c(i,j) * dist(pos, pos_j)
        где dist – манхэттенское расстояние между позициями.
        """
        cost = 0
        for node in placed_nodes:
            d = self._dist_positions(node.grid_position, pos, rows, cols)
            cost += adjacency_matrix[elem_num - 1][node.element_number - 1] * d
        return cost

    def _find_neighbors_positions(self, placed_nodes: List[Node],
                                  position_matrix: List[List[Optional[int]]],
                                  rows: int, cols: int) -> Set[int]:
        """
        Находит свободные позиции (Rk), соседние с занятыми.
        Соседняя позиция определяется как позиция, расстояние по манхэттену до занятой равно 1.
        """
        neighbors = set()
        for node in placed_nodes:
            r, c = self._pos_to_rc(node.grid_position, rows, cols)
            for dr, dc in ((0, 1), (1, 0), (-1, 0), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    if position_matrix[nr][nc] is None:
                        neighbors.add(self._rc_to_pos(nr, nc, cols))
        return neighbors

    def _dist_positions(self, pA: int, pB: int, rows: int, cols: int) -> int:
        """
        Вычисляет манхэттенское расстояние между позициями pA и pB.
        """
        rA, cA = self._pos_to_rc(pA, rows, cols)
        rB, cB = self._pos_to_rc(pB, rows, cols)
        return abs(rA - rB) + abs(cA - cB)

    def _pos_to_rc(self, pos: int, rows: int, cols: int) -> Tuple[int, int]:
        """
        Преобразует позицию (от 1 до rows*cols) в (row, col) с 0-индексацией.
        """
        p = pos - 1
        return (p // cols, p % cols)

    def _rc_to_pos(self, row: int, col: int, cols: int) -> int:
        """
        Преобразует (row, col) (с 0-индексацией) в позицию (от 1 до rows*cols).
        """
        return row * cols + col + 1
