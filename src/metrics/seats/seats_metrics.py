# filtros amplitude
from src.utils.amplitude_filters import (
    get_DB_filter,
    seat_selected_filter,
    bundle_selected_filter
)

# ===== CONSTANTES: PROPIEDADES DE CONTEO DE ASIENTOS =====
# Definición de propiedades de asiento según lógica GOLD
SEAT_COUNT_PROPS = [
    'seat_estandar_count',
    'seat_primera_fila_count',
    'seat_salida_emergencia_count',
    'seat_salida_rapida_count',
    'seat_smart_count'
]


def get_seat_count_filter():
    """
    Filtro para verificar que se haya vendido al menos un asiento de cualquier tipo.
    Usa las propiedades de conteo definidas en SEAT_COUNT_PROPS.
    
    Lógica GOLD: Verifica que la suma de todas las propiedades de conteo sea > 0:
    - seat_estandar_count
    - seat_primera_fila_count
    - seat_salida_emergencia_count
    - seat_salida_rapida_count
    - seat_smart_count
    
    Nota: Amplitude no soporta sumas directamente en filtros, por lo que usamos
    la propiedad 'seats' que representa el total de asientos vendidos.
    En el futuro, si Amplitude soporta filtros OR complejos, se podría verificar
    cada propiedad individualmente.
    """
    return {
        'subprop_type': 'event',
        'subprop_key': 'seats',
        'subprop_op': 'greater',
        'subprop_value': [0]
    }


# ===== WEBSITE CONVERSION RATE (WCR) =====

# Website Conversion Rate Seats - General
SEATS_WCR = {'events': [
    ('seatmap_dom_loaded', []),
    ('revenue_amount', [])
]}

# ===== NEXT STEP RATE (NSR) =====

# Next Step Rate Seats - General
SEATS_NSR = {'events': [
    ('seatmap_dom_loaded', []),
    ('extras_dom_loaded', [])
]}

# Next Step Rate Seats - DB
SEATS_DB_NSR = {'events': [
    ('seatmap_dom_loaded', [get_DB_filter()]),
    ('extras_dom_loaded', [get_DB_filter()])
]}

# Next Step Rate Seats - Con Asientos Seleccionados
SEATS_WITH_SELECTION_NSR = {'events': [
    ('seatmap_dom_loaded', []),
    ('extras_dom_loaded', [seat_selected_filter()])
]}

# Next Step Rate Seats - Con Bundle
SEATS_WITH_BUNDLE_NSR = {'events': [
    ('seatmap_dom_loaded', []),
    ('extras_dom_loaded', [bundle_selected_filter()])
]}

# ===== CONVERSION RATE (CR) =====

# Seats CR - General (Lógica GOLD: Conversión real basada en venta confirmada de cualquier tipo de asiento)
SEATS_CR = {'events': [
    ('seatmap_dom_loaded', []),
    ('revenue_amount', [get_seat_count_filter()])
]}

# Seats CR - DB (El filtro va en el EVENTO FINAL usando propiedades nativas de revenue_amount)
SEATS_DB_CR = {'events': [
    ('seatmap_dom_loaded', [get_DB_filter()]),
    ('revenue_amount', [get_seat_count_filter()])
]}

# Seats CR - Con Asientos Seleccionados (El filtro va en el EVENTO FINAL usando propiedades nativas de revenue_amount)
SEATS_WITH_SELECTION_CR = {'events': [
    ('seatmap_dom_loaded', []),
    ('revenue_amount', [get_seat_count_filter()])
]}

# Seats CR - Con Bundle (El filtro va en el EVENTO FINAL usando propiedades nativas de revenue_amount)
SEATS_WITH_BUNDLE_CR = {'events': [
    ('seatmap_dom_loaded', []),
    ('revenue_amount', [get_seat_count_filter()])
]}

# CR Outbound Seat
OUTBOUND_SEAT_CR = {'events': [
    ('outbound_seat_selected', []),
    ('revenue_amount', [get_seat_count_filter()])
]}

# CR Inbound Seat
INBOUND_SEAT_CR = {'events': [
    ('inbound_seat_selected', []),
    ('revenue_amount', [get_seat_count_filter()])
]}

# ===== ADD TO CART (A2C) =====

# Seats A2C - General (Selección de asientos)
SEATS_A2C = {'events': [
    ('seatmap_dom_loaded', []),
    ('continue_clicked_seat', [seat_selected_filter()])
]}

# Seats A2C - DB
SEATS_DB_A2C = {'events': [
    ('seatmap_dom_loaded', [get_DB_filter()]),
    ('continue_clicked_seat', [seat_selected_filter(), get_DB_filter()])
]}

# Seats A2C - Outbound (Selección de asiento de ida)
SEATS_OUTBOUND_A2C = {'events': [
    ('seatmap_dom_loaded', []),
    ('outbound_seat_selected', [])
]}

# Seats A2C - Inbound (Selección de asiento de regreso)
SEATS_INBOUND_A2C = {'events': [
    ('outbound_seat_selected', []),
    ('inbound_seat_selected', [])
]}

# Add to Cart Outbound Seat
OUTBOUND_SEAT_A2C = {'events': [
    ('seatmap_dom_loaded', []),
    ('outbound_seat_selected', [])
]}

# Add to Cart Inbound Seat
INBOUND_SEAT_A2C = {'events': [
    ('seatmap_dom_loaded', []),
    ('inbound_seat_selected', [])
]}

# ===== SELECTION RATE =====

# Seat Selection Rate (cualquier asiento)
SEAT_SELECTION_RATE = {'events': [
    ('seatmap_dom_loaded', []),
    ('seatmap_dom_loaded', [seat_selected_filter()])
]}
