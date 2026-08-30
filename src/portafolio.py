from typing import List
from src.modelos import Posicion


class PosicionNoExisteError(Exception):
    """Excepción lanzada cuando se intenta remover una posición que no existe."""

    pass


class Portafolio:

    def __init__(self):
        self.posiciones: List[Posicion] = []

    def agregar_posicion(self, posicion: Posicion):
        """Recibe un objeto Posicion y lo guarda en la lista."""
        self.posiciones.append(posicion)

    def remover_posicion(self, ticker: str):
        """Busca una posición por su ticker y la elimina o lanza un error si no la encuentra."""
        for pos in self.posiciones:
            pos_ticker = None
            if hasattr(pos, "instrumento") and hasattr(pos.instrumento, "ticker"):
                pos_ticker = pos.instrumento.ticker
            elif hasattr(pos, "ticker"):
                pos_ticker = pos.ticker

            if pos_ticker == ticker:
                self.posiciones.remove(pos)
                return

        raise PosicionNoExisteError(
            f"La posición con el ticker '{ticker}' no existe en el portafolio."
        )