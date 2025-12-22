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

def has_purchased_general_extra_filter():
    """
    Filtro técnico para validar que se compró alguno de los Extras Generales en revenue_amount.
    
    Lógica OR: El usuario compró si la suma de cualquiera de estas propiedades es > 0:
    - flexi_smart_count
    - pet_in_cabin_count
    - priority_boarding_count
    
    NOTA TÉCNICA: Amplitude no soporta sumar propiedades directamente ni OR entre diferentes propiedades.
    Esta implementación retorna múltiples filtros que Amplitude interpretará como AND por defecto.
    
    ALTERNATIVA: Si Amplitude no soporta OR entre propiedades diferentes, considerar:
    1. Usar una propiedad calculada en Amplitude que sume estos valores
    2. Crear múltiples métricas separadas y combinarlas en el análisis
    3. Usar la API de Amplitude con una estructura de filtro más compleja
    
    Por ahora, retornamos los 3 filtros y esperamos que el procesamiento posterior
    maneje la lógica OR correctamente, o que exista una propiedad calculada.
    """
    # Retornamos múltiples filtros - la lógica OR debe manejarse en el procesamiento
    # o mediante una propiedad calculada en Amplitude
    return [
        {
            'subprop_type': 'event',
            'subprop_key': 'flexi_smart_count',
            'subprop_op': 'greater',
            'subprop_value': [0]
        },
        {
            'subprop_type': 'event',
            'subprop_key': 'pet_in_cabin_count',
            'subprop_op': 'greater',
            'subprop_value': [0]
        },
        {
            'subprop_type': 'event',
            'subprop_key': 'priority_boarding_count',
            'subprop_op': 'greater',
            'subprop_value': [0]
        }
    ]

# CR Extras General (excluye airportCheckin)
# CORREGIDO: Usa extras_dom_loaded como anchor para igualar el denominador con EXTRAS_GENERAL_A2C
# Estrategia "Ghost Anchor": Filtros globales solo en el evento 1 (extras_dom_loaded)
EXTRAS_GENERAL_CR = {'events': [
    ('extras_dom_loaded', []),  # 1. ANCHOR: Recibe filtros globales, iguala el denominador del A2C
    ('revenue_amount', has_purchased_general_extra_filter())  # 2. GOAL: Filtro técnico OR
]}

# CR Flexi (El filtro va en el PRIMER evento)
FLEXI_CR = {'events': [
    ('extra_selected', [{
        'subprop_type': 'event',
        'subprop_key': 'type',
        'subprop_op': 'is',
        'subprop_value': ['flexiFee']
    }]),
    ('revenue_amount', [])
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

# CR Priority Boarding (El filtro va en el PRIMER evento)
PRIORITY_BOARDING_CR = {'events': [
    ('extra_selected', [{
        'subprop_type': 'event',
        'subprop_key': 'type',
        'subprop_op': 'is',
        'subprop_value': ['priorityBoarding']
    }]),
    ('revenue_amount', [])
]}

# CR Pet (El filtro va en el PRIMER evento)
PET_CR = {'events': [
    ('extra_selected', [{
        'subprop_type': 'event',
        'subprop_key': 'type',
        'subprop_op': 'is',
        'subprop_value': ['pet']
    }]),
    ('revenue_amount', [])
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
