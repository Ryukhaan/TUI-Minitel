from .color import Color
from . effect import Effect

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