"""
Product Management UI for POS system
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import datetime
from assets.styles import COLORS, FONTS, STYLES

class ProductManagementFrame(tk.Frame):
    """Product management with add, edit, search, and delete functionality"""
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=COLORS["bg_primary"])
        self.controller = controller
        
        # Keyboard navigation variables
        self.current_focus = None  # Current focus area: 'products', 'buttons', 'search'
        self.selected_product_item = -1
        
        # Bind keyboard events
        self.bind("<Key>", self.handle_key_event)
        
        # Create layout
        self.create_layout()
        
        # Load products
        self.load_products()
    
    def create_layout(self):
        """Create the product management layout"""
        # Header
        header_frame = tk.Frame(self, bg=COLORS["bg_primary"], pady=10)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        
        title = tk.Label(header_frame, 
                        text="Product Management",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"])
        title.pack(side=tk.LEFT, padx=20)
        
        # Search frame
        search_frame = tk.Frame(self, bg=COLORS["bg_primary"], pady=10, padx=20)
        search_frame.pack(side=tk.TOP, fill=tk.X)
        
        search_label = tk.Label(search_frame, 
                               text="Search:",
                               font=FONTS["regular"],
                               bg=COLORS["bg_primary"],
                               fg=COLORS["text_primary"])
        search_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.search_products())
        
        search_entry = tk.Entry(search_frame, 
                               textvariable=self.search_var,
                               font=FONTS["regular"],
                               width=30)
        search_entry.pack(side=tk.LEFT)
        
        # Add product button
        add_btn = tk.Button(search_frame,
                          text="Add New Product",
                          font=FONTS["regular"],
                          bg=COLORS["primary"],
                          fg=COLORS["text_white"],
                          padx=15,
                          pady=5,
                          cursor="hand2",
                          command=self.add_product)
        add_btn.pack(side=tk.RIGHT)
        
        # Products treeview
        tree_frame = tk.Frame(self)
        tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure treeview styles
        style = ttk.Style()
        style.configure("Treeview", 
                        background=COLORS["bg_white"],
                        foreground=COLORS["text_primary"],
                        rowheight=25,
                        fieldbackground=COLORS["bg_white"],
                        font=FONTS["regular"])
        style.configure("Treeview.Heading", 
                        font=FONTS["regular_bold"],
                        background=COLORS["bg_secondary"],
                        foreground=COLORS["text_primary"])
        
        # Create treeview
        self.product_tree = ttk.Treeview(tree_frame, 
                                        columns=("ID", "Code", "Name", "Vendor", "HSN", 
                                                "Wholesale", "Retail", "Tax", "Category"),
                                        show="headings",
                                        yscrollcommand=scrollbar.set)
        
        # Configure scrollbar
        scrollbar.config(command=self.product_tree.yview)
        
        # Define columns
        self.product_tree.heading("ID", text="ID")
        self.product_tree.heading("Code", text="Product Code")
        self.product_tree.heading("Name", text="Product Name")
        self.product_tree.heading("Vendor", text="Vendor")
        self.product_tree.heading("HSN", text="HSN Code")
        self.product_tree.heading("Wholesale", text="Wholesale Price")
        self.product_tree.heading("Retail", text="Retail Price")
        self.product_tree.heading("Tax", text="Tax %")
        self.product_tree.heading("Category", text="Category")
        
        # Set column widths
        self.product_tree.column("ID", width=50)
        self.product_tree.column("Code", width=100)
        self.product_tree.column("Name", width=200)
        self.product_tree.column("Vendor", width=150)
        self.product_tree.column("HSN", width=100)
        self.product_tree.column("Wholesale", width=120)
        self.product_tree.column("Retail", width=120)
        self.product_tree.column("Tax", width=80)
        self.product_tree.column("Category", width=100)
        
        self.product_tree.pack(fill=tk.BOTH, expand=True)
        
        # Binding for double-click to edit
        self.product_tree.bind("<Double-1>", self.edit_product)
        
        # Right-click menu for additional options
        self.context_menu = tk.Menu(self, tearoff=0, bg=COLORS["bg_white"], font=FONTS["small"])
        self.context_menu.add_command(label="Edit Product", command=self.edit_product)
        self.context_menu.add_command(label="Delete Product", command=self.delete_product)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Add Stock", command=self.add_stock)
        
        # Bind right-click to show menu
        self.product_tree.bind("<Button-3>", self.show_context_menu)
        
        # Action buttons frame
        button_frame = tk.Frame(self, bg=COLORS["bg_primary"], pady=10, padx=20)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Delete product button
        delete_btn = tk.Button(button_frame,
                             text="Delete Product",
                             font=FONTS["regular"],
                             bg=COLORS["danger"],
                             fg=COLORS["text_white"],
                             padx=15,
                             pady=5,
                             cursor="hand2",
                             command=self.delete_product)
        delete_btn.pack(side=tk.RIGHT, padx=5)
        
        # Edit product button
        edit_btn = tk.Button(button_frame,
                           text="Edit Product",
                           font=FONTS["regular"],
                           bg=COLORS["secondary"],
                           fg=COLORS["text_white"],
                           padx=15,
                           pady=5,
                           cursor="hand2",
                           command=self.edit_product)
        edit_btn.pack(side=tk.RIGHT, padx=5)
        
        # Add Stock button
        add_stock_btn = tk.Button(button_frame,
                               text="Add Stock",
                               font=FONTS["regular"],
                               bg=COLORS["primary"],
                               fg=COLORS["text_white"],
                               padx=15,
                               pady=5,
                               cursor="hand2",
                               command=self.add_stock)
        add_stock_btn.pack(side=tk.RIGHT, padx=5)
    
    def load_products(self):
        """Load products from database into treeview"""
        # Clear current items
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        # Get products from database
        query = """
            SELECT id, product_code, name, vendor, hsn_code, 
                   wholesale_price, selling_price, tax_percentage, category
            FROM products
            ORDER BY name
        """
        products = self.controller.db.fetchall(query)
        
        # Insert into treeview
        for product in products:
            self.product_tree.insert("", "end", values=product)
    
    def search_products(self):
        """Search products based on search term"""
        search_term = self.search_var.get().strip().lower()
        
        # Clear current items
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        if not search_term:
            # If search is empty, load all products
            self.load_products()
            return
        
        # Get filtered products
        query = """
            SELECT id, product_code, name, vendor, hsn_code, 
                   wholesale_price, selling_price, tax_percentage, category
            FROM products
            WHERE LOWER(name) LIKE ? OR 
                  LOWER(product_code) LIKE ? OR
                  LOWER(vendor) LIKE ?
            ORDER BY name
        """
        search_pattern = f"%{search_term}%"
        products = self.controller.db.fetchall(query, (search_pattern, search_pattern, search_pattern))
        
        # Insert into treeview
        for product in products:
            self.product_tree.insert("", "end", values=product)
    
    def get_categories(self):
        """Get list of product categories"""
        # Try to get categories from settings first
        query = "SELECT value FROM settings WHERE key = 'product_categories'"
        result = self.controller.db.fetchone(query)
        
        if result and result[0]:
            # Split by comma into a list
            categories = result[0].split(',')
            return categories
        else:
            # Default categories if not found in settings
            return ["Fertilizers", "Pesticides", "Seeds", "Equipment", "Other"]
    
    def get_vendors(self):
        """Get list of vendors"""
        # Try to get from settings
        query = "SELECT value FROM settings WHERE key = 'vendors'"
        result = self.controller.db.fetchone(query)
        
        vendors = []
        if result and result[0]:
            # Split by comma into a list
            vendors = result[0].split(',')
        
        # Also get unique vendors from products table
        query = "SELECT DISTINCT vendor FROM products WHERE vendor IS NOT NULL AND vendor != ''"
        results = self.controller.db.fetchall(query)
        
        for vendor in results:
            if vendor[0] and vendor[0] not in vendors:
                vendors.append(vendor[0])
                
        return vendors
    
    def add_product(self):
        """Open dialog to add a new product"""
        # Create product dialog window
        product_dialog = tk.Toplevel(self)
        product_dialog.title("Add New Product")
        product_dialog.geometry("700x700")  # Increased size for combined form
        product_dialog.resizable(False, False)
        product_dialog.configure(bg=COLORS["bg_primary"])
        product_dialog.grab_set()  # Make window modal
        
        # Center the dialog
        product_dialog.update_idletasks()
        width = product_dialog.winfo_width()
        height = product_dialog.winfo_height()
        x = (product_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (product_dialog.winfo_screenheight() // 2) - (height // 2)
        product_dialog.geometry(f"+{x}+{y}")
        
        # Create form
        title = tk.Label(product_dialog, 
                        text="Add New Product",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"])
        title.pack(pady=15)
        
        # Form frame for all fields
        form_frame = tk.Frame(product_dialog, bg=COLORS["bg_primary"], padx=20, pady=10)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a canvas with scrollbar for the form
        canvas = tk.Canvas(form_frame, bg=COLORS["bg_primary"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(form_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS["bg_primary"])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Get categories and vendors
        categories = self.get_categories()
        vendors = self.get_vendors()
        
        # Title for first section
        section1_title = tk.Label(scrollable_frame, 
                                text="Product Details",
                                font=FONTS["subheading"],
                                bg=COLORS["bg_secondary"],
                                fg=COLORS["text_primary"],
                                padx=10,
                                pady=5,
                                width=50)
        section1_title.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        # Create form fields
        fields = [
            {"name": "product_code", "label": "Product Code (Auto-Generated):", "required": False, "type": "entry", "readonly": True},
            {"name": "name", "label": "Product Name:", "required": True, "type": "entry"},
            {"name": "vendor", "label": "Vendor:", "required": False, "type": "combobox", "values": vendors},
            {"name": "hsn_code", "label": "HSN Code:", "required": False, "type": "entry"},
            {"name": "category", "label": "Category:", "required": False, "type": "combobox", "values": categories},
            {"name": "wholesale_price", "label": "Wholesale Price:", "required": True, "type": "entry"},
            {"name": "selling_price", "label": "Selling Price:", "required": True, "type": "entry"},
            {"name": "tax_percentage", "label": "Tax Percentage:", "required": False, "type": "entry"}
        ]
        
        # Inventory fields (now in the same form)
        # Title for second section
        section2_title = tk.Label(scrollable_frame, 
                                text="Initial Stock Information",
                                font=FONTS["subheading"],
                                bg=COLORS["bg_secondary"],
                                fg=COLORS["text_primary"],
                                padx=10,
                                pady=5)
        section2_title.grid(row=len(fields)+1, column=0, columnspan=2, sticky="ew", pady=(20, 10))
        
        inventory_fields = [
            {"name": "initial_stock", "label": "Initial Stock Quantity:", "required": False, "type": "entry"},
            {"name": "batch_number", "label": "Batch Number:", "required": False, "type": "entry"},
            {"name": "manufacturing_date", "label": "Manufacturing Date (YYYY-MM-DD):", "required": False, "type": "entry"},
            {"name": "expiry_date", "label": "Expiry Date (YYYY-MM-DD):", "required": False, "type": "entry"}
        ]
        
        # Variables to store entry values
        entry_vars = {}
        entries = {}
        
        # Create labels and entries for product details
        row_index = 1  # Start after section title
        for i, field in enumerate(fields):
            # Label
            label = tk.Label(scrollable_frame, 
                          text=field["label"],
                          font=FONTS["regular"],
                          bg=COLORS["bg_primary"],
                          fg=COLORS["text_primary"])
            label.grid(row=row_index, column=0, sticky="w", pady=8, padx=10)
            
            # Variable
            var = tk.StringVar()
            entry_vars[field["name"]] = var
            
            # Different types of input fields
            if field["name"] == "product_code":
                # Create disabled entry for product code (will be auto-generated)
                entry = tk.Entry(scrollable_frame, 
                             textvariable=var,
                             font=FONTS["regular"],
                             width=40,
                             state="disabled")
                var.set("(Auto-generated)")
            elif field["type"] == "combobox":
                # Create combobox with values
                entry = ttk.Combobox(scrollable_frame, 
                                  textvariable=var,
                                  font=FONTS["regular"],
                                  width=38,
                                  values=field["values"])
                
                # Add an option to create a new value
                values = list(field["values"])
                if "Add new..." not in values:
                    values.append("Add new...")
                entry["values"] = values
                
                # Bind selection event
                entry.bind("<<ComboboxSelected>>", 
                           lambda event, f=field["name"]: self.handle_combobox_selection(event, f, entry_vars, entries))
                
            else:
                # Create regular entry
                entry = tk.Entry(scrollable_frame, 
                              textvariable=var,
                              font=FONTS["regular"],
                              width=40)
                
            entries[field["name"]] = entry
            entry.grid(row=row_index, column=1, sticky="w", pady=8, padx=10)
            
            # Add asterisk for required fields
            if field["required"]:
                required = tk.Label(scrollable_frame, 
                                  text="*",
                                  font=FONTS["regular"],
                                  bg=COLORS["bg_primary"],
                                  fg=COLORS["danger"])
                required.grid(row=row_index, column=2, sticky="w")
            
            row_index += 1
        
        # Create labels and entries for inventory in the same form
        row_index += 1  # Skip a row after the section title
        for i, field in enumerate(inventory_fields):
            # Label
            label = tk.Label(scrollable_frame, 
                          text=field["label"],
                          font=FONTS["regular"],
                          bg=COLORS["bg_primary"],
                          fg=COLORS["text_primary"])
            label.grid(row=row_index, column=0, sticky="w", pady=8, padx=10)
            
            # Entry
            var = tk.StringVar()
            entry_vars[field["name"]] = var
            
            entry = tk.Entry(scrollable_frame, 
                          textvariable=var,
                          font=FONTS["regular"],
                          width=40)
            entries[field["name"]] = entry
            entry.grid(row=row_index, column=1, sticky="w", pady=8, padx=10)
            
            # Add asterisk for required fields
            if field["required"]:
                required = tk.Label(scrollable_frame, 
                                  text="*",
                                  font=FONTS["regular"],
                                  bg=COLORS["bg_primary"],
                                  fg=COLORS["danger"])
                required.grid(row=row_index, column=2, sticky="w")
            
            row_index += 1
        
        # Set default values
        entry_vars["tax_percentage"].set("0")
        entry_vars["initial_stock"].set("0")
        
        # Buttons frame
        button_frame = tk.Frame(product_dialog, bg=COLORS["bg_primary"], pady=15)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Cancel button
        cancel_btn = tk.Button(button_frame,
                             text="Cancel",
                             font=FONTS["regular"],
                             bg=COLORS["bg_secondary"],
                             fg=COLORS["text_primary"],
                             padx=20,
                             pady=5,
                             cursor="hand2",
                             command=product_dialog.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=20)
        
        # Function to save product
        def save_product():
            # Validate required fields
            for field in fields:
                if field["required"] and not entry_vars[field["name"]].get().strip():
                    messagebox.showerror("Error", f"{field['label']} is required.")
                    return
            
            # Validate numeric fields
            numeric_fields = ["wholesale_price", "selling_price", "tax_percentage", "initial_stock"]
            for field in numeric_fields:
                try:
                    if entry_vars[field].get().strip():
                        float(entry_vars[field].get())
                except ValueError:
                    messagebox.showerror("Error", f"{field} must be a number.")
                    return
            
            # Create product data
            product_data = {}
            for field in fields:
                # Skip product_code as it will be auto-generated
                if field["name"] == "product_code":
                    continue
                # Convert numeric fields to float before storing
                elif field["name"] in ["wholesale_price", "selling_price", "tax_percentage"]:
                    value = entry_vars[field["name"]].get().strip()
                    if value:
                        product_data[field["name"]] = float(value)
                    else:
                        product_data[field["name"]] = 0
                else:
                    product_data[field["name"]] = entry_vars[field["name"]].get().strip()
            
            # Auto-generate product code using full category name
            category = product_data.get("category", "")
            prefix = ""
            if category:
                # Get category name as prefix
                # Define standard prefixes for better readability and consistency
                category_prefixes = {
                    "Seeds": "SEED",
                    "Pesticides": "PESTI",
                    "Fertilizers": "FERTI",
                    "Equipment": "EQUIP",
                    "Tools": "TOOL",
                    "Other": "OTHER"
                }
                
                # Use defined prefix if available, otherwise use the full category name
                if category in category_prefixes:
                    prefix = category_prefixes[category]
                else:
                    # Create prefix from category name (keep it uppercase with no spaces)
                    prefix = ''.join(c for c in category if c.isalnum()).upper()
                    # Ensure prefix isn't too long
                    if len(prefix) > 6:
                        prefix = prefix[:6]
            else:
                # Default prefix if no category
                prefix = "PROD"
            
            # Get the next product number for this category
            query = "SELECT COUNT(*) FROM products WHERE product_code LIKE ?"
            count_result = self.controller.db.fetchone(query, (f"{prefix}%",))
            count = count_result[0] + 1 if count_result and count_result[0] is not None else 1
            
            # Generate code in format: SEED001, PESTI001, etc.
            product_data["product_code"] = f"{prefix}{str(count).zfill(3)}"
            
            # Begin database transaction
            self.controller.db.begin()
            
            try:
                # Insert into database
                product_id = self.controller.db.insert("products", product_data)
                
                if product_id:
                    # Check if we need to add initial stock
                    initial_stock = entry_vars["initial_stock"].get().strip()
                    
                    if initial_stock and float(initial_stock) > 0:
                        batch_number = entry_vars["batch_number"].get().strip()
                        manufacturing_date = entry_vars["manufacturing_date"].get().strip() or None
                        expiry_date = entry_vars["expiry_date"].get().strip() or None
                        
                        # Add to inventory
                        inventory_data = {
                            "product_id": product_id,
                            "batch_number": batch_number,
                            "quantity": int(float(initial_stock)),
                            "manufacturing_date": manufacturing_date,
                            "expiry_date": expiry_date,
                            "purchase_date": datetime.date.today().isoformat()
                        }
                        
                        inventory_id = self.controller.db.insert("inventory", inventory_data)
                        
                        if not inventory_id:
                            # Roll back if inventory insertion fails
                            self.controller.db.rollback()
                            messagebox.showerror("Error", "Failed to add inventory record.")
                            return
                        
                        # Record inventory transaction
                        transaction_data = {
                            "product_id": product_id,
                            "batch_number": batch_number,
                            "quantity": int(float(initial_stock)),
                            "transaction_type": "STOCK_ADD",
                            "notes": "Initial stock on product creation"
                        }
                        
                        self.controller.db.insert("inventory_transactions", transaction_data)
                
                # Save new values for categories and vendors
                current_category = entry_vars["category"].get().strip()
                if current_category and current_category != "Add new..." and current_category not in categories:
                    # Update categories in settings
                    new_categories = ",".join(categories + [current_category])
                    self.controller.db.update("settings", 
                                             {"value": new_categories}, 
                                             "key = 'product_categories'")
                
                current_vendor = entry_vars["vendor"].get().strip()
                if current_vendor and current_vendor != "Add new..." and current_vendor not in vendors:
                    # Get current vendors from settings
                    query = "SELECT value FROM settings WHERE key = 'vendors'"
                    result = self.controller.db.fetchone(query)
                    
                    if result and result[0]:
                        vendor_list = result[0].split(',')
                        if current_vendor not in vendor_list:
                            vendor_list.append(current_vendor)
                            new_vendors = ",".join(vendor_list)
                            self.controller.db.update("settings", 
                                                   {"value": new_vendors}, 
                                                   "key = 'vendors'")
                    else:
                        # Create new vendors setting
                        self.controller.db.insert("settings", {
                            "key": "vendors",
                            "value": current_vendor
                        })
                
                # Commit all changes
                self.controller.db.commit()
                
                messagebox.showinfo("Success", "Product added successfully!")
                product_dialog.destroy()
                self.load_products()  # Refresh product list
                
            except Exception as e:
                # Roll back in case of errors
                self.controller.db.rollback()
                messagebox.showerror("Error", f"Failed to add product: {e}")
        
        # Save button
        save_btn = tk.Button(button_frame,
                           text="Save Product",
                           font=FONTS["regular_bold"],
                           bg=COLORS["primary"],
                           fg=COLORS["text_white"],
                           padx=20,
                           pady=5,
                           cursor="hand2",
                           command=lambda: save_product())
        save_btn.pack(side=tk.RIGHT, padx=5)
        
        # Bind Enter key to save product
        def on_enter_key(event):
            save_product()
        
        product_dialog.bind('<Return>', on_enter_key)
    
    def handle_combobox_selection(self, event, field_name, entry_vars, entries):
        """Handle selection in category or vendor combobox"""
        combobox = event.widget
        selected_value = combobox.get()
        
        if selected_value == "Add new...":
            # Prompt user to enter a new value
            new_value = simpledialog.askstring(
                "Add New", 
                f"Enter new {field_name}:",
                parent=self)
            
            if new_value:
                # Update the combobox values
                values_list = list(combobox["values"])
                values_list.insert(-1, new_value)  # Insert before "Add new..."
                combobox["values"] = values_list
                
                # Set the new value
                entry_vars[field_name].set(new_value)
                
                # If it's a category, update the settings
                if field_name == "category":
                    categories = self.get_categories()
                    if new_value not in categories:
                        categories.append(new_value)
                        new_categories = ",".join(categories)
                        self.controller.db.update("settings", 
                                               {"value": new_categories}, 
                                               "key = 'product_categories'")
            else:
                # If user cancels, set to empty
                entry_vars[field_name].set("")
    
    def edit_product(self, event=None):
        """Open dialog to edit selected product"""
        # Get selected item
        selection = self.product_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a product to edit.")
            return
        
        # Get product ID
        product_id = self.product_tree.item(selection[0])["values"][0]
        
        # Get product data
        query = """
            SELECT * FROM products WHERE id = ?
        """
        product = self.controller.db.fetchone(query, (product_id,))
        
        if not product:
            messagebox.showerror("Error", "Product not found.")
            return
        
        # Create product dialog window
        product_dialog = tk.Toplevel(self)
        product_dialog.title("Edit Product")
        product_dialog.geometry("600x500")
        product_dialog.resizable(False, False)
        product_dialog.configure(bg=COLORS["bg_primary"])
        product_dialog.grab_set()  # Make window modal
        
        # Center the dialog
        product_dialog.update_idletasks()
        width = product_dialog.winfo_width()
        height = product_dialog.winfo_height()
        x = (product_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (product_dialog.winfo_screenheight() // 2) - (height // 2)
        product_dialog.geometry(f"+{x}+{y}")
        
        # Create form
        title = tk.Label(product_dialog, 
                        text="Edit Product",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"])
        title.pack(pady=15)
        
        # Form frame
        form_frame = tk.Frame(product_dialog, bg=COLORS["bg_primary"], padx=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Column names for reference
        columns = [description[0] for description in self.controller.db.cursor.description]
        
        # Create form fields
        fields = [
            {"name": "product_code", "label": "Product Code (Auto-generated):", "required": False, "readonly": True},
            {"name": "name", "label": "Product Name:", "required": True},
            {"name": "vendor", "label": "Vendor:", "required": False},
            {"name": "hsn_code", "label": "HSN Code:", "required": False},
            {"name": "category", "label": "Category:", "required": False},
            {"name": "wholesale_price", "label": "Wholesale Price:", "required": True},
            {"name": "selling_price", "label": "Selling Price:", "required": True},
            {"name": "tax_percentage", "label": "Tax Percentage:", "required": False}
        ]
        
        # Variables to store entry values
        entry_vars = {}
        
        # Create labels and entries
        for i, field in enumerate(fields):
            # Label
            label = tk.Label(form_frame, 
                            text=field["label"],
                            font=FONTS["regular"],
                            bg=COLORS["bg_primary"],
                            fg=COLORS["text_primary"])
            label.grid(row=i, column=0, sticky="w", pady=8)
            
            # Entry
            var = tk.StringVar()
            entry_vars[field["name"]] = var
            
            # Set value from product data
            index = columns.index(field["name"])
            if product[index] is not None:
                var.set(product[index])
            
            # Make product code field read-only
            if field["name"] == "product_code":
                entry = tk.Entry(form_frame, 
                              textvariable=var,
                              font=FONTS["regular"],
                              width=40,
                              state="readonly")
            else:
                entry = tk.Entry(form_frame, 
                              textvariable=var,
                              font=FONTS["regular"],
                              width=40)
            entry.grid(row=i, column=1, sticky="w", pady=8, padx=10)
            
            # Add asterisk for required fields
            if field["required"]:
                required = tk.Label(form_frame, 
                                  text="*",
                                  font=FONTS["regular"],
                                  bg=COLORS["bg_primary"],
                                  fg=COLORS["danger"])
                required.grid(row=i, column=2, sticky="w")
        
        # Buttons frame
        button_frame = tk.Frame(product_dialog, bg=COLORS["bg_primary"], pady=15)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Cancel button
        cancel_btn = tk.Button(button_frame,
                             text="Cancel",
                             font=FONTS["regular"],
                             bg=COLORS["bg_secondary"],
                             fg=COLORS["text_primary"],
                             padx=20,
                             pady=5,
                             cursor="hand2",
                             command=product_dialog.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=20)
        
        # Function to update product
        def update_product():
            # Validate required fields
            for field in fields:
                if field["required"] and not entry_vars[field["name"]].get().strip():
                    messagebox.showerror("Error", f"{field['label']} is required.")
                    return
            
            # Validate numeric fields
            numeric_fields = ["wholesale_price", "selling_price", "tax_percentage"]
            for field in numeric_fields:
                try:
                    if entry_vars[field].get().strip():
                        float(entry_vars[field].get())
                except ValueError:
                    messagebox.showerror("Error", f"{field} must be a number.")
                    return
            
            # Create product data
            product_data = {}
            for field in fields:
                # Skip product_code as it should remain unchanged
                if field["name"] != "product_code":
                    product_data[field["name"]] = entry_vars[field["name"]].get().strip()
            
            # Add updated timestamp
            product_data["updated_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Update in database
            updated = self.controller.db.update("products", product_data, f"id = {product_id}")
            
            if updated:
                messagebox.showinfo("Success", "Product updated successfully!")
                product_dialog.destroy()
                self.load_products()  # Refresh product list
            else:
                messagebox.showerror("Error", "Failed to update product.")
        
        # Save button
        save_btn = tk.Button(button_frame,
                           text="Update Product",
                           font=FONTS["regular_bold"],
                           bg=COLORS["primary"],
                           fg=COLORS["text_white"],
                           padx=20,
                           pady=5,
                           cursor="hand2",
                           command=lambda: update_product())
        save_btn.pack(side=tk.RIGHT, padx=5)
        
        # Bind Enter key to update product
        def on_enter_key(event):
            update_product()
        
        product_dialog.bind('<Return>', on_enter_key)
    
    def delete_product(self):
        """Delete selected product"""
        # Get selected item
        selection = self.product_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a product to delete.")
            return
        
        # Get product ID
        product_id = self.product_tree.item(selection[0])["values"][0]
        product_name = self.product_tree.item(selection[0])["values"][2]
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", 
                                 f"Are you sure you want to delete '{product_name}'?\n\n"
                                 f"This will also delete all inventory records for this product."):
            return
        
        # Delete from database
        deleted = self.controller.db.delete("products", f"id = {product_id}")
        
        if deleted:
            messagebox.showinfo("Success", "Product deleted successfully!")
            self.load_products()  # Refresh product list
        else:
            messagebox.showerror("Error", "Failed to delete product.")
    
    def add_stock(self):
        """Add stock to selected product"""
        # Get selected item
        selection = self.product_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a product to add stock.")
            return
        
        # Get product ID
        product_id = self.product_tree.item(selection[0])["values"][0]
        product_name = self.product_tree.item(selection[0])["values"][2]
        
        # Create add stock dialog
        stock_dialog = tk.Toplevel(self)
        stock_dialog.title("Add Stock")
        stock_dialog.geometry("500x400")
        stock_dialog.resizable(False, False)
        stock_dialog.configure(bg=COLORS["bg_primary"])
        stock_dialog.grab_set()  # Make window modal
        
        # Center the dialog
        stock_dialog.update_idletasks()
        width = stock_dialog.winfo_width()
        height = stock_dialog.winfo_height()
        x = (stock_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (stock_dialog.winfo_screenheight() // 2) - (height // 2)
        stock_dialog.geometry(f"+{x}+{y}")
        
        # Create form
        title = tk.Label(stock_dialog, 
                        text=f"Add Stock: {product_name}",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"],
                        wraplength=450)
        title.pack(pady=15)
        
        # Form frame
        form_frame = tk.Frame(stock_dialog, bg=COLORS["bg_primary"], padx=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create form fields
        batch_label = tk.Label(form_frame, 
                              text="Batch Number:",
                              font=FONTS["regular"],
                              bg=COLORS["bg_primary"],
                              fg=COLORS["text_primary"])
        batch_label.grid(row=0, column=0, sticky="w", pady=8)
        
        batch_var = tk.StringVar()
        batch_entry = tk.Entry(form_frame, 
                              textvariable=batch_var,
                              font=FONTS["regular"],
                              width=30)
        batch_entry.grid(row=0, column=1, sticky="w", pady=8, padx=10)
        
        # Quantity
        quantity_label = tk.Label(form_frame, 
                                text="Quantity:",
                                font=FONTS["regular"],
                                bg=COLORS["bg_primary"],
                                fg=COLORS["text_primary"])
        quantity_label.grid(row=1, column=0, sticky="w", pady=8)
        
        quantity_var = tk.StringVar()
        quantity_entry = tk.Entry(form_frame, 
                                textvariable=quantity_var,
                                font=FONTS["regular"],
                                width=30)
        quantity_entry.grid(row=1, column=1, sticky="w", pady=8, padx=10)
        
        # Manufacturing date
        mfg_label = tk.Label(form_frame, 
                            text="Manufacturing Date (YYYY-MM-DD):",
                            font=FONTS["regular"],
                            bg=COLORS["bg_primary"],
                            fg=COLORS["text_primary"])
        mfg_label.grid(row=2, column=0, sticky="w", pady=8)
        
        mfg_var = tk.StringVar()
        mfg_entry = tk.Entry(form_frame, 
                            textvariable=mfg_var,
                            font=FONTS["regular"],
                            width=30)
        mfg_entry.grid(row=2, column=1, sticky="w", pady=8, padx=10)
        
        # Expiry date
        exp_label = tk.Label(form_frame, 
                            text="Expiry Date (YYYY-MM-DD):",
                            font=FONTS["regular"],
                            bg=COLORS["bg_primary"],
                            fg=COLORS["text_primary"])
        exp_label.grid(row=3, column=0, sticky="w", pady=8)
        
        exp_var = tk.StringVar()
        exp_entry = tk.Entry(form_frame, 
                            textvariable=exp_var,
                            font=FONTS["regular"],
                            width=30)
        exp_entry.grid(row=3, column=1, sticky="w", pady=8, padx=10)
        
        # Buttons frame
        button_frame = tk.Frame(stock_dialog, bg=COLORS["bg_primary"], pady=15)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Cancel button
        cancel_btn = tk.Button(button_frame,
                             text="Cancel",
                             font=FONTS["regular"],
                             bg=COLORS["bg_secondary"],
                             fg=COLORS["text_primary"],
                             padx=20,
                             pady=5,
                             cursor="hand2",
                             command=stock_dialog.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=20)
        
        # Function to add stock
        def save_stock():
            # Validate required fields
            if not quantity_var.get().strip():
                messagebox.showerror("Error", "Quantity is required.")
                return
            
            # Validate quantity is a number
            try:
                quantity = int(quantity_var.get())
                if quantity <= 0:
                    messagebox.showerror("Error", "Quantity must be greater than zero.")
                    return
            except ValueError:
                messagebox.showerror("Error", "Quantity must be a number.")
                return
            
            # Validate dates if provided
            mfg_date = mfg_var.get().strip()
            exp_date = exp_var.get().strip()
            
            # Create inventory data
            inventory_data = {
                "product_id": product_id,
                "batch_number": batch_var.get().strip(),
                "quantity": quantity,
                "purchase_date": datetime.date.today().isoformat()
            }
            
            if mfg_date:
                try:
                    datetime.date.fromisoformat(mfg_date)
                    inventory_data["manufacturing_date"] = mfg_date
                except ValueError:
                    messagebox.showerror("Error", "Invalid manufacturing date format. Use YYYY-MM-DD.")
                    return
            
            if exp_date:
                try:
                    datetime.date.fromisoformat(exp_date)
                    inventory_data["expiry_date"] = exp_date
                except ValueError:
                    messagebox.showerror("Error", "Invalid expiry date format. Use YYYY-MM-DD.")
                    return
            
            # Insert into database
            inventory_id = self.controller.db.insert("inventory", inventory_data)
            
            if inventory_id:
                # Also add a transaction record
                transaction_data = {
                    "product_id": product_id,
                    "batch_number": batch_var.get().strip(),
                    "quantity": quantity,
                    "transaction_type": "STOCK_IN",
                    "reference_id": inventory_id,
                    "notes": "Stock addition"
                }
                self.controller.db.insert("inventory_transactions", transaction_data)
                
                messagebox.showinfo("Success", "Stock added successfully!")
                stock_dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to add stock.")
        
        # Save button
        save_btn = tk.Button(button_frame,
                           text="Add Stock",
                           font=FONTS["regular"],
                           bg=COLORS["primary"],
                           fg=COLORS["text_white"],
                           padx=20,
                           pady=5,
                           cursor="hand2",
                           command=save_stock)
        save_btn.pack(side=tk.RIGHT, padx=5)
        
        # Bind Enter key to add stock
        def on_enter_key(event):
            save_stock()
        
        stock_dialog.bind('<Return>', on_enter_key)
    
    def show_context_menu(self, event):
        """Show context menu on right-click"""
        # Select row under mouse
        iid = self.product_tree.identify_row(event.y)
        if iid:
            # Select the item
            self.product_tree.selection_set(iid)
            # Show context menu
            self.context_menu.post(event.x_root, event.y_root)
    
    def handle_key_event(self, event):
        """Handle keyboard events for product management navigation"""
        # Focus management
        if event.keysym == "Tab":
            # Switch between product list and search
            if self.current_focus is None or self.current_focus == "products":
                self.current_focus = "search"
                self.search_var.set("")
                for widget in self.winfo_children():
                    if isinstance(widget, tk.Frame):
                        for child in widget.winfo_children():
                            if isinstance(child, tk.Entry):
                                child.focus_set()
                                return "break"
            else:
                self.current_focus = "products"
                self.selected_product_item = 0 if self.product_tree.get_children() else -1
                if self.selected_product_item >= 0:
                    self.product_tree.selection_set(self.product_tree.get_children()[self.selected_product_item])
                    self.product_tree.focus_set()
                return "break"
                
        # Navigation within product list
        if self.current_focus == "products":
            product_items = self.product_tree.get_children()
            if not product_items:
                return
                
            if event.keysym == "Down":
                # Move to next product
                self.selected_product_item = min(self.selected_product_item + 1, len(product_items) - 1)
                self.product_tree.selection_set(product_items[self.selected_product_item])
                self.product_tree.see(product_items[self.selected_product_item])
            elif event.keysym == "Up":
                # Move to previous product
                self.selected_product_item = max(self.selected_product_item - 1, 0)
                self.product_tree.selection_set(product_items[self.selected_product_item])
                self.product_tree.see(product_items[self.selected_product_item])
            elif event.keysym == "Return" or event.keysym == "space":
                # Edit selected product
                self.edit_product()
            elif event.keysym == "Delete":
                # Delete selected product
                self.delete_product()
                
        # Global keyboard shortcuts
        if event.keysym == "n" and event.state & 0x4:  # Ctrl+N
            # Add new product
            self.add_product()
        elif event.keysym == "e" and event.state & 0x4:  # Ctrl+E
            # Edit selected product
            selected = self.product_tree.selection()
            if selected:
                self.edit_product()
        elif event.keysym == "d" and event.state & 0x4:  # Ctrl+D
            # Delete selected product
            selected = self.product_tree.selection()
            if selected:
                self.delete_product()
        elif event.keysym == "f" and event.state & 0x4:  # Ctrl+F
            # Focus on search
            self.current_focus = "search"
            self.search_var.set("")
            for widget in self.winfo_children():
                if isinstance(widget, tk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Entry):
                            child.focus_set()
                            return "break"
        elif event.keysym == "s" and event.state & 0x4:  # Ctrl+S
            # Add stock
            selected = self.product_tree.selection()
            if selected:
                self.add_stock()
    
    def on_show(self):
        """Called when frame is shown"""
        # Refresh product list
        self.load_products()
        
        # Set initial focus
        self.current_focus = "products"
        self.focus_set()
        
        # Select first product if available
        if self.product_tree.get_children():
            self.selected_product_item = 0
            self.product_tree.selection_set(self.product_tree.get_children()[0])
            self.product_tree.focus_set()
