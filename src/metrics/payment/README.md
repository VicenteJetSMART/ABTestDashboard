# Métricas de Payment (Pagos)

Métricas relacionadas con el step de pagos y confirmación en el flujo de compra.

## Métricas Disponibles

### NSR (Next Step Rate)
- **NSR_PAYMENT**: Tasa de usuarios que pasan de payment a confirmation (general)
- **NSR_PAYMENT_DB**: Tasa de usuarios que pasan de payment a confirmation (solo DB)

### WCR (Website Conversion Rate)
- **WCR_PAYMENT**: Conversión desde payment hasta revenue (general)
- **WCR_PAYMENT_DB**: Conversión desde payment hasta revenue (solo DB)

### Métricas Específicas
- **PAYMENT_SELECTED_RATE**: Tasa de selección de método de pago
- **PAYMENT_CLICK_RATE**: Tasa de click en botón de pago
- **INSTALLMENTS_SELECTION_RATE**: Tasa de selección de cuotas
- **SKIP_DIRECT_PAYMENT_RATE**: Tasa de skip del modal de pago directo
- **TOGGLE_TAXES_RATE**: Tasa de click en toggle de impuestos
- **PAYMENT_TO_REVENUE**: Conversión final de confirmación a revenue

## Eventos Utilizados
- `payment_dom_loaded`
- `payment_selected`
- `payment_clicked`
- `installments_selected`
- `modal_skip_direct_payment_clicked`
- `click_toggle_taxes`
- `payment_confirmation_loaded`
- `revenue_amount`

