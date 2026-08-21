from typing import List
from src.modelos import Posicion


class Portafolio:
    def __init__(self):
        self.posiciones: List[Posicion] = []

    def agregar_posicion(self, posicion: Posicion):
        """Guarda un objeto Posicion en la lista de posiciones."""
        self.posiciones.append(posicion)