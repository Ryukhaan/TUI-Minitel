from typing import NamedTuple
from .widget import Widget, Label
from .config import SCREEN_HEIGHT, SCREEN_WIDTH
from .core import Effect, Color
from .keyboard import Key

class Command(NamedTuple):
    name: str
    function: callable
    enabled: bool
    extension: dict

class Menu(Widget):

    def __init__(self, x, y, width, height, color = Color.WHITE, effect = Effect.NONE):
        super().__init__(x, y, width, height, color, effect)
        self.index: int = -1
        self.commands: list[Command] = []
        self.keymap = {
            Key.UP: lambda: self._update_by(-1),
            Key.DOWN: lambda: self._update_by(1)
        }

    def _update_by(self, value: int) -> bool:
        if len(self.commands) > 0:
            self.index = (self.index + value) % len(self.commands)
            return True
        return False
    
    def select(self, index):
        self.index = index
    
    def unselect(self):
        self.index = -1
    
    def add_command(self, name, function, enabled: bool = True, extension = {}):
        self.commands.append(Command(name, function, enabled, extension))
        self.height += 1
        self.width = max(self.width, len(name))
    
    def command_name(self):
        return self.commands[self.index].name

    @property
    def current_command(self):
        return self.commands if self.index >= 0 else None 

    def handle_key(self, key):
        """Met à jour le texte en fonction de la touche"""
        if key in self.keymap:
            return self.keymap[key]()
        
    def render(self):
        mixels = []
        for row, command in enumerate(self.commands):
            mixels.extend(
                Label(self.x, self.y + row, 
                    text=command.name,
                    effect=Effect.INVERT if self.index == row else Effect.NONE).render()
            )
        return mixels
