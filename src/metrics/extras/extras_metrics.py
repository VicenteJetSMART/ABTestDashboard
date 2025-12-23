# filtros amplitude
from src.utils.amplitude_filters import (
    get_DB_filter
)

# ===== NEXT STEP RATE (NSR) =====

# Next Step Rate Extras - General
EXTRAS_NSR = {'events': [
    ('extras_dom_loaded', []),
    ('passengers_dom_loaded', [])
]}

# Next Step Rate Extras - DB
EXTRAS_DB_NSR = {'events': [
    ('extras_dom_loaded', [get_DB_filter()]),
    ('passengers_dom_loaded', [get_DB_filter()])
]}

# ===== WEBSITE CONVERSION RATE (WCR) =====

# Website Conversion Rate from Extras - General
EXTRAS_WCR = {'events': [
    ('extras_dom_loaded', []),
    ('revenue_amount', [])
]}

# Website Conversion Rate from Extras - DB
EXTRAS_DB_WCR = {'events': [
    ('extras_dom_loaded', [get_DB_filter()]),
    ('revenue_amount', [get_DB_filter()])
]}

# ===== SELECTION RATE =====

# Extra Selection Rate
EXTRA_SELECTION_RATE = {'events': [
    ('extras_dom_loaded', []),
    ('extra_selected', [])
]}

# Continue Clicked Extras Rate
EXTRAS_CONTINUE_RATE = {'events': [
    ('extras_dom_loaded', []),
    ('continue_clicked_extras', [])
]}

# Modal Ancillary Interaction Rate
MODAL_ANCILLARY_RATE = {'events': [
    ('extras_dom_loaded', []),
    ('modal_ancillary_clicked', [])
]}

# ===== ADD TO CART (A2C) =====

# Add to Cart Extras General (excluye airportCheckin)
EXTRAS_GENERAL_A2C = {'events': [
    ('extras_dom_loaded', []),
    ('extra_selected', [{
        'subprop_type': 'event',
        'subprop_key': 'type',
        'subprop_op': 'is not',
        'subprop_value': ['airportCheckin']
    }])
]}

# Add to Cart Flexi (El filtro va en el SEGUNDO evento)
FLEXI_A2C = {'events': [
    ('extras_dom_loaded', []),
    ('extra_selected', [{
        'subprop_type': 'event',
        'subprop_key': 'type',
        'subprop_op': 'is',
        'subprop_value': ['flexiFee']
    }])
]}

# Add to Cart Airport Checkin (El filtro va en el SEGUNDO evento)
AIRPORT_CHECKIN_A2C = {'events': [
    ('extras_dom_loaded', []),
    ('extra_selected', [{
        'subprop_type': 'event',
        'subprop_key': 'type',
        'subprop_op': 'is',
        'subprop_value': ['airportCheckin']
    }])
]}

# Add to Cart Priority Boarding (El filtro va en el SEGUNDO evento)
PRIORITY_BOARDING_A2C = {'events': [
    ('extras_dom_loaded', []),
    ('extra_selected', [{
        'subprop_type': 'event',
        'subprop_key': 'type',
        'subprop_op': 'is',
        'subprop_value': ['priorityBoarding']
    }])
]}

# Add to Cart Pet (El filtro va en el SEGUNDO evento)
PET_A2C = {'events': [
    ('extras_dom_loaded', []),
    ('extra_selected', [{
        'subprop_type': 'event',
        'subprop_key': 'type',
        'subprop_op': 'is',
        'subprop_value': ['pet']
    }])
]}

# Add to Cart Insurance (El filtro va en el SEGUNDO evento)
INSURANCE_A2C = {'events': [
    ('extras_dom_loaded', []),
    ('extra_selected', [{
        'subprop_type': 'event',
        'subprop_key': 'type',
        'subprop_op': 'is',
        'subprop_value': ['insurance']
    }])
]}

# ===== CONVERSION RATE (CR) =====

# Helper functions para filtros de revenue_amount (usando propiedades de revenue)
def has_purchased_flexi_filter():
    """
    Retorna un filtro de Amplitude para validar compra de Flexi en revenue_amount.
    Usa la propiedad flexi_smart_count > 0.
    """
    return {
        'subprop_type': 'event',
        'subprop_key': 'flexi_smart_count',
        'subprop_op': 'greater',
        'subprop_value': [0]
    }

