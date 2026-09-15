from dataclasses import dataclass
import pytest
from src.modelos import Instrumento, Posicion
from src.portafolio import Portafolio, PosicionNoExisteError
from src.reportes import ReportadorFinanciero


@dataclass(frozen=True)
class InstrumentoPrueba(Instrumento):
    """Subclase concreta de Instrumento con tipo de instrumento válido."""

    pass


def test_agregar_posicion_camino_feliz():
    portafolio = Portafolio()
    instrumento = InstrumentoPrueba("AAPL", "Acción", "Tecnología")
    posicion = Posicion(instrumento, 10, 150.0)

    portafolio.agregar_posicion(posicion)

    assert len(portafolio.posiciones) == 1
    assert portafolio.posiciones[0] == posicion


def test_remover_posicion_camino_feliz():
    portafolio = Portafolio()
    instrumento = InstrumentoPrueba("AAPL", "Acción", "Tecnología")
    posicion = Posicion(instrumento, 10, 150.0)
    portafolio.agregar_posicion(posicion)

    portafolio.remover_posicion("AAPL")

    assert len(portafolio.posiciones) == 0


def test_remover_posicion_camino_infeliz():
    portafolio = Portafolio()

    with pytest.raises(PosicionNoExisteError):
        portafolio.remover_posicion("TSLA")


def test_reportador_financiero_cobertura():
    portafolio = Portafolio()
    instrumento = InstrumentoPrueba("AAPL", "Acción", "Tecnología")
    posicion = Posicion(instrumento, 10, 150.0)
    portafolio.agregar_posicion(posicion)

    reportador = ReportadorFinanciero()
    reportador.imprimir_resumen(portafolio)