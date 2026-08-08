"""
Modelos de dominio para el Core Bancario de SmartPortfolio.
Contiene las estructuras base y las validaciones de negocio estrictas.
"""

from dataclasses import dataclass

@dataclass(frozen=True)
class Instrumento:
    """
    Representa un instrumento financiero inmutable.
    
    Aplica limpieza automática de datos y validación estricta de tipos 
    y sectores permitidos para garantizar la integridad analítica.
    """
    ticker: str
    tipo: str
    sector: str

    def __post_init__(self):
        # 1. Limpieza extrema de TODOS los campos
        ticker_limpio = self.ticker.strip().upper()
        sector_limpio = self.sector.strip().title()
        
        # Limpiamos el tipo (y manejamos el caso especial de ETF que debe ir en mayúsculas)
        tipo_limpio = self.tipo.strip().capitalize()
        if tipo_limpio == "Etf":
            tipo_limpio = "ETF"

        # 2. Bloqueo de strings vacíos
        if not ticker_limpio:
            raise ValueError("Error: El ticker no puede estar vacío.")
        if not sector_limpio:
            raise ValueError("Error: El sector no puede estar vacío.")

        # 3. Validación de Tipo
        tipos_permitidos = ["Acción", "Bono", "ETF", "Fondo"]
        if tipo_limpio not in tipos_permitidos:
            raise ValueError(f"Error de Negocio: '{tipo_limpio}' inválido. Use alguno de los siguientes: {tipos_permitidos}")
        
        # 4. Validación de Sector (¡Ahora con las tildes correctas!)
        sectores_permitidos = [
            "Tecnología", "Finanzas", "Salud", "Energía", 
            "Consumo Discrecional", "Consumo Básico", 
            "Industriales", "Materiales", "Inmobiliario", 
            "Telecomunicaciones", "Servicios Públicos"
        ]
        if sector_limpio not in sectores_permitidos:
            raise ValueError(f"Error de Negocio: Sector '{sector_limpio}' no está en la lista. Use alguno de los siguientes: {sectores_permitidos}")
            
        # 5. Guardamos todos los valores limpios de una sola vez al final
        object.__setattr__(self, 'ticker', ticker_limpio)
        object.__setattr__(self, 'tipo', tipo_limpio)
        object.__setattr__(self, 'sector', sector_limpio)


class Posicion:
    """
    Representa una inversión activa en un instrumento financiero.
    
    Maneja la lógica de negocio, validando que las cantidades y precios 
    sean numéricos y estrictamente mayores a cero para evitar pérdidas.
    """
    def __init__(self, instrumento: Instrumento, cantidad: float, precio_entrada: float):
        if not isinstance(instrumento, Instrumento):
            raise TypeError("Arquitectura: 'instrumento' debe ser un objeto de la clase Instrumento.")
        
        self.instrumento = instrumento
        self.cantidad = cantidad 
        self.precio_entrada = precio_entrada

    @property
    def cantidad(self) -> float:
        return self._cantidad

    @cantidad.setter
    def cantidad(self, valor: float):
        if not isinstance(valor, (int, float)):
            raise TypeError("Error de tipo de dato: La cantidad debe ser un valor numérico.")
        if valor <= 0:
            raise ValueError("Error de Negocio: La cantidad para abrir una posición debe ser mayor a cero.")
        self._cantidad = valor

    @property
    def precio_entrada(self) -> float:
        return self._precio_entrada

    @precio_entrada.setter
    def precio_entrada(self, valor: float):
        if not isinstance(valor, (int, float)):
            raise TypeError("Error de tipo de dato: El precio debe ser un valor numérico.")
        if valor <= 0:
            raise ValueError("Error: El precio de entrada debe ser mayor a cero.")
        self._precio_entrada = valor

    def calcular_valor_actual(self, precio_mercado: float) -> float:
        """
        Calcula el valor actual de la posición según el precio del mercado.
        
        Args:
            precio_mercado (float): El precio actual del instrumento en el mercado.
            
        Returns:
            float: El valor total (cantidad * precio_mercado).
            
        Raises:
            TypeError: Si el precio no es un valor numérico.
            ValueError: Si el precio de mercado es negativo.
        """
        if not isinstance(precio_mercado, (int, float)):
            raise TypeError("Error de tipo de dato: El precio de mercado debe ser un valor numérico.")
        if precio_mercado < 0:
            raise ValueError("Error: El precio de mercado no puede ser negativo.")
        return self.cantidad * precio_mercado


