class Portafolio:
    def __init__(self):
        self.posiciones = []

    def agregar_posicion(self, posicion):
        """Recibe un objeto Posicion y lo guarda en la lista."""
        self.posiciones.append(posicion)