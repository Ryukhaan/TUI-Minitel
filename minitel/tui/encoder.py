from minitel.tui.core.constants import *
from minitel.tui.core import Effect, Color, Mixel

import numpy as np
from PIL import Image

def compute_cost(mixels: list[Mixel]):
    cost = np.ones((len(mixels), len(mixels)))
    for i in range(cost.shape[0]):
        m_i = mixels[i]
        for j in range(cost.shape[1]):
            m_j = mixels[j]
            if i == j:
                cost[i, j] = float('inf')
            else:
                cost[i,j] = cost_move(m_i, m_j) + cost_color(m_i, m_j) + cost_effect(m_i, m_j)
    cost_norm = (cost - cost.min()) / (cost.max() - cost.min())
    im = Image.fromarray(np.uint8(cost_norm*255))
    im.save("./cost.png")
    return cost

def cost_move(a: Mixel, b: Mixel):
    if a.x == b.x+1 and a.y == b.y:
        return 1
    return 3

def cost_color(a: Mixel, b: Mixel):
    cost = 0.
    if a.bg_color != b.bg_color:
        cost += 2
    if a.fg_color != b.fg_color:
        cost += 2
    return cost

def cost_effect(a: Mixel, b: Mixel):
    cost = 0.
    if a.effect != b.effect:
        cost += len(a.effect.encode(current_effect=b.effect))
    return cost

def nearest_neighbor_tsp(cost_matrix, start: int = 0):
    """
    Algorithme du voisin le plus proche pour TSP.

    :param cost_matrix: matrice carrée n x n des coûts entre chaque mixel
    :param start: index du mixel de départ
    :return: sequence des indices des mixels dans l'ordre du parcours
    """
    n = len(cost_matrix)
    visited = set()
    sequence = []

    current = start
    visited.add(current)
    sequence.append(current)

    while len(visited) < n:
        # trouver le mixel non visité le plus proche
        next_mixel = None
        min_cost = float('inf')
        for j in range(n):
            if j not in visited and cost_matrix[current][j] < min_cost:
                min_cost = cost_matrix[current][j]
                next_mixel = j

        if next_mixel is None:
            break  # sécurité, ne devrait pas arriver

        visited.add(next_mixel)
        sequence.append(next_mixel)
        current = next_mixel

    return sequence

class MinitelEncoder:
    def __init__(self):
        self.current_effect = Effect.NONE
        self.current_fg = Color.WHITE
        self.current_bg = Color.BLACK
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

        # changement de couleurs si nécessaire
        if first.bg_color != self.current_bg:  # arp
            bytes_arr.extend(first.bg_color.encode(background=True))
            self.current_bg = first.bg_color

        if first.fg_color != self.current_fg:  # avp
            bytes_arr.extend(first.fg_color.encode())
            self.current_fg = first.fg_color

        # changement d'effet si nécessaire
        if first.effect != self.current_effect:
            bytes_arr.extend(first.effect.encode(self.current_effect))
            self.current_effect = first.effect

        for mixel in run:
            # reset de l’effet si nécessaire avant d’écrire
            if mixel.effect != self.current_effect:
                bytes_arr.extend(mixel.effect.encode(self.current_effect))
                self.current_effect = mixel.effect
            bytes_arr.extend([ord(mixel.character)])

        # --- Reset effect et couleur à la fin de la run ---
        if self.current_effect != Effect.NONE:
            bytes_arr.extend(Effect.NONE.encode(self.current_effect))
            self.current_effect = Effect.NONE

        if self.current_fg != Color.WHITE:
            bytes_arr.extend(Color.WHITE.encode())
            self.current_color = Color.WHITE
        if self.current_bg != Color.BLACK:
            bytes_arr.extend(Color.BLACK.encode(background=True))
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
