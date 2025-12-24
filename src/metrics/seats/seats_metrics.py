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
# NOTA: Comentado - Ya no se usa en SEATS_CR (eliminamos validación redundante del paso 3)
# Se mantiene por referencia histórica y para otras métricas que puedan necesitarlo
# REVENUE_SEAT_TYPES = [
#     'seat_estandar_count',
#     'seat_primera_fila_count',
#     'seat_salida_emergencia_count',
#     'seat_salida_rapida_count',
#     'seat_smart_count',
#     'seats'  # Propiedad genérica de asientos en revenue
# ]


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
    
    NOTA: Este filtro ya NO se usa en SEATS_CR (eliminado para resolver bug de "0 ventas").
    Se mantiene porque otras métricas CR (SEATS_DB_CR, SEATS_WITH_SELECTION_CR, etc.) aún lo usan.
    Si esas métricas también presentan el mismo bug, considerar aplicar la misma solución.
    """
    # Usamos la propiedad 'seats' que representa el total de asientos vendidos en revenue
    return {
        'subprop_type': 'event',
        'subprop_key': 'seats',
        'subprop_op': 'greater',
        'subprop_value': [0]
    }


# Filtros para validar compra de tipos específicos de asientos en revenue_amount
def has_estandar_seat_filter():
    """Filtro para validar que se compró al menos un asiento estándar"""
    return {
        'subprop_type': 'event',
        'subprop_key': 'seat_estandar_count',
        'subprop_op': 'greater',
        'subprop_value': [0]
    }

def has_primera_fila_seat_filter():
    """Filtro para validar que se compró al menos un asiento de primera fila"""
    return {
        'subprop_type': 'event',
        'subprop_key': 'seat_primera_fila_count',
        'subprop_op': 'greater',
        'subprop_value': [0]
    }

def has_salida_emergencia_seat_filter():
    """Filtro para validar que se compró al menos un asiento de salida de emergencia"""
    return {
        'subprop_type': 'event',
        'subprop_key': 'seat_salida_emergencia_count',
        'subprop_op': 'greater',
        'subprop_value': [0]
    }

def has_salida_rapida_seat_filter():
    """Filtro para validar que se compró al menos un asiento de salida rápida"""
    return {
        'subprop_type': 'event',
        'subprop_key': 'seat_salida_rapida_count',
        'subprop_op': 'greater',
        'subprop_value': [0]
    }

def has_smart_seat_filter():
    """Filtro para validar que se compró al menos un asiento smart"""
    return {
        'subprop_type': 'event',
        'subprop_key': 'seat_smart_count',
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
# - Paso 2 (continue_clicked_seat): NO recibe filtros de segmento ni filtros técnicos (sin filtro)
SEATS_NSR = {'events': [
    ('seatmap_dom_loaded', []),  # 1. ANCHOR: Aquí "muerden" los filtros globales del Dashboard (Family, Business, etc.)
    ('continue_clicked_seat', [])  # 2. TARGET: NO recibe filtros de segmento ni filtros técnicos
]}


# ===== CONVERSION RATE (CR) - ESTRATEGIA GHOST ANCHOR =====

# Seats CR - General (Estrategia Ghost Anchor con funnel de 3 pasos)
# PROBLEMA RESUELTO: Al filtrar por segmentos (ej: "Travel Group = Familia"), 
# los eventos continue_clicked_seat y payment_confirmation_loaded devuelven 0 porque NO tienen 
# las propiedades de segmento.
# SOLUCIÓN: Funnel de 3 pasos donde:
# - Paso 1 (seatmap_dom_loaded): ÚNICO que recibe filtros de segmento (Family, Business, etc.)
# - Paso 2 (continue_clicked_seat): NO recibe filtros de segmento, solo valida seats_count > 0
# - Paso 3 (payment_confirmation_loaded): Confirma que llegó a la página de confirmación de pago (sin filtro adicional)
SEATS_CR = {'events': [
    ('seatmap_dom_loaded', []),  # 1. ANCHOR: Aquí "muerden" los filtros globales del Dashboard (Family, Business, etc.)
    ('payment_confirmation_loaded', [has_seat_purchase_filter()])  # 3. GOAL: Confirma que llegó a la página de confirmación de pago
]}

# Seats CR por tipo de asiento - Estrategia Ghost Anchor con funnel de 2 pasos
# Cada métrica valida que se compró al menos un asiento del tipo específico en revenue_amount
# - Paso 1 (seatmap_dom_loaded): ÚNICO que recibe filtros de segmento (Family, Business, etc.)
# - Paso 2 (revenue_amount): Valida que se compró al menos un asiento del tipo específico

# Seats CR - Estándar
SEATS_ESTANDAR_CR = {'events': [
    ('seatmap_dom_loaded', []),  # 1. ANCHOR: Recibe filtros globales
    ('revenue_amount', [has_estandar_seat_filter()])  # 2. GOAL: Valida seat_estandar_count > 0
]}

# Seats CR - Primera Fila
SEATS_PRIMERA_FILA_CR = {'events': [
    ('seatmap_dom_loaded', []),  # 1. ANCHOR: Recibe filtros globales
    ('revenue_amount', [has_primera_fila_seat_filter()])  # 2. GOAL: Valida seat_primera_fila_count > 0
]}

# Seats CR - Salida de Emergencia
SEATS_SALIDA_EMERGENCIA_CR = {'events': [
    ('seatmap_dom_loaded', []),  # 1. ANCHOR: Recibe filtros globales
    ('revenue_amount', [has_salida_emergencia_seat_filter()])  # 2. GOAL: Valida seat_salida_emergencia_count > 0
]}

# Seats CR - Salida Rápida
SEATS_SALIDA_RAPIDA_CR = {'events': [
    ('seatmap_dom_loaded', []),  # 1. ANCHOR: Recibe filtros globales
    ('revenue_amount', [has_salida_rapida_seat_filter()])  # 2. GOAL: Valida seat_salida_rapida_count > 0
]}

# Seats CR - Smart
SEATS_SMART_CR = {'events': [
    ('seatmap_dom_loaded', []),  # 1. ANCHOR: Recibe filtros globales
    ('revenue_amount', [has_smart_seat_filter()])  # 2. GOAL: Valida seat_smart_count > 0
]}


# ===== ADD TO CART (A2C) - ESTRATEGIA GHOST ANCHOR =====

# Seats A2C - General (Estrategia Ghost Anchor)
# PROBLEMA RESUELTO: Al filtrar por segmentos (ej: "Travel Group = Familia"), 
# el evento continue_clicked_seat devuelve 0 porque NO tiene la propiedad de segmento.
# SOLUCIÓN: Funnel de 2 pasos donde:
# - Paso 1 (seatmap_dom_loaded): ÚNICO que recibe filtros de segmento (Family, Business, etc.)
# - Paso 2 (continue_clicked_seat): NO recibe filtros de segmento, solo valida que se seleccionaron asientos
SEATS_A2C = {'events': [
    ('seatmap_dom_loaded', []),  # 1. ANCHOR: Aquí "muerden" los filtros globales del Dashboard (Family, Business, etc.)
    ('continue_clicked_seat', [seats_count_filter()])  # 2. TARGET: NO recibe filtros de segmento, solo valida que se seleccionaron asientos
]}

