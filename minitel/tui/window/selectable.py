from minitel.tui.core.color import Color
from minitel.tui.core.effect import Effect
from minitel.tui.core.mixel import Mixel
from minitel.tui.keyboard import Key
from minitel.tui.window.base import Window
from minitel.tui.window.ops import draw_text

PREV_PAGE_LABEL = "(previous page)"
NEXT_PAGE_LABEL = "(next page)"

class WindowSelectable(Window):

    def __init__(self, rect, item_max: int = 21):
        super().__init__(rect)
        self.index: int = 0
        self._last_index: int = -1
        self.item_max: int = item_max   # nombre max de lignes visibles
        self.page = 0                   # page courante

        self.active: bool = True
        self.handlers: dict = {}
        self.items = []
        self._last_rendered: list[Mixel] = []

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
        _, has_prev, _ = self.paged_items
        if has_prev:
            self.page = max(0, self.page - 1)
            self.index = 0  # ou dernière ligne si tu veux
            self._dirty = True
            return True
        return False

    def cursor_right(self):
        """Page suivante si elle existe"""
        _, _, has_next = self.paged_items
        if has_next:
            self.page += 1
            self.index = 0  # ou première ligne si tu veux
            self._dirty = True
            return True
        return False

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
    def draw_item(self, item, row: int = 0) -> list[Mixel]:
        text_color = Color.GRAY_6 if (item == PREV_PAGE_LABEL or item == NEXT_PAGE_LABEL) else Color.WHITE
        draw_text(self.rect.x, 
                self.rect.y + row,
                item,
                color=text_color,
                effect= Effect.INVERT if self.index == row else Effect.NONE)

    def render(self, full: bool = False) -> list[Mixel]:
        mixels = []
        
        if full:
            cleared = [Mixel(m.x, m.y, ' ') for m in self._last_rendered]

        visible, _, _ = self.paged_items

        for row, item in enumerate(visible):
            text_color = Color.GRAY_6 if (item == PREV_PAGE_LABEL or item == NEXT_PAGE_LABEL) else Color.WHITE
            mixels.extend(
                draw_text(self.rect.x, 
                        self.rect.y + row,
                        item,
                        color=text_color,
                        effect= Effect.INVERT if self.index == row else Effect.NONE)
            )
        
        if full:
            self._last_rendered = mixels
            return cleared + mixels
        else:
            return mixels