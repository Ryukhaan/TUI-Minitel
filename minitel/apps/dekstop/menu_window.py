from pathlib import Path
from minitel.constantes import CAN, US
from minitel.tui.core.config import SCREEN_HEIGHT, SCREEN_WIDTH
from minitel.tui.core import Effect, Mixel, Rectangle, Color
from minitel.tui.graphics import Graphics
from minitel.tui.keyboard import Key
from minitel.tui.window.base import Window
from minitel.tui.window.line import HorizontalLine
from minitel.tui.window.ops import draw_text

PREV_PAGE_LABEL = "(previous page)"
NEXT_PAGE_LABEL = "(next page)"

class MenuDesktopWindow(Window):

    def __init__(self, rect):
        super().__init__(rect)
        self.index: int = 0
        self._last_index: int = -1
        self.handlers: dict = {}
        self.items = []
        self.active: bool = True
        self._last_rendered: list[Mixel] = []
        self.item_max = 18         # nombre max de lignes visibles
        self.page = 0              # page courante

        # Eviter de calculer la page à chaque mouvement de curseur
        self._cached_visible = []
        self._cached_has_prev = False
        self._cached_has_next = False
        self._dirty = True

    @property
    def key_map(self):
        return {
            Key.UP: self.cursor_up,
            Key.DOWN: self.cursor_down,
            Key.LEFT: self.cursor_left,
            Key.RIGHT: self.cursor_right,
            Key.ENTER: self.handle_ok,
            Key.CANCEL: self.handle_cancel,
        }

    @property
    def current_item(self):
        return self.items[self.index]
    
    # ------------------------
    # Handlers
    # ------------------------
    def set_handler(self, key_name: str, callback: callable):
        """Associe une touche/événement à une méthode"""
        self.handlers[key_name] = callback

    def handle_key(self, key: str) -> bool:
        """
        Renvoi True si la key est handle par la window.
        Sinon False.
        
        :param self: Description
        :param key: Description
        :return: Description
        :rtype: bool
        """
        if not self.active:
            return False

        try:
            action = self.key_map[key]
            return action() or True
        except KeyError:
            return False

    def handle_ok(self):
        visible, has_prev, has_next = self.paged_items

        # Previous page
        if has_prev and self.index == 0:
            self.page = max(0, self.page - 1)
            self._dirty = True
            self.select(0)
            return

        # Next Page
        if has_next and self.index == len(visible) - 1:
            self.page += 1
            self._dirty = True
            self.select(0)
            return

        # vrai item
        real_index = self.index
        if has_prev:
            real_index -= 1

        global_index = self.page * self.item_max + real_index
        item = self.items[global_index]
        
        try:
            self.handlers["ok"](item)
            return True
        except KeyError:
            print("No handler for ok")
            return False

    def handle_cancel(self):
        try:
            self.handlers["cancel"]()
            return True
        except:
            print(f"No key 'cancel' found in handlers ({self.handlers.keys()})")
            return False
    # ------------------------
    # Cursor / Index management
    # ------------------------
    def select(self, index: int) -> None:
        """
        Fixe l'index à la valeur définie (équivalent à window.index = index)
        
        :param self: Description
        :param index: Description
        """
        self.index = index
    
    def unselect(self) -> None:
        """
        Déselection la fenêtre (index=-1)
        
        :param self: Description
        """
        self.index = -1

    def _update_by(self, value: int) -> bool:
        visible, _, _ = self.paged_items
        size = len(visible)
        if size > 0:
            self.index = (self.index + value) % size
            return True
        return False
    
    def cursor_up(self):
        return self._update_by(-1)
    
    def cursor_down(self):
        return self._update_by(1)

    def cursor_left(self):
        """Page précédente si elle existe"""
        self.handlers["prev_page"]()
        _, has_prev, _ = self.paged_items
        if has_prev:
            self.page = max(0, self.page - 1)
            self.index = 0  # ou dernière ligne si tu veux
            self._dirty = True
            return True
        return False

    def cursor_right(self):
        """Page suivante si elle existe"""
        self.handlers["next_page"]()
        _, _, has_next = self.paged_items
        if has_next:
            self.page += 1
            self.index = 0  # ou première ligne si tu veux
            self._dirty = True
            return True
        return False

    def __setitem__(self, key, value):
        self.handlers[key] = value
    
    def __getitem__(self, key):
        return self.handlers[key]

    # ------------------------
    # Pagination
    # ------------------------
    def _rebuild_page(self):
        total = len(self.items)
        start = self.page * self.item_max
        end = start + self.item_max

        visible = self.items[start:end]

        has_prev = start > 0
        has_next = end < total

        final = []
        if has_prev:
            final.append(PREV_PAGE_LABEL)
        final.extend(visible)
        if has_next:
            final.append(NEXT_PAGE_LABEL)

        self._cached_visible = final
        self._cached_has_prev = has_prev
        self._cached_has_next = has_next
        self._dirty = False

    @property
    def paged_items(self):
        if self._dirty:
            self._rebuild_page()
        return self._cached_visible, self._cached_has_prev, self._cached_has_next
    
    # ------------------------
    # Rendering
    # ------------------------
    def draw_type_item(self, item, row: int = 0):
        if item == PREV_PAGE_LABEL:
            type_mixels = draw_text(self.rect.x, self.rect.y + row, "<")
        elif item == NEXT_PAGE_LABEL:
            type_mixels = draw_text(self.rect.x, self.rect.y + row, ">")
        elif item.is_file():
            type_mixels = draw_text(self.rect.x, self.rect.y + row, "F")
        else:
            type_mixels = draw_text(self.rect.x, self.rect.y + row, "D", effect=Effect.INVERT)
        type_mixels += draw_text(self.rect.x + 1, self.rect.y + row, "|", effect=Effect.NONE)
        return type_mixels

    def draw_ext_item(self, item, row: int = 0):
        ext_mixels = draw_text(SCREEN_WIDTH-4, self.rect.y + row, "|")
        if item == PREV_PAGE_LABEL or item == NEXT_PAGE_LABEL:
            return ext_mixels
        extension = str(item.suffix)[1:]
        if extension:
            ext_mixels += draw_text(SCREEN_WIDTH-len(extension)+1, self.rect.y + row, extension)
        else:
            ext_mixels += draw_text(SCREEN_WIDTH-3, self.rect.y + row, " "*4)
        return ext_mixels

    def draw_item(self, item: Path, row: int = 0) -> list[Mixel]:
        type_m = self.draw_type_item(item, row)

        text_color = Color.GRAY_6 if (item == PREV_PAGE_LABEL or item == NEXT_PAGE_LABEL) else Color.WHITE
        if item == PREV_PAGE_LABEL:
            text = PREV_PAGE_LABEL
        elif item == NEXT_PAGE_LABEL:
            text = NEXT_PAGE_LABEL
        else:
            text = item.stem
            if len(text) > 20:
                text = text[:20]
        file_mixels = draw_text(self.rect.x + len(type_m), 
                self.rect.y + row,
                text,
                color=text_color,
                effect= Effect.INVERT if self.index == row else Effect.NONE)
        
        ext_m = self.draw_ext_item(item, row)
        return type_m + file_mixels + ext_m

    def render(self, full: bool = False) -> list[Mixel]:
        mixels = []
        visible, _, _ = self.paged_items

        for row, item in enumerate(visible):
            mixels.extend(self.draw_item(item, row))
        return mixels