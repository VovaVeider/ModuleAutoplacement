from abc import abstractmethod, ABC
from typing import Tuple, List

from models import SchemaData


class AbstractAutoPlacement(ABC):
    @abstractmethod
    def get_name(self) -> str:
        """
        Возвращает название алгоритма размещения.
        """
        pass

    @abstractmethod
    def run(self, schema_data: SchemaData, tab_name: str) -> List[Tuple[SchemaData, str]]:
        """
        Выполняет алгоритм авторазмещения.

        Args:
            schema_data (SchemaData): Исходная модель данных.

        Returns:
            List[Tuple[SchemaData, str]]: Список вариантов размещения.
                Каждый вариант – кортеж (новая модель данных, текст для вкладки).
        """
        pass