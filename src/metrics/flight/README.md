# Métricas de Flight (Vuelos)

Métricas relacionadas con el step de selección de vuelos en el flujo de compra.

## Métricas Disponibles

### NSR (Next Step Rate)
- **FLIGHTS_NSR**: Tasa de usuarios que pasan de flight a baggage

### WCR (Website Conversion Rate)
- **FLIGHTS_WCR**: Conversión desde flight hasta revenue

### A2C (Add to Cart)
- **FLIGHTS_A2C**: Tasa de selección de vuelos (usando evento custom `ce:flight_selected`)
- **BUNDLES_A2C**: Tasa de selección de bundles (usando evento custom `ce:bundle_a2c`)

### CR (Conversion Rate)
- **BUNDLES_CR**: Conversión desde la carga de flight hasta confirmación de pago con bundle

## Eventos Utilizados

### Eventos Estándar
- `flight_dom_loaded_flight` - Página de vuelos cargada
- `baggage_dom_loaded` - Siguiente paso (equipaje)
- `revenue_amount` - Conversión final

### Custom Events
- `ce:flight_selected` - Vuelo seleccionado (custom event)
- `ce:bundle_a2c` - Bundle agregado al carrito (custom event)
- `ce:payment_confirmation_with_any_bundle` - Confirmación de pago con bundle (custom event)

## Uso

```python
from src.metrics.flight import (
    FLIGHTS_NSR,
    FLIGHTS_WCR,
    FLIGHTS_A2C,
    BUNDLES_A2C,
    BUNDLES_CR
)

# NSR: Next Step Rate
nsr_events = FLIGHTS_NSR['events']
# [('flight_dom_loaded_flight', []), ('baggage_dom_loaded', [])]

# WCR: Website Conversion Rate
wcr_events = FLIGHTS_WCR['events']
# [('flight_dom_loaded_flight', []), ('revenue_amount', [])]

# A2C: Flights Add to Cart
flights_a2c_events = FLIGHTS_A2C['events']
# [('flight_dom_loaded_flight', []), ('ce:flight_selected', [])]

# A2C: Bundles Add to Cart
bundles_a2c_events = BUNDLES_A2C['events']
# [('flight_dom_loaded_flight', []), ('ce:bundle_a2c', [])]

# CR: Bundles Conversion Rate
bundles_cr_events = BUNDLES_CR['events']
# [('flight_dom_loaded_flight', []), ('ce:payment_confirmation_with_any_bundle', [])]
```

## Notas

- **Custom Events**: Los eventos con prefijo `ce:` son custom events de Amplitude
- **Sin filtros adicionales**: Todas las métricas miden el comportamiento general sin filtros específicos
- **Filtros globales**: Los filtros del dashboard (Culture, Device, etc.) se aplican automáticamente
- **FLIGHTS_A2C vs BUNDLES_A2C**: FLIGHTS_A2C mide la selección de vuelos individuales, mientras que BUNDLES_A2C mide la selección de bundles (paquetes)
- **BUNDLES_CR**: Mide la conversión completa desde que el usuario carga la página de vuelos hasta que confirma el pago con un bundle (usa custom event `ce:payment_confirmation_with_any_bundle` para validar que el pago incluyó un bundle)

## Flujo de Conversión

```
Home → Flight → Baggage → Seats → Extras → Passengers → Payment → Revenue
        ↓                                                              ↑
        └──────────────────────── FLIGHTS_WCR ───────────────────────┘
        └─ FLIGHTS_NSR ──→
        
Flight → Bundle Selection → Payment Confirmation (with bundle)
  ↓                           ↑
  └────────── BUNDLES_CR ────┘
```

