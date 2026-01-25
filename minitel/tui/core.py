from enum import Enum
from ..constantes import *

class Effect(Enum):
    NONE = -1
    UNDERLINE = 0
    BLINK = 1
    INVERT = 2
    SEMIGRAPHIQUE = 3

    def encode(self):
        if self.name == 'UNDERLINE':
            return [ESC, 0x5a]
        elif self.name == 'BLINK':
            return [ESC, 0x48]
        elif self.name == 'INVERT':
            return [ESC, 0x5d]
        elif self.name == 'SEMIGRAPHIQUE':
            return [SO]
        else:
            return  [ESC, 0x59, ESC, 0x49, ESC, 0x5c, SI]

class Color(Enum):
    BLACK = 0
    GRAY_1 = 1
    GRAY_2 = 2
    GRAY_3 = 3
    GRAY_4 = 4
    GRAY_5 = 5
    GRAY_6 = 6
    WHITE = 7

    def encode(self):
        try:
            return [ESC, 0x40 + COULEURS_MINITEL[str(self.value)]]
        except Exception:
            return []

class Mixel:
    "Minitel Element"

    def __init__(self, x: int = 1, y: int = 1, character: str = ' ', 
                 color: Color = Color.WHITE, 
                 effect: Effect = Effect.NONE):
        self.x = x
        self.y = y
        self.character = character
        self.color = color
        self.effect = effect
    
    def __eq__(self, other: 'Mixel'):
        if other is None:
            return False
        pos = self.x == other.x and self.y == other.y
        char = self.character == other.character
        color = self.color == other.color
        effect = self.effect == other.effect
        return pos and char and color and effect
    
    def __str__(self):
        return f"Mixel({self.x},{self.y},{self.character},color={self.color}, effect={self.effect})"