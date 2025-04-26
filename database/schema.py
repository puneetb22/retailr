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
            email TEXT,
            address TEXT,
            village TEXT,
            gstin TEXT,
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
            upi_reference TEXT,
            credit_amount REAL DEFAULT 0,
            invoice_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_path TEXT,
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
    """,
    
    "batches": """
        CREATE TABLE batches (
            id INTEGER PRIMARY KEY,
            product_id INTEGER NOT NULL,
            batch_number TEXT,
            quantity INTEGER NOT NULL DEFAULT 0,
            manufacturing_date DATE,
            expiry_date DATE,
            purchase_date DATE DEFAULT CURRENT_TIMESTAMP,
            cost_price REAL NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        )
    """,
    
    "inventory_movements": """
        CREATE TABLE inventory_movements (
            id INTEGER PRIMARY KEY,
            product_id INTEGER NOT NULL,
            batch_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            movement_type TEXT NOT NULL,
            reference_id INTEGER,
            movement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (batch_id) REFERENCES batches(id)
        )
    """,
    
    "sales": """
        CREATE TABLE sales (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            invoice_number TEXT UNIQUE NOT NULL,
            subtotal REAL NOT NULL,
            discount REAL DEFAULT 0,
            tax REAL DEFAULT 0,
            cgst REAL DEFAULT 0,
            sgst REAL DEFAULT 0,
            total REAL NOT NULL,
            payment_type TEXT NOT NULL,
            payment_reference TEXT,
            sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """,
    
    "sale_items": """
        CREATE TABLE sale_items (
            id INTEGER PRIMARY KEY,
            sale_id INTEGER NOT NULL,
            product_id INTEGER,
            product_name TEXT NOT NULL,
            hsn_code TEXT,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            discount_percent REAL DEFAULT 0,
            tax_rate REAL DEFAULT 0,
            tax_amount REAL DEFAULT 0,
            total REAL NOT NULL,
            FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """,
    
    "payment_splits": """
        CREATE TABLE payment_splits (
            id INTEGER PRIMARY KEY,
            sale_id INTEGER NOT NULL,
            cash_amount REAL DEFAULT 0,
            upi_amount REAL DEFAULT 0,
            upi_reference TEXT,
            FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE
        )
    """,
    
    "customer_transactions": """
        CREATE TABLE customer_transactions (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            transaction_type TEXT NOT NULL,
            reference_id INTEGER,
            transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
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
        {"key": "version", "value": "1.0.0"},
        {"key": "product_categories", "value": "Fertilizers,Pesticides,Seeds,Equipment,Other"}, 
        {"key": "vendors", "value": "Mahindra Agri,IFFCO,Rallis India,UPL Limited,Syngenta,Bayer CropScience,Godrej Agrovet"}
    ],
    
    "customers": [
        {
            "name": "Walk-in Customer",
            "phone": "",
            "email": "",
            "address": "",
            "village": "",
            "gstin": "",
            "credit_limit": 0
        },
        {
            "name": "Prakash Bhosle",
            "phone": "9876543210",
            "email": "prakash@example.com",
            "address": "123 Farmer's Colony",
            "village": "Nashik",
            "gstin": "27ABCPB1234A1Z5",
            "credit_limit": 5000
        },
        {
            "name": "Sanjay Patil",
            "phone": "8765432109",
            "email": "sanjay@example.com",
            "address": "456 Agriculture Road",
            "village": "Nanded",
            "gstin": "27AADCP5678B1Z7",
            "credit_limit": 2000
        }
    ],
    
    "products": [
        {
            "product_code": "FERT001",
            "name": "Urea Fertilizer",
            "category": "Fertilizers",
            "vendor": "IFFCO",
            "hsn_code": "3102",
            "description": "Nitrogen-rich fertilizer",
            "wholesale_price": 450,
            "selling_price": 500,
            "tax_percentage": 5
        },
        {
            "product_code": "PEST001",
            "name": "General Insecticide",
            "category": "Pesticides",
            "vendor": "Rallis India",
            "hsn_code": "3808",
            "description": "Broad-spectrum insecticide",
            "wholesale_price": 320,
            "selling_price": 380,
            "tax_percentage": 12
        },
        {
            "product_code": "SEED001",
            "name": "BT Cotton Seeds",
            "category": "Seeds",
            "vendor": "Mahindra Agri",
            "hsn_code": "1207",
            "description": "High yield cotton seeds (1 kg package)",
            "wholesale_price": 850,
            "selling_price": 950,
            "tax_percentage": 5
        },
        {
            "product_code": "EQUIP001",
            "name": "Hand Sprayer",
            "category": "Equipment",
            "vendor": "UPL Limited",
            "hsn_code": "8424",
            "description": "Manual pesticide sprayer",
            "wholesale_price": 750,
            "selling_price": 900,
            "tax_percentage": 18
        }
    ],
    
    "batches": [
        {
            "product_id": 1,
            "batch_number": "F001B001",
            "quantity": 50,
            "manufacturing_date": (datetime.datetime.now() - datetime.timedelta(days=90)).strftime('%Y-%m-%d'),
            "expiry_date": (datetime.datetime.now() + datetime.timedelta(days=365)).strftime('%Y-%m-%d'),
            "purchase_date": (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d'),
            "cost_price": 450
        },
        {
            "product_id": 2,
            "batch_number": "P001B001",
            "quantity": 30,
            "manufacturing_date": (datetime.datetime.now() - datetime.timedelta(days=60)).strftime('%Y-%m-%d'),
            "expiry_date": (datetime.datetime.now() + datetime.timedelta(days=730)).strftime('%Y-%m-%d'),
            "purchase_date": (datetime.datetime.now() - datetime.timedelta(days=20)).strftime('%Y-%m-%d'),
            "cost_price": 320
        },
        {
            "product_id": 3,
            "batch_number": "S001B001",
            "quantity": 15,
            "manufacturing_date": (datetime.datetime.now() - datetime.timedelta(days=120)).strftime('%Y-%m-%d'),
            "expiry_date": (datetime.datetime.now() + datetime.timedelta(days=365*2)).strftime('%Y-%m-%d'),
            "purchase_date": (datetime.datetime.now() - datetime.timedelta(days=15)).strftime('%Y-%m-%d'),
            "cost_price": 850
        },
        {
            "product_id": 4,
            "batch_number": "E001B001",
            "quantity": 10,
            "manufacturing_date": (datetime.datetime.now() - datetime.timedelta(days=180)).strftime('%Y-%m-%d'),
            "expiry_date": (datetime.datetime.now() + datetime.timedelta(days=365*5)).strftime('%Y-%m-%d'),
            "purchase_date": (datetime.datetime.now() - datetime.timedelta(days=10)).strftime('%Y-%m-%d'),
            "cost_price": 750
        }
    ]
}
