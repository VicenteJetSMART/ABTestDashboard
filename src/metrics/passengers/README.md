# Métricas de Passengers (Pasajeros)

Métricas relacionadas con el step de información de pasajeros en el flujo de compra.

## Métricas Disponibles

### NSR (Next Step Rate)
- **NSR_PASSENGERS**: Tasa de usuarios que pasan de passengers a payment (general)
- **NSR_PASSENGERS_DB**: Tasa de usuarios que pasan de passengers a payment (solo DB)

### WCR (Website Conversion Rate)
- **WCR_PASSENGERS**: Conversión desde passengers hasta revenue (general)
- **WCR_PASSENGERS_DB**: Conversión desde passengers hasta revenue (solo DB)

### Métricas Específicas
- **PASSENGERS_CONTINUE_RATE**: Tasa de click en continuar en passengers
- **GENDER_CONTINUE_RATE**: Tasa de click en continuar después de género
- **AADVANTAGE_CLICK_RATE**: Tasa de interacción con AAdvantage
- **PASSENGERS_LOGIN_RATE**: Tasa de login de usuarios en passengers

## Eventos Utilizados
- `passengers_dom_loaded`
- `continue_clicked_passengers`
- `continue_gender_passengers`
- `click_aadvantage_passengers`
- `user_login`
- `payment_dom_loaded`
- `revenue_amount`

