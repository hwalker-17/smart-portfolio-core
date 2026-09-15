
## API REST

### Correr el servidor

```bash
uvicorn src.api:app --reload
```

Documentación interactiva disponible en: `http://127.0.0.1:8000/docs`

### Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Estado general de la API |
| GET | `/historico/{ticker}` | Historial de precios del último año |
| GET | `/pronostico/{ticker}?dias=7` | Predicción de precio con regresión lineal |

## CLI: El Oráculo Financiero

```bash
python main.py
```

Ingresa un ticker, obtiene el precio actual y predice la tendencia usando regresión lineal.

## Cómo correr los tests

```bash
python -m pytest -v
```

Con reporte de cobertura:

```bash
python -m pytest --cov=src --cov-report=term-missing
```

Cobertura actual: **96%**

## Principios aplicados

- **SOLID**: Separación clara de responsabilidades entre módulos
- **Dataclasses**: Modelos inmutables con `frozen=True`
- **Type Hints**: Tipado estricto en todas las funciones
- **Validaciones**: `@property` para prevenir datos inválidos
- **Protocol**: Inyección de dependencias con `MarketDataProvider`
- **FastAPI**: API REST con documentación automática (Swagger)
- **ML**: Regresión lineal con scikit-learn para predicción de precios