# filtros amplitude
from src.utils.amplitude_filters import (
    get_DB_filter
)

# ===== NEXT STEP RATE (NSR) =====

# Next Step Rate Passengers - General
PASSENGERS_NSR = {'events': [
    ('passengers_dom_loaded', []),
    ('payment_dom_loaded', [])
]}

# Next Step Rate Passengers - DB
PASSENGERS_DB_NSR = {'events': [
    ('passengers_dom_loaded', [get_DB_filter()]),
    ('payment_dom_loaded', [get_DB_filter()])
]}

# ===== WEBSITE CONVERSION RATE (WCR) =====

# Website Conversion Rate from Passengers - General
PASSENGERS_WCR = {'events': [
    ('passengers_dom_loaded', []),
    ('revenue_amount', [])
]}

# Website Conversion Rate from Passengers - DB
PASSENGERS_DB_WCR = {'events': [
    ('passengers_dom_loaded', [get_DB_filter()]),
    ('revenue_amount', [get_DB_filter()])
]}

# ===== CONTINUE RATE =====

# Continue Clicked Passengers Rate
PASSENGERS_CONTINUE_RATE = {'events': [
    ('passengers_dom_loaded', []),
    ('continue_clicked_passengers', [])
]}

# Gender Continue Rate
GENDER_CONTINUE_RATE = {'events': [
    ('passengers_dom_loaded', []),
    ('continue_gender_passengers', [])
]}

# AAdvantage Click Rate
AADVANTAGE_CLICK_RATE = {'events': [
    ('passengers_dom_loaded', []),
    ('click_aadvantage_passengers', [])
]}

# User Login Rate in Passengers
PASSENGERS_LOGIN_RATE = {'events': [
    ('passengers_dom_loaded', []),
    ('user_login', [])
]}
