# Métricas para Flight
# Flight es el segundo paso en el flujo de compra (después de home)

# ===== NEXT STEP RATE (NSR) =====

# Next Step Rate Flight - General
# Mide la tasa de usuarios que pasan de flight a baggage
FLIGHTS_NSR = {'events': [
    ('flight_dom_loaded_flight', []),
    ('baggage_dom_loaded', [])
]}

# ===== WEBSITE CONVERSION RATE (WCR) =====

# Website Conversion Rate from Flight - General
# Mide la conversión desde flight hasta revenue
FLIGHTS_WCR = {'events': [
    ('flight_dom_loaded_flight', []),
    ('revenue_amount', [])
]}

# ===== ADD TO CART (A2C) =====

# Flights Add to Cart
# Mide la tasa de selección de vuelos usando el evento custom flight_selected
FLIGHTS_A2C = {'events': [
    ('flight_dom_loaded_flight', []),
    ('ce:flight_selected', [])
]}

# Bundles Add to Cart
# Mide la tasa de selección de bundles usando el evento custom bundle_a2c
BUNDLES_A2C = {'events': [
    ('flight_dom_loaded_flight', []),
    ('ce:bundle_a2c', [])
]}

# ===== CONVERSION RATE (CR) =====

# Bundles Conversion Rate
# Mide la conversión desde la carga de flight hasta confirmación de pago con bundle
BUNDLES_CR = {'events': [
    ('flight_dom_loaded_flight', []),
    ('ce:payment_confirmation_with_any_bundle', [])
]}
