from .color import Color
from .state import GraphicState

class Mixel:
    "Minitel Element"

    def __init__(self, x: int = 1, y: int = 1, character: str = ' ', 
                #  fg_color: Color = Color.WHITE,
                #  bg_color: Color = Color.BLACK,
                 state: GraphicState = None):
        self.x = x
        self.y = y
        self.character = character
        # self.fg_color = fg_color 
        # self.bg_color = bg_color
        if state is None:
            state = GraphicState(Color.WHITE, Color.BLACK, False, False, False, False)
        self.state = state
    
    def __eq__(self, other: 'Mixel'):
        if other is None:
            return False
        pos = self.x == other.x and self.y == other.y
        char = self.character == other.character
        # fg = self.state.fg == other.state.
        # bg = self.bg_color == other.bg_color
        state = self.state == other.state
        return pos and char and state
    
    def __str__(self):
        return f"Mixel({self.x}, {self.y}, {self.character}, state={self.state})"