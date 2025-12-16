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

# Propiedades de revenue para validar compra de asientos
REVENUE_SEAT_TYPES = [
    'seat_estandar_count',
    'seat_primera_fila_count',
    'seat_salida_emergencia_count',
    'seat_salida_rapida_count',
    'seat_smart_count',
    'seats'  # Propiedad genérica de asientos en revenue
]


def get_seat_count_filter():
    """
    Filtro para verificar que se haya vendido al menos un asiento de cualquier tipo.
    Usa las propiedades de conteo definidas en SEAT_COUNT_PROPS.
    
    Lógica GOLD: Verifica que la suma de todas las propiedades de conteo sea > 0.
    """
    return {
        'subprop_type': 'event',
        'subprop_key': 'seats',
        'subprop_op': 'greater',
        'subprop_value': [0]
    }


def seats_count_filter():
    """
    Filtro técnico para validar que se seleccionaron asientos en el paso 2 (bridge).
    Usa la propiedad 'seats_count' para verificar que hay al menos un asiento seleccionado.
    IMPORTANTE: Este filtro NO incluye filtros de segmento (Family, Business, etc.).
    Solo valida la acción técnica de selección de asientos.
    """
    return {
        'subprop_type': 'event',
        'subprop_key': 'seats_count',
        'subprop_op': 'greater',
        'subprop_value': [0]
    }


def has_seat_purchase_filter():
    """
    Filtro técnico para validar que se pagó por asientos en el paso 3 (goal).
    Usa las propiedades de revenue definidas en REVENUE_SEAT_TYPES.
    IMPORTANTE: Este filtro NO incluye filtros de segmento (Family, Business, etc.).
    Solo valida la compra técnica de asientos.
    """
    # Usamos la propiedad 'seats' que representa el total de asientos vendidos en revenue
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

# ===== NEXT STEP RATE (NSR) - ESTRATEGIA GHOST ANCHOR =====

# Next Step Rate Seats - General (Estrategia Ghost Anchor)
# PROBLEMA RESUELTO: Al filtrar por segmentos (ej: "Travel Group = Familia"), 
# el evento continue_clicked_seat devuelve 0 porque NO tiene la propiedad de segmento.
# SOLUCIÓN: Funnel de 2 pasos donde:
# - Paso 1 (seatmap_dom_loaded): ÚNICO que recibe filtros de segmento (Family, Business, etc.)
# - Paso 2 (continue_clicked_seat): NO recibe filtros de segmento, solo valida seats_count > 0
SEATS_NSR = {'events': [
    ('seatmap_dom_loaded', []),  # 1. ANCHOR: Aquí "muerden" los filtros globales del Dashboard (Family, Business, etc.)
    ('continue_clicked_seat', [seats_count_filter()])  # 2. TARGET: NO recibe filtros de segmento, solo valida que se seleccionaron asientos
]}

# Next Step Rate Seats - DB
SEATS_DB_NSR = {'events': [
    ('seatmap_dom_loaded', [get_DB_filter()]),  # ANCHOR: Filtro DB + filtros globales
    ('extras_dom_loaded', [get_DB_filter()])
]}

# Next Step Rate Seats - Con Asientos Seleccionados
SEATS_WITH_SELECTION_NSR = {'events': [
    ('seatmap_dom_loaded', []),  # ANCHOR: Recibe filtros globales
    ('extras_dom_loaded', [seat_selected_filter()])  # TARGET: Solo filtro técnico
]}

# Next Step Rate Seats - Con Bundle
SEATS_WITH_BUNDLE_NSR = {'events': [
    ('seatmap_dom_loaded', []),  # ANCHOR: Recibe filtros globales
    ('extras_dom_loaded', [bundle_selected_filter()])  # TARGET: Solo filtro técnico
]}

# ===== CONVERSION RATE (CR) - ESTRATEGIA GHOST ANCHOR =====

# Seats CR - General (Estrategia Ghost Anchor con funnel de 3 pasos)
# PROBLEMA RESUELTO: Al filtrar por segmentos (ej: "Travel Group = Familia"), 
# los eventos continue_clicked_seat y revenue_amount devuelven 0 porque NO tienen 
# las propiedades de segmento.
# SOLUCIÓN: Funnel de 3 pasos donde:
# - Paso 1 (seatmap_dom_loaded): ÚNICO que recibe filtros de segmento (Family, Business, etc.)
# - Paso 2 (continue_clicked_seat): NO recibe filtros de segmento, solo valida seats_count > 0
# - Paso 3 (revenue_amount): NO recibe filtros de segmento, solo valida que se pagó por asientos
SEATS_CR = {'events': [
    ('seatmap_dom_loaded', []),  # 1. ANCHOR: Aquí "muerden" los filtros globales del Dashboard (Family, Business, etc.)
    ('continue_clicked_seat', [seats_count_filter()]),  # 2. BRIDGE: NO recibe filtros de segmento, solo valida que se seleccionaron asientos
    ('revenue_amount', [has_seat_purchase_filter()])  # 3. GOAL: NO recibe filtros de segmento, solo valida que se pagó por asientos
]}

# Seats CR - DB (Misma estrategia Ghost Anchor con filtro DB en el ancla)
SEATS_DB_CR = {'events': [
    ('seatmap_dom_loaded', [get_DB_filter()]),  # ANCHOR: Filtro DB + filtros globales
    ('continue_clicked_seat', [seats_count_filter()]),  # BRIDGE: Solo filtro técnico
    ('revenue_amount', [has_seat_purchase_filter()])  # GOAL: Solo filtro técnico
]}

# Seats CR - Con Asientos Seleccionados (Estrategia Ghost Anchor)
SEATS_WITH_SELECTION_CR = {'events': [
    ('seatmap_dom_loaded', []),  # ANCHOR: Recibe filtros globales
    ('continue_clicked_seat', [seats_count_filter()]),  # BRIDGE: Solo filtro técnico
    ('revenue_amount', [has_seat_purchase_filter()])  # GOAL: Solo filtro técnico
]}

# Seats CR - Con Bundle (Estrategia Ghost Anchor)
SEATS_WITH_BUNDLE_CR = {'events': [
    ('seatmap_dom_loaded', []),  # ANCHOR: Recibe filtros globales
    ('continue_clicked_seat', [seats_count_filter()]),  # BRIDGE: Solo filtro técnico
    ('revenue_amount', [has_seat_purchase_filter()])  # GOAL: Solo filtro técnico
]}

# CR Outbound Seat (Estrategia Ghost Anchor)
OUTBOUND_SEAT_CR = {'events': [
    ('outbound_seat_selected', []),  # ANCHOR: Evento de selección
    ('continue_clicked_seat', [seats_count_filter()]),  # BRIDGE: Validar que continuaron con asientos
    ('revenue_amount', [has_seat_purchase_filter()])  # GOAL: Validar compra
]}

# CR Inbound Seat (Estrategia Ghost Anchor)
INBOUND_SEAT_CR = {'events': [
    ('inbound_seat_selected', []),  # ANCHOR: Evento de selección
    ('continue_clicked_seat', [seats_count_filter()]),  # BRIDGE: Validar que continuaron con asientos
    ('revenue_amount', [has_seat_purchase_filter()])  # GOAL: Validar compra
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
