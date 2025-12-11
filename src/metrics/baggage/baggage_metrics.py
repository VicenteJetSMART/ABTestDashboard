# filtros amplitude
from src.utils.amplitude_filters import (
    cabin_bag_filter,
    checked_bag_filter,
    get_DB_filter
)

# Next Step Rate Baggage - General
NSR_BAGGAGE = {'events': [
    ('baggage_dom_loaded', []),
    ('seatmap_dom_loaded', [])
]}


# Next Step Rate Baggage - General (Vuela Ligero)
NSR_BAGGAGE_VUELA_LIGERO = {'events': [
    ('ce:(NEW) baggage_dom_loaded_with_vuela_ligero', []),
    ('seatmap_dom_loaded', [])
]}


# Next Step Rate Baggage - DB (Vuela Ligero)
NSR_BAGGAGE_VUELA_LIGERO_DB = {'events': [
    ('ce:(NEW) baggage_dom_loaded_with_vuela_ligero', [get_DB_filter()]),
    ('seatmap_dom_loaded', [get_DB_filter()])
]}


# Next Step Rate Baggage - DB
NSR_BAGGAGE_DB = {'events': [
    ('baggage_dom_loaded', [get_DB_filter()]),
    ('seatmap_dom_loaded', [get_DB_filter()])
]}

# Website Conversion Rate from Baggage - General
WCR_BAGGAGE = {'events': [
    ('baggage_dom_loaded', []),
    ('payment_confirmation_loaded', [])
]}

# Website Conversion Rate from Baggage - Vuela Ligero
# Ojo los Custom Events parten con 'ce:'
WCR_BAGGAGE_VUELA_LIGERO = {'events': [
    ('ce:(NEW) baggage_dom_loaded_with_vuela_ligero', []),
    ('payment_confirmation_loaded', [])
]}

# Cabin Bag A2C - General
CABIN_BAG_A2C = {'events': [
    ('ce:(NEW) baggage_dom_loaded_with_vuela_ligero', []),  # Sin filtros
    ('seatmap_dom_loaded', [cabin_bag_filter()])  # Con filtro
]}

# Cabin Bag A2C - DB
CABIN_BAG_A2C_DB = {'events': [
    ('ce:(NEW) baggage_dom_loaded_with_vuela_ligero', [get_DB_filter()]),  # Sin filtros
    ('seatmap_dom_loaded', [cabin_bag_filter(), get_DB_filter()])  # Con filtro
]}

# Checked Bag A2C - General (Vuela Ligero)
CHECKED_BAG_A2C = {'events': [
    ('ce:(NEW) baggage_dom_loaded_with_vuela_ligero', []),
    ('seatmap_dom_loaded', [checked_bag_filter()])
]}

# Checked Bag A2C - DB (Vuela Ligero)
CHECKED_BAG_A2C_DB = {'events': [
    ('ce:(NEW) baggage_dom_loaded_with_vuela_ligero', [get_DB_filter()]),
    ('seatmap_dom_loaded', [checked_bag_filter(), get_DB_filter()])
]}

# ===== ADD TO CART (A2C) - Baggage (Nuevas Métricas) =====

# Add to Cart Cabin Bag (El filtro va en el SEGUNDO evento)
ADD_TO_CART_CABIN_BAG = {'events': [
    ('baggage_dom_loaded', []),
    ('seatmap_dom_loaded', [{
        'subprop_type': 'event',
        'subprop_key': 'cabin_bag_count',
        'subprop_op': 'is not',
        'subprop_value': [0]
    }])
]}

# Add to Cart Checked Bag (El filtro va en el SEGUNDO evento)
ADD_TO_CART_CHECKED_BAG = {'events': [
    ('baggage_dom_loaded', []),
    ('seatmap_dom_loaded', [{
        'subprop_type': 'event',
        'subprop_key': 'checked_bag_count',
        'subprop_op': 'is not',
        'subprop_value': [0]
    }])
]}

# Add to Cart Ancillary Modal
ADD_TO_CART_ANCILLARY_MODAL = {'events': [
    ('baggage_dom_loaded', []),
    ('modal_ancillary_clicked', [])
]}

# ===== CONVERSION RATE (CR) - Baggage =====

# CR Cabin Bag (El filtro va en el EVENTO FINAL usando propiedades nativas de payment_confirmation_loaded)
# NOTA: La propiedad se llama 'cabing_bag' (con 'g' extra) según el esquema real de Amplitude
CR_CABIN_BAG = {'events': [
    ('seatmap_dom_loaded', []),
    ('payment_confirmation_loaded', [{
        'subprop_type': 'event',
        'subprop_key': 'cabing_bag',
        'subprop_op': 'greater',
        'subprop_value': [0]
    }])
]}

# CR Checked Bag (El filtro va en el EVENTO FINAL usando propiedades nativas de payment_confirmation_loaded)
CR_CHECKED_BAG = {'events': [
    ('seatmap_dom_loaded', []),
    ('payment_confirmation_loaded', [{
        'subprop_type': 'event',
        'subprop_key': 'checked_bag',
        'subprop_op': 'greater',
        'subprop_value': [0]
    }])
]}

# CR Ancillary Modal
CR_ANCILLARY_MODAL = {'events': [
    ('modal_ancillary_clicked', []),
    ('payment_confirmation_loaded', [])
]}