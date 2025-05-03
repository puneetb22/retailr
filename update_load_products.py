#!/usr/bin/env python3

with open('ui/inventory_management.py', 'r') as file:
    content = file.read()

# Update the load_products function query
old_load_query = """        # Get all products
        query = """
            SELECT id, product_code, name, vendor, hsn_code, 
                   wholesale_price, selling_price, tax_percentage, category
            FROM products
            ORDER BY name
        \"\"\""""

new_load_query = """        # Get all products
        query = """
            SELECT id, product_code, name, vendor, hsn_code, 
                   wholesale_price, selling_price, tax_percentage, category,
                   manufacturer, unit
            FROM products
            ORDER BY name
        \"\"\""""

content = content.replace(old_load_query, new_load_query)

# Update the search_products function query
old_search_query = """        # Get filtered products
        query = """
            SELECT id, product_code, name, vendor, hsn_code, 
                   wholesale_price, selling_price, tax_percentage, category
            FROM products
            WHERE LOWER(name) LIKE ? OR 
                  LOWER(product_code) LIKE ? OR
                  LOWER(vendor) LIKE ?"""

new_search_query = """        # Get filtered products
        query = """
            SELECT id, product_code, name, vendor, hsn_code, 
                   wholesale_price, selling_price, tax_percentage, category,
                   manufacturer, unit
            FROM products
            WHERE LOWER(name) LIKE ? OR 
                  LOWER(product_code) LIKE ? OR
                  LOWER(vendor) LIKE ? OR
                  LOWER(manufacturer) LIKE ?"""

content = content.replace(old_search_query, new_search_query)

# Update the search parameters
old_search_params = """        params = (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%")"""
new_search_params = """        params = (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%")"""

content = content.replace(old_search_params, new_search_params)

# Write updated file
with open('ui/inventory_management.py', 'w') as file:
    file.write(content)

print("Updated load_products and search_products functions successfully!")