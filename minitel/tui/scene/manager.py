class SceneManager:
    _scene = None
    _stack = []

    def __init__(self):
        pass
    
    @classmethod
    def run(cls, scene):
        cls._scene = scene
        while cls._scene is not None:
            cls._scene.main()
    
    @classmethod
    def goto(cls, scene_class):
        """Direct transition to a new scene."""
        cls._scene = scene_class()

    @classmethod
    def call(cls, scene_class):
        """Call a new scene and push the current scene onto the stack."""
        cls._stack.append(cls._scene)
        cls._scene = scene_class()

    @classmethod
    def return_to_caller(cls):
        """Return to the previous scene by popping the stack."""
        cls._scene = cls._stack.pop()