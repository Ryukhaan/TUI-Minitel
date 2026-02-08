from dataclasses import dataclass, fields
from enum import Enum
from minitel.tui.core.color import Color
from minitel.constantes import *

@dataclass
class GraphicState:
    fg: Color = Color.WHITE
    bg: Color = Color.BLACK
    # size: Size          # normal / double hauteur / double largeur / double
    blink: bool = False
    invert: bool = False
    underline: bool = False
    mask: bool = False
    semigraphic: bool = False

    def __post_init__(self):
       self.fg = self.fg or Color.WHITE
       self.bg = self.bg or Color.BLACK
       self.blink = self.blink or False
       self.invert = self.invert or False
       self.underline = self.underline or False
       self.mask = self.mask or False
       self.semigraphic = self.semigraphic or False

    def __eq__(self, other: 'GraphicState'):
        return all(value == getattr(other, attr) for attr, value in self.__dict__.items())
    
    def __ne__(self, other: 'GraphicState'):
        return any(value != getattr(other, attr) for attr, value in self.__dict__.items())

    # def encode(self, target: 'GraphicState' = None):
    #     sequences = []

    #     # Mapping activation / désactivation
    #     codes = {
    #         'UNDERLINE':   ( [ESC, 0x5a], [ESC, 0x59] ),
    #         'BLINK':       ( [ESC, 0x48], [ESC, 0x49] ),
    #         'INVERT':      ( [ESC, 0x5d], [ESC, 0x5c] ),
    #         'SEMIGRAPHIQUE': ( [SO], [SI] )
    #     }
    #     if self.blink != target.blink:
    #         sequences.extend(codes['BLINK'][int(target.blink)])
    #     if self.invert != target.invert:
    #         sequences.extend()
        
    #     if target != self:
    #         # désactiver l'effet courant s'il existe
    #         if target and target != Effect.NONE:
    #             key = target.name
    #             sequences.extend(codes[key][1])
    #         # activer le nouvel effet
    #         key = self.name
    #         sequences.extend(codes[key][0])
    #     return sequences
    

# class GraphicState(Enum):
#     NONE = -1
#     UNDERLINE = 0
#     BLINK = 1
#     INVERT = 2
#     SEMIGRAPHIQUE = 3

#     def encode(self, current_effect=None):
#         sequences = []

#         # Mapping activation / désactivation
#         codes = {
#             'UNDERLINE':   ( [ESC, 0x5a], [ESC, 0x59] ),
#             'BLINK':       ( [ESC, 0x48], [ESC, 0x49] ),
#             'INVERT':      ( [ESC, 0x5d], [ESC, 0x5c] ),
#             'SEMIGRAPHIQUE': ( [SO], [SI] )
#         }
#         if self == GraphicState.NONE:
#             if current_effect and current_effect != GraphicState.NONE:
#                 # désactiver l'effet courant
#                 key = current_effect.name
#                 sequences.extend(codes[key][1])
#             return sequences
        
#         if current_effect != self:
#             # désactiver l'effet courant s'il existe
#             if current_effect and current_effect != GraphicState.NONE:
#                 key = current_effect.name
#                 sequences.extend(codes[key][1])
#             # activer le nouvel effet
#             key = self.name
#             sequences.extend(codes[key][0])
#         return sequences
    
#         if self.name == 'UNDERLINE':
#             return [ESC, 0x5a]
#         elif self.name == 'BLINK':
#             return [ESC, 0x48]
#         elif self.name == 'INVERT':
#             return [ESC, 0x5d]
#         elif self.name == 'SEMIGRAPHIQUE':
#             return [SO]
#         else:
#             return  [ESC, 0x59, ESC, 0x49, ESC, 0x5c, SI]