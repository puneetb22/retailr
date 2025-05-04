"""
Test customer data to debug purchase history issues.
"""
import sqlite3
import datetime
import os

def display_all_customer_data(customer_id):
    """Display all relevant data for a customer to diagnose issues"""
    conn = sqlite3.connect('pos_data.db')
    cursor = conn.cursor()
    
    try:
        # Get customer info
        customer_query = "SELECT id, name, phone, credit_limit FROM customers WHERE id = ?"
        customer = cursor.execute(customer_query, (customer_id,)).fetchone()
        if not customer:
            print(f"No customer found with ID {customer_id}")
            return
        
        print(f"\n--- Customer Information ---")
        print(f"ID: {customer[0]}")
        print(f"Name: {customer[1]}")
        print(f"Phone: {customer[2]}")
        print(f"Credit Limit: ₹{customer[3] or 0:.2f}")
        
        # Get all customer invoices
        invoices_query = """
            SELECT id, invoice_number, invoice_date, total_amount, payment_method, payment_status, credit_amount
            FROM invoices 
            WHERE customer_id = ?
            ORDER BY invoice_date DESC
        """
        invoices = cursor.execute(invoices_query, (customer_id,)).fetchall()
        
        print(f"\n--- Invoices for Customer {customer[1]} ---")
        if not invoices:
            print("No invoices found for this customer")
        else:
            print(f"Found {len(invoices)} invoices")
            for inv in invoices:
                print(f"ID: {inv[0]}, Number: {inv[1]}, Date: {inv[2]}, Total: ₹{inv[3]:.2f}, " +
                      f"Method: {inv[4]}, Status: {inv[5]}, Credit Amount: ₹{inv[6] or 0:.2f}")
        
        # Get customer payments
        payments_query = """
            SELECT id, invoice_id, amount, payment_method, payment_date, depositor_name, notes, created_at
            FROM customer_payments
            WHERE customer_id = ?
            ORDER BY payment_date DESC
        """
        payments = cursor.execute(payments_query, (customer_id,)).fetchall()
        
        print(f"\n--- Payment History for Customer {customer[1]} ---")
        if not payments:
            print("No payment records found for this customer")
        else:
            print(f"Found {len(payments)} payment records")
            for pmt in payments:
                # Get invoice number for this payment
                inv_query = "SELECT invoice_number FROM invoices WHERE id = ?"
                invoice_num = cursor.execute(inv_query, (pmt[1],)).fetchone()
                inv_str = invoice_num[0] if invoice_num else "Unknown"
                
                print(f"ID: {pmt[0]}, Invoice: {inv_str}, Amount: ₹{pmt[2]:.2f}, " +
                      f"Method: {pmt[3]}, Date: {pmt[4]}, Depositor: {pmt[5]}, " +
                      f"Notes: {pmt[6]}, Created: {pmt[7]}")
        
        # Calculate outstanding amount
        outstanding_query = """
            SELECT SUM(credit_amount) FROM invoices 
            WHERE customer_id = ? AND (payment_status IN ('CREDIT', 'PARTIALLY_PAID', 'PARTIAL', 'UNPAID'))
        """
        outstanding = cursor.execute(outstanding_query, (customer_id,)).fetchone()[0] or 0
        print(f"\n--- Credit Summary ---")
        print(f"Total Outstanding Amount: ₹{outstanding:.2f}")
        
        # Get outstanding invoices
        outstanding_inv_query = """
            SELECT id, invoice_number, invoice_date, total_amount, credit_amount, payment_status
            FROM invoices
            WHERE customer_id = ? AND (payment_status IN ('CREDIT', 'PARTIALLY_PAID', 'PARTIAL', 'UNPAID'))
            ORDER BY invoice_date DESC
        """
        outstanding_invoices = cursor.execute(outstanding_inv_query, (customer_id,)).fetchall()
        
        print(f"\n--- Outstanding Invoices ---")
        if not outstanding_invoices:
            print("No outstanding invoices for this customer")
        else:
            for inv in outstanding_invoices:
                # Calculate days outstanding
                try:
                    date_str = inv[2]
                    if ' ' in date_str:  # Format with time
                        date_str = date_str.split(' ')[0]
                    
                    invoice_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                    days_outstanding = (datetime.date.today() - invoice_date).days
                except (ValueError, TypeError):
                    days_outstanding = 0
                
                print(f"ID: {inv[0]}, Number: {inv[1]}, Date: {inv[2]}, " +
                      f"Total: ₹{inv[3]:.2f}, Outstanding: ₹{inv[4]:.2f}, " +
                      f"Status: {inv[5]}, Days Outstanding: {days_outstanding}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("\n=== Testing Prakash Bhosle (ID: 2) ===")
    display_all_customer_data(2)
    
    print("\n=== Testing Sanjay Patil (ID: 3) ===")
    display_all_customer_data(3)