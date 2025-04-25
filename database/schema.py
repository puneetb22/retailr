"""
Database schema for POS system
Defines table structure and initial data
"""

import datetime

# Define table schemas
DB_SCHEMA = {
    "settings": """
        CREATE TABLE settings (
            id INTEGER PRIMARY KEY,
            key TEXT UNIQUE NOT NULL,
            value TEXT
        )
    """,
    
    "products": """
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            product_code TEXT UNIQUE,
            name TEXT NOT NULL,
            vendor TEXT,
            hsn_code TEXT,
            category TEXT,
            description TEXT,
            wholesale_price REAL NOT NULL,
            selling_price REAL NOT NULL,
            tax_percentage REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,
    
    "inventory": """
        CREATE TABLE inventory (
            id INTEGER PRIMARY KEY,
            product_id INTEGER NOT NULL,
            batch_number TEXT,
            quantity INTEGER NOT NULL DEFAULT 0,
            manufacturing_date DATE,
            expiry_date DATE,
            purchase_date DATE,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        )
    """,
    
    "customers": """
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            credit_limit REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,
    
    "invoices": """
        CREATE TABLE invoices (
            id INTEGER PRIMARY KEY,
            invoice_number TEXT UNIQUE NOT NULL,
            customer_id INTEGER,
            subtotal REAL NOT NULL,
            discount_amount REAL DEFAULT 0,
            tax_amount REAL DEFAULT 0,
            total_amount REAL NOT NULL,
            payment_method TEXT,
            payment_status TEXT DEFAULT 'PAID',
            cash_amount REAL DEFAULT 0,
            upi_amount REAL DEFAULT 0,
            credit_amount REAL DEFAULT 0,
            invoice_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """,
    
    "invoice_items": """
        CREATE TABLE invoice_items (
            id INTEGER PRIMARY KEY,
            invoice_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            batch_number TEXT,
            quantity INTEGER NOT NULL,
            price_per_unit REAL NOT NULL,
            discount_percentage REAL DEFAULT 0,
            tax_percentage REAL DEFAULT 0,
            total_price REAL NOT NULL,
            FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """,
    
    "expenses": """
        CREATE TABLE expenses (
            id INTEGER PRIMARY KEY,
            expense_date DATE NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,
    
    "inventory_transactions": """
        CREATE TABLE inventory_transactions (
            id INTEGER PRIMARY KEY,
            product_id INTEGER NOT NULL,
            batch_number TEXT,
            quantity INTEGER NOT NULL,
            transaction_type TEXT NOT NULL,
            reference_id INTEGER,
            notes TEXT,
            transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """
}

# Initial data to populate the database
INITIAL_DATA = {
    "settings": [
        {"key": "shop_name", "value": "Agritech Products Shop"},
        {"key": "shop_address", "value": "Main Road, Maharashtra"},
        {"key": "shop_phone", "value": "+91 1234567890"},
        {"key": "shop_gst", "value": "27AABCU9603R1ZX"},
        {"key": "invoice_prefix", "value": "AGT"},
        {"key": "invoice_template", "value": "default"},
        {"key": "low_stock_threshold", "value": "10"},
        {"key": "version", "value": "1.0.0"}
    ],
    
    "customers": [
        {
            "name": "Walk-in Customer",
            "phone": "",
            "address": "",
            "credit_limit": 0
        }
    ]
}
