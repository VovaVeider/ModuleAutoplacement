import tkinter as tk
import math
import random
import json
from tkinter import simpledialog, messagebox, filedialog

class Node:
    def __init__(self, element_number, grid_position, x, y):
        self.element_number = element_number  # Номер элемента (идентификатор узла)
        self.grid_position = grid_position    # Позиция в сетке (отсчитана слева направо, сверху вниз)
        self.position = (x, y)                # Позиция на экране

class MenuBar:
    def __init__(self, root, schema_editor):
        self.schema_editor = schema_editor
        menu_bar = tk.Menu(root)
        root.config(menu=menu_bar)

        # -- Меню "Файл"
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Открыть", command=self.open_file)
        file_menu.add_command(label="Сохранить", command=self.save_file)
        file_menu.add_command(label="Сохранить как", command=self.save_as_file)
        menu_bar.add_cascade(label="Файл", menu=file_menu)

        # -- Меню "Изменить"
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Удалить все связи", command=self.clear_edges)
        edit_menu.add_command(label="Новая схема", command=self.new_schema)
        menu_bar.add_cascade(label="Изменить", menu=edit_menu)

        # -- Меню "Размещение"
        layout_menu = tk.Menu(menu_bar, tearoff=0)
        layout_menu.add_command(label="Авторазмещение", command=self.auto_layout)
        menu_bar.add_cascade(label="Размещение", menu=layout_menu)

        # -- Меню "Справка" с кнопкой "О программе"
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="О программе", command=self.about)
        menu_bar.add_cascade(label="Справка", menu=help_menu)

    def open_file(self):
        """Открытие схемы из файла JSON."""
        filename = filedialog.askopenfilename(
            title="Открыть файл",
            filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")]
        )
        if filename:
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
                nodes_data = data.get("nodes", {})
                nodes = {}
                for key, node_info in nodes_data.items():
                    element_number = node_info["element_number"]
                    grid_position = node_info["grid_position"]
                    x, y = node_info["position"]
                    nodes[element_number] = Node(element_number, grid_position, x, y)
                adjacency_matrix = data.get("adjacency_matrix", [])
                self.schema_editor.set_graph(nodes, adjacency_matrix)
                self.schema_editor.current_file = filename
                messagebox.showinfo("Открыть файл", "Файл успешно открыт!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{e}")

    def save_file(self):
        """Сохранение схемы в текущий файл или через 'Сохранить как', если файл не задан."""
        if self.schema_editor.current_file:
            self._save_to_file(self.schema_editor.current_file)
        else:
            self.save_as_file()

    def save_as_file(self):
        """Сохранение схемы в новый файл JSON."""
        filename = filedialog.asksaveasfilename(
            title="Сохранить как",
            defaultextension=".json",
            filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")]
        )
        if filename:
            self.schema_editor.current_file = filename
            self._save_to_file(filename)

    def _save_to_file(self, filename):
        """Вспомогательный метод для сохранения схемы в файл."""
        try:
            # Преобразуем узлы в сериализуемый словарь
            nodes_data = {}
            for number, node in self.schema_editor.nodes.items():
                nodes_data[number] = {
                    "element_number": node.element_number,
                    "grid_position": node.grid_position,
                    "position": list(node.position)
                }
            data = {
                "nodes": nodes_data,
                "adjacency_matrix": self.schema_editor.adjacency_matrix
            }
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Сохранить файл", "Файл успешно сохранён!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")

    def clear_edges(self):
        """Удаляет все связи (обнуляет матрицу смежности)."""
        new_matrix = [[0] * len(self.schema_editor.nodes) for _ in range(len(self.schema_editor.nodes))]
        self.schema_editor.set_adjacency_matrix(new_matrix)

    def new_schema(self):
        """Создание новой схемы по вводу вида 'колонки x строки'."""
        input_value = simpledialog.askstring("Новая схема", "Введите количество элементов (горизонталь x вертикаль):")
        if input_value:
            try:
                cols, rows = map(int, input_value.lower().replace('x', ' ').split())
                num_nodes = cols * rows
                nodes = {}
                for i in range(num_nodes):
                    x = 100 + (i % cols) * 100
                    y = 100 + (i // cols) * 100
                    # Здесь и element_number, и grid_position равны i+1
                    nodes[i+1] = Node(i+1, i+1, x, y)
                adjacency_matrix = [[0] * num_nodes for _ in range(num_nodes)]
                self.schema_editor.set_graph(nodes, adjacency_matrix)
                self.schema_editor.current_file = None
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректные данные в формате 'число x число'")

    def auto_layout(self):
        """Заглушка для автоматического расположения узлов на холсте."""
        messagebox.showinfo("Авторазмещение", "Здесь можно добавить логику авторазмещения узлов.")

    def about(self):
        """Отображает информацию о программе."""
        messagebox.showinfo("О программе",
            "Студенты РГРТУ гр 146\nДикун В.В.\nСвиридов Е.С.\nКостяева А.М\n2025г")

class SchemaEditor:
    def __init__(self, root,
                 nodes=None,
                 adjacency_matrix=None,
                 square_size=50,
                 font_size=10,
                 line_width=2):
        self.root = root
        self.root.title("Редактор схем")

        self.square_size = square_size
        self.font_size = font_size
        self.line_width = line_width

        self.nodes = nodes if nodes else {}
        self.adjacency_matrix = adjacency_matrix if adjacency_matrix else []
        self.edges = []
        self.current_file = None  # Для хранения пути к текущему файлу

        self.selected_nodes = []
        self.edge_positions = {}
        self.text_positions = set()

        self.menu = MenuBar(root, self)
        self.create_canvas()
        self.create_graph()

        # ЛКМ для выбора узла
        self.canvas.bind("<Button-1>", self.select_node)
        # ПКМ: Press и Release для логики
        self.canvas.bind("<ButtonPress-3>", self.on_right_press)
        self.canvas.bind("<ButtonRelease-3>", self.on_right_release)

    def create_canvas(self):
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            frame, bg="white",
            width=800, height=600,
            scrollregion=(0, 0, 2000, 2000)
        )
        hbar = tk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        vbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=hbar.set, yscrollcommand=vbar.set)

        hbar.pack(side=tk.BOTTOM, fill=tk.X)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

    def create_graph(self):
        """Очищаем холст и рисуем узлы + связи"""
        self.canvas.delete("all")
        for node in self.nodes.values():
            self.add_node(node.element_number, *node.position)

        for i, row in enumerate(self.adjacency_matrix):
            for j, weight in enumerate(row):
                if weight > 0 and (i + 1) in self.nodes and (j + 1) in self.nodes:
                    self.create_edge_from_matrix(self.nodes[i + 1], self.nodes[j + 1], weight)

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def create_graph(self):
        """Очищаем холст и рисуем узлы + связи"""
        self.canvas.delete("all")
        for node in self.nodes.values():
            self.add_node(node)  # передаём объект узла целиком

        for i, row in enumerate(self.adjacency_matrix):
            for j, weight in enumerate(row):
                if weight > 0 and (i + 1) in self.nodes and (j + 1) in self.nodes:
                    self.create_edge_from_matrix(self.nodes[i + 1], self.nodes[j + 1], weight)

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def add_node(self, node):
        """Отрисовывает узел, используя его element_number и grid_position."""
        element_number = node.element_number
        grid_position = node.grid_position
        x, y = node.position
        half_size = self.square_size // 2
        self.canvas.create_rectangle(
            x - half_size, y - half_size,
            x + half_size, y + half_size,
            fill="white", outline="black", width=3,
            tags=str(element_number)
        )
        self.canvas.create_text(
            x, y,
            text=f"№{element_number}\nП-{grid_position}",
            font=("Arial", self.font_size),
            tags=str(element_number)
        )
        # Обновляем словарь узлов, если нужно
        self.nodes[element_number] = node

    def set_adjacency_matrix(self, new_matrix):
        self.adjacency_matrix = new_matrix
        self.edges.clear()
        self.create_graph()

    def set_graph(self, nodes, adjacency_matrix):
        self.nodes = nodes
        self.adjacency_matrix = adjacency_matrix
        self.edges.clear()
        self.create_graph()


    def select_node(self, event):
        """ЛКМ. Если выбрано 2 узла — создаём связь."""
        click_x = self.canvas.canvasx(event.x)
        click_y = self.canvas.canvasy(event.y)
        for label, node in self.nodes.items():
            node_x, node_y = node.position
            half_size = self.square_size // 2
            if (node_x - half_size <= click_x <= node_x + half_size and
                node_y - half_size <= click_y <= node_y + half_size):
                if label not in self.selected_nodes:
                    self.selected_nodes.append(label)
                    print(f"Выбран элемент: {label}")
                if len(self.selected_nodes) == 2:
                    self.create_edge()
                return

    def remove_edge(self, event):
        """Старый метод, оставлен пустым, логика перенесена в on_right_press."""
        pass

    def create_edge(self):
        """Создаёт связь между 2 выбранными узлами и обновляет матрицу смежности."""
        if len(self.selected_nodes) < 2:
            return
        node1, node2 = self.selected_nodes
        # Проверяем, нет ли уже связи
        if any(e[2] == node1 and e[3] == node2 or e[2] == node2 and e[3] == node1 for e in self.edges):
            messagebox.showwarning("Ошибка", "Эти узлы уже соединены!")
            self.selected_nodes.clear()
            return
        weight = simpledialog.askinteger("Вес связи", "Введите вес связи:")
        if weight is not None:
            # Обновляем матрицу смежности (учитываем, что индексы списка начинаются с 0)
            self.adjacency_matrix[node1 - 1][node2 - 1] = weight
            self.adjacency_matrix[node2 - 1][node1 - 1] = weight
            self.create_edge_from_matrix(self.nodes[node1], self.nodes[node2], weight)
        self.selected_nodes.clear()



    def create_edge_from_matrix(self, node1, node2, weight):
        """Рисует линию от края к краю, число вес — бОльшим шрифтом."""
        x1, y1 = self.get_closest_edge_position(node1, node2)
        x2, y2 = self.get_closest_edge_position(node2, node1)
        color = f"#{random.randint(0,255):02x}{random.randint(0,255):02x}{random.randint(0,255):02x}"
        edge = self.canvas.create_line(
            x1, y1, x2, y2,
            width=self.line_width,
            fill=color
        )
        text_x, text_y = (x1 + x2) // 2, (y1 + y2) // 2
        text = self.canvas.create_text(
            text_x, text_y,
            text=str(weight),
            font=("Arial", self.font_size + 2, "bold"),
            fill=color
        )
        self.edges.append((edge, text, node1.element_number, node2.element_number, weight))
        self.edge_positions[(node1.element_number, node2.element_number)] = (text_x, text_y)

    def get_closest_edge_position(self, nodeA, nodeB):
        """Край квадрата A, ближайший к B."""
        (xA, yA) = nodeA.position
        (xB, yB) = nodeB.position
        half_size = self.square_size // 2
        dx = xB - xA
        dy = yB - yA
        if abs(dx) > abs(dy):
            if dx > 0:
                return (xA + half_size, yA)
            else:
                return (xA - half_size, yA)
        else:
            if dy > 0:
                return (xA, yA + half_size)
            else:
                return (xA, yA - half_size)

    ################################################################
    # Логика точного определения узел/ребро + скрытие/показ
    ################################################################

    def highlight_edges(self, node_label=None):
        """Скрывает все связи, кроме тех, что содержат node_label. Если node_label=None, показывает все."""
        for edge, text, n1, n2, _ in self.edges:
            self.canvas.itemconfigure(edge, state='normal')
            self.canvas.itemconfigure(text, state='normal')
        if node_label is not None:
            for edge, text, n1, n2, _ in self.edges:
                if n1 != node_label and n2 != node_label:
                    self.canvas.itemconfigure(edge, state='hidden')
                    self.canvas.itemconfigure(text, state='hidden')

    def on_right_press(self, event):
        """Точное определение: или ребро (удаляем), или узел (скрываем чужие связи)."""
        px = self.canvas.canvasx(event.x)
        py = self.canvas.canvasy(event.y)

        # Проверяем, не попали ли на ребро
        TOL = 5
        for (edge_obj, text_obj, node1, node2, weight) in self.edges:
            x1, y1 = self.get_closest_edge_position(self.nodes[node1], self.nodes[node2])
            x2, y2 = self.get_closest_edge_position(self.nodes[node2], self.nodes[node1])
            dist = self.dist_point_segment(px, py, x1, y1, x2, y2)
            if dist <= TOL:
                # Удаляем это ребро
                if messagebox.askyesno("Подтверждение", f"Удалить связь между {node1} и {node2} (вес {weight})?"):
                    self.canvas.delete(edge_obj)
                    self.canvas.delete(text_obj)
                    self.edges.remove((edge_obj, text_obj, node1, node2, weight))
                    if (node1, node2) in self.edge_positions:
                        del self.edge_positions[(node1, node2)]
                return

        # Если не попали на ребро, проверяем узел
        found_node = None
        for label, node in self.nodes.items():
            xN, yN = node.position
            half_size = self.square_size // 2
            if (xN - half_size <= px <= xN + half_size and
                yN - half_size <= py <= yN + half_size):
                found_node = label
                break

        if found_node is not None:
            self.highlight_edges(found_node)
        else:
            self.highlight_edges(None)

    def on_right_release(self, event):
        """Отпускание ПКМ — показываем все связи."""
        self.highlight_edges(None)

    def dist_point_segment(self, px, py, x1, y1, x2, y2):
        """Расстояние от (px, py) до отрезка (x1,y1)-(x2,y2)."""
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

##########################################################
# Пример запуска
##########################################################

if __name__ == "__main__":
    root = tk.Tk()
    # Пример 3x3: для каждого узла в качестве element_number и grid_position используется i+1
    nodes = {
        i+1: Node(i+1, i+1,
                  100 + (i % 3) * 100,
                  100 + (i // 3) * 100)
        for i in range(9)
    }
    adjacency_matrix = [[0] * 9 for _ in range(9)]
    app = SchemaEditor(root, nodes=nodes, adjacency_matrix=adjacency_matrix)
    root.mainloop()
