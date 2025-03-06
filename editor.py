"""
editor.py
Модуль, содержащий класс SchemaEditor, отвечающий за отрисовку схемы на холсте и обработку событий.
"""

import math
import random
import tkinter as tk
from tkinter import simpledialog, messagebox
from typing import Dict, List, Optional, Tuple

from models import Node, SchemaData


class SchemaEditor:
    """
    SchemaEditor отвечает за отрисовку схемы (узлов и рёбер) и обработку событий мыши.

    Особенности:
      - Узлы хранятся по их element_number (для матрицы смежности).
      - Расположение узлов вычисляется по grid_position.
      - Рёбра отрисовываются для ячеек матрицы, где j > i (неориентированный граф).
      - Линии рисуются тёмными (цветовые компоненты от 0 до 150), а метки веса – через Label с фоном "lightgray".
      - Поддерживаются обработчики: левый клик (выбор узла), ПКМ (удаление/скрытие рёбер) и двойной клик (перемещение метки).

    Attributes:
      nodes (Dict[int, Node]): Узлы схемы.
      adjacency_matrix (List[List[int]]): Матрица смежности.
      cols (int): Количество колонок.
      rows (int): Количество строк.
      edges (List[Tuple[int, int, int, int, int]]): Список рёбер, каждый кортеж содержит
            (edge_obj, label_id, node1, node2, weight).
      selected_nodes (List[int]): Список выбранных узлов (element_number).
    """

    def __init__(self, parent: tk.Widget, schema_data: Optional[SchemaData] = None,
                 square_size: int = 50, font_size: int = 10, line_width: int = 2) -> None:
        self.parent = parent
        self.square_size = square_size
        self.font_size = font_size
        self.line_width = line_width
        self.current_file: Optional[str] = None

        self.nodes: Dict[int, Node] = {}
        self.edges: List[Tuple[int, int, int, int, int]] = []
        self.selected_nodes: List[int] = []
        self.edge_positions: Dict[Tuple[int, int], Tuple[int, int]] = {}
        self.edge_original_colors: Dict[int, str] = {}

        self.base_x = 100
        self.base_y = 100
        self.spacing_x = 100
        self.spacing_y = 100

        self.create_canvas()

        if schema_data:
            self.set_graph(schema_data)
        else:
            self.adjacency_matrix = []
            self.cols = 0
            self.rows = 0

        self.canvas.bind("<Button-1>", self.select_node)
        self.canvas.bind("<ButtonPress-3>", self.on_right_press)
        self.canvas.bind("<ButtonRelease-3>", self.on_right_release)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)

    def create_canvas(self) -> None:
        self.canvas = tk.Canvas(self.parent, bg="white", width=800, height=600,
                                scrollregion=(0, 0, 2000, 2000))
        hbar = tk.Scrollbar(self.parent, orient=tk.HORIZONTAL, command=self.canvas.xview)
        vbar = tk.Scrollbar(self.parent, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        hbar.pack(side=tk.BOTTOM, fill=tk.X)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

    def set_graph(self, schema_data: SchemaData) -> None:
        self.nodes.clear()
        for key, node in schema_data.nodes.items():
            self.nodes[node.element_number] = node
        self.adjacency_matrix = schema_data.adjacency_matrix
        self.cols = schema_data.cols
        self.rows = schema_data.rows
        self.edges.clear()
        self.create_graph()

    def set_adjacency_matrix(self, new_matrix: List[List[int]]) -> None:
        self.adjacency_matrix = new_matrix
        self.edges.clear()
        self.create_graph()

    def create_graph(self) -> None:
        self.canvas.delete("all")
        for node in self.nodes.values():
            self.add_node(node)
        for i, row in enumerate(self.adjacency_matrix):
            for j, weight in enumerate(row):
                if j > i and weight > 0:
                    if (i + 1) in self.nodes and (j + 1) in self.nodes:
                        self.create_edge_from_matrix(self.nodes[i + 1], self.nodes[j + 1], weight)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def add_node(self, node: Node) -> None:
        x, y = self.compute_node_position(node)
        half = self.square_size // 2
        self.canvas.create_rectangle(
            x - half, y - half, x + half, y + half,
            fill="white", outline="black", width=3, tags=str(node.element_number)
        )
        self.canvas.create_text(
            x, y, text=f"№{node.element_number}\nП-{node.grid_position}",
            font=("Arial", self.font_size), tags=str(node.element_number)
        )

    def compute_node_position(self, node: Node) -> Tuple[int, int]:
        index = node.grid_position - 1
        col = index % self.cols
        row = index // self.cols
        x = self.base_x + col * self.spacing_x
        y = self.base_y + row * self.spacing_y
        return (x, y)

    def select_node(self, event: tk.Event) -> None:
        click_x = self.canvas.canvasx(event.x)
        click_y = self.canvas.canvasy(event.y)
        for element, node in self.nodes.items():
            x, y = self.compute_node_position(node)
            half = self.square_size // 2
            if (x - half <= click_x <= x + half and y - half <= click_y <= y + half):
                if element not in self.selected_nodes:
                    self.selected_nodes.append(element)
                    print(f"Выбран узел: {element} (Позиция: {node.grid_position})")
                if len(self.selected_nodes) == 2:
                    self.create_edge()
                return

    def create_edge(self) -> None:
        if len(self.selected_nodes) < 2:
            return
        n1, n2 = self.selected_nodes
        if any(e[2] == n1 and e[3] == n2 or e[2] == n2 and e[3] == n1 for e in self.edges):
            messagebox.showwarning("Ошибка", "Эти узлы уже соединены!")
            self.selected_nodes.clear()
            return
        weight: Optional[int] = simpledialog.askinteger("Вес связи", "Введите вес связи:")
        if weight is not None:
            self.adjacency_matrix[n1 - 1][n2 - 1] = weight
            self.adjacency_matrix[n2 - 1][n1 - 1] = weight
            self.create_edge_from_matrix(self.nodes[n1], self.nodes[n2], weight)
        self.selected_nodes.clear()

    def create_edge_from_matrix(self, node1: Node, node2: Node, weight: int) -> None:
        x1, y1 = self.get_closest_edge_position(node1, node2)
        x2, y2 = self.get_closest_edge_position(node2, node1)
        base_color: str = f"#{random.randint(0, 150):02x}{random.randint(0, 150):02x}{random.randint(0, 150):02x}"
        edge_obj: int = self.canvas.create_line(x1, y1, x2, y2, width=self.line_width, fill=base_color)
        self.edge_original_colors[edge_obj] = base_color
        text_x: int = (x1 + x2) // 2
        text_y: int = (y1 + y2) // 2
        label: tk.Label = tk.Label(self.canvas, text=str(weight),
                                   font=("Arial", self.font_size + 2, "bold"),
                                   fg=base_color, bg="lightgray", bd=0, highlightthickness=0)
        label_id: int = self.canvas.create_window(text_x, text_y, window=label)
        self.edges.append((edge_obj, label_id, node1.element_number, node2.element_number, weight))
        self.edge_positions[(node1.element_number, node2.element_number)] = (text_x, text_y)
        for element, node in self.nodes.items():
            if element in (node1.element_number, node2.element_number):
                continue
            nx, ny = self.compute_node_position(node)
            half = self.square_size // 2
            rx1: int = nx - half
            ry1: int = ny - half
            rx2: int = nx + half
            ry2: int = ny + half
            inter: Optional[Tuple[float, float, float, float]] = self.get_line_rect_intersection(
                x1, y1, x2, y2, rx1, ry1, rx2, ry2
            )
            if inter is not None:
                ix1, iy1, ix2, iy2 = inter
                dashed_color: str = self._lighten_color(base_color, 0.3)
                self.canvas.create_line(ix1, iy1, ix2, iy2,
                                        width=self.line_width,
                                        fill=dashed_color, dash=(5, 5))

    def get_closest_edge_position(self, nodeA: Node, nodeB: Node) -> Tuple[int, int]:
        xA, yA = self.compute_node_position(nodeA)
        xB, yB = self.compute_node_position(nodeB)
        half: int = self.square_size // 2
        dx: int = xB - xA
        dy: int = yB - yA
        if abs(dx) > abs(dy):
            return (xA + half, yA) if dx > 0 else (xA - half, yA)
        else:
            return (xA, yA + half) if dy > 0 else (xA, yA - half)

    def get_line_rect_intersection(self, x1: float, y1: float, x2: float, y2: float,
                                   rx1: float, ry1: float, rx2: float, ry2: float) -> Optional[Tuple[float, float, float, float]]:
        dx: float = x2 - x1
        dy: float = y2 - y1
        u1: float = 0.0
        u2: float = 1.0
        p: List[float] = [-dx, dx, -dy, dy]
        q: List[float] = [x1 - rx1, rx2 - x1, y1 - ry1, ry2 - y1]
        for i in range(4):
            if p[i] == 0:
                if q[i] < 0:
                    return None
            else:
                t: float = q[i] / p[i]
                if p[i] < 0:
                    u1 = max(u1, t)
                else:
                    u2 = min(u2, t)
        if u1 > u2:
            return None
        ix1: float = x1 + u1 * dx
        iy1: float = y1 + u1 * dy
        ix2: float = x1 + u2 * dx
        iy2: float = y1 + u2 * dy
        return (ix1, iy1, ix2, iy2)

    def _lighten_color(self, hex_color: str, factor: float) -> str:
        hex_color = hex_color.lstrip('#')
        r: int = int(hex_color[0:2], 16)
        g: int = int(hex_color[2:4], 16)
        b: int = int(hex_color[4:6], 16)
        r = int(r + (255 - r) * factor)
        g = int(g + (255 - g) * factor)
        b = int(b + (255 - b) * factor)
        return f"#{r:02x}{g:02x}{b:02x}"

    def highlight_edges(self, node_label: Optional[int] = None) -> None:
        for edge_obj, label_id, n1, n2, _ in self.edges:
            self.canvas.itemconfigure(edge_obj, state='normal')
            self.canvas.itemconfigure(label_id, state='normal')
        if node_label is not None:
            for edge_obj, label_id, n1, n2, _ in self.edges:
                if n1 != node_label and n2 != node_label:
                    self.canvas.itemconfigure(edge_obj, state='hidden')
                    self.canvas.itemconfigure(label_id, state='hidden')

    def on_right_press(self, event: tk.Event) -> None:
        px: int = self.canvas.canvasx(event.x)
        py: int = self.canvas.canvasy(event.y)
        TOL: int = 5
        for edge_obj, label_id, n1, n2, weight in self.edges:
            x1, y1 = self.get_closest_edge_position(self.nodes[n1], self.nodes[n2])
            x2, y2 = self.get_closest_edge_position(self.nodes[n2], self.nodes[n1])
            dist: float = self.dist_point_segment(px, py, x1, y1, x2, y2)
            if dist <= TOL:
                if tk.messagebox.askyesno("Подтверждение", f"Удалить связь между {n1} и {n2} (вес {weight})?"):
                    self.canvas.delete(edge_obj)
                    self.canvas.delete(label_id)
                    self.edges.remove((edge_obj, label_id, n1, n2, weight))
                    self.adjacency_matrix[n1 - 1][n2 - 1] = 0
                    self.adjacency_matrix[n2 - 1][n1 - 1] = 0
                    if (n1, n2) in self.edge_positions:
                        del self.edge_positions[(n1, n2)]
                return
        found_node: Optional[int] = None
        for element, node in self.nodes.items():
            x, y = self.compute_node_position(node)
            half: int = self.square_size // 2
            if (x - half <= px <= x + half and y - half <= py <= y + half):
                found_node = element
                break
        if found_node is not None:
            self.highlight_edges(found_node)
        else:
            self.highlight_edges(None)

    def on_right_release(self, event: tk.Event) -> None:
        self.highlight_edges(None)

    def dist_point_segment(self, px: float, py: float, x1: float, y1: float, x2: float, y2: float) -> float:
        dx: float = x2 - x1
        dy: float = y2 - y1
        if dx == 0 and dy == 0:
            return math.hypot(px - x1, py - y1)
        t: float = ((px - x1) * dx + (py - y1) * dy) / float(dx * dx + dy * dy)
        if t < 0:
            return math.hypot(px - x1, py - y1)
        elif t > 1:
            return math.hypot(px - x2, py - y2)
        else:
            projx: float = x1 + t * dx
            projy: float = y1 + t * dy
            return math.hypot(px - projx, py - projy)

    def on_double_click(self, event: tk.Event) -> None:
        px: int = self.canvas.canvasx(event.x)
        py: int = self.canvas.canvasy(event.y)
        TOL_dbl: int = 15
        for edge_obj, label_id, n1, n2, weight in self.edges:
            x1, y1 = self.get_closest_edge_position(self.nodes[n1], self.nodes[n2])
            x2, y2 = self.get_closest_edge_position(self.nodes[n2], self.nodes[n1])
            dist: float = self.dist_point_segment(px, py, x1, y1, x2, y2)
            if dist <= TOL_dbl:
                self.canvas.coords(label_id, px, py)
                self.edge_positions[(n1, n2)] = (px, py)
                break
