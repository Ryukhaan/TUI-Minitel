from .widget import Mixel
from .config import SCREEN_HEIGHT, SCREEN_WIDTH

class MinitelBuffer:
    def __init__(self, cols=SCREEN_WIDTH, rows=SCREEN_HEIGHT):
        self.cols = cols
        self.rows = rows
        self.buffer = [[None for _ in range(cols)] for _ in range(rows)]

    def clear(self):
        self.buffer = [[None for _ in range(self.cols)] for _ in range(self.rows)]

    def apply(self, mixels: list[Mixel]) -> list[Mixel]:
        changed = []

        for m in mixels:
            x, y = m.x-1, m.y-1
            old = self.buffer[y][x]
            # comparaison logique
            if old != m:        
                self.buffer[y][x] = m
                changed.append(m)

        return changed
