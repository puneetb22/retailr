"""
Helper functions for POS system
Common utility functions used across the application
"""

import os
import datetime
import re
import tkinter as tk
from decimal import Decimal

def format_currency(amount, symbol="₹", decimal_places=2):
    """
    Format a number as currency with Indian Rupee symbol and Indian number format
    Example: ₹1,23,456.78
    
    Args:
        amount: Number to format
        symbol: Currency symbol (default: ₹)
        decimal_places: Number of decimal places to show
        
    Returns:
        Formatted currency string with Indian number system
    """
    if amount is None:
        return f"{symbol}0.00"
        
    try:
        # Convert to float (handles Decimal, string and other numeric types)
        amount = float(amount)
        
        # Format with proper rounding
        # We multiply by 10^decimal_places, round, and then divide to get exact decimal places
        rounded_amount = round(amount * (10 ** decimal_places)) / (10 ** decimal_places)
        
        # Get the integer and decimal parts
        int_part = int(rounded_amount)
        decimal_part = int(round((rounded_amount - int_part) * (10 ** decimal_places)))
        
        # Format decimal part to ensure correct number of places
        decimal_str = f"{decimal_part:0{decimal_places}d}"
        
        # Convert integer part to string
        int_str = str(int_part)
        
        # Special case for zero
        if int_part == 0:
            int_str = "0"
            
        # Improved implementation of Indian number formatting (e.g., 1,00,00,000.00)
        if len(int_str) <= 3:
            # Numbers up to 999
            result = int_str
        else:
            # First group of 3 from right
            result = int_str[-3:]
            # Remaining digits in groups of 2 from right to left
            remaining = int_str[:-3]
            i = len(remaining)
            while i > 0:
                if i >= 2:
                    result = remaining[i-2:i] + "," + result
                    i -= 2
                else:
                    result = remaining[0:i] + "," + result
                    i = 0
            
        # Combine parts
        formatted = f"{symbol}{result}.{decimal_str}"
        return formatted
        
    except (ValueError, TypeError) as e:
        print(f"Currency formatting error: {e}")
        return f"{symbol}0.00"

def parse_currency(currency_str):
    """
    Parse a currency string to Decimal
    
    Args:
        currency_str: String containing currency amount
        
    Returns:
        Decimal representation of the amount
    """
    print(f"DEBUG parse_currency input: '{currency_str}', type: {type(currency_str)}")
    
    # If already a numeric type, just convert to Decimal
    if isinstance(currency_str, (int, float, Decimal)):
        result = Decimal(str(currency_str))
        print(f"DEBUG parse_currency numeric result: {result}")
        return result
        
    # Handle empty or None values
    if not currency_str:
        print("DEBUG parse_currency empty input, returning 0")
        return Decimal('0')
        
    # Convert to string if it's not already
    currency_str = str(currency_str)
    
    # Print the string before cleaning for debugging
    print(f"DEBUG parse_currency string before cleaning: '{currency_str}'")
    
    # Remove everything except digits, minus sign, and decimal point
    clean_str = re.sub(r'[^\d.-]', '', currency_str)
    
    # Print the cleaned string for debugging
    print(f"DEBUG parse_currency after cleaning: '{clean_str}'")
    
    try:
        result = Decimal(clean_str)
        print(f"DEBUG parse_currency final result: {result}")
        return result
    except Exception as e:
        print(f"DEBUG parse_currency error: {e}, returning 0")
        return Decimal('0')

def format_date(date_obj, format_str="%d-%m-%Y"):
    """
    Format a date object to string
    
    Args:
        date_obj: Date object or string
        format_str: Date format string
        
    Returns:
        Formatted date string
    """
    if not date_obj:
        return ""
        
    # If already a string, try to parse it
    if isinstance(date_obj, str):
        try:
            # Assume ISO format if it's a string
            date_obj = datetime.datetime.fromisoformat(date_obj.replace('Z', '+00:00'))
        except ValueError:
            # Return as is if parsing fails
            return date_obj
    
    try:
        return date_obj.strftime(format_str)
    except:
        return str(date_obj)

