class Scene:
    def __init__(self):
        self.windows: dict = {}

    def main(self):
        self.update()

    def render(self):
        for window in self.windows.values():
            window.render()