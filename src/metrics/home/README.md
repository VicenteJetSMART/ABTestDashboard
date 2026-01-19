# Métricas de Home

Métricas relacionadas con el home/landing page en el flujo de compra.

## Métricas Disponibles

### NSR (Next Step Rate)
- **HOME_NSR**: Tasa de usuarios que pasan de home a flight

### WCR (Website Conversion Rate)
- **HOME_WCR**: Conversión desde home hasta revenue (compra final)

## Eventos Utilizados
- `home_dom_loaded` - Evento que se dispara cuando el home/landing page se carga
- `flight_dom_loaded_flight` - Evento que se dispara cuando la página de selección de vuelos se carga
- `revenue_amount` - Evento que se dispara cuando se confirma el pago

## Flujo de Conversión

```
Home → Flight → Baggage → Seats → Extras → Passengers → Payment → Revenue
 ↓                                                                      ↑
 └─────────────────────────────── WCR ───────────────────────────────┘
 └── NSR ──→
```

## Uso

```python
from src.metrics.home import HOME_NSR, HOME_WCR

# NSR: Next Step Rate
nsr_events = HOME_NSR['events']
# [('home_dom_loaded', []), ('flight_dom_loaded_flight', [])]

# WCR: Website Conversion Rate
wcr_events = HOME_WCR['events']
# [('home_dom_loaded', []), ('revenue_amount', [])]
```

## Notas

- **HOME_NSR**: Mide qué tan efectivo es el home para llevar usuarios al siguiente paso (flight)
- **HOME_WCR**: Mide la conversión completa desde el home hasta la compra final
- Ambas métricas no requieren filtros adicionales ya que miden el comportamiento general del home
- Los filtros globales del dashboard (Culture, Device, etc.) se aplicarán automáticamente

