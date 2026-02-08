from minitel.tui.core.constants import *
from minitel.tui.core import GraphicState, Mixel

UNDERLINE_ON = [ESC, 0x5a]
UNDERLINE_OFF = [ESC, 0x59]
BLINK_OFF = [ESC, 0x48]
BLINK_ON = [ESC, 0x49]
INVERT_ON = [ESC, 0x5d]
INVERT_OFF = [ESC, 0x5c]
MASK_ON = [ESC, 0x58]
MASK_OFF = [ESC, 0x5f]


class MinitelEncoder:
    def __init__(self):
        self.current_state = GraphicState()
        self.last_x = 1  # Position du curseur actuelle
        self.last_y = 1

    def encode(self, mixels):
        if not mixels:
            return []

        # trier par ligne, puis par colonne
        mixels = sorted(mixels, key=lambda m: (m.y, m.x))
        
        run = []
        last = None

        for mixel in mixels:
            if last and mixel.y == last.y and mixel.x == last.x + 1:
                # caractère consécutif sur la même ligne -> on continue le run
                run.append(mixel)
            else:
                # nouveau run
                if run:
                    yield self._encode_run(run)
                run = [mixel]
            last = mixel

        if run:
            yield self._encode_run(run)


    def _encode_run(self, run):
        bytes_arr = []
        first: Mixel = run[0]

        # position du curseur
        pos = self._encode_position(first.x, first.y)
        bytes_arr.extend(pos)

        # bytes_arr.extend(self._encode_state(current))

        # current = first.state
        for mixel in run:
            # reset de l’effet si nécessaire avant d’écrire
            if mixel.state != self.current_state:
                bytes_arr.extend(self._encode_state_delta(self.current_state, mixel.state))
                self.current_state = mixel.state
            bytes_arr.extend([ord(mixel.character)])

        # --- Reset effect et couleur à la fin de la run ---
        self.current_state = GraphicState()

        return bytes_arr
    
    def _encode_position(self, x, y, relatif = False):
        """Définit la position du curseur du Minitel

        Note:
        Cette méthode optimise le déplacement du curseur, il est donc important
        de se poser la question sur le mode de positionnement (relatif vs
        absolu) car le nombre de caractères générés peut aller de 1 à 5.

        Sur le Minitel, la première colonne a la valeur 1. La première ligne
        a également la valeur 1 bien que la ligne 0 existe. Cette dernière
        correspond à la ligne d’état et possède un fonctionnement différent
        des autres lignes.

        :param colonne:
            colonne à laquelle positionner le curseur
        :type colonne:
            un entier relatif

        :param ligne:
            ligne à laquelle positionner le curseur
        :type ligne:
            un entier relatif

        :param relatif:
            indique si les coordonnées fournies sont relatives
            (True) par rapport à la position actuelle du curseur ou si
            elles sont absolues (False, valeur par défaut)
        :type relatif:
            un booléen
        """
        if not relatif:
            # Déplacement absolu
            if x == 1 and y == 1:
                return [RS]
            else:
                return [US, 0x40 + y, 0x40 + x]
            # # Déplacement absolu
            # if x == 1 and y == 1:
            #     # Length = 3
            #     return [HOME]
            # else:
            #     # Length = 6 too much
            #     seq = [CSI]
            #     seq += [ord(c) for c in f"{y};{x}H"]
            #     return seq
        else:
            if x == -1:
                return [BS]
            if y == 1:
                return [LF]
            
    def _encode_state_delta(self, current, target):
        seq = []

        if current.fg != target.fg:
            seq += target.fg.encode()

        if current.bg != target.bg:
            seq += target.bg.encode(background=True)

        if current.blink != target.blink:
            seq += (BLINK_ON if target.blink else BLINK_OFF)

        if current.invert != target.invert:
            seq += (INVERT_ON if target.invert else INVERT_OFF)

        if current.underline != target.underline:
            seq += (UNDERLINE_ON if target.underline else UNDERLINE_OFF)

        if current.mask != target.mask:
            seq += (MASK_ON if target.mask else MASK_OFF)

        if current.semigraphic != target.semigraphic:
            seq += ([SO] if target.semigraphic else [SI])

        return seq