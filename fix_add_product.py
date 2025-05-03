#!/usr/bin/env python3

with open('ui/inventory_management.py', 'r') as file:
    content = file.read()

# Add debug output for product_data
old_product_insert = """                # Insert product
                product_id = self.controller.db.insert("products", product_data)"""

new_product_insert = """                # Insert product
                print(f"Inserting product data: {product_data}")
                product_id = self.controller.db.insert("products", product_data)"""

content = content.replace(old_product_insert, new_product_insert)

# Update the save_product function's error handling to include the error message
old_error_handling = """            except Exception as e:
                # Roll back in case of errors
                self.controller.db.rollback()
                messagebox.showerror("Error", f"Failed to add product: {e}")"""

new_error_handling = """            except Exception as e:
                # Roll back in case of errors
                self.controller.db.rollback()
                error_details = str(e)
                print(f"Error adding product: {error_details}")
                messagebox.showerror("Error", f"Failed to add product: {error_details}")"""

content = content.replace(old_error_handling, new_error_handling)

# Write updated file
with open('ui/inventory_management.py', 'w') as file:
    file.write(content)

print("Added debugging to product insertion!")