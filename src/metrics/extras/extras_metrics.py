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

# CR Extras General (excluye airportCheckin)
EXTRAS_GENERAL_CR = {'events': [
    ('extra_selected', [{
        'subprop_type': 'event',
        'subprop_key': 'type',
        'subprop_op': 'is not',
        'subprop_value': ['airportCheckin']
    }]),
    ('revenue_amount', [])
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
