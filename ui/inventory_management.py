"""
Inventory Management UI for POS system
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import datetime
from assets.styles import COLORS, FONTS, STYLES

class InventoryManagementFrame(tk.Frame):
    """Inventory management with stock tracking, alerts and batch management"""
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=COLORS["bg_primary"])
        self.controller = controller
        
        # Header with title
        header_frame = tk.Frame(self, bg=COLORS["bg_primary"], pady=10)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        
        title = tk.Label(header_frame, 
                        text="Inventory Management",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"])
        title.pack(side=tk.LEFT, padx=20)
        
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
        self.categories_tab = tk.Frame(self.notebook, bg=COLORS["bg_primary"])
        self.vendors_tab = tk.Frame(self.notebook, bg=COLORS["bg_primary"])
        self.hsn_codes_tab = tk.Frame(self.notebook, bg=COLORS["bg_primary"])
        
        self.notebook.add(self.inventory_tab, text="Stock Levels")
        self.notebook.add(self.batches_tab, text="Batch Management")
        self.notebook.add(self.alerts_tab, text="Alerts & Expiry")
        self.notebook.add(self.categories_tab, text="Categories")
        self.notebook.add(self.vendors_tab, text="Vendors")
        self.notebook.add(self.hsn_codes_tab, text="HSN Codes")
        
        # Setup tabs
        self.setup_inventory_tab()
        self.setup_batches_tab()
        self.setup_alerts_tab()
        self.setup_categories_tab()
        self.setup_vendors_tab()
        self.setup_hsn_codes_tab()
    
    def setup_inventory_tab(self):
        """Setup the inventory tab with stock levels"""
        # Main container
        container = tk.Frame(self.inventory_tab, bg=COLORS["bg_primary"])
        container.pack(fill=tk.BOTH, expand=True)
        
        # Header with title and description
        header_frame = tk.Frame(container, bg=COLORS["bg_primary"], pady=10)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        
        title = tk.Label(header_frame, 
                        text="Current Stock Levels",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"])
        title.pack(side=tk.LEFT, padx=20)
        
        # Search and action area with improved layout
        action_area = tk.Frame(container, bg=COLORS["bg_secondary"], pady=10, padx=10)
        action_area.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        # Search area - place search components inline for better space usage
        search_frame = tk.Frame(action_area, bg=COLORS["bg_secondary"])
        search_frame.pack(fill=tk.X, pady=5)
        
        search_label = tk.Label(search_frame, 
                               text="Search Product:",
                               font=FONTS["regular_bold"],
                               bg=COLORS["bg_secondary"],
                               fg=COLORS["text_primary"])
        search_label.pack(side=tk.LEFT, padx=5)
        
        self.inventory_search_var = tk.StringVar()
        self.inventory_search_var.trace("w", lambda name, index, mode: self.search_inventory())
        
        search_entry = tk.Entry(search_frame, 
                               textvariable=self.inventory_search_var,
                               font=FONTS["regular"],
                               width=30)
        search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Action buttons in a row
        button_frame = tk.Frame(search_frame, bg=COLORS["bg_secondary"])
        button_frame.pack(side=tk.RIGHT, padx=5)
        
        # Refresh button
        refresh_btn = tk.Button(button_frame,
                              text="Refresh",
                              font=FONTS["regular"],
                              bg=COLORS["secondary"],
                              fg=COLORS["text_white"],
                              padx=15,
                              pady=5,
                              cursor="hand2",
                              command=self.load_inventory)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Add sorting options
        sort_frame = tk.Frame(action_area, bg=COLORS["bg_secondary"])
        sort_frame.pack(fill=tk.X, pady=5)
        
        sort_label = tk.Label(sort_frame,
                             text="Sort by:",
                             font=FONTS["regular"],
                             bg=COLORS["bg_secondary"],
                             fg=COLORS["text_primary"])
        sort_label.pack(side=tk.LEFT, padx=5)
        
        self.sort_options = ["Product Name", "Quantity (High to Low)", "Category"]
        self.sort_var = tk.StringVar(value=self.sort_options[0])
        sort_dropdown = ttk.Combobox(sort_frame,
                                    textvariable=self.sort_var,
                                    values=self.sort_options,
                                    width=20,
                                    state="readonly")
        sort_dropdown.pack(side=tk.LEFT, padx=5)
        sort_dropdown.bind("<<ComboboxSelected>>", lambda e: self.load_inventory())
        
        # Inventory treeview with improved visibility
        tree_container = tk.Frame(container, bg=COLORS["bg_primary"])
        tree_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Add a border to make the treeview stand out
        tree_frame = tk.Frame(tree_container, bd=1, relief=tk.RIDGE)
        tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Add both vertical and horizontal scrollbars
        y_scrollbar = ttk.Scrollbar(tree_frame)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        x_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal')
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
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
        
        # Create treeview with both scrollbars and increased height
        self.inventory_tree = ttk.Treeview(tree_frame, 
                                         columns=("ID", "Product", "Total Qty", "Category", "Wholesale", "Retail"),
                                         show="headings",
                                         yscrollcommand=y_scrollbar.set,
                                         xscrollcommand=x_scrollbar.set,
                                         height=20)  # Increase visible rows
        
        # Configure scrollbars
        y_scrollbar.config(command=self.inventory_tree.yview)
        x_scrollbar.config(command=self.inventory_tree.xview)
        
        # Define columns
        self.inventory_tree.heading("ID", text="Product ID")
        self.inventory_tree.heading("Product", text="Product Name")
        self.inventory_tree.heading("Total Qty", text="Total Quantity")
        self.inventory_tree.heading("Category", text="Category")
        self.inventory_tree.heading("Wholesale", text="Wholesale Price")
        self.inventory_tree.heading("Retail", text="Retail Price")
        
        # Set column widths
        self.inventory_tree.column("ID", width=80, minwidth=60)
        self.inventory_tree.column("Product", width=250, minwidth=150)
        self.inventory_tree.column("Total Qty", width=100, minwidth=80)
        self.inventory_tree.column("Category", width=150, minwidth=100)
        self.inventory_tree.column("Wholesale", width=120, minwidth=100)
        self.inventory_tree.column("Retail", width=120, minwidth=100)
        
        self.inventory_tree.pack(fill=tk.BOTH, expand=True)
        
        # Color code low stock items
        self.inventory_tree.tag_configure("low_stock", background=COLORS["warning_light"])
        self.inventory_tree.tag_configure("out_of_stock", background=COLORS["danger_light"])
        
        # Binding for double-click to view batches
        self.inventory_tree.bind("<Double-1>", self.view_product_batches)
        # Bind Enter key directly to the treeview
        self.inventory_tree.bind("<Return>", self.view_product_batches)
        
        # Information and help panel at the bottom
        info_frame = tk.Frame(container, bg=COLORS["bg_secondary"], pady=5)
        info_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        
        # Add a help icon
        help_icon = "ⓘ"  # Unicode information symbol
        help_label = tk.Label(info_frame,
                             text=help_icon,
                             font=("Arial", 16, "bold"),
                             bg=COLORS["bg_secondary"],
                             fg=COLORS["primary"])
        help_label.pack(side=tk.LEFT, padx=5)
        
        # Info text
        info_text = "Double-click or press Enter on a product to view its batch details. Items in yellow have low stock."
        info_label = tk.Label(info_frame, 
                             text=info_text,
                             font=FONTS["small_italic"],
                             bg=COLORS["bg_secondary"],
                             fg=COLORS["text_primary"],
                             justify=tk.LEFT)
        info_label.pack(side=tk.LEFT, padx=5)
    
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
        
        # Base query to get inventory summary from batches table
        # Note: Products table doesn't have min_stock_level column, so we'll use a default value
        query = """
            SELECT p.id, p.name, COALESCE(SUM(b.quantity), 0) as total_qty, p.category, 
                   p.wholesale_price, p.selling_price
            FROM products p
            LEFT JOIN batches b ON p.id = b.product_id
            GROUP BY p.id
        """
        
        # Add sorting based on selected option
        sort_option = self.sort_var.get() if hasattr(self, 'sort_var') else "Product Name"
        
        if sort_option == "Quantity (High to Low)":
            query += " ORDER BY total_qty DESC, p.name"
        elif sort_option == "Category":
            query += " ORDER BY p.category, p.name"
        else:  # Default: Product Name
            query += " ORDER BY p.name"
        
        try:
            inventory = self.controller.db.fetchall(query)
            
            # Default minimum stock level for all products
            default_min_stock = 10
            
            # Insert into treeview with color coding for stock levels
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
                
                # Determine tag based on stock level
                tag = ""
                if quantity <= 0:
                    tag = "out_of_stock"
                elif quantity < default_min_stock:
                    tag = "low_stock"
                
                # Insert into treeview with appropriate tag
                if tag:
                    self.inventory_tree.insert("", "end", values=row, tags=(tag,))
                else:
                    self.inventory_tree.insert("", "end", values=row)
        except Exception as e:
            print(f"Error loading inventory: {e}")
            messagebox.showerror("Database Error", f"Failed to load inventory: {str(e)}")
    
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
        
        # Get filtered inventory from batches table without min_stock_level
        query = """
            SELECT p.id, p.name, COALESCE(SUM(b.quantity), 0) as total_qty, p.category, 
                   p.wholesale_price, p.selling_price
            FROM products p
            LEFT JOIN batches b ON p.id = b.product_id
            WHERE LOWER(p.name) LIKE ? OR LOWER(p.product_code) LIKE ? OR LOWER(p.category) LIKE ?
            GROUP BY p.id
            ORDER BY p.name
        """
        
        try:
            search_pattern = f"%{search_term}%"
            inventory = self.controller.db.fetchall(query, (search_pattern, search_pattern, search_pattern))
            
            # Default minimum stock level for all products
            default_min_stock = 10
            
            # Insert into treeview with color coding for stock levels
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
                
                # Determine tag based on stock level
                tag = ""
                if quantity <= 0:
                    tag = "out_of_stock"
                elif quantity < default_min_stock:
                    tag = "low_stock"
                
                # Insert into treeview with appropriate tag
                if tag:
                    self.inventory_tree.insert("", "end", values=row, tags=(tag,))
                else:
                    self.inventory_tree.insert("", "end", values=row)
        except Exception as e:
            print(f"Error searching inventory: {e}")
            messagebox.showerror("Database Error", f"Failed to search inventory: {str(e)}")
    
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
            SELECT b.id, p.name, b.batch_number, b.quantity, 
                   b.manufacturing_date, b.expiry_date, b.purchase_date
            FROM batches b
            JOIN products p ON b.product_id = p.id
        """
        
        # Add filter if not showing all
        if not show_all and self.batch_product_var.get() and ":" in self.batch_product_var.get():
            product_id = self.batch_product_var.get().split(":")[0]
            query += f" WHERE b.product_id = {product_id}"
        
        query += " ORDER BY p.name, b.expiry_date"
        
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
        
        # Use a default low stock threshold
        # Get from settings table if available, otherwise use default
        try:
            setting = self.controller.db.fetchone("SELECT value FROM settings WHERE key = 'low_stock_threshold'")
            low_stock_threshold = int(setting[0]) if setting else 10
        except Exception as e:
            print(f"Error getting low_stock_threshold from settings: {e}")
            low_stock_threshold = 10
        
        # Get current date for expiry comparisons
        today = datetime.date.today()
        thirty_days_later = today + datetime.timedelta(days=30)
        
        # Build query based on alert type
        if alert_type == "Low Stock" or alert_type == "All Alerts":
            # Low stock query
            query = """
                SELECT 'Low Stock' as alert_type, p.name, b.quantity, b.batch_number, 
                       b.expiry_date, 'Low Stock' as status, b.id
                FROM batches b
                JOIN products p ON b.product_id = p.id
                WHERE b.quantity <= ?
                ORDER BY b.quantity
            """
            
            # Get low stock items
            low_stock_items = self.controller.db.fetchall(query, (low_stock_threshold,))
            
            # Insert into treeview
            for item in low_stock_items:
                self.alerts_tree.insert("", "end", values=item[:-1], tags=("low_stock",))
        
        if alert_type == "Expiring Soon" or alert_type == "All Alerts":
            # Expiring soon query
            query = """
                SELECT 'Expiring Soon' as alert_type, p.name, b.quantity, b.batch_number, 
                       b.expiry_date, 'Expiring Soon' as status, b.id
                FROM batches b
                JOIN products p ON b.product_id = p.id
                WHERE b.expiry_date IS NOT NULL 
                AND b.expiry_date <= ? 
                AND b.expiry_date >= ?
                AND b.quantity > 0
                ORDER BY b.expiry_date
            """
            
            # Get expiring items
            expiring_items = self.controller.db.fetchall(query, (thirty_days_later.isoformat(), today.isoformat()))
            
            # Insert into treeview
            for item in expiring_items:
                self.alerts_tree.insert("", "end", values=item[:-1], tags=("expiring",))
        
        if alert_type == "Expired" or alert_type == "All Alerts":
            # Expired query
            query = """
                SELECT 'Expired' as alert_type, p.name, b.quantity, b.batch_number, 
                       b.expiry_date, 'Expired' as status, b.id
                FROM batches b
                JOIN products p ON b.product_id = p.id
                WHERE b.expiry_date IS NOT NULL 
                AND b.expiry_date < ?
                AND b.quantity > 0
                ORDER BY b.expiry_date
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
            SELECT b.*, p.name 
            FROM batches b
            JOIN products p ON b.product_id = p.id
            WHERE b.id = ?
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
            
            # Create batch data
            batch_data = {
                "batch_number": batch_var.get().strip(),
                "quantity": quantity
            }
            
            if mfg_date:
                try:
                    datetime.date.fromisoformat(mfg_date)
                    batch_data["manufacturing_date"] = mfg_date
                except ValueError:
                    messagebox.showerror("Error", "Invalid manufacturing date format. Use YYYY-MM-DD.")
                    return
            
            if exp_date:
                try:
                    datetime.date.fromisoformat(exp_date)
                    batch_data["expiry_date"] = exp_date
                except ValueError:
                    messagebox.showerror("Error", "Invalid expiry date format. Use YYYY-MM-DD.")
                    return
            
            # Get old quantity for transaction record
            old_quantity = batch[quantity_idx]
            
            # Update in database
            updated = self.controller.db.update("batches", batch_data, f"id = {batch_id}")
            
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
        deleted = self.controller.db.delete("batches", f"id = {batch_id}")
        
        if deleted:
            messagebox.showinfo("Success", "Batch deleted successfully!")
            # Refresh data
            self.load_batches()
            self.load_inventory()
            self.load_alerts()
        else:
            messagebox.showerror("Error", "Failed to delete batch.")
    
    def setup_categories_tab(self):
        """Setup the categories management tab"""
        # Header
        header_frame = tk.Frame(self.categories_tab, bg=COLORS["bg_primary"], pady=10)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        
        title = tk.Label(header_frame, 
                        text="Product Categories",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"])
        title.pack(side=tk.LEFT, padx=20)
        
        # Split frame into left (list) and right (form) sections
        main_frame = tk.Frame(self.categories_tab, bg=COLORS["bg_primary"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left side - Category list
        list_frame = tk.Frame(main_frame, bg=COLORS["bg_primary"], width=400)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Treeview for categories
        tree_frame = tk.Frame(list_frame, bg=COLORS["bg_primary"])
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Categories treeview
        self.categories_tree = ttk.Treeview(tree_frame, 
                                         columns=("ID", "Name", "Description"),
                                         show="headings",
                                         yscrollcommand=scrollbar.set)
        
        # Configure scrollbar
        scrollbar.config(command=self.categories_tree.yview)
        
        # Define columns
        self.categories_tree.heading("ID", text="ID")
        self.categories_tree.heading("Name", text="Category Name")
        self.categories_tree.heading("Description", text="Description")
        
        # Set column widths
        self.categories_tree.column("ID", width=50)
        self.categories_tree.column("Name", width=150)
        self.categories_tree.column("Description", width=200)
        
        self.categories_tree.pack(fill=tk.BOTH, expand=True)
        
        # Right side - Category form
        form_frame = tk.Frame(main_frame, bg=COLORS["bg_primary"], width=400)
        form_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Category form
        form_title = tk.Label(form_frame, 
                           text="Add/Edit Category",
                           font=FONTS["heading2"],
                           bg=COLORS["bg_primary"],
                           fg=COLORS["text_primary"])
        form_title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))
        
        # Category name
        name_label = tk.Label(form_frame, 
                            text="Category Name:",
                            font=FONTS["regular"],
                            bg=COLORS["bg_primary"],
                            fg=COLORS["text_primary"])
        name_label.grid(row=1, column=0, sticky="w", pady=5)
        
        self.category_name_var = tk.StringVar()
        name_entry = tk.Entry(form_frame, 
                            textvariable=self.category_name_var,
                            font=FONTS["regular"],
                            width=30)
        name_entry.grid(row=1, column=1, sticky="w", pady=5)
        
        # Description
        desc_label = tk.Label(form_frame, 
                            text="Description:",
                            font=FONTS["regular"],
                            bg=COLORS["bg_primary"],
                            fg=COLORS["text_primary"])
        desc_label.grid(row=2, column=0, sticky="w", pady=5)
        
        self.category_desc_var = tk.StringVar()
        desc_entry = tk.Entry(form_frame, 
                            textvariable=self.category_desc_var,
                            font=FONTS["regular"],
                            width=30)
        desc_entry.grid(row=2, column=1, sticky="w", pady=5)
        
        # Buttons frame
        btn_frame = tk.Frame(form_frame, bg=COLORS["bg_primary"], pady=20)
        btn_frame.grid(row=3, column=0, columnspan=2, sticky="w")
        
        # Save button
        self.category_save_btn = tk.Button(btn_frame,
                                       text="Save Category",
                                       font=FONTS["regular"],
                                       bg=COLORS["primary"],
                                       fg=COLORS["text_white"],
                                       padx=15,
                                       pady=5,
                                       cursor="hand2",
                                       command=self.save_category)
        self.category_save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # New button
        new_category_btn = tk.Button(btn_frame,
                                  text="New Category",
                                  font=FONTS["regular"],
                                  bg=COLORS["secondary"],
                                  fg=COLORS["text_white"],
                                  padx=15,
                                  pady=5,
                                  cursor="hand2",
                                  command=self.new_category)
        new_category_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Delete button
        delete_category_btn = tk.Button(btn_frame,
                                     text="Delete Category",
                                     font=FONTS["regular"],
                                     bg=COLORS["danger"],
                                     fg=COLORS["text_white"],
                                     padx=15,
                                     pady=5,
                                     cursor="hand2",
                                     command=self.delete_category)
        delete_category_btn.pack(side=tk.LEFT)
        
        # Bind treeview selection
        self.categories_tree.bind("<<TreeviewSelect>>", self.on_category_select)
        
        # Status variable
        self.category_id_var = None
        self.category_mode = "add"  # 'add' or 'edit'

    def setup_vendors_tab(self):
        """Setup the vendors management tab"""
        # Header
        header_frame = tk.Frame(self.vendors_tab, bg=COLORS["bg_primary"], pady=10)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        
        title = tk.Label(header_frame, 
                        text="Vendor Management",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"])
        title.pack(side=tk.LEFT, padx=20)
        
        # Split frame into left (list) and right (form) sections
        main_frame = tk.Frame(self.vendors_tab, bg=COLORS["bg_primary"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left side - Vendor list
        list_frame = tk.Frame(main_frame, bg=COLORS["bg_primary"], width=400)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Treeview for vendors
        tree_frame = tk.Frame(list_frame, bg=COLORS["bg_primary"])
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Vendors treeview
        self.vendors_tree = ttk.Treeview(tree_frame, 
                                      columns=("ID", "Name", "Contact", "Phone", "GSTIN"),
                                      show="headings",
                                      yscrollcommand=scrollbar.set)
        
        # Configure scrollbar
        scrollbar.config(command=self.vendors_tree.yview)
        
        # Define columns
        self.vendors_tree.heading("ID", text="ID")
        self.vendors_tree.heading("Name", text="Vendor Name")
        self.vendors_tree.heading("Contact", text="Contact Person")
        self.vendors_tree.heading("Phone", text="Phone")
        self.vendors_tree.heading("GSTIN", text="GSTIN")
        
        # Set column widths
        self.vendors_tree.column("ID", width=50)
        self.vendors_tree.column("Name", width=150)
        self.vendors_tree.column("Contact", width=150)
        self.vendors_tree.column("Phone", width=120)
        self.vendors_tree.column("GSTIN", width=150)
        
        self.vendors_tree.pack(fill=tk.BOTH, expand=True)
        
        # Right side - Vendor form
        form_frame = tk.Frame(main_frame, bg=COLORS["bg_primary"], width=400)
        form_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Vendor form
        form_title = tk.Label(form_frame, 
                           text="Add/Edit Vendor",
                           font=FONTS["heading2"],
                           bg=COLORS["bg_primary"],
                           fg=COLORS["text_primary"])
        form_title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))
        
        # Vendor name
        name_label = tk.Label(form_frame, 
                            text="Vendor Name:",
                            font=FONTS["regular"],
                            bg=COLORS["bg_primary"],
                            fg=COLORS["text_primary"])
        name_label.grid(row=1, column=0, sticky="w", pady=5)
        
        self.vendor_name_var = tk.StringVar()
        name_entry = tk.Entry(form_frame, 
                            textvariable=self.vendor_name_var,
                            font=FONTS["regular"],
                            width=30)
        name_entry.grid(row=1, column=1, sticky="w", pady=5)
        
        # Contact person
        contact_label = tk.Label(form_frame, 
                              text="Contact Person:",
                              font=FONTS["regular"],
                              bg=COLORS["bg_primary"],
                              fg=COLORS["text_primary"])
        contact_label.grid(row=2, column=0, sticky="w", pady=5)
        
        self.vendor_contact_var = tk.StringVar()
        contact_entry = tk.Entry(form_frame, 
                              textvariable=self.vendor_contact_var,
                              font=FONTS["regular"],
                              width=30)
        contact_entry.grid(row=2, column=1, sticky="w", pady=5)
        
        # Phone
        phone_label = tk.Label(form_frame, 
                             text="Phone:",
                             font=FONTS["regular"],
                             bg=COLORS["bg_primary"],
                             fg=COLORS["text_primary"])
        phone_label.grid(row=3, column=0, sticky="w", pady=5)
        
        self.vendor_phone_var = tk.StringVar()
        phone_entry = tk.Entry(form_frame, 
                             textvariable=self.vendor_phone_var,
                             font=FONTS["regular"],
                             width=30)
        phone_entry.grid(row=3, column=1, sticky="w", pady=5)
        
        # Email
        email_label = tk.Label(form_frame, 
                             text="Email:",
                             font=FONTS["regular"],
                             bg=COLORS["bg_primary"],
                             fg=COLORS["text_primary"])
        email_label.grid(row=4, column=0, sticky="w", pady=5)
        
        self.vendor_email_var = tk.StringVar()
        email_entry = tk.Entry(form_frame, 
                             textvariable=self.vendor_email_var,
                             font=FONTS["regular"],
                             width=30)
        email_entry.grid(row=4, column=1, sticky="w", pady=5)
        
        # Address
        address_label = tk.Label(form_frame, 
                               text="Address:",
                               font=FONTS["regular"],
                               bg=COLORS["bg_primary"],
                               fg=COLORS["text_primary"])
        address_label.grid(row=5, column=0, sticky="w", pady=5)
        
        self.vendor_address_var = tk.StringVar()
        address_entry = tk.Entry(form_frame, 
                               textvariable=self.vendor_address_var,
                               font=FONTS["regular"],
                               width=30)
        address_entry.grid(row=5, column=1, sticky="w", pady=5)
        
        # GSTIN
        gstin_label = tk.Label(form_frame, 
                             text="GSTIN:",
                             font=FONTS["regular"],
                             bg=COLORS["bg_primary"],
                             fg=COLORS["text_primary"])
        gstin_label.grid(row=6, column=0, sticky="w", pady=5)
        
        self.vendor_gstin_var = tk.StringVar()
        gstin_entry = tk.Entry(form_frame, 
                             textvariable=self.vendor_gstin_var,
                             font=FONTS["regular"],
                             width=30)
        gstin_entry.grid(row=6, column=1, sticky="w", pady=5)
        
        # Buttons frame
        btn_frame = tk.Frame(form_frame, bg=COLORS["bg_primary"], pady=20)
        btn_frame.grid(row=7, column=0, columnspan=2, sticky="w")
        
        # Save button
        self.vendor_save_btn = tk.Button(btn_frame,
                                     text="Save Vendor",
                                     font=FONTS["regular"],
                                     bg=COLORS["primary"],
                                     fg=COLORS["text_white"],
                                     padx=15,
                                     pady=5,
                                     cursor="hand2",
                                     command=self.save_vendor)
        self.vendor_save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # New button
        new_vendor_btn = tk.Button(btn_frame,
                                text="New Vendor",
                                font=FONTS["regular"],
                                bg=COLORS["secondary"],
                                fg=COLORS["text_white"],
                                padx=15,
                                pady=5,
                                cursor="hand2",
                                command=self.new_vendor)
        new_vendor_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Delete button
        delete_vendor_btn = tk.Button(btn_frame,
                                   text="Delete Vendor",
                                   font=FONTS["regular"],
                                   bg=COLORS["danger"],
                                   fg=COLORS["text_white"],
                                   padx=15,
                                   pady=5,
                                   cursor="hand2",
                                   command=self.delete_vendor)
        delete_vendor_btn.pack(side=tk.LEFT)
        
        # Bind treeview selection
        self.vendors_tree.bind("<<TreeviewSelect>>", self.on_vendor_select)
        
        # Status variable
        self.vendor_id_var = None
        self.vendor_mode = "add"  # 'add' or 'edit'

    def setup_hsn_codes_tab(self):
        """Setup the HSN codes management tab"""
        # Header
        header_frame = tk.Frame(self.hsn_codes_tab, bg=COLORS["bg_primary"], pady=10)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        
        title = tk.Label(header_frame, 
                        text="HSN Codes Management",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"])
        title.pack(side=tk.LEFT, padx=20)
        
        # Split frame into left (list) and right (form) sections
        main_frame = tk.Frame(self.hsn_codes_tab, bg=COLORS["bg_primary"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left side - HSN codes list
        list_frame = tk.Frame(main_frame, bg=COLORS["bg_primary"], width=400)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Search frame
        search_frame = tk.Frame(list_frame, bg=COLORS["bg_primary"], pady=10)
        search_frame.pack(side=tk.TOP, fill=tk.X)
        
        search_label = tk.Label(search_frame, 
                              text="Search HSN Code:",
                              font=FONTS["regular"],
                              bg=COLORS["bg_primary"],
                              fg=COLORS["text_primary"])
        search_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.hsn_search_var = tk.StringVar()
        self.hsn_search_var.trace("w", lambda name, index, mode: self.search_hsn())
        
        search_entry = tk.Entry(search_frame, 
                              textvariable=self.hsn_search_var,
                              font=FONTS["regular"],
                              width=30)
        search_entry.pack(side=tk.LEFT)
        
        # Treeview for HSN codes
        tree_frame = tk.Frame(list_frame, bg=COLORS["bg_primary"])
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # HSN codes treeview
        self.hsn_tree = ttk.Treeview(tree_frame, 
                                   columns=("ID", "Code", "Description", "Tax Rate"),
                                   show="headings",
                                   yscrollcommand=scrollbar.set)
        
        # Configure scrollbar
        scrollbar.config(command=self.hsn_tree.yview)
        
        # Define columns
        self.hsn_tree.heading("ID", text="ID")
        self.hsn_tree.heading("Code", text="HSN Code")
        self.hsn_tree.heading("Description", text="Description")
        self.hsn_tree.heading("Tax Rate", text="Tax Rate (%)")
        
        # Set column widths
        self.hsn_tree.column("ID", width=50)
        self.hsn_tree.column("Code", width=100)
        self.hsn_tree.column("Description", width=250)
        self.hsn_tree.column("Tax Rate", width=100)
        
        self.hsn_tree.pack(fill=tk.BOTH, expand=True)
        
        # Right side - HSN code form
        form_frame = tk.Frame(main_frame, bg=COLORS["bg_primary"], width=400)
        form_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # HSN code form
        form_title = tk.Label(form_frame, 
                           text="Add/Edit HSN Code",
                           font=FONTS["heading2"],
                           bg=COLORS["bg_primary"],
                           fg=COLORS["text_primary"])
        form_title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))
        
        # HSN code
        code_label = tk.Label(form_frame, 
                            text="HSN Code:",
                            font=FONTS["regular"],
                            bg=COLORS["bg_primary"],
                            fg=COLORS["text_primary"])
        code_label.grid(row=1, column=0, sticky="w", pady=5)
        
        self.hsn_code_var = tk.StringVar()
        code_entry = tk.Entry(form_frame, 
                            textvariable=self.hsn_code_var,
                            font=FONTS["regular"],
                            width=30)
        code_entry.grid(row=1, column=1, sticky="w", pady=5)
        
        # Description
        desc_label = tk.Label(form_frame, 
                            text="Description:",
                            font=FONTS["regular"],
                            bg=COLORS["bg_primary"],
                            fg=COLORS["text_primary"])
        desc_label.grid(row=2, column=0, sticky="w", pady=5)
        
        self.hsn_desc_var = tk.StringVar()
        desc_entry = tk.Entry(form_frame, 
                            textvariable=self.hsn_desc_var,
                            font=FONTS["regular"],
                            width=30)
        desc_entry.grid(row=2, column=1, sticky="w", pady=5)
        
        # Tax rate
        tax_label = tk.Label(form_frame, 
                           text="Tax Rate (%):",
                           font=FONTS["regular"],
                           bg=COLORS["bg_primary"],
                           fg=COLORS["text_primary"])
        tax_label.grid(row=3, column=0, sticky="w", pady=5)
        
        self.hsn_tax_var = tk.StringVar()
        tax_entry = tk.Entry(form_frame, 
                           textvariable=self.hsn_tax_var,
                           font=FONTS["regular"],
                           width=30)
        tax_entry.grid(row=3, column=1, sticky="w", pady=5)
        
        # Buttons frame
        btn_frame = tk.Frame(form_frame, bg=COLORS["bg_primary"], pady=20)
        btn_frame.grid(row=4, column=0, columnspan=2, sticky="w")
        
        # Save button
        self.hsn_save_btn = tk.Button(btn_frame,
                                   text="Save HSN Code",
                                   font=FONTS["regular"],
                                   bg=COLORS["primary"],
                                   fg=COLORS["text_white"],
                                   padx=15,
                                   pady=5,
                                   cursor="hand2",
                                   command=self.save_hsn)
        self.hsn_save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # New button
        new_hsn_btn = tk.Button(btn_frame,
                              text="New HSN Code",
                              font=FONTS["regular"],
                              bg=COLORS["secondary"],
                              fg=COLORS["text_white"],
                              padx=15,
                              pady=5,
                              cursor="hand2",
                              command=self.new_hsn)
        new_hsn_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Delete button
        delete_hsn_btn = tk.Button(btn_frame,
                                 text="Delete HSN Code",
                                 font=FONTS["regular"],
                                 bg=COLORS["danger"],
                                 fg=COLORS["text_white"],
                                 padx=15,
                                 pady=5,
                                 cursor="hand2",
                                 command=self.delete_hsn)
        delete_hsn_btn.pack(side=tk.LEFT)
        
        # Bind treeview selection
        self.hsn_tree.bind("<<TreeviewSelect>>", self.on_hsn_select)
        
        # Status variable
        self.hsn_id_var = None
        self.hsn_mode = "add"  # 'add' or 'edit'
        
    # Category management functions
    def load_categories(self):
        """Load categories from database"""
        # Clear existing data
        for item in self.categories_tree.get_children():
            self.categories_tree.delete(item)
            
        # Get categories from database
        categories = self.controller.db.fetchall("SELECT * FROM categories ORDER BY name")
        
        # Insert into treeview
        for category in categories:
            self.categories_tree.insert("", "end", values=(category[0], category[1], category[2]))
    
    def on_category_select(self, event):
        """Handle category selection"""
        selection = self.categories_tree.selection()
        if not selection:
            return
            
        # Get category details
        category_id = self.categories_tree.item(selection[0])["values"][0]
        category = self.controller.db.fetchone(f"SELECT * FROM categories WHERE id = {category_id}")
        
        if category:
            # Fill form fields
            self.category_name_var.set(category[1])
            self.category_desc_var.set(category[2])
            
            # Set status
            self.category_id_var = category_id
            self.category_mode = "edit"
            self.category_save_btn.config(text="Update Category")
    
    def new_category(self):
        """Reset form for new category"""
        # Clear form fields
        self.category_name_var.set("")
        self.category_desc_var.set("")
        
        # Set status
        self.category_id_var = None
        self.category_mode = "add"
        self.category_save_btn.config(text="Save Category")
    
    def save_category(self):
        """Save or update category"""
        # Get form data
        name = self.category_name_var.get().strip()
        description = self.category_desc_var.get().strip()
        
        # Validate
        if not name:
            messagebox.showerror("Error", "Category name is required.")
            return
            
        try:
            if self.category_mode == "add":
                # Check if category already exists
                existing = self.controller.db.fetchone(f"SELECT id FROM categories WHERE name = ?", (name,))
                if existing:
                    messagebox.showerror("Error", f"Category '{name}' already exists.")
                    return
                    
                # Insert new category
                data = {
                    "name": name,
                    "description": description
                }
                
                inserted = self.controller.db.insert("categories", data)
                if inserted:
                    messagebox.showinfo("Success", "Category added successfully!")
                    self.load_categories()
                    self.new_category()
                else:
                    messagebox.showerror("Error", "Failed to add category.")
            else:
                # Update existing category
                data = {
                    "name": name,
                    "description": description
                }
                
                updated = self.controller.db.update("categories", data, f"id = {self.category_id_var}")
                if updated:
                    messagebox.showinfo("Success", "Category updated successfully!")
                    self.load_categories()
                    self.new_category()
                else:
                    messagebox.showerror("Error", "Failed to update category.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def delete_category(self):
        """Delete selected category"""
        if not self.category_id_var:
            messagebox.showinfo("Info", "Please select a category to delete.")
            return
            
        # Check if category is used in products
        products = self.controller.db.fetchall(f"SELECT id FROM products WHERE category = ?", 
                                             (self.category_name_var.get(),))
        
        if products:
            messagebox.showerror("Error", "Cannot delete category as it is used by products.")
            return
            
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", 
                                 f"Are you sure you want to delete category '{self.category_name_var.get()}'?"):
            return
            
        # Delete from database
        deleted = self.controller.db.delete("categories", f"id = {self.category_id_var}")
        
        if deleted:
            messagebox.showinfo("Success", "Category deleted successfully!")
            self.load_categories()
            self.new_category()
        else:
            messagebox.showerror("Error", "Failed to delete category.")

    # Vendor management functions
    def load_vendors(self):
        """Load vendors from database"""
        # Clear existing data
        for item in self.vendors_tree.get_children():
            self.vendors_tree.delete(item)
            
        # Get vendors from database
        vendors = self.controller.db.fetchall("SELECT * FROM vendors ORDER BY name")
        
        # Insert into treeview
        for vendor in vendors:
            self.vendors_tree.insert("", "end", values=(vendor[0], vendor[1], vendor[2], vendor[3], vendor[6]))
    
    def on_vendor_select(self, event):
        """Handle vendor selection"""
        selection = self.vendors_tree.selection()
        if not selection:
            return
            
        # Get vendor details
        vendor_id = self.vendors_tree.item(selection[0])["values"][0]
        vendor = self.controller.db.fetchone(f"SELECT * FROM vendors WHERE id = {vendor_id}")
        
        if vendor:
            # Fill form fields
            self.vendor_name_var.set(vendor[1])
            self.vendor_contact_var.set(vendor[2] or "")
            self.vendor_phone_var.set(vendor[3] or "")
            self.vendor_email_var.set(vendor[4] or "")
            self.vendor_address_var.set(vendor[5] or "")
            self.vendor_gstin_var.set(vendor[6] or "")
            
            # Set status
            self.vendor_id_var = vendor_id
            self.vendor_mode = "edit"
            self.vendor_save_btn.config(text="Update Vendor")
    
    def new_vendor(self):
        """Reset form for new vendor"""
        # Clear form fields
        self.vendor_name_var.set("")
        self.vendor_contact_var.set("")
        self.vendor_phone_var.set("")
        self.vendor_email_var.set("")
        self.vendor_address_var.set("")
        self.vendor_gstin_var.set("")
        
        # Set status
        self.vendor_id_var = None
        self.vendor_mode = "add"
        self.vendor_save_btn.config(text="Save Vendor")
    
    def save_vendor(self):
        """Save or update vendor"""
        # Get form data
        name = self.vendor_name_var.get().strip()
        contact = self.vendor_contact_var.get().strip()
        phone = self.vendor_phone_var.get().strip()
        email = self.vendor_email_var.get().strip()
        address = self.vendor_address_var.get().strip()
        gstin = self.vendor_gstin_var.get().strip()
        
        # Validate
        if not name:
            messagebox.showerror("Error", "Vendor name is required.")
            return
            
        try:
            if self.vendor_mode == "add":
                # Check if vendor already exists
                existing = self.controller.db.fetchone(f"SELECT id FROM vendors WHERE name = ?", (name,))
                if existing:
                    messagebox.showerror("Error", f"Vendor '{name}' already exists.")
                    return
                    
                # Insert new vendor
                data = {
                    "name": name,
                    "contact_person": contact,
                    "phone": phone,
                    "email": email,
                    "address": address,
                    "gstin": gstin
                }
                
                inserted = self.controller.db.insert("vendors", data)
                if inserted:
                    messagebox.showinfo("Success", "Vendor added successfully!")
                    self.load_vendors()
                    self.new_vendor()
                else:
                    messagebox.showerror("Error", "Failed to add vendor.")
            else:
                # Update existing vendor
                data = {
                    "name": name,
                    "contact_person": contact,
                    "phone": phone,
                    "email": email,
                    "address": address,
                    "gstin": gstin
                }
                
                updated = self.controller.db.update("vendors", data, f"id = {self.vendor_id_var}")
                if updated:
                    messagebox.showinfo("Success", "Vendor updated successfully!")
                    self.load_vendors()
                    self.new_vendor()
                else:
                    messagebox.showerror("Error", "Failed to update vendor.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def delete_vendor(self):
        """Delete selected vendor"""
        if not self.vendor_id_var:
            messagebox.showinfo("Info", "Please select a vendor to delete.")
            return
            
        # Check if vendor is used in products
        products = self.controller.db.fetchall(f"SELECT id FROM products WHERE vendor = ?", 
                                             (self.vendor_name_var.get(),))
        
        if products:
            messagebox.showerror("Error", "Cannot delete vendor as it is used by products.")
            return
            
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", 
                                 f"Are you sure you want to delete vendor '{self.vendor_name_var.get()}'?"):
            return
            
        # Delete from database
        deleted = self.controller.db.delete("vendors", f"id = {self.vendor_id_var}")
        
        if deleted:
            messagebox.showinfo("Success", "Vendor deleted successfully!")
            self.load_vendors()
            self.new_vendor()
        else:
            messagebox.showerror("Error", "Failed to delete vendor.")

    # HSN code management functions
    def load_hsn_codes(self):
        """Load HSN codes from database"""
        # Clear existing data
        for item in self.hsn_tree.get_children():
            self.hsn_tree.delete(item)
            
        # Get HSN codes from database
        hsn_codes = self.controller.db.fetchall("SELECT * FROM hsn_codes ORDER BY code")
        
        # Insert into treeview
        for hsn in hsn_codes:
            self.hsn_tree.insert("", "end", values=(hsn[0], hsn[1], hsn[2], hsn[3]))
    
    def search_hsn(self):
        """Search HSN codes"""
        search_term = self.hsn_search_var.get().strip()
        
        # Clear treeview
        for item in self.hsn_tree.get_children():
            self.hsn_tree.delete(item)
            
        if not search_term:
            self.load_hsn_codes()
            return
            
        # Search in database
        hsn_codes = self.controller.db.fetchall(
            "SELECT * FROM hsn_codes WHERE code LIKE ? OR description LIKE ? ORDER BY code",
            (f"%{search_term}%", f"%{search_term}%")
        )
        
        # Insert into treeview
        for hsn in hsn_codes:
            self.hsn_tree.insert("", "end", values=(hsn[0], hsn[1], hsn[2], hsn[3]))
    
    def on_hsn_select(self, event):
        """Handle HSN code selection"""
        selection = self.hsn_tree.selection()
        if not selection:
            return
            
        # Get HSN code details
        hsn_id = self.hsn_tree.item(selection[0])["values"][0]
        hsn = self.controller.db.fetchone(f"SELECT * FROM hsn_codes WHERE id = {hsn_id}")
        
        if hsn:
            # Fill form fields
            self.hsn_code_var.set(hsn[1])
            self.hsn_desc_var.set(hsn[2])
            self.hsn_tax_var.set(hsn[3])
            
            # Set status
            self.hsn_id_var = hsn_id
            self.hsn_mode = "edit"
            self.hsn_save_btn.config(text="Update HSN Code")
    
    def new_hsn(self):
        """Reset form for new HSN code"""
        # Clear form fields
        self.hsn_code_var.set("")
        self.hsn_desc_var.set("")
        self.hsn_tax_var.set("")
        
        # Set status
        self.hsn_id_var = None
        self.hsn_mode = "add"
        self.hsn_save_btn.config(text="Save HSN Code")
    
    def save_hsn(self):
        """Save or update HSN code"""
        # Get form data
        code = self.hsn_code_var.get().strip()
        description = self.hsn_desc_var.get().strip()
        tax_rate = self.hsn_tax_var.get().strip()
        
        # Validate
        if not code:
            messagebox.showerror("Error", "HSN code is required.")
            return
            
        try:
            # Validate tax rate
            if tax_rate:
                tax_rate = float(tax_rate)
            else:
                tax_rate = 0.0
                
            if self.hsn_mode == "add":
                # Check if HSN code already exists
                existing = self.controller.db.fetchone(f"SELECT id FROM hsn_codes WHERE code = ?", (code,))
                if existing:
                    messagebox.showerror("Error", f"HSN code '{code}' already exists.")
                    return
                    
                # Insert new HSN code
                data = {
                    "code": code,
                    "description": description,
                    "tax_rate": tax_rate
                }
                
                inserted = self.controller.db.insert("hsn_codes", data)
                if inserted:
                    messagebox.showinfo("Success", "HSN code added successfully!")
                    self.load_hsn_codes()
                    self.new_hsn()
                else:
                    messagebox.showerror("Error", "Failed to add HSN code.")
            else:
                # Update existing HSN code
                data = {
                    "code": code,
                    "description": description,
                    "tax_rate": tax_rate
                }
                
                updated = self.controller.db.update("hsn_codes", data, f"id = {self.hsn_id_var}")
                if updated:
                    messagebox.showinfo("Success", "HSN code updated successfully!")
                    self.load_hsn_codes()
                    self.new_hsn()
                else:
                    messagebox.showerror("Error", "Failed to update HSN code.")
        except ValueError:
            messagebox.showerror("Error", "Tax rate must be a number.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def delete_hsn(self):
        """Delete selected HSN code"""
        if not self.hsn_id_var:
            messagebox.showinfo("Info", "Please select an HSN code to delete.")
            return
            
        # Check if HSN code is used in products
        products = self.controller.db.fetchall(f"SELECT id FROM products WHERE hsn_code = ?", 
                                             (self.hsn_code_var.get(),))
        
        if products:
            messagebox.showerror("Error", "Cannot delete HSN code as it is used by products.")
            return
            
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", 
                                 f"Are you sure you want to delete HSN code '{self.hsn_code_var.get()}'?"):
            return
            
        # Delete from database
        deleted = self.controller.db.delete("hsn_codes", f"id = {self.hsn_id_var}")
        
        if deleted:
            messagebox.showinfo("Success", "HSN code deleted successfully!")
            self.load_hsn_codes()
            self.new_hsn()
        else:
            messagebox.showerror("Error", "Failed to delete HSN code.")
    
    def on_show(self):
        """Called when frame is shown"""
        # Load data for all tabs
        self.load_inventory()
        self.load_product_dropdown()  # Load products for batch filtering
        self.load_batches(show_all=True)
        self.load_alerts()
        self.load_categories()
        self.load_vendors()
        self.load_hsn_codes()
