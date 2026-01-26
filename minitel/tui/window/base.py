from minitel.tui.core.config import SCREEN_HEIGHT, SCREEN_WIDTH
from minitel.tui.core import Effect, Mixel, Rectangle
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
    
class WindowSelectable(Window):

    def __init__(self, rect):
        super().__init__(rect)
        self.index: int = 0
        self._last_index: int = -1
        self.handlers: dict = {}
        self.items = []
        self.active: bool = True
        self._last_rendered: list[Mixel] = []


    @property
    def current_item(self):
        return self.items[self.index]
    
    # ------------------------
    # Handlers
    # ------------------------
    def set_handler(self, key_name: str, callback: callable):
        """Associe une touche/événement à une méthode"""
        self.handlers[key_name] = callback

    def handle_key(self, key: str) -> bool:
        """
        Renvoi True si la key est handle par la window.
        Sinon False.
        
        :param self: Description
        :param key: Description
        :return: Description
        :rtype: bool
        """
        if key in self.handlers:
            self.handlers[key]()
            return True
        return False

    def handle_ok(self):
        try:
            self.handlers["ok"]()
        except KeyError:
            print(f"No key 'ok' found in handlers ({self.handlers.keys()})")

    def handle_cancel(self):
        try:
            self.handlers["cancel"]()
        except:
            print(f"No key 'cancel' found in handlers ({self.handlers.keys()})")

    # ------------------------
    # Cursor / Index management
    # ------------------------
    def select(self, index: int) -> None:
        """
        Fixe l'index à la valeur définie (équivalent à window.index = index)
        
        :param self: Description
        :param index: Description
        """
        self.index = index
    
    def unselect(self) -> None:
        """
        Déselection la fenêtre (index=-1)
        
        :param self: Description
        """
        self.index = -1

    def _update_by(self, value: int) -> bool:
        if len(self.items) > 0:
            self.index = (self.index + value) % len(self.items)
            return True
        return False
    
    def cursor_up(self):
        return self._update_by(-1)
    
    def cursor_down(self):
        return self._update_by(1)

    def __setitem__(self, key, value):
        self.handlers[key] = value
    
    def __getitem__(self, key):
        return self.handlers[key]

    # ------------------------
    # Update / Polling
    # ------------------------
    def handle_key(self, key):
        if not self.active:
            return False

        if key == Key.UP:
            return self.cursor_up()
        elif key == Key.DOWN:
            return self.cursor_down()
        elif key == Key.ENTER:
            self.handle_ok()
            return True
        elif key == Key.CANCEL:
            self.handle_cancel()
            return True
        return False
    
    # ------------------------
    # Rendering
    # ------------------------
    def render(self, full: bool = False) -> list[Mixel]:
        mixels = []
        
        if full:
            cleared = [Mixel(m.x, m.y, ' ') for m in self._last_rendered]

        for row, item in enumerate(self.items):
            mixels.extend(
                draw_text(self.rect.x, self.rect.y + row,
                          item,
                          effect= Effect.INVERT if self.index == row else Effect.NONE)
            )
        
        if full:
            self._last_rendered = mixels
            return cleared + mixels
        else:
            return mixels
    
