from minitel.tui.core import Mixel, Color, Effect

def draw_text(x, y, text, 
              color: Color = Color.WHITE, 
              effect: Effect = Effect.NONE) -> list[Mixel]:
    """Créer l'ensemble des Mixel pour afficher un texte.
    """
    return [Mixel(x+i, y, char, fg_color=color, effect=effect) for i, char in enumerate(text)]
