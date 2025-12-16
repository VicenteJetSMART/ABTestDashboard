# filtros amplitude
from src.utils.amplitude_filters import (
    get_DB_filter
)

# ===== NEXT STEP RATE (NSR) =====

# Next Step Rate Payment (Payment to Confirmation)
PAYMENT_NSR = {'events': [
    ('payment_dom_loaded', []),
    ('revenue_amount', [])
]}

# Next Step Rate Payment - DB
PAYMENT_DB_NSR = {'events': [
    ('payment_dom_loaded', [get_DB_filter()]),
    ('revenue_amount', [get_DB_filter()])
]}

# ===== WEBSITE CONVERSION RATE (WCR) =====

# Website Conversion Rate from Payment - General
PAYMENT_WCR = {'events': [
    ('payment_dom_loaded', []),
    ('revenue_amount', [])
]}

# Website Conversion Rate from Payment - DB
PAYMENT_DB_WCR = {'events': [
    ('payment_dom_loaded', [get_DB_filter()]),
    ('revenue_amount', [get_DB_filter()])
]}

# ===== SELECTION RATE =====

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

# ===== PAYMENT TO REVENUE (MANTENER EXACTO) =====

# Payment to Revenue (Final Conversion)
PAYMENT_TO_REVENUE = {'events': [
    ('payment_dom_loaded', []),
    ('revenue_amount', [])
]}
