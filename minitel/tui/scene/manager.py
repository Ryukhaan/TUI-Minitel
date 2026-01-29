import time

from minitel.tui.graphics import Graphics


class SceneManager:
    _scene = None
    _stack = []

    def __init__(self):
        pass
    
    @classmethod
    def run(cls, scene):
        cls._scene = scene
        # Rendu initial
        cls._scene.render()
        while cls._scene:
            changed = cls._scene.update()
            if changed:
                cls._scene.render()
                Graphics.flush()
            time.sleep(0.01)
    
    @classmethod
    def goto(cls, scene_class):
        """Direct transition to a new scene."""
        cls._scene = scene_class()

    @classmethod
    def call(cls, scene_class, *args, **kwargs):
        """Call a new scene and push the current scene onto the stack."""
        if cls._scene:
            cls._stack.append(cls._scene)
        Graphics.flush()
        Graphics.clear()
        Graphics.clear_buffer()
        cls._scene = scene_class(*args, **kwargs)
        cls._scene.on_enter()

    @classmethod
    def return_to_caller(cls):
        """Return to the previous scene by popping the stack."""
        try:
            cls._scene.on_exit()
        except AttributeError as ex:
            raise ex
        
        if cls._stack:
            cls._scene = cls._stack.pop()
            Graphics.flush()
            Graphics.clear()
            Graphics.clear_buffer()
            cls._scene.on_resume()
        else:
            cls._scene = None