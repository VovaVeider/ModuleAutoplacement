# Список доступных алгоритмов авторазмещения
from typing import List

from autoplacement.AbstractAutoPlacement import AbstractAutoPlacement
from autoplacement.RandomPlacement import RandomPlacement
from autoplacement.SequentialConnectivityPlacement import SequentialConnectivityPlacement

AUTO_PLACEMENT_ALGORITHMS: List[AbstractAutoPlacement] = [
    RandomPlacement(),
    SequentialConnectivityPlacement()
]