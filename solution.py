class Solution:
    def __init__(self, w, h, array_c):
        self.h = h
        self.w = w
        self.array_c = array_c
        self.sizePlat = (h, w)
        self.positions_count = h * w
        self.grid_original, self.grid_result = self.create_grids()
        self.array_d = self.create_d()
        self.E_n = self.create_E_n()
        self.E_r = []

    def create_grids(self):
        n, m = self.sizePlat
        array_with_values_original = [[() for _ in range(m)] for _ in range(n)]
        array_with_nulls_result = [[() for _ in range(m)] for _ in range(n)]

        for i in range(n):
            for j in range(m):
                index = i * m + j + 1
                element_original = (index, index)
                array_with_values_original[i][j] = element_original
                element_result = (index, None)
                array_with_nulls_result[i][j] = element_result

        return array_with_values_original, array_with_nulls_result

    def create_d(self):
        k = self.positions_count
        h, w = self.sizePlat
        ArrayD = [[0 for _ in range(k + 1)] for _ in range(k + 1)]

        for i in range(1, k + 1):
            for j in range(1, k + 1):
                x1, y1 = (i - 1) % w + 1, (i - 1) // w + 1
                if i == j:
                    ArrayD[i][j] = 0
                else:
                    x2, y2 = (j - 1) % w + 1, (j - 1) // w + 1
                    ArrayD[i][j] = abs(x1 - x2) + abs(y1 - y2)

        return ArrayD

    def create_E_n(self):
        E_n = []
        for row in self.grid_original:
            for item in row:
                pos, element = item
                if element is not None:
                    E_n.append(element)
        return E_n


# Добавлены две вспомогательные функции
def get_result_position_of_element_2(element, grid):
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j][1] == element:
                return grid[i][j][0]

def find_L(array_c, array_d, grid):
    sum = 0
    for i in range(1, len(array_c)):
        for j in range(1, len(array_c[i])):
            position_i = get_result_position_of_element_2(i, grid)
            position_j = get_result_position_of_element_2(j, grid)
            sum += array_c[i][j] * array_d[position_i][position_j]

    return sum / 2
