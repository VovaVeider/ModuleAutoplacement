import tkinter as tk
import math
import random
import json
from tkinter import simpledialog, messagebox, filedialog
from tkinter import ttk


# =============================================================================
# КЛАСС Node
# =============================================================================
class Node:
    """
    Класс Node представляет узел схемы.

    Attributes:
        element_number (int): Номер элемента (идентификатор узла).
        grid_position (int): Порядковый номер узла в сетке (отсчитанный слева направо, сверху вниз).
    """

    def __init__(self, element_number, grid_position):
        self.element_number = element_number  # Например, 1, 2, 3, ...
        self.grid_position = grid_position  # Порядковый номер в сетке (используется для вычисления позиции)


# =============================================================================
# КЛАСС SchemaData
# =============================================================================
class SchemaData:
    """
    Класс SchemaData хранит данные схемы, такие как узлы, матрица связей и размеры сетки.

    Attributes:
        nodes (dict): Словарь узлов; ключ – номер узла, значение – объект Node.
        adjacency_matrix (list): Матрица смежности для описания связей между узлами.
        cols (int): Количество колонок в сетке.
        rows (int): Количество строк в сетке.
    """

    def __init__(self, nodes, adjacency_matrix, cols, rows):
        self.nodes = nodes  # Сохраняем словарь узлов
        self.adjacency_matrix = adjacency_matrix  # Сохраняем матрицу связей
        self.cols = cols  # Количество колонок
        self.rows = rows  # Количество строк


