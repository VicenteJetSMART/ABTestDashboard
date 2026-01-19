# Métricas para Home
# Home es el primer paso en el flujo de compra

# ===== NEXT STEP RATE (NSR) =====

# Next Step Rate Home - General
# Mide la tasa de usuarios que pasan de home a flight
HOME_NSR = {'events': [
    ('homepage_dom_loaded', []),
    ('flight_dom_loaded_flight', [])
]}

# ===== WEBSITE CONVERSION RATE (WCR) =====

# Website Conversion Rate from Home - General
# Mide la conversión desde home hasta revenue
HOME_WCR = {'events': [
    ('homepage_dom_loaded', []),
    ('revenue_amount', [])
]}

