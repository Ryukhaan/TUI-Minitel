# from .widget.widget import Widget
from minitel.constantes import ESC, SI
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
    
    @classmethod
    def update(cls, mixels, cursor_pos = None):
        if cls._instance is None:
            raise RuntimeError("Graphics.init() must be called first")
        return cls._instance._update_instance(mixels, cursor_pos)

    def _update_instance(cls, mixels: list, cursor_pos: tuple[int, int] = None) -> None:
        # Clipped in range
        clipped = [
            m for m in mixels
            if 1 <= m.x <= cls.width and 1 <= m.y <= cls.height
        ]

        # 2. Calcul les changements
        buffer = cls.buffer.apply(clipped)

        # 3. Encodage
        for payload in cls.encoder.encode(buffer):
            cls.minitel.send(payload)
            cls.flush()
    
    @classmethod
    def clear(cls, kind: str = 'tout'):
        if cls._instance is None:
            raise RuntimeError("Graphics.init() must be called first")
        cls._instance.minitel.efface(kind)

    @classmethod
    def direct_send(cls, sequence):
        if cls._instance is None:
            raise RuntimeError("Graphics.init() must be called first")
        cls._instance.minitel.send(sequence)

    @classmethod
    def clear_buffer(cls):
        if cls._instance is None:
            raise RuntimeError("Graphics.init() must be called first")
        cls._instance.buffer.clear()

    @classmethod
    def flush(cls):
        if cls._instance is None:
            raise RuntimeError("Graphics.init() must be called first")
        cls._instance.minitel.flush()

    @classmethod
    def reset_attributes(cls):
        if cls._instance is None:
            raise RuntimeError("Graphics.init() must be called first")
        cls._instance.minitel.send([
            ESC, 0x59,   # underline off
            ESC, 0x49,   # blink off
            ESC, 0x5c,   # invert off
            SI,          # mode alpha
        ])