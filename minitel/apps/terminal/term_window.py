import subprocess
from pathlib import Path

from minitel.tui.core import GraphicState, Mixel, Rectangle, Color
from minitel.tui.core.config import SCREEN_WIDTH, SCREEN_HEIGHT
from minitel.tui.keyboard import Key
from minitel.tui.window.base import Window
from minitel.tui.window.ops import draw_text, draw_line

OUTPUT_ROWS = SCREEN_HEIGHT - 2  # rows 1-22
SEPARATOR_ROW = SCREEN_HEIGHT - 1  # row 23
INPUT_ROW = SCREEN_HEIGHT          # row 24
MAX_INPUT_DISPLAY = SCREEN_WIDTH - 2  # 38 chars after "$ "


class TerminalWindow(Window):

    def __init__(self, rect: Rectangle, cwd: Path = None):
        super().__init__(rect)
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
                    cmd, shell=True, capture_output=True, text=True, cwd=self.cwd
                )
                for line in result.stdout.splitlines():
                    self.output_lines.extend(self._wrap(line))
                if result.stderr:
                    for line in result.stderr.splitlines():
                        self.output_lines.extend(self._wrap(line))
            except Exception as e:
                self.output_lines.append(f"  {e}")

        self._dirty = True

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

    def _scroll_up(self):
        max_scroll = max(0, len(self.output_lines) - OUTPUT_ROWS)
        if self.scroll < max_scroll:
            self.scroll += 1
            self._dirty = True

    def _scroll_down(self):
        if self.scroll > 0:
            self.scroll -= 1
            self._dirty = True

    def _wrap(self, text: str) -> list[str]:
        if not text:
            return [""]
        lines = []
        while len(text) > SCREEN_WIDTH:
            lines.append(text[:SCREEN_WIDTH])
            text = text[SCREEN_WIDTH:]
        lines.append(text)
        return lines

    def _visible_output(self) -> list[str]:
        total = len(self.output_lines)
        end = total - self.scroll if self.scroll > 0 else total
        start = max(0, end - OUTPUT_ROWS)
        visible = list(self.output_lines[start:end])
        while len(visible) < OUTPUT_ROWS:
            visible.insert(0, "")
        return visible

    def render(self) -> list[Mixel]:
        mixels = []

        # Zone de sortie (lignes 1-22)
        output = self._visible_output()
        for row_idx, line in enumerate(output):
            y = self.rect.y + row_idx
            padded = line[:SCREEN_WIDTH].ljust(SCREEN_WIDTH)
            mixels.extend(draw_text(self.rect.x, y, padded))

        # Séparateur (ligne 23)
        mixels.extend(draw_line(1, SEPARATOR_ROW, SCREEN_WIDTH, type='middle'))

        # Ligne de saisie (ligne 24)
        display_input = self.input_buffer
        if len(display_input) > MAX_INPUT_DISPLAY:
            display_input = display_input[-MAX_INPUT_DISPLAY:]
        prompt = ("$ " + display_input + "_").ljust(SCREEN_WIDTH)
        mixels.extend(draw_text(1, INPUT_ROW, prompt, state=GraphicState(fg=Color.WHITE)))

        return mixels
