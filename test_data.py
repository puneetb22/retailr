"""
Test Data Generator for the POS System
This script adds mock data to test different features of the POS system
"""

import datetime
import sqlite3
import random
import os

# Database connection
DB_PATH = './pos_data.db'

def connect_db():
    """Connect to the SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def add_inventory_test_data():
    """Add test data for inventory alerts functionality"""
    conn = connect_db()
    cursor = conn.cursor()
    
    print("Adding inventory test data...")
    
    # Add new test products
    test_products = [
        {
            "product_code": "FERT002",
            "name": "NPK Fertilizer",
            "category": "Fertilizers",
            "vendor": "Godrej Agrovet",
            "hsn_code": "3105",
            "description": "Balanced NPK fertilizer for all crops",
            "wholesale_price": 520,
            "selling_price": 600,
            "tax_percentage": 5
        },
        {
            "product_code": "PEST002",
            "name": "Fungicide Spray",
            "category": "Pesticides",
            "vendor": "Bayer CropScience",
            "hsn_code": "3808",
            "description": "Effective against fungal infections in crops",
            "wholesale_price": 420,
            "selling_price": 480,
            "tax_percentage": 12
        },
        {
            "product_code": "SEED002",
            "name": "Hybrid Maize Seeds",
            "category": "Seeds",
            "vendor": "Syngenta",
            "hsn_code": "1005",
            "description": "High-yielding hybrid maize seeds (1 kg)",
            "wholesale_price": 650,
            "selling_price": 750,
            "tax_percentage": 5
        },
        {
            "product_code": "EQUIP002",
            "name": "Garden Hoe",
            "category": "Equipment",
            "vendor": "UPL Limited",
            "hsn_code": "8201",
            "description": "Manual farming tool for weeding",
            "wholesale_price": 350,
            "selling_price": 450,
            "tax_percentage": 18
        }
    ]
    
    # Insert test products
    for product in test_products:
        try:
            cursor.execute(
                """
                INSERT OR IGNORE INTO products 
                (product_code, name, category, vendor, hsn_code, description, 
                wholesale_price, selling_price, tax_percentage)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    product["product_code"],
                    product["name"],
                    product["category"],
                    product["vendor"],
                    product["hsn_code"],
                    product["description"],
                    product["wholesale_price"],
                    product["selling_price"],
                    product["tax_percentage"]
                )
            )
        except Exception as e:
            print(f"Error adding product {product['name']}: {e}")
    
    conn.commit()
    
    # Get product IDs
    cursor.execute("SELECT id, name FROM products")
    products = {row['name']: row['id'] for row in cursor.fetchall()}
    
    # Add inventory batches for testing low stock alerts
    low_stock_batch = {
        "product_id": products.get("Garden Hoe"),
        "batch_number": "EQ002B001",
        "quantity": 5,  # Below default threshold of 10
        "manufacturing_date": (datetime.datetime.now() - datetime.timedelta(days=60)).strftime('%Y-%m-%d'),
        "expiry_date": (datetime.datetime.now() + datetime.timedelta(days=730)).strftime('%Y-%m-%d'),
        "purchase_date": (datetime.datetime.now() - datetime.timedelta(days=20)).strftime('%Y-%m-%d'),
        "cost_price": 350
    }
    
    # Add inventory batches for testing expiring soon alerts (within 30 days)
    expiring_soon_batch = {
        "product_id": products.get("Fungicide Spray"),
        "batch_number": "P002B001",
        "quantity": 25,
        "manufacturing_date": (datetime.datetime.now() - datetime.timedelta(days=335)).strftime('%Y-%m-%d'),
        "expiry_date": (datetime.datetime.now() + datetime.timedelta(days=25)).strftime('%Y-%m-%d'),
        "purchase_date": (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d'),
        "cost_price": 420
    }
    
    # Add inventory batches for testing expired alerts
    expired_batch = {
        "product_id": products.get("NPK Fertilizer"),
        "batch_number": "F002B001",
        "quantity": 15,
        "manufacturing_date": (datetime.datetime.now() - datetime.timedelta(days=400)).strftime('%Y-%m-%d'),
        "expiry_date": (datetime.datetime.now() - datetime.timedelta(days=5)).strftime('%Y-%m-%d'),
        "purchase_date": (datetime.datetime.now() - datetime.timedelta(days=200)).strftime('%Y-%m-%d'),
        "cost_price": 520
    }
    
    # Add normal batch (control)
    normal_batch = {
        "product_id": products.get("Hybrid Maize Seeds"),
        "batch_number": "S002B001",
        "quantity": 40,
        "manufacturing_date": (datetime.datetime.now() - datetime.timedelta(days=60)).strftime('%Y-%m-%d'),
        "expiry_date": (datetime.datetime.now() + datetime.timedelta(days=305)).strftime('%Y-%m-%d'),
        "purchase_date": (datetime.datetime.now() - datetime.timedelta(days=20)).strftime('%Y-%m-%d'),
        "cost_price": 650
    }
    
    # Insert test batches
    test_batches = [low_stock_batch, expiring_soon_batch, expired_batch, normal_batch]
    
    for batch in test_batches:
        if batch["product_id"] is None:
            print(f"Skipping batch with missing product ID")
            continue
            
        try:
            cursor.execute(
                """
                INSERT INTO batches 
                (product_id, batch_number, quantity, manufacturing_date, 
                expiry_date, purchase_date, cost_price)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    batch["product_id"],
                    batch["batch_number"],
                    batch["quantity"],
                    batch["manufacturing_date"],
                    batch["expiry_date"],
                    batch["purchase_date"],
                    batch["cost_price"]
                )
            )
            
            # Also add to inventory (some POS features might use this table)
            cursor.execute(
                """
                INSERT INTO inventory 
                (product_id, batch_number, quantity, manufacturing_date, 
                expiry_date, purchase_date)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    batch["product_id"],
                    batch["batch_number"],
                    batch["quantity"],
                    batch["manufacturing_date"],
                    batch["expiry_date"],
                    batch["purchase_date"]
                )
            )
            
            print(f"Added batch {batch['batch_number']} for product ID {batch['product_id']}")
        except Exception as e:
            print(f"Error adding batch {batch['batch_number']}: {e}")
    
    conn.commit()

