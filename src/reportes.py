class ReportadorFinanciero:
    def imprimir_resumen(self, portafolio):
        """Recibe un objeto Portafolio e imprime un resumen en consola."""
        print("=== RESUMEN DEL PORTAFOLIO ===")
        if not hasattr(portafolio, 'posiciones') or not portafolio.posiciones:
            print("El portafolio no contiene posiciones actualmente.")
            return

        for i, posicion in enumerate(portafolio.posiciones, 1):
            print(f"{i}. {posicion}")