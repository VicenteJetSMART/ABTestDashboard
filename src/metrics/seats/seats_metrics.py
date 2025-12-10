# filtros amplitude
from src.utils.amplitude_filters import (
    get_DB_filter,
    seat_selected_filter,
    bundle_selected_filter
)

# ===== NEXT STEP RATE (NSR) =====

# Next Step Rate Seats - General
NSR_SEATS = {'events': [
    ('seatmap_dom_loaded', []),
    ('extras_dom_loaded', [])
]}

# Next Step Rate Seats - DB
NSR_SEATS_DB = {'events': [
    ('seatmap_dom_loaded', [get_DB_filter()]),
    ('extras_dom_loaded', [get_DB_filter()])
]}

# Next Step Rate Seats - Con Asientos Seleccionados
NSR_SEATS_WITH_SELECTION = {'events': [
    ('seatmap_dom_loaded', []),
    ('extras_dom_loaded', [seat_selected_filter()])
]}

# Next Step Rate Seats - Con Bundle
NSR_SEATS_WITH_BUNDLE = {'events': [
    ('seatmap_dom_loaded', []),
    ('extras_dom_loaded', [bundle_selected_filter()])
]}

# ===== WEBSITE CONVERSION RATE (WCR) =====

# WCR Seats - General (Website Conversion Rate desde seatmap hasta revenue)
WCR_SEATS = {'events': [
    ('seatmap_dom_loaded', []),
    ('revenue_amount', [])
]}

# ===== CONVERSION RATE (CR) =====

# Seats CR - General (Conversion Rate desde seatmap hasta revenue)
SEATS_CR = {'events': [
    ('seatmap_dom_loaded', []),
    ('revenue_amount', [])
]}

# Seats CR - DB
SEATS_CR_DB = {'events': [
    ('seatmap_dom_loaded', [get_DB_filter()]),
    ('revenue_amount', [get_DB_filter()])
]}

# Seats CR - Con Asientos Seleccionados
SEATS_CR_WITH_SELECTION = {'events': [
    ('seatmap_dom_loaded', []),
    ('revenue_amount', [seat_selected_filter()])
]}

# Seats CR - Con Bundle
SEATS_CR_WITH_BUNDLE = {'events': [
    ('seatmap_dom_loaded', []),
    ('revenue_amount', [bundle_selected_filter()])
]}

# ===== ADD TO CART (A2C) =====

# Seats A2C - General (Selección de asientos)
SEATS_A2C = {'events': [
    ('seatmap_dom_loaded', []),
    ('continue_clicked_seat', [seat_selected_filter()])
]}

# Seats A2C - DB
SEATS_A2C_DB = {'events': [
    ('seatmap_dom_loaded', [get_DB_filter()]),
    ('continue_clicked_seat', [seat_selected_filter(), get_DB_filter()])
]}

# Seats A2C - Outbound (Selección de asiento de ida)
SEATS_A2C_OUTBOUND = {'events': [
    ('seatmap_dom_loaded', []),
    ('outbound_seat_selected', [])
]}

# Seats A2C - Inbound (Selección de asiento de regreso)
SEATS_A2C_INBOUND = {'events': [
    ('outbound_seat_selected', []),
    ('inbound_seat_selected', [])
]}



# Seat Selection Rate (cualquier asiento)
SEAT_SELECTION_RATE = {'events': [
    ('seatmap_dom_loaded', []),
    ('seatmap_dom_loaded', [seat_selected_filter()])
]}

# ===== ADD TO CART (A2C) - Seats (Nuevas Métricas) =====

# Add to Cart Outbound Seat
ADD_TO_CART_OUTBOUND_SEAT = {'events': [
    ('seatmap_dom_loaded', []),
    ('outbound_seat_selected', [])
]}

# Add to Cart Inbound Seat
ADD_TO_CART_INBOUND_SEAT = {'events': [
    ('seatmap_dom_loaded', []),
    ('inbound_seat_selected', [])
]}

# ===== CONVERSION RATE (CR) - Seats (Nuevas Métricas) =====

# CR Outbound Seat
CR_OUTBOUND_SEAT = {'events': [
    ('outbound_seat_selected', []),
    ('revenue_amount', [])
]}

# CR Inbound Seat
CR_INBOUND_SEAT = {'events': [
    ('inbound_seat_selected', []),
    ('revenue_amount', [])
]}

