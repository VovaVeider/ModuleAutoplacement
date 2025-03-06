"""
globalmenu.py
Модуль с классом GlobalMenu для управления глобальным меню приложения.
"""

import os
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
from typing import Optional, List, Dict

from autoplacement import AUTO_PLACEMENT_ALGORITHMS
from autoplacement.AbstractAutoPlacement import AbstractAutoPlacement
from autoplacement.utils import compute_total_weighted_length

from editor import SchemaEditor
from models import SchemaData, Node
from serializer import SchemaSerializer
from tabmanager import TabManager


class GlobalMenu:
    """
    GlobalMenu реализует глобальное меню приложения.
    """
    def __init__(self, master: tk.Tk, tab_manager: TabManager) -> None:
        self.tab_manager: TabManager = tab_manager
        # Флаг: если True, после авторазмещения создаётся новая вкладка с новым размещением,
        # иначе текущая схема обновляется.
        self.new_tab_after_autoplacement: bool = True

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

        # Динамическое добавление пунктов для авторазмещения
        auto_menu: tk.Menu = tk.Menu(menu_bar, tearoff=0)
        for algo in AUTO_PLACEMENT_ALGORITHMS:
            auto_menu.add_command(label=algo.get_name(), command=lambda a=algo: self.run_auto_placement(a))
        menu_bar.add_cascade(label="Авторазмещение", menu=auto_menu)

        stats_menu: tk.Menu = tk.Menu(menu_bar, tearoff=0)
        stats_menu.add_command(label="Суммарная длина связей", command=self.show_total_length)
        menu_bar.add_cascade(label="Статистика", menu=stats_menu)

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
                # Обновляем имя вкладки на базовое имя файла
                base_name: str = os.path.basename(filename)
                current_tab: str = self.tab_manager.notebook.select()
                self.tab_manager.notebook.tab(current_tab, text=base_name)

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
        # Подставляем имя текущей вкладки как значение по умолчанию
        current_tab: str = self.tab_manager.notebook.select()
        default_name: str = self.tab_manager.notebook.tab(current_tab, "text")
        filename: str = filedialog.asksaveasfilename(title="Сохранить как",
                                                      initialfile=default_name,
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
                new_matrix: List[List[int]] = [[0] * num_nodes for _ in range(num_nodes)]
                schema_data: SchemaData = SchemaData(nodes, new_matrix, cols, rows)
                editor.set_graph(schema_data)
                editor.current_file = None
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректные данные в формате 'число x число'")

    def run_auto_placement(self, algorithm: AbstractAutoPlacement) -> None:
        """
        Выполняет выбранный алгоритм авторазмещения.
        Если флаг new_tab_after_autoplacement установлен, создаётся новая вкладка с новым размещением,
        иначе обновляется текущая вкладка.
        """
        editor = self.get_current_editor()
        if not editor:
            return
        # Формируем текущую модель данных
        from models import SchemaData  # Локальный импорт для избежания циклических зависимостей
        current_schema = SchemaData(editor.nodes, editor.adjacency_matrix, editor.cols, editor.rows).clone()
        variants = algorithm.run(current_schema,self.tab_manager.get_current_tab_name())
        if not variants:
            messagebox.showinfo("Авторазмещение", "Алгоритм не вернул ни одного варианта.")
            return
        # Берем первый вариант (можно расширить, если алгоритм возвращает несколько вариантов)
        new_schema, variant_text = variants[0]
        if self.new_tab_after_autoplacement:
            # Создаем новую вкладку с именем, равным тексту варианта
            new_tab = self.tab_manager.create_new_tab_with_name(variant_text)
            if new_tab:
                new_editor = self.tab_manager.tabs[str(new_tab)]
                new_editor.set_graph(new_schema)
                self.tab_manager.notebook.select(new_tab)
        else:
            editor.set_graph(new_schema)

    def arrange_by_connectivity(self) -> None:
        messagebox.showinfo("Размещение по связности", "Эта функция будет реализована через авторазмещение.")

    def pair_swaps(self) -> None:
        messagebox.showinfo("Парные перестановки", "Эта функция будет реализована через авторазмещение.")

    def show_total_length(self) -> None:
        editor: Optional[SchemaEditor] = self.get_current_editor()
        if not editor:
            return
        schema_data = SchemaData(editor.nodes, editor.adjacency_matrix, editor.cols, editor.rows)
        total_length: float = compute_total_weighted_length(schema_data)
        tk.messagebox.showinfo("Статистика", f"Суммарная длина связей: {total_length}")

    def about(self) -> None:
        messagebox.showinfo("О программе", "Студенты РГРТУ гр 146\nДикун В.В.\nСвиридов Е.С.\nКостяева А.М\n2025г")
