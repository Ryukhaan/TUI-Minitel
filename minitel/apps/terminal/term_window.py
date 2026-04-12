import subprocess
from pathlib import Path

from minitel.tui.core import Rectangle
from minitel.tui.keyboard import Key
from minitel.tui.window.base import Window
from minitel.tui.telinfo import TeleinformatiqueRenderer


class TerminalWindow(Window):
    """État et gestion des touches du terminal.

    Le rendu est délégué à TeleinformatiqueRenderer via TerminalScene.
    Cette classe ne produit plus de Mixels.
    """

    def __init__(self, rect: Rectangle, cwd: Path = None,
                 renderer: TeleinformatiqueRenderer = None):
        super().__init__(rect)
        self._renderer = renderer
        self._cols = renderer.COLS if renderer else 40
        self._output_rows = renderer.ROWS - 2 if renderer else 22

        self.cwd = cwd or Path.home()
        self.output_lines: list[str] = []
        self.input_buffer: str = ""
        self.history: list[str] = []
        self.history_idx: int = -1
        self.scroll: int = 0
        self.active: bool = True
        self.handlers: dict = {}
        self._dirty: bool = True

    def set_handler(self, name: str, callback):
        self.handlers[name] = callback

    def update(self) -> bool:
        return False

    def handle_key(self, key) -> bool:
        if not self.active or key is None:
            return False
        if isinstance(key, str):
            self.input_buffer += key
            self.scroll = 0
            self._dirty = True
            return True
        if key == Key.BACKSPACE:
            if self.input_buffer:
                self.input_buffer = self.input_buffer[:-1]
                self._dirty = True
            return True
        if key == Key.ENTER:
            self._execute()
            return True
        if key == Key.UP:
            self._history_prev()
            return True
        if key == Key.DOWN:
            self._history_next()
            return True
        if key == Key.LEFT:
            self._scroll_up()
            return True
        if key == Key.RIGHT:
            self._scroll_down()
            return True
        if key == Key.CANCEL:
            if 'cancel' in self.handlers:
                self.handlers['cancel']()
            return True
        return False

    # ------------------------------------------------------------------
    # Exécution de commandes
    # ------------------------------------------------------------------

    def _execute(self):
        cmd = self.input_buffer.strip()
        self.input_buffer = ""
        self.history_idx = -1
        self.scroll = 0

        if not cmd:
            self._dirty = True
            return

        self.history.append(cmd)
        self.output_lines.extend(self._wrap(f"$ {cmd}"))

        if cmd.startswith("cd"):
            parts = cmd.split(None, 1)
            target = parts[1] if len(parts) > 1 else str(Path.home())
            try:
                new_cwd = (self.cwd / target).resolve()
                if new_cwd.is_dir():
                    self.cwd = new_cwd
                else:
                    self.output_lines.append(f"  no such directory: {target}")
            except Exception as e:
                self.output_lines.append(f"  {e}")
        else:
            try:
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True,
                    cwd=self.cwd
                )
                for line in result.stdout.splitlines():
                    self.output_lines.extend(self._wrap(line))
                if result.stderr:
                    for line in result.stderr.splitlines():
                        self.output_lines.extend(self._wrap(line))
            except Exception as e:
                self.output_lines.append(f"  {e}")

        self._dirty = True

    # ------------------------------------------------------------------
    # Historique
    # ------------------------------------------------------------------

    def _history_prev(self):
        if not self.history:
            return
        if self.history_idx == -1:
            self.history_idx = len(self.history) - 1
        elif self.history_idx > 0:
            self.history_idx -= 1
        self.input_buffer = self.history[self.history_idx]
        self._dirty = True

    def _history_next(self):
        if self.history_idx == -1:
            return
        if self.history_idx < len(self.history) - 1:
            self.history_idx += 1
            self.input_buffer = self.history[self.history_idx]
        else:
            self.history_idx = -1
            self.input_buffer = ""
        self._dirty = True

    # ------------------------------------------------------------------
    # Scroll
    # ------------------------------------------------------------------

    def _scroll_up(self):
        max_scroll = max(0, len(self.output_lines) - self._output_rows)
        if self.scroll < max_scroll:
            self.scroll += 1
            self._dirty = True

    def _scroll_down(self):
        if self.scroll > 0:
            self.scroll -= 1
            self._dirty = True

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _wrap(self, text: str) -> list[str]:
        if not text:
            return [""]
        lines = []
        while len(text) > self._cols:
            lines.append(text[:self._cols])
            text = text[self._cols:]
        lines.append(text)
        return lines

    def visible_output(self) -> list[str]:
        """Retourne les lignes visibles (utilisé par la scène pour le rendu)."""
        total = len(self.output_lines)
        end = total - self.scroll if self.scroll > 0 else total
        start = max(0, end - self._output_rows)
        visible = list(self.output_lines[start:end])
        while len(visible) < self._output_rows:
            visible.insert(0, "")
        return visible

    def render(self):
        """Non utilisé : le rendu est géré par TerminalScene via le renderer."""
        return []
