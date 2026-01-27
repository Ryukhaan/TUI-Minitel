import os
import time

from minitel.tui.core import Rectangle
from minitel.tui.keyboard import Key, KeyboardController
from minitel.tui.scene.image import SceneImage
from minitel.tui.scene.manager import SceneManager
from minitel.tui.window.base import WindowSelectable
from .base import SceneBase
from minitel.tui.window import Footer, Header
from minitel.tui.graphics import Graphics

class Desktop(SceneBase):

    def __init__(self, start_path: str = '.'):
        super().__init__()
        self.windows = {}
        self.cwd = os.path.abspath(start_path)
        self.initialize()

    def update(self):
        _, key = KeyboardController.poll()
        menu: WindowSelectable = self.windows['menu']
        # Déplacement de curseur
        if key in [Key.UP, Key.DOWN]:
            Graphics.update(menu.render(full=False))  # seulement curseur
        # Changement de contenu
        elif key in [Key.ENTER, Key.CANCEL, Key.LEFT, Key.RIGHT]:
            self.refresh()  # réaffecte menu.items
            Graphics.update(menu.render(full=True))   # redessine tout
        return key
    
    def initialize(self):
        self.windows['header'] = Header()
        self.windows['footer'] = Footer()
        self.create_menu_window()

    def create_menu_window(self):
        menu = WindowSelectable(Rectangle(1, 3, 1, 1))
        menu.set_handler('ok', self.on_item_ok)
        menu.set_handler('cancel', self.on_item_cancel)
        self.windows['menu'] = menu
        self.refresh()
        # Register into the KeyboardController
        KeyboardController.register(menu)

    def on_item_ok(self, item):
        # file = self.windows['menu'].current_item
        path = os.path.join(self.cwd, item)
        if os.path.isdir(path):
            self.cwd = path
            self.refresh(reset_page=True)
        if os.path.isfile(path) and path[-3:] in ["png", "jpg"]:
            SceneManager.call(SceneImage, path)
    
    def on_item_cancel(self):
        """Appelé quand CANCEL / ESC"""
        parent = os.path.dirname(self.cwd)
        if parent and parent != self.cwd:
            self.cwd = parent
            self.refresh(reset_page=True)
    
    def refresh(self, reset_page: bool = False):
        """Recréé le menu avec le contenu du dossier courant"""
        menu: WindowSelectable = self.windows['menu']
        menu.items = os.listdir(self.cwd)
        menu.rect.height = len(menu.items)
        menu.rect.width = max((len(f) for f in menu.items), default=1)
        if reset_page:
            menu.page = 0      # revenir à la première page
        menu.select(0)     # remettre le curseur sur le premier item
        menu._dirty = True # invalide le cache de pagination
    
    def render(self):
        mixels = []
        for window in self.windows.values():
            mixels.extend(window.render())
        Graphics.update(mixels)
        