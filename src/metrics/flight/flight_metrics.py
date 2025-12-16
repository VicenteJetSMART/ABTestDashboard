# filtros amplitude
from src.utils.amplitude_filters import (
    get_DB_filter
)

# ===== NEXT STEP RATE (NSR) =====

# Next Step Rate Flight - General
FLIGHT_NSR = {'events': [
    ('flight_dom_loaded_flight', []),
    ('baggage_dom_loaded', [])
]}

# Next Step Rate Flight - DB
FLIGHT_DB_NSR = {'events': [
    ('flight_dom_loaded_flight', [get_DB_filter()]),
    ('baggage_dom_loaded', [get_DB_filter()])
]}

# ===== WEBSITE CONVERSION RATE (WCR) =====

# Website Conversion Rate from Flight - General
FLIGHT_WCR = {'events': [
    ('flight_dom_loaded_flight', []),
    ('revenue_amount', [])
]}

# Website Conversion Rate from Flight - DB
FLIGHT_DB_WCR = {'events': [
    ('flight_dom_loaded_flight', [get_DB_filter()]),
    ('revenue_amount', [get_DB_filter()])
]}

# ===== SELECTION RATE =====

# Outbound Flight Selection Rate
OUTBOUND_FLIGHT_SELECTION = {'events': [
    ('flight_dom_loaded_flight', []),
    ('outbound_flight_selected_flight', [])
]}

# Inbound Flight Selection Rate
INBOUND_FLIGHT_SELECTION = {'events': [
    ('outbound_flight_selected_flight', []),
    ('inbound_flight_selected_flight', [])
]}

# Complete Flight Selection Rate (Outbound + Inbound)
COMPLETE_FLIGHT_SELECTION = {'events': [
    ('flight_dom_loaded_flight', []),
    ('inbound_flight_selected_flight', [])
]}

# Flight to Continue Click Rate
FLIGHT_CONTINUE_RATE = {'events': [
    ('inbound_flight_selected_flight', []),
    ('continue_clicked_flight', [])
]}

# ===== ADD TO CART (A2C) =====

# Add to Cart Outbound Flight
OUTBOUND_FLIGHT_A2C = {'events': [
    ('flight_dom_loaded_flight', []),
    ('outbound_flight_selected_flight', [])
]}

# Add to Cart Inbound Flight
INBOUND_FLIGHT_A2C = {'events': [
    ('flight_dom_loaded_flight', []),
    ('inbound_flight_selected_flight', [])
]}

# Add to Cart Discount Club
DISCOUNT_CLUB_A2C = {'events': [
    ('flight_dom_loaded_flight', []),
    ('dc_modal_dom_loaded', [])
]}

# ===== CONVERSION RATE (CR) =====

# CR Outbound Flight
OUTBOUND_FLIGHT_CR = {'events': [
    ('outbound_flight_selected_flight', []),
    ('revenue_amount', [])
]}

# CR Inbound Flight
INBOUND_FLIGHT_CR = {'events': [
    ('inbound_flight_selected_flight', []),
    ('revenue_amount', [])
]}

# CR Discount Club
DISCOUNT_CLUB_CR = {'events': [
    ('dc_modal_dom_loaded', []),
    ('revenue_amount', [])
]}
