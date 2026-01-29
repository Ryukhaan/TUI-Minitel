from minitel.tui.core.config import SCREEN_HEIGHT, SCREEN_WIDTH
from minitel.tui.core import Effect, Mixel, Rectangle, Color
from minitel.tui.keyboard import Key
from minitel.tui.window.ops import draw_text

class Window:
    """Classe de base pour la création d’élément d’interface utilisateur

    Cette classe fournit un cadre de fonctionnement pour la création d’autres
    classes pour réaliser une interface utilisateur.

    Elle instaure les attributs suivants :

    - x et y : coordonnées haut gauche de l’élément
    - width et height : dimensions en caractères de l’élément
    """
    def __init__(self, rect: Rectangle):
        # Un élément UI occupe une zone rectangulaire de l’écran du Minitel
        self.rect = Rectangle(
            max(1, min(rect.x, SCREEN_WIDTH)),
            max(1, min(rect.y, SCREEN_HEIGHT)),
            min(rect.width, SCREEN_WIDTH - rect.x + 1),
            min(rect.height, SCREEN_HEIGHT - rect.y + 1)
        )
    
    def render(self) -> list[Mixel]:
        """
        Retourne la liste de Mixels à afficher,
        chaque widget doit gérer le clipping dans sa propre méthode.
        """
        raise NotImplementedError()
    