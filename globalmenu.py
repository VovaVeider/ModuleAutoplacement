"""
globalmenu.py
Модуль с классом GlobalMenu для управления глобальным меню приложения.
"""

import tkinter as tk
import json
from tkinter import simpledialog, messagebox, filedialog
from typing import Optional, List, Dict
from editor import SchemaEditor
from tabmanager import TabManager
from serializer import SchemaSerializer
from models import SchemaData, Node

class GlobalMenu:
    """
    GlobalMenu реализует глобальное меню приложения.
    """
    def __init__(self, master: tk.Tk, tab_manager: TabManager) -> None:
        self.tab_manager: TabManager = tab_manager
        menu_bar: tk.Menu = tk.Menu(master)
        master.config(menu=menu_bar)

        file_menu: tk.Menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Открыть", command=self.open_file)
        file_menu.add_command(label="Сохранить", command=self.save_file)
        file_menu.add_command(label="Сохранить как", command=self.save_as_file)
        menu_bar.add_cascade(label="Файл", menu=file_menu)

        edit_menu: tk.Menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Удалить все связи", command=self.clear_edges)
        edit_menu.add_command(label="Новая схема", command=self.new_schema)
        menu_bar.add_cascade(label="Изменить", menu=edit_menu)

        auto_menu: tk.Menu = tk.Menu(menu_bar, tearoff=0)
        auto_menu.add_command(label="Размещение по связности", command=self.arrange_by_connectivity)
        auto_menu.add_command(label="Парные перестановки", command=self.pair_swaps)
        menu_bar.add_cascade(label="Авторазмещение", menu=auto_menu)

        help_menu: tk.Menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="О программе", command=self.about)
        menu_bar.add_cascade(label="Справка", menu=help_menu)

    def get_current_editor(self) -> Optional[SchemaEditor]:
        return self.tab_manager.get_current_editor()

    def open_file(self) -> None:
        editor: Optional[SchemaEditor] = self.get_current_editor()
        if not editor:
            return
        filename: str = filedialog.askopenfilename(title="Открыть файл",
                                                    filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")])
        if filename:
            schema_data: Optional[SchemaData] = SchemaSerializer.deserialize(filename)
            if schema_data:
                editor.set_graph(schema_data)
                editor.current_file = filename

    def save_file(self) -> None:
        editor: Optional[SchemaEditor] = self.get_current_editor()
        if not editor:
            return
        if editor.current_file:
            SchemaSerializer.serialize(
                SchemaData(editor.nodes, editor.adjacency_matrix, editor.cols, editor.rows),
                editor.current_file
            )
        else:
            self.save_as_file()

    def save_as_file(self) -> None:
        editor: Optional[SchemaEditor] = self.get_current_editor()
        if not editor:
            return
        filename: str = filedialog.asksaveasfilename(title="Сохранить как",
                                                      defaultextension=".json",
                                                      filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")])
        if filename:
            editor.current_file = filename
            SchemaSerializer.serialize(
                SchemaData(editor.nodes, editor.adjacency_matrix, editor.cols, editor.rows),
                filename
            )

    def clear_edges(self) -> None:
        editor: Optional[SchemaEditor] = self.get_current_editor()
        if editor:
            new_matrix: List[List[int]] = [[0] * len(editor.nodes) for _ in range(len(editor.nodes))]
            editor.set_adjacency_matrix(new_matrix)

    def new_schema(self) -> None:
        editor: Optional[SchemaEditor] = self.get_current_editor()
        if not editor:
            return
        input_value: Optional[str] = simpledialog.askstring("Новая схема", "Введите количество элементов (колонки x строки):")
        if input_value:
            try:
                cols, rows = map(int, input_value.lower().replace('x', ' ').split())
                num_nodes: int = cols * rows
                nodes: Dict[int, Node] = {i + 1: Node(i + 1, i + 1) for i in range(num_nodes)}
                adjacency_matrix: List[List[int]] = [[0] * num_nodes for _ in range(num_nodes)]
                schema_data: SchemaData = SchemaData(nodes, adjacency_matrix, cols, rows)
                editor.set_graph(schema_data)
                editor.current_file = None
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректные данные в формате 'число x число'")

    def arrange_by_connectivity(self) -> None:
        messagebox.showinfo("Размещение по связности", "Здесь будет реализована логика размещения по связности.")

    def pair_swaps(self) -> None:
        messagebox.showinfo("Парные перестановки", "Здесь будет реализована логика парных перестановок.")

    def about(self) -> None:
        messagebox.showinfo("О программе", "Студенты РГРТУ гр 146\nДикун В.В.\nСвиридов Е.С.\nКостяева А.М\n2025г")
