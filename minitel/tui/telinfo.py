"""TeleinformatiqueRenderer — rendu bas niveau pour le mode TELEINFORMATIQUE.

Utilisable par toute app nécessitant 80 colonnes et le charset ASCII standard
(terminal, éditeur de texte, etc.). Ne dépend pas du pipeline VIDEOTEX
(Mixels / Buffer / Encoder).

Positionnement curseur : VT52  →  ESC Y (row-1+0x20) (col-1+0x20)
Coordonnées 1-indexées : col 1..COLS, row 1..ROWS.
"""

import re

from minitel.constantes import ESC, FF, CAN, SI

COLS = 80
ROWS = 24   # la ligne 25 est la ligne de statut, non utilisée

_ANSI_ESCAPE = re.compile(
    r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])'
)


class TeleinformatiqueRenderer:

    COLS = COLS
    ROWS = ROWS

    def __init__(self, minitel):
        self._minitel = minitel

    # ------------------------------------------------------------------
    # Cycle de vie
    # ------------------------------------------------------------------

    def enter(self):
        """Bascule en mode TELEINFORMATIQUE et efface l'écran."""
        ok = self._minitel.definir_mode('TELEINFORMATIQUE')
        if not ok:
            print("[TeleinformatiqueRenderer] échec du changement de mode")
        self._minitel.curseur(False)
        self.clear()

    def exit(self):
        """Retourne en mode VIDEOTEX."""
        self._minitel.send([SI])   # reset shift-in (précaution)
        self._minitel.definir_mode('VIDEOTEX')

    # ------------------------------------------------------------------
    # Primitives d'écran
    # ------------------------------------------------------------------

    def clear(self):
        """Efface tout l'écran."""
        self._minitel.send([FF])

    def move_cursor(self, col: int, row: int):
        """Positionne le curseur (VT52 : ESC Y row+0x1F col+0x1F)."""
        r = max(1, min(row, ROWS))
        c = max(1, min(col, COLS))
        self._minitel.send([ESC, 0x59, (r - 1) + 0x20, (c - 1) + 0x20])

    def clear_to_eol(self):
        """Efface du curseur jusqu'à la fin de la ligne."""
        self._minitel.send([CAN])

    def write(self, text: str):
        """Écrit du texte ASCII à la position courante.

        Les séquences ANSI et les caractères non-ASCII sont filtrés.
        """
        clean = _ANSI_ESCAPE.sub('', text)
        payload = [
            b for b in clean.encode('ascii', errors='replace')
            if 32 <= b <= 126
        ]
        if payload:
            self._minitel.send(payload)

    def write_at(self, col: int, row: int, text: str):
        """Positionne puis écrit."""
        self.move_cursor(col, row)
        self.write(text)

    def separator(self, row: int):
        """Affiche une ligne de séparation horizontale."""
        self.write_at(1, row, '-' * COLS)

    # ------------------------------------------------------------------
    # Rendu de blocs (utilisé par les apps)
    # ------------------------------------------------------------------

    def render_lines(self, lines: list[str], start_row: int = 1):
        """Affiche une liste de lignes depuis start_row.

        Chaque ligne est tronquée à COLS et complétée par des espaces
        pour effacer tout résidu sur l'écran.
        """
        for idx, line in enumerate(lines):
            padded = line[:COLS].ljust(COLS)
            self.write_at(1, start_row + idx, padded)

    def render_input(self, row: int, prompt: str, text: str):
        """Affiche la ligne de saisie avec un curseur '_'."""
        max_text = COLS - len(prompt) - 1   # -1 pour le curseur
        display = text[-max_text:] if len(text) > max_text else text
        line = (prompt + display + '_').ljust(COLS)
        self.write_at(1, row, line)

    # ------------------------------------------------------------------
    # Flush
    # ------------------------------------------------------------------

    def flush(self):
        self._minitel.flush()
