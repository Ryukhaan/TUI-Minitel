from typing import NamedTuple
from .base import Window, WindowSelectable
from .ops import draw_text

from minitel.tui.core import Effect
from minitel.tui.keyboard import Key

class Command(NamedTuple):
    name: str
    function: callable
    enabled: bool
    extension: dict

class Menu(WindowSelectable):

    def __init__(self, rect):
        super().__init__(rect)
        self.set_handler(Key.UP, lambda: self._update_by(-1))
        self.set_handler(Key.DOWN, lambda: self._update_by(1))

    def _update_by(self, value: int) -> bool:
        if len(self.handlers) > 0:
            self.index = (self.index + value) % len(self.handlers)
            return True
        return False
    
    # def add_command(self, name, function, enabled: bool = True, extension = {}):
    #     self.commands.append(Command(name, function, enabled, extension))
    #     self.rect.height += 1
    #     self.rect.width = max(self.rect.width, len(name))
    
    # def command_name(self):
    #     return self.commands[self.index].name

    # @property
    # def current_command(self):
    #     return self.commands if self.index >= 0 else None 
        
    def render(self):
        mixels = []
        for row, command in enumerate(self.commands):
            mixels.extend(
                draw_text(self.rect.x, self.rect.y + row,
                          command.name,
                          effect= Effect.INVERT if self.index == row else Effect.NONE)
            )
        return mixels
