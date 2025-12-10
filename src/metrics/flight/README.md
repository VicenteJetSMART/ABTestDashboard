# Métricas de Flight (Vuelos)

Métricas relacionadas con el step de selección de vuelos en el flujo de compra.

## Métricas Disponibles

### NSR (Next Step Rate)
- **NSR_FLIGHT**: Tasa de usuarios que pasan de flight a baggage (general)
- **NSR_FLIGHT_DB**: Tasa de usuarios que pasan de flight a baggage (solo DB)

### WCR (Website Conversion Rate)
- **WCR_FLIGHT**: Conversión desde flight hasta revenue (general)
- **WCR_FLIGHT_DB**: Conversión desde flight hasta revenue (solo DB)

### Métricas Específicas
- **OUTBOUND_FLIGHT_SELECTION**: Tasa de selección de vuelo de ida
- **INBOUND_FLIGHT_SELECTION**: Tasa de selección de vuelo de regreso
- **COMPLETE_FLIGHT_SELECTION**: Tasa de selección completa (ida + regreso)
- **FLIGHT_CONTINUE_RATE**: Tasa de click en continuar después de seleccionar vuelos

## Eventos Utilizados
- `flight_dom_loaded_flight`
- `outbound_flight_selected_flight`
- `inbound_flight_selected_flight`
- `continue_clicked_flight`
- `baggage_dom_loaded`
- `revenue_amount`