# =============================================================================
# КЛАСС SchemaEditor
# =============================================================================
class SchemaEditor:
    """
    SchemaEditor отвечает за отрисовку схемы (узлов и связей) на холсте и обработку событий мыши.

    Помимо стандартных событий (одинарный клик, ПКМ) добавлена обработка двойного клика ЛКМ:
    при двойном клике на ребро текст с весом перемещается в точку клика.

    Args:
        parent (tk.Widget): Родительский виджет (фрейм вкладки).
        schema_data (SchemaData, optional): Данные схемы для инициализации.
        square_size (int, optional): Размер квадрата, представляющего узел.
        font_size (int, optional): Размер шрифта для текста узла.
        line_width (int, optional): Толщина линий для ребер.
    """

    def __init__(self, parent, schema_data=None, square_size=50, font_size=10, line_width=2):
        self.parent = parent
        self.square_size = square_size
        self.font_size = font_size
        self.line_width = line_width
        self.current_file = None

        # Списки для хранения отрисованных объектов схемы
        self.edges = []  # Список ребер: (edge_obj, text_obj, node1, node2, weight)
        self.selected_nodes = []  # Список выбранных узлов для создания ребра
        self.edge_positions = {}  # Словарь для хранения позиций текста ребра
        self.text_positions = set()  # Для предотвращения наложения текста (при необходимости)

        # Параметры для вычисления координат узлов в сетке
        self.base_x = 100  # Начальное смещение по X
        self.base_y = 100  # Начальное смещение по Y
        self.spacing_x = 100  # Расстояние между узлами по горизонтали
        self.spacing_y = 100  # Расстояние между узлами по вертикали

        self.create_canvas()

        if schema_data:
            self.set_graph(schema_data)
        else:
            self.nodes = {}
            self.adjacency_matrix = []
            self.cols = 0
            self.rows = 0

        # Привязываем обработчики событий:
        self.canvas.bind("<Button-1>", self.select_node)
        self.canvas.bind("<ButtonPress-3>", self.on_right_press)
        self.canvas.bind("<ButtonRelease-3>", self.on_right_release)
        # Добавляем обработчик двойного клика для перемещения текста веса ребра
        self.canvas.bind("<Double-Button-1>", self.on_double_click)

    def compute_node_position(self, node):
        """
        Вычисляет координаты узла на холсте, исходя из его grid_position и размеров сетки.

        Args:
            node (Node): Объект узла.

        Returns:
            tuple: (x, y) координаты узла.
        """
        index = node.grid_position - 1  # Переводим порядковый номер в индекс (начиная с 0)
        col = index % self.cols  # Определяем номер столбца
        row = index // self.cols  # Определяем номер строки
        x = self.base_x + col * self.spacing_x  # Координата X = базовое смещение + сдвиг по колонкам
        y = self.base_y + row * self.spacing_y  # Координата Y = базовое смещение + сдвиг по строкам
        return (x, y)

    def create_canvas(self):
        """
        Создает холст для отрисовки схемы и настраивает полосы прокрутки.
        """
        self.canvas = tk.Canvas(self.parent, bg="white", width=800, height=600,
                                scrollregion=(0, 0, 2000, 2000))
        hbar = tk.Scrollbar(self.parent, orient=tk.HORIZONTAL, command=self.canvas.xview)
        vbar = tk.Scrollbar(self.parent, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        hbar.pack(side=tk.BOTTOM, fill=tk.X)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

    def create_graph(self):
        """
        Очищает холст и отрисовывает узлы и ребра по матрице смежности.
        """
        self.canvas.delete("all")
        for node in self.nodes.values():
            self.add_node(node)
        for i, row in enumerate(self.adjacency_matrix):
            for j, weight in enumerate(row):
                if weight > 0 and (i + 1) in self.nodes and (j + 1) in self.nodes:
                    self.create_edge_from_matrix(self.nodes[i + 1], self.nodes[j + 1], weight)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def set_adjacency_matrix(self, new_matrix):
        """
        Обновляет матрицу смежности и перерисовывает схему.

        Args:
            new_matrix (list): Новая матрица связей.
        """
        self.adjacency_matrix = new_matrix
        self.edges.clear()
        self.create_graph()

    def set_graph(self, schema_data):
        """
        Устанавливает данные схемы и перерисовывает её.

        Args:
            schema_data (SchemaData): Данные схемы.
        """
        self.nodes = schema_data.nodes
        self.adjacency_matrix = schema_data.adjacency_matrix
        self.cols = schema_data.cols
        self.rows = schema_data.rows
        self.edges.clear()
        self.create_graph()

    def add_node(self, node):
        """
        Отрисовывает узел на холсте: квадрат и текст внутри него.

        Args:
            node (Node): Объект узла.
        """
        x, y = self.compute_node_position(node)
        half_size = self.square_size // 2
        element_number = node.element_number
        # Рисуем квадрат
        self.canvas.create_rectangle(
            x - half_size, y - half_size,
            x + half_size, y + half_size,
            fill="white", outline="black", width=3,
            tags=str(element_number)
        )
        # Рисуем текст с номером и позицией узла
        self.canvas.create_text(
            x, y,
            text=f"№{node.element_number}\nП-{node.grid_position}",
            font=("Arial", self.font_size),
            tags=str(element_number)
        )
        self.nodes[element_number] = node

    def select_node(self, event):
        """
        Обрабатывает левый клик по холсту. Определяет, по какому узлу был произведён клик,
        и если выбраны два узла, инициирует создание ребра.

        Args:
            event: Событие Tkinter с координатами клика.
        """
        click_x = self.canvas.canvasx(event.x)
        click_y = self.canvas.canvasy(event.y)
        for label, node in self.nodes.items():
            x, y = self.compute_node_position(node)
            half_size = self.square_size // 2
            if (x - half_size <= click_x <= x + half_size and
                    y - half_size <= click_y <= y + half_size):
                if label not in self.selected_nodes:
                    self.selected_nodes.append(label)
                    print(f"Выбран элемент: {label}")
                if len(self.selected_nodes) == 2:
                    self.create_edge()
                return

    def create_edge(self):
        """
        Создает ребро между двумя выбранными узлами:
        - Проверяет, существует ли уже связь.
        - Запрашивает вес.
        - Обновляет матрицу связей.
        - Отрисовывает ребро.
        """
        if len(self.selected_nodes) < 2:
            return
        node1, node2 = self.selected_nodes
        if any(e[2] == node1 and e[3] == node2 or e[2] == node2 and e[3] == node1 for e in self.edges):
            messagebox.showwarning("Ошибка", "Эти узлы уже соединены!")
            self.selected_nodes.clear()
            return
        weight = simpledialog.askinteger("Вес связи", "Введите вес связи:")
        if weight is not None:
            self.adjacency_matrix[node1 - 1][node2 - 1] = weight
            self.adjacency_matrix[node2 - 1][node1 - 1] = weight
            self.create_edge_from_matrix(self.nodes[node1], self.nodes[node2], weight)
        self.selected_nodes.clear()

    def create_edge_from_matrix(self, node1, node2, weight):
        """
        Отрисовывает ребро между двумя узлами на основе вычисленных координат и добавляет текст с весом.

        Args:
            node1 (Node): Первый узел.
            node2 (Node): Второй узел.
            weight (int): Вес ребра.
        """
        # Вычисляем точку на краю первого узла, ближайшую к второму узлу
        x1, y1 = self.get_closest_edge_position(node1, node2)
        # Аналогично, вычисляем точку на краю второго узла
        x2, y2 = self.get_closest_edge_position(node2, node1)
        # Генерируем случайный цвет для линии
        color = f"#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}"
        edge = self.canvas.create_line(x1, y1, x2, y2, width=self.line_width, fill=color)
        # Текст размещается по середине линии
        text_x, text_y = (x1 + x2) // 2, (y1 + y2) // 2
        text = self.canvas.create_text(text_x, text_y, text=str(weight),
                                       font=("Arial", self.font_size + 2, "bold"), fill=color)
        self.edges.append((edge, text, node1.element_number, node2.element_number, weight))
        self.edge_positions[(node1.element_number, node2.element_number)] = (text_x, text_y)

    def get_closest_edge_position(self, nodeA, nodeB):
        """
        Вычисляет точку на границе узла nodeA, ближайшую к узлу nodeB.

        Идея: Нужно, чтобы линия ребра начиналась не из центра узла, а с его стороны,
        которая ближе к другому узлу.
          - Вычисляем центр узла nodeA.
          - Сравниваем разницу по X и Y с центром nodeB.
          - Если разница по X больше, выбираем правую или левую сторону.
          - Иначе выбираем верхнюю или нижнюю сторону.

        Args:
            nodeA (Node): Узел, от которого начинается линия.
            nodeB (Node): Узел, к которому направлена линия.

        Returns:
            tuple: (x, y) координаты на границе узла nodeA.
        """
        xA, yA = self.compute_node_position(nodeA)
        xB, yB = self.compute_node_position(nodeB)
        half_size = self.square_size // 2
        dx = xB - xA
        dy = yB - yA
        if abs(dx) > abs(dy):
            return (xA + half_size, yA) if dx > 0 else (xA - half_size, yA)
        else:
            return (xA, yA + half_size) if dy > 0 else (xA, yA - half_size)

    def highlight_edges(self, node_label=None):
        """
        Делает все ребра видимыми; если задан node_label, скрывает те ребра,
        которые не связаны с указанным узлом.

        Args:
            node_label (int, optional): Номер узла для фильтрации ребер.
        """
        for edge, text, n1, n2, _ in self.edges:
            self.canvas.itemconfigure(edge, state='normal')
            self.canvas.itemconfigure(text, state='normal')
        if node_label is not None:
            for edge, text, n1, n2, _ in self.edges:
                if n1 != node_label and n2 != node_label:
                    self.canvas.itemconfigure(edge, state='hidden')
                    self.canvas.itemconfigure(text, state='hidden')

    def on_right_press(self, event):
        """
        Обрабатывает правый клик по холсту. Если клик происходит по линии ребра (с допуском TOL),
        запрашивает подтверждение на удаление ребра, иначе выделяет узел.

        Args:
            event: Событие Tkinter.
        """
        px = self.canvas.canvasx(event.x)
        py = self.canvas.canvasy(event.y)
        TOL = 5  # Допустимое отклонение для определения попадания в линию
        for (edge_obj, text_obj, node1, node2, weight) in self.edges:
            x1, y1 = self.get_closest_edge_position(self.nodes[node1], self.nodes[node2])
            x2, y2 = self.get_closest_edge_position(self.nodes[node2], self.nodes[node1])
            dist = self.dist_point_segment(px, py, x1, y1, x2, y2)
            if dist <= TOL:
                if messagebox.askyesno("Подтверждение", f"Удалить связь между {node1} и {node2} (вес {weight})?"):
                    self.canvas.delete(edge_obj)
                    self.canvas.delete(text_obj)
                    self.edges.remove((edge_obj, text_obj, node1, node2, weight))
                    self.adjacency_matrix[node1 - 1][node2 - 1] = 0
                    self.adjacency_matrix[node2 - 1][node1 - 1] = 0
                    if (node1, node2) in self.edge_positions:
                        del self.edge_positions[(node1, node2)]
                return
        # Если клик не по линии, ищем, по какому узлу произведен клик
        found_node = None
        for label, node in self.nodes.items():
            x, y = self.compute_node_position(node)
            half_size = self.square_size // 2
            if (x - half_size <= px <= x + half_size and y - half_size <= py <= y + half_size):
                found_node = label
                break
        if found_node is not None:
            self.highlight_edges(found_node)
        else:
            self.highlight_edges(None)

    def on_right_release(self, event):
        """
        При отпускании правой кнопки мыши возвращает все ребра в видимое состояние.
        """
        self.highlight_edges(None)

    def dist_point_segment(self, px, py, x1, y1, x2, y2):
        """
        Вычисляет расстояние от точки (px, py) до отрезка, заданного конечными точками (x1, y1) и (x2, y2).

        Returns:
            float: Расстояние от точки до отрезка.
        """
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0 and dy == 0:
            return math.hypot(px - x1, py - y1)
        t = ((px - x1) * dx + (py - y1) * dy) / float(dx * dx + dy * dy)
        if t < 0:
            return math.hypot(px - x1, py - y1)
        elif t > 1:
            return math.hypot(px - x2, py - y2)
        else:
            projx = x1 + t * dx
            projy = y1 + t * dy
            return math.hypot(px - projx, py - projy)

    def on_double_click(self, event):
        """
        Обрабатывает двойной клик ЛКМ по холсту.
        Если клик происходит вблизи линии ребра (с допуском TOL_dbl),
        перемещает текст с весом ребра (label) в точку клика.

        Args:
            event: Событие двойного клика Tkinter.
        """
        px = self.canvas.canvasx(event.x)
        py = self.canvas.canvasy(event.y)
        TOL_dbl = 10  # Допуск для определения попадания по ребру при двойном клике
        for (edge_obj, text_obj, node1, node2, weight) in self.edges:
            # Вычисляем точки на границах узлов для текущего ребра
            x1, y1 = self.get_closest_edge_position(self.nodes[node1], self.nodes[node2])
            x2, y2 = self.get_closest_edge_position(self.nodes[node2], self.nodes[node1])
            # Вычисляем расстояние от точки клика до отрезка ребра
            dist = self.dist_point_segment(px, py, x1, y1, x2, y2)
            if dist <= TOL_dbl:
                # Если точка клика достаточно близко, перемещаем текст с весом в эту точку
                self.canvas.coords(text_obj, px, py)
                # Обновляем сохраненную позицию текста в словаре edge_positions
                self.edge_positions[(node1, node2)] = (px, py)
                break

    # Добавляем привязку двойного клика в конструкторе (__init__) вызовом self.canvas.bind("<Double-Button-1>", self.on_double_click)


# =============================================================================
# КЛАСС TabManager
# =============================================================================
class TabManager:
    """
    TabManager управляет вкладками, каждая из которых содержит экземпляр SchemaEditor.
    Обеспечивает создание вкладки с символом "+" и обработку событий создания, переименования и удаления вкладок.

    Attributes:
        notebook (ttk.Notebook): Виджет, реализующий систему вкладок.
        tabs (dict): Словарь, сопоставляющий идентификатор вкладки (фрейм) с экземпляром SchemaEditor.
        plus_tab_id (str): Идентификатор вкладки с символом "+".
        last_tab (str): Идентификатор последней выбранной вкладки (не "+"), для возврата фокуса.
    """

    def __init__(self, master):
        self.master = master
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.tabs = {}
        self.plus_tab_id = None
        self.last_tab = None  # Запоминаем последний выбранный таб (не "+")
        first_tab = self.create_new_tab(initial=True)  # Создаем первую вкладку
        if first_tab is not None:
            self.last_tab = str(first_tab)
        self.add_plus_tab()
        self.notebook.bind("<Button-1>", self.on_notebook_click)
        self.notebook.bind("<Button-3>", self.on_tab_right_click)

    def create_new_tab(self, initial=False):
        """
        Создает новую вкладку.
        Если initial==True, имя вкладки фиксированное ("безымянный").
        Если initial==False, запрашивается имя вкладки.
        Если пользователь отменяет ввод, возвращается None.

        Returns:
            Фрейм вкладки или None.
        """
        if initial:
            tab_name = "безымянный"
        else:
            tab_name = simpledialog.askstring("Новая вкладка", "Введите имя новой вкладки:")
            if tab_name is None or tab_name.strip() == "":
                return None
        frame = tk.Frame(self.notebook)
        cols, rows = 3, 3
        num_nodes = cols * rows
        nodes = {i + 1: Node(i + 1, i + 1) for i in range(num_nodes)}
        adjacency_matrix = [[0] * num_nodes for _ in range(num_nodes)]
        schema_data = SchemaData(nodes, adjacency_matrix, cols, rows)
        editor = SchemaEditor(frame, schema_data=schema_data)
        # Привязываем двойной клик для перемещения веса ребра в редакторе (обратите внимание: внутри SchemaEditor уже есть привязка)
        self.notebook.add(frame, text=tab_name)
        self.tabs[str(frame)] = editor
        return frame

    def add_plus_tab(self):
        """
        Добавляет вкладку с символом "+" для создания новых вкладок.
        """
        frame = tk.Frame(self.notebook)
        self.plus_tab_id = str(frame)
        self.notebook.add(frame, text="+")

    def on_notebook_click(self, event):
        """
        Обрабатывает левый клик по вкладкам.
        Если клик по вкладке с "+" – запоминает текущую вкладку и запрашивает имя новой.
        При отмене ввода фокус возвращается на сохранённую вкладку, и новая вкладка не создается.
        """
        try:
            tab_index = self.notebook.index(f"@{event.x},{event.y}")
            tab_id = self.notebook.tabs()[tab_index]
        except Exception:
            return
        if self.notebook.tab(tab_id, "text") != "+":
            self.last_tab = tab_id  # Запоминаем текущую вкладку, если это не "+"
            return
        current = self.notebook.select()
        if current != self.plus_tab_id:
            self.last_tab = current
        new_name = simpledialog.askstring("Новая вкладка", "Введите имя новой вкладки:")
        self.notebook.forget(self.plus_tab_id)  # Удаляем вкладку "+"
        if new_name is None or new_name.strip() == "":
            # Если ввод отменен, возвращаемся на последнюю выбранную вкладку
            if self.last_tab is not None:
                self.notebook.select(self.last_tab)
            self.add_plus_tab()
            return
        new_tab = self.create_new_tab_with_name(new_name)
        if new_tab is not None:
            self.notebook.select(new_tab)
            self.last_tab = str(new_tab)
        self.add_plus_tab()

    def create_new_tab_with_name(self, tab_name):
        """
        Создает новую вкладку с заданным именем.

        Args:
            tab_name (str): Имя новой вкладки.

        Returns:
            Фрейм вкладки.
        """
        frame = tk.Frame(self.notebook)
        cols, rows = 3, 3
        num_nodes = cols * rows
        nodes = {i + 1: Node(i + 1, i + 1) for i in range(num_nodes)}
        adjacency_matrix = [[0] * num_nodes for _ in range(num_nodes)]
        schema_data = SchemaData(nodes, adjacency_matrix, cols, rows)
        editor = SchemaEditor(frame, schema_data=schema_data)
        self.notebook.add(frame, text=tab_name)
        self.tabs[str(frame)] = editor
        return frame

    def on_tab_right_click(self, event):
        """
        Обрабатывает правый клик по вкладкам и показывает контекстное меню с опциями "Переименовать" и "Удалить".
        """
        try:
            tab_index = self.notebook.index(f"@{event.x},{event.y}")
            tab_id = self.notebook.tabs()[tab_index]
        except Exception:
            return
        if self.notebook.tab(tab_id, "text") == "+":
            return
        menu = tk.Menu(self.notebook, tearoff=0)
        menu.add_command(label="Переименовать", command=lambda: self.rename_tab(tab_id))
        menu.add_command(label="Удалить", command=lambda: self.delete_tab(tab_id))
        menu.tk_popup(event.x_root, event.y_root)

    def delete_tab(self, tab_id):
        """
        Удаляет вкладку, если их больше одной (без учета вкладки "+").
        Запрашивает подтверждение, и если вкладка удаляется, переключает фокус на оставшуюся вкладку.
        """
        if len(self.tabs) <= 1:
            messagebox.showwarning("Ошибка", "Нельзя удалить последнюю вкладку!")
            return
        if messagebox.askyesno("Подтверждение", "Удалить вкладку?"):
            self.notebook.forget(tab_id)
            if tab_id in self.tabs:
                del self.tabs[tab_id]
            remaining = list(self.tabs.keys())
            if remaining:
                self.notebook.select(remaining[0])
                self.last_tab = remaining[0]

    def rename_tab(self, tab_id):
        """
        Позволяет переименовать вкладку, запрашивая новое имя у пользователя.

        Args:
            tab_id (str): Идентификатор вкладки.
        """
        new_name = simpledialog.askstring("Переименовать вкладку", "Введите новое имя вкладки:")
        if new_name:
            self.notebook.tab(tab_id, text=new_name)

    def get_current_editor(self):
        """
        Возвращает экземпляр SchemaEditor для текущей выбранной вкладки.

        Returns:
            SchemaEditor или None, если текущая вкладка не содержит редактор.
        """
        current_tab = self.notebook.select()
        if current_tab in self.tabs:
            return self.tabs[current_tab]
        return None


# =============================================================================
# КЛАСС GlobalMenu
# =============================================================================
class GlobalMenu:
    """
    GlobalMenu реализует глобальное меню приложения, работающее с текущей вкладкой.
    """

    def __init__(self, master, tab_manager):
        self.tab_manager = tab_manager
        menu_bar = tk.Menu(master)
        master.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Открыть", command=self.open_file)
        file_menu.add_command(label="Сохранить", command=self.save_file)
        file_menu.add_command(label="Сохранить как", command=self.save_as_file)
        menu_bar.add_cascade(label="Файл", menu=file_menu)

        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Удалить все связи", command=self.clear_edges)
        edit_menu.add_command(label="Новая схема", command=self.new_schema)
        menu_bar.add_cascade(label="Изменить", menu=edit_menu)

        auto_menu = tk.Menu(menu_bar, tearoff=0)
        auto_menu.add_command(label="Размещение по связности", command=self.arrange_by_connectivity)
        auto_menu.add_command(label="Парные перестановки", command=self.pair_swaps)
        menu_bar.add_cascade(label="Авторазмещение", menu=auto_menu)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="О программе", command=self.about)
        menu_bar.add_cascade(label="Справка", menu=help_menu)

    def get_current_editor(self):
        return self.tab_manager.get_current_editor()

    def open_file(self):
        editor = self.get_current_editor()
        if not editor:
            return
        filename = filedialog.askopenfilename(title="Открыть файл",
                                              filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")])
        if filename:
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
                cols = data.get("cols", 0)
                rows = data.get("rows", 0)
                nodes_data = data.get("nodes", {})
                nodes = {}
                for key, node_info in nodes_data.items():
                    element_number = node_info["element_number"]
                    grid_position = node_info["grid_position"]
                    nodes[element_number] = Node(element_number, grid_position)
                adjacency_matrix = data.get("adjacency_matrix", [])
                schema_data = SchemaData(nodes, adjacency_matrix, cols, rows)
                editor.set_graph(schema_data)
                editor.current_file = filename
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{e}")

    def save_file(self):
        editor = self.get_current_editor()
        if not editor:
            return
        if editor.current_file:
            self._save_to_file(editor.current_file, editor)
        else:
            self.save_as_file()

    def save_as_file(self):
        editor = self.get_current_editor()
        if not editor:
            return
        filename = filedialog.asksaveasfilename(title="Сохранить как",
                                                defaultextension=".json",
                                                filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")])
        if filename:
            editor.current_file = filename
            self._save_to_file(filename, editor)

    def _save_to_file(self, filename, editor):
        try:
            nodes_data = {}
            for element_number, node in editor.nodes.items():
                nodes_data[element_number] = {
                    "element_number": node.element_number,
                    "grid_position": node.grid_position
                }
            data = {
                "cols": editor.cols,
                "rows": editor.rows,
                "nodes": nodes_data,
                "adjacency_matrix": editor.adjacency_matrix
            }
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")

    def clear_edges(self):
        editor = self.get_current_editor()
        if editor:
            new_matrix = [[0] * len(editor.nodes) for _ in range(len(editor.nodes))]
            editor.set_adjacency_matrix(new_matrix)

    def new_schema(self):
        editor = self.get_current_editor()
        if not editor:
            return
        input_value = simpledialog.askstring("Новая схема", "Введите количество элементов (колонки x строки):")
        if input_value:
            try:
                cols, rows = map(int, input_value.lower().replace('x', ' ').split())
                num_nodes = cols * rows
                nodes = {}
                for i in range(num_nodes):
                    nodes[i + 1] = Node(i + 1, i + 1)
                adjacency_matrix = [[0] * num_nodes for _ in range(num_nodes)]
                schema_data = SchemaData(nodes, adjacency_matrix, cols, rows)
                editor.set_graph(schema_data)
                editor.current_file = None
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректные данные в формате 'число x число'")

    def arrange_by_connectivity(self):
        messagebox.showinfo("Размещение по связности", "Здесь будет реализована логика размещения по связности.")

    def pair_swaps(self):
        messagebox.showinfo("Парные перестановки", "Здесь будет реализована логика парных перестановок.")

    def about(self):
        messagebox.showinfo("О программе", "Студенты РГРТУ гр 146\nДикун В.В.\nСвиридов Е.С.\nКостяева А.М\n2025г")


# =============================================================================
# Основной запуск приложения
# =============================================================================
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Редактор схем РГРТУ")
    root.geometry("1024x768")
    tab_manager = TabManager(root)
    global_menu = GlobalMenu(root, tab_manager)
    root.mainloop()
