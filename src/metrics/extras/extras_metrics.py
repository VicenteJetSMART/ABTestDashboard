# filtros amplitude
from src.utils.amplitude_filters import (
    get_DB_filter
)

# Next Step Rate Extras - General
NSR_EXTRAS = {'events': [
    ('extras_dom_loaded', []),
    ('passengers_dom_loaded', [])
]}

# Next Step Rate Extras - DB
NSR_EXTRAS_DB = {'events': [
    ('extras_dom_loaded', [get_DB_filter()]),
    ('passengers_dom_loaded', [get_DB_filter()])
]}

# Website Conversion Rate from Extras - General
WCR_EXTRAS = {'events': [
    ('extras_dom_loaded', []),
    ('payment_confirmation_loaded', [])
]}

# Website Conversion Rate from Extras - DB
WCR_EXTRAS_DB = {'events': [
    ('extras_dom_loaded', [get_DB_filter()]),
    ('revenue_amount', [get_DB_filter()])
]}

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

# ===== ADD TO CART (A2C) - Extras =====

# Add to Cart Extras General
ADD_TO_CART_EXTRAS_GENERAL = {'events': [
    ('extras_dom_loaded', []),
    ('extra_selected', [])
]}

# Add to Cart Flexi (El filtro va en el SEGUNDO evento)
ADD_TO_CART_FLEXI = {'events': [
    ('extras_dom_loaded', []),
    ('extra_selected', [{
        'subprop_type': 'event',
        'subprop_key': 'type',
        'subprop_op': 'is',
        'subprop_value': ['flexiFee']
    }])
]}

# Add to Cart Airport Checkin (El filtro va en el SEGUNDO evento)
ADD_TO_CART_AIRPORT_CHECKIN = {'events': [
    ('extras_dom_loaded', []),
    ('extra_selected', [{
        'subprop_type': 'event',
        'subprop_key': 'type',
        'subprop_op': 'is',
        'subprop_value': ['airportCheckin']
    }])
]}

# Add to Cart Priority Boarding (El filtro va en el SEGUNDO evento)
ADD_TO_CART_PRIORITY_BOARDING = {'events': [
    ('extras_dom_loaded', []),
    ('extra_selected', [{
        'subprop_type': 'event',
        'subprop_key': 'type',
        'subprop_op': 'is',
        'subprop_value': ['priorityBoarding']
    }])
]}

# Add to Cart Pet (El filtro va en el SEGUNDO evento)
ADD_TO_CART_PET = {'events': [
    ('extras_dom_loaded', []),
    ('extra_selected', [{
        'subprop_type': 'event',
        'subprop_key': 'type',
        'subprop_op': 'is',
        'subprop_value': ['pet']
    }])
]}

# Add to Cart Insurance (El filtro va en el SEGUNDO evento)
ADD_TO_CART_INSURANCE = {'events': [
    ('extras_dom_loaded', []),
    ('extra_selected', [{
        'subprop_type': 'event',
        'subprop_key': 'type',
        'subprop_op': 'is',
        'subprop_value': ['insurance']
    }])
]}

# ===== CONVERSION RATE (CR) - Extras =====

# CR Extras General
CR_EXTRAS_GENERAL = {'events': [
    ('extra_selected', []),
    ('payment_confirmation_loaded', [])
]}

# CR Flexi (El filtro va en el PRIMER evento)
CR_FLEXI = {'events': [
    ('extra_selected', [{
        'subprop_type': 'event',
        'subprop_key': 'type',
        'subprop_op': 'is',
        'subprop_value': ['flexiFee']
    }]),
    ('payment_confirmation_loaded', [])
]}

# CR Airport Checkin (El filtro va en el PRIMER evento)
CR_AIRPORT_CHECKIN = {'events': [
    ('extra_selected', [{
        'subprop_type': 'event',
        'subprop_key': 'type',
        'subprop_op': 'is',
        'subprop_value': ['airportCheckin']
    }]),
    ('payment_confirmation_loaded', [])
]}

# CR Priority Boarding (El filtro va en el PRIMER evento)
CR_PRIORITY_BOARDING = {'events': [
    ('extra_selected', [{
        'subprop_type': 'event',
        'subprop_key': 'type',
        'subprop_op': 'is',
        'subprop_value': ['priorityBoarding']
    }]),
    ('payment_confirmation_loaded', [])
]}

# CR Pet (El filtro va en el PRIMER evento)
CR_PET = {'events': [
    ('extra_selected', [{
        'subprop_type': 'event',
        'subprop_key': 'type',
        'subprop_op': 'is',
        'subprop_value': ['pet']
    }]),
    ('payment_confirmation_loaded', [])
]}

# CR Insurance (El filtro va en el PRIMER evento)
CR_INSURANCE = {'events': [
    ('extra_selected', [{
        'subprop_type': 'event',
        'subprop_key': 'type',
        'subprop_op': 'is',
        'subprop_value': ['insurance']
    }]),
    ('payment_confirmation_loaded', [])
]}

