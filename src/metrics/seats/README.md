# Métricas de Seats (Asientos)

Métricas relacionadas con el step de selección de asientos en el flujo de compra.

## Métricas Disponibles

### NSR (Next Step Rate)
Tasa de usuarios que pasan de seatmap a extras:
- **NSR_SEATS**: General (sin filtros)
- **NSR_SEATS_DB**: Solo flujo Direct Booking
- **NSR_SEATS_WITH_SELECTION**: Con asientos seleccionados
- **NSR_SEATS_WITH_BUNDLE**: Con bundle seleccionado

### CR (Conversion Rate)
Conversión desde seatmap hasta revenue:
- **SEATS_CR**: General (sin filtros)
- **SEATS_CR_DB**: Solo flujo Direct Booking
- **SEATS_CR_WITH_SELECTION**: Con asientos seleccionados
- **SEATS_CR_WITH_BUNDLE**: Con bundle seleccionado

### A2C (Add to Cart)
Tasa de selección de asientos:
- **SEATS_A2C**: Selección general con click en continuar
- **SEATS_A2C_DB**: Selección en flujo DB
- **SEATS_A2C_OUTBOUND**: Selección de asiento de ida
- **SEATS_A2C_INBOUND**: Selección de asiento de regreso
- **SEATS_A2C_BUNDLE_OUTBOUND**: Selección de bundle de ida
- **SEATS_A2C_BUNDLE_INBOUND**: Selección de bundle de regreso

### Métricas Específicas Adicionales
- **COMPLETE_SEAT_SELECTION**: Selección completa de asientos (ida + regreso)
- **COMPLETE_BUNDLE_SELECTION**: Selección completa de bundles (ida + regreso)
- **SEAT_SELECTION_RATE**: Tasa de selección de cualquier asiento

## Filtros Utilizados

### Filtros de Flujo
- **get_DB_filter()**: Filtra por flujo Direct Booking

### Filtros de Selección
- **seat_selected_filter()**: Filtra por usuarios que seleccionaron asientos (seat_count > 0)
- **bundle_selected_filter()**: Filtra por usuarios que seleccionaron bundles

## Eventos Utilizados
- `seatmap_dom_loaded`: Carga del mapa de asientos
- `outbound_seat_selected`: Selección de asiento de ida
- `inbound_seat_selected`: Selección de asiento de regreso
- `continue_clicked_seat`: Click en continuar en seatmap
- `outbound_bundle_selected`: Selección de bundle de ida
- `inbound_bundle_selected`: Selección de bundle de regreso
- `extras_dom_loaded`: Siguiente paso (extras)
- `revenue_amount`: Conversión final

## Ejemplos de Uso

### Comparar conversión con y sin selección de asientos
1. **SEATS_CR**: Conversión general
2. **SEATS_CR_WITH_SELECTION**: Conversión cuando seleccionan asientos
   - La diferencia muestra el impacto de seleccionar asientos en la conversión

### Analizar efectividad de bundles
1. **SEATS_A2C_BUNDLE_OUTBOUND**: Tasa de selección de bundle de ida
2. **SEATS_A2C_BUNDLE_INBOUND**: Tasa de selección de bundle de regreso
3. **COMPLETE_BUNDLE_SELECTION**: Tasa de selección completa

### Optimizar flujo DB
- **NSR_SEATS_DB**: Next step rate en DB
- **SEATS_CR_DB**: Conversión en DB
- **SEATS_A2C_DB**: Selección de asientos en DB

