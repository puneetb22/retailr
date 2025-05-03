"""
Sales History UI for POS system
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import subprocess

# Import global styles and formatting utils
from assets.styles import COLORS, FONTS
from utils.helpers import format_currency, parse_date, format_date

class SalesHistoryFrame(tk.Frame):
    """Sales history frame for viewing and reprinting invoices"""
    
    def __init__(self, parent, controller):
        """Initialize the sales history frame"""
        super().__init__(parent, bg=COLORS["bg_primary"])
        self.controller = controller
        self.selected_date = datetime.date.today()
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create widgets for sales history display"""
        # Main container with padding
        main_container = tk.Frame(self, bg=COLORS["bg_primary"], padx=10, pady=10)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid for main container
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)
        
        # Title and date selection
        header_frame = tk.Frame(main_container, bg=COLORS["bg_primary"])
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Configure header grid
        header_frame.columnconfigure(0, weight=1)  # Title expands
        header_frame.columnconfigure(1, weight=0)  # Date controls fixed width
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="Daily Sales History",
            font=FONTS["heading"],
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"]
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        # Date filter controls
        date_frame = tk.Frame(header_frame, bg=COLORS["bg_primary"])
        date_frame.grid(row=0, column=1, sticky="e")
        
        tk.Label(
            date_frame,
            text="Select Date:",
            font=FONTS["regular_bold"],
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"]
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Create date selection dropdown menus
        date_controls_frame = tk.Frame(date_frame, bg=COLORS["bg_primary"])
        date_controls_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        # Day dropdown
        self.day_var = tk.StringVar(value=str(self.selected_date.day).zfill(2))
        days = [str(day).zfill(2) for day in range(1, 32)]
        self.day_dropdown = ttk.Combobox(
            date_controls_frame, 
            textvariable=self.day_var,
            values=days,
            width=3,
            state="readonly"
        )
        self.day_dropdown.pack(side=tk.LEFT, padx=2)
        self.day_dropdown.bind("<<ComboboxSelected>>", self.on_date_component_change)
        
        tk.Label(
            date_controls_frame,
            text="/",
            font=FONTS["regular_bold"],
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"]
        ).pack(side=tk.LEFT)
        
        # Month dropdown
        self.month_var = tk.StringVar(value=str(self.selected_date.month).zfill(2))
        months = [str(month).zfill(2) for month in range(1, 13)]
        self.month_dropdown = ttk.Combobox(
            date_controls_frame, 
            textvariable=self.month_var,
            values=months,
            width=3,
            state="readonly"
        )
        self.month_dropdown.pack(side=tk.LEFT, padx=2)
        self.month_dropdown.bind("<<ComboboxSelected>>", self.on_date_component_change)
        
        tk.Label(
            date_controls_frame,
            text="/",
            font=FONTS["regular_bold"],
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"]
        ).pack(side=tk.LEFT)
        
        # Year dropdown
        current_year = datetime.date.today().year
        self.year_var = tk.StringVar(value=str(self.selected_date.year))
        years = [str(year) for year in range(current_year - 5, current_year + 1)]
        self.year_dropdown = ttk.Combobox(
            date_controls_frame, 
            textvariable=self.year_var,
            values=years,
            width=5,
            state="readonly"
        )
        self.year_dropdown.pack(side=tk.LEFT, padx=2)
        self.year_dropdown.bind("<<ComboboxSelected>>", self.on_date_component_change)
        
        # Today button
        today_btn = tk.Button(
            date_frame,
            text="Today",
            font=FONTS["regular"],
            bg=COLORS["secondary"],
            fg=COLORS["text_white"],
            padx=10,
            pady=3,
            cursor="hand2",
            command=self.select_today
        )
        today_btn.pack(side=tk.LEFT, padx=(5, 10))
        
        view_button = tk.Button(
            date_frame,
            text="View Sales",
            font=FONTS["regular_bold"],
            bg=COLORS["primary"],
            fg=COLORS["text_white"],
            padx=15,
            pady=5,
            cursor="hand2",
            command=self.load_sales
        )
        view_button.pack(side=tk.LEFT)
        
        # Create main content area with sales list and details using grid
        content_frame = tk.Frame(main_container, bg=COLORS["bg_primary"])
        content_frame.grid(row=1, column=0, sticky="nsew")
        
        # Configure content frame grid for better resizing
        content_frame.columnconfigure(0, weight=4)  # 40% for list
        content_frame.columnconfigure(1, weight=6)  # 60% for details
        content_frame.rowconfigure(0, weight=1)     # Let content expand
        
        # Setup two panels - left for invoices list, right for details
        self.setup_sales_list(content_frame)
        self.setup_details_panel(content_frame)
    
    def setup_sales_list(self, parent):
        """Setup the sales/invoices list panel"""
        list_frame = tk.Frame(parent, bg=COLORS["bg_secondary"], padx=15, pady=15)
        list_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure list frame grid
        list_frame.columnconfigure(0, weight=1)  # Make columns expandable
        list_frame.rowconfigure(3, weight=1)    # Treeview row should expand
        
        # Title for list - row 0
        tk.Label(
            list_frame,
            text="Invoices",
            font=FONTS["subheading"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        # Stats for the selected day - row 1
        self.stats_frame = tk.Frame(list_frame, bg=COLORS["bg_secondary"])
        self.stats_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        self.total_sales_label = tk.Label(
            self.stats_frame,
            text="Total Sales: ₹0.00",
            font=FONTS["regular_bold"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        )
        self.total_sales_label.pack(side=tk.LEFT, padx=(0, 15))
        
        self.invoice_count_label = tk.Label(
            self.stats_frame,
            text="Invoices: 0",
            font=FONTS["regular_bold"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        )
        self.invoice_count_label.pack(side=tk.LEFT)
        
        # Search frame - row 2
        search_frame = tk.Frame(list_frame, bg=COLORS["bg_secondary"])
        search_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        
        # Configure search frame grid
        search_frame.columnconfigure(1, weight=1)  # Make entry expand
        
        tk.Label(
            search_frame,
            text="Search:",
            font=FONTS["regular"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=FONTS["regular"]
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        search_entry.bind("<KeyRelease>", self.search_invoices)
        
        # Tree and scrollbar container - row 3
        tree_container = tk.Frame(list_frame, bg=COLORS["bg_secondary"])
        tree_container.grid(row=3, column=0, sticky="nsew")
        
        # Configure tree container
        tree_container.columnconfigure(0, weight=1)
        tree_container.rowconfigure(0, weight=1)
        
        # Treeview for sales list
        columns = ("invoice_number", "customer", "amount", "payment", "time")
        self.sales_tree = ttk.Treeview(
            tree_container, 
            columns=columns,
            show="headings",
            selectmode="browse",
            style="Custom.Treeview"
        )
        
        # Define headings
        self.sales_tree.heading("invoice_number", text="Invoice #")
        self.sales_tree.heading("customer", text="Customer")
        self.sales_tree.heading("amount", text="Amount")
        self.sales_tree.heading("payment", text="Payment")
        self.sales_tree.heading("time", text="Time")
        
        # Define columns with better proportions and explicit anchors
        self.sales_tree.column("invoice_number", width=120, anchor="w", minwidth=80)
        self.sales_tree.column("customer", width=150, anchor="w", minwidth=100)
        self.sales_tree.column("amount", width=100, anchor="e", minwidth=80)
        self.sales_tree.column("payment", width=100, anchor="center", minwidth=80)
        self.sales_tree.column("time", width=80, anchor="center", minwidth=60)
        
        # Create scrollbar
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.sales_tree.yview)
        self.sales_tree.configure(yscrollcommand=scrollbar.set)
        
        # Horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal", command=self.sales_tree.xview)
        self.sales_tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Place treeview and scrollbars with grid
        self.sales_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Bind selection event
        self.sales_tree.bind("<<TreeviewSelect>>", self.on_invoice_select)
        self.sales_tree.bind("<Double-1>", self.view_invoice)
        
        # Bind right-click context menu
        self.sales_tree.bind("<Button-3>", self.show_context_menu)
    
    def setup_details_panel(self, parent):
        """Setup the invoice details panel"""
        details_frame = tk.Frame(parent, bg=COLORS["bg_secondary"], padx=15, pady=15)
        details_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        # Use Grid layout manager for better control
        details_frame.columnconfigure(0, weight=1)  # Make the frame expandable
        details_frame.rowconfigure(2, weight=1)  # Make items section expandable
        
        # Title for details - row 0
        title_label = tk.Label(
            details_frame,
            text="Invoice Details",
            font=FONTS["subheading"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        )
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 15))
        
        # Customer and invoice info container - row 1
        info_frame = tk.Frame(details_frame, bg=COLORS["bg_secondary"])
        info_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        info_frame.columnconfigure(0, weight=1)
        info_frame.columnconfigure(1, weight=1)
        
        # Customer info - left column
        customer_frame = tk.Frame(info_frame, bg=COLORS["bg_secondary"])
        customer_frame.grid(row=0, column=0, sticky="nw")
        
        tk.Label(
            customer_frame,
            text="Customer Information",
            font=FONTS["regular_bold"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        ).pack(anchor="w")
        
        self.customer_name_label = tk.Label(
            customer_frame,
            text="Name: -",
            font=FONTS["regular"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            anchor="w", 
            justify="left"
        )
        self.customer_name_label.pack(anchor="w", pady=(5, 0))
        
        self.customer_phone_label = tk.Label(
            customer_frame,
            text="Phone: -",
            font=FONTS["regular"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            anchor="w", 
            justify="left"
        )
        self.customer_phone_label.pack(anchor="w")
        
        self.customer_address_label = tk.Label(
            customer_frame,
            text="Address: -",
            font=FONTS["regular"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            anchor="w", 
            justify="left"
        )
        self.customer_address_label.pack(anchor="w")
        
        # Invoice info - right column
        invoice_frame = tk.Frame(info_frame, bg=COLORS["bg_secondary"])
        invoice_frame.grid(row=0, column=1, sticky="ne")
        
        tk.Label(
            invoice_frame,
            text="Invoice Information",
            font=FONTS["regular_bold"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        ).pack(anchor="w")
        
        self.invoice_number_label = tk.Label(
            invoice_frame,
            text="Number: -",
            font=FONTS["regular"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            anchor="w", 
            justify="left"
        )
        self.invoice_number_label.pack(anchor="w", pady=(5, 0))
        
        self.invoice_date_label = tk.Label(
            invoice_frame,
            text="Date: -",
            font=FONTS["regular"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            anchor="w", 
            justify="left"
        )
        self.invoice_date_label.pack(anchor="w")
        
        self.invoice_amount_label = tk.Label(
            invoice_frame,
            text="Amount: -",
            font=FONTS["regular"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            anchor="w", 
            justify="left"
        )
        self.invoice_amount_label.pack(anchor="w")
        
        # Invoice items section - row 2 (expanded)
        items_label_frame = tk.Frame(details_frame, bg=COLORS["bg_secondary"])
        items_label_frame.grid(row=2, column=0, sticky="new", pady=(5, 0))
        
        tk.Label(
            items_label_frame,
            text="Items",
            font=FONTS["regular_bold"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        ).pack(side=tk.LEFT, anchor="w")
        
        # Create a container with fixed height for items
        items_container = tk.Frame(details_frame, bg=COLORS["bg_secondary"], 
                                  highlightbackground=COLORS["border"], 
                                  highlightthickness=1)
        items_container.grid(row=3, column=0, sticky="nsew", pady=(5, 10))
        
        # Ensure minimum height for the items container
        items_container.grid_propagate(False)
        items_container.configure(height=200)
        
        # Configure items container layout
        items_container.columnconfigure(0, weight=1)
        items_container.rowconfigure(0, weight=1)
        
        # Create frame for treeview and scrollbars
        tree_frame = tk.Frame(items_container, bg=COLORS["bg_secondary"])
        tree_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal")
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview for invoice items
        columns = ("item", "hsn", "qty", "price", "discount", "amount")
        self.items_tree = ttk.Treeview(
            tree_frame, 
            columns=columns,
            show="headings",
            selectmode="browse",
            style="Custom.Treeview",
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        
        # Connect scrollbars to treeview
        v_scrollbar.config(command=self.items_tree.yview)
        h_scrollbar.config(command=self.items_tree.xview)
        
        # Define headings
        self.items_tree.heading("item", text="Item")
        self.items_tree.heading("hsn", text="HSN")
        self.items_tree.heading("qty", text="Qty")
        self.items_tree.heading("price", text="Price")
        self.items_tree.heading("discount", text="Disc %")
        self.items_tree.heading("amount", text="Amount")
        
        # Define columns with improved alignment and proportions
        self.items_tree.column("item", width=180, anchor="w")  # Wider for item names, left aligned
        self.items_tree.column("hsn", width=80, anchor="center")  # Center HSN codes
        self.items_tree.column("qty", width=60, anchor="center")  # Center quantities
        self.items_tree.column("price", width=100, anchor="e")  # Right align prices
        self.items_tree.column("discount", width=80, anchor="center")  # Center discounts
        self.items_tree.column("amount", width=100, anchor="e")  # Right align amounts
        
        # Place treeview
        self.items_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Payment info - row 4
        payment_label_frame = tk.Frame(details_frame, bg=COLORS["bg_secondary"])
        payment_label_frame.grid(row=4, column=0, sticky="new", pady=(15, 5))
        
        tk.Label(
            payment_label_frame,
            text="Payment Information",
            font=FONTS["regular_bold"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        ).pack(side=tk.LEFT, anchor="w")
        
        # Payment details container
        payment_container = tk.Frame(details_frame, bg=COLORS["bg_secondary"])
        payment_container.grid(row=5, column=0, sticky="ew")
        
        # Layout for payment details 
        payment_container.columnconfigure(0, weight=1)
        payment_container.columnconfigure(1, weight=1)
        
        # Left side payment info
        payment_left = tk.Frame(payment_container, bg=COLORS["bg_secondary"])
        payment_left.grid(row=0, column=0, sticky="w")
        
        self.payment_method_label = tk.Label(
            payment_left,
            text="Method: -",
            font=FONTS["regular"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        )
        self.payment_method_label.pack(anchor="w")
        
        # Right side payment info
        payment_right = tk.Frame(payment_container, bg=COLORS["bg_secondary"])
        payment_right.grid(row=0, column=1, sticky="w")
        
        self.payment_status_label = tk.Label(
            payment_right,
            text="Status: -",
            font=FONTS["regular"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        )
        self.payment_status_label.pack(anchor="w")
        
        # Additional payment details below
        payment_details = tk.Frame(payment_container, bg=COLORS["bg_secondary"])
        payment_details.grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 0))
        
        self.payment_details_label = tk.Label(
            payment_details,
            text="",
            font=FONTS["regular"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        )
        self.payment_details_label.pack(anchor="w")
        
        # Buttons frame at the bottom - row 6
        buttons_frame = tk.Frame(details_frame, bg=COLORS["bg_secondary"])
        buttons_frame.grid(row=6, column=0, sticky="ew", pady=(15, 0))
        
        self.view_btn = tk.Button(
            buttons_frame,
            text="View Invoice",
            font=FONTS["regular_bold"],
            bg=COLORS["primary"],
            fg=COLORS["text_white"],
            padx=15,
            pady=5,
            cursor="hand2",
            state=tk.DISABLED,
            command=self.view_invoice
        )
        self.view_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.print_btn = tk.Button(
            buttons_frame,
            text="Print Invoice",
            font=FONTS["regular_bold"],
            bg=COLORS["secondary"],
            fg=COLORS["text_white"],
            padx=15,
            pady=5,
            cursor="hand2",
            state=tk.DISABLED,
            command=self.print_invoice
        )
        self.print_btn.grid(row=0, column=1)
    
    def on_date_component_change(self, event=None):
        """Handle date component (day, month, year) change"""
        try:
            day = int(self.day_var.get())
            month = int(self.month_var.get())
            year = int(self.year_var.get())
            
            # Validate the date
            # Handle month with less than 31 days
            max_day = 31
            if month in [4, 6, 9, 11]:  # Apr, Jun, Sep, Nov have 30 days
                max_day = 30
            elif month == 2:  # February has 28 or 29 days
                if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):  # Leap year
                    max_day = 29
                else:
                    max_day = 28
            
            # Adjust day if needed
            if day > max_day:
                day = max_day
                self.day_var.set(str(day).zfill(2))
            
            self.selected_date = datetime.date(year, month, day)
            self.load_sales()
        except ValueError:
            # Reset to today if invalid date
            today = datetime.date.today()
            self.day_var.set(str(today.day).zfill(2))
            self.month_var.set(str(today.month).zfill(2))
            self.year_var.set(str(today.year))
            self.selected_date = today
    
    def select_today(self):
        """Set date to today"""
        today = datetime.date.today()
        self.day_var.set(str(today.day).zfill(2))
        self.month_var.set(str(today.month).zfill(2))
        self.year_var.set(str(today.year))
        self.selected_date = today
        self.load_sales()
    
    def load_sales(self):
        """Load sales for the selected date"""
        # Clear existing data
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)
        
        # Reset details
        self.clear_details()
        
        # Format date for SQL query
        date_str = self.selected_date.strftime("%Y-%m-%d")
        
        # Query to get invoices for the selected date
        query = """
            SELECT i.id, i.invoice_number, c.name as customer_name, 
                   i.total_amount, i.payment_method, i.payment_status,
                   i.invoice_date, i.file_path
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            WHERE DATE(i.invoice_date) = ?
            ORDER BY i.invoice_date DESC
        """
        
        invoices = self.controller.db.fetchall(query, (date_str,))
        
        if not invoices:
            self.update_stats(0, 0)
            messagebox.showinfo("No Invoices", f"No invoices found for {self.selected_date.strftime('%d-%m-%Y')}.")
            return
        
        # Calculate total sales
        total_sales = sum(invoice[3] for invoice in invoices)
        invoice_count = len(invoices)
        
        # Update stats
        self.update_stats(total_sales, invoice_count)
        
        # Add invoices to treeview
        for invoice in invoices:
            # Parse invoice date for display
            invoice_time = datetime.datetime.strptime(invoice[6], "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
            
            self.sales_tree.insert(
                "",
                "end",
                values=(
                    invoice[1],                      # Invoice number
                    invoice[2] or "Walk-in Customer", # Customer name
                    format_currency(invoice[3]),     # Total amount
                    invoice[4],                      # Payment method
                    invoice_time                     # Time
                ),
                tags=(str(invoice[0]),)  # Store invoice ID as tag for selection
            )
    
    def search_invoices(self, event=None):
        """Search invoices based on search term"""
        search_term = self.search_var.get().lower()
        
        # If search term is empty, reload all invoices
        if not search_term:
            self.load_sales()
            return
        
        # Clear existing data
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)
        
        # Format date for SQL query
        date_str = self.selected_date.strftime("%Y-%m-%d")
        
        # Query to get invoices for the selected date matching search term
        query = """
            SELECT i.id, i.invoice_number, c.name as customer_name, 
                   i.total_amount, i.payment_method, i.payment_status,
                   i.invoice_date, i.file_path
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            WHERE DATE(i.invoice_date) = ?
              AND (i.invoice_number LIKE ? OR c.name LIKE ? OR i.payment_method LIKE ?)
            ORDER BY i.invoice_date DESC
        """
        
        search_pattern = f"%{search_term}%"
        invoices = self.controller.db.fetchall(
            query, 
            (date_str, search_pattern, search_pattern, search_pattern)
        )
        
        if not invoices:
            # No results found
            self.update_stats(0, 0)
            return
        
        # Calculate total sales for filtered results
        total_sales = sum(invoice[3] for invoice in invoices)
        invoice_count = len(invoices)
        
        # Update stats for filtered results
        self.update_stats(total_sales, invoice_count)
        
        # Add invoices to treeview
        for invoice in invoices:
            # Parse invoice date for display
            invoice_time = datetime.datetime.strptime(invoice[6], "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
            
            self.sales_tree.insert(
                "",
                "end",
                values=(
                    invoice[1],                      # Invoice number
                    invoice[2] or "Walk-in Customer", # Customer name
                    format_currency(invoice[3]),     # Total amount
                    invoice[4],                      # Payment method
                    invoice_time                     # Time
                ),
                tags=(str(invoice[0]),)  # Store invoice ID as tag for selection
            )
    
    def update_stats(self, total_sales, invoice_count):
        """Update stats display"""
        self.total_sales_label.config(text=f"Total Sales: {format_currency(total_sales)}")
        self.invoice_count_label.config(text=f"Invoices: {invoice_count}")
    
    def on_invoice_select(self, event=None):
        """Handle invoice selection in treeview"""
        selection = self.sales_tree.selection()
        if not selection:
            self.clear_details()
            return
        
        # Get invoice ID from tag with better error handling
        try:
            # Dump ALL item details to see exactly what we're working with
            all_item_details = self.sales_tree.item(selection[0])
            print(f"DEBUG: ALL selected item details: {all_item_details}")
            
            item_tags = self.sales_tree.item(selection[0], "tags")
            print(f"DEBUG: Selected item tags: {item_tags}")
            
            # Also print the item values to see what invoice number we're looking at
            item_values = self.sales_tree.item(selection[0], "values")
            print(f"DEBUG: Selected item values: {item_values}")
            
            if not item_tags:
                print("DEBUG: No tags found on selected item")
                # Try to recover - use the row directly 
                row_id = selection[0]
                try:
                    # See if the row's ID can be parsed as an invoice ID
                    if row_id.startswith("I"):
                        potential_id = int(row_id[1:]) # Skip the "I" prefix
                        print(f"DEBUG: Recovered potential ID from row_id: {potential_id}")
                        invoice_id = potential_id
                    else:
                        raise ValueError("Row ID not in expected format")
                except (ValueError, TypeError) as e:
                    print(f"DEBUG: Couldn't extract ID from row: {e}")
                    self.clear_details()
                    messagebox.showerror("Error", "This invoice record is missing its ID tag. Please try another invoice.")
                    return
            else:
                try:    
                    invoice_id = int(item_tags[0])
                except (IndexError, ValueError, TypeError) as e:
                    print(f"DEBUG: Error extracting invoice ID from tags: {e}")
                    self.clear_details()
                    messagebox.showerror("Error", "Could not determine invoice ID from selection.")
                    return
                
            print(f"DEBUG: Processing selection for invoice ID: {invoice_id}")
            
            # Check if invoice exists in either invoices or sales table
            check_query = """
                SELECT 
                    (SELECT COUNT(*) FROM invoices WHERE id = ?) as invoice_count,
                    (SELECT COUNT(*) FROM sales WHERE id = ?) as sale_count
            """
            check_result = self.controller.db.fetchone(check_query, (invoice_id, invoice_id))
            
            if not check_result:
                print(f"DEBUG: Failed to check if invoice ID {invoice_id} exists")
                self.clear_details()
                return
                
            invoice_exists = check_result[0] > 0
            sale_exists = check_result[1] > 0
            
            print(f"DEBUG: Invoice ID {invoice_id} exists in invoices: {invoice_exists}, in sales: {sale_exists}")
            
            # Determine which table to query based on existence
            if invoice_exists:
                # Query from invoices table
                query = """
                    SELECT 
                        i.id, i.invoice_number, i.customer_id, i.subtotal, 
                        i.discount_amount, i.tax_amount, i.total_amount, 
                        i.payment_method, i.payment_status, i.cash_amount, 
                        i.upi_amount, i.upi_reference, i.credit_amount, 
                        i.invoice_date, i.file_path,
                        c.name, c.phone, c.address
                    FROM invoices i
                    LEFT JOIN customers c ON i.customer_id = c.id
                    WHERE i.id = ?
                """
            elif sale_exists:
                # Query from sales table 
                query = """
                    SELECT 
                        s.id, s.invoice_number, s.customer_id, s.subtotal, 
                        s.discount_amount, s.tax_amount, s.total, 
                        s.payment_method, s.status, s.cash_amount, 
                        s.upi_amount, s.upi_reference, s.credit_amount, 
                        s.created_at, NULL as file_path,
                        c.name, c.phone, c.address
                    FROM sales s
                    LEFT JOIN customers c ON s.customer_id = c.id
                    WHERE s.id = ?
                """
            else:
                print(f"DEBUG: Invoice {invoice_id} not found in either table")
                self.clear_details()
                messagebox.showinfo("Not Found", f"Invoice #{invoice_id} could not be found in the database.")
                return
            
            # Fetch the record
            invoice = self.controller.db.fetchone(query, (invoice_id,))
            
            if not invoice:
                print(f"DEBUG: Query returned no results for ID: {invoice_id}")
                self.clear_details()
                return
            
            # Debug output to see what we're working with
            print(f"DEBUG: Found invoice: {invoice}")
            
            # Update UI with comprehensive error handling
            try:
                # Update customer info - safely handle missing data
                customer_name = invoice[15] if len(invoice) > 15 and invoice[15] else 'Walk-in Customer'
                customer_phone = invoice[16] if len(invoice) > 16 and invoice[16] else '-'
                customer_address = invoice[17] if len(invoice) > 17 and invoice[17] else '-'
                
                self.customer_name_label.config(text=f"Name: {customer_name}")
                self.customer_phone_label.config(text=f"Phone: {customer_phone}")
                self.customer_address_label.config(text=f"Address: {customer_address}")
                
                # Update invoice info
                invoice_number = invoice[1] if len(invoice) > 1 and invoice[1] else '-'
                self.invoice_number_label.config(text=f"Number: {invoice_number}")
                
                # Handle date formatting with comprehensive error handling
                try:
                    invoice_date = invoice[13] if len(invoice) > 13 else None
                    if invoice_date:
                        try:
                            formatted_date = format_date(invoice_date)
                        except:
                            # If format_date fails, try parsing first
                            formatted_date = format_date(parse_date(invoice_date))
                    else:
                        formatted_date = format_date(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                except Exception as e:
                    print(f"DEBUG: Error formatting date: {e}, using current date")
                    formatted_date = format_date(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                
                self.invoice_date_label.config(text=f"Date: {formatted_date}")
                
                # Total amount could be in different columns based on the table
                total_index = 6
                total = 0
                if len(invoice) > total_index:
                    try:
                        total = float(invoice[total_index]) if invoice[total_index] is not None else 0
                    except (ValueError, TypeError):
                        print(f"DEBUG: Error converting total to float: {invoice[total_index]}")
                
                self.invoice_amount_label.config(text=f"Amount: {format_currency(total)}")
                
                # Update payment info
                payment_method = invoice[7] if len(invoice) > 7 and invoice[7] else '-'
                payment_status = invoice[8] if len(invoice) > 8 and invoice[8] else 'PAID'
                
                self.payment_method_label.config(text=f"Method: {payment_method}")
                self.payment_status_label.config(text=f"Status: {payment_status}")
                
                # Add payment details based on method with safe data access
                payment_details = ""
                try:
                    if payment_method and payment_method.upper() == "SPLIT":
                        cash = invoice[9] if len(invoice) > 9 and invoice[9] is not None else 0
                        upi = invoice[10] if len(invoice) > 10 and invoice[10] is not None else 0
                        upi_ref = invoice[11] if len(invoice) > 11 and invoice[11] else ""
                        credit = invoice[12] if len(invoice) > 12 and invoice[12] is not None else 0
                        
                        payment_details = f"Cash: {format_currency(cash)}\n"
                        payment_details += f"UPI: {format_currency(upi)}\n"
                        if upi_ref:
                            payment_details += f"UPI Ref: {upi_ref}\n"
                        payment_details += f"Credit: {format_currency(credit)}"
                    elif payment_method and payment_method.upper() == "UPI":
                        upi_ref = invoice[11] if len(invoice) > 11 and invoice[11] else ""
                        if upi_ref:
                            payment_details = f"UPI Ref: {upi_ref}"
                    elif payment_method and payment_method.upper() == "CREDIT":
                        credit = invoice[12] if len(invoice) > 12 and invoice[12] is not None else 0
                        payment_details = f"Credit Amount: {format_currency(credit)}"
                except Exception as e:
                    print(f"DEBUG: Error creating payment details: {e}")
                
                self.payment_details_label.config(text=payment_details)
                
                # Handle buttons for view/print
                if invoice_exists and len(invoice) > 14:
                    file_path = invoice[14]  # file_path is at index 14 from invoices table
                    if file_path and os.path.exists(file_path):
                        print(f"DEBUG: Invoice file exists at: {file_path}")
                        self.view_btn.config(state=tk.NORMAL)
                        self.print_btn.config(state=tk.NORMAL)
                    else:
                        # Try with relative path
                        file_name = os.path.basename(file_path) if file_path else ""
                        rel_path = os.path.join(".", "invoices", file_name) if file_name else ""
                        
                        if rel_path and os.path.exists(rel_path):
                            print(f"DEBUG: Invoice file exists at relative path: {rel_path}")
                            self.view_btn.config(state=tk.NORMAL)
                            self.print_btn.config(state=tk.NORMAL)
                        else:
                            print(f"DEBUG: Invoice file not found at: {file_path} or {rel_path}")
                            self.view_btn.config(state=tk.DISABLED)
                            self.print_btn.config(state=tk.DISABLED)
                else:
                    # No file for sales or missing data
                    self.view_btn.config(state=tk.DISABLED)
                    self.print_btn.config(state=tk.DISABLED)
                
            except Exception as e:
                print(f"DEBUG: Error updating UI with invoice details: {e}")
                import traceback
                traceback.print_exc()
            
            # Load invoice items with the ID
            self.load_invoice_items(invoice_id)
            
        except Exception as e:
            print(f"DEBUG: Unhandled error in on_invoice_select: {e}")
            import traceback
            traceback.print_exc()
            self.clear_details()
    
    def load_invoice_items(self, invoice_id):
        """Load items for the selected invoice"""
        # Clear existing items
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
        
        print(f"DEBUG: Loading items for invoice ID: {invoice_id}")
        
        # First check if this is a valid invoice ID
        query_check = "SELECT COUNT(*) FROM invoices WHERE id = ?"
        result_check = self.controller.db.fetchone(query_check, (invoice_id,))
        has_invoice = result_check and result_check[0] > 0
        
        # Check if there's a corresponding sale ID
        query_check_sale = "SELECT COUNT(*) FROM sales WHERE id = ?"
        result_check_sale = self.controller.db.fetchone(query_check_sale, (invoice_id,))
        has_sale = result_check_sale and result_check_sale[0] > 0
        
        print(f"DEBUG: Invoice ID {invoice_id} exists in invoices table: {has_invoice}")
        print(f"DEBUG: Invoice ID {invoice_id} exists in sales table: {has_sale}")
        
        # Get the table schema to understand what columns are available
        try:
            print("DEBUG: Checking table schema for invoice_items")
            schema_query = "PRAGMA table_info(invoice_items)"
            schema = self.controller.db.fetchall(schema_query)
            print(f"DEBUG: invoice_items schema: {[col[1] for col in schema]}")
        except Exception as e:
            print(f"DEBUG: Error checking schema: {e}")
        
        # Search for invoice items with more rigorous error handling
        items = []
        
        # Try the invoice_items table if we have an invoice record
        if has_invoice:
            try:
                # Use a dynamic approach that checks column names first
                schema_query = "PRAGMA table_info(invoice_items)"
                schema = self.controller.db.fetchall(schema_query)
                column_names = [col[1] for col in schema]
                
                # Determine price column
                price_column = None
                for price_name in ['unit_price', 'price_per_unit', 'price']:
                    if price_name in column_names:
                        price_column = price_name
                        break
                
                # Default to 'unit_price' if we can't determine
                if not price_column:
                    price_column = 'unit_price'
                    print(f"DEBUG: Could not determine price column, using {price_column}")
                else:
                    print(f"DEBUG: Using {price_column} for price")
                
                # Build a more resilient query based on available columns
                query = f"""
                    SELECT 
                        COALESCE(p.name, 'Item ' || ii.product_id) as product_name,
                        COALESCE(ii.hsn_code, p.hsn_code, '-') as hsn_code,
                        COALESCE(ii.quantity, 0) as quantity,
                        COALESCE(ii.{price_column}, 0) as price,
                        COALESCE(ii.discount_percentage, 0) as discount,
                        COALESCE(ii.total_price, 0) as total
                    FROM invoice_items ii
                    LEFT JOIN products p ON ii.product_id = p.id
                    WHERE ii.invoice_id = ?
                """
                items = self.controller.db.fetchall(query, (invoice_id,))
                if items:
                    print(f"DEBUG: Found {len(items)} items in invoice_items table")
                    # Print first item for debugging
                    if len(items) > 0:
                        print(f"DEBUG: First item data: {items[0]}")
            except Exception as e:
                print(f"DEBUG: Error querying invoice_items: {e}")
                import traceback
                traceback.print_exc()
        
        # If no items found or no invoice, try the sale_items table
        if not items and has_sale:
            try:
                # Check schema of sale_items too
                schema_query = "PRAGMA table_info(sale_items)"
                schema = self.controller.db.fetchall(schema_query)
                column_names = [col[1] for col in schema]
                print(f"DEBUG: sale_items schema: {column_names}")
                
                # Determine discount column
                discount_column = 'discount_percentage'
                if 'discount_percentage' in column_names:
                    discount_column = 'discount_percentage'
                elif 'discount_percent' in column_names:
                    discount_column = 'discount_percent'
                
                query = f"""
                    SELECT 
                        COALESCE(si.product_name, 'Item ' || si.product_id) as product_name,
                        COALESCE(si.hsn_code, '-') as hsn_code,
                        COALESCE(si.quantity, 0) as quantity,
                        COALESCE(si.price, 0) as price,
                        COALESCE(si.{discount_column}, 0) as discount,
                        COALESCE(si.total, ROUND(COALESCE(si.quantity, 0) * COALESCE(si.price, 0) * (1 - COALESCE(si.{discount_column}, 0)/100), 2)) as total
                    FROM sale_items si
                    WHERE si.sale_id = ?
                """
                items = self.controller.db.fetchall(query, (invoice_id,))
                if items:
                    print(f"DEBUG: Found {len(items)} items in sale_items table")
                    # Print first item for debugging
                    if len(items) > 0:
                        print(f"DEBUG: First sale item data: {items[0]}")
            except Exception as e:
                print(f"DEBUG: Error querying sale_items: {e}")
                import traceback
                traceback.print_exc()
        
        # Check relationship between invoices and sales to try alternative approach
        if not items and has_invoice:
            try:
                print("DEBUG: Trying to find related sale for this invoice")
                # Try to find associated sale ID via invoice number
                query = """
                    SELECT s.id 
                    FROM sales s
                    JOIN invoices i ON s.invoice_number = i.invoice_number
                    WHERE i.id = ?
                """
                related_sale = self.controller.db.fetchone(query, (invoice_id,))
                
                if related_sale:
                    sale_id = related_sale[0]
                    print(f"DEBUG: Found related sale ID {sale_id} for invoice {invoice_id}")
                    
                    # Now query sale_items using this sale ID
                    query = """
                        SELECT 
                            COALESCE(si.product_name, 'Item ' || si.product_id) as product_name,
                            COALESCE(si.hsn_code, '-') as hsn_code,
                            COALESCE(si.quantity, 0) as quantity,
                            COALESCE(si.price, 0) as price,
                            COALESCE(si.discount_percentage, 0) as discount,
                            COALESCE(si.total, ROUND(COALESCE(si.quantity, 0) * COALESCE(si.price, 0) * (1 - COALESCE(si.discount_percentage, 0)/100), 2)) as total
                        FROM sale_items si
                        WHERE si.sale_id = ?
                    """
                    items = self.controller.db.fetchall(query, (sale_id,))
                    if items:
                        print(f"DEBUG: Found {len(items)} items in sale_items table via related sale")
            except Exception as e:
                print(f"DEBUG: Error finding related sale: {e}")
        
        # If still no items found, try a raw approach to get any data
        if not items:
            print(f"DEBUG: No items found in either table for ID {invoice_id}")
            try:
                # Get a raw dump of any invoice_items for this invoice_id
                raw_query = "SELECT * FROM invoice_items WHERE invoice_id = ?"
                raw_items = self.controller.db.fetchall(raw_query, (invoice_id,))
                
                if raw_items and len(raw_items) > 0:
                    print(f"DEBUG: Found {len(raw_items)} raw invoice_items")
                    # Print the raw data to understand structure
                    for i, raw_item in enumerate(raw_items):
                        print(f"DEBUG: Raw item {i+1}: {raw_item}")
                        
                        # Try to create proper display values
                        try:
                            product_id = raw_item[2] if len(raw_item) > 2 and raw_item[2] is not None else "Unknown"
                            # Try to get product name from products table
                            product_query = "SELECT name FROM products WHERE id = ?"
                            product_result = self.controller.db.fetchone(product_query, (product_id,))
                            product_name = product_result[0] if product_result else f"Product #{product_id}"
                            
                            # Find quantity, price and total based on column position
                            quantity = raw_item[4] if len(raw_item) > 4 and raw_item[4] is not None else 0
                            price = 0
                            for j in range(3, len(raw_item)):
                                if isinstance(raw_item[j], (int, float)) and raw_item[j] > 0 and raw_item[j] < 10000:
                                    # This is likely the price value
                                    price = raw_item[j]
                                    break
                            
                            # Total is likely one of the higher values
                            total = 0
                            for j in range(3, len(raw_item)):
                                if isinstance(raw_item[j], (int, float)) and raw_item[j] > price:
                                    # This is likely the total value
                                    total = raw_item[j]
                                    break
                            
                            # Create a display item
                            self.items_tree.insert(
                                "",
                                "end",
                                values=(
                                    product_name,
                                    "-",
                                    quantity,
                                    format_currency(price),
                                    "0",
                                    format_currency(total)
                                )
                            )
                        except Exception as e:
                            print(f"DEBUG: Error processing raw item: {e}")
                    
                    # If we processed items, return
                    if self.items_tree.get_children():
                        print("DEBUG: Successfully added items from raw data")
                        return
            except Exception as e:
                print(f"DEBUG: Error in raw query: {e}")
                import traceback
                traceback.print_exc()
            
            # If still nothing, add a placeholder item for better user experience
            self.items_tree.insert(
                "",
                "end",
                values=(
                    "No items found for this invoice",
                    "-",
                    "0",
                    "₹0.00",
                    "0",
                    "₹0.00"
                )
            )
            return
        
        # Add the items to the treeview
        for i, item in enumerate(items, 1):
            try:
                # Extract data with comprehensive error handling
                product_name = item[0] if item[0] and len(item) > 0 else "Unknown Product"
                hsn_code = item[1] if len(item) > 1 and item[1] else "-"
                
                try:
                    quantity = int(item[2]) if len(item) > 2 and item[2] is not None else 0
                except (ValueError, TypeError):
                    quantity = 0
                
                try:
                    price = float(item[3]) if len(item) > 3 and item[3] is not None else 0.0
                except (ValueError, TypeError):
                    price = 0.0
                
                try:
                    discount = float(item[4]) if len(item) > 4 and item[4] is not None else 0.0
                except (ValueError, TypeError):
                    discount = 0.0
                
                try:
                    total = float(item[5]) if len(item) > 5 and item[5] is not None else 0.0
                except (ValueError, TypeError):
                    total = 0.0
                
                # Create a unique ID for this row
                row_id = f"item_{invoice_id}_{i}"
                
                # Insert data into treeview
                self.items_tree.insert(
                    "",
                    "end",
                    iid=row_id,
                    values=(
                        product_name,
                        hsn_code,
                        quantity,
                        format_currency(price),
                        discount,
                        format_currency(total)
                    )
                )
                
                print(f"DEBUG: Added item {row_id}: {product_name}, {hsn_code}, {quantity}, {price}, {discount}, {total}")
            except Exception as e:
                print(f"DEBUG: Error adding item to treeview: {e}")
                import traceback
                traceback.print_exc()
        
        # Add a success message if items were added
        if self.items_tree.get_children():
            print(f"DEBUG: Successfully added {len(self.items_tree.get_children())} items to treeview")
        else:
            print("DEBUG: No items were added to the treeview despite finding data")
            # Add a placeholder item so the user sees something
            self.items_tree.insert(
                "",
                "end",
                values=(
                    "Items could not be displayed properly",
                    "-",
                    "0",
                    "₹0.00",
                    "0",
                    "₹0.00"
                )
            )
    
    def clear_details(self):
        """Clear all detail fields"""
        self.customer_name_label.config(text="Name: -")
        self.customer_phone_label.config(text="Phone: -")
        self.customer_address_label.config(text="Address: -")
        
        self.invoice_number_label.config(text="Number: -")
        self.invoice_date_label.config(text="Date: -")
        self.invoice_amount_label.config(text="Amount: -")
        
        self.payment_method_label.config(text="Method: -")
        self.payment_status_label.config(text="Status: -")
        self.payment_details_label.config(text="")
        
        self.view_btn.config(state=tk.DISABLED)
        self.print_btn.config(state=tk.DISABLED)
        
        # Clear items
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
    
    def view_invoice(self, event=None):
        """View the selected invoice"""
        selection = self.sales_tree.selection()
        if not selection:
            return
        
        # Get invoice ID from tag
        try:
            invoice_id = int(self.sales_tree.item(selection[0], "tags")[0])
            print(f"DEBUG: Viewing invoice with ID: {invoice_id}")
        except (IndexError, ValueError) as e:
            print(f"DEBUG: Error getting invoice ID from selection: {e}")
            messagebox.showerror("Error", "Unable to determine invoice ID. Please try selecting the invoice again.")
            return
        
        # Query to get invoice file path
        query = "SELECT file_path FROM invoices WHERE id = ?"
        result = self.controller.db.fetchone(query, (invoice_id,))
        
        if not result or not result[0]:
            print(f"DEBUG: Invoice file path not found in database for ID: {invoice_id}")
            # Try to regenerate the invoice if the file is missing
            if self.attempt_invoice_regeneration(invoice_id):
                # If regeneration succeeded, get the new path
                result = self.controller.db.fetchone(query, (invoice_id,))
                if not result or not result[0]:
                    messagebox.showerror("Error", "Invoice PDF file could not be regenerated.")
                    return
            else:
                messagebox.showerror("Error", "Invoice PDF file not found and could not be regenerated.")
                return
        
        file_path = result[0]
        print(f"DEBUG: Original invoice file path: {file_path}")
        
        # Fix absolute paths to use relative paths
        if file_path and (file_path.startswith('C:') or file_path.startswith('/')):
            # Convert absolute path to relative path
            print(f"DEBUG: Converting absolute path to relative")
            file_name = os.path.basename(file_path)
            file_path = os.path.join(".", "invoices", file_name)
            
            # Update the database with the fixed path
            self.controller.db.execute(
                "UPDATE invoices SET file_path = ? WHERE id = ?",
                (file_path, invoice_id)
            )
            self.controller.db.commit()
            print(f"DEBUG: Updated to relative path: {file_path}")
        
        # Ensure invoices directory exists
        invoices_dir = os.path.join(".", "invoices")
        os.makedirs(invoices_dir, exist_ok=True)
        
        # Check if file exists
        if not os.path.isfile(file_path):
            print(f"DEBUG: Invoice file does not exist at path: {file_path}")
            
            # Try regenerating the invoice
            regenerated = self.attempt_invoice_regeneration(invoice_id)
            
            # If regeneration succeeded, get new path
            if regenerated:
                # Get the new path
                result = self.controller.db.fetchone(query, (invoice_id,))
                if result and result[0]:
                    file_path = result[0]
                    print(f"DEBUG: Regenerated invoice with new path: {file_path}")
                else:
                    messagebox.showerror("Error", "Invoice regenerated but path is missing.")
                    return
            else:
                messagebox.showerror("Error", 
                                  f"Invoice PDF file not found at the expected location:\n{file_path}\n"
                                  "And automatic regeneration failed.")
                return
            
            # Check again if file exists after regeneration
            if not os.path.isfile(file_path):
                messagebox.showerror("Error", 
                                  f"Invoice PDF file still not found after regeneration attempt:\n{file_path}")
                return
        
        try:
            print(f"DEBUG: Attempting to open file: {file_path}")
            # Open the PDF with the default application
            import platform
            import subprocess
            print(f"DEBUG: Attempting to open file with platform-specific method on {platform.system()}")
            
            # Open PDF with default viewer
            if platform.system() == 'Windows':
                # Use subprocess instead of os.startfile for better cross-platform compatibility
                subprocess.call(['start', '', file_path], shell=True)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', file_path])
            else:  # Linux
                subprocess.call(['xdg-open', file_path])
                if os.name == 'posix':
                    subprocess.Popen(['xdg-open', file_path])
                else:
                    subprocess.Popen(['open', file_path])
                print("DEBUG: Subprocess call completed")
                
        except Exception as e:
            print(f"DEBUG: Error opening invoice: {e}")
            messagebox.showinfo(
                "File Location", 
                f"The invoice has been saved to:\n{os.path.abspath(file_path)}\n\n"
                "Please open this file to view the invoice."
            )
            
    def attempt_invoice_regeneration(self, invoice_id):
        """Attempt to regenerate a missing invoice file"""
        print(f"DEBUG: Attempting to regenerate invoice {invoice_id}")
        try:
            # First try to get invoice data from invoices table with detailed field selection
            query = """
                SELECT 
                    i.invoice_number, 
                    i.invoice_date, 
                    i.total_amount,
                    i.payment_method,
                    c.name as customer_name,
                    c.phone as customer_phone,
                    c.address as customer_address,
                    c.village as customer_village,
                    c.gstin as customer_gstin
                FROM 
                    invoices i
                LEFT JOIN 
                    customers c ON i.customer_id = c.id
                WHERE 
                    i.id = ?
            """
            invoice_data = self.controller.db.fetchone(query, (invoice_id,))
            
            # If not found, try the sales table as a fallback
            using_sales_table = False
            if not invoice_data:
                print(f"DEBUG: Invoice data not found in invoices table for ID: {invoice_id}")
                print(f"DEBUG: Trying to find data in sales table instead")
                
                # More detailed query to get all needed sales data
                sales_query = """
                    SELECT 
                        s.invoice_number, 
                        s.sale_date, 
                        s.total,
                        s.payment_type,
                        c.name as customer_name,
                        c.phone as customer_phone,
                        c.address as customer_address,
                        c.village as customer_village,
                        c.gstin as customer_gstin
                    FROM 
                        sales s
                    LEFT JOIN 
                        customers c ON s.customer_id = c.id
                    WHERE 
                        s.id = ?
                """
                invoice_data = self.controller.db.fetchone(sales_query, (invoice_id,))
                using_sales_table = True
                
                if not invoice_data:
                    print(f"DEBUG: Invoice data not found in sales table either for ID: {invoice_id}")
                    return False
            
            # Get the invoice items - first try invoice_items table with detailed product info
            items_query = """
                SELECT 
                    p.name as product_name,
                    p.hsn_code,
                    ii.quantity,
                    ii.price_per_unit as price,
                    ii.discount_percentage as discount,
                    ii.total_price as total,
                    ii.tax_percentage as tax_rate,
                    ii.tax_amount as tax_amount
                FROM 
                    invoice_items ii
                LEFT JOIN 
                    products p ON ii.product_id = p.id
                WHERE 
                    ii.invoice_id = ?
            """
            items = self.controller.db.fetchall(items_query, (invoice_id,))
            
            # If no items found, try sale_items table
            if not items:
                print(f"DEBUG: No items found in invoice_items for ID: {invoice_id}")
                print(f"DEBUG: Trying sale_items table")
                
                sale_items_query = """
                    SELECT 
                        product_name,
                        hsn_code,
                        quantity,
                        price,
                        discount_percent as discount,
                        total,
                        tax_percentage as tax_rate,
                        tax_amount
                    FROM 
                        sale_items
                    WHERE 
                        sale_id = ?
                """
                items = self.controller.db.fetchall(sale_items_query, (invoice_id,))
            
            if not items:
                print(f"DEBUG: No items found for invoice ID: {invoice_id}")
                return False
                
            # Initialize default values first
            invoice_number = f"INV-{invoice_id}"
            invoice_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            total_amount = 0.0
            payment_method = "CASH"
            customer = {
                "name": "Walk-in Customer",
                "phone": "",
                "address": "",
                "village": "",
                "gstin": ""
            }
            
            # Try to extract values from invoice_data
            try:
                if invoice_data and len(invoice_data) > 0:
                    invoice_number = invoice_data[0] if invoice_data[0] else f"INV-{invoice_id}"
                    
                    if len(invoice_data) > 1:
                        invoice_date = invoice_data[1] if invoice_data[1] else datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        
                    if len(invoice_data) > 2 and invoice_data[2] is not None:
                        total_amount = float(invoice_data[2])
                        
                    if len(invoice_data) > 3:
                        payment_method = invoice_data[3] if invoice_data[3] else "CASH"
                    
                    # More detailed customer information
                    if len(invoice_data) > 4:
                        customer = {
                            "name": invoice_data[4] or "Walk-in Customer",
                            "phone": invoice_data[5] if len(invoice_data) > 5 and invoice_data[5] else "",
                            "address": invoice_data[6] if len(invoice_data) > 6 and invoice_data[6] else "",
                            "village": invoice_data[7] if len(invoice_data) > 7 and invoice_data[7] else "",
                            "gstin": invoice_data[8] if len(invoice_data) > 8 and invoice_data[8] else ""
                        }
                
                print(f"DEBUG: Extracted invoice data - Number: {invoice_number}, Date: {invoice_date}, Total: {total_amount}")
                print(f"DEBUG: Customer: {customer['name']}, Phone: {customer['phone']}")
            except (IndexError, TypeError, ValueError) as e:
                print(f"DEBUG: Error extracting invoice details: {e}")
                # We already set default values above, so no need to handle missing values here
            
            # Format the items with better error handling
            formatted_items = []
            subtotal = 0.0
            tax_total = 0.0
            
            for item in items:
                try:
                    # Get values with default fallbacks
                    name = item[0] if item[0] else "Unknown Product"
                    hsn_code = item[1] if len(item) > 1 and item[1] else ""
                    quantity = float(item[2]) if len(item) > 2 and item[2] is not None else 0
                    price = float(item[3]) if len(item) > 3 and item[3] is not None else 0
                    discount = float(item[4]) if len(item) > 4 and item[4] is not None else 0
                    total = float(item[5]) if len(item) > 5 and item[5] is not None else 0
                    tax_rate = float(item[6]) if len(item) > 6 and item[6] is not None else 0
                    tax_amount = float(item[7]) if len(item) > 7 and item[7] is not None else 0
                    
                    # Build the item dictionary with all available information
                    item_dict = {
                        "name": name,
                        "hsn_code": hsn_code,
                        "quantity": quantity,
                        "price": price,
                        "discount": discount,
                        "total": total,
                        "tax_rate": tax_rate,
                        "tax_amount": tax_amount
                    }
                    
                    formatted_items.append(item_dict)
                    subtotal += (price * quantity)
                    tax_total += tax_amount
                    
                    print(f"DEBUG: Added invoice item: {name}, Qty: {quantity}, Price: {price}, Total: {total}")
                except (IndexError, TypeError, ValueError) as e:
                    print(f"DEBUG: Error processing invoice item: {e}, item data: {item}")
                    # Continue with other items
            
            # Safety check - if no items were processed successfully, return false
            if not formatted_items:
                print("DEBUG: No items could be processed successfully")
                return False
                
            # Import the invoice generator
            from utils.invoice_generator import generate_invoice
            
            # Format invoice data as expected by the generator
            invoice_data_dict = {
                'invoice_number': invoice_number,
                'date': invoice_date,
                'customer_name': customer['name'],
                'customer_phone': customer['phone'],
                'customer_address': customer['address'],
                'customer_village': customer.get('village', ''),
                'customer_gstin': customer.get('gstin', ''),
                'items': formatted_items,
                'payment_method': payment_method,
                'subtotal': subtotal,
                'tax_total': tax_total,
                'total': total_amount,
                'payment_status': 'PAID'  # Default to paid for regenerated invoices
            }
            
            # Create invoices directory if it doesn't exist - use relative path
            invoices_dir = os.path.join('.', 'invoices')
            if not os.path.exists(invoices_dir):
                os.makedirs(invoices_dir)
                
            # Generate path for the new invoice file - using relative path
            # Clean the invoice number to make a valid filename
            safe_invoice_number = invoice_number.replace('/', '-').replace('\\', '-').replace(':', '-')
            invoice_filename = f"INV_{safe_invoice_number}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
            file_path = os.path.join(invoices_dir, invoice_filename)
            
            # Debug output
            print(f"DEBUG: Creating regenerated invoice at: {os.path.abspath(file_path)}")
            print(f"DEBUG: Invoice data: {invoice_data_dict}")
            
            # Generate the new invoice file
            success = generate_invoice(invoice_data_dict, file_path)
            
            if success and os.path.exists(file_path):
                print(f"DEBUG: Invoice file created successfully at: {file_path}")
                
                # Check if this invoice exists in the invoices table
                check_query = "SELECT id FROM invoices WHERE id = ?"
                invoice_exists = self.controller.db.fetchone(check_query, (invoice_id,))
                
                if invoice_exists:
                    # Update existing invoice record with the new file path
                    update_query = "UPDATE invoices SET file_path = ? WHERE id = ?"
                    self.controller.db.execute(update_query, (file_path, invoice_id))
                    print(f"DEBUG: Updated existing invoice record with new file path")
                elif using_sales_table:
                    # This was a sales record that doesn't have a corresponding invoices record
                    # Get the invoice details from the sales table
                    sales_details = self.controller.db.fetchone("""
                        SELECT invoice_number, customer_id, subtotal, discount, tax, total, payment_type
                        FROM sales WHERE id = ?
                    """, (invoice_id,))
                    
                    if sales_details:
                        # Create a new entry in the invoices table
                        try:
                            self.controller.db.execute("""
                                INSERT INTO invoices
                                (id, invoice_number, customer_id, subtotal, tax_amount, total_amount, 
                                 payment_method, payment_status, file_path, invoice_date)
                                VALUES (?, ?, ?, ?, ?, ?, ?, 'PAID', ?, CURRENT_TIMESTAMP)
                            """, (
                                invoice_id,  # Use the same ID as the sales record
                                sales_details[0],  # invoice_number
                                sales_details[1],  # customer_id
                                sales_details[2],  # subtotal
                                sales_details[4],  # tax
                                sales_details[5],  # total
                                sales_details[6],  # payment_type/method
                                file_path
                            ))
                            print(f"DEBUG: Created new invoice record in invoices table from sales record")
                        except Exception as e:
                            print(f"DEBUG: Error creating invoice record: {e}")
                            # Even if the database insert fails, we still generated the invoice file
                
                self.controller.db.commit()
                print(f"DEBUG: Invoice regeneration process completed successfully")
                return True
            else:
                print(f"DEBUG: Invoice regeneration failed - generate_invoice returned {success}")
                return False
                
        except Exception as e:
            print(f"DEBUG: Error regenerating invoice: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def print_invoice(self):
        """Print the selected invoice"""
        selection = self.sales_tree.selection()
        if not selection:
            return
        
        # Get invoice ID from tag
        try:
            invoice_id = int(self.sales_tree.item(selection[0], "tags")[0])
            print(f"DEBUG: Printing invoice with ID: {invoice_id}")
        except (IndexError, ValueError) as e:
            print(f"DEBUG: Error getting invoice ID from selection: {e}")
            messagebox.showerror("Error", "Unable to determine invoice ID. Please try selecting the invoice again.")
            return
        
        # Query to get invoice file path
        query = "SELECT file_path FROM invoices WHERE id = ?"
        result = self.controller.db.fetchone(query, (invoice_id,))
        
        if not result or not result[0]:
            print(f"DEBUG: Invoice file path not found in database for ID: {invoice_id}")
            # Try to regenerate the invoice if the file is missing
            if self.attempt_invoice_regeneration(invoice_id):
                # If regeneration succeeded, get the new path
                result = self.controller.db.fetchone(query, (invoice_id,))
                if not result or not result[0]:
                    messagebox.showerror("Error", "Invoice PDF file could not be regenerated.")
                    return
            else:
                messagebox.showerror("Error", "Invoice PDF file not found and could not be regenerated.")
                return
        
        file_path = result[0]
        print(f"DEBUG: Invoice file path: {file_path}")
        
        # Check if file exists
        if not os.path.isfile(file_path):
            print(f"DEBUG: Invoice file does not exist at path: {file_path}")
            # Try to regenerate the invoice if the file is missing
            if self.attempt_invoice_regeneration(invoice_id):
                # If regeneration succeeded, get the new path
                result = self.controller.db.fetchone(query, (invoice_id,))
                if result and result[0] and os.path.isfile(result[0]):
                    file_path = result[0]
                else:
                    messagebox.showerror("Error", "Invoice PDF file could not be regenerated.")
                    return
            else:
                messagebox.showerror("Error", "Invoice PDF file not found and could not be regenerated.")
                return
        
        try:
            print(f"DEBUG: Attempting to print file: {file_path}")
            # Print the PDF
            import platform
            if platform.system() == 'Windows':
                # On Windows, open the file with the print operation or use default viewer
                messagebox.showinfo(
                    "Print Invoice", 
                    "Please use the file's print dialog to print the invoice.\n\n"
                    "The invoice will now open for printing."
                )
                # Use subprocess to open for printing - more compatible than startfile
                try:
                    # Try to use default print command
                    subprocess.call(['rundll32.exe', 'shell32.dll,ShellExec_RunDLL', 'print', file_path])
                except Exception as print_err:
                    print(f"DEBUG: Error using direct print command: {print_err}")
                    # Fall back to just opening the file
                    subprocess.call(['start', '', file_path], shell=True)
                print("DEBUG: Print command sent to Windows")
            else:
                # On Unix-like systems
                print("DEBUG: Attempting to print on Unix-like system")
                try:
                    # Try using lpr for printing
                    subprocess.call(['lpr', file_path])
                    messagebox.showinfo("Print Invoice", "Invoice has been sent to the default printer.")
                except Exception as print_err:
                    print(f"DEBUG: Error printing with lpr: {print_err}")
                    # Fall back to opening the file
                    if platform.system() == 'Darwin':  # macOS
                        subprocess.call(['open', file_path])
                    else:  # Linux
                        subprocess.call(['xdg-open', file_path])
                    messagebox.showinfo(
                        "Manual Printing Required", 
                        "Automated printing is not available.\n\n"
                        "The file has been opened. Please use the application's print function."
                    )
                print("DEBUG: Print command completed")
        except Exception as e:
            print(f"DEBUG: Error printing invoice: {e}")
            messagebox.showinfo(
                "Manual Printing Required", 
                "Automated printing is not available.\n\n"
                "Please open the file and print it manually."
            )
            self.view_invoice()
    
    def show_context_menu(self, event):
        """Show context menu for invoice list"""
        selection = self.sales_tree.selection()
        if not selection:
            return
        
        # Get invoice ID from tag
        try:
            invoice_id = int(self.sales_tree.item(selection[0], "tags")[0])
        except (IndexError, ValueError):
            return
        
        # Query to check if invoice has a file path
        query = "SELECT file_path FROM invoices WHERE id = ?"
        result = self.controller.db.fetchone(query, (invoice_id,))
        
        has_file = result and result[0] and os.path.isfile(result[0])
        
        # Create context menu
        context_menu = tk.Menu(self, tearoff=0)
        
        # Add menu items
        context_menu.add_command(label="View Details", command=self.on_invoice_select)
        
        # Always add view and print options, they will attempt regeneration if needed
        context_menu.add_command(label="View Invoice", command=self.view_invoice)
        context_menu.add_command(label="Print Invoice", command=self.print_invoice)
        
        # If invoice file is missing, add explicit regenerate option
        if not has_file:
            context_menu.add_separator()
            context_menu.add_command(
                label="Regenerate Invoice PDF", 
                command=lambda: self.regenerate_invoice_from_menu(invoice_id)
            )
        
        # Display the menu
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
            
    def regenerate_invoice_from_menu(self, invoice_id):
        """Explicitly regenerate an invoice from the context menu"""
        if self.attempt_invoice_regeneration(invoice_id):
            messagebox.showinfo(
                "Success", 
                "Invoice PDF has been regenerated successfully.\n"
                "You can now view or print the invoice."
            )
            # Update the selection to refresh buttons
            self.on_invoice_select()
        else:
            messagebox.showerror(
                "Error", 
                "Failed to regenerate the invoice PDF.\n"
                "Please check the application logs for more details."
            )
    
    def on_show(self):
        """Called when frame is shown"""
        # Load today's sales by default
        self.select_today()