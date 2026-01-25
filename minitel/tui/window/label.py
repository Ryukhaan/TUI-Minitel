from .base import Window
from .ops import draw_text
from minitel.tui.core import Color, Effect, Mixel, Rectangle

class Label(Window):
    """Classe de gestion de label

    Elle ne fait qu’afficher un texte d’une seule ligne.
    """
    def __init__(self, x: int, y: int,
                text: str = '', 
                color: Color = Color.WHITE, 
                effect: Effect = Effect.NONE):
        super().__init__(Rectangle(x, y, len(text), 1))
        self.color = color
        self.effect = effect
        self.text = text

    def render(self) -> list[Mixel]:
        """Affiche le label

        Cette méthode est appelée dès que l’on veut afficher l’élément.
        """
        return draw_text(self.rect.x, self.rect.y, self.text, self.color, self.effect)
