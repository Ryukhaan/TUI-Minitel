from minitel.tui.core.image import ImageMinitelMixels, quantify_with_kmeans
from minitel.tui.core.mixel import Mixel
from minitel.tui.core.rectangle import Rectangle
from minitel.tui.keyboard import Key
from minitel.tui.window.base import Window

from PIL import Image

class WindowImage(Window):

    def __init__(self, rect, im_path: str):
        super().__init__(rect)
        self.rect = rect
        self.im_path = im_path
        self.handlers: dict = {}
        self.mixels = []
        self.init_image()

    def init_image(self):
        image = Image.open(self.im_path)
        image = image.resize((self.rect.width, self.rect.height), Image.Resampling.LANCZOS)
        image = image.convert("L")
        image_q, _, _ = quantify_with_kmeans(image)

        img_mixels = ImageMinitelMixels()
        img_mixels.importer(image_q)
        self.mixels = img_mixels.render()

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

    def handle_cancel(self):
        try:
            self.handlers["cancel"]()
        except:
            print(f"No key 'cancel' found in handlers ({self.handlers.keys()})")
    
    # ------------------------
    # Rendering
    # ------------------------
    def render(self) -> list[Mixel]:
       return self.mixels