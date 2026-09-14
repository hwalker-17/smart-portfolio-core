import yfinance as yf

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