def add_sales_data():
    """Add test data for sales functionality"""
    conn = connect_db()
    cursor = conn.cursor()
    
    print("Adding sales test data...")
    
    # Get customer IDs
    cursor.execute("SELECT id, name FROM customers")
    customers = {row['name']: row['id'] for row in cursor.fetchall()}
    
    # Get product IDs
    cursor.execute("SELECT id, name, selling_price, tax_percentage FROM products")
    products = {row['id']: {
        'name': row['name'], 
        'price': row['selling_price'], 
        'tax': row['tax_percentage']
    } for row in cursor.fetchall()}
    
    # Generate test sales (last 30 days)
    today = datetime.date.today()
    
    # Insert 10 test sales
    for i in range(1, 11):
        # Random date within last 30 days
        sale_date = today - datetime.timedelta(days=random.randint(0, 30))
        
        # Random customer (sometimes walk-in)
        customer_names = list(customers.keys())
        customer_name = random.choice(customer_names)
        customer_id = customers[customer_name]
        
        # Generate invoice number
        invoice_number = f"AGT{sale_date.strftime('%Y%m%d')}{i:02d}"
        
        # Calculate amounts
        product_ids = list(products.keys())
        # Pick 1-3 random products for the sale
        sale_products = random.sample(product_ids, random.randint(1, min(3, len(product_ids))))
        
        subtotal = 0
        tax_amount = 0
        
        # Prepare invoice items
        invoice_items = []
        
        for product_id in sale_products:
            # Random quantity 1-5
            quantity = random.randint(1, 5)
            price = products[product_id]['price']
            tax_rate = products[product_id]['tax']
            
            # Calculate item total
            item_subtotal = quantity * price
            item_tax = item_subtotal * (tax_rate / 100)
            item_total = item_subtotal + item_tax
            
            subtotal += item_subtotal
            tax_amount += item_tax
            
            invoice_items.append({
                'product_id': product_id,
                'quantity': quantity,
                'price_per_unit': price,
                'tax_percentage': tax_rate,
                'total_price': item_subtotal  # Pre-tax total for the item
            })
        
        total_amount = subtotal + tax_amount
        
        # Random payment type
        payment_types = ["CASH", "UPI", "CREDIT", "SPLIT"]
        payment_method = random.choice(payment_types)
        
        # Payment details
        cash_amount = 0
        upi_amount = 0
        upi_reference = ""
        credit_amount = 0
        payment_status = "PAID"
        
        if payment_method == "CASH":
            cash_amount = total_amount
        elif payment_method == "UPI":
            upi_amount = total_amount
            upi_reference = f"UPI{random.randint(100000, 999999)}"
        elif payment_method == "CREDIT":
            # Only allow credit for non-walk-in customers
            if customer_name == "Walk-in Customer":
                payment_method = "CASH"
                cash_amount = total_amount
            else:
                credit_amount = total_amount
                payment_status = "CREDIT"
        elif payment_method == "SPLIT":
            # Random split between cash and UPI
            cash_amount = round(total_amount * random.uniform(0.3, 0.7), 2)
            upi_amount = round(total_amount - cash_amount, 2)
            upi_reference = f"UPI{random.randint(100000, 999999)}"
        
        # Insert invoice record
        try:
            cursor.execute(
                """
                INSERT INTO invoices
                (invoice_number, customer_id, subtotal, tax_amount, total_amount, 
                payment_method, payment_status, cash_amount, upi_amount, upi_reference, 
                credit_amount, invoice_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    invoice_number,
                    customer_id,
                    subtotal,
                    tax_amount,
                    total_amount,
                    payment_method,
                    payment_status,
                    cash_amount,
                    upi_amount,
                    upi_reference if payment_method == "UPI" or payment_method == "SPLIT" else "",
                    credit_amount,
                    sale_date.strftime('%Y-%m-%d %H:%M:%S')
                )
            )
            
            invoice_id = cursor.lastrowid
            
            # Insert invoice items
            for item in invoice_items:
                cursor.execute(
                    """
                    INSERT INTO invoice_items
                    (invoice_id, product_id, quantity, price_per_unit, 
                    tax_percentage, total_price)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        invoice_id,
                        item['product_id'],
                        item['quantity'],
                        item['price_per_unit'],
                        item['tax_percentage'],
                        item['total_price']
                    )
                )
            
            # Add customer transaction for credit sales
            if payment_method == "CREDIT":
                try:
                    cursor.execute(
                        """
                        INSERT INTO customer_transactions
                        (customer_id, amount, transaction_type, reference_id, notes)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            customer_id,
                            -total_amount,  # Negative amount for credit (customer owes)
                            "CREDIT_SALE",
                            invoice_id,
                            f"Credit sale - Invoice #{invoice_number}"
                        )
                    )
                except Exception as e:
                    # If customer_transactions table doesn't exist, just log and continue
                    print(f"Note: Couldn't add customer transaction: {e}")
            
            print(f"Added invoice {invoice_number} for customer ID {customer_id}")
        except Exception as e:
            print(f"Error adding invoice {invoice_number}: {e}")
    
    conn.commit()

def add_expense_data():
    """Add test data for expenses functionality"""
    conn = connect_db()
    cursor = conn.cursor()
    
    print("Adding expense test data...")
    
    # Common expense categories
    expense_categories = [
        "Rent", "Electricity", "Wages", "Transportation", 
        "Office Supplies", "Marketing", "Maintenance", "Miscellaneous"
    ]
    
    # Generate expenses for the last 90 days
    today = datetime.date.today()
    
    # Insert 20 test expenses
    for i in range(20):
        # Random date within last 90 days
        expense_date = today - datetime.timedelta(days=random.randint(0, 90))
        
        # Random category
        category = random.choice(expense_categories)
        
        # Random amount based on category
        if category == "Rent":
            amount = random.uniform(5000, 8000)
        elif category == "Electricity":
            amount = random.uniform(800, 2500)
        elif category == "Wages":
            amount = random.uniform(3000, 7000)
        elif category == "Transportation":
            amount = random.uniform(500, 2000)
        else:
            amount = random.uniform(100, 1500)
        
        # Round to 2 decimal places
        amount = round(amount, 2)
        
        # Random description
        descriptions = {
            "Rent": ["Monthly shop rent", "Warehouse rent payment", "Store space rent"],
            "Electricity": ["Monthly electricity bill", "Power bill payment", "Electricity charges"],
            "Wages": ["Staff salary", "Employee wages", "Labor payment", "Temporary worker payment"],
            "Transportation": ["Delivery charges", "Transport cost", "Vehicle fuel", "Shipping expenses"],
            "Office Supplies": ["Stationery purchase", "Office items", "Paper and pens", "Printer ink"],
            "Marketing": ["Advertising expense", "Promotion material", "Marketing campaign", "Signboard printing"],
            "Maintenance": ["Shop repairs", "Equipment maintenance", "Computer servicing", "AC repair"],
            "Miscellaneous": ["Miscellaneous expense", "Other expenses", "General purchases", "Unclassified expense"]
        }
        
        description = random.choice(descriptions.get(category, ["General expense"]))
        
        try:
            cursor.execute(
                """
                INSERT INTO expenses
                (expense_date, category, amount, description)
                VALUES (?, ?, ?, ?)
                """,
                (
                    expense_date.strftime('%Y-%m-%d'),
                    category,
                    amount,
                    description
                )
            )
            print(f"Added {category} expense of ₹{amount:.2f} on {expense_date}")
        except Exception as e:
            print(f"Error adding expense: {e}")
    
    conn.commit()

def main():
    """Main function to run all test data generators"""
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file {DB_PATH} not found. Make sure the POS system is initialized.")
        return
    
    print("=======================================")
    print("POS System Test Data Generator")
    print("=======================================")
    
    # Add inventory test data for alerts
    add_inventory_test_data()
    
    # Add sales data
    add_sales_data()
    
    # Add expense data
    add_expense_data()
    
    print("=======================================")
    print("Test data generation complete!")
    print("=======================================")

if __name__ == "__main__":
    main()