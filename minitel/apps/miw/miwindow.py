from PIL import Image
import glob
import os

from minitel.tui.core.image import ImageMinitelMixels, quantify_with_kmeans
from minitel.tui.core.mixel import Mixel
from minitel.tui.keyboard import Key
from minitel.tui.window.base import Window

from .config import SUPPORTED_FORMAT

class WindowImage(Window):

    def __init__(self, rect, directory_path: str):
        super().__init__(rect)
        self.rect = rect
        # Collect all image files
        self.image_files = []
        for ext in SUPPORTED_FORMAT:
            self.image_files.extend(glob.glob(os.path.join(directory_path, ext)))
        # Selectable-like
        self.index = 0
        self.handlers: dict = {
            Key.LEFT: self.cursor_left,
            Key.RIGHT: self.cursor_right,
        }
        self.active: bool = False
        self.sequence = []
        self._has_new_seq: bool = False
        self.refresh()

    def refresh(self):
        self.sequence = []
        image = Image.open(self.image_files[self.index])
        image = image.resize((self.rect.width, self.rect.height), Image.Resampling.LANCZOS)
        image = image.convert("L")
        image_q, _, _ = quantify_with_kmeans(image)
        img_mixels = ImageMinitelMixels()
        self.sequence = img_mixels.importer(image_q)
        self._has_new_seq = True


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
        if not self.active:
            return False
        if key in self.handlers:
            self.handlers[key]()
            return True
        return False
    
    def cursor_left(self):
        self.index = (self.index - 1) % len(self.image_files)
        self.refresh()

    def cursor_right(self):
        self.index = (self.index + 1) % len(self.image_files)
        self.refresh()

    # ------------------------
    # Rendering
    # ------------------------
    def render(self) -> list[Mixel]:
    #    return self.mixels
        pass