from minitel.tui.core import Mixel, Color, GraphicState

def draw_text(x: int, y:int, text: str, state: GraphicState = None) -> list[Mixel]:
    """Créer l'ensemble des Mixel pour afficher un texte.
    """
    return [Mixel(x+i, y, char, state=state) for i, char in enumerate(text)]

def draw_line(x:int, y:int , length: int , type: str = 'top', state: GraphicState = None):
    if type == 'top':
        text = "#" * length
    elif type == 'middle':
        text = "," * length
    elif type == 'bottom':
        text = "p" * length
    else:
        text = f"{type}" * length
    if state:
        state.semigraphic = True
    else:
        state = GraphicState(semigraphic=True)
    return draw_text(x, y, text, state)