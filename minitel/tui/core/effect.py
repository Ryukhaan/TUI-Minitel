from enum import Enum
from minitel.constantes import *

class Effect(Enum):
    NONE = -1
    UNDERLINE = 0
    BLINK = 1
    INVERT = 2
    SEMIGRAPHIQUE = 3

    def encode(self, current_effect=None):
        sequences = []

        # Mapping activation / désactivation
        codes = {
            'UNDERLINE':   ( [ESC, 0x5a], [ESC, 0x59] ),
            'BLINK':       ( [ESC, 0x48], [ESC, 0x49] ),
            'INVERT':      ( [ESC, 0x5d], [ESC, 0x5c] ),
            'SEMIGRAPHIQUE': ( [SO], [SI] )
        }
        if self == Effect.NONE:
            if current_effect and current_effect != Effect.NONE:
                # désactiver l'effet courant
                key = current_effect.name
                sequences.extend(codes[key][1])
            return sequences
        
        if current_effect != self:
            # désactiver l'effet courant s'il existe
            if current_effect and current_effect != Effect.NONE:
                key = current_effect.name
                sequences.extend(codes[key][1])
            # activer le nouvel effet
            key = self.name
            sequences.extend(codes[key][0])
        return sequences
    
        # if self.name == 'UNDERLINE':
        #     return [ESC, 0x5a]
        # elif self.name == 'BLINK':
        #     return [ESC, 0x48]
        # elif self.name == 'INVERT':
        #     return [ESC, 0x5d]
        # elif self.name == 'SEMIGRAPHIQUE':
        #     return [SO]
        # else:
        #     return  [ESC, 0x59, ESC, 0x49, ESC, 0x5c, SI]