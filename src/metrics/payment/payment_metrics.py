# filtros amplitude
from src.utils.amplitude_filters import (
    get_DB_filter
)

# Next Step Rate Payment (Payment to Confirmation)
NSR_PAYMENT = {'events': [
    ('payment_dom_loaded', []),
    ('payment_confirmation_loaded', [])
]}

# Next Step Rate Payment - DB
NSR_PAYMENT_DB = {'events': [
    ('payment_dom_loaded', [get_DB_filter()]),
    ('payment_confirmation_loaded', [get_DB_filter()])
]}

# Website Conversion Rate from Payment - General
WCR_PAYMENT = {'events': [
    ('payment_dom_loaded', []),
    ('payment_confirmation_loaded', [])
]}

# Website Conversion Rate from Payment - DB
WCR_PAYMENT_DB = {'events': [
    ('payment_dom_loaded', [get_DB_filter()]),
    ('revenue_amount', [get_DB_filter()])
]}

# Payment Method Selection Rate
PAYMENT_SELECTED_RATE = {'events': [
    ('payment_dom_loaded', []),
    ('payment_selected', [])
]}

# Payment Click Rate
PAYMENT_CLICK_RATE = {'events': [
    ('payment_dom_loaded', []),
    ('payment_clicked', [])
]}

# Installments Selection Rate
INSTALLMENTS_SELECTION_RATE = {'events': [
    ('payment_dom_loaded', []),
    ('installments_selected', [])
]}

# Direct Payment Modal Skip Rate
SKIP_DIRECT_PAYMENT_RATE = {'events': [
    ('payment_dom_loaded', []),
    ('modal_skip_direct_payment_clicked', [])
]}

# Toggle Taxes Click Rate
TOGGLE_TAXES_RATE = {'events': [
    ('payment_dom_loaded', []),
    ('click_toggle_taxes', [])
]}

# Payment to Revenue (Final Conversion)
PAYMENT_TO_REVENUE = {'events': [
    ('payment_confirmation_loaded', []),
    ('payment_confirmation_loaded', [])
]}

