import os

from .widget import Widget, HorizontalLine, Label
from .core import Color, Effect, Mixel
from .config import SCREEN_HEIGHT, SCREEN_WIDTH

class Header(Widget):
    """Classe Header.

    Commande Disponible
    """
    def __init__(self, x: int = 1, y: int = 1,
                text: str = '', 
                color: Color = Color.WHITE, 
                effect: Effect = None):
        super().__init__(x, y, len(text), 1, color)
        self.text = text
        self.effect = effect

    def render(self) -> list[Mixel]:
        """Affiche le label

        Cette méthode est appelée dès que l’on veut afficher l’élément.
        """
        mixel_array: list[Mixel] = super().render()
        for i, char in enumerate(self.text):
            mixel_array.append(Mixel(self.x+i, self.y, char))
        return mixel_array
    
class Footer(Widget):

    def __init__(self, x: int = 1, y: int = 23,
            color: Color = Color.WHITE, 
            effect: Effect = Effect.NONE):
        super().__init__(x, y, SCREEN_WIDTH, 2, color, effect)
        self.separator = HorizontalLine(1, self.y, SCREEN_WIDTH, type='middle')
        self.label = Label(1, self.y+1, text=os.path.basename(__file__))

    def update(self, path: str = ''):
        self.label.text = path

    def render(self) -> list[Mixel]:
        """Affiche le footer

        Cette méthode est appelée dès que l’on veut afficher l’élément.
        """
        return self.separator.render() + self.label.render()


