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
        
        # Keep track of suspended bills
        self.suspended_bills = []
        
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
    
    def setup_cart_panel(self, parent):
        """Setup the cart panel with item list and totals"""
        # Customer info frame with border and better visual styling
        customer_frame = tk.Frame(parent, bg=COLORS["bg_secondary"], pady=8, padx=5, relief=tk.GROOVE, bd=1)
        customer_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Customer info
        tk.Label(customer_frame, 
               text="Customer:",
               font=FONTS["regular_bold"],
               bg=COLORS["bg_secondary"],
               fg=COLORS["text_primary"]).pack(side=tk.LEFT, padx=(5, 5))
               
        self.customer_label = tk.Label(customer_frame, 
                                     text="Walk-in Customer",
                                     font=FONTS["regular"],
                                     bg=COLORS["bg_secondary"],
                                     fg=COLORS["text_primary"])
        self.customer_label.pack(side=tk.LEFT)
        
        # Change customer button - made more prominent
        change_customer_btn = tk.Button(customer_frame,
                                      text="Change Customer",
                                      font=FONTS["regular_bold"],
                                      bg=COLORS["primary"],
                                      fg=COLORS["text_white"],
                                      padx=10,
                                      pady=2,
                                      cursor="hand2",
                                      command=self.change_customer)
        change_customer_btn.pack(side=tk.RIGHT, padx=10)
        
        # Add new customer button
        add_customer_btn = tk.Button(customer_frame,
                                   text="+ New",
                                   font=FONTS["small"],
                                   bg=COLORS["secondary"],
                                   fg=COLORS["text_white"],
                                   padx=8,
                                   pady=2,
                                   cursor="hand2",
                                   command=lambda: self.change_customer(add_new=True))
        add_customer_btn.pack(side=tk.RIGHT, padx=5)
        
        # Cart label
        cart_label = tk.Label(parent, 
                             text="Cart Items",
                             font=FONTS["subheading"],
                             bg=COLORS["bg_primary"],
                             fg=COLORS["text_primary"])
        cart_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Cart treeview frame
        tree_frame = tk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
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
        
        # Create treeview for cart items
        self.cart_tree = ttk.Treeview(tree_frame, 
                                    columns=("id", "product", "price", "qty", "discount", "total"),
                                    show="headings",
                                    yscrollcommand=scrollbar.set)
        
        # Configure scrollbar
        scrollbar.config(command=self.cart_tree.yview)
        
        # Define columns
        self.cart_tree.heading("id", text="#")
        self.cart_tree.heading("product", text="Product")
        self.cart_tree.heading("price", text="Price")
        self.cart_tree.heading("qty", text="Qty")
        self.cart_tree.heading("discount", text="Disc %")
        self.cart_tree.heading("total", text="Total")
        
        # Set column widths
        self.cart_tree.column("id", width=50)
        self.cart_tree.column("product", width=250)
        self.cart_tree.column("price", width=100)
        self.cart_tree.column("qty", width=70)
        self.cart_tree.column("discount", width=70)
        self.cart_tree.column("total", width=120)
        
        self.cart_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind double-click to edit item
        self.cart_tree.bind("<Double-1>", self.edit_cart_item)
        # Bind right-click for context menu
        self.cart_tree.bind("<Button-3>", self.show_cart_context_menu)
        
        # Totals and payment frame
        totals_frame = tk.Frame(parent, bg=COLORS["bg_white"], padx=10, pady=10)
        totals_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Subtotal
        tk.Label(totals_frame, 
               text="Subtotal:",
               font=FONTS["regular_bold"],
               bg=COLORS["bg_white"],
               fg=COLORS["text_primary"]).grid(row=0, column=0, sticky="w", pady=5)
               
        self.subtotal_label = tk.Label(totals_frame, 
                                     text="₹0.00",
                                     font=FONTS["regular"],
                                     bg=COLORS["bg_white"],
                                     fg=COLORS["text_primary"])
        self.subtotal_label.grid(row=0, column=1, sticky="e", pady=5)
        
        # Discount
        tk.Label(totals_frame, 
               text="Discount:",
               font=FONTS["regular_bold"],
               bg=COLORS["bg_white"],
               fg=COLORS["text_primary"]).grid(row=1, column=0, sticky="w", pady=5)
        
        discount_frame = tk.Frame(totals_frame, bg=COLORS["bg_white"])
        discount_frame.grid(row=1, column=1, sticky="e", pady=5)
        
        self.discount_var = tk.StringVar(value="0.00")
        discount_entry = tk.Entry(discount_frame, 
                                textvariable=self.discount_var,
                                font=FONTS["regular"],
                                width=8)
        discount_entry.pack(side=tk.LEFT)
        
        self.discount_type_var = tk.StringVar(value="amount")
        discount_type = ttk.Combobox(discount_frame, 
                                   textvariable=self.discount_type_var,
                                   values=["amount", "%"],
                                   width=5,
                                   state="readonly")
        discount_type.pack(side=tk.LEFT, padx=(5, 0))
        
        # Label to show calculated discount amount
        self.discount_amount_label = tk.Label(totals_frame, 
                                           text="- ₹0.00",
                                           font=FONTS["regular"],
                                           bg=COLORS["bg_white"],
                                           fg=COLORS["danger"])
        # Not displaying this label directly in the grid, but keeping it for update_totals()
        
        # Bind discount changes
        self.discount_var.trace_add("write", lambda *args: self.update_totals())
        self.discount_type_var.trace_add("write", lambda *args: self.update_totals())
        
        # CGST (2.5%)
        tk.Label(totals_frame, 
               text="CGST (2.5%):",
               font=FONTS["regular"],
               bg=COLORS["bg_white"],
               fg=COLORS["text_primary"]).grid(row=2, column=0, sticky="w", pady=3)
               
        self.cgst_label = tk.Label(totals_frame, 
                                text="₹0.00",
                                font=FONTS["regular"],
                                bg=COLORS["bg_white"],
                                fg=COLORS["text_primary"])
        self.cgst_label.grid(row=2, column=1, sticky="e", pady=3)
        
        # SGST (2.5%)
        tk.Label(totals_frame, 
               text="SGST (2.5%):",
               font=FONTS["regular"],
               bg=COLORS["bg_white"],
               fg=COLORS["text_primary"]).grid(row=3, column=0, sticky="w", pady=3)
               
        self.sgst_label = tk.Label(totals_frame, 
                                text="₹0.00",
                                font=FONTS["regular"],
                                bg=COLORS["bg_white"],
                                fg=COLORS["text_primary"])
        self.sgst_label.grid(row=3, column=1, sticky="e", pady=3)
        
        # Total Tax (for compatibility)
        self.tax_label = tk.Label(totals_frame, 
                                text="₹0.00",
                                font=FONTS["regular"],
                                bg=COLORS["bg_white"],
                                fg=COLORS["text_primary"])
        # Not showing this label but keeping it for code compatibility
        
        # Total
        tk.Label(totals_frame, 
               text="TOTAL:",
               font=FONTS["heading"],
               bg=COLORS["bg_white"],
               fg=COLORS["text_primary"]).grid(row=4, column=0, sticky="w", pady=10)
               
        self.total_label = tk.Label(totals_frame, 
                                  text="₹0.00",
                                  font=FONTS["heading"],
                                  bg=COLORS["bg_white"],
                                  fg=COLORS["primary"])
        self.total_label.grid(row=4, column=1, sticky="e", pady=10)
        
        # Make totals_frame columns expandable
        totals_frame.columnconfigure(0, weight=1)
        totals_frame.columnconfigure(1, weight=1)
        
        # Payment buttons frame
        payment_frame = tk.Frame(parent, bg=COLORS["bg_primary"], pady=10)
        payment_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Cancel button
        cancel_btn = tk.Button(payment_frame,
                             text="CANCEL",
                             font=FONTS["regular_bold"],
                             bg=COLORS["danger"],
                             fg=COLORS["text_white"],
                             padx=15,
                             pady=10,
                             cursor="hand2",
                             command=self.cancel_sale)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Suspend button - for saving a sale for later
        suspend_btn = tk.Button(payment_frame,
                              text="SUSPEND",
                              font=FONTS["regular_bold"],
                              bg=COLORS["warning"],
                              fg=COLORS["text_primary"],
                              padx=15,
                              pady=10,
                              cursor="hand2",
                              command=self.suspend_sale)
        suspend_btn.pack(side=tk.LEFT, padx=5)
        
        # Suspended bills button
        suspended_btn = tk.Button(payment_frame,
                                text="SUSPENDED",
                                font=FONTS["regular_bold"],
                                bg=COLORS["bg_secondary"],
                                fg=COLORS["text_primary"],
                                padx=15,
                                pady=10,
                                cursor="hand2",
                                command=self.show_suspended_bills)
        suspended_btn.pack(side=tk.LEFT, padx=5)
        
        # Right-aligned payment buttons
        payment_btns_frame = tk.Frame(payment_frame, bg=COLORS["bg_primary"])
        payment_btns_frame.pack(side=tk.RIGHT)
        
        # Cash payment button
        cash_btn = tk.Button(payment_btns_frame,
                           text="CASH",
                           font=FONTS["regular_bold"],
                           bg=COLORS["success"],
                           fg=COLORS["text_white"],
                           padx=15,
                           pady=10,
                           cursor="hand2",
                           command=lambda: self.process_payment("CASH"))
        cash_btn.pack(side=tk.LEFT, padx=5)
        
        # UPI payment button
        upi_btn = tk.Button(payment_btns_frame,
                          text="UPI",
                          font=FONTS["regular_bold"],
                          bg=COLORS["secondary"],
                          fg=COLORS["text_white"],
                          padx=15,
                          pady=10,
                          cursor="hand2",
                          command=lambda: self.process_payment("UPI"))
        upi_btn.pack(side=tk.LEFT, padx=5)
        
        # Credit payment button
        credit_btn = tk.Button(payment_btns_frame,
                             text="CREDIT",
                             font=FONTS["regular_bold"],
                             bg=COLORS["primary"],
                             fg=COLORS["text_white"],
                             padx=15,
                             pady=10,
                             cursor="hand2",
                             command=lambda: self.process_payment("CREDIT"))
        credit_btn.pack(side=tk.LEFT, padx=5)
        
        # Split payment button
        split_btn = tk.Button(payment_btns_frame,
                            text="SPLIT",
                            font=FONTS["regular_bold"],
                            bg=COLORS["info"],
                            fg=COLORS["text_white"],
                            padx=15,
                            pady=10,
                            cursor="hand2",
                            command=lambda: self.process_payment("SPLIT"))
        split_btn.pack(side=tk.LEFT, padx=5)
    
    def setup_product_panel(self, parent):
        """Setup the product search panel"""
        # Product search section
        search_frame = tk.Frame(parent, bg=COLORS["bg_secondary"], padx=10, pady=5)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Search label and entry in the same row for compact layout
        search_label = tk.Label(search_frame, 
                              text="Search Products:",
                              font=FONTS["regular_bold"],
                              bg=COLORS["bg_secondary"],
                              fg=COLORS["text_primary"])
        search_label.pack(side=tk.LEFT, pady=5)
        
        # Search input with autocommit
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, 
                              textvariable=self.search_var,
                              font=FONTS["regular"],
                              width=25)
        search_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0), pady=5)
        
        # Bind search input changes to search_products method
        self.search_var.trace_add("write", lambda *args: self.search_products())
        
        # Product list section - give it more vertical space
        list_frame = tk.Frame(parent, bg=COLORS["bg_secondary"])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Product list label
        products_label = tk.Label(list_frame, 
                                text="Products List",
                                font=FONTS["subheading"],
                                bg=COLORS["bg_secondary"],
                                fg=COLORS["text_primary"])
        products_label.pack(anchor="w", padx=5, pady=(5, 5))
        
        # Products treeview frame - make it taller
        products_frame = tk.Frame(list_frame, bg=COLORS["bg_secondary"])
        products_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add both vertical and horizontal scrollbars
        scrollbar_y = ttk.Scrollbar(products_frame)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scrollbar_x = ttk.Scrollbar(products_frame, orient='horizontal')
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Products treeview with both scrollbars
        self.products_tree = ttk.Treeview(products_frame, 
                                        columns=("id", "name", "price", "stock"),
                                        show="headings",
                                        yscrollcommand=scrollbar_y.set,
                                        xscrollcommand=scrollbar_x.set,
                                        height=15)  # Increase visible rows
        
        # Configure scrollbars
        scrollbar_y.config(command=self.products_tree.yview)
        scrollbar_x.config(command=self.products_tree.xview)
        
        # Define columns
        self.products_tree.heading("id", text="ID")
        self.products_tree.heading("name", text="Product Name")
        self.products_tree.heading("price", text="Price")
        self.products_tree.heading("stock", text="Stock")
        
        # Set column widths - make product name wider
        self.products_tree.column("id", width=50, minwidth=50)
        self.products_tree.column("name", width=250, minwidth=150)
        self.products_tree.column("price", width=80, minwidth=80)
        self.products_tree.column("stock", width=60, minwidth=60)
        
        self.products_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind double-click to add to cart
        self.products_tree.bind("<Double-1>", self.add_to_cart)
        # Bind Enter key directly to the treeview
        self.products_tree.bind("<Return>", self.add_to_cart)
        
        # Load products initially
        self.load_products()
        
        # Action buttons frame - more compact layout
        action_frame = tk.Frame(parent, bg=COLORS["bg_secondary"], padx=10, pady=5)
        action_frame.pack(fill=tk.X, pady=5)
        
        # Button frame with two buttons side by side
        button_frame = tk.Frame(action_frame, bg=COLORS["bg_secondary"])
        button_frame.pack(fill=tk.X)
        
        # Add to cart button
        add_to_cart_btn = tk.Button(button_frame,
                                  text="Add to Cart",
                                  font=FONTS["regular_bold"],
                                  bg=COLORS["primary"],
                                  fg=COLORS["text_white"],
                                  padx=10,
                                  pady=5,
                                  cursor="hand2",
                                  command=lambda: self.add_to_cart(None))
        add_to_cart_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Quick add button
        quick_add_btn = tk.Button(button_frame,
                                text="Quick Add",
                                font=FONTS["regular"],
                                bg=COLORS["secondary"],
                                fg=COLORS["text_white"],
                                padx=10,
                                pady=5,
                                cursor="hand2",
                                command=self.quick_add_item)
        quick_add_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
    
    def load_products(self):
        """Load products from database into treeview"""
        # Clear existing items
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
            
        # Get products from database
        db = self.controller.db
        products = db.fetchall("""
            SELECT p.id, p.name, p.selling_price, COALESCE(SUM(b.quantity), 0) as stock
            FROM products p
            LEFT JOIN batches b ON p.id = b.product_id AND b.expiry_date > date('now')
            GROUP BY p.id, p.name, p.selling_price
            ORDER BY p.name
        """)
        
        # Insert products into treeview
        for product in products:
            product_id, name, price, stock = product
            # Format price with Rupee symbol
            formatted_price = format_currency(price)
            # Insert into treeview
            self.products_tree.insert("", "end", values=(product_id, name, formatted_price, stock))
    
    def search_products(self):
        """Search products based on search term"""
        search_term = self.search_var.get().strip()
        
        # Clear existing items
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
            
        # If search term is empty, load all products
        if not search_term:
            self.load_products()
            return
            
        # Get products from database that match search term
        db = self.controller.db
        products = db.fetchall("""
            SELECT p.id, p.name, p.selling_price, COALESCE(SUM(b.quantity), 0) as stock
            FROM products p
            LEFT JOIN batches b ON p.id = b.product_id AND b.expiry_date > date('now')
            WHERE p.name LIKE ? OR p.code LIKE ? OR p.description LIKE ?
            GROUP BY p.id, p.name, p.selling_price
            ORDER BY p.name
        """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
        
        # Insert matching products into treeview
        for product in products:
            product_id, name, price, stock = product
            # Format price with Rupee symbol
            formatted_price = format_currency(price)
            # Insert into treeview
            self.products_tree.insert("", "end", values=(product_id, name, formatted_price, stock))
    
    def add_to_cart(self, event=None):
        """Add selected product to cart"""
        # Get selected product
        if event:  # Triggered by double-click
            selected_item = self.products_tree.selection()
            if not selected_item:
                return
            item = selected_item[0]
        else:  # Triggered by button
            selected_items = self.products_tree.selection()
            if not selected_items:
                messagebox.showinfo("Select Product", "Please select a product first!")
                return
            item = selected_items[0]
            
        # Get product details
        product_values = self.products_tree.item(item, "values")
        product_id = product_values[0]
        product_name = product_values[1]
        product_price = parse_currency(product_values[2])
        available_stock = int(product_values[3])
        
        # Check stock
        if available_stock <= 0:
            messagebox.showwarning("Out of Stock", 
                                   f"{product_name} is out of stock!")
            return
            
        # Ask for quantity and discount
        dialog = tk.Toplevel(self)
        dialog.title("Add to Cart")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Set dialog position
        self._set_dialog_transient(dialog)
        
        # Create frame for content
        content_frame = tk.Frame(dialog, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Product info
        tk.Label(content_frame, 
               text=product_name,
               font=FONTS["subheading"]).pack(pady=(0, 10))
        
        tk.Label(content_frame, 
               text=f"Price: {product_values[2]} | Available: {available_stock}",
               font=FONTS["regular"]).pack(pady=(0, 20))
        
        # Quantity
        qty_frame = tk.Frame(content_frame)
        qty_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(qty_frame, 
               text="Quantity:",
               font=FONTS["regular_bold"],
               width=12,
               anchor="w").grid(row=0, column=0, sticky="w")
        
        qty_var = tk.StringVar(value="1")
        qty_entry = tk.Entry(qty_frame, 
                           textvariable=qty_var,
                           font=FONTS["regular"],
                           width=10)
        qty_entry.grid(row=0, column=1, sticky="w")
        qty_entry.select_range(0, tk.END)  # Select all text
        
        # Item discount
        discount_frame = tk.Frame(content_frame)
        discount_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(discount_frame, 
               text="Discount (%):",
               font=FONTS["regular_bold"],
               width=12,
               anchor="w").grid(row=0, column=0, sticky="w")
        
        discount_var = tk.StringVar(value="0")
        discount_entry = tk.Entry(discount_frame, 
                                textvariable=discount_var,
                                font=FONTS["regular"],
                                width=10)
        discount_entry.grid(row=0, column=1, sticky="w")
        
        # Buttons
        button_frame = tk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        cancel_btn = tk.Button(button_frame,
                             text="Cancel",
                             font=FONTS["regular"],
                             padx=20,
                             pady=5,
                             command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        def add_item():
            try:
                quantity = int(qty_var.get())
                discount = float(discount_var.get())
                
                # Validate quantity
                if quantity <= 0:
                    messagebox.showwarning("Invalid Quantity", 
                                         "Quantity must be greater than zero!")
                    return
                
                if quantity > available_stock:
                    messagebox.showwarning("Insufficient Stock", 
                                         f"Only {available_stock} units available!")
                    return
                
                # Validate discount
                if discount < 0 or discount > 100:
                    messagebox.showwarning("Invalid Discount", 
                                         "Discount must be between 0 and 100!")
                    return
                
                # Calculate total - use Decimal for consistent math with money values
                discount_factor = Decimal('1') - (Decimal(str(discount)) / Decimal('100'))
                total = Decimal(str(product_price)) * Decimal(str(quantity)) * discount_factor
                
                # Add to cart
                self.cart_items.append({
                    "id": self.next_item_id,
                    "product_id": product_id,
                    "name": product_name,
                    "price": product_price,
                    "quantity": quantity,
                    "discount": discount,
                    "total": total
                })
                
                # Increment next item ID
                self.next_item_id += 1
                
                # Update cart display
                self.update_cart()
                
                # Close dialog
                dialog.destroy()
                
            except ValueError:
                messagebox.showwarning("Invalid Input", 
                                     "Please enter valid numbers for quantity and discount!")
        
        add_btn = tk.Button(button_frame,
                          text="Add to Cart",
                          font=FONTS["regular_bold"],
                          bg=COLORS["primary"],
                          fg=COLORS["text_white"],
                          padx=20,
                          pady=5,
                          command=add_item)
        add_btn.pack(side=tk.RIGHT, padx=5)
        
        # Set focus to quantity entry
        qty_entry.focus_set()
        
        # Bind Enter key to add_item function
        dialog.bind("<Return>", lambda event: add_item())
        
        # Wait for dialog to close
        dialog.wait_window()
    
    def quick_add_item(self):
        """Add an item without barcode/product lookup"""
        # Create dialog
        dialog = tk.Toplevel(self)
        dialog.title("Quick Add Item")
        dialog.geometry("500x350")
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Set dialog position
        self._set_dialog_transient(dialog)
        
        # Create frame for content
        content_frame = tk.Frame(dialog, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        tk.Label(content_frame, 
               text="Add Custom Item",
               font=FONTS["subheading"]).pack(pady=(0, 20))
        
        # Product name
        name_frame = tk.Frame(content_frame)
        name_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(name_frame, 
               text="Name:",
               font=FONTS["regular_bold"],
               width=12,
               anchor="w").grid(row=0, column=0, sticky="w")
        
        name_var = tk.StringVar()
        name_entry = tk.Entry(name_frame, 
                            textvariable=name_var,
                            font=FONTS["regular"],
                            width=30)
        name_entry.grid(row=0, column=1, sticky="w")
        
        # Price
        price_frame = tk.Frame(content_frame)
        price_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(price_frame, 
               text="Price:",
               font=FONTS["regular_bold"],
               width=12,
               anchor="w").grid(row=0, column=0, sticky="w")
        
        price_var = tk.StringVar()
        price_entry = tk.Entry(price_frame, 
                             textvariable=price_var,
                             font=FONTS["regular"],
                             width=15)
        price_entry.grid(row=0, column=1, sticky="w")
        
        # Quantity
        qty_frame = tk.Frame(content_frame)
        qty_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(qty_frame, 
               text="Quantity:",
               font=FONTS["regular_bold"],
               width=12,
               anchor="w").grid(row=0, column=0, sticky="w")
        
        qty_var = tk.StringVar(value="1")
        qty_entry = tk.Entry(qty_frame, 
                           textvariable=qty_var,
                           font=FONTS["regular"],
                           width=10)
        qty_entry.grid(row=0, column=1, sticky="w")
        
        # Tax rate (GST)
        tax_frame = tk.Frame(content_frame)
        tax_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(tax_frame, 
               text="GST Rate:",
               font=FONTS["regular_bold"],
               width=12,
               anchor="w").grid(row=0, column=0, sticky="w")
        
        tax_var = tk.StringVar(value="5")
        tax_combo = ttk.Combobox(tax_frame, 
                               textvariable=tax_var,
                               values=["0", "5", "12", "18", "28"],
                               font=FONTS["regular"],
                               width=10,
                               state="readonly")
        tax_combo.grid(row=0, column=1, sticky="w")
        
        # Item discount
        discount_frame = tk.Frame(content_frame)
        discount_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(discount_frame, 
               text="Discount (%):",
               font=FONTS["regular_bold"],
               width=12,
               anchor="w").grid(row=0, column=0, sticky="w")
        
        discount_var = tk.StringVar(value="0")
        discount_entry = tk.Entry(discount_frame, 
                                textvariable=discount_var,
                                font=FONTS["regular"],
                                width=10)
        discount_entry.grid(row=0, column=1, sticky="w")
        
        # Add HSN/SAC code field
        hsn_frame = tk.Frame(content_frame)
        hsn_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(hsn_frame, 
               text="HSN/SAC Code:",
               font=FONTS["regular_bold"],
               width=12,
               anchor="w").grid(row=0, column=0, sticky="w")
        
        hsn_var = tk.StringVar()
        hsn_entry = tk.Entry(hsn_frame, 
                           textvariable=hsn_var,
                           font=FONTS["regular"],
                           width=15)
        hsn_entry.grid(row=0, column=1, sticky="w")
        
        # Buttons
        button_frame = tk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        cancel_btn = tk.Button(button_frame,
                             text="Cancel",
                             font=FONTS["regular"],
                             padx=20,
                             pady=5,
                             command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        def add_item():
            try:
                # Get values
                name = name_var.get().strip()
                price = float(price_var.get())
                quantity = int(qty_var.get())
                discount = float(discount_var.get())
                hsn_code = hsn_var.get().strip()
                
                # Validate
                if not name:
                    messagebox.showwarning("Missing Name", 
                                         "Please enter a product name!")
                    return
                
                if price <= 0:
                    messagebox.showwarning("Invalid Price", 
                                         "Price must be greater than zero!")
                    return
                
                if quantity <= 0:
                    messagebox.showwarning("Invalid Quantity", 
                                         "Quantity must be greater than zero!")
                    return
                
                if discount < 0 or discount > 100:
                    messagebox.showwarning("Invalid Discount", 
                                         "Discount must be between 0 and 100!")
                    return
                
                # Calculate total - use Decimal for consistent math with money values
                discount_factor = Decimal('1') - (Decimal(str(discount)) / Decimal('100'))
                total = Decimal(str(price)) * Decimal(str(quantity)) * discount_factor
                
                # Add to cart
                self.cart_items.append({
                    "id": self.next_item_id,
                    "product_id": None,  # None for custom items
                    "name": name,
                    "price": price,
                    "quantity": quantity,
                    "discount": discount,
                    "total": total,
                    "hsn_code": hsn_code,
                    "tax_rate": float(tax_var.get())
                })
                
                # Increment next item ID
                self.next_item_id += 1
                
                # Update cart display
                self.update_cart()
                
                # Close dialog
                dialog.destroy()
                
            except ValueError:
                messagebox.showwarning("Invalid Input", 
                                     "Please enter valid numbers for price, quantity, and discount!")
        
        add_btn = tk.Button(button_frame,
                          text="Add to Cart",
                          font=FONTS["regular_bold"],
                          bg=COLORS["primary"],
                          fg=COLORS["text_white"],
                          padx=20,
                          pady=5,
                          command=add_item)
        add_btn.pack(side=tk.RIGHT, padx=5)
        
        # Set focus to name entry
        name_entry.focus_set()
        
        # Bind Enter key to move between fields
        name_entry.bind("<Return>", lambda event: price_entry.focus_set())
        price_entry.bind("<Return>", lambda event: qty_entry.focus_set())
        qty_entry.bind("<Return>", lambda event: tax_combo.focus_set())
        tax_combo.bind("<Return>", lambda event: discount_entry.focus_set())
        discount_entry.bind("<Return>", lambda event: hsn_entry.focus_set())
        hsn_entry.bind("<Return>", lambda event: add_item())
        
        # Wait for dialog to close
        dialog.wait_window()
    
    def update_cart(self):
        """Update cart display and totals"""
        # Clear existing items in cart treeview
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
            
        # Add cart items to treeview
        for item in self.cart_items:
            # Format price and total with Rupee symbol
            formatted_price = format_currency(item["price"])
            formatted_total = format_currency(item["total"])
            
            # Insert into treeview
            self.cart_tree.insert("", "end", values=(
                item["id"],
                item["name"],
                formatted_price,
                item["quantity"],
                item["discount"],
                formatted_total
            ))
            
        # Update totals
        self.update_totals()
    
    def update_totals(self):
        """Calculate and update cart totals"""
        # Calculate subtotal
        subtotal = sum(item["total"] for item in self.cart_items)
        
        # Apply any additional discount - using Decimal for consistent math
        try:
            discount_value = Decimal(str(self.discount_var.get() or '0'))
            discount_type = self.discount_type_var.get()
            
            if discount_type == "amount":
                # Fixed amount discount
                discount_amount = discount_value
            else:
                # Percentage discount
                discount_amount = subtotal * discount_value / Decimal('100')
                
            # Ensure discount doesn't exceed subtotal
            if discount_amount > subtotal:
                discount_amount = subtotal
            
            # Calculate final subtotal after discount
            final_subtotal = subtotal - discount_amount
            
        except (ValueError, InvalidOperation):
            # Invalid discount value, treat as zero
            discount_amount = Decimal('0')
            final_subtotal = subtotal
        
        # Calculate tax (default 5% GST)
        # Split into CGST (2.5%) and SGST (2.5%) for proper tax display
        tax_rate = Decimal('0.05')  # 5% GST
        tax_amount = final_subtotal * tax_rate
        
        # Store CGST and SGST separately for invoice generation
        self.cgst_amount = tax_amount / Decimal('2')
        self.sgst_amount = tax_amount / Decimal('2')
        
        # Calculate total
        total = final_subtotal + tax_amount
        
        # Update labels with improved tax breakdown
        self.subtotal_label.config(text=format_currency(subtotal))
        self.discount_amount_label.config(text=f"- {format_currency(discount_amount)}")
        
        # Update separate CGST and SGST labels
        self.cgst_label.config(text=format_currency(self.cgst_amount))
        self.sgst_label.config(text=format_currency(self.sgst_amount))
        
        # Keep the original tax_label updated for compatibility
        self.tax_label.config(text=format_currency(tax_amount))
        
        self.total_label.config(text=format_currency(total))
    
    def edit_cart_item(self, event=None):
        """Edit selected cart item"""
        # Get selected item
        selected_items = self.cart_tree.selection()
        if not selected_items:
            return
        selected_item = selected_items[0]
        
        # Get cart item id
        cart_item_id = int(self.cart_tree.item(selected_item, "values")[0])
        
        # Find the corresponding cart item
        cart_item = next((item for item in self.cart_items if item["id"] == cart_item_id), None)
        if not cart_item:
            return
            
        # Create dialog
        dialog = tk.Toplevel(self)
        dialog.title("Edit Cart Item")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Set dialog position
        self._set_dialog_transient(dialog)
        
        # Create frame for content
        content_frame = tk.Frame(dialog, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Product info
        tk.Label(content_frame, 
               text=cart_item["name"],
               font=FONTS["subheading"]).pack(pady=(0, 10))
        
        tk.Label(content_frame, 
               text=f"Price: {format_currency(cart_item['price'])}",
               font=FONTS["regular"]).pack(pady=(0, 20))
        
        # Quantity
        qty_frame = tk.Frame(content_frame)
        qty_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(qty_frame, 
               text="Quantity:",
               font=FONTS["regular_bold"],
               width=12,
               anchor="w").grid(row=0, column=0, sticky="w")
        
        qty_var = tk.StringVar(value=str(cart_item["quantity"]))
        qty_entry = tk.Entry(qty_frame, 
                           textvariable=qty_var,
                           font=FONTS["regular"],
                           width=10)
        qty_entry.grid(row=0, column=1, sticky="w")
        qty_entry.select_range(0, tk.END)  # Select all text
        
        # Item discount
        discount_frame = tk.Frame(content_frame)
        discount_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(discount_frame, 
               text="Discount (%):",
               font=FONTS["regular_bold"],
               width=12,
               anchor="w").grid(row=0, column=0, sticky="w")
        
        discount_var = tk.StringVar(value=str(cart_item["discount"]))
        discount_entry = tk.Entry(discount_frame, 
                                textvariable=discount_var,
                                font=FONTS["regular"],
                                width=10)
        discount_entry.grid(row=0, column=1, sticky="w")
        
        # Buttons
        button_frame = tk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        cancel_btn = tk.Button(button_frame,
                             text="Cancel",
                             font=FONTS["regular"],
                             padx=20,
                             pady=5,
                             command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        def remove_item():
            # Ask for confirmation
            if messagebox.askyesno("Remove Item", 
                                 f"Are you sure you want to remove {cart_item['name']} from the cart?"):
                # Remove from cart
                self.cart_items = [item for item in self.cart_items if item["id"] != cart_item_id]
                
                # Update cart display
                self.update_cart()
                
                # Close dialog
                dialog.destroy()
        
        remove_btn = tk.Button(button_frame,
                             text="Remove Item",
                             font=FONTS["regular"],
                             bg=COLORS["danger"],
                             fg=COLORS["text_white"],
                             padx=10,
                             pady=5,
                             command=remove_item)
        remove_btn.pack(side=tk.LEFT, padx=5)
        
        def update_item():
            try:
                quantity = int(qty_var.get())
                discount = float(discount_var.get())
                
                # Validate quantity
                if quantity <= 0:
                    messagebox.showwarning("Invalid Quantity", 
                                         "Quantity must be greater than zero!")
                    return
                
                # Check stock if this is a database product
                if cart_item["product_id"]:
                    db = self.controller.db
                    available_stock = db.fetchone("""
                        SELECT COALESCE(SUM(b.quantity), 0) as stock
                        FROM products p
                        LEFT JOIN batches b ON p.id = b.product_id AND b.expiry_date > date('now')
                        WHERE p.id = ?
                        GROUP BY p.id
                    """, (cart_item["product_id"],))
                    
                    if available_stock and quantity > available_stock[0]:
                        messagebox.showwarning("Insufficient Stock", 
                                             f"Only {available_stock[0]} units available!")
                        return
                
                # Validate discount
                if discount < 0 or discount > 100:
                    messagebox.showwarning("Invalid Discount", 
                                         "Discount must be between 0 and 100!")
                    return
                
                # Calculate total - use Decimal for consistent math with money values
                discount_factor = Decimal('1') - (Decimal(str(discount)) / Decimal('100'))
                total = Decimal(str(cart_item["price"])) * Decimal(str(quantity)) * discount_factor
                
                # Update cart item
                for item in self.cart_items:
                    if item["id"] == cart_item_id:
                        item["quantity"] = quantity
                        item["discount"] = discount
                        item["total"] = total
                        break
                
                # Update cart display
                self.update_cart()
                
                # Close dialog
                dialog.destroy()
                
            except ValueError:
                messagebox.showwarning("Invalid Input", 
                                     "Please enter valid numbers for quantity and discount!")
        
        update_btn = tk.Button(button_frame,
                             text="Update",
                             font=FONTS["regular_bold"],
                             bg=COLORS["primary"],
                             fg=COLORS["text_white"],
                             padx=20,
                             pady=5,
                             command=update_item)
        update_btn.pack(side=tk.RIGHT, padx=5)
        
        # Set focus to quantity entry
        qty_entry.focus_set()
        
        # Bind Enter key to update_item function
        dialog.bind("<Return>", lambda event: update_item())
        
        # Wait for dialog to close
        dialog.wait_window()
    
    def show_cart_context_menu(self, event):
        """Show context menu for cart treeview"""
        # Get clicked item
        item = self.cart_tree.identify_row(event.y)
        if not item:
            return
            
        # Select the item
        self.cart_tree.selection_set(item)
        
        # Create context menu
        context_menu = tk.Menu(self, tearoff=0)
        context_menu.add_command(label="Edit Item", 
                               command=self.edit_cart_item)
        context_menu.add_command(label="Remove Item", 
                               command=self.remove_selected_item)
        
        # Show context menu
        context_menu.post(event.x_root, event.y_root)
    
    def remove_selected_item(self):
        """Remove selected item from cart"""
        # Get selected item
        selected_items = self.cart_tree.selection()
        if not selected_items:
            return
        selected_item = selected_items[0]
        
        # Get cart item id
        cart_item_id = int(self.cart_tree.item(selected_item, "values")[0])
        
        # Find the corresponding cart item
        cart_item = next((item for item in self.cart_items if item["id"] == cart_item_id), None)
        if not cart_item:
            return
            
        # Ask for confirmation
        if messagebox.askyesno("Remove Item", 
                             f"Are you sure you want to remove {cart_item['name']} from the cart?"):
            # Remove from cart
            self.cart_items = [item for item in self.cart_items if item["id"] != cart_item_id]
            
            # Update cart display
            self.update_cart()
    
    def change_customer(self, add_new=False):
        """Change the customer for this sale"""
        # Get current customer
        current_customer_id = self.current_customer["id"]
        
        # If adding new customer
        if add_new:
            # Create dialog
            dialog = tk.Toplevel(self)
            dialog.title("Add New Customer")
            dialog.geometry("500x400")
            dialog.resizable(False, False)
            dialog.transient(self.winfo_toplevel())
            dialog.grab_set()
            
            # Set dialog position
            self._set_dialog_transient(dialog)
            
            # Create frame for content
            content_frame = tk.Frame(dialog, padx=20, pady=20)
            content_frame.pack(fill=tk.BOTH, expand=True)
            
            # Header
            tk.Label(content_frame, 
                   text="Add New Customer",
                   font=FONTS["subheading"]).pack(pady=(0, 20))
            
            # Customer details
            # Name
            name_frame = tk.Frame(content_frame)
            name_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(name_frame, 
                   text="Name:",
                   font=FONTS["regular_bold"],
                   width=15,
                   anchor="w").grid(row=0, column=0, sticky="w")
            
            name_var = tk.StringVar()
            name_entry = tk.Entry(name_frame, 
                                textvariable=name_var,
                                font=FONTS["regular"],
                                width=30)
            name_entry.grid(row=0, column=1, sticky="w")
            
            # Phone
            phone_frame = tk.Frame(content_frame)
            phone_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(phone_frame, 
                   text="Phone:",
                   font=FONTS["regular_bold"],
                   width=15,
                   anchor="w").grid(row=0, column=0, sticky="w")
            
            phone_var = tk.StringVar()
            phone_entry = tk.Entry(phone_frame, 
                                 textvariable=phone_var,
                                 font=FONTS["regular"],
                                 width=20)
            phone_entry.grid(row=0, column=1, sticky="w")
            
            # Email
            email_frame = tk.Frame(content_frame)
            email_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(email_frame, 
                   text="Email:",
                   font=FONTS["regular_bold"],
                   width=15,
                   anchor="w").grid(row=0, column=0, sticky="w")
            
            email_var = tk.StringVar()
            email_entry = tk.Entry(email_frame, 
                                 textvariable=email_var,
                                 font=FONTS["regular"],
                                 width=30)
            email_entry.grid(row=0, column=1, sticky="w")
            
            # Address
            address_frame = tk.Frame(content_frame)
            address_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(address_frame, 
                   text="Address:",
                   font=FONTS["regular_bold"],
                   width=15,
                   anchor="w").grid(row=0, column=0, sticky="w")
            
            address_var = tk.StringVar()
            address_entry = tk.Entry(address_frame, 
                                   textvariable=address_var,
                                   font=FONTS["regular"],
                                   width=30)
            address_entry.grid(row=0, column=1, sticky="w")
            
            # Village
            village_frame = tk.Frame(content_frame)
            village_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(village_frame, 
                   text="Village:",
                   font=FONTS["regular_bold"],
                   width=15,
                   anchor="w").grid(row=0, column=0, sticky="w")
            
            village_var = tk.StringVar()
            village_entry = tk.Entry(village_frame, 
                                   textvariable=village_var,
                                   font=FONTS["regular"],
                                   width=20)
            village_entry.grid(row=0, column=1, sticky="w")
            
            # Tax information
            tax_frame = tk.Frame(content_frame)
            tax_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(tax_frame, 
                   text="GSTIN:",
                   font=FONTS["regular_bold"],
                   width=15,
                   anchor="w").grid(row=0, column=0, sticky="w")
            
            gstin_var = tk.StringVar()
            gstin_entry = tk.Entry(tax_frame, 
                                 textvariable=gstin_var,
                                 font=FONTS["regular"],
                                 width=20)
            gstin_entry.grid(row=0, column=1, sticky="w")
            
            # Buttons
            button_frame = tk.Frame(content_frame)
            button_frame.pack(fill=tk.X, pady=(20, 0))
            
            cancel_btn = tk.Button(button_frame,
                                 text="Cancel",
                                 font=FONTS["regular"],
                                 padx=20,
                                 pady=5,
                                 command=dialog.destroy)
            cancel_btn.pack(side=tk.LEFT, padx=5)
            
            def add_customer():
                # Get values
                name = name_var.get().strip()
                phone = phone_var.get().strip()
                email = email_var.get().strip()
                address = address_var.get().strip()
                village = village_var.get().strip()
                gstin = gstin_var.get().strip()
                
                # Validate
                if not name:
                    messagebox.showwarning("Missing Name", 
                                         "Please enter customer name!")
                    return
                
                # Create customer
                db = self.controller.db
                try:
                    db.begin()
                    
                    # Insert customer
                    customer_id = db.insert("customers", {
                        "name": name,
                        "phone": phone,
                        "email": email,
                        "address": address,
                        "village": village,
                        "gstin": gstin,
                        "created_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    
                    db.commit()
                    
                    # Update current customer
                    self.current_customer = {
                        "id": customer_id,
                        "name": name,
                        "phone": phone,
                        "address": address,
                        "village": village,
                        "gstin": gstin
                    }
                    
                    # Update customer label
                    self.customer_label.config(text=name)
                    
                    # Close dialog
                    dialog.destroy()
                    
                except Exception as e:
                    db.rollback()
                    messagebox.showerror("Error", f"Failed to create customer: {str(e)}")
            
            save_btn = tk.Button(button_frame,
                               text="Save Customer",
                               font=FONTS["regular_bold"],
                               bg=COLORS["primary"],
                               fg=COLORS["text_white"],
                               padx=20,
                               pady=5,
                               command=add_customer)
            save_btn.pack(side=tk.RIGHT, padx=5)
            
            # Set focus to name entry
            name_entry.focus_set()
            
            # Bind Enter key to move between fields
            name_entry.bind("<Return>", lambda event: phone_entry.focus_set())
            phone_entry.bind("<Return>", lambda event: email_entry.focus_set())
            email_entry.bind("<Return>", lambda event: address_entry.focus_set())
            address_entry.bind("<Return>", lambda event: village_entry.focus_set())
            village_entry.bind("<Return>", lambda event: gstin_entry.focus_set())
            gstin_entry.bind("<Return>", lambda event: add_customer())
            
            # Wait for dialog to close
            dialog.wait_window()
            
        else:
            # Create dialog
            dialog = tk.Toplevel(self)
            dialog.title("Select Customer")
            dialog.geometry("800x500")
            dialog.resizable(True, True)
            dialog.transient(self.winfo_toplevel())
            dialog.grab_set()
            
            # Set dialog position
            self._set_dialog_transient(dialog)
            
            # Create frame for content
            content_frame = tk.Frame(dialog, padx=20, pady=20)
            content_frame.pack(fill=tk.BOTH, expand=True)
            
            # Header
            header_frame = tk.Frame(content_frame)
            header_frame.pack(fill=tk.X, pady=(0, 10))
            
            tk.Label(header_frame, 
                   text="Select Customer",
                   font=FONTS["subheading"]).pack(side=tk.LEFT)
            
            # Search frame
            search_frame = tk.Frame(content_frame)
            search_frame.pack(fill=tk.X, pady=10)
            
            tk.Label(search_frame, 
                   text="Search:",
                   font=FONTS["regular_bold"]).pack(side=tk.LEFT, padx=(0, 10))
            
            search_var = tk.StringVar()
            search_entry = tk.Entry(search_frame, 
                                  textvariable=search_var,
                                  font=FONTS["regular"],
                                  width=30)
            search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Customer treeview
            tree_frame = tk.Frame(content_frame)
            tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(tree_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Treeview
            columns = ("id", "name", "phone", "village", "address")
            customer_tree = ttk.Treeview(tree_frame, 
                                       columns=columns,
                                       show="headings",
                                       yscrollcommand=scrollbar.set)
            
            # Configure scrollbar
            scrollbar.config(command=customer_tree.yview)
            
            # Configure columns
            customer_tree.heading("id", text="ID")
            customer_tree.heading("name", text="Name")
            customer_tree.heading("phone", text="Phone")
            customer_tree.heading("village", text="Village")
            customer_tree.heading("address", text="Address")
            
            customer_tree.column("id", width=50)
            customer_tree.column("name", width=200)
            customer_tree.column("phone", width=120)
            customer_tree.column("village", width=120)
            customer_tree.column("address", width=250)
            
            customer_tree.pack(fill=tk.BOTH, expand=True)
            
            # Load customers
            def load_customers(search_term=None):
                # Clear treeview
                for item in customer_tree.get_children():
                    customer_tree.delete(item)
                
                # Get customers from database
                db = self.controller.db
                
                if search_term:
                    customers = db.fetchall("""
                        SELECT id, name, phone, village, address
                        FROM customers
                        WHERE name LIKE ? OR phone LIKE ? OR village LIKE ?
                        ORDER BY name
                    """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
                else:
                    customers = db.fetchall("""
                        SELECT id, name, phone, village, address
                        FROM customers
                        ORDER BY name
                    """)
                
                # Insert walk-in customer
                customer_tree.insert("", "end", values=(1, "Walk-in Customer", "", "", ""))
                
                # Insert customers
                for customer in customers:
                    # Skip walk-in customer if it's in the database
                    if customer[0] == 1:
                        continue
                    customer_tree.insert("", "end", values=customer)
                
                # Select current customer
                if current_customer_id == 1:
                    # Select walk-in customer
                    customer_tree.selection_set(customer_tree.get_children()[0])
                else:
                    # Find current customer
                    for item in customer_tree.get_children():
                        if customer_tree.item(item, "values")[0] == current_customer_id:
                            customer_tree.selection_set(item)
                            customer_tree.see(item)
                            break
            
            # Initial load
            load_customers()
            
            # Bind search
            def on_search(*args):
                search_term = search_var.get().strip()
                load_customers(search_term if search_term else None)
            
            search_var.trace_add("write", on_search)
            
            # Buttons
            button_frame = tk.Frame(content_frame)
            button_frame.pack(fill=tk.X, pady=10)
            
            cancel_btn = tk.Button(button_frame,
                                 text="Cancel",
                                 font=FONTS["regular"],
                                 padx=20,
                                 pady=5,
                                 command=dialog.destroy)
            cancel_btn.pack(side=tk.LEFT, padx=5)
            
            def select_customer():
                # Get selected item
                selected_items = customer_tree.selection()
                if not selected_items:
                    messagebox.showinfo("Select Customer", "Please select a customer!")
                    return
                selected_item = selected_items[0]
                
                # Get customer details
                customer_values = customer_tree.item(selected_item, "values")
                customer_id = int(customer_values[0])
                
                # If walk-in customer
                if customer_id == 1:
                    self.current_customer = {
                        "id": 1,
                        "name": "Walk-in Customer",
                        "phone": "",
                        "address": "",
                        "village": "",
                        "gstin": ""
                    }
                else:
                    # Get complete customer details from database
                    db = self.controller.db
                    customer = db.fetchone("""
                        SELECT id, name, phone, address, village, gstin
                        FROM customers
                        WHERE id = ?
                    """, (customer_id,))
                    
                    self.current_customer = {
                        "id": customer[0],
                        "name": customer[1],
                        "phone": customer[2],
                        "address": customer[3],
                        "village": customer[4],
                        "gstin": customer[5]
                    }
                
                # Update customer label
                self.customer_label.config(text=self.current_customer["name"])
                
                # Close dialog
                dialog.destroy()
            
            select_btn = tk.Button(button_frame,
                                 text="Select Customer",
                                 font=FONTS["regular_bold"],
                                 bg=COLORS["primary"],
                                 fg=COLORS["text_white"],
                                 padx=20,
                                 pady=5,
                                 command=select_customer)
            select_btn.pack(side=tk.RIGHT, padx=5)
            
            # Add button for new customer
            add_btn = tk.Button(button_frame,
                              text="Add New Customer",
                              font=FONTS["regular"],
                              bg=COLORS["secondary"],
                              fg=COLORS["text_white"],
                              padx=20,
                              pady=5,
                              command=lambda: [dialog.destroy(), self.change_customer(add_new=True)])
            add_btn.pack(side=tk.RIGHT, padx=5)
            
            # Double-click to select
            customer_tree.bind("<Double-1>", lambda event: select_customer())
            
            # Set focus to search entry
            search_entry.focus_set()
            
            # Bind Enter key in search entry
            search_entry.bind("<Return>", lambda event: customer_tree.focus_set())
            
            # Bind Enter key on treeview
            customer_tree.bind("<Return>", lambda event: select_customer())
            
            # Wait for dialog to close
            dialog.wait_window()
    
    def cancel_sale(self):
        """Cancel the current sale"""
        if not self.cart_items:
            return
            
        # Ask for confirmation
        if messagebox.askyesno("Cancel Sale", 
                             "Are you sure you want to cancel this sale? All items will be removed."):
            # Clear cart
            self.cart_items = []
            
            # Reset to walk-in customer
            self.current_customer = {
                "id": 1,
                "name": "Walk-in Customer",
                "phone": "",
                "address": ""
            }
            self.customer_label.config(text="Walk-in Customer")
            
            # Reset discount
            self.discount_var.set("0.00")
            self.discount_type_var.set("amount")
            
            # Update cart display
            self.update_cart()
            
            # Reset item ID counter
            self.next_item_id = 1
    
    def suspend_sale(self):
        """Suspend the current sale for later retrieval"""
        if not self.cart_items:
            messagebox.showinfo("Empty Cart", "No items in cart to suspend!")
            return
            
        # Create dialog for suspension notes
        dialog = tk.Toplevel(self)
        dialog.title("Suspend Sale")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Set dialog position
        self._set_dialog_transient(dialog)
        
        # Create frame for content
        content_frame = tk.Frame(dialog, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        tk.Label(content_frame, 
               text="Suspend Current Sale",
               font=FONTS["subheading"]).pack(pady=(0, 20))
        
        # Notes
        tk.Label(content_frame, 
               text="Notes (optional):",
               font=FONTS["regular_bold"],
               anchor="w").pack(anchor="w")
        
        notes_var = tk.StringVar()
        notes_entry = tk.Entry(content_frame, 
                             textvariable=notes_var,
                             font=FONTS["regular"],
                             width=40)
        notes_entry.pack(fill=tk.X, pady=5)
        
        # Buttons
        button_frame = tk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        cancel_btn = tk.Button(button_frame,
                             text="Cancel",
                             font=FONTS["regular"],
                             padx=20,
                             pady=5,
                             command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        def suspend():
            # Get suspension notes
            notes = notes_var.get().strip()
            
            # Create suspended bill
            suspended_bill = {
                "customer": self.current_customer,
                "items": self.cart_items,
                "notes": notes,
                "timestamp": datetime.datetime.now(),
                "discount": self.discount_var.get(),
                "discount_type": self.discount_type_var.get()
            }
            
            # Add to suspended bills
            self.suspended_bills.append(suspended_bill)
            
            # Reset sale
            self.cancel_sale()
            
            # Close dialog
            dialog.destroy()
            
            # Show confirmation
            messagebox.showinfo("Sale Suspended", 
                              "The sale has been suspended and can be retrieved later.")
        
        suspend_btn = tk.Button(button_frame,
                              text="Suspend Sale",
                              font=FONTS["regular_bold"],
                              bg=COLORS["warning"],
                              fg=COLORS["text_primary"],
                              padx=20,
                              pady=5,
                              command=suspend)
        suspend_btn.pack(side=tk.RIGHT, padx=5)
        
        # Set focus to notes entry
        notes_entry.focus_set()
        
        # Bind Enter key
        dialog.bind("<Return>", lambda event: suspend())
        
        # Wait for dialog to close
        dialog.wait_window()
    
    def show_suspended_bills(self):
        """Show suspended bills and allow retrieval"""
        if not self.suspended_bills:
            messagebox.showinfo("No Suspended Bills", 
                              "There are no suspended bills to retrieve.")
            return
            
        # Create dialog
        dialog = tk.Toplevel(self)
        dialog.title("Suspended Bills")
        dialog.geometry("800x500")
        dialog.resizable(True, True)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Set dialog position
        self._set_dialog_transient(dialog)
        
        # Create frame for content
        content_frame = tk.Frame(dialog, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        tk.Label(content_frame, 
               text="Suspended Bills",
               font=FONTS["subheading"]).pack(anchor="w", pady=(0, 20))
        
        # Bills treeview
        tree_frame = tk.Frame(content_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        columns = ("id", "customer", "items", "total", "timestamp", "notes")
        bills_tree = ttk.Treeview(tree_frame, 
                                columns=columns,
                                show="headings",
                                yscrollcommand=scrollbar.set)
        
        # Configure scrollbar
        scrollbar.config(command=bills_tree.yview)
        
        # Configure columns
        bills_tree.heading("id", text="#")
        bills_tree.heading("customer", text="Customer")
        bills_tree.heading("items", text="Items")
        bills_tree.heading("total", text="Total")
        bills_tree.heading("timestamp", text="Suspended At")
        bills_tree.heading("notes", text="Notes")
        
        bills_tree.column("id", width=50)
        bills_tree.column("customer", width=150)
        bills_tree.column("items", width=80)
        bills_tree.column("total", width=100)
        bills_tree.column("timestamp", width=150)
        bills_tree.column("notes", width=200)
        
        bills_tree.pack(fill=tk.BOTH, expand=True)
        
        # Load suspended bills
        for i, bill in enumerate(self.suspended_bills):
            # Calculate total
            total = sum(item["total"] for item in bill["items"])
            
            # Apply bill-level discount
            try:
                discount_value = float(bill["discount"])
                discount_type = bill["discount_type"]
                
                if discount_type == "amount":
                    # Fixed amount discount
                    discount_amount = discount_value
                else:
                    # Percentage discount
                    discount_amount = total * discount_value / 100
                    
                # Ensure discount doesn't exceed total
                discount_amount = min(discount_amount, total)
                
                # Calculate final total after discount
                final_total = total - discount_amount
                
            except (ValueError, KeyError):
                # Invalid discount value, treat as zero
                final_total = total
            
            # Format total
            formatted_total = format_currency(final_total)
            
            # Format timestamp
            formatted_timestamp = bill["timestamp"].strftime("%Y-%m-%d %H:%M")
            
            # Insert into treeview
            bills_tree.insert("", "end", values=(
                i + 1,
                bill["customer"]["name"],
                len(bill["items"]),
                formatted_total,
                formatted_timestamp,
                bill["notes"]
            ))
        
        # Buttons
        button_frame = tk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        close_btn = tk.Button(button_frame,
                            text="Close",
                            font=FONTS["regular"],
                            padx=20,
                            pady=5,
                            command=dialog.destroy)
        close_btn.pack(side=tk.LEFT, padx=5)
        
        def retrieve_bill():
            # Get selected item
            selected_items = bills_tree.selection()
            if not selected_items:
                messagebox.showinfo("Select Bill", "Please select a suspended bill to retrieve!")
                return
            selected_item = selected_items[0]
            
            # Get bill index
            bill_index = int(bills_tree.item(selected_item, "values")[0]) - 1
            
            # Get suspended bill
            suspended_bill = self.suspended_bills[bill_index]
            
            # Check if current cart has items
            if self.cart_items:
                if not messagebox.askyesno("Replace Cart", 
                                         "This will replace the current cart items. Continue?"):
                    return
            
            # Restore customer
            self.current_customer = suspended_bill["customer"]
            self.customer_label.config(text=self.current_customer["name"])
            
            # Restore items
            self.cart_items = suspended_bill["items"]
            
            # Reset item ID counter to ensure unique IDs
            if self.cart_items:
                self.next_item_id = max(item["id"] for item in self.cart_items) + 1
            else:
                self.next_item_id = 1
            
            # Restore discount
            self.discount_var.set(suspended_bill["discount"])
            self.discount_type_var.set(suspended_bill["discount_type"])
            
            # Update cart display
            self.update_cart()
            
            # Remove from suspended bills
            self.suspended_bills.pop(bill_index)
            
            # Close dialog
            dialog.destroy()
            
            # Show confirmation
            messagebox.showinfo("Bill Retrieved", 
                              "The suspended bill has been retrieved successfully.")
        
        retrieve_btn = tk.Button(button_frame,
                               text="Retrieve Bill",
                               font=FONTS["regular_bold"],
                               bg=COLORS["primary"],
                               fg=COLORS["text_white"],
                               padx=20,
                               pady=5,
                               command=retrieve_bill)
        retrieve_btn.pack(side=tk.RIGHT, padx=5)
        
        def delete_bill():
            # Get selected item
            selected_items = bills_tree.selection()
            if not selected_items:
                messagebox.showinfo("Select Bill", "Please select a suspended bill to delete!")
                return
            selected_item = selected_items[0]
            
            # Get bill index
            bill_index = int(bills_tree.item(selected_item, "values")[0]) - 1
            
            # Confirm deletion
            if messagebox.askyesno("Delete Bill", 
                                 "Are you sure you want to delete this suspended bill?"):
                # Remove from suspended bills
                self.suspended_bills.pop(bill_index)
                
                # Close dialog and re-open (refresh)
                dialog.destroy()
                self.show_suspended_bills()
        
        delete_btn = tk.Button(button_frame,
                             text="Delete Bill",
                             font=FONTS["regular"],
                             bg=COLORS["danger"],
                             fg=COLORS["text_white"],
                             padx=20,
                             pady=5,
                             command=delete_bill)
        delete_btn.pack(side=tk.RIGHT, padx=5)
        
        # Double-click to retrieve
        bills_tree.bind("<Double-1>", lambda event: retrieve_bill())
        
        # Wait for dialog to close
        dialog.wait_window()
    
    def process_payment(self, payment_type):
        """Process payment for the current sale"""
        if not self.cart_items:
            messagebox.showinfo("Empty Cart", "No items in cart to process payment!")
            return
            
        # Calculate totals
        subtotal = sum(item["total"] for item in self.cart_items)
        
        # Convert to Decimal for consistent types and precision
        subtotal = Decimal(str(subtotal))
        
        # Apply any additional discount
        try:
            discount_value = Decimal(str(self.discount_var.get()))
            discount_type = self.discount_type_var.get()
            
            if discount_type == "amount":
                # Fixed amount discount
                discount_amount = discount_value
            else:
                # Percentage discount
                discount_amount = subtotal * discount_value / Decimal('100')
                
            # Ensure discount doesn't exceed subtotal
            discount_amount = min(discount_amount, subtotal)
            
            # Calculate final subtotal after discount
            final_subtotal = subtotal - discount_amount
            
        except (ValueError, InvalidOperation):
            # Invalid discount value, treat as zero
            discount_amount = Decimal('0')
            final_subtotal = subtotal
        
        # Calculate tax (default 5% GST)
        # This is a simplified calculation; in practice, we'd calculate
        # tax based on individual product tax rates
        tax_rate = Decimal('0.05')  # 5% GST
        tax_amount = final_subtotal * tax_rate
        
        # Calculate total
        total = final_subtotal + tax_amount
        
        # Check payment type and process accordingly
        if payment_type == "CASH":
            # Process cash payment
            self._process_cash_payment(total)
        elif payment_type == "UPI":
            # Process UPI payment
            self._process_upi_payment(total)
        elif payment_type == "CREDIT":
            # Process credit payment
            self._process_credit_payment(total)
        elif payment_type == "SPLIT":
            # Process split payment
            self._process_split_payment(total)
    
    def _process_cash_payment(self, total):
        """Process cash payment"""
        # Create dialog
        dialog = tk.Toplevel(self)
        dialog.title("Cash Payment")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Set dialog position
        self._set_dialog_transient(dialog)
        
        # Create frame for content
        content_frame = tk.Frame(dialog, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        tk.Label(content_frame, 
               text="Cash Payment",
               font=FONTS["subheading"]).pack(pady=(0, 20))
        
        # Create a frame for tax breakdown
        breakdown_frame = tk.Frame(content_frame)
        breakdown_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Subtotal row
        tk.Label(breakdown_frame, 
               text="Subtotal:",
               font=FONTS["regular"]).grid(row=0, column=0, sticky="w", pady=2)
        
        # Calculate subtotal by removing GST from total
        subtotal = sum(item["total"] for item in self.cart_items)
        tk.Label(breakdown_frame, 
               text=format_currency(subtotal),
               font=FONTS["regular"]).grid(row=0, column=1, sticky="e", pady=2)
               
        # CGST row
        tk.Label(breakdown_frame, 
               text="CGST (2.5%):",
               font=FONTS["regular"]).grid(row=1, column=0, sticky="w", pady=2)
               
        tk.Label(breakdown_frame, 
               text=format_currency(self.cgst_amount),
               font=FONTS["regular"]).grid(row=1, column=1, sticky="e", pady=2)
               
        # SGST row
        tk.Label(breakdown_frame, 
               text="SGST (2.5%):",
               font=FONTS["regular"]).grid(row=2, column=0, sticky="w", pady=2)
               
        tk.Label(breakdown_frame, 
               text=format_currency(self.sgst_amount),
               font=FONTS["regular"]).grid(row=2, column=1, sticky="e", pady=2)
        
        # Total amount row
        tk.Label(breakdown_frame, 
               text="Total Amount:",
               font=FONTS["regular_bold"]).grid(row=3, column=0, sticky="w", pady=5)
        
        total_label = tk.Label(breakdown_frame, 
                             text=format_currency(total),
                             font=FONTS["heading"],
                             fg=COLORS["primary"])
        total_label.grid(row=3, column=1, sticky="e", pady=5)
        
        # Configure columns
        breakdown_frame.columnconfigure(0, weight=1)
        breakdown_frame.columnconfigure(1, weight=1)
        
        # Received amount
        tk.Label(content_frame, 
               text="Amount Received:",
               font=FONTS["regular_bold"]).pack(anchor="w")
        
        received_var = tk.StringVar(value=str(total))
        received_entry = tk.Entry(content_frame, 
                                textvariable=received_var,
                                font=FONTS["heading"],
                                width=15)
        received_entry.pack(anchor="w", pady=(0, 20))
        received_entry.select_range(0, tk.END)  # Select all text
        
        # Change
        tk.Label(content_frame, 
               text="Change:",
               font=FONTS["regular_bold"]).pack(anchor="w")
        
        change_label = tk.Label(content_frame, 
                              text="₹0.00",
                              font=FONTS["heading"],
                              fg=COLORS["secondary"])
        change_label.pack(anchor="w", pady=(0, 20))
        
        # Calculate change on input
        def calculate_change(*args):
            try:
                received = Decimal(str(received_var.get()))
                change = received - total
                change_label.config(text=format_currency(change))
            except (ValueError, InvalidOperation):
                change_label.config(text="₹0.00")
        
        received_var.trace_add("write", calculate_change)
        
        # Calculate initial change
        calculate_change()
        
        # Buttons
        button_frame = tk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        cancel_btn = tk.Button(button_frame,
                             text="Cancel",
                             font=FONTS["regular"],
                             padx=20,
                             pady=5,
                             command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        def complete_sale():
            try:
                received = Decimal(str(received_var.get()))
                if received < total:
                    messagebox.showwarning("Insufficient Payment", 
                                         "Amount received is less than total amount!")
                    return
                
                # Proceed with completing the sale
                dialog.destroy()
                # Use a reference object to pass data between methods
                payment_data = {
                    "payment_type": "CASH",
                    "amount": total,
                    "received": received,
                    "change": received - total,
                    "reference": None
                }
                self._complete_sale(payment_data)
                
            except ValueError:
                messagebox.showwarning("Invalid Amount", 
                                     "Please enter a valid amount!")
        
        complete_btn = tk.Button(button_frame,
                               text="Complete Sale",
                               font=FONTS["regular_bold"],
                               bg=COLORS["success"],
                               fg=COLORS["text_white"],
                               padx=20,
                               pady=5,
                               command=complete_sale)
        complete_btn.pack(side=tk.RIGHT, padx=5)
        
        # Set focus to received amount entry
        received_entry.focus_set()
        
        # Bind Enter key
        dialog.bind("<Return>", lambda event: complete_sale())
        
        # Wait for dialog to close
        dialog.wait_window()
    
    def _process_upi_payment(self, total):
        """Process UPI payment"""
        # Create dialog
        dialog = tk.Toplevel(self)
        dialog.title("UPI Payment")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Set dialog position
        self._set_dialog_transient(dialog)
        
        # Create frame for content
        content_frame = tk.Frame(dialog, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        tk.Label(content_frame, 
               text="UPI Payment",
               font=FONTS["subheading"]).pack(pady=(0, 20))
        
        # Create a frame for tax breakdown
        breakdown_frame = tk.Frame(content_frame)
        breakdown_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Subtotal row
        tk.Label(breakdown_frame, 
               text="Subtotal:",
               font=FONTS["regular"]).grid(row=0, column=0, sticky="w", pady=2)
        
        # Calculate subtotal by removing GST from total
        subtotal = sum(item["total"] for item in self.cart_items)
        tk.Label(breakdown_frame, 
               text=format_currency(subtotal),
               font=FONTS["regular"]).grid(row=0, column=1, sticky="e", pady=2)
               
        # CGST row
        tk.Label(breakdown_frame, 
               text="CGST (2.5%):",
               font=FONTS["regular"]).grid(row=1, column=0, sticky="w", pady=2)
               
        tk.Label(breakdown_frame, 
               text=format_currency(self.cgst_amount),
               font=FONTS["regular"]).grid(row=1, column=1, sticky="e", pady=2)
               
        # SGST row
        tk.Label(breakdown_frame, 
               text="SGST (2.5%):",
               font=FONTS["regular"]).grid(row=2, column=0, sticky="w", pady=2)
               
        tk.Label(breakdown_frame, 
               text=format_currency(self.sgst_amount),
               font=FONTS["regular"]).grid(row=2, column=1, sticky="e", pady=2)
        
        # Total amount row
        tk.Label(breakdown_frame, 
               text="Total Amount:",
               font=FONTS["regular_bold"]).grid(row=3, column=0, sticky="w", pady=5)
        
        total_label = tk.Label(breakdown_frame, 
                             text=format_currency(total),
                             font=FONTS["heading"],
                             fg=COLORS["primary"])
        total_label.grid(row=3, column=1, sticky="e", pady=5)
        
        # Configure columns
        breakdown_frame.columnconfigure(0, weight=1)
        breakdown_frame.columnconfigure(1, weight=1)
        
        # Transaction reference
        tk.Label(content_frame, 
               text="UPI Transaction Reference:",
               font=FONTS["regular_bold"]).pack(anchor="w")
        
        reference_var = tk.StringVar()
        reference_entry = tk.Entry(content_frame, 
                                 textvariable=reference_var,
                                 font=FONTS["regular"],
                                 width=30)
        reference_entry.pack(anchor="w", pady=(0, 5))
        
        # Hint for UPI reference
        hint_label = tk.Label(content_frame, 
                           text="Enter the last 6 digits of the UPI transaction ID",
                           font=FONTS["small"],
                           fg=COLORS["text_secondary"])
        hint_label.pack(anchor="w", pady=(0, 20))
        
        # Buttons
        button_frame = tk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        cancel_btn = tk.Button(button_frame,
                             text="Cancel",
                             font=FONTS["regular"],
                             padx=20,
                             pady=5,
                             command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        def complete_sale():
            reference = reference_var.get().strip()
            if not reference:
                messagebox.showwarning("Missing Reference", 
                                     "Please enter the UPI transaction reference!")
                return
            
            # Validate reference format (simple check for 6 digits)
            if not (reference.isdigit() and 4 <= len(reference) <= 10):
                messagebox.showwarning("Invalid Reference", 
                                     "Please enter a valid UPI reference (4-10 digits)!")
                return
            
            # Proceed with completing the sale
            dialog.destroy()
            # Use a reference object to pass data between methods
            payment_data = {
                "payment_type": "UPI",
                "amount": total,
                "received": total,  # Exact amount for UPI
                "change": Decimal('0'),
                "reference": reference
            }
            self._complete_sale(payment_data)
        
        complete_btn = tk.Button(button_frame,
                               text="Complete Sale",
                               font=FONTS["regular_bold"],
                               bg=COLORS["success"],
                               fg=COLORS["text_white"],
                               padx=20,
                               pady=5,
                               command=complete_sale)
        complete_btn.pack(side=tk.RIGHT, padx=5)
        
        # Set focus to reference entry
        reference_entry.focus_set()
        
        # Bind Enter key
        dialog.bind("<Return>", lambda event: complete_sale())
        
        # Wait for dialog to close
        dialog.wait_window()
    
    def _process_credit_payment(self, total):
        """Process credit payment"""
        # Check if customer is walk-in
        if self.current_customer["id"] == 1:
            messagebox.showwarning("Cannot Extend Credit", 
                                 "Credit sales require a registered customer. " +
                                 "Please change the customer before proceeding with credit payment.")
            return
            
        # Create dialog
        dialog = tk.Toplevel(self)
        dialog.title("Credit Payment")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Set dialog position
        self._set_dialog_transient(dialog)
        
        # Create frame for content
        content_frame = tk.Frame(dialog, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        tk.Label(content_frame, 
               text="Credit Payment",
               font=FONTS["subheading"]).pack(pady=(0, 20))
        
        # Customer info
        tk.Label(content_frame, 
               text="Customer:",
               font=FONTS["regular_bold"]).pack(anchor="w")
        
        customer_label = tk.Label(content_frame, 
                                text=self.current_customer["name"],
                                font=FONTS["regular"])
        customer_label.pack(anchor="w", pady=(0, 10))
        
        # Create a frame for tax breakdown
        breakdown_frame = tk.Frame(content_frame)
        breakdown_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Subtotal row
        tk.Label(breakdown_frame, 
               text="Subtotal:",
               font=FONTS["regular"]).grid(row=0, column=0, sticky="w", pady=2)
        
        # Calculate subtotal by removing GST from total
        subtotal = sum(item["total"] for item in self.cart_items)
        tk.Label(breakdown_frame, 
               text=format_currency(subtotal),
               font=FONTS["regular"]).grid(row=0, column=1, sticky="e", pady=2)
               
        # CGST row
        tk.Label(breakdown_frame, 
               text="CGST (2.5%):",
               font=FONTS["regular"]).grid(row=1, column=0, sticky="w", pady=2)
               
        tk.Label(breakdown_frame, 
               text=format_currency(self.cgst_amount),
               font=FONTS["regular"]).grid(row=1, column=1, sticky="e", pady=2)
               
        # SGST row
        tk.Label(breakdown_frame, 
               text="SGST (2.5%):",
               font=FONTS["regular"]).grid(row=2, column=0, sticky="w", pady=2)
               
        tk.Label(breakdown_frame, 
               text=format_currency(self.sgst_amount),
               font=FONTS["regular"]).grid(row=2, column=1, sticky="e", pady=2)
        
        # Total amount row
        tk.Label(breakdown_frame, 
               text="Total Amount:",
               font=FONTS["regular_bold"]).grid(row=3, column=0, sticky="w", pady=5)
        
        total_label = tk.Label(breakdown_frame, 
                             text=format_currency(total),
                             font=FONTS["heading"],
                             fg=COLORS["primary"])
        total_label.grid(row=3, column=1, sticky="e", pady=5)
        
        # Configure columns
        breakdown_frame.columnconfigure(0, weight=1)
        breakdown_frame.columnconfigure(1, weight=1)
        
        # Get customer's current credit balance
        db = self.controller.db
        credit_balance = db.fetchone("""
            SELECT COALESCE(SUM(
                CASE 
                    WHEN transaction_type = 'CREDIT_SALE' THEN amount 
                    WHEN transaction_type = 'CREDIT_PAYMENT' THEN -amount 
                    ELSE 0 
                END
            ), 0) as balance
            FROM customer_transactions
            WHERE customer_id = ?
        """, (self.current_customer["id"],))
        
        current_balance = credit_balance[0] if credit_balance else 0
        new_balance = current_balance + total
        
        # Show credit balance
        tk.Label(content_frame, 
               text="Current Credit Balance:",
               font=FONTS["regular_bold"]).pack(anchor="w")
        
        balance_label = tk.Label(content_frame, 
                               text=format_currency(current_balance),
                               font=FONTS["regular"])
        balance_label.pack(anchor="w", pady=(0, 10))
        
        tk.Label(content_frame, 
               text="New Credit Balance (after this sale):",
               font=FONTS["regular_bold"]).pack(anchor="w")
        
        new_balance_label = tk.Label(content_frame, 
                                   text=format_currency(new_balance),
                                   font=FONTS["regular"],
                                   fg=COLORS["danger"])
        new_balance_label.pack(anchor="w", pady=(0, 20))
        
        # Buttons
        button_frame = tk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        cancel_btn = tk.Button(button_frame,
                             text="Cancel",
                             font=FONTS["regular"],
                             padx=20,
                             pady=5,
                             command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        def complete_sale():
            # Confirm credit sale
            if messagebox.askyesno("Confirm Credit Sale", 
                                 f"Extend credit of {format_currency(total)} to {self.current_customer['name']}?"):
                # Proceed with completing the sale
                dialog.destroy()
                # Use a reference object to pass data between methods
                payment_data = {
                    "payment_type": "CREDIT",
                    "amount": total,
                    "received": Decimal('0'),  # No immediate payment
                    "change": Decimal('0'),
                    "reference": None
                }
                self._complete_sale(payment_data)
        
        complete_btn = tk.Button(button_frame,
                               text="Complete Credit Sale",
                               font=FONTS["regular_bold"],
                               bg=COLORS["primary"],
                               fg=COLORS["text_white"],
                               padx=20,
                               pady=5,
                               command=complete_sale)
        complete_btn.pack(side=tk.RIGHT, padx=5)
        
        # Bind Enter key
        dialog.bind("<Return>", lambda event: complete_sale())
        
        # Wait for dialog to close
        dialog.wait_window()
    
    def _process_split_payment(self, total):
        """Process split payment (cash + UPI)"""
        # Create dialog
        dialog = tk.Toplevel(self)
        dialog.title("Split Payment")
        dialog.geometry("500x500")
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Set dialog position
        self._set_dialog_transient(dialog)
        
        # Create frame for content
        content_frame = tk.Frame(dialog, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        tk.Label(content_frame, 
               text="Split Payment",
               font=FONTS["subheading"]).pack(pady=(0, 20))
        
        # Create a frame for tax breakdown
        breakdown_frame = tk.Frame(content_frame)
        breakdown_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Subtotal row
        tk.Label(breakdown_frame, 
               text="Subtotal:",
               font=FONTS["regular"]).grid(row=0, column=0, sticky="w", pady=2)
        
        # Calculate subtotal by removing GST from total
        subtotal = sum(item["total"] for item in self.cart_items)
        tk.Label(breakdown_frame, 
               text=format_currency(subtotal),
               font=FONTS["regular"]).grid(row=0, column=1, sticky="e", pady=2)
               
        # CGST row
        tk.Label(breakdown_frame, 
               text="CGST (2.5%):",
               font=FONTS["regular"]).grid(row=1, column=0, sticky="w", pady=2)
               
        tk.Label(breakdown_frame, 
               text=format_currency(self.cgst_amount),
               font=FONTS["regular"]).grid(row=1, column=1, sticky="e", pady=2)
               
        # SGST row
        tk.Label(breakdown_frame, 
               text="SGST (2.5%):",
               font=FONTS["regular"]).grid(row=2, column=0, sticky="w", pady=2)
               
        tk.Label(breakdown_frame, 
               text=format_currency(self.sgst_amount),
               font=FONTS["regular"]).grid(row=2, column=1, sticky="e", pady=2)
        
        # Total amount row
        tk.Label(breakdown_frame, 
               text="Total Amount:",
               font=FONTS["regular_bold"]).grid(row=3, column=0, sticky="w", pady=5)
        
        total_label = tk.Label(breakdown_frame, 
                             text=format_currency(total),
                             font=FONTS["heading"],
                             fg=COLORS["primary"])
        total_label.grid(row=3, column=1, sticky="e", pady=5)
        
        # Configure columns
        breakdown_frame.columnconfigure(0, weight=1)
        breakdown_frame.columnconfigure(1, weight=1)
        
        # Cash amount
        tk.Label(content_frame, 
               text="Cash Amount:",
               font=FONTS["regular_bold"]).pack(anchor="w")
        
        cash_var = tk.StringVar(value="0.00")
        cash_entry = tk.Entry(content_frame, 
                            textvariable=cash_var,
                            font=FONTS["regular"],
                            width=15)
        cash_entry.pack(anchor="w", pady=(0, 10))
        
        # UPI amount
        tk.Label(content_frame, 
               text="UPI Amount:",
               font=FONTS["regular_bold"]).pack(anchor="w")
        
        upi_var = tk.StringVar(value=str(total))
        upi_label = tk.Label(content_frame, 
                           textvariable=upi_var,
                           font=FONTS["regular"],
                           fg=COLORS["secondary"])
        upi_label.pack(anchor="w", pady=(0, 10))
        
        # Update UPI amount when cash amount changes
        def update_upi_amount(*args):
            try:
                cash_amount = Decimal(str(cash_var.get()))
                upi_amount = total - cash_amount
                if upi_amount < Decimal('0'):
                    upi_amount = Decimal('0')
                upi_var.set(format_currency(upi_amount))
            except (ValueError, InvalidOperation):
                upi_var.set(format_currency(total))
        
        cash_var.trace_add("write", update_upi_amount)
        
        # UPI reference
        tk.Label(content_frame, 
               text="UPI Transaction Reference:",
               font=FONTS["regular_bold"]).pack(anchor="w")
        
        reference_var = tk.StringVar()
        reference_entry = tk.Entry(content_frame, 
                                 textvariable=reference_var,
                                 font=FONTS["regular"],
                                 width=30)
        reference_entry.pack(anchor="w", pady=(0, 5))
        
        # Hint for UPI reference
        hint_label = tk.Label(content_frame, 
                           text="Enter the last 6 digits of the UPI transaction ID",
                           font=FONTS["small"],
                           fg=COLORS["text_secondary"])
        hint_label.pack(anchor="w", pady=(0, 20))
        
        # Buttons
        button_frame = tk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        cancel_btn = tk.Button(button_frame,
                             text="Cancel",
                             font=FONTS["regular"],
                             padx=20,
                             pady=5,
                             command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        def complete_sale():
            try:
                cash_amount = Decimal(str(cash_var.get()))
                upi_amount = total - cash_amount
                
                # Validate amounts
                if cash_amount < Decimal('0') or upi_amount < Decimal('0'):
                    messagebox.showwarning("Invalid Amounts", 
                                         "Payment amounts cannot be negative!")
                    return
                
                # Validate total
                if abs((cash_amount + upi_amount) - total) > Decimal('0.01'):  # Allow small rounding error
                    messagebox.showwarning("Payment Mismatch", 
                                         f"Total payment ({cash_amount + upi_amount}) does not match sale total ({total})!")
                    return
                
                # If UPI amount is significant, require reference
                if upi_amount > Decimal('0.01'):  # More than 0.01 is considered UPI payment
                    reference = reference_var.get().strip()
                    if not reference:
                        messagebox.showwarning("Missing Reference", 
                                             "Please enter the UPI transaction reference!")
                        return
                    
                    # Validate reference format (simple check for 6 digits)
                    if not (reference.isdigit() and 4 <= len(reference) <= 10):
                        messagebox.showwarning("Invalid Reference", 
                                             "Please enter a valid UPI reference (4-10 digits)!")
                        return
                else:
                    reference = None
                
                # Proceed with completing the sale
                dialog.destroy()
                # Use a reference object to pass data between methods
                payment_data = {
                    "payment_type": "SPLIT",
                    "amount": total,
                    "cash_amount": cash_amount,
                    "upi_amount": upi_amount,
                    "received": cash_amount + upi_amount,  # Total received
                    "change": Decimal('0'),  # No change in split payment
                    "reference": reference
                }
                self._complete_sale(payment_data)
                
            except (ValueError, InvalidOperation):
                messagebox.showwarning("Invalid Amount", 
                                     "Please enter a valid cash amount!")
        
        complete_btn = tk.Button(button_frame,
                               text="Complete Sale",
                               font=FONTS["regular_bold"],
                               bg=COLORS["success"],
                               fg=COLORS["text_white"],
                               padx=20,
                               pady=5,
                               command=complete_sale)
        complete_btn.pack(side=tk.RIGHT, padx=5)
        
        # Set focus to cash entry
        cash_entry.focus_set()
        
        # Bind Enter key to move between fields
        cash_entry.bind("<Return>", lambda event: reference_entry.focus_set())
        reference_entry.bind("<Return>", lambda event: complete_sale())
        
        # Wait for dialog to close
        dialog.wait_window()
    
    def _complete_sale(self, payment_data):
        """Complete the sale and save to database"""
        # Calculate totals
        subtotal = sum(item["total"] for item in self.cart_items)
        
        # Convert to Decimal for consistent types and precision
        subtotal = Decimal(str(subtotal))
        
        # Apply any additional discount
        try:
            discount_value = Decimal(str(self.discount_var.get()))
            discount_type = self.discount_type_var.get()
            
            if discount_type == "amount":
                # Fixed amount discount
                discount_amount = discount_value
            else:
                # Percentage discount
                discount_amount = subtotal * discount_value / Decimal('100')
                
            # Ensure discount doesn't exceed subtotal
            discount_amount = min(discount_amount, subtotal)
            
        except (ValueError, InvalidOperation):
            # Invalid discount value, treat as zero
            discount_amount = Decimal('0')
        
        # Calculate final subtotal after discount
        final_subtotal = subtotal - discount_amount
        
        # Store sale in database
        db = self.controller.db
        try:
            db.begin()
            
            # Get financial year for invoice number prefix
            today = datetime.datetime.now()
            if today.month >= 4:  # After April 1 (Indian Financial Year starts in April)
                fy_start = today.year
                fy_end = today.year + 1
            else:
                fy_start = today.year - 1
                fy_end = today.year
            
            # Format as YY-YY (e.g., 24-25)
            fy_prefix = f"{str(fy_start)[-2:]}-{str(fy_end)[-2:]}"
            
            # Get store name for invoice number prefix
            store_name = "AGT"  # Default prefix
            store_info = db.fetchone("SELECT value FROM settings WHERE key = 'invoice_prefix'")
            if store_info and store_info[0].strip():
                store_name = store_info[0].strip()
            
            # Get next invoice number
            invoice_prefix = f"{fy_prefix}/{store_name}-"
            last_invoice = db.fetchone("""
                SELECT invoice_number FROM sales
                WHERE invoice_number LIKE ?
                ORDER BY id DESC LIMIT 1
            """, (f"{fy_prefix}/%",))
            
            if last_invoice:
                try:
                    # Extract the numeric part
                    last_part = last_invoice[0].split('-')[-1]
                    last_num = int(last_part)
                    invoice_num = last_num + 1
                except (ValueError, IndexError):
                    invoice_num = 1
            else:
                invoice_num = 1
            
            # Format invoice number with 3 digits (e.g., 24-25/AGT-001)
            invoice_number = f"{fy_prefix}/{store_name}-{invoice_num:03d}"
            
            # Create sale record with better tax handling (split into CGST and SGST)
            tax_amount = Decimal(str(final_subtotal)) * Decimal('0.05')  # 5% GST (2.5% CGST + 2.5% SGST)
            
            sale_id = db.insert("sales", {
                "customer_id": self.current_customer["id"],
                "invoice_number": invoice_number,
                "subtotal": subtotal,
                "discount": discount_amount,
                "tax": tax_amount,  # Total GST (5%)
                "cgst": tax_amount / Decimal('2'),  # 2.5% CGST
                "sgst": tax_amount / Decimal('2'),  # 2.5% SGST
                "total": payment_data["amount"],
                "payment_type": payment_data["payment_type"],
                "payment_reference": payment_data.get("reference"),
                "sale_date": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "user_id": 1  # Default user ID
            })
            
            # Store split payment details if applicable
            if payment_data["payment_type"] == "SPLIT":
                db.insert("payment_splits", {
                    "sale_id": sale_id,
                    "cash_amount": payment_data["cash_amount"],
                    "upi_amount": payment_data["upi_amount"],
                    "upi_reference": payment_data["reference"]
                })
            
            # Store sale items
            for item in self.cart_items:
                # Get product price from database to ensure data integrity
                product_price = item["price"]
                if item["product_id"]:
                    product_info = db.fetchone("""
                        SELECT selling_price FROM products WHERE id = ?
                    """, (item["product_id"],))
                    if product_info:
                        product_price = product_info[0]
                
                # Calculate item tax with proper Decimal handling
                tax_rate = item.get("tax_rate", 5)  # Default 5% if not specified
                price = Decimal(str(item["price"]))
                quantity = Decimal(str(item["quantity"]))
                discount = Decimal(str(item["discount"]))
                tax_rate_decimal = Decimal(str(tax_rate))
                
                # Calculate discounted price
                discounted_amount = price * quantity * (Decimal('1') - discount / Decimal('100'))
                
                # Calculate tax amount (split between CGST and SGST)
                tax_amount = discounted_amount * (tax_rate_decimal / Decimal('100'))
                
                # Insert sale item
                sale_item_id = db.insert("sale_items", {
                    "sale_id": sale_id,
                    "product_id": item["product_id"],
                    "product_name": item["name"],
                    "hsn_code": item.get("hsn_code", ""),
                    "quantity": item["quantity"],
                    "price": product_price,
                    "discount_percent": item["discount"],
                    "tax_rate": tax_rate,
                    "tax_amount": tax_amount,
                    "total": item["total"]
                })
                
                # Update inventory for database products
                if item["product_id"]:
                    # Get batches for this product, starting with oldest expiry
                    batches = db.fetchall("""
                        SELECT id, quantity
                        FROM batches
                        WHERE product_id = ? AND quantity > 0 AND expiry_date > date('now')
                        ORDER BY expiry_date ASC
                    """, (item["product_id"],))
                    
                    remaining_qty = item["quantity"]
                    for batch_id, batch_qty in batches:
                        if remaining_qty <= 0:
                            break
                        
                        # How much to take from this batch
                        batch_deduction = min(remaining_qty, batch_qty)
                        
                        # Update batch quantity
                        db.execute("""
                            UPDATE batches
                            SET quantity = quantity - ?
                            WHERE id = ?
                        """, (batch_deduction, batch_id))
                        
                        # Record inventory movement
                        db.insert("inventory_movements", {
                            "product_id": item["product_id"],
                            "batch_id": batch_id,
                            "quantity": -batch_deduction,
                            "movement_type": "SALE",
                            "reference_id": sale_item_id,
                            "movement_date": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                        
                        remaining_qty -= batch_deduction
            
            # If credit sale, record the transaction
            if payment_data["payment_type"] == "CREDIT":
                db.insert("customer_transactions", {
                    "customer_id": self.current_customer["id"],
                    "amount": payment_data["amount"],
                    "transaction_type": "CREDIT_SALE",
                    "reference_id": sale_id,
                    "transaction_date": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "notes": f"Credit sale - Invoice #{invoice_number}"
                })
            
            db.commit()
            
            # Show success message
            messagebox.showinfo("Sale Complete", 
                              f"Sale completed successfully!\nInvoice #: {invoice_number}")
            
            # Generate and print invoice
            self._generate_invoice(sale_id, invoice_number)
            
            # Reset cart
            self.cart_items = []
            
            # Reset to walk-in customer
            self.current_customer = {
                "id": 1,
                "name": "Walk-in Customer",
                "phone": "",
                "address": ""
            }
            self.customer_label.config(text="Walk-in Customer")
            
            # Reset discount
            self.discount_var.set("0.00")
            self.discount_type_var.set("amount")
            
            # Update cart display
            self.update_cart()
            
            # Reset item ID counter
            self.next_item_id = 1
            
        except Exception as e:
            db.rollback()
            messagebox.showerror("Error", f"Failed to complete sale: {str(e)}")
            # Log the error for debugging
            print(f"Sale error: {str(e)}")
    
    def _generate_invoice(self, sale_id, invoice_number):
        """Generate invoice for completed sale"""
        db = self.controller.db
        
        # Get sale details
        sale = db.fetchone("""
            SELECT s.*, c.name as customer_name, c.phone as customer_phone,
                   c.address as customer_address, c.village as customer_village,
                   c.gstin as customer_gstin
            FROM sales s
            JOIN customers c ON s.customer_id = c.id
            WHERE s.id = ?
        """, (sale_id,))
        
        if not sale:
            messagebox.showerror("Error", "Could not find sale details for invoice generation!")
            return
        
        # Get sale items
        items = db.fetchall("""
            SELECT si.*, p.hsn_code
            FROM sale_items si
            LEFT JOIN products p ON si.product_id = p.id
            WHERE si.sale_id = ?
        """, (sale_id,))
        
        # Get store info
        store_info = {}
        settings = db.fetchall("SELECT key, value FROM settings WHERE key IN ('store_name', 'store_address', 'store_phone', 'store_gstin', 'store_email')")
        for key, value in settings:
            store_info[key] = value
        
        # Prepare invoice data
        invoice_data = {
            "invoice_number": invoice_number,
            "date": datetime.datetime.strptime(sale[9], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y'),
            "time": datetime.datetime.strptime(sale[9], '%Y-%m-%d %H:%M:%S').strftime('%I:%M %p'),
            "store_info": {
                "name": store_info.get("store_name", "Agritech Store"),
                "address": store_info.get("store_address", "Address Not Set"),
                "phone": store_info.get("store_phone", "Phone Not Set"),
                "gstin": store_info.get("store_gstin", "GSTIN Not Set"),
                "email": store_info.get("store_email", "Email Not Set")
            },
            "customer": {
                "name": sale[11],
                "phone": sale[12],
                "address": sale[13],
                "village": sale[14],
                "gstin": sale[15]
            },
            "items": [],
            "payment": {
                "subtotal": sale[3],
                "discount": sale[4],
                "cgst": sale[6],  # Using CGST column directly
                "sgst": sale[7],  # Using SGST column directly
                "total": sale[8],
                "method": sale[9],
                "reference": sale[10]
            }
        }
        
        # Add payment split details if applicable
        if sale[9] == "SPLIT":  # Updated index for payment_type
            payment_split = db.fetchone("""
                SELECT cash_amount, upi_amount, upi_reference
                FROM payment_splits
                WHERE sale_id = ?
            """, (sale_id,))
            
            if payment_split:
                invoice_data["payment"]["split"] = {
                    "cash_amount": payment_split[0],
                    "upi_amount": payment_split[1],
                    "upi_reference": payment_split[2]
                }
        
        # Add items
        for item in items:
            # Use HSN code from product if available, otherwise from sale_item
            hsn_code = item[12] if item[12] else item[3]
            
            invoice_data["items"].append({
                "name": item[2],
                "hsn_code": hsn_code,
                "quantity": item[4],
                "price": item[5],
                "discount": item[6],
                "tax_rate": item[7],
                "tax_amount": item[8],
                "total": item[9]
            })
        
        try:
            # Get invoice directory
            invoices_dir = os.path.join(os.getcwd(), "invoices")
            os.makedirs(invoices_dir, exist_ok=True)
            
            # Save path
            file_name = f"Invoice_{invoice_number.replace('/', '-')}.pdf"
            save_path = os.path.join(invoices_dir, file_name)
            
            # Generate PDF
            from utils.invoice_generator import generate_invoice
            generate_invoice(invoice_data, save_path)
            
            # Ask if user wants to open the invoice
            if messagebox.askyesno("Invoice Generated", 
                                 f"Invoice generated successfully: {file_name}\n\nOpen invoice?"):
                import platform
                import subprocess
                
                # Open PDF with default viewer
                if platform.system() == 'Windows':
                    # Use subprocess instead of os.startfile for better cross-platform compatibility
                    subprocess.call(['start', '', save_path], shell=True)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.call(['open', save_path])
                else:  # Linux
                    subprocess.call(['xdg-open', save_path])
                
        except Exception as e:
            messagebox.showerror("Invoice Error", f"Failed to generate invoice: {str(e)}")
            # Log the error for debugging
            print(f"Invoice error: {str(e)}")
    
    def handle_key_event(self, event):
        """Handle keyboard events for navigation"""
        key = event.keysym
        ctrl = event.state & 0x4  # Control key
        shift = event.state & 0x1  # Shift key
        
        # Get the widget that currently has focus
        focused_widget = self.focus_get()
        
        # Tab key to cycle focus
        if key == "Tab":
            if not self.current_focus:
                self.current_focus = "products"
            elif self.current_focus == "products":
                self.current_focus = "cart"
            elif self.current_focus == "cart":
                self.current_focus = "buttons"
            else:
                self.current_focus = "products"
            
            self._update_focus()
            return "break"  # Prevent default tab behavior
        
        # Ctrl+Shift+P to focus products
        elif ctrl and shift and key.lower() == "p":
            self.current_focus = "products"
            self._update_focus()
            return "break"
        
        # Ctrl+Shift+C to focus cart
        elif ctrl and shift and key.lower() == "c":
            self.current_focus = "cart"
            self._update_focus()
            return "break"
        
        # Ctrl+Shift+B to focus buttons
        elif ctrl and shift and key.lower() == "b":
            self.current_focus = "buttons"
            self._update_focus()
            return "break"
        
        # Enter key to select or edit
        elif key == "Return":
            # Check if we're in the products or cart treeview
            if focused_widget == self.products_tree:
                # The Enter key is now directly bound to the treeview via self.products_tree.bind("<Return>", self.add_to_cart)
                # so we don't need to handle it here, but keep as backup
                self.add_to_cart(None)
                return "break"
            elif focused_widget == self.cart_tree:
                self.edit_cart_item()
                return "break"
            elif self.current_focus == "products":
                self.add_to_cart(None)
            elif self.current_focus == "cart":
                self.edit_cart_item()
        
        # Escape key to clear search
        elif key == "Escape":
            if self.current_focus == "products" or focused_widget == self.products_tree:
                self.search_var.set("")
                self.load_products()
    
    def _update_focus(self):
        """Update the focus based on current_focus"""
        if self.current_focus == "products":
            # Focus products treeview
            self.products_tree.focus_set()
            
            # Select first item if none selected
            if not self.products_tree.selection():
                items = self.products_tree.get_children()
                if items:
                    self.products_tree.selection_set(items[0])
                    self.products_tree.focus(items[0])
        
        elif self.current_focus == "cart":
            # Focus cart treeview
            self.cart_tree.focus_set()
            
            # Select first item if none selected
            if not self.cart_tree.selection():
                items = self.cart_tree.get_children()
                if items:
                    self.cart_tree.selection_set(items[0])
                    self.cart_tree.focus(items[0])
        
        elif self.current_focus == "buttons":
            # For now, just focus the search entry
            # In a future enhancement, we could make the payment buttons focusable
            self.search_var.set("")
            search_entry = self.winfo_children()[0].winfo_children()[0].winfo_children()[0]
            search_entry.focus_set()
    
    def on_show(self):
        """Called when frame is shown"""
        # Reset the view
        self.load_products()
        
        # Set initial focus to products treeview
        self.current_focus = "products"
        self._update_focus()