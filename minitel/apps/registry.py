"""Registre central des applications disponibles dans le launcher."""
from pathlib import Path


def get_apps() -> list[tuple[str, callable]]:
    """Retourne la liste des apps sous forme (label, factory)."""
    from minitel.apps.terminal.terminal import TerminalScene
    from minitel.apps.dekstop.desktop import Desktop as SceneDesktop

    return [
        ("Terminal", lambda: TerminalScene(Path.home())),
        ("Desktop", lambda: SceneDesktop(start_path=Path("assets").resolve())),
    ]
