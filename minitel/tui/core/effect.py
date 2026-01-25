from enum import Enum
from minitel.constantes import *

class Effect(Enum):
    NONE = -1
    UNDERLINE = 0
    BLINK = 1
    INVERT = 2
    SEMIGRAPHIQUE = 3

    def encode(self):
        if self.name == 'UNDERLINE':
            return [ESC, 0x5a]
        elif self.name == 'BLINK':
            return [ESC, 0x48]
        elif self.name == 'INVERT':
            return [ESC, 0x5d]
        elif self.name == 'SEMIGRAPHIQUE':
            return [SO]
        else:
            return  [ESC, 0x59, ESC, 0x49, ESC, 0x5c, SI]