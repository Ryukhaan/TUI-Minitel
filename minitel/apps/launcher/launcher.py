from minitel.tui.core import GraphicState, Mixel, Rectangle, Color
from minitel.tui.core.config import SCREEN_WIDTH, SCREEN_HEIGHT
from minitel.tui.keyboard import Key, KeyboardController
from minitel.tui.scene.base import SceneBase
from minitel.tui.scene.manager import SceneManager
from minitel.tui.graphics import Graphics
from minitel.tui.window.base import Window
from minitel.tui.window.ops import draw_text, draw_line

# Position verticale centrée
_TOP = 8
_TITLE_ROW = _TOP + 1
_DIVIDER_ROW = _TOP + 2
_ITEMS_START = _TOP + 4   # première ligne d'item
_BOTTOM = _ITEMS_START    # sera recalculé dynamiquement
_FOOTER_ROW = SCREEN_HEIGHT


class LauncherWindow(Window):

    def __init__(self, apps: list[tuple[str, callable]]):
        super().__init__(Rectangle(1, 1, SCREEN_WIDTH, SCREEN_HEIGHT))
        self.apps = apps          # [(label, factory_fn), ...]
        self.index = 0
        self.active = True
        self.handlers: dict = {}
        self._dirty = True

    def set_handler(self, name: str, callback):
        self.handlers[name] = callback

    def update(self) -> bool:
        return False

    def handle_key(self, key) -> bool:
        if not self.active or key is None:
            return False
        if key == Key.UP:
            self.index = (self.index - 1) % len(self.apps)
            self._dirty = True
            return True
        if key == Key.DOWN:
            self.index = (self.index + 1) % len(self.apps)
            self._dirty = True
            return True
        if key == Key.ENTER:
            if 'select' in self.handlers:
                self.handlers['select'](self.index)
            return True
        if key == Key.CANCEL:
            if 'cancel' in self.handlers:
                self.handlers['cancel']()
            return True
        return False

    def render(self) -> list[Mixel]:
        mixels = []

        # Lignes vides pour centrer
        blank = " " * SCREEN_WIDTH
        for row in range(1, _TOP):
            mixels.extend(draw_text(1, row, blank))

        # Bordure haute
        mixels.extend(draw_line(1, _TOP, SCREEN_WIDTH, type='top'))

        # Titre
        title = "APPLICATIONS"
        title_padded = title.center(SCREEN_WIDTH)
        mixels.extend(draw_text(1, _TITLE_ROW, title_padded,
                                state=GraphicState(invert=True)))

        # Séparateur
        mixels.extend(draw_line(1, _DIVIDER_ROW, SCREEN_WIDTH, type='middle'))

        # Items
        for i, (label, _) in enumerate(self.apps):
            row = _ITEMS_START + i
            prefix = " > " if i == self.index else "   "
            text = (prefix + label).ljust(SCREEN_WIDTH)
            state = GraphicState(fg=Color.WHITE, invert=(i == self.index))
            mixels.extend(draw_text(1, row, text, state=state))

        # Lignes vides après les items
        bottom_border = _ITEMS_START + len(self.apps)
        for row in range(_ITEMS_START + len(self.apps), bottom_border + 1):
            mixels.extend(draw_text(1, row, blank))

        # Bordure basse
        mixels.extend(draw_line(1, bottom_border + 1, SCREEN_WIDTH, type='bottom'))

        # Lignes vides jusqu'au footer
        for row in range(bottom_border + 2, _FOOTER_ROW):
            mixels.extend(draw_text(1, row, blank))

        # Aide en bas
        help_text = " ENTREE: ouvrir   ANNUL: retour"
        mixels.extend(draw_text(1, _FOOTER_ROW, help_text.ljust(SCREEN_WIDTH),
                                state=GraphicState(fg=Color.GRAY_4)))

        return mixels


class LauncherScene(SceneBase):

    def __init__(self, apps: list[tuple[str, callable]]):
        super().__init__()
        win = LauncherWindow(apps)
        win.set_handler('select', self._on_select)
        win.set_handler('cancel', self._on_cancel)
        self.windows['launcher'] = win
        KeyboardController.register(win)

    def on_enter(self):
        self.windows['launcher'].active = True
        self.windows['launcher']._dirty = True

    def on_exit(self):
        self.windows['launcher'].active = False

    def on_resume(self):
        self.windows['launcher'].active = True
        self.windows['launcher']._dirty = True

    def _on_select(self, index: int):
        self.windows['launcher'].active = False
        _, factory = self.windows['launcher'].apps[index]
        SceneManager.switch_to(factory())

    def _on_cancel(self):
        self.windows['launcher'].active = False
        SceneManager.return_to_caller()

    def update(self):
        if SceneManager._scene != self:
            return None
        _, key = KeyboardController.poll()
        win = self.windows['launcher']
        return key or win._dirty

    def render(self):
        if SceneManager._scene != self:
            return
        win = self.windows['launcher']
        Graphics.update(win.render())
        win._dirty = False
