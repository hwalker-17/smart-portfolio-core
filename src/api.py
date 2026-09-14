"""
Módulo de API para SmartPortfolio utilizando FastAPI.
Expone endpoints para consultar datos históricos de mercado y conecta con el modelo de dominio.
"""

from fastapi import FastAPI, HTTPException
import yfinance as yf
from typing import List

app = FastAPI(
    title="SmartPortfolio Core API",
    description="API de microservicios para el Core Bancario y Análisis de Inversiones.",
    version="1.0.0"
)

@app.get("/", summary="Información general de la API")
def estado_api():
    """
    Endpoint raíz que proporciona una descripción general de las capacidades de la API.
    """
    return {
        "nombre": "SmartPortfolio Core API",
        "descripcion": "API de microservicios para el Core Bancario. Permite consultar datos históricos de mercado y ejecutar modelos predictivos para análisis de inversiones.",
        "version": "1.0.0",
        "estado": "Activo"
    }

class YahooFinanceClient:
    """
    Cliente concreto para interactuar con Yahoo Finance.
    Cumple estrictamente con la interfaz MarketDataProvider de modelos.py.
    """
    
    def obtener_datos(self, ticker: str) -> List[float]:
        """
        Implementación del Protocolo MarketDataProvider (Para el Core de Negocio).
        Retorna únicamente los precios de cierre en una lista plana para el modelo predictivo OLS.
        """
        try:
            accion = yf.Ticker(ticker.upper())
            df = accion.history(period="1y")
            
            if df.empty:
                return []
                
            return df['Close'].tolist()
        except Exception as e:
            raise RuntimeError(f"Error al obtener datos para ML: {str(e)}")

    def obtener_historico(self, ticker: str) -> list[dict]:
        """
        Método extendido (Para el Endpoint de la API).
        Retorna la data completa (OHLCV) estructurada en diccionarios para serialización JSON.
        """
        try:
            accion = yf.Ticker(ticker.upper())
            df = accion.history(period="1y")
            
            if df.empty:
                return []
            
            # Limpiamos y transformamos el DataFrame a una lista de diccionarios JSON-friendly
            df = df.reset_index()
            df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
            
            registros = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']].to_dict(orient='records')
            return registros
        except Exception as e:
            raise RuntimeError(f"Error al conectar con el proveedor de datos: {str(e)}")


@app.get("/historico/{ticker}", summary="Obtener historial de precios de un ticker")
def obtener_historico_ticker(ticker: str):
    """
    Endpoint GET que recibe un símbolo de ticker (ej: AAPL, BTC-USD) 
    y retorna su histórico de precios del último año usando YahooFinanceClient.
    """
    try:
        cliente = YahooFinanceClient() 
        datos = cliente.obtener_historico(ticker)
        
        if not datos:
            raise HTTPException(
                status_code=404, 
                detail=f"No se encontraron datos históricos para el ticker '{ticker.upper()}'."
            )
            
        return {
            "ticker": ticker.upper(),
            "total_registros": len(datos),
            "data": datos
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))