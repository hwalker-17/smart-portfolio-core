import pytest
import pandas as pd
from fastapi.testclient import TestClient
from unittest.mock import patch
from src.api import app, YahooFinanceClient

# Inicializamos el cliente de pruebas de FastAPI
client = TestClient(app)

# ==========================================
# MOCKS Y DATOS DE PRUEBA
# ==========================================

# Mock para el endpoint web (Lista de diccionarios)
DATOS_HISTORICOS_MOCK = [
    {"Date": "2025-08-30", "Open": 100.0, "High": 110.0, "Low": 95.0, "Close": 105.0, "Volume": 10000},
    {"Date": "2025-08-31", "Open": 105.0, "High": 115.0, "Low": 100.0, "Close": 110.0, "Volume": 15000}
]

# Mock para el cliente real (DataFrame de Pandas)
DATOS_PANDAS_MOCK = pd.DataFrame({
    "Open": [100.0, 105.0],
    "High": [110.0, 115.0],
    "Low": [95.0, 100.0],
    "Close": [105.0, 110.0],
    "Volume": [10000, 15000]
}, index=pd.to_datetime(["2025-08-30", "2025-08-31"]))
DATOS_PANDAS_MOCK.index.name = "Date"


# ==========================================
# TESTS PARA EL ENDPOINT: GET / (Estado API)
# ==========================================

def test_estado_api_exitoso():
    response = client.get("/")
    assert response.status_code == 200
    datos = response.json()
    assert datos["nombre"] == "SmartPortfolio Core API"
    assert datos["estado"] == "Activo"
    assert "descripcion" in datos


# ==========================================
# TESTS PARA EL ENDPOINT: GET /historico/{ticker}
# ==========================================

@patch("src.api.YahooFinanceClient.obtener_historico")
def test_obtener_historico_exitoso(mock_obtener_historico):
    # Camino Feliz: Retorna datos
    mock_obtener_historico.return_value = DATOS_HISTORICOS_MOCK
    
    response = client.get("/historico/aapl") # Pasamos en minúscula para probar normalización
    
    assert response.status_code == 200
    datos = response.json()
    
    assert datos["ticker"] == "AAPL"
    assert datos["total_registros"] == 2
    assert len(datos["data"]) == 2
    assert datos["data"][0]["Close"] == 105.0
    
    # Verificamos que el mock fue llamado exactamente con el parámetro esperado
    mock_obtener_historico.assert_called_once_with("aapl")

@patch("src.api.YahooFinanceClient.obtener_historico")
def test_obtener_historico_no_encontrado(mock_obtener_historico):
    # Camino Triste: Retorna 404 si la lista está vacía
    mock_obtener_historico.return_value = []
    
    response = client.get("/historico/TICKERFALSO")
    
    assert response.status_code == 404
    datos = response.json()
    assert "No se encontraron datos históricos" in datos["detail"]

@patch("src.api.YahooFinanceClient.obtener_historico")
def test_obtener_historico_error_servidor(mock_obtener_historico):
    # Camino Triste: Retorna 500 si el cliente falla
    mock_obtener_historico.side_effect = RuntimeError("Fallo de conexión simulado")
    
    response = client.get("/historico/AAPL")
    
    assert response.status_code == 500
    datos = response.json()
    assert "Fallo de conexión simulado" in datos["detail"]


# ==========================================
# TESTS PARA LA CLASE: YahooFinanceClient
# ==========================================

@patch("src.api.yf.Ticker")
def test_cliente_obtener_datos_exitoso(mock_ticker):
    # Camino Feliz: Retorna solo lista de precios de cierre para ML
    mock_ticker.return_value.history.return_value = DATOS_PANDAS_MOCK
    
    cliente = YahooFinanceClient()
    resultado = cliente.obtener_datos("AAPL")
    
    assert len(resultado) == 2
    assert resultado == [105.0, 110.0]

@patch("src.api.yf.Ticker")
def test_cliente_obtener_datos_vacio(mock_ticker):
    # Camino Triste: Ticker inválido, DataFrame vacío
    mock_ticker.return_value.history.return_value = pd.DataFrame()
    
    cliente = YahooFinanceClient()
    resultado = cliente.obtener_datos("TICKERFALSO")
    
    assert resultado == []

@patch("src.api.yf.Ticker")
def test_cliente_obtener_datos_error(mock_ticker):
    # Camino Triste: Falla la librería externa
    mock_ticker.return_value.history.side_effect = Exception("Caída de API")
    
    cliente = YahooFinanceClient()
    with pytest.raises(RuntimeError, match="Error al obtener datos para ML"):
        cliente.obtener_datos("AAPL")

@patch("src.api.yf.Ticker")
def test_cliente_obtener_historico_exitoso(mock_ticker):
    # Camino Feliz: Retorna OHLCV en formato diccionario para la API
    mock_ticker.return_value.history.return_value = DATOS_PANDAS_MOCK
    
    cliente = YahooFinanceClient()
    resultado = cliente.obtener_historico("AAPL")
    
    assert len(resultado) == 2
    assert resultado[0]["Date"] == "2025-08-30"
    assert resultado[0]["Close"] == 105.0

@patch("src.api.yf.Ticker")
def test_cliente_obtener_historico_vacio(mock_ticker):
    # Camino Triste: Ticker inválido, DataFrame vacío para histórico
    mock_ticker.return_value.history.return_value = pd.DataFrame()
    
    cliente = YahooFinanceClient()
    resultado = cliente.obtener_historico("TICKERFALSO")
    
    assert resultado == []

@patch("src.api.yf.Ticker")
def test_cliente_obtener_historico_error(mock_ticker):
    # Camino Triste: Falla la librería externa al pedir histórico
    mock_ticker.return_value.history.side_effect = Exception("Timeout")
    
    cliente = YahooFinanceClient()
    with pytest.raises(RuntimeError, match="Error al conectar con el proveedor"):
        cliente.obtener_historico("AAPL")