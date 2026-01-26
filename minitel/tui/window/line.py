from .label import Label
from minitel.tui.core import Color, Effect, Mixel

class HorizontalLine(Label):
    """Classe de gestion de label

    Elle ne fait qu’afficher un texte d’une seule ligne.
    """
    def __init__(self, x: int, y: int, length: int = 1, type: str = 'top',
                color: Color = Color.WHITE, 
                effect: Effect = Effect.SEMIGRAPHIQUE):
        if type == 'top':
            text = "#" * length
        elif type == 'middle':
            text = "," * length
        elif type == 'bottom':
            text = "p" * length
        else:
            text = f"{type}" * length
        super().__init__(x, y, text, color, effect)


    def render(self) -> list[Mixel]:
        """Affiche le label

        Cette méthode est appelée dès que l’on veut afficher l’élément.
        """
        return super().render()
