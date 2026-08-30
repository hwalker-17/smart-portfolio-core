import pytest
from src.modelos import Instrumento

@pytest.fixture
def instrumento_test():
    """Fixture requerido por la rúbrica (Responsabilidad: modelos)."""
    return Instrumento(ticker="TSLA", tipo="Acción", sector="Tecnología")