from typing import NamedTuple
from .base import Window
from .ops import draw_text

from minitel.tui.core import Effect, Color
from minitel.tui.keyboard import Key

class Command(NamedTuple):
    name: str
    function: callable
    enabled: bool
    extension: dict

class Menu(Window):

    def __init__(self, rect):
        super().__init__(rect)
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
                draw_text(self.rect.x, self.rect.y + row,
                          command.text,
                          effect= Effect.INVERT if self.index == row else Effect.NONE)
            )
        return mixels
