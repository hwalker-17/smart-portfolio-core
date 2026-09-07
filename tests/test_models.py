import pytest
from src.modelos import Instrumento, Posicion

# ==========================================
# TESTS PARA LA CLASE: Instrumento
# ==========================================

def test_instrumento_limpieza_exitosa():
    inst = Instrumento(ticker=" aapl ", tipo="etf", sector="tecnología ")
    assert inst.ticker == "AAPL"
    assert inst.tipo == "ETF"
    assert inst.sector == "Tecnología"

def test_instrumento_ticker_vacio():
    with pytest.raises(ValueError):
        Instrumento(ticker="", tipo="Acción", sector="Tecnología")

def test_instrumento_sector_vacio():
    with pytest.raises(ValueError):
        Instrumento(ticker="AAPL", tipo="Acción", sector="")

def test_instrumento_tipo_invalido():
    with pytest.raises(ValueError):
        Instrumento(ticker="AAPL", tipo="Cripto", sector="Tecnología")

def test_instrumento_sector_invalido():
    with pytest.raises(ValueError):
        Instrumento(ticker="AAPL", tipo="Acción", sector="Agricultura")

# ==========================================
# TESTS PARA LA CLASE: Posicion (Creación y Setters)
# ==========================================

def test_posicion_creacion_invalida(instrumento_test):
    # Validar cantidad negativa en la creación
    with pytest.raises(ValueError):
        Posicion(instrumento=instrumento_test, cantidad=-5, precio_entrada=100.0)

def test_posicion_instrumento_invalido():
    with pytest.raises(TypeError):
        Posicion(instrumento="NoSoyUnInstrumento", cantidad=10, precio_entrada=100.0)

def test_posicion_setters_errores_tipo(instrumento_test):
    posicion = Posicion(instrumento=instrumento_test, cantidad=10, precio_entrada=100.0)
    with pytest.raises(TypeError):
        posicion.cantidad = "Diez"
    with pytest.raises(TypeError):
        posicion.precio_entrada = "Cien"

def test_posicion_setters_errores_valor(instrumento_test):
    posicion = Posicion(instrumento=instrumento_test, cantidad=10, precio_entrada=100.0)
    with pytest.raises(ValueError):
        posicion.cantidad = -5
    with pytest.raises(ValueError):
        posicion.precio_entrada = -50.0

def test_posicion_precio_actual_invalido(instrumento_test):
    posicion = Posicion(instrumento=instrumento_test, cantidad=10, precio_entrada=100.0)
    with pytest.raises(TypeError):
        posicion.precio_actual = "Strings no"
    with pytest.raises(ValueError):
        posicion.precio_actual = -10.0

# ==========================================
# TESTS CLASE: Posicion (Alerta de Riesgo)
# ==========================================

def test_posicion_alerta_riesgo_falsa(instrumento_test):
    # Compra a 100. El precio actual (default) es 100. Pérdida = 0%.
    posicion = Posicion(instrumento=instrumento_test, cantidad=10, precio_entrada=100.0)
    assert posicion.alerta_riesgo is False
    
    # Precio cae a 95. Pérdida = 5%. (No pasa de 10%)
    posicion.precio_actual = 95.0
    assert posicion.alerta_riesgo is False
    
    # Precio cae exactamente a 90. Pérdida = 10%. (La regla dice > 10%)
    posicion.precio_actual = 90.0
    assert posicion.alerta_riesgo is False

def test_posicion_alerta_riesgo_verdadera(instrumento_test):
    # Compra a 100. Cae a 85. Pérdida = 15%. Debería activar alerta.
    posicion = Posicion(instrumento=instrumento_test, cantidad=10, precio_entrada=100.0)
    posicion.precio_actual = 85.0
    assert posicion.alerta_riesgo is True

# ==========================================
# TESTS CLASE: Posicion (Cálculos y Parametrize)
# ==========================================

def test_calcular_valor_actual_exitoso(instrumento_test):
    posicion = Posicion(instrumento=instrumento_test, cantidad=10, precio_entrada=100.0)
    assert posicion.calcular_valor_actual(150.0) == 1500.0
    assert posicion.precio_actual == 150.0 # Valida sincronización

def test_calcular_valor_actual_errores(instrumento_test):
    posicion = Posicion(instrumento=instrumento_test, cantidad=10, precio_entrada=100.0)
    with pytest.raises(TypeError):
        posicion.calcular_valor_actual("Cincuenta")
    with pytest.raises(ValueError):
        posicion.calcular_valor_actual(-10.0)

@pytest.mark.parametrize(
    "precio_entrada, precio_actual, cantidad, esperado",
    [
        (100, 150, 10, 500),   # Camino Feliz: Ganancia
        (200, 180, 5, -100),   # Camino Feliz: Pérdida
        (50, 50, 7, 0),        # Camino Feliz: Empate
    ],
)
def test_calculo_pnl(precio_entrada, precio_actual, cantidad, esperado, instrumento_test):
    posicion = Posicion(instrumento=instrumento_test, cantidad=cantidad, precio_entrada=precio_entrada)
    pnl = posicion.calcular_ganancia_no_realizada(precio_actual=precio_actual)
    assert pnl == pytest.approx(esperado)
