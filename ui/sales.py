"""
Sales UI for POS system
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import datetime
import re
import os
import decimal
from decimal import Decimal, InvalidOperation

from assets.styles import COLORS, FONTS, STYLES
from utils.helpers import format_currency, parse_currency
from utils.invoice_generator import generate_invoice

class SalesFrame(tk.Frame):
    """Sales frame for processing transactions"""
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=COLORS["bg_primary"])
        self.controller = controller
        
        # Store cart items
        self.cart_items = []
        self.next_item_id = 1
        
        # Current customer
        self.current_customer = {
            "id": 1,  # Default to Walk-in Customer
            "name": "Walk-in Customer",
            "phone": "",
            "address": ""
        }
        
        # Create layout
        self.create_layout()
        
        # We now use the database for suspended bills
        # self.suspended_bills is kept for backward compatibility but not used
        
        # Keyboard navigation variables
        self.current_focus = None  # Current focus area: 'cart', 'products', 'buttons'
        self.selected_cart_item = -1
        self.selected_product_item = -1
        
        # Bind keyboard events
        self.bind("<Key>", self.handle_key_event)
        self.focus_set()
    
    def _set_dialog_transient(self, dialog):
        """Helper method to set dialog transient property correctly"""
        # Get the top-level window for this frame
        root = self.winfo_toplevel()
        dialog.transient(root)
        # Center dialog on parent
        x = self.winfo_x() + (self.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
    
    def create_layout(self):
        """Create the sales layout"""
        # Top customer search panel
        top_panel = tk.Frame(self, bg=COLORS["bg_primary"], padx=10, pady=8)
        top_panel.pack(fill=tk.X, padx=5, pady=(5, 0))
        
        # Customer search frame with dropdown, walk-in, new, and directory buttons
        self.setup_customer_search_panel(top_panel)
        
    def setup_customer_search_panel(self, parent):
        """Setup the customer search panel with dropdown and buttons"""
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
        self.customer_var.set("")  # Empty by default, no Walk-in Customer
        
        # Create autocomplete combobox
        self.customer_combo = ttk.Combobox(container, 
                                         textvariable=self.customer_var,
                                         font=FONTS["regular"],
                                         width=30)
        self.customer_combo.pack(side=tk.LEFT, padx=5)
        
        # Set default placeholder text
        if not self.customer_var.get():
            self.customer_combo.insert(0, "Search customers...")
        
        # Bind events for dropdown
        self.customer_combo.bind("<KeyRelease>", self.filter_customers)
        self.customer_combo.bind("<<ComboboxSelected>>", self.on_customer_selected)
        
        # Load initial customer list
        self.load_customers_for_dropdown()
        
        # Walk-in customer button
        walkin_btn = tk.Button(container,
                             text="Walk-in",
                             font=FONTS["regular"],
                             bg=COLORS["bg_secondary"],
                             fg=COLORS["text_primary"],
                             padx=10,
                             pady=3,
                             cursor="hand2",
                             command=self.set_walkin_customer)
        walkin_btn.pack(side=tk.LEFT, padx=5)
        
        # New customer button
        new_btn = tk.Button(container,
                          text="+ New",
                          font=FONTS["regular"],
                          bg=COLORS["secondary"],
                          fg=COLORS["text_white"],
                          padx=10,
                          pady=3,
                          cursor="hand2",
                          command=self.add_new_customer)
        new_btn.pack(side=tk.LEFT, padx=5)
        
        # Directory button
        dir_btn = tk.Button(container,
                          text="📁",
                          font=FONTS["regular_bold"],
                          bg=COLORS["primary"],
                          fg=COLORS["text_white"],
                          padx=8,
                          pady=3,
                          cursor="hand2",
                          command=self.open_customer_directory)
        dir_btn.pack(side=tk.LEFT, padx=5)
        
        # Main container with two frames side by side
        main_container = tk.Frame(self, bg=COLORS["bg_primary"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Cart (55% width)
        self.left_panel = tk.Frame(main_container, bg=COLORS["bg_primary"])
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Right panel - Product search and customer info (45% width)
        self.right_panel = tk.Frame(main_container, bg=COLORS["bg_secondary"], width=500)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Make sure the right panel maintains width
        self.right_panel.grid_propagate(False)  # For grid layout
        self.right_panel.pack_propagate(False)  # For pack layout
        
        # Setup left panel (cart)
        self.setup_cart_panel(self.left_panel)
        
        # Setup right panel (product search)
        self.setup_product_panel(self.right_panel)
        
        # Add keyboard shortcuts info
        shortcut_frame = tk.Frame(self.right_panel, bg=COLORS["bg_secondary"], padx=10, pady=5)
        shortcut_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        shortcut_label = tk.Label(
            shortcut_frame,
            text="Keyboard Shortcuts: Tab: Cycle focus | Ctrl+Shift+P: Products | Ctrl+Shift+C: Cart | Enter: Add/Edit",
            font=FONTS["small"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_secondary"],
            justify=tk.LEFT
        )
        shortcut_label.pack(anchor="w")
    def on_show(self):
        """Called when frame is shown"""
        # Reset the view
        self.load_products()
        
        # Load customers for dropdown
        self.load_customers_for_dropdown()
        
        # Set initial focus to products treeview
        self.current_focus = "products"
        
    def load_customers_for_dropdown(self):
        """Load customer list for dropdown"""
        db = self.controller.db
        query = """
            SELECT id, name, phone FROM customers
            ORDER BY name
            LIMIT 50
        """
        customers = db.fetchall(query)
        
        # Format customer list for combobox - no Walk-in customer by default
        customer_list = []
        self.customer_data = {}
        
        for i, customer in enumerate(customers):
            display_text = f"{customer[1]} ({customer[2] if customer[2] else 'No phone'})"
            customer_list.append(display_text)
            self.customer_data[i] = {"id": customer[0], "name": customer[1], "phone": customer[2] or ""}
        
        # Update combobox values
        self.customer_combo['values'] = customer_list
    
    def filter_customers(self, event):
        """Filter customers based on input in combobox"""
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
        query = """
            SELECT id, name, phone FROM customers
            WHERE LOWER(name) LIKE ? OR LOWER(phone) LIKE ?
            ORDER BY name
            LIMIT 50
        """
        
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
            self.customer_combo.event_generate('<Down>')
    
    def on_customer_selected(self, event):
        """Handle customer selection from dropdown"""
        selection = self.customer_combo.current()
        
        if selection >= 0 and selection in self.customer_data:
            customer_info = self.customer_data[selection]
            
            # Update current customer
            self.current_customer = {
                "id": customer_info["id"],
                "name": customer_info["name"],
                "phone": customer_info["phone"]
            }
            
            # Update customer label in cart panel
            self.customer_label.config(text=customer_info["name"])
    
    def set_walkin_customer(self):
        """Set customer to Walk-in Customer"""
        # Update combobox
        self.customer_var.set("")
        
        # Update current customer
        self.current_customer = {
            "id": 1,
            "name": "Walk-in Customer",
            "phone": ""
        }
        
        # Update customer label in cart panel
        self.customer_label.config(text="Walk-in Customer")
        
    def add_new_customer(self):
        """Open dialog to add a new customer and select them"""
        # Temporarily use a simplified version to avoid import issues
        # from ui.customer_management import add_customer_dialog
        def add_customer_dialog(controller):
            messagebox.showinfo("Feature Coming Soon", "Adding new customers will be available soon.")
            return None
        
        # Open customer add dialog
        new_customer = add_customer_dialog(self.controller)
        
        if new_customer:
            # Update current customer
            self.current_customer = {
                "id": new_customer["id"],
                "name": new_customer["name"],
                "phone": new_customer["phone"]
            }
            
            # Update customer label in cart panel
            self.customer_label.config(text=new_customer["name"])
            
            # Update customer dropdown
            self.customer_var.set(f"{new_customer['name']} ({new_customer['phone'] if new_customer['phone'] else 'No phone'})")
            
            # Reload customer list to include the new customer
            self.load_customers_for_dropdown()
            
    def open_customer_directory(self):
        """Open customer directory dialog to select a customer"""
        # Temporarily use a simplified version to avoid import issues
        # from ui.customer_management import select_customer_dialog
        def select_customer_dialog(controller):
            messagebox.showinfo("Feature Coming Soon", "Customer directory will be available soon.")
            return None
        
        # Open customer select dialog
        selected_customer = select_customer_dialog(self.controller)
        
        if selected_customer:
            # Update current customer
            self.current_customer = {
                "id": selected_customer["id"],
                "name": selected_customer["name"],
                "phone": selected_customer["phone"]
            }
            
            # Update customer label in cart panel
            self.customer_label.config(text=selected_customer["name"])
            
            # Update customer dropdown
            self.customer_var.set(f"{selected_customer['name']} ({selected_customer['phone'] if selected_customer['phone'] else 'No phone'})")
            
    def setup_cart_panel(self, parent):
        """Setup the cart panel (left side)"""
        # Cart header with customer and total info
        header_frame = tk.Frame(parent, bg=COLORS["bg_primary"])
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Customer information (first row)
        customer_info_frame = tk.Frame(header_frame, bg=COLORS["bg_primary"])
        customer_info_frame.pack(fill=tk.X, pady=(0, 5))
        
        customer_header = tk.Label(
            customer_info_frame,
            text="Current Customer:",
            font=FONTS["small_bold"],
            bg=COLORS["bg_primary"],
            fg=COLORS["text_secondary"]
        )
        customer_header.pack(side=tk.LEFT)
        
        # This label will be updated when customer is changed
        self.customer_label = tk.Label(
            customer_info_frame,
            text=self.current_customer["name"],
            font=FONTS["regular_bold"],
            bg=COLORS["bg_primary"],
            fg=COLORS["primary"]
        )
        self.customer_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Cart items heading with column labels
        columns_frame = tk.Frame(parent, bg=COLORS["bg_secondary"])
        columns_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        columns = [
            {"text": "#", "width": 30},
            {"text": "Item", "width": 200},
            {"text": "Price", "width": 80},
            {"text": "Qty", "width": 50},
            {"text": "Discount", "width": 80},
            {"text": "Total", "width": 100}
        ]
        
        for col in columns:
            lbl = tk.Label(
                columns_frame,
                text=col["text"],
                font=FONTS["small_bold"],
                width=0,  # Use pixel width instead
                bg=COLORS["bg_secondary"],
                fg=COLORS["text_primary"],
                anchor="w" if col["text"] == "Item" else "center",
                padx=5,
                pady=5
            )
            lbl.pack(side=tk.LEFT, fill=tk.BOTH, expand=(col["text"] == "Item"))
            lbl.config(width=col["width"])  # Set pixel width
        
        # Cart items list (Treeview)
        self.cart_tree_frame = tk.Frame(parent, bg=COLORS["bg_primary"])
        self.cart_tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Setup scrollbar for cart treeview
        cart_scroll = ttk.Scrollbar(self.cart_tree_frame)
        cart_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Cart treeview
        self.cart_tree = ttk.Treeview(
            self.cart_tree_frame,
            columns=("id", "name", "price", "qty", "discount", "total", "product_id"),
            show="tree",
            selectmode="browse",
            height=10
        )
        self.cart_tree.pack(fill=tk.BOTH, expand=True)
        
        # Configure the scrollbar
        cart_scroll.config(command=self.cart_tree.yview)
        self.cart_tree.config(yscrollcommand=cart_scroll.set)
        
        # Configure column widths and headings
        self.cart_tree.column("#0", width=30, stretch=tk.NO)  # Item number column
        self.cart_tree.column("id", width=0, stretch=tk.NO)  # Hidden column
        self.cart_tree.column("name", width=200, stretch=tk.YES)
        self.cart_tree.column("price", width=80, stretch=tk.NO)
        self.cart_tree.column("qty", width=50, stretch=tk.NO)
        self.cart_tree.column("discount", width=80, stretch=tk.NO)
        self.cart_tree.column("total", width=100, stretch=tk.NO)
        self.cart_tree.column("product_id", width=0, stretch=tk.NO)  # Hidden column
        
        # Bind events to the cart treeview
        self.cart_tree.bind("<Double-1>", self.edit_cart_item)
        self.cart_tree.bind("<Delete>", self.remove_cart_item)
        self.cart_tree.bind("<Return>", self.edit_cart_item)  # Enter key
        
        # Cart actions frame (buttons)
        cart_actions = tk.Frame(parent, bg=COLORS["bg_primary"])
        cart_actions.pack(fill=tk.X, padx=5, pady=5)
        
        # Cart action buttons - first row
        cart_buttons_row1 = tk.Frame(cart_actions, bg=COLORS["bg_primary"])
        cart_buttons_row1.pack(fill=tk.X, pady=(0, 5))
        
        # Add item button
        add_item_btn = tk.Button(
            cart_buttons_row1,
            text="Add Item",
            font=FONTS["regular_bold"],
            bg=COLORS["primary"],
            fg=COLORS["text_white"],
            padx=15,
            pady=8,
            cursor="hand2",
            command=self.add_custom_item
        )
        add_item_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Edit item button
        edit_item_btn = tk.Button(
            cart_buttons_row1,
            text="Edit Item",
            font=FONTS["regular_bold"],
            bg=COLORS["secondary"],
            fg=COLORS["text_white"],
            padx=15,
            pady=8,
            cursor="hand2",
            command=lambda: self.edit_cart_item(None)
        )
        edit_item_btn.pack(side=tk.LEFT, padx=5)
        
        # Remove item button
        remove_item_btn = tk.Button(
            cart_buttons_row1,
            text="Remove Item",
            font=FONTS["regular_bold"],
            bg=COLORS["danger"],
            fg=COLORS["text_white"],
            padx=15,
            pady=8,
            cursor="hand2",
            command=lambda: self.remove_cart_item(None)
        )
        remove_item_btn.pack(side=tk.LEFT, padx=5)
        
        # Cart action buttons - second row
        cart_buttons_row2 = tk.Frame(cart_actions, bg=COLORS["bg_primary"])
        cart_buttons_row2.pack(fill=tk.X, pady=(0, 5))
        
        # Clear cart button
        clear_cart_btn = tk.Button(
            cart_buttons_row2,
            text="Clear Cart",
            font=FONTS["regular_bold"],
            bg=COLORS["warning"],
            fg=COLORS["text_primary"],
            padx=15,
            pady=8,
            cursor="hand2",
            command=self.clear_cart
        )
        clear_cart_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Apply discount button
        apply_discount_btn = tk.Button(
            cart_buttons_row2,
            text="Apply Discount",
            font=FONTS["regular_bold"],
            bg=COLORS["success"],
            fg=COLORS["text_white"],
            padx=15,
            pady=8,
            cursor="hand2",
            command=self.apply_cart_discount
        )
        apply_discount_btn.pack(side=tk.LEFT, padx=5)
        
        # Suspend sale button
        suspend_btn = tk.Button(
            cart_buttons_row2,
            text="Suspend Sale",
            font=FONTS["regular_bold"],
            bg=COLORS["secondary"],
            fg=COLORS["text_white"],
            padx=15,
            pady=8,
            cursor="hand2",
            command=self.suspend_sale
        )
        suspend_btn.pack(side=tk.LEFT, padx=5)
        
        # Cart totals frame
        cart_totals = tk.Frame(parent, bg=COLORS["bg_primary"], pady=5)
        cart_totals.pack(fill=tk.X, padx=5, pady=5)
        
        # Subtotal
        subtotal_frame = tk.Frame(cart_totals, bg=COLORS["bg_primary"])
        subtotal_frame.pack(fill=tk.X, pady=2)
        
        subtotal_label = tk.Label(
            subtotal_frame,
            text="Subtotal:",
            font=FONTS["regular"],
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"],
            anchor="e"
        )
        subtotal_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.subtotal_var = tk.StringVar()
        self.subtotal_var.set("₹0.00")
        
        subtotal_value = tk.Label(
            subtotal_frame,
            textvariable=self.subtotal_var,
            font=FONTS["regular_bold"],
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"]
        )
        subtotal_value.pack(side=tk.LEFT)
        
        # Tax
        tax_frame = tk.Frame(cart_totals, bg=COLORS["bg_primary"])
        tax_frame.pack(fill=tk.X, pady=2)
        
        tax_label = tk.Label(
            tax_frame,
            text="Tax (18%):",
            font=FONTS["regular"],
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"],
            anchor="e"
        )
        tax_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.tax_var = tk.StringVar()
        self.tax_var.set("₹0.00")
        
        tax_value = tk.Label(
            tax_frame,
            textvariable=self.tax_var,
            font=FONTS["regular_bold"],
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"]
        )
        tax_value.pack(side=tk.LEFT)
        
        # Discount
        discount_frame = tk.Frame(cart_totals, bg=COLORS["bg_primary"])
        discount_frame.pack(fill=tk.X, pady=2)
        
        discount_label = tk.Label(
            discount_frame,
            text="Discount:",
            font=FONTS["regular"],
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"],
            anchor="e"
        )
        discount_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.discount_var = tk.StringVar()
        self.discount_var.set("₹0.00")
        
        discount_value = tk.Label(
            discount_frame,
            textvariable=self.discount_var,
            font=FONTS["regular_bold"],
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"]
        )
        discount_value.pack(side=tk.LEFT)
        
        # Grand Total (with a separator line)
        separator = ttk.Separator(cart_totals, orient="horizontal")
        separator.pack(fill=tk.X, pady=5)
        
        total_frame = tk.Frame(cart_totals, bg=COLORS["bg_primary"])
        total_frame.pack(fill=tk.X, pady=2)
        
        total_label = tk.Label(
            total_frame,
            text="TOTAL:",
            font=FONTS["heading"],
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"],
            anchor="e"
        )
        total_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.total_var = tk.StringVar()
        self.total_var.set("₹0.00")
        
        total_value = tk.Label(
            total_frame,
            textvariable=self.total_var,
            font=FONTS["heading"],
            bg=COLORS["bg_primary"],
            fg=COLORS["primary"]
        )
        total_value.pack(side=tk.LEFT)
        
        # Checkout button
        checkout_frame = tk.Frame(parent, bg=COLORS["bg_primary"])
        checkout_frame.pack(fill=tk.X, padx=5, pady=10)
        
        checkout_btn = tk.Button(
            checkout_frame,
            text="CHECKOUT",
            font=FONTS["heading"],
            bg=COLORS["success"],
            fg=COLORS["text_white"],
            padx=20,
            pady=12,
            cursor="hand2",
            command=self.checkout
        )
        checkout_btn.pack(fill=tk.X)
        
        # Keep reference to the cart tree for focus management
        self.cart_tree.bind("<FocusIn>", lambda e: self._set_focus_area("cart"))
        
    def setup_product_panel(self, parent):
        """Setup the product panel (right side)"""
        # Header frame with search option
        header_frame = tk.Frame(parent, bg=COLORS["bg_secondary"], padx=10, pady=8)
        header_frame.pack(fill=tk.X)
        
        search_label = tk.Label(
            header_frame,
            text="Search Products:",
            font=FONTS["regular_bold"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        )
        search_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_change)
        
        search_entry = tk.Entry(
            header_frame,
            textvariable=self.search_var,
            font=FONTS["regular"],
            width=25
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Product list
        list_frame = tk.Frame(parent, bg=COLORS["bg_secondary"])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        
        # Search result count
        self.result_label = tk.Label(
            list_frame,
            text="",
            font=FONTS["small"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_secondary"],
            anchor="w"
        )
        self.result_label.pack(fill=tk.X, pady=(0, 5))
        
        # Products treeview frame with scrollbar
        product_tree_frame = tk.Frame(list_frame, bg=COLORS["bg_secondary"])
        product_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        product_scroll = ttk.Scrollbar(product_tree_frame)
        product_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Products treeview
        self.product_tree = ttk.Treeview(
            product_tree_frame,
            columns=("id", "name", "price", "stock", "category"),
            show="headings",
            selectmode="browse",
            height=20
        )
        self.product_tree.pack(fill=tk.BOTH, expand=True)
        
        # Configure the scrollbar
        product_scroll.config(command=self.product_tree.yview)
        self.product_tree.config(yscrollcommand=product_scroll.set)
        
        # Configure columns
        self.product_tree.column("id", width=0, stretch=tk.NO)  # Hidden column
        self.product_tree.column("name", width=200, anchor="w")
        self.product_tree.column("price", width=80, anchor="e")
        self.product_tree.column("stock", width=60, anchor="center")
        self.product_tree.column("category", width=100, anchor="center")
        
        # Configure headings
        self.product_tree.heading("id", text="ID")
        self.product_tree.heading("name", text="Product Name")
        self.product_tree.heading("price", text="Price")
        self.product_tree.heading("stock", text="Stock")
        self.product_tree.heading("category", text="Category")
        
        # Bind events
        self.product_tree.bind("<Double-1>", self.add_to_cart)
        self.product_tree.bind("<Return>", self.add_to_cart)  # Enter key
        self.product_tree.bind("<FocusIn>", lambda e: self._set_focus_area("products"))
        
        # Action buttons
        buttons_frame = tk.Frame(parent, bg=COLORS["bg_secondary"], padx=10, pady=8)
        buttons_frame.pack(fill=tk.X, pady=5)
        
        add_to_cart_btn = tk.Button(
            buttons_frame,
            text="Add to Cart",
            font=FONTS["regular_bold"],
            bg=COLORS["primary"],
            fg=COLORS["text_white"],
            padx=15,
            pady=8,
            cursor="hand2",
            command=lambda: self.add_to_cart(None)
        )
        add_to_cart_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        refresh_btn = tk.Button(
            buttons_frame,
            text="Refresh",
            font=FONTS["regular"],
            bg=COLORS["bg_light"],
            fg=COLORS["text_primary"],
            padx=15,
            pady=8,
            cursor="hand2",
            command=self.load_products
        )
        refresh_btn.pack(side=tk.LEFT)
        
        # Category filter
        category_frame = tk.Frame(parent, bg=COLORS["bg_secondary"], padx=10, pady=8)
        category_frame.pack(fill=tk.X, pady=(0, 5))
        
        category_label = tk.Label(
            category_frame,
            text="Filter by Category:",
            font=FONTS["regular"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        )
        category_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.category_var = tk.StringVar()
        self.category_var.set("All Categories")
        
        # Get categories from database
        categories = ["All Categories"]
        try:
            db = self.controller.db
            category_query = "SELECT DISTINCT category FROM products WHERE category IS NOT NULL ORDER BY category"
            results = db.fetchall(category_query)
            for row in results:
                if row[0] and row[0].strip():  # Skip empty categories
                    categories.append(row[0])
        except Exception as e:
            print(f"Error loading categories: {str(e)}")
        
        self.category_combo = ttk.Combobox(
            category_frame,
            values=categories,
            textvariable=self.category_var,
            state="readonly",
            font=FONTS["regular"],
            width=20
        )
        self.category_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Bind category change event
        self.category_combo.bind("<<ComboboxSelected>>", lambda e: self.load_products())
        
    # Other required methods 
    def _on_search_change(self, *args):
        """Handle search text changes"""
        self.load_products()
        
    def _set_focus_area(self, area):
        """Set the current focus area"""
        self.current_focus = area
        
    def load_products(self):
        """Load products based on search and category filters"""
        search_term = self.search_var.get().strip().lower()
        category = self.category_var.get()
        
        # Clear the treeview
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
            
        try:
            # Connect to database
            db = self.controller.db
            
            # Base query
            query = """
                SELECT p.id, p.name, p.selling_price, 
                       (SELECT SUM(i.quantity) FROM inventory i WHERE i.product_id = p.id) AS quantity, 
                       p.category 
                FROM products p
                WHERE 1=1
            """
            params = []
            
            # Add search filter if search term is provided
            if search_term:
                query += " AND (LOWER(p.name) LIKE ? OR LOWER(p.barcode) LIKE ?)"
                params.extend([f"%{search_term}%", f"%{search_term}%"])
                
            # Add category filter if a specific category is selected
            if category and category != "All Categories":
                query += " AND p.category = ?"
                params.append(category)
                
            # Add sorting
            query += " ORDER BY p.name"
            
            # Execute query
            products = db.fetchall(query, tuple(params))
            
            # Update result count
            self.result_label.config(text=f"Showing {len(products)} result{'s' if len(products) != 1 else ''}")
            
            # Add products to treeview
            for product in products:
                # Format price and stock
                price_str = format_currency(product[2])
                stock_str = str(product[3]) if product[3] is not None else "N/A"
                
                # Insert into treeview
                self.product_tree.insert("", "end", values=(
                    product[0],  # ID
                    product[1],  # Name
                    price_str,   # Price
                    stock_str,   # Stock
                    product[4] or "Uncategorized"  # Category
                ))
                
        except Exception as e:
            print(f"Error loading products: {str(e)}")
            self.result_label.config(text="Error loading products")
            
    def add_to_cart(self, event=None):
        """Add selected product to cart"""
        # Get selected product
        selection = self.product_tree.selection()
        if not selection:
            return
            
        item = self.product_tree.item(selection[0])
        product_id = item["values"][0]
        product_name = item["values"][1]
        price_str = item["values"][2]
        
        # Parse the price (remove currency symbol)
        price = parse_currency(price_str)
        
        # Open quantity dialog
        quantity = simpledialog.askfloat(
            "Enter Quantity", 
            f"Enter quantity for {product_name}:",
            parent=self,
            minvalue=0.001,
            initialvalue=1.0
        )
        
        if quantity is None:
            return  # User cancelled
            
        # Add to cart
        self._add_product_to_cart(product_id, product_name, price, quantity)
        
    def _add_product_to_cart(self, product_id, product_name, price, quantity, discount=0.0):
        """Internal method to add a product to the cart"""
        # Calculate total
        total = price * quantity - discount
        
        # Create a unique item ID for this cart entry
        item_id = self.next_item_id
        self.next_item_id += 1
        
        # Add to cart items list
        self.cart_items.append({
            "id": item_id,
            "product_id": product_id,
            "name": product_name,
            "price": price,
            "quantity": quantity,
            "discount": discount,
            "total": total
        })
        
        # Insert into cart treeview
        self.cart_tree.insert(
            "", "end", 
            text=str(len(self.cart_items)),
            values=(
                item_id,
                product_name,
                format_currency(price),
                f"{quantity:.3f}".rstrip('0').rstrip('.') if quantity == int(quantity) else f"{quantity:.3f}",
                format_currency(discount),
                format_currency(total),
                product_id
            )
        )
        
        # Update cart totals
        self._update_cart_totals()
        
    def _update_cart_totals(self):
        """Update cart total calculations"""
        subtotal = sum(item["total"] for item in self.cart_items)
        
        # Apply tax (18%)
        tax_rate = 0.18  # 18% GST
        tax = subtotal * tax_rate
        
        # Total discount (sum of all item discounts)
        total_discount = sum(item["discount"] for item in self.cart_items)
        
        # Grand total
        total = subtotal + tax
        
        # Update display
        self.subtotal_var.set(format_currency(subtotal))
        self.tax_var.set(format_currency(tax))
        self.discount_var.set(format_currency(total_discount))
        self.total_var.set(format_currency(total))
        
    def add_custom_item(self):
        """Add a custom item to the cart"""
        pass  # Placeholder
        
    def edit_cart_item(self, event=None):
        """Edit the selected cart item"""
        pass  # Placeholder
        
    def remove_cart_item(self, event=None):
        """Remove the selected cart item"""
        pass  # Placeholder
        
    def clear_cart(self):
        """Clear all items from the cart"""
        pass  # Placeholder
        
    def apply_cart_discount(self):
        """Apply a discount to the entire cart"""
        pass  # Placeholder
        
    def suspend_sale(self):
        """Suspend the current sale for later retrieval"""
        pass  # Placeholder
        
    def checkout(self):
        """Process checkout"""
        pass  # Placeholder
        
    def handle_key_event(self, event):
        """Handle keyboard events for navigation and shortcuts"""
        pass  # Placeholder