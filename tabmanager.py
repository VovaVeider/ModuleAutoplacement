"""
tabmanager.py
Модуль с классом TabManager, отвечающим за управление вкладками.
"""

import tkinter as tk
from tkinter import simpledialog, messagebox
from tkinter import ttk
from typing import Dict, Optional, List

from editor import SchemaEditor
from models import Node, SchemaData


class TabManager:
    """
    TabManager управляет вкладками, каждая из которых содержит экземпляр SchemaEditor.

    Attributes:
        notebook (ttk.Notebook): Виджет вкладок.
        tabs (Dict[str, SchemaEditor]): Словарь, где ключ – идентификатор фрейма, а значение – SchemaEditor.
        plus_tab_id (Optional[str]): Идентификатор вкладки с символом "+".
        last_tab (Optional[str]): Последняя выбранная вкладка (не "+").
    """

    def __init__(self, master: tk.Tk) -> None:
        self.master: tk.Tk = master
        self.notebook: ttk.Notebook = ttk.Notebook(master)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.tabs: Dict[str, SchemaEditor] = {}
        self.plus_tab_id: Optional[str] = None
        self.last_tab: Optional[str] = None
        first_tab: Optional[tk.Frame] = self.create_new_tab(initial=True)
        if first_tab is not None:
            self.last_tab = str(first_tab)
        self.add_plus_tab()
        self.notebook.bind("<Button-1>", self.on_notebook_click)
        self.notebook.bind("<Button-3>", self.on_tab_right_click)

    def create_new_tab(self, initial: bool = False) -> Optional[tk.Frame]:
        if initial:
            tab_name: str = "безымянный"
        else:
            tab_name = simpledialog.askstring("Новая вкладка", "Введите имя новой вкладки:")
            if tab_name is None or tab_name.strip() == "":
                return None
        frame: tk.Frame = tk.Frame(self.notebook)
        cols: int = 3
        rows: int = 3
        num_nodes: int = cols * rows
        nodes: Dict[int, Node] = {i + 1: Node(i + 1, i + 1) for i in range(num_nodes)}
        adjacency_matrix = [[0] * num_nodes for _ in range(num_nodes)]
        schema_data: SchemaData = SchemaData(nodes, adjacency_matrix, cols, rows)
        editor: SchemaEditor = SchemaEditor(frame, schema_data=schema_data)
        # Если вкладка "+" уже существует, вставляем новую вкладку перед ней
        if self.plus_tab_id is not None:
            index = self.notebook.index(self.plus_tab_id)
            self.notebook.insert(index, frame, text=tab_name)
        else:
            self.notebook.add(frame, text=tab_name)
        self.tabs[str(frame)] = editor
        return frame

    def create_new_tab_with_name(self, tab_name: str) -> tk.Frame:
        frame: tk.Frame = tk.Frame(self.notebook)
        cols: int = 3
        rows: int = 3
        num_nodes: int = cols * rows
        nodes: Dict[int, Node] = {i + 1: Node(i + 1, i + 1) for i in range(num_nodes)}
        adjacency_matrix = [[0] * num_nodes for _ in range(num_nodes)]
        schema_data: SchemaData = SchemaData(nodes, adjacency_matrix, cols, rows)
        editor: SchemaEditor = SchemaEditor(frame, schema_data=schema_data)
        # Вставляем новую вкладку перед вкладкой "+"
        if self.plus_tab_id is not None:
            index = self.notebook.index(self.plus_tab_id)
            self.notebook.insert(index, frame, text=tab_name)
        else:
            self.notebook.add(frame, text=tab_name)
        self.tabs[str(frame)] = editor
        return frame

    def add_plus_tab(self) -> None:
        """Добавляет вкладку с символом '+' для создания новых вкладок."""
        frame: tk.Frame = tk.Frame(self.notebook)
        self.plus_tab_id = str(frame)
        self.notebook.add(frame, text="+")

    def on_notebook_click(self, event: tk.Event) -> None:
        """
        Обрабатывает левый клик по вкладкам.
        Если клик по вкладке с '+', запрашивает имя новой вкладки.
        """
        try:
            tab_index: int = self.notebook.index(f"@{event.x},{event.y}")
            tab_id: str = self.notebook.tabs()[tab_index]
        except Exception:
            return
        if self.notebook.tab(tab_id, "text") != "+":
            self.last_tab = tab_id
            return
        current: str = self.notebook.select()
        if current != self.plus_tab_id:
            self.last_tab = current
        new_name = simpledialog.askstring("Новая вкладка", "Введите имя новой вкладки:")
        self.notebook.forget(self.plus_tab_id)
        if new_name is None or new_name.strip() == "":
            if self.last_tab is not None:
                self.notebook.select(self.last_tab)
            self.add_plus_tab()
            return
        new_tab: Optional[tk.Frame] = self.create_new_tab_with_name(new_name)
        if new_tab is not None:
            self.notebook.select(new_tab)
            self.last_tab = str(new_tab)
        self.add_plus_tab()

    def on_tab_right_click(self, event: tk.Event) -> None:
        """
        Обрабатывает правый клик по вкладкам и показывает контекстное меню с опциями "Переименовать" и "Удалить".
        """
        try:
            tab_index: int = self.notebook.index(f"@{event.x},{event.y}")
            tab_id: str = self.notebook.tabs()[tab_index]
        except Exception:
            return
        if self.notebook.tab(tab_id, "text") == "+":
            return
        menu: tk.Menu = tk.Menu(self.notebook, tearoff=0)
        menu.add_command(label="Переименовать", command=lambda: self.rename_tab(tab_id))
        menu.add_command(label="Удалить", command=lambda: self.delete_tab(tab_id))
        menu.tk_popup(event.x_root, event.y_root)

    def delete_tab(self, tab_id: str) -> None:
        """
        Удаляет вкладку (если их больше одной, кроме вкладки "+").
        """
        if len(self.tabs) <= 1:
            messagebox.showwarning("Ошибка", "Нельзя удалить последнюю вкладку!")
            return
        if messagebox.askyesno("Подтверждение", "Удалить вкладку?"):
            self.notebook.forget(tab_id)
            if tab_id in self.tabs:
                del self.tabs[tab_id]
            remaining: List[str] = list(self.tabs.keys())
            if remaining:
                self.notebook.select(remaining[0])
                self.last_tab = remaining[0]

    def rename_tab(self, tab_id: str) -> None:
        """
        Переименовывает вкладку, запрашивая новое имя у пользователя.

        Args:
            tab_id (str): Идентификатор вкладки.
        """
        new_name = simpledialog.askstring("Переименовать вкладку", "Введите новое имя вкладки:")
        if new_name:
            self.notebook.tab(tab_id, text=new_name)

    def get_current_editor(self) -> Optional[SchemaEditor]:
        """
        Возвращает текущий экземпляр SchemaEditor.

        Returns:
            Optional[SchemaEditor]: Текущий редактор или None.
        """
        current_tab: str = self.notebook.select()
        if current_tab in self.tabs:
            return self.tabs[current_tab]
        return None

    def get_current_tab_name(self) -> str:
        current_tab = self.notebook.select()
        tab_name = self.notebook.tab(current_tab, "text")
        return tab_name
