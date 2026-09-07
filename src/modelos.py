"""
Modelos de dominio para el Core Bancario de SmartPortfolio.
Contiene las estructuras base, validaciones y capacidades predictivas.
"""

from dataclasses import dataclass, field
from typing import Protocol, Optional, List

class MarketDataProvider(Protocol):
    """
    Protocolo (Interfaz) para inyectar proveedores de datos de mercado.
    Cualquier clase que implemente 'obtener_datos' funcionará aquí (ej. Yahoo Finance).
    """
    def obtener_datos(self, ticker: str) -> List[float]:
        ...

@dataclass(frozen=True)
class Instrumento:
    """
    Representa un instrumento financiero inmutable y con capacidades predictivas.
    """
    ticker: str
    tipo: str
    sector: str
    data_provider: Optional[MarketDataProvider] = field(default=None, compare=False, repr=False)

    def __post_init__(self):
        # 1. Limpieza extrema
        ticker_limpio = self.ticker.strip().upper()
        sector_limpio = self.sector.strip().title()
        
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
            raise ValueError(f"Error de Negocio: '{tipo_limpio}' inválido. Use: {tipos_permitidos}")
        
        # 4. Validación de Sector
        sectores_permitidos = [
            "Tecnología", "Finanzas", "Salud", "Energía", 
            "Consumo Discrecional", "Consumo Básico", 
            "Industriales", "Materiales", "Inmobiliario", 
            "Telecomunicaciones", "Servicios Públicos", "Gobierno"
        ]
        if sector_limpio not in sectores_permitidos:
            raise ValueError(f"Error de Negocio: Sector '{sector_limpio}' inválido. Use: {sectores_permitidos}")
            
        # Asignación inmutable de datos básicos
        object.__setattr__(self, 'ticker', ticker_limpio)
        object.__setattr__(self, 'tipo', tipo_limpio)
        object.__setattr__(self, 'sector', sector_limpio)

        # Variables internas de estado para el modelo de Machine Learning
        object.__setattr__(self, '_modelo_entrenado', False)
        object.__setattr__(self, '_intercepto', 0.0)
        object.__setattr__(self, '_pendiente', 0.0)
        object.__setattr__(self, '_ultimo_precio', 0.0)

    def entrenar_modelo(self):
        """
        Entrena un modelo predictivo (Regresión Lineal Simple) de la acción.
        Usa el precio del día anterior para predecir el día actual, simulando OLS.
        """
        if not self.data_provider:
            raise ValueError("Error: No se ha inyectado un MarketDataProvider.")
        
        datos = self.data_provider.obtener_datos(self.ticker)
        if not datos or len(datos) < 2:
            raise ValueError("Error: Datos insuficientes para entrenar el modelo (mínimo 2).")

        if not all(isinstance(precio, (int, float)) for precio in datos):
            raise TypeError("Error: El oráculo entregó datos corruptos o no numéricos.")
        
        # X: Close_Anterior, Y: Close actual 
        x = datos[:-1]
        y = datos[1:]
        n = len(x)
        
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_xx = sum(xi ** 2 for xi in x)
        
        denominador = (n * sum_xx - sum_x ** 2)
        if denominador == 0:
            raise ValueError("Error Matemático: Varianza cero en los datos históricos.")
        
        # Cálculo manual de OLS (Ordinary Least Squares) para no depender de statsmodels en el core
        pendiente = (n * sum_xy - sum_x * sum_y) / denominador
        intercepto = (sum_y - pendiente * sum_x) / n
        
        object.__setattr__(self, '_pendiente', pendiente)
        object.__setattr__(self, '_intercepto', intercepto)
        object.__setattr__(self, '_ultimo_precio', datos[-1])
        object.__setattr__(self, '_modelo_entrenado', True)

    def predecir_tendencia(self, dias: int) -> float:
        """
        Proyecta el precio 'n' días hacia el futuro de forma recursiva.
        """

        if not isinstance(dias, int):
            raise TypeError("Error de tipo de dato: Los días a predecir deben ser un número entero.")
        if not self._modelo_entrenado:
            raise RuntimeError("Error: Debe llamar a entrenar_modelo() antes de predecir.")
        if dias <= 0:
            raise ValueError("Error: Los días a predecir deben ser mayores a cero.")
        
        precio_pred = self._ultimo_precio
        for _ in range(dias):
            precio_pred = self._intercepto + self._pendiente * precio_pred
            
        return precio_pred


class Posicion:
    """
    Representa una inversión activa con alertas de riesgo inteligentes.
    """
    def __init__(self, instrumento: Instrumento, cantidad: float, precio_entrada: float):
        if not isinstance(instrumento, Instrumento):
            raise TypeError("Arquitectura: 'instrumento' debe ser un objeto Instrumento.")
        
        self.instrumento = instrumento
        self.cantidad = cantidad 
        self.precio_entrada = precio_entrada
        self._precio_actual = precio_entrada # Inicializa en punto de equilibrio

    @property
    def cantidad(self) -> float:
        return self._cantidad

    @cantidad.setter
    def cantidad(self, valor: float):
        if not isinstance(valor, (int, float)):
            raise TypeError("Error de tipo de dato: La cantidad debe ser un valor numérico.")
        if valor <= 0:
            raise ValueError("Error de Negocio: La cantidad debe ser mayor a cero.")
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

    @property
    def precio_actual(self) -> float:
        return self._precio_actual

    @precio_actual.setter
    def precio_actual(self, valor: float):
        """Permite a los oráculos del mercado actualizar el precio en tiempo real."""
        if not isinstance(valor, (int, float)):
            raise TypeError("Error de tipo de dato: El precio actual debe ser numérico.")
        if valor < 0:
            raise ValueError("Error: El precio actual no puede ser negativo.")
        self._precio_actual = valor

    @property
    def alerta_riesgo(self) -> bool:
        """
        Propiedad inteligente. Retorna True si la pérdida excede el 10% 
        respecto al precio de entrada y el último precio actual registrado.
        """
        variacion = (self._precio_actual - self.precio_entrada) / self.precio_entrada
        return variacion < -0.10

    def calcular_valor_actual(self, precio_mercado: float) -> float:
        if not isinstance(precio_mercado, (int, float)):
            raise TypeError("Error de tipo de dato: El precio de mercado debe ser un valor numérico.")
        if precio_mercado < 0:
            raise ValueError("Error: El precio de mercado no puede ser negativo.")
        self.precio_actual = precio_mercado # Sincroniza estado
        return self.cantidad * precio_mercado

    def calcular_ganancia_no_realizada(self, precio_actual: float) -> float:
        self.precio_actual = precio_actual # Sincroniza estado
        valor_pagado = self.cantidad * self.precio_entrada
        valor_mercado = self.cantidad * precio_actual
        return valor_mercado - valor_pagado
