import os
from pathlib import Path
from copy import deepcopy

from minitel.constantes import CAN, CSI, LF, US
from minitel.tui.core import Rectangle
from minitel.tui.core.config import SCREEN_WIDTH
from minitel.tui.keyboard import Key, KeyboardController
from minitel.tui.scene.manager import SceneManager
from minitel.tui.scene.base import SceneBase
from minitel.tui.window import Footer, Header
from minitel.tui.graphics import Graphics

from minitel.apps.miw.miw import MinitelImageViewer

from .menu_window import MenuDesktopWindow

class Desktop(SceneBase):

    def __init__(self, start_path: str = '.'):
        super().__init__()
        self.windows = {}
        self.cwd = Path(start_path).resolve()
        self._initialize()
        self.refresh()
        self._update_files()

    def on_resume(self):
        self.windows['menu'].active = True
    
    def on_enter(self):
        pass

    def on_exit(self):
        pass

    def update(self):
        _, key = KeyboardController.poll()
        return key
    
    def _initialize(self):
        self.windows['header'] = Header()
        self.windows['footer'] = Footer()
        self.create_menu_window()

    def create_menu_window(self):
        menu = MenuDesktopWindow(Rectangle(1, 3, 1, SCREEN_WIDTH))
        menu.set_handler("ok", self.on_item_ok)
        menu.set_handler("cancel", self.on_item_cancel)
        menu.set_handler("next_page", self.refresh)
        menu.set_handler("prev_page", self.refresh)

        self.windows['menu'] = menu
        # Register into the KeyboardController
        KeyboardController.register(menu)

    def on_item_ok(self, item):
        path = self.cwd / item
        if os.path.isdir(path):
            self.cwd = path
            self.refresh()
            self._update_files()
        if os.path.isfile(path):
            if path.suffix in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
                self.windows['menu'].active = False
                path: Path = deepcopy(Path(path))
                SceneManager.call(MinitelImageViewer, path.parent.resolve())
    
    def on_item_cancel(self):
        """Appelé quand CANCEL / ESC"""
        parent = Path(self.cwd).parent.resolve()
        if parent and parent != self.cwd:
            self.cwd = parent
            self.refresh()
            self._update_files()
    
    def _update_files(self):
        # Mise à jour des items
        menu: MenuDesktopWindow = self.windows['menu']
        paths = [
            (self.cwd / name).resolve()
            for name in os.listdir(self.cwd)
        ]
        paths.sort(key=lambda p: (not p.is_dir(), p.name.lower()))
        menu.items = paths
        menu.rect.height = len(menu.items)
        menu.page = 0      # revenir à la première page
        menu.select(0)     # remettre le curseur sur le premier item
        menu._dirty = True # invalide le cache de pagination

    def refresh(self):
        """Recréé le menu avec le contenu du dossier courant"""
        menu: MenuDesktopWindow = self.windows['menu']
        # Cleaning
        Graphics.reset_attributes()
        Graphics.direct_send([US, 0x40 + menu.rect.y , 0x41])
        for i in range(len(menu.paged_items[0])):
            print(menu.rect.y, i)
            Graphics.direct_send([CSI, 0x4B, LF])
            Graphics._instance.buffer.reset_row(menu.rect.y + i - 1)
        Graphics.flush()
    
    def render(self):
        if SceneManager._scene != self:
            return
        mixels = []
        for window in self.windows.values():
            mixels.extend(window.render())
        Graphics.update(mixels)
        