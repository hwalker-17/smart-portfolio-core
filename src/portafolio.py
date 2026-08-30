from typing import List
from src.modelos import Posicion


class Portafolio:
    def __init__(self):
        self.posiciones: List[Posicion] = []

    def agregar_posicion(self, posicion: Posicion):
        """Recibe un objeto Posicion y lo guarda en la lista."""
        self.posiciones.append(posicion)