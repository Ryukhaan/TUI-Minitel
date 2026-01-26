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

KEY_MAP = {
    (27, 79, 77): Key.ENTER,
    (13,): Key.ENTER,
    (27,): Key.CANCEL,
    (27, 91, 65): Key.UP,
    (27, 91, 66): Key.DOWN,
    (10,): Key.DOWN,
    (27, 91, 67): Key.RIGHT,
    (27, 91, 68): Key.LEFT,
    (8,): Key.LEFT,
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
        for listener in cls._instance.listeners:
            if listener.handle_key(key):
                changed = True
        return changed, key

    def _register(self, listener):
        self.listeners.append(listener)

    def _interpet(self, seq: Sequence):
        # Séquences spéciales
        if not seq:
            return None
        print("Keyboard Sequence", seq.valeurs)
        vals = tuple(seq.valeurs)
        key = KEY_MAP[vals]
        if key:
            return key
        return chr(seq.valeurs[-1])