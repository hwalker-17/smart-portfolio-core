from unittest.mock import MagicMock, patch
from src.providers import StockProvider

def test_get_price_mocked():
    provider = StockProvider()
    
    with patch("yfinance.Ticker") as mock_ticker:
        mock_instance = MagicMock()
        mock_instance.fast_info = {"last_price": 150.25}
        mock_ticker.return_value = mock_instance
        
        price = provider.get_price("AAPL")
        
        assert price == 150.25
        mock_ticker.assert_called_once_with("AAPL")