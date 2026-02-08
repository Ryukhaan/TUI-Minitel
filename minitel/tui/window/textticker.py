from minitel.tui.core.mixel import Mixel
from minitel.tui.window.base import Window
from minitel.tui.window.ops import draw_text


class TextTicker(Window):

    def __init__(self, rect, label: str = "",
                 wait: int = 30,
                 wait_pause: int = 120):
        super().__init__(rect)
        self.label = label
        self.wait = wait
        self.wait_pause = wait_pause   # pause longue aux extrémités
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

    def get_current_text(self):
        if len(self.label) > self.rect.width:
            text = self.label[self.delta:self.delta+self.rect.width]
        else:
            text = self.label
        return text.rjust(self.rect.width, " ")

    def render(self) -> list[Mixel]:
        """Affiche le footer

        Cette méthode est appelée dès que l’on veut afficher l’élément.
        """
        return draw_text(1, self.rect.y+1, self.get_current_text())
