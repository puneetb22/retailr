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
        main_container = tk.Frame(self, bg=COLORS["bg_primary"], padx=20, pady=20)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Title and date selection
        header_frame = tk.Frame(main_container, bg=COLORS["bg_primary"])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="Daily Sales History",
            font=FONTS["heading"],
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"]
        )
        title_label.pack(side=tk.LEFT)
        
        # Date filter controls
        date_frame = tk.Frame(header_frame, bg=COLORS["bg_primary"])
        date_frame.pack(side=tk.RIGHT)
        
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
        
        # Create main content area with sales list and details
        content_frame = tk.Frame(main_container, bg=COLORS["bg_primary"])
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Split into two panels - left for invoices list, right for details
        self.setup_sales_list(content_frame)
        self.setup_details_panel(content_frame)
    
    def setup_sales_list(self, parent):
        """Setup the sales/invoices list panel"""
        list_frame = tk.Frame(parent, bg=COLORS["bg_secondary"], padx=15, pady=15)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Title for list
        tk.Label(
            list_frame,
            text="Invoices",
            font=FONTS["subheading"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        ).pack(anchor="w", pady=(0, 10))
        
        # Stats for the selected day
        self.stats_frame = tk.Frame(list_frame, bg=COLORS["bg_secondary"])
        self.stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.total_sales_label = tk.Label(
            self.stats_frame,
            text="Total Sales: ₹0.00",
            font=FONTS["regular_bold"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        )
        self.total_sales_label.pack(side=tk.LEFT)
        
        self.invoice_count_label = tk.Label(
            self.stats_frame,
            text="Invoices: 0",
            font=FONTS["regular_bold"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            padx=20
        )
        self.invoice_count_label.pack(side=tk.LEFT)
        
        # Search frame
        search_frame = tk.Frame(list_frame, bg=COLORS["bg_secondary"])
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
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
            font=FONTS["regular"],
            width=20
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        search_entry.bind("<KeyRelease>", self.search_invoices)
        
        # Treeview for sales list
        columns = ("invoice_number", "customer", "amount", "payment", "time")
        self.sales_tree = ttk.Treeview(
            list_frame, 
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
        self.sales_tree.column("invoice_number", width=120, anchor="w")
        self.sales_tree.column("customer", width=150, anchor="w")
        self.sales_tree.column("amount", width=100, anchor="e")
        self.sales_tree.column("payment", width=100, anchor="center")
        self.sales_tree.column("time", width=80, anchor="center")
        
        # Create scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.sales_tree.yview)
        self.sales_tree.configure(yscrollcommand=scrollbar.set)
        
        # Place treeview and scrollbar
        self.sales_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.sales_tree.bind("<<TreeviewSelect>>", self.on_invoice_select)
        self.sales_tree.bind("<Double-1>", self.view_invoice)
        
        # Bind right-click context menu
        self.sales_tree.bind("<Button-3>", self.show_context_menu)
    
    def setup_details_panel(self, parent):
        """Setup the invoice details panel"""
        details_frame = tk.Frame(parent, bg=COLORS["bg_secondary"], padx=15, pady=15)
        details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(20, 0))
        
        # Title for details
        tk.Label(
            details_frame,
            text="Invoice Details",
            font=FONTS["subheading"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        ).pack(anchor="w", pady=(0, 15))
        
        # Customer and invoice info container
        info_frame = tk.Frame(details_frame, bg=COLORS["bg_secondary"])
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Customer info
        customer_frame = tk.Frame(info_frame, bg=COLORS["bg_secondary"])
        customer_frame.pack(side=tk.LEFT, anchor="nw", fill=tk.Y)
        
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
        
        # Invoice info
        invoice_frame = tk.Frame(info_frame, bg=COLORS["bg_secondary"])
        invoice_frame.pack(side=tk.RIGHT, anchor="ne", fill=tk.Y)
        
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
        
        # Invoice items
        tk.Label(
            details_frame,
            text="Items",
            font=FONTS["regular_bold"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        ).pack(anchor="w", pady=(0, 10))
        
        # Treeview for invoice items
        columns = ("item", "hsn", "qty", "price", "discount", "amount")
        self.items_tree = ttk.Treeview(
            details_frame, 
            columns=columns,
            show="headings",
            selectmode="browse",
            style="Custom.Treeview",
            height=10
        )
        
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
        
        # Create scrollbar
        items_scrollbar = ttk.Scrollbar(details_frame, orient="vertical", command=self.items_tree.yview)
        self.items_tree.configure(yscrollcommand=items_scrollbar.set)
        
        # Place treeview and scrollbar
        self.items_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        items_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Payment info
        payment_frame = tk.Frame(details_frame, bg=COLORS["bg_secondary"], pady=10)
        payment_frame.pack(fill=tk.X, pady=(15, 0))
        
        tk.Label(
            payment_frame,
            text="Payment Information",
            font=FONTS["regular_bold"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        ).pack(anchor="w", pady=(0, 5))
        
        self.payment_method_label = tk.Label(
            payment_frame,
            text="Method: -",
            font=FONTS["regular"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        )
        self.payment_method_label.pack(anchor="w")
        
        self.payment_status_label = tk.Label(
            payment_frame,
            text="Status: -",
            font=FONTS["regular"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        )
        self.payment_status_label.pack(anchor="w")
        
        self.payment_details_label = tk.Label(
            payment_frame,
            text="",
            font=FONTS["regular"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        )
        self.payment_details_label.pack(anchor="w")
        
        # Buttons frame at the bottom
        buttons_frame = tk.Frame(details_frame, bg=COLORS["bg_secondary"], pady=10)
        buttons_frame.pack(fill=tk.X, pady=(15, 0))
        
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
        self.view_btn.pack(side=tk.LEFT, padx=(0, 10))
        
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
        self.print_btn.pack(side=tk.LEFT)
    
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
        
        # Get invoice ID from tag
        invoice_id = int(self.sales_tree.item(selection[0], "tags")[0])
        
        # Query to get invoice details
        query = """
            SELECT i.*, c.name, c.phone, c.address
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            WHERE i.id = ?
        """
        
        invoice = self.controller.db.fetchone(query, (invoice_id,))
        
        if not invoice:
            self.clear_details()
            return
        
        # Update customer info
        self.customer_name_label.config(text=f"Name: {invoice[15] or 'Walk-in Customer'}")
        self.customer_phone_label.config(text=f"Phone: {invoice[16] or '-'}")
        self.customer_address_label.config(text=f"Address: {invoice[17] or '-'}")
        
        # Update invoice info
        self.invoice_number_label.config(text=f"Number: {invoice[1]}")
        self.invoice_date_label.config(text=f"Date: {format_date(invoice[14])}")
        self.invoice_amount_label.config(text=f"Amount: {format_currency(invoice[6])}")
        
        # Update payment info
        self.payment_method_label.config(text=f"Method: {invoice[7]}")
        self.payment_status_label.config(text=f"Status: {invoice[8]}")
        
        # Add payment details based on method
        payment_details = ""
        if invoice[7] == "SPLIT":
            payment_details = f"Cash: {format_currency(invoice[9])}\n"
            payment_details += f"UPI: {format_currency(invoice[10])}\n"
            if invoice[11]:  # UPI reference
                payment_details += f"UPI Ref: {invoice[11]}\n"
            payment_details += f"Credit: {format_currency(invoice[12])}"
        elif invoice[7] == "UPI" and invoice[11]:
            payment_details = f"UPI Ref: {invoice[11]}"
        elif invoice[7] == "CREDIT":
            payment_details = f"Credit Amount: {format_currency(invoice[12])}"
        
        self.payment_details_label.config(text=payment_details)
        
        # Enable buttons if invoice has a file path
        if invoice[14]:  # file_path
            self.view_btn.config(state=tk.NORMAL)
            self.print_btn.config(state=tk.NORMAL)
        else:
            self.view_btn.config(state=tk.DISABLED)
            self.print_btn.config(state=tk.DISABLED)
        
        # Load invoice items
        self.load_invoice_items(invoice_id)
    
    def load_invoice_items(self, invoice_id):
        """Load items for the selected invoice"""
        # Clear existing items
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
        
        # Query to get invoice items
        query = """
            SELECT ii.*, p.name, p.hsn_code
            FROM invoice_items ii
            JOIN products p ON ii.product_id = p.id
            WHERE ii.invoice_id = ?
        """
        
        items = self.controller.db.fetchall(query, (invoice_id,))
        
        if not items:
            return
        
        # Add items to treeview
        for i, item in enumerate(items, 1):
            self.items_tree.insert(
                "",
                "end",
                values=(
                    item[12],                      # Product name
                    item[13] or "-",               # HSN code
                    item[4],                       # Quantity
                    format_currency(item[5]),      # Price per unit
                    item[6],                       # Discount percentage
                    format_currency(item[8])       # Total price
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
        print(f"DEBUG: Invoice file path: {file_path}")
        
        # Check if file exists
        if not os.path.isfile(file_path):
            print(f"DEBUG: Invoice file does not exist at path: {file_path}")
            messagebox.showerror("Error", 
                              f"Invoice PDF file not found at the expected location:\n{file_path}\n"
                              "Please check if the file has been moved or deleted.")
            return
        
        try:
            print(f"DEBUG: Attempting to open file: {file_path}")
            # Open the PDF with the default application
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            else:  # macOS or Linux
                import subprocess
                print(f"DEBUG: Using subprocess to open the file on {os.name}")
                # Try to use the platform's default application
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
            # Get the invoice data
            query = """
                SELECT 
                    i.invoice_number, 
                    i.invoice_date, 
                    i.total_amount,
                    i.payment_method,
                    c.name as customer_name,
                    c.phone as customer_phone,
                    c.address as customer_address
                FROM 
                    invoices i
                LEFT JOIN 
                    customers c ON i.customer_id = c.id
                WHERE 
                    i.id = ?
            """
            invoice_data = self.controller.db.fetchone(query, (invoice_id,))
            
            if not invoice_data:
                print(f"DEBUG: Invoice data not found for ID: {invoice_id}")
                return False
                
            # Get the invoice items
            items_query = """
                SELECT 
                    p.name as product_name,
                    p.hsn_code,
                    ii.quantity,
                    ii.price,
                    ii.discount,
                    ii.total
                FROM 
                    invoice_items ii
                JOIN 
                    products p ON ii.product_id = p.id
                WHERE 
                    ii.invoice_id = ?
            """
            items = self.controller.db.fetchall(items_query, (invoice_id,))
            
            if not items:
                print(f"DEBUG: No items found for invoice ID: {invoice_id}")
                return False
                
            # Format the data for the invoice generator
            invoice_number = invoice_data[0]
            invoice_date = invoice_data[1]
            total_amount = invoice_data[2]
            payment_method = invoice_data[3]
            customer = {
                "name": invoice_data[4] or "Walk-in Customer",
                "phone": invoice_data[5] or "",
                "address": invoice_data[6] or ""
            }
            
            # Format the items
            formatted_items = []
            for item in items:
                formatted_items.append({
                    "name": item[0],
                    "hsn_code": item[1] or "",
                    "quantity": item[2],
                    "price": item[3],
                    "discount": item[4],
                    "total": item[5]
                })
                
            # Import the invoice generator
            from utils.invoice_generator import generate_invoice
            
            # Format invoice data as expected by the generator
            invoice_data = {
                'invoice_number': invoice_number,
                'date': invoice_date,
                'customer_name': customer['name'],
                'customer_phone': customer['phone'],
                'customer_address': customer['address'],
                'items': formatted_items,
                'payment_method': payment_method,
                'total': total_amount,
                'payment_status': 'PAID'  # Default to paid for regenerated invoices
            }
            
            # Create invoices directory if it doesn't exist
            invoices_dir = os.path.join(os.getcwd(), 'invoices')
            if not os.path.exists(invoices_dir):
                os.makedirs(invoices_dir)
                
            # Generate path for the new invoice file
            invoice_filename = f"INV_{invoice_number}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
            file_path = os.path.join(invoices_dir, invoice_filename)
            
            # Generate the new invoice file
            success = generate_invoice(invoice_data, file_path)
            
            if success and file_path:
                # Update the invoice record with the new file path
                update_query = "UPDATE invoices SET file_path = ? WHERE id = ?"
                self.controller.db.execute(update_query, (file_path, invoice_id))
                self.controller.db.commit()
                print(f"DEBUG: Invoice regenerated successfully: {file_path}")
                return True
            else:
                print(f"DEBUG: Invoice regeneration failed")
                return False
                
        except Exception as e:
            print(f"DEBUG: Error regenerating invoice: {e}")
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
            if os.name == 'nt':  # Windows
                # Using Acrobat Reader's command line printing (if available)
                messagebox.showinfo(
                    "Print Invoice", 
                    "Please use the file's print dialog to print the invoice.\n\n"
                    "The invoice will now open for printing."
                )
                os.startfile(file_path, "print")
                print("DEBUG: Print command sent to Windows")
            else:
                # On Unix-like systems
                print("DEBUG: Attempting to print on Unix-like system")
                subprocess.call(('lpr', file_path))
                messagebox.showinfo("Print Invoice", "Invoice has been sent to the default printer.")
                print("DEBUG: Print command sent to Unix printer")
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