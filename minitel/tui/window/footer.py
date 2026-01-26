import os

from .base import Window
from .line import HorizontalLine
from .label import Label
from minitel.tui.core import Mixel, Rectangle
from minitel.tui.core.config import SCREEN_HEIGHT, SCREEN_WIDTH

FOOTER_X = 1
FOOTER_Y = 23
FOOTER_HEIGHT = SCREEN_HEIGHT - FOOTER_Y

class Footer(Window):

    def __init__(self):
        super().__init__(
            Rectangle(FOOTER_X, FOOTER_Y, SCREEN_WIDTH, FOOTER_HEIGHT)
        )
        self.label = Label(1, self.rect.y+1, text=os.path.basename(__file__))

    def update(self, path: str = ''):
        self.label.text = path

    def render(self) -> list[Mixel]:
        """Affiche le footer

        Cette méthode est appelée dès que l’on veut afficher l’élément.
        """
        return HorizontalLine(1, self.rect.y, self.rect.width, type='middle').render() \
            + self.label.render()


