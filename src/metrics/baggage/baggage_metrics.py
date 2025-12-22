# filtros amplitude
from src.utils.amplitude_filters import (
    cabin_bag_filter,
    checked_bag_filter,
    get_DB_filter
)

# ===== NEXT STEP RATE (NSR) =====

# Next Step Rate Baggage - General
BAGGAGE_NSR = {'events': [
    ('baggage_dom_loaded', []),
    ('seatmap_dom_loaded', [])
]}

# Next Step Rate Baggage - DB
BAGGAGE_DB_NSR = {'events': [
    ('baggage_dom_loaded', [get_DB_filter()]),
    ('seatmap_dom_loaded', [get_DB_filter()])
]}

# Next Step Rate Baggage - Vuela Ligero
BAGGAGE_VUELA_LIGERO_NSR = {'events': [
    ('ce:(NEW) baggage_dom_loaded_with_vuela_ligero', []),
    ('seatmap_dom_loaded', [])
]}

# Next Step Rate Baggage - DB (Vuela Ligero)
BAGGAGE_VUELA_LIGERO_DB_NSR = {'events': [
    ('ce:(NEW) baggage_dom_loaded_with_vuela_ligero', [get_DB_filter()]),
    ('seatmap_dom_loaded', [get_DB_filter()])
]}

# ===== WEBSITE CONVERSION RATE (WCR) =====

# Website Conversion Rate from Baggage - General
BAGGAGE_WCR = {'events': [
    ('baggage_dom_loaded', []),
    ('revenue_amount', [])
]}

# Website Conversion Rate from Baggage - Vuela Ligero
BAGGAGE_VUELA_LIGERO_WCR = {'events': [
    ('ce:(NEW) baggage_dom_loaded_with_vuela_ligero', []),
    ('revenue_amount', [])
]}

# ===== ADD TO CART (A2C) =====

# Cabin Bag A2C - General
CABIN_BAG_A2C = {'events': [
    ('ce:(NEW) baggage_dom_loaded_with_vuela_ligero', []),
    ('seatmap_dom_loaded', [cabin_bag_filter()])
]}

# Cabin Bag A2C - DB
CABIN_BAG_DB_A2C = {'events': [
    ('ce:(NEW) baggage_dom_loaded_with_vuela_ligero', [get_DB_filter()]),
    ('seatmap_dom_loaded', [cabin_bag_filter(), get_DB_filter()])
]}

# Checked Bag A2C - General (Vuela Ligero)
CHECKED_BAG_A2C = {'events': [
    ('ce:(NEW) baggage_dom_loaded_with_vuela_ligero', []),
    ('seatmap_dom_loaded', [checked_bag_filter()])
]}

# Checked Bag A2C - DB (Vuela Ligero)
CHECKED_BAG_DB_A2C = {'events': [
    ('ce:(NEW) baggage_dom_loaded_with_vuela_ligero', [get_DB_filter()]),
    ('seatmap_dom_loaded', [checked_bag_filter(), get_DB_filter()])
]}

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
ANCILLARY_MODAL_A2C = {'events': [
    ('baggage_dom_loaded', []),
    ('modal_ancillary_clicked', [])
]}

# ===== CONVERSION RATE (CR) =====

# CR Cabin Bag (El filtro va en el EVENTO FINAL usando propiedades nativas de revenue_amount)
# CORREGIDO: Usa 'during_booking_baggage_count' que es la propiedad real en revenue_amount
# TODO: Verificar si existe una propiedad específica para cabin (ej: 'cabin_bag_count' en revenue)
#       Si existe, actualizar este filtro para mayor precisión
CABIN_BAG_CR = {'events': [
    ('seatmap_dom_loaded', []),
    ('revenue_amount', [{
        'subprop_type': 'event',
        'subprop_key': 'during_booking_baggage_count',
        'subprop_op': 'greater',
        'subprop_value': [0]
    }])
]}

# CR Checked Bag (El filtro va en el EVENTO FINAL usando propiedades nativas de revenue_amount)
# CORREGIDO: Usa 'during_booking_baggage_count' que es la propiedad real en revenue_amount
# (reemplaza la propiedad antigua 'checked_bag' que no existe en el esquema actual)
CHECKED_BAG_CR = {'events': [
    ('seatmap_dom_loaded', []),
    ('revenue_amount', [{
        'subprop_type': 'event',
        'subprop_key': 'during_booking_baggage_count',
        'subprop_op': 'greater',
        'subprop_value': [0]
    }])
]}

# CR Ancillary Modal
ANCILLARY_MODAL_CR = {'events': [
    ('modal_ancillary_clicked', []),
    ('revenue_amount', [])
]}
