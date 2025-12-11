# filtros amplitude
from src.utils.amplitude_filters import (
    get_DB_filter
)

# Next Step Rate Passengers - General
NSR_PASSENGERS = {'events': [
    ('passengers_dom_loaded', []),
    ('payment_dom_loaded', [])
]}

# Next Step Rate Passengers - DB
NSR_PASSENGERS_DB = {'events': [
    ('passengers_dom_loaded', [get_DB_filter()]),
    ('payment_dom_loaded', [get_DB_filter()])
]}

# Website Conversion Rate from Passengers - General
WCR_PASSENGERS = {'events': [
    ('passengers_dom_loaded', []),
    ('payment_confirmation_loaded', [])
]}

# Website Conversion Rate from Passengers - DB
WCR_PASSENGERS_DB = {'events': [
    ('passengers_dom_loaded', [get_DB_filter()]),
    ('revenue_amount', [get_DB_filter()])
]}

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

