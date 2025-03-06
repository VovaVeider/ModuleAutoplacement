import random
from typing import List, Tuple

from autoplacement.AbstractAutoPlacement import AbstractAutoPlacement
from models import SchemaData, Node


class RandomPlacement(AbstractAutoPlacement):
    def get_name(self) -> str:
        return "Случайное размещение"

    def run(self, schema_data: SchemaData, tab_name: str) -> List[Tuple[SchemaData, str]]:
        # назначаем случайные grid_position для каждого узла.
        new_nodes = {}
        total = len(schema_data.nodes)
        positions = list(range(1, total + 1))
        random.shuffle(positions)
        for node, pos in zip(schema_data.nodes.values(), positions):
            new_nodes[node.element_number] = Node(node.element_number, pos)
        new_schema = SchemaData(new_nodes, schema_data.adjacency_matrix, schema_data.cols, schema_data.rows)
        return [(new_schema, f"{tab_name} случ. размещ.")]