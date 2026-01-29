from __future__ import annotations
from pathlib import Path
import time

from minitel.Minitel import Minitel
from minitel.tui.keyboard import KeyboardController
from minitel.tui.graphics import Graphics
from minitel.tui.scene.manager import SceneManager
from minitel.tui.widget.widget import *

from minitel.apps.dekstop.desktop import Desktop as SceneDesktop

if __name__ == "__main__":
    minitel = Minitel('COM6')
    minitel.deviner_vitesse()
    minitel.identifier()

    # Switch to fast mode
    minitel.definir_vitesse(4800)
    minitel.send([0x13, 0x5e])
    minitel.definir_mode('VIDEOTEX')
    minitel.flush()
    minitel.configurer_clavier(etendu = True, curseur = False, minuscule = True)
    minitel.echo(False)
    minitel.curseur(False)
    minitel.efface('tout')

    # minitel.send([0x40, 0x41, 0x42])
    KeyboardController.init(minitel)
    Graphics.init(minitel)
    Graphics.reset_attributes()
    desktop = SceneDesktop(start_path=Path("assets").resolve())
    SceneManager.run(desktop)
