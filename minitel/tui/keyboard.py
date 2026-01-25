from enum import Enum, auto
from queue import Empty

from minitel.Sequence import Sequence

class Key(Enum):
    UP = auto()
    DOWN = auto()
    RIGHT = auto()
    LEFT = auto()
    ENTER = auto()


class KeyboardController:
    def __init__(self, minitel):
        self.minitel = minitel
        self.listeners = []

    def register(self, listener):
        self.listeners.append(listener)

    def poll(self):
        try:
            seq = self.minitel.recevoir_sequence(bloque=False)
        except Empty:
            return  False # rien à traiter pour le moment

        key = self.interpret(seq)
        changed = False
        for l in self.listeners:
            if l.handle_key(key):
                changed = True
        return changed

    def interpret(self, seq: Sequence):
        # Séquences spéciales
        # if seq:
            # print("Keyboard Sequence", seq.valeurs)
        if seq.valeurs == [27, 79, 77]:
            return Key.ENTER
        elif seq.valeurs == [27, 91, 65]:
            return Key.UP
        elif seq.valeurs == [27, 91, 66] or seq.valeurs == [10]:
            return Key.DOWN
        elif seq.valeurs == [27, 91, 67]:
            return Key.RIGHT
        elif seq.valeurs == [27, 91, 68] or seq.valeurs == [8]:
            return Key.LEFT
        # caractère normal
        else:
            return chr(seq.valeurs[-1])