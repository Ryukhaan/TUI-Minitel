import os

from minitel.tui.core.state import GraphicState
from minitel.tui.window.ops import draw_text, draw_line

from minitel.tui.window.base import Window
# from ...tui.window.line import HorizontalLine
# from ...tui.window.label import Label
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
        self.labels = [
            "Guide",
            "Sommaire",
            "Twitch"
        ]

    def update(self):
        pass

    def render(self) -> list[Mixel]:
        """Affiche le footer

        Cette méthode est appelée dès que l’on veut afficher l’élément.
        """
        mixels = []
        mixels += draw_line(1, self.rect.y, self.rect.width, type='middle')
        dx = 1
        for label in self.labels:
            shortcut = label[0]
            mixels += draw_text(dx, self.rect.y+1, shortcut, state=GraphicState(invert=True))
            dx += 1
            remainder = label[1:]
            mixels += draw_text(dx, self.rect.y + 1, remainder, state=GraphicState(invert=False))
            dx += len(remainder) + 1
        return mixels


