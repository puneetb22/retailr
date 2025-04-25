"""
Inventory Management UI for POS system
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from assets.styles import COLORS, FONTS, STYLES

class InventoryManagementFrame(tk.Frame):
    """Inventory management with stock tracking, alerts and batch management"""
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=COLORS["bg_primary"])
        self.controller = controller
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure notebook style
        style = ttk.Style()
        style.configure("TNotebook", background=COLORS["bg_primary"], borderwidth=0)
        style.configure("TNotebook.Tab", 
                       background=COLORS["bg_secondary"], 
                       foreground=COLORS["text_primary"],
                       padding=[10, 5],
                       font=FONTS["regular"])
        style.map("TNotebook.Tab", 
                 background=[("selected", COLORS["primary"])],
                 foreground=[("selected", COLORS["text_white"])])
        
        # Create tabs
        self.inventory_tab = tk.Frame(self.notebook, bg=COLORS["bg_primary"])
        self.batches_tab = tk.Frame(self.notebook, bg=COLORS["bg_primary"])
        self.alerts_tab = tk.Frame(self.notebook, bg=COLORS["bg_primary"])
        
        self.notebook.add(self.inventory_tab, text="Stock Levels")
        self.notebook.add(self.batches_tab, text="Batch Management")
        self.notebook.add(self.alerts_tab, text="Alerts & Expiry")
        
        # Setup tabs
        self.setup_inventory_tab()
        self.setup_batches_tab()
        self.setup_alerts_tab()
    
    def setup_inventory_tab(self):
        """Setup the inventory tab with stock levels"""
        # Header
        header_frame = tk.Frame(self.inventory_tab, bg=COLORS["bg_primary"], pady=10)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        
        title = tk.Label(header_frame, 
                        text="Current Stock Levels",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"])
        title.pack(side=tk.LEFT, padx=20)
        
        # Search frame
        search_frame = tk.Frame(self.inventory_tab, bg=COLORS["bg_primary"], pady=10, padx=20)
        search_frame.pack(side=tk.TOP, fill=tk.X)
        
        search_label = tk.Label(search_frame, 
                               text="Search Product:",
                               font=FONTS["regular"],
                               bg=COLORS["bg_primary"],
                               fg=COLORS["text_primary"])
        search_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.inventory_search_var = tk.StringVar()
        self.inventory_search_var.trace("w", lambda name, index, mode: self.search_inventory())
        
        search_entry = tk.Entry(search_frame, 
                               textvariable=self.inventory_search_var,
                               font=FONTS["regular"],
                               width=30)
        search_entry.pack(side=tk.LEFT)
        
        # Refresh button
        refresh_btn = tk.Button(search_frame,
                              text="Refresh",
                              font=FONTS["regular"],
                              bg=COLORS["secondary"],
                              fg=COLORS["text_white"],
                              padx=15,
                              pady=5,
                              cursor="hand2",
                              command=self.load_inventory)
        refresh_btn.pack(side=tk.RIGHT)
        
        # Inventory treeview
        tree_frame = tk.Frame(self.inventory_tab)
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
        self.inventory_tree = ttk.Treeview(tree_frame, 
                                         columns=("ID", "Product", "Total Qty", "Category", "Wholesale", "Retail"),
                                         show="headings",
                                         yscrollcommand=scrollbar.set)
        
        # Configure scrollbar
        scrollbar.config(command=self.inventory_tree.yview)
        
        # Define columns
        self.inventory_tree.heading("ID", text="Product ID")
        self.inventory_tree.heading("Product", text="Product Name")
        self.inventory_tree.heading("Total Qty", text="Total Quantity")
        self.inventory_tree.heading("Category", text="Category")
        self.inventory_tree.heading("Wholesale", text="Wholesale Price")
        self.inventory_tree.heading("Retail", text="Retail Price")
        
        # Set column widths
        self.inventory_tree.column("ID", width=80)
        self.inventory_tree.column("Product", width=250)
        self.inventory_tree.column("Total Qty", width=100)
        self.inventory_tree.column("Category", width=150)
        self.inventory_tree.column("Wholesale", width=120)
        self.inventory_tree.column("Retail", width=120)
        
        self.inventory_tree.pack(fill=tk.BOTH, expand=True)
        
        # Binding for double-click to view batches
        self.inventory_tree.bind("<Double-1>", self.view_product_batches)
        
        # Info label at bottom
        info_label = tk.Label(self.inventory_tab, 
                             text="Double-click on a product to view its batches",
                             font=FONTS["small_italic"],
                             bg=COLORS["bg_primary"],
                             fg=COLORS["text_secondary"])
        info_label.pack(side=tk.BOTTOM, pady=5)
    
    def setup_batches_tab(self):
        """Setup the batches tab with batch details"""
        # Header
        header_frame = tk.Frame(self.batches_tab, bg=COLORS["bg_primary"], pady=10)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        
        title = tk.Label(header_frame, 
                        text="Batch Management",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"])
        title.pack(side=tk.LEFT, padx=20)
        
        # Search and filter frame
        filter_frame = tk.Frame(self.batches_tab, bg=COLORS["bg_primary"], pady=10, padx=20)
        filter_frame.pack(side=tk.TOP, fill=tk.X)
        
        # Product dropdown
        product_label = tk.Label(filter_frame, 
                                text="Filter by Product:",
                                font=FONTS["regular"],
                                bg=COLORS["bg_primary"],
                                fg=COLORS["text_primary"])
        product_label.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")
        
        self.batch_product_var = tk.StringVar()
        self.product_dropdown = ttk.Combobox(filter_frame, 
                                           textvariable=self.batch_product_var,
                                           font=FONTS["regular"],
                                           width=30,
                                           state="readonly")
        self.product_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.product_dropdown.bind("<<ComboboxSelected>>", lambda e: self.load_batches())
        
        # Show all button
        show_all_btn = tk.Button(filter_frame,
                               text="Show All Batches",
                               font=FONTS["regular"],
                               bg=COLORS["secondary"],
                               fg=COLORS["text_white"],
                               padx=15,
                               pady=5,
                               cursor="hand2",
                               command=lambda: self.load_batches(show_all=True))
        show_all_btn.grid(row=0, column=2, padx=10, pady=5)
        
        # Batch treeview
        tree_frame = tk.Frame(self.batches_tab)
        tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create treeview
        self.batch_tree = ttk.Treeview(tree_frame, 
                                     columns=("ID", "Product", "Batch", "Qty", "MFG Date", 
                                            "Expiry", "Purchase Date"),
                                     show="headings",
                                     yscrollcommand=scrollbar.set)
        
        # Configure scrollbar
        scrollbar.config(command=self.batch_tree.yview)
        
        # Define columns
        self.batch_tree.heading("ID", text="ID")
        self.batch_tree.heading("Product", text="Product Name")
        self.batch_tree.heading("Batch", text="Batch Number")
        self.batch_tree.heading("Qty", text="Quantity")
        self.batch_tree.heading("MFG Date", text="MFG Date")
        self.batch_tree.heading("Expiry", text="Expiry Date")
        self.batch_tree.heading("Purchase Date", text="Purchase Date")
        
        # Set column widths
        self.batch_tree.column("ID", width=50)
        self.batch_tree.column("Product", width=250)
        self.batch_tree.column("Batch", width=100)
        self.batch_tree.column("Qty", width=80)
        self.batch_tree.column("MFG Date", width=100)
        self.batch_tree.column("Expiry", width=100)
        self.batch_tree.column("Purchase Date", width=100)
        
        self.batch_tree.pack(fill=tk.BOTH, expand=True)
        
        # Action buttons frame
        button_frame = tk.Frame(self.batches_tab, bg=COLORS["bg_primary"], pady=10, padx=20)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Edit batch button
        edit_btn = tk.Button(button_frame,
                           text="Edit Batch",
                           font=FONTS["regular"],
                           bg=COLORS["primary"],
                           fg=COLORS["text_white"],
                           padx=15,
                           pady=5,
                           cursor="hand2",
                           command=self.edit_batch)
        edit_btn.pack(side=tk.RIGHT, padx=5)
        
        # Delete batch button
        delete_btn = tk.Button(button_frame,
                             text="Delete Batch",
                             font=FONTS["regular"],
                             bg=COLORS["danger"],
                             fg=COLORS["text_white"],
                             padx=15,
                             pady=5,
                             cursor="hand2",
                             command=self.delete_batch)
        delete_btn.pack(side=tk.RIGHT, padx=5)
    
    def setup_alerts_tab(self):
        """Setup the alerts tab with expiry and low stock alerts"""
        # Header
        header_frame = tk.Frame(self.alerts_tab, bg=COLORS["bg_primary"], pady=10)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        
        title = tk.Label(header_frame, 
                        text="Inventory Alerts",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"])
        title.pack(side=tk.LEFT, padx=20)
        
        # Filter frame
        filter_frame = tk.Frame(self.alerts_tab, bg=COLORS["bg_primary"], pady=10, padx=20)
        filter_frame.pack(side=tk.TOP, fill=tk.X)
        
        # Alert type selection
        alert_label = tk.Label(filter_frame, 
                              text="Alert Type:",
                              font=FONTS["regular"],
                              bg=COLORS["bg_primary"],
                              fg=COLORS["text_primary"])
        alert_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.alert_type_var = tk.StringVar(value="All Alerts")
        alert_options = ["All Alerts", "Low Stock", "Expiring Soon", "Expired"]
        
        for i, option in enumerate(alert_options):
            rb = tk.Radiobutton(filter_frame,
                              text=option,
                              variable=self.alert_type_var,
                              value=option,
                              font=FONTS["regular"],
                              bg=COLORS["bg_primary"],
                              fg=COLORS["text_primary"],
                              selectcolor=COLORS["bg_primary"],
                              command=self.load_alerts)
            rb.pack(side=tk.LEFT, padx=10)
        
        # Alerts treeview
        tree_frame = tk.Frame(self.alerts_tab)
        tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create treeview
        self.alerts_tree = ttk.Treeview(tree_frame, 
                                      columns=("Type", "Product", "Current Qty", "Batch", 
                                             "Expiry", "Status"),
                                      show="headings",
                                      yscrollcommand=scrollbar.set)
        
        # Configure scrollbar
        scrollbar.config(command=self.alerts_tree.yview)
        
        # Define columns
        self.alerts_tree.heading("Type", text="Alert Type")
        self.alerts_tree.heading("Product", text="Product Name")
        self.alerts_tree.heading("Current Qty", text="Current Qty")
        self.alerts_tree.heading("Batch", text="Batch Number")
        self.alerts_tree.heading("Expiry", text="Expiry Date")
        self.alerts_tree.heading("Status", text="Status")
        
        # Set column widths
        self.alerts_tree.column("Type", width=100)
        self.alerts_tree.column("Product", width=250)
        self.alerts_tree.column("Current Qty", width=100)
        self.alerts_tree.column("Batch", width=100)
        self.alerts_tree.column("Expiry", width=100)
        self.alerts_tree.column("Status", width=120)
        
        self.alerts_tree.pack(fill=tk.BOTH, expand=True)
        
        # Tag configurations for color coding
        self.alerts_tree.tag_configure("expired", background=COLORS["danger_light"])
        self.alerts_tree.tag_configure("expiring", background=COLORS["warning_light"])
        self.alerts_tree.tag_configure("low_stock", background=COLORS["info_light"])
    
    def load_inventory(self):
        """Load inventory data into the stock levels tab"""
        # Clear current items
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        
        # Get inventory summary from database
        query = """
            SELECT p.id, p.name, SUM(i.quantity), p.category, 
                   p.wholesale_price, p.selling_price
            FROM products p
            LEFT JOIN inventory i ON p.id = i.product_id
            GROUP BY p.id
            ORDER BY p.name
        """
        inventory = self.controller.db.fetchall(query)
        
        # Insert into treeview
        for item in inventory:
            # Handle None for quantity (products with no inventory)
            quantity = item[2] if item[2] is not None else 0
            
            # Format the row
            row = (
                item[0],
                item[1],
                quantity,
                item[3] if item[3] else "",
                f"₹{item[4]:.2f}",
                f"₹{item[5]:.2f}"
            )
            
            self.inventory_tree.insert("", "end", values=row)
    
    def search_inventory(self):
        """Search inventory based on search term"""
        search_term = self.inventory_search_var.get().strip().lower()
        
        # Clear current items
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        
        if not search_term:
            # If search is empty, load all inventory
            self.load_inventory()
            return
        
        # Get filtered inventory
        query = """
            SELECT p.id, p.name, SUM(i.quantity), p.category, 
                   p.wholesale_price, p.selling_price
            FROM products p
            LEFT JOIN inventory i ON p.id = i.product_id
            WHERE LOWER(p.name) LIKE ? OR LOWER(p.product_code) LIKE ?
            GROUP BY p.id
            ORDER BY p.name
        """
        search_pattern = f"%{search_term}%"
        inventory = self.controller.db.fetchall(query, (search_pattern, search_pattern))
        
        # Insert into treeview
        for item in inventory:
            # Handle None for quantity
            quantity = item[2] if item[2] is not None else 0
            
            # Format the row
            row = (
                item[0],
                item[1],
                quantity,
                item[3] if item[3] else "",
                f"₹{item[4]:.2f}",
                f"₹{item[5]:.2f}"
            )
            
            self.inventory_tree.insert("", "end", values=row)
    
    def load_product_dropdown(self):
        """Load products into the dropdown for batch filtering"""
        # Get products from database
        query = "SELECT id, name FROM products ORDER BY name"
        products = self.controller.db.fetchall(query)
        
        # Format for dropdown (ID: Name)
        product_list = [f"{product[0]}: {product[1]}" for product in products]
        
        # Update dropdown values
        self.product_dropdown["values"] = ["-- Select Product --"] + product_list
        self.product_dropdown.current(0)
    
    def load_batches(self, show_all=False):
        """Load batch data into the batches tab"""
        # Clear current items
        for item in self.batch_tree.get_children():
            self.batch_tree.delete(item)
        
        # Base query
        query = """
            SELECT i.id, p.name, i.batch_number, i.quantity, 
                   i.manufacturing_date, i.expiry_date, i.purchase_date
            FROM inventory i
            JOIN products p ON i.product_id = p.id
        """
        
        # Add filter if not showing all
        if not show_all and self.batch_product_var.get() and ":" in self.batch_product_var.get():
            product_id = self.batch_product_var.get().split(":")[0]
            query += f" WHERE i.product_id = {product_id}"
        
        query += " ORDER BY p.name, i.expiry_date"
        
        # Get batches from database
        batches = self.controller.db.fetchall(query)
        
        # Insert into treeview
        for batch in batches:
            # Format dates
            mfg_date = batch[4] if batch[4] else ""
            exp_date = batch[5] if batch[5] else ""
            purchase_date = batch[6] if batch[6] else ""
            
            row = (
                batch[0],
                batch[1],
                batch[2] if batch[2] else "",
                batch[3],
                mfg_date,
                exp_date,
                purchase_date
            )
            
            self.batch_tree.insert("", "end", values=row)
    
    def load_alerts(self):
        """Load alert data into the alerts tab"""
        # Clear current items
        for item in self.alerts_tree.get_children():
            self.alerts_tree.delete(item)
        
        alert_type = self.alert_type_var.get()
        
        # Get low stock threshold from settings
        low_stock_threshold = int(self.controller.config.get('low_stock_threshold', 10))
        
        # Get current date for expiry comparisons
        today = datetime.date.today()
        thirty_days_later = today + datetime.timedelta(days=30)
        
        # Build query based on alert type
        if alert_type == "Low Stock" or alert_type == "All Alerts":
            # Low stock query
            query = """
                SELECT 'Low Stock' as alert_type, p.name, i.quantity, i.batch_number, 
                       i.expiry_date, 'Low Stock' as status, i.id
                FROM inventory i
                JOIN products p ON i.product_id = p.id
                WHERE i.quantity <= ?
                ORDER BY i.quantity
            """
            
            # Get low stock items
            low_stock_items = self.controller.db.fetchall(query, (low_stock_threshold,))
            
            # Insert into treeview
            for item in low_stock_items:
                self.alerts_tree.insert("", "end", values=item[:-1], tags=("low_stock",))
        
        if alert_type == "Expiring Soon" or alert_type == "All Alerts":
            # Expiring soon query
            query = """
                SELECT 'Expiring Soon' as alert_type, p.name, i.quantity, i.batch_number, 
                       i.expiry_date, 'Expiring Soon' as status, i.id
                FROM inventory i
                JOIN products p ON i.product_id = p.id
                WHERE i.expiry_date IS NOT NULL 
                AND i.expiry_date <= ? 
                AND i.expiry_date >= ?
                AND i.quantity > 0
                ORDER BY i.expiry_date
            """
            
            # Get expiring items
            expiring_items = self.controller.db.fetchall(query, (thirty_days_later.isoformat(), today.isoformat()))
            
            # Insert into treeview
            for item in expiring_items:
                self.alerts_tree.insert("", "end", values=item[:-1], tags=("expiring",))
        
        if alert_type == "Expired" or alert_type == "All Alerts":
            # Expired query
            query = """
                SELECT 'Expired' as alert_type, p.name, i.quantity, i.batch_number, 
                       i.expiry_date, 'Expired' as status, i.id
                FROM inventory i
                JOIN products p ON i.product_id = p.id
                WHERE i.expiry_date IS NOT NULL 
                AND i.expiry_date < ?
                AND i.quantity > 0
                ORDER BY i.expiry_date
            """
            
            # Get expired items
            expired_items = self.controller.db.fetchall(query, (today.isoformat(),))
            
            # Insert into treeview
            for item in expired_items:
                self.alerts_tree.insert("", "end", values=item[:-1], tags=("expired",))
    
    def view_product_batches(self, event=None):
        """View batches for selected product"""
        # Get selected product
        selection = self.inventory_tree.selection()
        if not selection:
            return
        
        # Get product ID and name
        product_id = self.inventory_tree.item(selection[0])["values"][0]
        product_name = self.inventory_tree.item(selection[0])["values"][1]
        
        # Switch to batches tab
        self.notebook.select(1)  # Select batches tab
        
        # Set filter and load batches
        product_entry = f"{product_id}: {product_name}"
        self.batch_product_var.set(product_entry)
        self.load_batches()
    
    def edit_batch(self):
        """Edit selected batch"""
        # Get selected batch
        selection = self.batch_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a batch to edit.")
            return
        
        # Get batch ID
        batch_id = self.batch_tree.item(selection[0])["values"][0]
        
        # Get batch data
        query = """
            SELECT i.*, p.name 
            FROM inventory i
            JOIN products p ON i.product_id = p.id
            WHERE i.id = ?
        """
        batch = self.controller.db.fetchone(query, (batch_id,))
        
        if not batch:
            messagebox.showerror("Error", "Batch not found.")
            return
        
        # Column names for reference
        columns = [description[0] for description in self.controller.db.cursor.description]
        
        # Create edit batch dialog
        batch_dialog = tk.Toplevel(self)
        batch_dialog.title("Edit Batch")
        batch_dialog.geometry("500x400")
        batch_dialog.resizable(False, False)
        batch_dialog.configure(bg=COLORS["bg_primary"])
        batch_dialog.grab_set()  # Make window modal
        
        # Center the dialog
        batch_dialog.update_idletasks()
        width = batch_dialog.winfo_width()
        height = batch_dialog.winfo_height()
        x = (batch_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (batch_dialog.winfo_screenheight() // 2) - (height // 2)
        batch_dialog.geometry(f"+{x}+{y}")
        
        # Get product name (last column from join)
        product_name = batch[-1]
        
        # Create form
        title = tk.Label(batch_dialog, 
                        text=f"Edit Batch for: {product_name}",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"],
                        wraplength=450)
        title.pack(pady=15)
        
        # Form frame
        form_frame = tk.Frame(batch_dialog, bg=COLORS["bg_primary"], padx=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create form fields
        batch_label = tk.Label(form_frame, 
                              text="Batch Number:",
                              font=FONTS["regular"],
                              bg=COLORS["bg_primary"],
                              fg=COLORS["text_primary"])
        batch_label.grid(row=0, column=0, sticky="w", pady=8)
        
        batch_var = tk.StringVar()
        batch_idx = columns.index("batch_number")
        if batch[batch_idx]:
            batch_var.set(batch[batch_idx])
        
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
        quantity_idx = columns.index("quantity")
        quantity_var.set(batch[quantity_idx])
        
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
        mfg_idx = columns.index("manufacturing_date")
        if batch[mfg_idx]:
            mfg_var.set(batch[mfg_idx])
        
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
        exp_idx = columns.index("expiry_date")
        if batch[exp_idx]:
            exp_var.set(batch[exp_idx])
        
        exp_entry = tk.Entry(form_frame, 
                            textvariable=exp_var,
                            font=FONTS["regular"],
                            width=30)
        exp_entry.grid(row=3, column=1, sticky="w", pady=8, padx=10)
        
        # Buttons frame
        button_frame = tk.Frame(batch_dialog, bg=COLORS["bg_primary"], pady=15)
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
                             command=batch_dialog.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=20)
        
        # Function to update batch
        def update_batch():
            # Validate required fields
            if not quantity_var.get().strip():
                messagebox.showerror("Error", "Quantity is required.")
                return
            
            # Validate quantity is a number
            try:
                quantity = int(quantity_var.get())
                if quantity < 0:
                    messagebox.showerror("Error", "Quantity cannot be negative.")
                    return
            except ValueError:
                messagebox.showerror("Error", "Quantity must be a number.")
                return
            
            # Validate dates if provided
            mfg_date = mfg_var.get().strip()
            exp_date = exp_var.get().strip()
            
            # Create inventory data
            inventory_data = {
                "batch_number": batch_var.get().strip(),
                "quantity": quantity
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
            
            # Get old quantity for transaction record
            old_quantity = batch[quantity_idx]
            
            # Update in database
            updated = self.controller.db.update("inventory", inventory_data, f"id = {batch_id}")
            
            if updated:
                # Add transaction record if quantity changed
                if old_quantity != quantity:
                    # Difference in quantity
                    qty_diff = quantity - old_quantity
                    
                    if qty_diff != 0:
                        # Create transaction record
                        transaction_data = {
                            "product_id": batch[columns.index("product_id")],
                            "batch_number": batch_var.get().strip(),
                            "quantity": abs(qty_diff),
                            "transaction_type": "STOCK_IN" if qty_diff > 0 else "STOCK_OUT",
                            "reference_id": batch_id,
                            "notes": "Batch update"
                        }
                        self.controller.db.insert("inventory_transactions", transaction_data)
                
                messagebox.showinfo("Success", "Batch updated successfully!")
                batch_dialog.destroy()
                
                # Refresh data
                self.load_batches()
                self.load_inventory()
                self.load_alerts()
            else:
                messagebox.showerror("Error", "Failed to update batch.")
        
        # Save button
        save_btn = tk.Button(button_frame,
                           text="Update Batch",
                           font=FONTS["regular"],
                           bg=COLORS["primary"],
                           fg=COLORS["text_white"],
                           padx=20,
                           pady=5,
                           cursor="hand2",
                           command=update_batch)
        save_btn.pack(side=tk.RIGHT, padx=5)
    
    def delete_batch(self):
        """Delete selected batch"""
        # Get selected batch
        selection = self.batch_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a batch to delete.")
            return
        
        # Get batch details
        batch_id = self.batch_tree.item(selection[0])["values"][0]
        product_name = self.batch_tree.item(selection[0])["values"][1]
        batch_number = self.batch_tree.item(selection[0])["values"][2]
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", 
                                 f"Are you sure you want to delete batch {batch_number} of '{product_name}'?"):
            return
        
        # Delete from database
        deleted = self.controller.db.delete("inventory", f"id = {batch_id}")
        
        if deleted:
            messagebox.showinfo("Success", "Batch deleted successfully!")
            # Refresh data
            self.load_batches()
            self.load_inventory()
            self.load_alerts()
        else:
            messagebox.showerror("Error", "Failed to delete batch.")
    
    def on_show(self):
        """Called when frame is shown"""
        # Load data for all tabs
        self.load_inventory()
        self.load_product_dropdown()
        self.load_batches(show_all=True)
        self.load_alerts()
