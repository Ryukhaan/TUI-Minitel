from __future__ import annotations
import os
import time

from minitel.Minitel import Minitel
from minitel.constantes import PRO1, PRO2
from minitel.tui.keyboard import KeyboardController
from minitel.tui.screen import MinitelScreen
from minitel.tui.widget.widget import *
from minitel.tui.core import Color, Effect
from minitel.tui.window.footer import Footer
from minitel.tui.window.menu import Menu

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
    minitel.curseur(True)
    # minitel.definir_mode("TELEINFORMATIQUE")
    # Clean Screen
    minitel.efface('tout')

    keyboard = KeyboardController(minitel)
    screen = MinitelScreen(minitel)

    # user_input = TextInput(1, 4, 40, height=10)
    screen["header_label"] = Label(1, 1, text=" Minitel Text UI - Version: Alpha")
    screen["header_2"] = Label(1, 2, text="-"*80)
    screen["footer"] = Footer()
    menu = Menu(1, 3, 1, 1)
    for file in os.listdir():
        menu.add_command(file, None, True)
    menu.select(1)
    screen["menu"] = menu
    keyboard.register(menu)
    screen.set_active("menu")
    screen.render()
    time.sleep(0.02)
    while True:
        changed = keyboard.poll()
        if changed:
            screen.render()
        time.sleep(0.01)
    # Fin du programme retour en mode "default"

    time.sleep(2.)
    minitel.close()
