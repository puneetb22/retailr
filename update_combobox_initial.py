#!/usr/bin/env python3

with open('ui/inventory_management.py', 'r') as file:
    content = file.read()

# Update the initial value for comboboxes to handle unit field
old_combobox_initial = """                # Set initial value from product data
                if field["name"] == "vendor":
                    entry_vars[field["name"]].set(product[3] or "")  # Vendor
                elif field["name"] == "hsn_code":
                    entry_vars[field["name"]].set(product[4] or "")  # HSN Code
                elif field["name"] == "category":
                    entry_vars[field["name"]].set(product[8] or "")  # Category"""

new_combobox_initial = """                # Set initial value from product data
                if field["name"] == "vendor":
                    entry_vars[field["name"]].set(product[3] or "")  # Vendor
                elif field["name"] == "hsn_code":
                    entry_vars[field["name"]].set(product[4] or "")  # HSN Code
                elif field["name"] == "category":
                    entry_vars[field["name"]].set(product[8] or "")  # Category
                elif field["name"] == "unit":
                    entry_vars[field["name"]].set(product[10] or "")  # Unit"""

content = content.replace(old_combobox_initial, new_combobox_initial)

# Write updated file
with open('ui/inventory_management.py', 'w') as file:
    file.write(content)

print("Updated combobox initial values successfully!")