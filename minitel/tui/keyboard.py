from enum import Enum, auto
from queue import Empty

from minitel.Sequence import Sequence

class Key(Enum):
    UP = auto()
    DOWN = auto()
    RIGHT = auto()
    LEFT = auto()
    ENTER = auto()
    CANCEL = auto()
    BACKSPACE = auto()
    SOMMAIRE = auto()

KEY_MAP = {
    (27, 79, 77): Key.ENTER,
    (13,): Key.ENTER,
    (27,): Key.CANCEL,
    (27, 91, 65): Key.UP,
    (27, 91, 66): Key.DOWN,
    (10,): Key.DOWN,
    (27, 91, 67): Key.RIGHT,
    (27, 91, 68): Key.LEFT,
    (8,): Key.BACKSPACE,
    # Touches de fonction Minitel (DC3/SEP = 0x13 + code)
    (19, 65): Key.ENTER,      # ENVOI
    (19, 69): Key.CANCEL,     # ANNULATION
    (19, 70): Key.SOMMAIRE,   # SOMMAIRE
    (19, 71): Key.BACKSPACE,  # CORRECTION
}

class KeyboardController:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, minitel):
        if getattr(self, '_initialized', False):
            return
        self._initialize = True
        self.minitel = minitel
        self.listeners = []

    @classmethod
    def init(cls, minitel):
        return cls(minitel)
    
    @classmethod
    def register(cls, listener):
        if cls._instance is None:
            raise RuntimeError("KeyboardController not initialized")
        cls._instance._register(listener)

    @classmethod
    def poll(cls):
        if cls._instance is None:
            raise RuntimeError("KeyboardController not initialized")
        try:
            seq = cls._instance.minitel.recevoir_sequence(bloque=False)
        except Empty:
            return False, None # rien à traiter pour le moment

        key = cls._instance._interpet(seq)
        changed = False
        for listener in list(cls._instance.listeners):
            if listener.handle_key(key):
                changed = True
                break  # touche consommée, on arrête la propagation
        return changed, key

    def _register(self, listener):
        self.listeners.append(listener)

    def _interpet(self, seq: Sequence):
        if not seq:
            return None
        vals = tuple(seq.valeurs)
        if vals in KEY_MAP:
            return KEY_MAP[vals]
        if len(vals) == 1 and 32 <= vals[0] <= 126:
            return chr(vals[0])
        return None