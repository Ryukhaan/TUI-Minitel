from pathlib import Path

from minitel.tui.core import Rectangle
from minitel.tui.telinfo import TeleinformatiqueRenderer
from minitel.tui.keyboard import Key, KeyboardController
from minitel.tui.scene.base import SceneBase
from minitel.tui.scene.manager import SceneManager
from minitel.tui.graphics import Graphics

from .term_window import TerminalWindow


class TerminalScene(SceneBase):

    def __init__(self, cwd: Path = None):
        super().__init__()
        self._renderer = TeleinformatiqueRenderer(Graphics._instance.minitel)

        rect = Rectangle(1, 1,
                         self._renderer.COLS,
                         self._renderer.ROWS)
        term = TerminalWindow(rect, cwd or Path.home(), self._renderer)
        term.set_handler('cancel', self._on_cancel)
        self.windows['terminal'] = term
        KeyboardController.register(term)

    # ------------------------------------------------------------------
    # Cycle de vie
    # ------------------------------------------------------------------

    def on_enter(self):
        self._renderer.enter()
        self.windows['terminal'].active = True
        self.windows['terminal']._dirty = True

    def on_exit(self):
        self.windows['terminal'].active = False
        self._renderer.exit()

    def on_resume(self):
        self._renderer.enter()
        self.windows['terminal'].active = True
        self.windows['terminal']._dirty = True

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    def _on_cancel(self):
        self.windows['terminal'].active = False
        SceneManager.return_to_caller()

    def _open_launcher(self):
        from minitel.apps.launcher.launcher import LauncherScene
        from minitel.apps.registry import get_apps
        self.windows['terminal'].active = False
        SceneManager.call(LauncherScene, get_apps())

    # ------------------------------------------------------------------
    # Boucle principale
    # ------------------------------------------------------------------

    def update(self):
        if SceneManager._scene != self:
            return None
        _, key = KeyboardController.poll()
        if key == Key.SOMMAIRE:
            self._open_launcher()
            return True
        term = self.windows['terminal']
        return key or term._dirty

    def render(self):
        if SceneManager._scene != self:
            return
        r = self._renderer
        term = self.windows['terminal']

        # Zone de sortie (lignes 1 .. ROWS-2)
        r.render_lines(term.visible_output(), start_row=1)

        # Séparateur
        r.separator(r.ROWS - 1)

        # Ligne de saisie
        r.render_input(r.ROWS, '$ ', term.input_buffer)

        r.flush()
        term._dirty = False
