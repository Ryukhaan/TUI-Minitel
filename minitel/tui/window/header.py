from minitel.tui.core.config import SCREEN_HEIGHT, SCREEN_WIDTH
from minitel.tui.core.mixel import Mixel
from minitel.tui.core.rectangle import Rectangle
from minitel.tui.window.label import Label
from minitel.tui.window.line import HorizontalLine
from .base import Window

HEADER_X = 1
HEADER_Y = 1
HEADER_HEIGHT = SCREEN_HEIGHT - HEADER_Y

class Header(Window):

    def __init__(self):
        super().__init__(
            Rectangle(HEADER_X, HEADER_Y, SCREEN_WIDTH, HEADER_HEIGHT)
        )
        self.label = Label(1, self.rect.y, text="MoDEM - Version: Alpha")

    def render(self) -> list[Mixel]:
        """Affiche le footer

        Cette méthode est appelée dès que l’on veut afficher l’élément.
        """
        return  self.label.render() \
            + HorizontalLine(1, self.rect.y+1, self.rect.width, type='top').render()