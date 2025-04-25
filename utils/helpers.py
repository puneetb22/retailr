"""
Helper functions for POS system
"""

import re
from decimal import Decimal, ROUND_HALF_UP

def format_currency(amount, symbol="₹"):
    """Format decimal amount to currency string"""
    if amount is None:
        return f"{symbol}0.00"
    
    # Format with 2 decimal places and thousands separator
    formatted = "{:,.2f}".format(float(amount))
    return f"{symbol}{formatted}"

def parse_currency(amount_str):
    """Parse currency string to Decimal"""
    if not amount_str:
        return Decimal('0.00')
        
    # Remove currency symbol and any thousand separators
    clean = re.sub(r'[^\d.-]', '', amount_str)
    
    try:
        return Decimal(clean).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    except:
        return Decimal('0.00')