#!/usr/bin/env python3
"""
Test script to verify GST calculations with 18% tax rate (9% CGST + 9% SGST).
This script tests both inclusive and exclusive tax calculations.
"""

from decimal import Decimal, ROUND_HALF_UP, getcontext

# Set precision to 10 decimal places for consistent results
getcontext().prec = 10
getcontext().rounding = ROUND_HALF_UP

def calculate_gst_inclusive(amount, rate=18):
    """
    Calculate GST from an amount that already includes tax.
    Example: For a product priced at Rs. 118 (inclusive of 18% GST),
    the taxable value is Rs. 100 and GST is Rs. 18.
    
    Args:
        amount: Amount (inclusive of tax)
        rate: GST rate in percentage (default: 18%)
        
    Returns:
        Tuple of (taxable_amount, gst_amount, total_amount)
    """
    if not amount:
        return Decimal('0'), Decimal('0'), Decimal('0')
        
    try:
        amount = Decimal(str(amount))
        gst_rate = Decimal(str(rate)) / Decimal('100')
        
        # Formula: taxable_value = total_price / (1 + tax_rate)
        taxable_amount = amount / (Decimal('1') + gst_rate)
        
        # GST amount is the difference between total and taxable amount
        gst_amount = amount - taxable_amount
        
        # Total amount is the original amount (since it's inclusive of tax)
        total_amount = amount
        
        return taxable_amount, gst_amount, total_amount
        
    except Exception as e:
        print(f"Error calculating GST (inclusive): {e}")
        return Decimal('0'), Decimal('0'), Decimal('0')

def calculate_gst_exclusive(amount, rate=18):
    """
    Calculate GST for an amount that does not include tax.
    Example: For a product priced at Rs. 100 (exclusive of GST),
    the total price with 18% GST is Rs. 118.
    
    Args:
        amount: Amount (exclusive of tax)
        rate: GST rate in percentage (default: 18%)
        
    Returns:
        Tuple of (taxable_amount, gst_amount, total_amount)
    """
    if not amount:
        return Decimal('0'), Decimal('0'), Decimal('0')
        
    try:
        amount = Decimal(str(amount))
        gst_rate = Decimal(str(rate)) / Decimal('100')
        
        # Taxable amount is the original amount
        taxable_amount = amount
        
        # GST amount is calculated by applying the rate to the taxable amount
        gst_amount = taxable_amount * gst_rate
        
        # Total amount is taxable amount plus GST
        total_amount = taxable_amount + gst_amount
        
        return taxable_amount, gst_amount, total_amount
        
    except Exception as e:
        print(f"Error calculating GST (exclusive): {e}")
        return Decimal('0'), Decimal('0'), Decimal('0')

def format_currency(amount, symbol="₹", decimal_places=2):
    """Format a number as currency with Indian number format"""
    try:
        amount = Decimal(str(amount))
        
        # Round to specified decimal places
        rounded = amount.quantize(Decimal('0.01'))
        
        # Convert to string and split
        amount_str = str(rounded)
        parts = amount_str.split('.')
        
        # Format the whole number part with Indian numbering system
        whole = parts[0]
        decimal = parts[1] if len(parts) > 1 else "00"
        
        # Ensure decimal part has correct number of digits
        decimal = decimal.ljust(decimal_places, '0')[:decimal_places]
        
        # Format the whole number part with commas
        if len(whole) > 3:
            # Add commas for thousands
            formatted = whole[-3:]
            remaining = whole[:-3]
            
            # Add commas for lakhs and above (Indian numbering system)
            i = len(remaining)
            while i > 0:
                if i >= 2:
                    formatted = remaining[i-2:i] + "," + formatted
                    i -= 2
                else:
                    formatted = remaining[0:i] + "," + formatted
                    i = 0
            
            result = f"{symbol}{formatted}.{decimal}"
        else:
            result = f"{symbol}{whole}.{decimal}"
            
        return result
        
    except Exception as e:
        print(f"Error formatting currency: {e}")
        return f"{symbol}0.00"

def main():
    """Test GST calculations with various amounts"""
    print("===== TAX-INCLUSIVE CALCULATIONS (18% GST) =====")
    print("When price includes tax:")
    
    test_values = [100, 118, 500, 1000, 1180, 5000, 10000]
    
    print("\n{:<15} {:<15} {:<15} {:<15}".format(
        "Total (Incl.)", "Taxable Value", "GST (18%)", "CGST+SGST (9%+9%)"
    ))
    print("-" * 65)
    
    for value in test_values:
        taxable, gst, total = calculate_gst_inclusive(value)
        cgst = gst / 2
        
        print("{:<15} {:<15} {:<15} {:<15}".format(
            format_currency(total), 
            format_currency(taxable), 
            format_currency(gst),
            f"{format_currency(cgst)}+{format_currency(cgst)}"
        ))
    
    print("\n\n===== TAX-EXCLUSIVE CALCULATIONS (18% GST) =====")
    print("When price excludes tax:")
    
    print("\n{:<15} {:<15} {:<15} {:<15}".format(
        "Base Value", "GST (18%)", "Total (Incl.)", "CGST+SGST (9%+9%)"
    ))
    print("-" * 65)
    
    for value in test_values:
        taxable, gst, total = calculate_gst_exclusive(value)
        cgst = gst / 2
        
        print("{:<15} {:<15} {:<15} {:<15}".format(
            format_currency(taxable), 
            format_currency(gst),
            format_currency(total), 
            f"{format_currency(cgst)}+{format_currency(cgst)}"
        ))
    
    # Test a specific value with full calculations
    print("\n\nDetailed example with ₹1,180 (inclusive of GST):")
    price = Decimal('1180')
    taxable, gst, total = calculate_gst_inclusive(price)
    cgst = gst / 2
    
    print(f"Price including GST: {format_currency(price)}")
    print(f"Taxable value: {format_currency(taxable)}")
    print(f"Total GST (18%): {format_currency(gst)}")
    print(f"CGST (9%): {format_currency(cgst)}")
    print(f"SGST (9%): {format_currency(cgst)}")
    print(f"Verification: {format_currency(taxable)} + {format_currency(gst)} = {format_currency(taxable + gst)}")

if __name__ == "__main__":
    main()