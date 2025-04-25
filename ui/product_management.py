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
    
    def add_product(self):
        """Open dialog to add a new product"""
        # Create product dialog window
        product_dialog = tk.Toplevel(self)
        product_dialog.title("Add New Product")
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
                        text="Add New Product",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"])
        title.pack(pady=15)
        
        # Form frame
        form_frame = tk.Frame(product_dialog, bg=COLORS["bg_primary"], padx=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create form fields
        fields = [
            {"name": "product_code", "label": "Product Code:", "required": False},
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
        
        # Set default values
        entry_vars["tax_percentage"].set("0")
        
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
                product_data[field["name"]] = entry_vars[field["name"]].get().strip()
            
            # Insert into database
            product_id = self.controller.db.insert("products", product_data)
            
            if product_id:
                messagebox.showinfo("Success", "Product added successfully!")
                product_dialog.destroy()
                self.load_products()  # Refresh product list
            else:
                messagebox.showerror("Error", "Failed to add product.")
        
        # Save button
        save_btn = tk.Button(button_frame,
                           text="Save Product",
                           font=FONTS["regular"],
                           bg=COLORS["primary"],
                           fg=COLORS["text_white"],
                           padx=20,
                           pady=5,
                           cursor="hand2",
                           command=save_product)
        save_btn.pack(side=tk.RIGHT, padx=5)
    
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
            {"name": "product_code", "label": "Product Code:", "required": False},
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
                           font=FONTS["regular"],
                           bg=COLORS["primary"],
                           fg=COLORS["text_white"],
                           padx=20,
                           pady=5,
                           cursor="hand2",
                           command=update_product)
        save_btn.pack(side=tk.RIGHT, padx=5)
    
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
    
    def show_context_menu(self, event):
        """Show context menu on right-click"""
        # Select row under mouse
        iid = self.product_tree.identify_row(event.y)
        if iid:
            # Select the item
            self.product_tree.selection_set(iid)
            # Show context menu
            self.context_menu.post(event.x_root, event.y_root)
    
    def on_show(self):
        """Called when frame is shown"""
        # Refresh product list
        self.load_products()
