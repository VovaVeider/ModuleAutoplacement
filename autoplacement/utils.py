from tkinter import messagebox, simpledialog
from typing import Dict, List, Set, Optional

from models import Node, SchemaData


def compute_total_weighted_length(schema_data: SchemaData) -> float:
    """
    Вычисляет суммарную длину связей схемы.

    Для каждого ребра (i < j) вычисляется:
        weight * (|row_i - row_j| + |col_i - col_j|)
    где row и col вычисляются из grid_position узлов (с учетом количества колонок).

    Args:
        schema_data (SchemaData): Объект схемы.

    Returns:
        float: Суммарная длина связей.
    """
    total: float = 0.0
    cols: int = schema_data.cols
    nodes: Dict[int, Node] = schema_data.nodes
    # Проходим по матрице для i < j, чтобы не дублировать ребра
    for i, row in enumerate(schema_data.adjacency_matrix):
        for j, weight in enumerate(row):
            if j > i and weight > 0:
                node_i = nodes.get(i + 1)
                node_j = nodes.get(j + 1)
                if node_i is None or node_j is None:
                    continue
                row_i = (node_i.grid_position - 1) // cols
                col_i = (node_i.grid_position - 1) % cols
                row_j = (node_j.grid_position - 1) // cols
                col_j = (node_j.grid_position - 1) % cols
                manhattan_distance = abs(row_i - row_j) + abs(col_i - col_j)
                total += weight * manhattan_distance
    return total


def get_directive_nodes(max_id: int) -> Optional[List[Node]]:
    """
    Запрашивает у пользователя директивно размещённые элементы и их позиции.
    Формат (одна строка): "элемент,позиция; элемент,позиция; ..."

    Ограничения:
      - элемент ≤ max_id
      - позиция ≤ max_id
      - нельзя использовать одну позицию для нескольких элементов
    Если пользователь ничего не ввел (или только пробелы),
    возвращаем пустой список.

    Пример использования:
      user_input = "1,5; 3,7"
      => Node(1,5), Node(3,7)

    Возвращает список Node(element_number, grid_position)
    или None, если пользователь нажал "Отмена"
    (т. е. закрыл диалог).
    """

    prompt = (
        f"Введите пары 'элемент,позиция' через точку с запятой.\n"
        f"Ограничение: элемент и позиция не больше {max_id}.\n"
        f"Пример: 1,2; 3,7\n"
        f"(Если оставить пустым, список вернется пустым.)"
    )

    user_input = simpledialog.askstring("Директивное размещение", prompt)
    if user_input is None:
        # Пользователь нажал «Отмена» или закрыл диалог
        return None

    # Удаляем лишние пробелы
    user_input = user_input.strip()
    if not user_input:
        # Если строка пустая или из одних пробелов
        return []

    # Разделяем строку по ";" – получаем блоки "элемент,позиция"
    pairs_str = [segment.strip() for segment in user_input.split(";") if segment.strip()]
    # Если в итоге нечего парсить, возвращаем пустой список
    if not pairs_str:
        return []

    result_nodes: List[Node] = []
    used_positions: Set[int] = set()

    try:
        for pair in pairs_str:
            el_s, pos_s = [x.strip() for x in pair.split(",")]
            el_num = int(el_s)
            pos_num = int(pos_s)

            # Проверяем, что элемент и позиция в диапазоне 1..max_id
            if el_num < 1 or el_num > max_id:
                messagebox.showerror(
                    "Ошибка",
                    f"Элемент {el_num} вне диапазона (1..{max_id})."
                )
                return None

            if pos_num < 1 or pos_num > max_id:
                messagebox.showerror(
                    "Ошибка",
                    f"Позиция {pos_num} вне диапазона (1..{max_id})."
                )
                return None

            if pos_num in used_positions:
                messagebox.showerror(
                    "Ошибка",
                    f"Позиция {pos_num} уже занята другим элементом."
                )
                return None

            used_positions.add(pos_num)
            result_nodes.append(Node(el_num, pos_num))

    except ValueError:
        messagebox.showerror("Ошибка",
                             "Неверный формат. Нужно 'элемент,позиция; элемент,позиция; ...'")
        return None
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")
        return None

    # Если пользователь ввел пары, и все прошло – возвращаем список узлов
    return result_nodes

