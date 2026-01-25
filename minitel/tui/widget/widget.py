from tui.core.core import Color, Effect, Mixel
from tui.core.config import SCREEN_WIDTH, SCREEN_HEIGHT

class Widget:
    """Classe de base pour la création d’élément d’interface utilisateur

    Cette classe fournit un cadre de fonctionnement pour la création d’autres
    classes pour réaliser une interface utilisateur.

    Elle instaure les attributs suivants :

    - x et y : coordonnées haut gauche de l’élément
    - width et height : dimensions en caractères de l’élément
    - color : couleur d’avant-plan/des caractères
    """
    def __init__(self, x: int, y: int, width: int, height: int, color: int | Color, effect: Effect):
        # Un élément UI occupe une zone rectangulaire de l’écran du Minitel
        self.x = max(1, min(x, SCREEN_WIDTH))
        self.y = max(1, min(y, SCREEN_HEIGHT))
        self.width = min(width, SCREEN_WIDTH - self.x + 1)
        self.height = min(height, SCREEN_HEIGHT - self.y + 1)
        self.color = color
        self.effect = effect
    
    def render(self) -> list[Mixel]:
        """
        Retourne la liste de Mixels à afficher,
        chaque widget doit gérer le clipping dans sa propre méthode.
        """
        raise NotImplementedError()


class TextInput:
    def __init__(self, x, y, width, height=1):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.lines = [""] * self.height
        self.cursor_x, self.cursor_y = 0, 0

        # mapping des touches spéciales vers les méthodes
        self.keymap = {
            "BACKSPACE": self._backspace,
            "LEFT": self._left,
            "RIGHT": self._right,
            "UP": self._up,
            "DONW": self._down,
            "ENTER": self._enter
        }

    def handle_key(self, key):
        """Met à jour le texte en fonction de la touche"""
        if key in self.keymap:
            return self.keymap[key]()
        elif isinstance(key, str) and len(key) == 1:
            return self._insert_char(key)

    # Handlers spécifiques
    def _backspace(self):
        if self.cursor > 0:
            self.text = self.text[:self.cursor-1] + self.text[self.cursor:]
            self.cursor_x -= 1

    def _left(self):
        if self.cursor_x > 0:
            self.cursor_x -= 1
        elif self.cursor_y > 0:
            self.cursor_y -= 1
            self.cursor_x = len(self.lines[self.cursor_y])

    def _right(self):
        line_len = len(self.lines[self.cursor_y])
        if self.cursor_x < line_len:
            self.cursor_x += 1
        elif self.cursor_y < len(self.lines) - 1:
            self.cursor_y += 1
            self.cursor_x = 0

    def _up(self):
        if self.cursor_y > 0:
            self.cursor_y -= 1
            self.cursor_x = min(self.cursor_x, len(self.lines[self.cursor_y]))

    def _down(self):
        if self.cursor_y < len(self.lines) - 1:
            self.cursor_y += 1
            self.cursor_x = min(self.cursor_x, len(self.lines[self.cursor_y]))

    def _enter(self):
        return self.text  # soumission

    def _insert_char(self, ch):
        line = self.lines[self.cursor_y]
        if len(line) < self.width:
            self.lines[self.cursor_y] = line[:self.cursor_x] + ch + line[self.cursor_x+1:]
            self.cursor_x += 1
            if self.cursor_x > self.width:
                self.cursor_x = 0
                self.cursor_y += 1

    def render(self):
        mixels = []
        for i, line in enumerate(self.lines[:self.height]):
            text_clipped = line[:self.width]
            for j, c in enumerate(text_clipped):
                mixels.append(Mixel(self.x + j, self.y + i, c))
        return mixels