from __future__ import annotations

from minitel.Minitel import Minitel
from minitel.tui.keyboard import KeyboardController
from minitel.tui.graphics import Graphics
from minitel.tui.scene.desktop import Desktop as SceneDesktop
from minitel.tui.scene.manager import SceneManager
from minitel.tui.widget.widget import *

class MinitelRedirector:
    def __init__(self, minitel):
        self.minitel = minitel
        self.buffer = ""

    def write(self, data):
        self.buffer += data
        if '\n' in self.buffer:
            lines = self.buffer.split('\n')
            for line in lines[:-1]:
                self.minitel.send(line + '\r\n')
            self.buffer = lines[-1]

    def flush(self):
        if self.buffer:
            self.minitel.send(self.buffer + '\r\n')
            self.buffer = ""

if __name__ == "__main__":
    minitel = Minitel('COM6')
    minitel.deviner_vitesse()
    minitel.identifier()

    # Switch to fast mode
    minitel.definir_vitesse(4800)
    minitel.configurer_clavier(etendu = True, curseur = False, minuscule = True)
    minitel.echo(False)
    minitel.curseur(False)
    # minitel.definir_mode("TELEINFORMATIQUE")
    # Clean Screen
    minitel.efface('tout')

    KeyboardController.init(minitel)
    Graphics.init(minitel)
    SceneManager.run(SceneDesktop())

    # user_input = TextInput(1, 4, 40, height=10)
    # screen["header_label"] = Label(1, 1, text=" Minitel Text UI - Version: Alpha")
    # screen["header_2"] = Label(1, 2, text="-"*80)
    # screen["footer"] = Footer()
    # menu = Menu(1, 3, 1, 1)
    # for file in os.listdir():
    #     menu.add_command(file, None, True)
    # menu.select(1)
    # screen["menu"] = menu
    # keyboard.register(menu)
    # screen.set_active("menu")
    # screen.update()
    # time.sleep(0.02)
    # while True:
    #     changed = keyboard.poll()
    #     if changed:
    #         screen.update()
    #     time.sleep(0.01)
    # # Fin du programme retour en mode "default"

    # time.sleep(2.)
    # minitel.close()
