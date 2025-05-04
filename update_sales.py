"""
Update the sales.py file with proper customer search functionality
"""

import os
import re

def update_sales_file():
    # Read the current sales.py file
    with open("ui/sales.py", "r") as f:
        content = f.read()
    
    # Update customer search panel
    # 1. Update the setup_customer_search_panel method
    pattern = r"def setup_customer_search_panel\(self, parent\):.*?self\.customer_var = tk\.StringVar\(\)\n\s+self\.customer_var\.set\(.*?\)"
    replacement = """def setup_customer_search_panel(self, parent):
        \"\"\"Setup the customer search panel with dropdown and buttons\"\"\"
        # Container frame
        container = tk.Frame(parent, bg=COLORS["bg_primary"])
        container.pack(fill=tk.X)
        
        # Customer label
        customer_label = tk.Label(container, 
                                text="Customer:",
                                font=FONTS["regular_bold"],
                                bg=COLORS["bg_primary"],
                                fg=COLORS["text_primary"])
        customer_label.pack(side=tk.LEFT, padx=(5, 10))
        
        # Customer search/combobox frame
        self.customer_var = tk.StringVar()
        self.customer_var.set("")  # Empty by default, no Walk-in Customer"""
    
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # 2. Update load_customers_for_dropdown at the beginning of the file
    pattern = r"def load_customers_for_dropdown\(self\):.*?self\.customer_combo\['values'\] = customer_list"
    replacement = """def load_customers_for_dropdown(self):
        \"\"\"Load customer list for dropdown\"\"\"
        db = self.controller.db
        query = \"\"\"
            SELECT id, name, phone FROM customers
            ORDER BY name
            LIMIT 50
        \"\"\"
        customers = db.fetchall(query)
        
        # Format customer list for combobox - no Walk-in customer by default
        customer_list = []
        self.customer_data = {}
        
        for i, customer in enumerate(customers):
            display_text = f"{customer[1]} ({customer[2] if customer[2] else 'No phone'})"
            customer_list.append(display_text)
            self.customer_data[i] = {"id": customer[0], "name": customer[1], "phone": customer[2] or ""}
        
        # Update combobox values
        self.customer_combo['values'] = customer_list"""
    
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # 3. Update filter_customers at the beginning of the file
    pattern = r"def filter_customers\(self, event\):.*?if len\(customer_list\) > 1:.*?self\.customer_combo\.event_generate\('<Down>'\)"
    replacement = """def filter_customers(self, event):
        \"\"\"Filter customers based on input in combobox\"\"\"
        search_term = self.customer_var.get().strip().lower()
        
        # Clear placeholder text if it exists
        if search_term == "search customers...":
            self.customer_combo.delete(0, tk.END)
            return
            
        # Skip searching if input is too short
        if len(search_term) < 2:
            return
        
        # Get all customers matching the search term
        db = self.controller.db
        query = \"\"\"
            SELECT id, name, phone FROM customers
            WHERE LOWER(name) LIKE ? OR LOWER(phone) LIKE ?
            ORDER BY name
            LIMIT 50
        \"\"\"
        
        # Use % for wildcard search
        search_pattern = f"%{search_term}%"
        customers = db.fetchall(query, (search_pattern, search_pattern))
        
        # Format customer list for combobox (no Walk-in Customer in dropdown)
        customer_list = []
        self.customer_data = {}
        
        for i, customer in enumerate(customers):
            display_text = f"{customer[1]} ({customer[2] if customer[2] else 'No phone'})"
            customer_list.append(display_text)
            self.customer_data[i] = {"id": customer[0], "name": customer[1], "phone": customer[2] or ""}
        
        # Update combobox values
        self.customer_combo['values'] = customer_list
        
        # If there are matching customers, show the dropdown
        if customer_list:
            self.customer_combo.event_generate('<Down>')"""
    
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # 4. Remove duplicate methods at the end
    pattern = r"\n\s+def load_customers_for_dropdown\(self\):.*?def on_show\(self\):"
    replacement = "\n    def on_show(self):"
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # 5. Update the combobox to handle placeholder text
    pattern = r"# Create autocomplete combobox.*?self\.customer_combo\.pack\(side=tk\.LEFT, padx=5\)"
    replacement = """# Create autocomplete combobox
        self.customer_combo = ttk.Combobox(container, 
                                         textvariable=self.customer_var,
                                         font=FONTS["regular"],
                                         width=30)
        self.customer_combo.pack(side=tk.LEFT, padx=5)
        
        # Set default placeholder text
        if not self.customer_var.get():
            self.customer_combo.insert(0, "Search customers...")"""
    
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Save the updated content
    with open("ui/sales.py.new", "w") as f:
        f.write(content)
    
    # Replace the old file
    os.rename("ui/sales.py.new", "ui/sales.py")
    
    print("Sales.py updated successfully!")

if __name__ == "__main__":
    update_sales_file()