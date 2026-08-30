
# SmartPortfolio 🚀

Sistema de gestión de portafolios de inversión desarrollado en Python. Reemplaza el control manual en Excel con un backend robusto, tipado y validado que previene errores humanos.

## Equipo

| Nombre | Rol |
|--------|-----|
| Hannah Walker | Arquitecto (Repository Owner) |
| Cristian Huertas | Desarrollador - Modelos |
| Cristian Suarez | Desarrollador - Lógica y Reportes |

## Estructura del Proyecto

smart-portfolio-core/
├── src/
│   ├── __init__.py
│   ├── modelos.py       # Clases Instrumento y Posicion
│   ├── portafolio.py    # Clase Portafolio
│   └── reportes.py      # Clase ReportadorFinanciero
├── tests/
│   ├── conftest.py      # Fixtures reutilizables
│   └── test_models.py   # Tests de modelos
├── .gitignore
├── README.md
└── main.py              # Script de prueba

## Cómo correr el proyecto

python main.py

## Cómo correr los tests

PYTHONPATH=. python -m pytest -v

## Principios aplicados

- SOLID: Separación clara de responsabilidades entre módulos
- Dataclasses: Modelos inmutables con frozen=True
- Type Hints: Tipado estricto en todas las funciones
- Validaciones: @property para prevenir datos inválidos