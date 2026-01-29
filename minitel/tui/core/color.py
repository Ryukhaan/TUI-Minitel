from enum import Enum
from minitel.constantes import *

class Color(Enum):
    BLACK = 0
    GRAY_1 = 1
    GRAY_2 = 2
    GRAY_3 = 3
    GRAY_4 = 4
    GRAY_5 = 5
    GRAY_6 = 6
    WHITE = 7

    def encode(self, background: bool =False):
        if background:
            try:
                return [ESC, 0x50 + COULEURS_MINITEL[str(self.value)]]
            except IndexError:
                return [ESC, 0x50]
        else:
            try:
                return [ESC, 0x40 + COULEURS_MINITEL[str(self.value)]]
            except Exception:
                return [ESC, 0x40]