def parse_date(date_str, format_str="%d-%m-%Y"):
    """
    Parse a date string to date object
    
    Args:
        date_str: String containing date
        format_str: Expected date format
        
    Returns:
        Date object or None if parsing fails
    """
    if not date_str:
        return None
        
    # If already a date/datetime object, return it
    if isinstance(date_str, (datetime.date, datetime.datetime)):
        return date_str
        
    try:
        return datetime.datetime.strptime(date_str, format_str).date()
    except ValueError:
        # Try ISO format
        try:
            return datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
        except ValueError:
            return None

def calculate_gst(amount, rate=18, is_inclusive=True):
    """
    Calculate GST amount for a given amount and rate
    
    Args:
        amount: Amount (inclusive of tax if is_inclusive=True)
        rate: GST rate in percentage
        is_inclusive: Whether the amount already includes tax
        
    Returns:
        Tuple of (taxable_amount, gst_amount, total_amount)
    """
    if not amount:
        return Decimal('0'), Decimal('0'), Decimal('0')
        
    try:
        amount = Decimal(str(amount))
        gst_rate = Decimal(str(rate)) / Decimal('100')
        
        if is_inclusive:
            # Calculate GST from inclusive amount
            # Formula: taxable_amount = amount / (1 + gst_rate)
            taxable_amount = amount / (Decimal('1') + gst_rate)
            gst_amount = amount - taxable_amount
            total_amount = amount  # Total already includes GST
        else:
            # Calculate GST for exclusive amount
            taxable_amount = amount
            gst_amount = amount * gst_rate
            total_amount = amount + gst_amount
        
        return taxable_amount, gst_amount, total_amount
    except Exception as e:
        print(f"GST calculation error: {e}")
        return Decimal('0'), Decimal('0'), Decimal('0')

def calculate_discount(amount, discount, is_percentage=True):
    """
    Calculate discount amount
    
    Args:
        amount: Original amount
        discount: Discount amount or percentage
        is_percentage: Whether discount is a percentage
        
    Returns:
        Tuple of (discount_amount, discounted_price)
    """
    if not amount or not discount:
        return Decimal('0'), Decimal(str(amount)) if amount else Decimal('0')
        
    try:
        amount = Decimal(str(amount))
        discount = Decimal(str(discount))
        
        if is_percentage:
            if discount > 100:
                discount = Decimal('100')
            discount_amount = amount * (discount / Decimal('100'))
        else:
            if discount > amount:
                discount = amount
            discount_amount = discount
            
        discounted_price = amount - discount_amount
        
        return discount_amount, discounted_price
    except:
        return Decimal('0'), Decimal(str(amount)) if amount else Decimal('0')

def get_financial_year_dates():
    """
    Get start and end dates for the current financial year (April to March)
    
    Returns:
        Tuple of (start_date, end_date)
    """
    today = datetime.date.today()
    current_year = today.year
    current_month = today.month
    
    # If current month is January to March, financial year started last year
    if current_month <= 3:
        start_year = current_year - 1
        end_year = current_year
    else:
        start_year = current_year
        end_year = current_year + 1
        
    start_date = datetime.date(start_year, 4, 1)
    end_date = datetime.date(end_year, 3, 31)
    
    return start_date, end_date

def get_quarter_dates(year=None, quarter=None):
    """
    Get start and end dates for a specific quarter
    
    Args:
        year: Year (default: current year)
        quarter: Quarter number 1-4 (default: current quarter)
        
    Returns:
        Tuple of (start_date, end_date)
    """
    today = datetime.date.today()
    
    if year is None:
        year = today.year
        
    if quarter is None:
        # Calculate current quarter
        quarter = (today.month - 1) // 3 + 1
        
    if quarter < 1 or quarter > 4:
        quarter = 1
        
    quarters = {
        1: (datetime.date(year, 1, 1), datetime.date(year, 3, 31)),
        2: (datetime.date(year, 4, 1), datetime.date(year, 6, 30)),
        3: (datetime.date(year, 7, 1), datetime.date(year, 9, 30)),
        4: (datetime.date(year, 10, 1), datetime.date(year, 12, 31))
    }
    
    return quarters[quarter]

