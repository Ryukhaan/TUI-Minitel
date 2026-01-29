from minitel.tui.graphics import Graphics
from minitel.tui.scene.manager import SceneManager

class SceneBase:
    def __init__(self):
        self.windows: dict = {}

    def __setitem__(self, key, window):
        if 1 <= window.x <= self.width  and 1 <= window.y <= self.height:
            self.widgets[key] = window
            if self.active_key is None:
                self.active_key = key
        else:
            raise ValueError(f"Out of Bound widget ({window.x, window.y}) , should be less than (0, {SCREEN_WIDTH}) and (0, {SCREEN_HEIGHT})")

    def __getitem__(self, key):
        return self.windows[key]
    
    def on_enter(self):
        raise NotImplementedError("on_enter function not implemented")
    
    def on_exit(self):
        raise NotImplementedError("on_exit function not implemented")
    
    def on_resume(self):
        raise NotImplementedError("on_resume function not implemented")

    def handle_key(self, key):
        for widget in self.widgets.values():
            if hasattr(widget, "handle_key"):
                changed = widget.handle_key(key)
                if changed:
                    return True
        return False
    
    def update(self):
        if SceneManager._scene != self:
            return None

    def render(self):
        if SceneManager._scene != self:
            return
        mixels = [window.render() for window in self.windows.values()]
        Graphics.update(mixels)
    
            