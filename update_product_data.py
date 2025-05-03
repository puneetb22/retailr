#!/usr/bin/env python3

with open('ui/inventory_management.py', 'r') as file:
    content = file.read()

# Update the product_tree columns definition
old_columns = """        self.product_tree = ttk.Treeview(tree_frame, 
                                      columns=("ID", "Code", "Name", "Vendor", "HSN", 
                                              "Wholesale", "Retail", "Tax", "Category"),
                                      show="headings",
                                      yscrollcommand=scrollbar.set)"""

new_columns = """        self.product_tree = ttk.Treeview(tree_frame, 
                                      columns=("ID", "Code", "Name", "Vendor", "HSN", 
                                              "Wholesale", "Retail", "Tax", "Category",
                                              "Manufacturer", "Unit"),
                                      show="headings",
                                      yscrollcommand=scrollbar.set)"""

content = content.replace(old_columns, new_columns)

# Add new column headings
old_headings = """        self.product_tree.heading("Tax", text="Tax %")
        self.product_tree.heading("Category", text="Category")"""

new_headings = """        self.product_tree.heading("Tax", text="Tax %")
        self.product_tree.heading("Category", text="Category")
        self.product_tree.heading("Manufacturer", text="Manufacturer")
        self.product_tree.heading("Unit", text="Unit")"""

content = content.replace(old_headings, new_headings)

# Add column widths for the new columns
old_widths = """        self.product_tree.column("Tax", width=80, minwidth=60)
        self.product_tree.column("Category", width=120, minwidth=100)"""

new_widths = """        self.product_tree.column("Tax", width=80, minwidth=60)
        self.product_tree.column("Category", width=120, minwidth=100)
        self.product_tree.column("Manufacturer", width=120, minwidth=100)
        self.product_tree.column("Unit", width=80, minwidth=60)"""

content = content.replace(old_widths, new_widths)

# Write updated file
with open('ui/inventory_management.py', 'w') as file:
    file.write(content)

print("Updated product tree columns successfully!")