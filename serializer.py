import json
from tkinter import messagebox
from typing import Dict, Optional

from models import Node, SchemaData


class SchemaSerializer:
    """
    SchemaSerializer инкапсулирует логику сохранения и загрузки схемы в формате JSON.
    """
    @staticmethod
    def serialize(schema_data: SchemaData, filename: str) -> None:
        try:
            # Формируем словарь узлов
            nodes_data: Dict[str, Dict[str, int]] = {}
            for node in schema_data.nodes.values():
                nodes_data[str(node.element_number)] = {
                    "element_number": node.element_number,
                    "grid_position": node.grid_position
                }
            # Получаем матрицу смежности
            matrix = schema_data.adjacency_matrix
            formatted_matrix: str = ""
            if matrix:
                # Определяем число столбцов (предполагаем, что все строки одинаковой длины)
                num_cols = len(matrix[0])
                # Вычисляем ширину для каждого столбца как максимальную длину числа в этом столбце
                col_widths = [
                    max(len(str(row[i])) for row in matrix)
                    for i in range(num_cols)
                ]
                # Форматируем каждую строку матрицы с выравниванием по столбцам
                formatted_rows = []
                for row in matrix:
                    formatted_row = "[ " + ", ".join(
                        str(num).rjust(col_widths[i]) for i, num in enumerate(row)
                    ) + " ]"
                    formatted_rows.append(formatted_row)
                # Собираем итоговую строку с отступами
                formatted_matrix = "[\n    " + ",\n    ".join(formatted_rows) + "\n]"
            # Форматируем узлы с помощью json.dumps для аккуратного вывода
            nodes_json: str = json.dumps(nodes_data, indent=4, ensure_ascii=False)
            # Собираем итоговый JSON-вывод вручную, вставляя отформатированную матрицу
            final_json: str = "{\n"
            final_json += f'    "cols": {schema_data.cols},\n'
            final_json += f'    "rows": {schema_data.rows},\n'
            final_json += f'    "nodes": {nodes_json},\n'
            final_json += '    "adjacency_matrix": ' + formatted_matrix + "\n"
            final_json += "}"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(final_json)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")

    @staticmethod
    def deserialize(filename: str) -> Optional[SchemaData]:
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            cols: int = data.get("cols", 0)
            rows: int = data.get("rows", 0)
            nodes_data: Dict[str, Dict[str, int]] = data.get("nodes", {})
            nodes: Dict[int, Node] = {}
            for key, node_info in nodes_data.items():
                element_number: int = node_info["element_number"]
                grid_position: int = node_info["grid_position"]
                nodes[element_number] = Node(element_number, grid_position)
            adjacency_matrix = data.get("adjacency_matrix", [])
            return SchemaData(nodes, adjacency_matrix, cols, rows)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{e}")
            return None
