from minitel.tui.core.config import SCREEN_HEIGHT, SCREEN_WIDTH
from minitel.tui.core.mixel import Mixel
from minitel.tui.core.rectangle import Rectangle

from minitel.tui.window.ops import draw_text, draw_line
from minitel.tui.window.textticker import TextTicker

HEADER_X = 1
HEADER_Y = 1
HEADER_HEIGHT = SCREEN_HEIGHT - HEADER_Y

class Header(TextTicker):

    def __init__(self, label: str = ""):
        super().__init__(
            Rectangle(HEADER_X, HEADER_Y, SCREEN_WIDTH, HEADER_HEIGHT),
            label=label
        )

    def render(self) -> list[Mixel]:
        """Affiche le footer

        Cette méthode est appelée dès que l’on veut afficher l’élément.
        """
        mixels = []
        mixels += draw_text(1, self.rect.y, self.get_current_text())
        mixels += draw_line(1, self.rect.y+1, self.rect.width, type='middle')
        return mixels