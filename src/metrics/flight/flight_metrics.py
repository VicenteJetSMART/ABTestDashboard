# filtros amplitude
from src.utils.amplitude_filters import (
    get_DB_filter
)

# Next Step Rate Flight - General
NSR_FLIGHT = {'events': [
    ('flight_dom_loaded_flight', []),
    ('baggage_dom_loaded', [])
]}

# Next Step Rate Flight - DB
NSR_FLIGHT_DB = {'events': [
    ('flight_dom_loaded_flight', [get_DB_filter()]),
    ('baggage_dom_loaded', [get_DB_filter()])
]}

# Website Conversion Rate from Flight - General
WCR_FLIGHT = {'events': [
    ('flight_dom_loaded_flight', []),
    ('revenue_amount', [])
]}

# Website Conversion Rate from Flight - DB
WCR_FLIGHT_DB = {'events': [
    ('flight_dom_loaded_flight', [get_DB_filter()]),
    ('revenue_amount', [get_DB_filter()])
]}

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

# ===== ADD TO CART (A2C) - Flights =====

# Add to Cart Outbound Flight
ADD_TO_CART_OUTBOUND_FLIGHT = {'events': [
    ('flight_dom_loaded_flight', []),
    ('outbound_flight_selected_flight', [])
]}

# Add to Cart Inbound Flight
ADD_TO_CART_INBOUND_FLIGHT = {'events': [
    ('flight_dom_loaded_flight', []),
    ('inbound_flight_selected_flight', [])
]}

# Add to Cart Discount Club
ADD_TO_CART_DISCOUNT_CLUB = {'events': [
    ('flight_dom_loaded_flight', []),
    ('dc_modal_dom_loaded', [])
]}

# ===== CONVERSION RATE (CR) - Flights =====

# CR Outbound Flight
CR_OUTBOUND_FLIGHT = {'events': [
    ('outbound_flight_selected_flight', []),
    ('revenue_amount', [])
]}

# CR Inbound Flight
CR_INBOUND_FLIGHT = {'events': [
    ('inbound_flight_selected_flight', []),
    ('revenue_amount', [])
]}

# CR Discount Club
CR_DISCOUNT_CLUB = {'events': [
    ('dc_modal_dom_loaded', []),
    ('revenue_amount', [])
]}

