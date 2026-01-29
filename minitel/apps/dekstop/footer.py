import os

from minitel.tui.core.effect import Effect
from minitel.tui.window.ops import draw_text

from ...tui.window.base import Window
from ...tui.window.line import HorizontalLine
from ...tui.window.label import Label
from minitel.tui.core import Mixel, Rectangle
from minitel.tui.core.config import SCREEN_HEIGHT, SCREEN_WIDTH

FOOTER_X = 1
FOOTER_Y = 23
FOOTER_HEIGHT = SCREEN_HEIGHT - FOOTER_Y

class Footer(Window):

    def __init__(self, label: str = ""):
        super().__init__(
            Rectangle(FOOTER_X, FOOTER_Y, SCREEN_WIDTH, FOOTER_HEIGHT)
        )
        self.label = label
        self.wait = 30
        self.wait_pause = 120   # pause longue aux extrémités
        self.timestep = 0
        self.delta = 0
        self._pause = True

    def update(self):
        # Choix du tempo selon l'état
        current_wait = self.wait_pause if self._pause else self.wait
        self.timestep = (self.timestep + 1) % current_wait

        if self.timestep != 0:
            return False

        # Fin de pause → on repart
        if self._pause:
            self._pause = False

        # Avance normale du texte
        self.delta += 1

        max_delta = max(0, len(self.label) - self.rect.width)

        # Arrivé à la fin → pause longue
        if self.delta == max_delta:
            self.delta = max_delta
            self._pause = True
        elif self.delta > max_delta:
            self.delta = 0
            self._pause = True
        return True

    def render(self) -> list[Mixel]:
        """Affiche le footer

        Cette méthode est appelée dès que l’on veut afficher l’élément.
        """
        hline = draw_text(1, self.rect.y, "," * self.rect.width, effect=Effect.SEMIGRAPHIQUE)
        if len(self.label) > self.rect.width:
            text = self.label[self.delta:self.delta+self.rect.width]
        else:
            text = self.label
        text.rjust(self.rect.width, " ")
        mtext = draw_text(1, self.rect.y+1, text, effect=Effect.NONE)
        return hline + mtext


