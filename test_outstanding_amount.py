"""
Test outstanding amount calculation logic for customers.
"""
import sqlite3
import datetime

def get_outstanding_amount(customer_id):
    """Get outstanding amount for a specific customer"""
    conn = sqlite3.connect('pos_data.db')
    cursor = conn.cursor()
    
    try:
        # Get total outstanding amount
        query = """
            SELECT SUM(credit_amount) FROM invoices 
            WHERE customer_id = ? AND (payment_status IN ('CREDIT', 'PARTIALLY_PAID', 'PARTIAL', 'UNPAID'))
        """
        result = cursor.execute(query, (customer_id,)).fetchone()
        total_outstanding = result[0] or 0
        
        # Get customer info
        customer_query = "SELECT id, name FROM customers WHERE id = ?"
        customer_info = cursor.execute(customer_query, (customer_id,)).fetchone()
        
        # Get invoice details
        invoice_query = """
            SELECT id, invoice_number, total_amount, credit_amount, payment_status, payment_method
            FROM invoices
            WHERE customer_id = ? AND (payment_status IN ('CREDIT', 'PARTIALLY_PAID', 'PARTIAL', 'UNPAID'))
        """
        invoices = cursor.execute(invoice_query, (customer_id,)).fetchall()
        
        # Print customer info
        print(f"Customer ID: {customer_info[0]}, Name: {customer_info[1]}")
        print(f"Total Outstanding Amount: ₹{total_outstanding:.2f}")
        print("\nOutstanding Invoices:")
        
        # Print invoice details
        if invoices:
            for inv in invoices:
                print(f"ID: {inv[0]}, Invoice: {inv[1]}, Total: ₹{inv[2]:.2f}, " +
                      f"Outstanding: ₹{inv[3]:.2f}, Status: {inv[4]}, Method: {inv[5]}")
        else:
            print("No outstanding invoices found.")
            
        return total_outstanding
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("\n=== Testing Outstanding Amount for Prakash Bhosle (ID: 2) ===")
    get_outstanding_amount(2)
    
    print("\n=== Testing Outstanding Amount for Sanjay Patil (ID: 3) ===")
    get_outstanding_amount(3)