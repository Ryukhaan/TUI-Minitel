from pathlib import Path

from minitel.tui.core import Rectangle
from minitel.tui.core.config import SCREEN_WIDTH, SCREEN_HEIGHT
from minitel.tui.keyboard import Key, KeyboardController
from minitel.tui.scene.base import SceneBase
from minitel.tui.scene.manager import SceneManager
from minitel.tui.graphics import Graphics

from .term_window import TerminalWindow


class TerminalScene(SceneBase):

    def __init__(self, cwd: Path = None):
        super().__init__()
        rect = Rectangle(1, 1, SCREEN_WIDTH, SCREEN_HEIGHT)
        term = TerminalWindow(rect, cwd or Path.home())
        term.set_handler('cancel', self._on_cancel)
        self.windows['terminal'] = term
        KeyboardController.register(term)

    def on_enter(self):
        self.windows['terminal'].active = True
        self.windows['terminal']._dirty = True

    def on_exit(self):
        self.windows['terminal'].active = False

    def on_resume(self):
        self.windows['terminal'].active = True
        self.windows['terminal']._dirty = True

    def _on_cancel(self):
        self.windows['terminal'].active = False
        Graphics.clear()
        SceneManager.return_to_caller()

    def update(self):
        if SceneManager._scene != self:
            return None
        _, key = KeyboardController.poll()
        if key == Key.SOMMAIRE:
            self._open_launcher()
            return True
        term = self.windows['terminal']
        return key or term._dirty

    def _open_launcher(self):
        from minitel.apps.launcher.launcher import LauncherScene
        from minitel.apps.registry import get_apps
        self.windows['terminal'].active = False
        SceneManager.call(LauncherScene, get_apps())

    def render(self):
        if SceneManager._scene != self:
            return
        term = self.windows['terminal']
        Graphics.update(term.render())
        term._dirty = False