def has_purchased_pet_filter():
    """
    Retorna un filtro de Amplitude para validar compra de Pet en revenue_amount.
    Usa la propiedad pet_in_cabin_count > 0.
    """
    return {
        'subprop_type': 'event',
        'subprop_key': 'pet_in_cabin_count',
        'subprop_op': 'greater',
        'subprop_value': [0]
    }

def has_purchased_priority_filter():
    """
    Retorna un filtro de Amplitude para validar compra de Priority Boarding en revenue_amount.
    Usa la propiedad priority_boarding_count > 0.
    """
    return {
        'subprop_type': 'event',
        'subprop_key': 'priority_boarding_count',
        'subprop_op': 'greater',
        'subprop_value': [0]
    }

# CR Extras General (excluye airportCheckin)
# ARQUITECTURA DE 3 PASOS: Filtramos la intención en el paso intermedio
# 1. ANCHOR: Define el denominador correcto (Sesiones en la página de extras)
# 2. INTENTION: Filtra qué tipo de extra queremos medir (excluye airportCheckin)
# 3. GOAL: Confirmación de pago (si pasó por el paso 2 y pagó, asumimos que pagó lo que seleccionó)
EXTRAS_GENERAL_CR = {'events': [
    ('extras_dom_loaded', []),  # 1. ANCHOR: Recibe filtros globales, iguala el denominador del A2C
    ('extra_selected', [{  # 2. INTENTION: Filtro OR simple - excluye airportCheckin
        'subprop_type': 'event',
        'subprop_key': 'type',  # Propiedad que contiene el tipo de extra
        'subprop_op': 'is not',  # "Todo lo que NO sea Checkin" = Extras Generales
        'subprop_value': ['airportCheckin']
    }]),
    ('revenue_amount', [])  # 3. GOAL: Confirmación de pago (sin filtros adicionales)
]}

# CR Flexi
# CORREGIDO: Usa extras_dom_loaded como anchor para igualar el denominador con FLEXI_A2C
# Estrategia "Ghost Anchor": Filtros globales solo en el evento 1 (extras_dom_loaded)
FLEXI_CR = {'events': [
    ('extras_dom_loaded', []),  # 1. ANCHOR: Recibe filtros globales, iguala el denominador del A2C
    ('revenue_amount', [has_purchased_flexi_filter()])  # 2. GOAL: Filtro técnico en revenue_amount
]}

# CR Airport Checkin (El filtro va en el PRIMER evento)
AIRPORT_CHECKIN_CR = {'events': [
    ('extra_selected', [{
        'subprop_type': 'event',
        'subprop_key': 'type',
        'subprop_op': 'is',
        'subprop_value': ['airportCheckin']
    }]),
    ('revenue_amount', [])
]}

# CR Priority Boarding
# CORREGIDO: Usa extras_dom_loaded como anchor para igualar el denominador con PRIORITY_BOARDING_A2C
# Estrategia "Ghost Anchor": Filtros globales solo en el evento 1 (extras_dom_loaded)
PRIORITY_BOARDING_CR = {'events': [
    ('extras_dom_loaded', []),  # 1. ANCHOR: Recibe filtros globales, iguala el denominador del A2C
    ('revenue_amount', [has_purchased_priority_filter()])  # 2. GOAL: Filtro técnico en revenue_amount
]}

# CR Pet
# CORREGIDO: Usa extras_dom_loaded como anchor para igualar el denominador con PET_A2C
# Estrategia "Ghost Anchor": Filtros globales solo en el evento 1 (extras_dom_loaded)
PET_CR = {'events': [
    ('extras_dom_loaded', []),  # 1. ANCHOR: Recibe filtros globales, iguala el denominador del A2C
    ('revenue_amount', [has_purchased_pet_filter()])  # 2. GOAL: Filtro técnico en revenue_amount
]}

# CR Insurance (El filtro va en el PRIMER evento)
INSURANCE_CR = {'events': [
    ('extra_selected', [{
        'subprop_type': 'event',
        'subprop_key': 'type',
        'subprop_op': 'is',
        'subprop_value': ['insurance']
    }]),
    ('revenue_amount', [])
]}
