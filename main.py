from __future__ import annotations

from minitel.Minitel import Minitel
from minitel.tui.keyboard import KeyboardController
from minitel.tui.graphics import Graphics
from minitel.tui.scene.desktop import Desktop as SceneDesktop
from minitel.tui.scene.manager import SceneManager
from minitel.tui.widget.widget import *

if __name__ == "__main__":
    minitel = Minitel('COM6')
    minitel.deviner_vitesse()
    minitel.identifier()

    # Switch to fast mode
    minitel.definir_vitesse(4800)
    minitel.definir_mode('VIDEOTEX')
    minitel.configurer_clavier(etendu = True, curseur = False, minuscule = True)
    minitel.echo(False)
    minitel.curseur(False)
    minitel.efface('tout')

    KeyboardController.init(minitel)
    Graphics.init(minitel)
    SceneManager.run(SceneDesktop())
