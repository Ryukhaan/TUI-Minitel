
from pathlib import Path

from minitel.constantes import SI
from minitel.tui.core import Rectangle
from minitel.tui.core.config import SCREEN_HEIGHT, SCREEN_WIDTH
from minitel.tui.keyboard import Key, KeyboardController
from minitel.tui.scene.manager import SceneManager
from minitel.tui.scene.base import SceneBase
from minitel.tui.graphics import Graphics

from .miwindow import WindowImage

class MinitelImageViewer(SceneBase):

    def __init__(self, directory_path: Path):
        super().__init__()
        self.initialize(directory_path.resolve())

    def on_resume(self):
        pass
    
    def on_enter(self):
        pass

    def on_exit(self):
        Graphics.direct_send([SI])

    def update(self):
        if SceneManager._scene != self:
            return None
        _, key = KeyboardController.poll()
        return key
    
    def initialize(self, directory_path: str):
        image = WindowImage(Rectangle(1, 1, 2*SCREEN_WIDTH, 3*SCREEN_HEIGHT), directory_path)
        image.set_handler(Key.CANCEL, self.return_back)
        image.active = True
        self.windows['image'] = image
        # Register into the KeyboardController
        KeyboardController.register(image)

    def return_back(self):
        self.windows['image'].active = False
        Graphics.clear() 
        SceneManager.return_to_caller()
    
    def render(self):
        if SceneManager._scene != self:
            return
        if self.windows['image']._has_new_seq:
            Graphics.direct_send(self.windows['image'].sequence)
            self.windows['image']._has_new_seq = False

        