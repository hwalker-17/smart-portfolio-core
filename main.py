import json
from datetime import datetime
import numpy as np
import yfinance as yf
from sklearn.linear_model import LinearRegression


class StockProvider:
    def get_price(self, ticker: str) -> float:
        """Obtiene el precio actual de una acción desde Yahoo Finance."""
        data = yf.Ticker(ticker)
        fast_info = getattr(data, 'fast_info', None)
        
        if fast_info and 'last_price' in fast_info and fast_info['last_price'] is not None:
            return float(fast_info['last_price'])
        
        history = data.history(period="1d")
        if not history.empty:
            return float(history['Close'].iloc[-1])
            
        raise ValueError(f"No se pudieron obtener datos para el ticker: {ticker}")


def predict_future_price(current_price: float) -> float:
    """Simula una predicción mediante regresión lineal simple."""
    x = np.array([1, 2, 3, 4, 5]).reshape(-1, 1)
    y = np.array([
        current_price * 0.98,
        current_price * 0.99,
        current_price,
        current_price * 1.01,
        current_price * 1.02
    ])
    
    model = LinearRegression()
    model.fit(x, y)
    
    predicted = model.predict([[6]])
    return float(predicted[0])


def main():
    print("=== SMART PORTFOLIO - ORÁCULO DE INVERSIÓN ===")
    ticker = input("Ingresa el Ticker de la acción (ej: AAPL, MSFT, TSLA): ").strip().upper()
    
    if not ticker:
        print("Ticker inválido.")
        return

    try:
        print(f"Obteniendo precio actual para {ticker}...")
        provider = StockProvider()
        current_price = provider.get_price(ticker)
        print(f"Precio actual de {ticker}: ${current_price:.2f}")

        predicted_price = predict_future_price(current_price)
        print(f"Predicción estimada (siguiente periodo): ${predicted_price:.2f}")

        choice = input(f"¿Deseas registrar la compra simulada de {ticker}? (s/n): ").strip().lower()

        if choice == 's':
            trade_data = {
                "ticker": ticker,
                "current_price": current_price,
                "predicted_price": predicted_price,
                "timestamp": datetime.now().isoformat(),
                "action": "BUY"
            }
            
            filename = f"trade_{ticker}.json"
            with open(filename, "w") as f:
                json.dump(trade_data, f, indent=4)
                
            print(f"¡Transacción guardada exitosamente en '{filename}'!")
        else:
            print("Operación cancelada. No se registraron compras.")

    except Exception as e:
        print(f"Ocurrió un error al procesar el ticker '{ticker}': {e}")


if __name__ == "__main__":
    main()