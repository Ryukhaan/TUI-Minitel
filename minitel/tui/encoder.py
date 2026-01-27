from minitel.tui.core.constants import *
from minitel.tui.core import Effect, Color, Mixel

class MinitelEncoder:
    def __init__(self):
        self.current_effect = Effect.NONE
        self.current_color = Color.WHITE

    def encode(self, mixels):
        if not mixels:
            return []

        # trier par ligne, puis par colonne
        mixels = sorted(mixels, key=lambda m: (m.y, m.x))
        sequences = []
        run = []
        last = None

        for mixel in mixels:
            if last and mixel.y == last.y and mixel.x == last.x + 1:
                # caractère consécutif sur la même ligne -> on continue le run
                run.append(mixel)
            else:
                # nouveau run
                if run:
                    sequences.append(self._encode_run(run))
                run = [mixel]
            last = mixel

        if run:
            sequences.append(self._encode_run(run))

        return sequences

    def _encode_run(self, run):
        bytes_arr = []
        first: Mixel = run[0]

        # position du curseur
        bytes_arr.extend(self._encode_position(first.x, first.y))

        # changement de couleur si nécessaire
        if first.color != self.current_color:
            bytes_arr.extend(first.color.encode())
            self.current_color = first.color

        # changement d'effet si nécessaire
        if first.effect != self.current_effect:
            bytes_arr.extend(first.effect.encode())
            self.current_effect = first.effect

        for mixel in run:
            bytes_arr.extend([ord(mixel.character)])

        # --- Reset effect et couleur à la fin de la run ---
        if self.current_effect != Effect.NONE:
            bytes_arr.extend(Effect.NONE.encode())
            self.current_effect = Effect.NONE

        if self.current_color != Color.WHITE:
            bytes_arr.extend(Color.WHITE.encode())
            self.current_color = Color.WHITE

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
                # Length = 3
                return [HOME]
            else:
                # Length = 6
                seq = [CSI]
                seq += [ord(c) for c in f"{y};{x}H"]
                return seq
        else:
            if x == -1:
                return [BS]
            if y == 1:
                return [LF] 
