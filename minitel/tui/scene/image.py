
from PIL import Image

from minitel.ImageMinitel import ImageMinitel
from minitel.tui.core import Rectangle
from minitel.tui.core.config import SCREEN_HEIGHT, SCREEN_WIDTH
from minitel.tui.core.image import ImageMinitelMixels, quantify_with_kmeans
from minitel.tui.keyboard import Key, KeyboardController
from minitel.tui.scene.manager import SceneManager
from minitel.tui.window.image import WindowImage
from .base import SceneBase
from minitel.tui.graphics import Graphics

class SceneImage(SceneBase):

    def __init__(self, image_path: str):
        super().__init__()
        self.initialize(image_path)

    def update(self):
        _, key = KeyboardController.poll()
        return key
    
    def initialize(self, image_path: str):
        image = WindowImage(Rectangle(1, 1, 2*SCREEN_WIDTH, 3*SCREEN_HEIGHT), image_path)
        image.set_handler(Key.CANCEL, self.return_back)
        self.windows['image'] = image
        # Register into the KeyboardController
        KeyboardController.register(image)
	
    def return_back(self):
        print("Here")
        SceneManager.return_to_caller()
    
    def render(self):
        Graphics.update(self.windows['image'].mixels)
        