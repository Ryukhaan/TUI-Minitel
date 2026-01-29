from .color import Color
from . effect import Effect

class Mixel:
    "Minitel Element"

    def __init__(self, x: int = 1, y: int = 1, character: str = ' ', 
                 fg_color: Color = Color.WHITE,
                 bg_color: Color = Color.BLACK,
                 effect: Effect = Effect.NONE):
        self.x = x
        self.y = y
        self.character = character
        self.fg_color = fg_color 
        self.bg_color = bg_color
        self.effect = effect
    
    def __eq__(self, other: 'Mixel'):
        if other is None:
            return False
        pos = self.x == other.x and self.y == other.y
        char = self.character == other.character
        fg = self.fg_color == other.fg_color
        bg = self.bg_color == other.bg_color
        effect = self.effect == other.effect
        return pos and char and fg and bg and effect
    
    def __str__(self):
        return f"Mixel({self.x},{self.y},{self.character},color=({self.bg_color}, {self.fg_color}), effect={self.effect})"