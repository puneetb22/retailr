#!/usr/bin/env python3

with open('ui/inventory_management.py', 'r') as file:
    content = file.read()

# Now we need to update the fields array in the edit_product function
old_fields = """        # Create form fields
        fields = [
            {"name": "id", "label": "Product ID:", "required": False, "type": "entry", "readonly": True},
            {"name": "product_code", "label": "Product Code:", "required": False, "type": "entry", "readonly": False},
            {"name": "name", "label": "Product Name:", "required": True, "type": "entry"},
            {"name": "vendor", "label": "Vendor:", "required": False, "type": "combobox", "values": vendors},
            {"name": "hsn_code", "label": "HSN Code:", "required": False, "type": "combobox", "values": hsn_codes},
            {"name": "category", "label": "Category:", "required": False, "type": "combobox", "values": categories},
            {"name": "wholesale_price", "label": "Wholesale Price:", "required": True, "type": "entry"},
            {"name": "selling_price", "label": "Selling Price:", "required": True, "type": "entry"},
            {"name": "tax_percentage", "label": "Tax Percentage:", "required": False, "type": "entry"}
        ]"""

# Create unit options list and updated fields
new_fields = """        # Create unit options list
        unit_options = ["Kilogram (kg)", "Gram (g)", "Quintal (100 kg)", "Metric Tonne (MT)", 
                        "Litre (L)", "Millilitre (ml)", "Piece (pc)", "Packet", "Bag", 
                        "Box", "Bottle", "Sachet", "Dozen"]
                        
        # Create form fields
        fields = [
            {"name": "id", "label": "Product ID:", "required": False, "type": "entry", "readonly": True},
            {"name": "product_code", "label": "Product Code:", "required": False, "type": "entry", "readonly": False},
            {"name": "name", "label": "Product Name:", "required": True, "type": "entry"},
            {"name": "manufacturer", "label": "Manufacturer Name:", "required": False, "type": "entry"},
            {"name": "vendor", "label": "Vendor:", "required": False, "type": "combobox", "values": vendors},
            {"name": "hsn_code", "label": "HSN Code:", "required": False, "type": "combobox", "values": hsn_codes},
            {"name": "category", "label": "Category:", "required": False, "type": "combobox", "values": categories},
            {"name": "unit", "label": "Unit:", "required": False, "type": "combobox", "values": unit_options},
            {"name": "wholesale_price", "label": "Wholesale Price:", "required": True, "type": "entry"},
            {"name": "selling_price", "label": "Selling Price:", "required": True, "type": "entry"},
            {"name": "tax_percentage", "label": "Tax Percentage:", "required": False, "type": "entry"}
        ]"""

content = content.replace(old_fields, new_fields)

# Update the set initial value code to handle manufacturer and unit fields
old_initial_values = """                # Set initial value from product data
                if field["name"] == "id":
                    entry_vars[field["name"]].set(product[0])  # ID
                elif field["name"] == "product_code":
                    entry_vars[field["name"]].set(product[1])  # Product Code
                elif field["name"] == "name":
                    entry_vars[field["name"]].set(product[2])  # Name
                elif field["name"] == "wholesale_price":
                    entry_vars[field["name"]].set(product[5])  # Wholesale Price
                elif field["name"] == "selling_price":
                    entry_vars[field["name"]].set(product[6])  # Selling Price
                elif field["name"] == "tax_percentage":
                    entry_vars[field["name"]].set(product[7])  # Tax Percentage"""

new_initial_values = """                # Set initial value from product data
                if field["name"] == "id":
                    entry_vars[field["name"]].set(product[0])  # ID
                elif field["name"] == "product_code":
                    entry_vars[field["name"]].set(product[1])  # Product Code
                elif field["name"] == "name":
                    entry_vars[field["name"]].set(product[2])  # Name
                elif field["name"] == "wholesale_price":
                    entry_vars[field["name"]].set(product[5])  # Wholesale Price
                elif field["name"] == "selling_price":
                    entry_vars[field["name"]].set(product[6])  # Selling Price
                elif field["name"] == "tax_percentage":
                    entry_vars[field["name"]].set(product[7])  # Tax Percentage
                elif field["name"] == "manufacturer":
                    entry_vars[field["name"]].set(product[9] or "")  # Manufacturer
                elif field["name"] == "unit":
                    entry_vars[field["name"]].set(product[10] or "")  # Unit"""

content = content.replace(old_initial_values, new_initial_values)

# Update the save_product function in edit_product to include manufacturer and unit
old_save_product_data = """                # Construct product data
                product_data = {
                    "name": entry_vars["name"].get(),
                    "vendor": entry_vars["vendor"].get(),
                    "hsn_code": entry_vars["hsn_code"].get(),
                    "category": entry_vars["category"].get(),
                    "wholesale_price": float(wholesale_price),
                    "selling_price": float(selling_price),
                    "tax_percentage": float(tax_percentage)
                }"""

new_save_product_data = """                # Construct product data
                product_data = {
                    "name": entry_vars["name"].get(),
                    "manufacturer": entry_vars["manufacturer"].get(),
                    "vendor": entry_vars["vendor"].get(),
                    "hsn_code": entry_vars["hsn_code"].get(),
                    "category": entry_vars["category"].get(),
                    "unit": entry_vars["unit"].get(),
                    "wholesale_price": float(wholesale_price),
                    "selling_price": float(selling_price),
                    "tax_percentage": float(tax_percentage)
                }"""

content = content.replace(old_save_product_data, new_save_product_data)

# Write updated file
with open('ui/inventory_management.py', 'w') as file:
    file.write(content)

print("Updated edit_product function successfully!")