def generate_invoice_number(prefix="INV", last_number=0):
    """
    Generate an invoice number
    
    Args:
        prefix: Invoice number prefix
        last_number: Last used invoice number
        
    Returns:
        New invoice number string
    """
    next_number = last_number + 1
    today = datetime.date.today()
    date_part = today.strftime("%Y%m")
    
    return f"{prefix}{date_part}{next_number:04d}"

def num_to_words_indian(num):
    """
    Convert a number to words in Indian numbering system
    e.g. 1234567 -> Twelve Lakh Thirty Four Thousand Five Hundred Sixty Seven Rupees Only
    
    Args:
        num: Number to convert (float or int)
        
    Returns:
        String representation of the number in words following Indian currency format
    """
    if not isinstance(num, (int, float, Decimal)):
        try:
            num = float(num)
        except (ValueError, TypeError):
            return "Zero Rupees Only"
            
    if num == 0:
        return "Zero Rupees Only"
        
    ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", 
            "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", 
            "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
    
    def numToWords(n):
        """Convert a number to words using Indian number system"""
        if n == 0:
            return ""
        if n < 20:
            return ones[n]
        elif n < 100:
            return tens[n // 10] + (" " + ones[n % 10] if n % 10 != 0 else "")
        elif n < 1000:
            return ones[n // 100] + " Hundred" + (" and " + numToWords(n % 100) if n % 100 != 0 else "")
        elif n < 100000:  # Less than 1 lakh
            return numToWords(n // 1000) + " Thousand" + (" " + numToWords(n % 1000) if n % 1000 != 0 else "")
        elif n < 10000000:  # Less than 1 crore
            return numToWords(n // 100000) + " Lakh" + (" " + numToWords(n % 100000) if n % 100000 != 0 else "")
        elif n < 1000000000:  # Less than 100 crore
            return numToWords(n // 10000000) + " Crore" + (" " + numToWords(n % 10000000) if n % 10000000 != 0 else "")
        else:  # Beyond 100 crore
            return numToWords(n // 1000000000) + " Arab" + (" " + numToWords(n % 1000000000) if n % 1000000000 != 0 else "")
    
    try:
        # Handle Decimal type
        if isinstance(num, Decimal):
            num = float(num)
            
        # Ensure precise handling of paise with rounding
        num_rounded = round(num, 2)  # Round to 2 decimal places
        
        # Convert to integer and keep track of paise
        rupees = int(num_rounded)
        paise = int(round((num_rounded - rupees) * 100))
        
        # Convert rupees to words
        rupees_text = numToWords(rupees)
        
        # Handle special case when amount is zero
        if rupees == 0 and paise == 0:
            return "Zero Rupees Only"
            
        # Handle special case if only paise exists
        if rupees == 0 and paise > 0:
            return numToWords(paise) + " Paise Only"
        
        # Convert paise to words if there are any
        if paise > 0:
            # For formal invoice display, format is typically like:
            # "One Thousand Two Hundred Thirty Four Rupees and Fifty Six Paise Only"
            return f"{rupees_text} Rupees and {numToWords(paise)} Paise Only"
        else:
            return f"{rupees_text} Rupees Only"
    except Exception as e:
        print(f"Error in num_to_words_indian: {e}")
        return "Amount In Words: Error Converting to Words"

def make_button_keyboard_navigable(button, command=None):
    """
    Enhance a button with keyboard navigation support
    
    Args:
        button: Tkinter Button widget to enhance
        command: Function to call when button is activated (defaults to button's command)
    """
    if not isinstance(button, tk.Button):
        print("Warning: Widget is not a Button. Keyboard navigation might not work properly.")
        return
    
    # If no command is provided, use the button's command
    if command is None:
        command = button.cget("command")
    
    # Skip if there's no command to execute
    if not command:
        print("Warning: Button has no command. Keyboard navigation won't work.")
        return
    
    # Increase highlight thickness for better focus visibility
    button.config(highlightthickness=3)
    
    # Function to handle Enter key
    def on_enter(event):
        command()
        return "break"  # Prevent event propagation
    
    # Bind Enter key to button
    button.bind("<Return>", on_enter)
    button.bind("<space>", on_enter)
    
    return button  # Return the button for method chaining