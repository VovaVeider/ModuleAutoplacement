"""
serializer.py
Модуль для сериализации (сохранения) и десериализации (загрузки) схемы.
"""

import json
from tkinter import messagebox
from typing import Dict, Optional, Any
from models import Node, SchemaData

class SchemaSerializer:
    """
    Инкапсулирует логику сохранения и загрузки схемы в формате JSON.
    """
    @staticmethod
    def serialize(schema_data: SchemaData, filename: str) -> None:
        try:
            nodes_data: Dict[str, Dict[str, int]] = {}
            for node in schema_data.nodes.values():
                nodes_data[str(node.element_number)] = {
                    "element_number": node.element_number,
                    "grid_position": node.grid_position
                }
            data: Dict[str, Any] = {
                "cols": schema_data.cols,
                "rows": schema_data.rows,
                "nodes": nodes_data,
                "adjacency_matrix": schema_data.adjacency_matrix
            }
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
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
