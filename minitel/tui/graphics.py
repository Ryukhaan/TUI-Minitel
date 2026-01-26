# from .widget.widget import Widget
from .buffer import MinitelBuffer
from .encoder import MinitelEncoder
from .core.config import SCREEN_WIDTH, SCREEN_HEIGHT


class Graphics:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
        
    def __init__(self, minitel, 
                 width: int = SCREEN_WIDTH,
                 height: int = SCREEN_HEIGHT,
                 buffer: MinitelBuffer = MinitelBuffer(), 
                 encoder: MinitelEncoder = MinitelEncoder()):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True

        # self.widgets: dict[str, Widget] = {}
        self.buffer = buffer
        self.minitel = minitel
        self.encoder = encoder
        self.width = width
        self.height = height
        self.active_key: str | None = None
        self._last_cursor_pos: tuple[int, int] | None = [0,0]

    @classmethod
    def init(cls, minitel):
        """Initialisation singleton"""
        return cls(minitel)
    
    # @property
    # def active_widget(self) -> None | Widget:
    #     if self.active_key:
    #         try:
    #             return self.widgets[self.active_key]
    #         except KeyError:
    #             return None
    
    # def set_active(self, key: str):
    #     if key in self.widgets.keys():
    #         self.active_key = key
    #         x, y = self.get_cursor_position()
    #         self.minitel.position(x, y)
    #     else:
    #         raise KeyError("Pas de widget de ce nom !")

    # def __setitem__(self, key, widget):
    #     if 1 <= widget.x <= self.width  and 1 <= widget.y <= self.height:
    #         self.widgets[key] = widget
    #         if self.active_key is None:
    #             self.active_key = key
    #     else:
    #         raise ValueError(f"Out of Bound widget ({widget.x, widget.y}) , should be less than (0, {SCREEN_WIDTH}) and (0, {SCREEN_HEIGHT})")

    # def __getitem__(self, key):
    #     return self.widgets[key]
    
    # def __xor__(self, other):
    #     return self.widgets.items() ^ other.widgets.items()

    # def get_cursor_position(self):
    #     widget = self.active_widget
    #     if widget is None:
    #         return None
    #     x = widget.x + getattr(widget, "cursor_x", 0)
    #     y = widget.y + getattr(widget, "cursor_y", 0)
    #     return x, y
    
    @classmethod
    def update(cls, mixels, cursor_pos = None):
        if cls._instance is None:
            raise RuntimeError("Graphics.init() must be called first")
        return cls._instance._update_instance(mixels, cursor_pos)

    def _update_instance(cls, mixels: list, cursor_pos: tuple[int, int] = None) -> None:
        
        # 1. Rendu des widgets
        # mixels = []
        # for widget in widgets.values():
        #     for mixel in widget.render():
        #     # clip final : ne pas dépasser l’écran
        #         if 1 <= mixel.x <= self.width and 1 <= mixel.y <= self.height:
        #             mixels.append(mixel)
        # 1. Clip écran

        clipped = [
            m for m in mixels
            if 1 <= m.x <= cls.width and 1 <= m.y <= cls.height
        ]

        # 2. Calcul les changements
        buffer = cls.buffer.apply(clipped)

        # 3. Encodage
        payload = cls.encoder.encode(buffer)

        # 4. Envoi
        cls.minitel.send(payload)

        # 5. Mise à jour curseur
        # if cursor_pos and cursor_pos != self._last_cursor_pos:
        #     x, y = cursor_pos
        #     delta_x = x - self._last_cursor_pos[0]
        #     delta_y = y - self._last_cursor_pos[1]
        #     seq = self.encoder._encode_position(delta_x, delta_y, relatif=True)
        #     self.minitel.send(seq)
        #     self._last_cursor_pos = cursor_pos