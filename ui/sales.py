"""
Sales UI for POS system
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import datetime
import re
import os
import decimal
from decimal import Decimal

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
        
    def create_layout(self):
        """Create the sales layout"""
        # Main container with two frames side by side
        main_container = tk.Frame(self, bg=COLORS["bg_primary"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Cart
        self.left_panel = tk.Frame(main_container, bg=COLORS["bg_primary"], width=800)
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Right panel - Product search and customer info
        self.right_panel = tk.Frame(main_container, bg=COLORS["bg_secondary"], width=400)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        self.right_panel.pack_propagate(False)  # Don't shrink
        
        # Setup left panel (cart)
        self.setup_cart_panel(self.left_panel)
        
        # Setup right panel (product search)
        self.setup_product_panel(self.right_panel)
    
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
        
        # Bind discount changes
        self.discount_var.trace_add("write", lambda *args: self.update_totals())
        self.discount_type_var.trace_add("write", lambda *args: self.update_totals())
        
        # Tax
        tk.Label(totals_frame, 
               text="Tax:",
               font=FONTS["regular_bold"],
               bg=COLORS["bg_white"],
               fg=COLORS["text_primary"]).grid(row=2, column=0, sticky="w", pady=5)
               
        self.tax_label = tk.Label(totals_frame, 
                                text="₹0.00",
                                font=FONTS["regular"],
                                bg=COLORS["bg_white"],
                                fg=COLORS["text_primary"])
        self.tax_label.grid(row=2, column=1, sticky="e", pady=5)
        
        # Total
        tk.Label(totals_frame, 
               text="TOTAL:",
               font=FONTS["heading"],
               bg=COLORS["bg_white"],
               fg=COLORS["text_primary"]).grid(row=3, column=0, sticky="w", pady=10)
               
        self.total_label = tk.Label(totals_frame, 
                                  text="₹0.00",
                                  font=FONTS["heading"],
                                  bg=COLORS["bg_white"],
                                  fg=COLORS["primary"])
        self.total_label.grid(row=3, column=1, sticky="e", pady=10)
        
        # Make totals_frame columns expandable
        totals_frame.columnconfigure(0, weight=1)
        totals_frame.columnconfigure(1, weight=1)
        
        # Payment buttons frame
        payment_frame = tk.Frame(parent, bg=COLORS["bg_primary"], pady=10)
        payment_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Cancel button
        cancel_btn = tk.Button(payment_frame,
                             text="Cancel Sale",
                             font=FONTS["regular_bold"],
                             bg=COLORS["danger"],
                             fg=COLORS["text_white"],
                             padx=15,
                             pady=8,
                             cursor="hand2",
                             command=self.cancel_sale)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Suspend button
        suspend_btn = tk.Button(payment_frame,
                              text="Suspend",
                              font=FONTS["regular_bold"],
                              bg=COLORS["warning"],
                              fg=COLORS["text_primary"],
                              padx=15,
                              pady=8,
                              cursor="hand2",
                              command=self.suspend_sale)
        suspend_btn.pack(side=tk.LEFT, padx=5)
        
        # Payment button - Cash
        cash_btn = tk.Button(payment_frame,
                           text="Cash Payment",
                           font=FONTS["regular_bold"],
                           bg=COLORS["secondary"],
                           fg=COLORS["text_white"],
                           padx=15,
                           pady=8,
                           cursor="hand2",
                           command=lambda: self.process_payment("CASH"))
        cash_btn.pack(side=tk.RIGHT, padx=5)
        
        # Payment button - UPI
        upi_btn = tk.Button(payment_frame,
                          text="UPI Payment",
                          font=FONTS["regular_bold"],
                          bg=COLORS["info"],
                          fg=COLORS["text_white"],
                          padx=15,
                          pady=8,
                          cursor="hand2",
                          command=lambda: self.process_payment("UPI"))
        upi_btn.pack(side=tk.RIGHT, padx=5)
        
        # Payment button - Split
        split_btn = tk.Button(payment_frame,
                            text="Split Payment",
                            font=FONTS["regular_bold"],
                            bg=COLORS["primary"],
                            fg=COLORS["text_white"],
                            padx=15,
                            pady=8,
                            cursor="hand2",
                            command=lambda: self.process_payment("SPLIT"))
        split_btn.pack(side=tk.RIGHT, padx=5)
        
        # Payment button - Credit
        credit_btn = tk.Button(payment_frame,
                             text="Credit Sale",
                             font=FONTS["regular_bold"],
                             bg=COLORS["primary_dark"],
                             fg=COLORS["text_white"],
                             padx=15,
                             pady=8,
                             cursor="hand2",
                             command=lambda: self.process_payment("CREDIT"))
        credit_btn.pack(side=tk.RIGHT, padx=5)
    
    def setup_product_panel(self, parent):
        """Setup the product search panel"""
        # Title
        title = tk.Label(parent, 
                       text="Product Search",
                       font=FONTS["subheading"],
                       bg=COLORS["bg_secondary"],
                       fg=COLORS["text_primary"])
        title.pack(pady=(20, 10))
        
        # Search frame
        search_frame = tk.Frame(parent, bg=COLORS["bg_secondary"], padx=10)
        search_frame.pack(fill=tk.X, pady=10)
        
        # Search entry
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, 
                              textvariable=self.search_var,
                              font=FONTS["regular"],
                              width=25)
        search_entry.pack(side=tk.LEFT, padx=(0, 5))
        search_entry.bind("<Return>", lambda event: self.search_products())
        
        # Search button
        search_btn = tk.Button(search_frame,
                             text="Search",
                             font=FONTS["regular"],
                             bg=COLORS["primary"],
                             fg=COLORS["text_white"],
                             padx=10,
                             pady=5,
                             cursor="hand2",
                             command=self.search_products)
        search_btn.pack(side=tk.LEFT)
        
        # Products treeview frame
        tree_frame = tk.Frame(parent, bg=COLORS["bg_secondary"])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create treeview for products
        self.product_tree = ttk.Treeview(tree_frame, 
                                       columns=("id", "name", "price", "stock"),
                                       show="headings",
                                       yscrollcommand=scrollbar.set)
        
        # Configure scrollbar
        scrollbar.config(command=self.product_tree.yview)
        
        # Define columns
        self.product_tree.heading("id", text="ID")
        self.product_tree.heading("name", text="Product Name")
        self.product_tree.heading("price", text="Price")
        self.product_tree.heading("stock", text="Stock")
        
        # Set column widths
        self.product_tree.column("id", width=50)
        self.product_tree.column("name", width=180)
        self.product_tree.column("price", width=80)
        self.product_tree.column("stock", width=60)
        
        self.product_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind double-click to add to cart
        self.product_tree.bind("<Double-1>", self.add_to_cart)
        # Bind right-click for context menu
        self.product_tree.bind("<Button-3>", self.show_product_context_menu)
        
        # Add to cart button
        add_to_cart_frame = tk.Frame(parent, bg=COLORS["bg_secondary"])
        add_to_cart_frame.pack(fill=tk.X, pady=5)
        
        add_to_cart_btn = tk.Button(add_to_cart_frame,
                                  text="Add Selected to Cart",
                                  font=FONTS["regular_bold"],
                                  bg=COLORS["primary"],
                                  fg=COLORS["text_white"],
                                  padx=15,
                                  pady=8,
                                  cursor="hand2",
                                  command=self.add_to_cart)
        add_to_cart_btn.pack(side=tk.LEFT, padx=10)
        
        # Add selection tip
        tip_label = tk.Label(add_to_cart_frame,
                           text="Tip: Double-click to add to cart",
                           font=FONTS["small"],
                           bg=COLORS["bg_secondary"],
                           fg=COLORS["text_secondary"])
        tip_label.pack(side=tk.RIGHT, padx=10)
        
        # Quick add button
        quick_add_btn = tk.Button(parent,
                                text="Quick Add New Product",
                                font=FONTS["regular_bold"],
                                bg=COLORS["secondary"],
                                fg=COLORS["text_white"],
                                padx=15,
                                pady=8,
                                cursor="hand2",
                                command=self.quick_add_product)
        quick_add_btn.pack(padx=10, pady=5)
        
        # Suspended bills button frame
        suspended_frame = tk.Frame(parent, bg=COLORS["bg_secondary"], padx=10, pady=10)
        suspended_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Suspended bills button
        suspended_btn = tk.Button(suspended_frame,
                                text="Suspended Bills",
                                font=FONTS["regular_bold"],
                                bg=COLORS["warning"],
                                fg=COLORS["text_primary"],
                                padx=15,
                                pady=8,
                                cursor="hand2",
                                command=self.show_suspended_bills)
        suspended_btn.pack(fill=tk.X)
        
        # Load initial products
        self.load_products()
    
    def load_products(self):
        """Load all products into the treeview"""
        # Clear existing items
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        # Get products with stock information
        query = """
            SELECT 
                p.id,
                p.name,
                p.selling_price,
                COALESCE(SUM(i.quantity), 0) as stock
            FROM 
                products p
            LEFT JOIN 
                inventory i ON p.id = i.product_id
            GROUP BY 
                p.id
            ORDER BY 
                p.name
        """
        products = self.controller.db.fetchall(query)
        
        # Insert into treeview
        for product in products:
            product_id, name, price, stock = product
            self.product_tree.insert("", "end", values=(
                product_id,
                name,
                format_currency(price),
                stock
            ))
    
    def search_products(self):
        """Search products based on search term"""
        search_term = self.search_var.get()
        
        if not search_term:
            # If search is empty, load all products
            self.load_products()
            return
        
        # Clear existing items
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        # Search by name or product code
        query = """
            SELECT 
                p.id,
                p.name,
                p.selling_price,
                COALESCE(SUM(i.quantity), 0) as stock
            FROM 
                products p
            LEFT JOIN 
                inventory i ON p.id = i.product_id
            WHERE 
                p.name LIKE ? OR
                p.product_code LIKE ?
            GROUP BY 
                p.id
            ORDER BY 
                p.name
        """
        search_pattern = f"%{search_term}%"
        products = self.controller.db.fetchall(query, (search_pattern, search_pattern))
        
        # Insert into treeview
        for product in products:
            product_id, name, price, stock = product
            self.product_tree.insert("", "end", values=(
                product_id,
                name,
                format_currency(price),
                stock
            ))
    
    def add_to_cart(self, event=None):
        """Add selected product to cart"""
        selection = self.product_tree.selection()
        if not selection:
            return
        
        # Get product data
        product_values = self.product_tree.item(selection[0], "values")
        product_id = product_values[0]
        product_name = product_values[1]
        product_price = parse_currency(product_values[2])
        stock = int(product_values[3])
        
        # Check if we have stock
        if stock <= 0:
            messagebox.showwarning("No Stock", "This product is out of stock.")
            return
        
        # Get product batches
        batches = self.get_product_batches(product_id)
        
        # Add to cart (default quantity = 1)
        self.add_product_to_cart(product_id, product_name, product_price, 1, 0, batches)
        
        # Update totals
        self.update_totals()
    
    def get_product_batches(self, product_id):
        """Get available batches for product"""
        query = """
            SELECT 
                batch_number,
                quantity,
                expiry_date
            FROM 
                inventory
            WHERE 
                product_id = ? AND
                quantity > 0
            ORDER BY
                expiry_date ASC
        """
        return self.controller.db.fetchall(query, (product_id,))
    
    def add_product_to_cart(self, product_id, product_name, price, quantity, discount=0, batches=None):
        """Add product to cart with specified quantity"""
        # Check if product already exists in cart
        existing_item = None
        existing_item_index = None
        
        for i, item in enumerate(self.cart_items):
            if item["product_id"] == product_id and item["price"] == price and item["discount"] == discount:
                existing_item = item
                existing_item_index = i
                break
        
        if existing_item:
            # Update existing item quantity
            total_stock = sum(batch[1] for batch in batches) if batches else 0
            new_quantity = existing_item["quantity"] + quantity
            
            # Check if we have enough stock
            if total_stock > 0 and new_quantity > total_stock:
                if not messagebox.askyesno("Stock Warning", 
                                         f"Only {total_stock} units available in stock. Continue anyway?",
                                         icon="warning"):
                    return
            
            # Update item in cart_items list
            existing_item["quantity"] = new_quantity
            existing_item["total"] = float(price) * new_quantity * (1 - discount/100)
            self.cart_items[existing_item_index] = existing_item
            
            # Find the treeview item with this product
            for tree_item in self.cart_tree.get_children():
                if int(self.cart_tree.item(tree_item, "values")[0]) == existing_item["id"]:
                    # Update the treeview item
                    self.cart_tree.item(tree_item, values=(
                        existing_item["id"],
                        existing_item["name"],
                        format_currency(existing_item["price"]),
                        existing_item["quantity"],
                        f"{existing_item['discount']}%",
                        format_currency(existing_item["total"])
                    ))
                    break
        else:
            # Calculate total for new item
            item_total = float(price) * quantity * (1 - discount/100)
            
            # Add to cart items list
            item = {
                "id": self.next_item_id,
                "product_id": product_id,
                "name": product_name,
                "price": price,
                "quantity": quantity,
                "discount": discount,
                "total": item_total,
                "batches": batches
            }
            self.cart_items.append(item)
            self.next_item_id += 1
            
            # Add to cart treeview
            self.cart_tree.insert("", "end", values=(
                item["id"],
                item["name"],
                format_currency(item["price"]),
                item["quantity"],
                f"{item['discount']}%",
                format_currency(item["total"])
            ))
    
    def edit_cart_item(self, event=None):
        """Edit selected cart item"""
        selection = self.cart_tree.selection()
        if not selection:
            return
        
        # Get item ID from treeview
        item_id = int(self.cart_tree.item(selection[0], "values")[0])
        
        # Find item in cart_items list
        item = next((item for item in self.cart_items if item["id"] == item_id), None)
        if not item:
            return
        
        # Create edit dialog
        edit_dialog = tk.Toplevel(self)
        edit_dialog.title("Edit Cart Item")
        edit_dialog.geometry("400x300")
        edit_dialog.resizable(False, False)
        edit_dialog.transient(self.master)
        edit_dialog.grab_set()
        
        # Center dialog
        x = self.winfo_x() + (self.winfo_width() // 2) - (400 // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (300 // 2)
        edit_dialog.geometry(f"+{x}+{y}")
        
        # Dialog content
        frame = tk.Frame(edit_dialog, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Product name
        tk.Label(frame, 
               text="Product:",
               font=FONTS["regular_bold"]).grid(row=0, column=0, sticky="w", pady=10)
        
        tk.Label(frame, 
               text=item["name"],
               font=FONTS["regular"]).grid(row=0, column=1, sticky="w", pady=10)
        
        # Price
        tk.Label(frame, 
               text="Price:",
               font=FONTS["regular_bold"]).grid(row=1, column=0, sticky="w", pady=10)
        
        price_var = tk.StringVar(value=format_currency(item["price"]).replace("₹", ""))
        price_entry = tk.Entry(frame, 
                             textvariable=price_var,
                             font=FONTS["regular"],
                             width=15)
        price_entry.grid(row=1, column=1, sticky="w", pady=10)
        
        # Quantity with +/- buttons for quick adjustments
        tk.Label(frame, 
               text="Quantity:",
               font=FONTS["regular_bold"]).grid(row=2, column=0, sticky="w", pady=10)
        
        # Create a frame for quantity controls
        qty_frame = tk.Frame(frame)
        qty_frame.grid(row=2, column=1, sticky="w", pady=10)
        
        # Decrease quantity button
        decrease_btn = tk.Button(qty_frame,
                               text="-",
                               font=FONTS["regular_bold"],
                               width=2,
                               bg=COLORS["bg_secondary"],
                               fg=COLORS["text_primary"],
                               command=lambda: adjust_quantity(-1))
        decrease_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Quantity entry
        qty_var = tk.StringVar(value=str(item["quantity"]))
        qty_entry = tk.Entry(qty_frame, 
                           textvariable=qty_var,
                           font=FONTS["regular"],
                           width=6,
                           justify=tk.CENTER)
        qty_entry.pack(side=tk.LEFT)
        
        # Increase quantity button
        increase_btn = tk.Button(qty_frame,
                               text="+",
                               font=FONTS["regular_bold"],
                               width=2,
                               bg=COLORS["primary"],
                               fg=COLORS["text_white"],
                               command=lambda: adjust_quantity(1))
        increase_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        def adjust_quantity(amount):
            """Adjust quantity by the given amount"""
            try:
                current_qty = int(qty_var.get())
                new_qty = max(1, current_qty + amount)  # Ensure quantity is at least 1
                qty_var.set(str(new_qty))
            except ValueError:
                qty_var.set("1")  # Reset to 1 if invalid value
        
        # Discount
        tk.Label(frame, 
               text="Discount %:",
               font=FONTS["regular_bold"]).grid(row=3, column=0, sticky="w", pady=10)
        
        discount_var = tk.StringVar(value=str(item["discount"]))
        discount_entry = tk.Entry(frame, 
                                textvariable=discount_var,
                                font=FONTS["regular"],
                                width=10)
        discount_entry.grid(row=3, column=1, sticky="w", pady=10)
        
        # Buttons frame
        btn_frame = tk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        # Update button
        update_btn = tk.Button(btn_frame,
                             text="Update",
                             font=FONTS["regular_bold"],
                             bg=COLORS["primary"],
                             fg=COLORS["text_white"],
                             padx=15,
                             pady=5,
                             cursor="hand2",
                             command=lambda: update_item())
        update_btn.pack(side=tk.LEFT, padx=10)
        
        # Cancel button
        cancel_btn = tk.Button(btn_frame,
                             text="Cancel",
                             font=FONTS["regular"],
                             bg=COLORS["bg_secondary"],
                             fg=COLORS["text_primary"],
                             padx=15,
                             pady=5,
                             cursor="hand2",
                             command=edit_dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
        # Remove button
        remove_btn = tk.Button(btn_frame,
                             text="Remove Item",
                             font=FONTS["regular_bold"],
                             bg=COLORS["danger"],
                             fg=COLORS["text_white"],
                             padx=15,
                             pady=5,
                             cursor="hand2",
                             command=lambda: remove_item())
        remove_btn.pack(side=tk.LEFT, padx=10)
        
        def update_item():
            try:
                # Get values from entries
                new_price = parse_currency(price_var.get())
                new_quantity = int(qty_var.get())
                new_discount = float(discount_var.get())
                
                # Validate
                if new_quantity <= 0:
                    messagebox.showerror("Invalid Input", "Quantity must be greater than zero.")
                    return
                
                if new_discount < 0 or new_discount > 100:
                    messagebox.showerror("Invalid Input", "Discount must be between 0 and 100.")
                    return
                
                # Check if we have enough stock
                total_stock = sum(batch[1] for batch in item["batches"]) if item["batches"] else 0
                if new_quantity > total_stock:
                    if not messagebox.askyesno("Stock Warning", 
                                             f"Only {total_stock} units available in stock. Continue anyway?",
                                             icon="warning"):
                        return
                
                # Update item in cart_items list
                item["price"] = new_price
                item["quantity"] = new_quantity
                item["discount"] = new_discount
                item["total"] = float(new_price) * new_quantity * (1 - new_discount/100)
                
                # Update item in treeview
                selection = self.cart_tree.selection()
                if selection:
                    self.cart_tree.item(selection[0], values=(
                        item["id"],
                        item["name"],
                        format_currency(item["price"]),
                        item["quantity"],
                        f"{item['discount']}%",
                        format_currency(item["total"])
                    ))
                
                # Update totals
                self.update_totals()
                
                # Close dialog
                edit_dialog.destroy()
                
            except (ValueError, TypeError) as e:
                messagebox.showerror("Invalid Input", "Please enter valid numbers.")
        
        def remove_item():
            # Remove item from cart_items list
            self.cart_items = [i for i in self.cart_items if i["id"] != item_id]
            
            # Remove item from treeview
            selection = self.cart_tree.selection()
            if selection:
                self.cart_tree.delete(selection[0])
            
            # Update totals
            self.update_totals()
            
            # Close dialog
            edit_dialog.destroy()
    
    def update_totals(self):
        """Update cart totals"""
        # Calculate subtotal
        subtotal = sum(item["total"] for item in self.cart_items)
        
        # Get discount
        try:
            discount_value = float(self.discount_var.get() or 0)
            discount_type = self.discount_type_var.get()
            
            if discount_type == "amount":
                discount = min(discount_value, subtotal)  # Can't discount more than subtotal
            else:  # percentage
                discount_value = min(discount_value, 100)  # Cap at 100%
                discount = subtotal * (discount_value / 100)
        except ValueError:
            discount = 0
        
        # Calculate tax (simplified for now - using a flat 5% tax)
        taxable_amount = subtotal - discount
        tax = taxable_amount * 0.05  # 5% tax
        
        # Calculate total
        total = taxable_amount + tax
        
        # Update labels
        self.subtotal_label.config(text=format_currency(subtotal))
        self.tax_label.config(text=format_currency(tax))
        self.total_label.config(text=format_currency(total))
    
    def cancel_sale(self):
        """Cancel the current sale"""
        if not self.cart_items:
            return
            
        if messagebox.askyesno("Cancel Sale", "Are you sure you want to cancel this sale?"):
            # Clear cart
            self.cart_items = []
            self.next_item_id = 1
            
            # Clear treeview
            for item in self.cart_tree.get_children():
                self.cart_tree.delete(item)
            
            # Reset customer to default
            self.current_customer = {
                "id": 1,  # Default to Walk-in Customer
                "name": "Walk-in Customer",
                "phone": "",
                "address": ""
            }
            self.customer_label.config(text="Walk-in Customer")
            
            # Reset discount
            self.discount_var.set("0.00")
            self.discount_type_var.set("amount")
            
            # Update totals
            self.update_totals()
    
    def suspend_sale(self):
        """Suspend current sale for later retrieval"""
        if not self.cart_items:
            messagebox.showinfo("Suspend Sale", "No items in cart to suspend.")
            return
        
        # Create a unique ID for this suspended sale
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        sale_id = f"S{timestamp}"
        
        # Create suspended sale object
        suspended_sale = {
            "id": sale_id,
            "items": self.cart_items.copy(),
            "customer": self.current_customer.copy(),
            "discount": self.discount_var.get(),
            "discount_type": self.discount_type_var.get(),
            "timestamp": datetime.datetime.now(),
        }
        
        # Add to suspended bills list
        self.suspended_bills.append(suspended_sale)
        
        # Inform user
        messagebox.showinfo("Sale Suspended", 
                          f"Sale has been suspended with ID: {sale_id}\n\n"
                          "You can find it in the Suspended Bills list.")
        
        # Clear current sale
        self.cancel_sale()
    
    def show_suspended_bills(self):
        """Show dialog with suspended bills"""
        if not self.suspended_bills:
            messagebox.showinfo("Suspended Bills", "No suspended bills found.")
            return
        
        # Create dialog
        dialog = tk.Toplevel(self)
        dialog.title("Suspended Bills")
        dialog.geometry("600x400")
        dialog.transient(self.master)
        dialog.grab_set()
        
        # Center dialog
        x = self.winfo_x() + (self.winfo_width() // 2) - (600 // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (400 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Dialog content
        frame = tk.Frame(dialog, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(frame, 
               text="Suspended Bills",
               font=FONTS["subheading"]).pack(anchor="w", pady=(0, 10))
        
        # Treeview frame
        tree_frame = tk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create treeview for suspended bills
        suspended_tree = ttk.Treeview(tree_frame, 
                                    columns=("id", "customer", "items", "value", "time"),
                                    show="headings",
                                    yscrollcommand=scrollbar.set)
        
        # Configure scrollbar
        scrollbar.config(command=suspended_tree.yview)
        
        # Define columns
        suspended_tree.heading("id", text="ID")
        suspended_tree.heading("customer", text="Customer")
        suspended_tree.heading("items", text="Items")
        suspended_tree.heading("value", text="Value")
        suspended_tree.heading("time", text="Time")
        
        # Set column widths
        suspended_tree.column("id", width=70)
        suspended_tree.column("customer", width=150)
        suspended_tree.column("items", width=70)
        suspended_tree.column("value", width=100)
        suspended_tree.column("time", width=150)
        
        suspended_tree.pack(fill=tk.BOTH, expand=True)
        
        # Populate treeview
        for bill in self.suspended_bills:
            # Calculate total items and value
            total_items = sum(item["quantity"] for item in bill["items"])
            total_value = sum(item["total"] for item in bill["items"])
            
            # Apply bill discount
            try:
                discount_value = float(bill["discount"] or 0)
                discount_type = bill["discount_type"]
                
                if discount_type == "amount":
                    discount = min(discount_value, total_value)
                else:  # percentage
                    discount_value = min(discount_value, 100)
                    discount = total_value * (discount_value / 100)
                    
                total_value -= discount
            except (ValueError, KeyError):
                pass
            
            # Add tax (simplified - 5%)
            total_value *= 1.05
            
            # Format time
            time_str = bill["timestamp"].strftime("%Y-%m-%d %H:%M")
            
            suspended_tree.insert("", "end", values=(
                bill["id"],
                bill["customer"]["name"],
                total_items,
                format_currency(total_value),
                time_str
            ))
        
        # Buttons frame
        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        # Recall button
        recall_btn = tk.Button(btn_frame,
                             text="Recall Selected",
                             font=FONTS["regular_bold"],
                             bg=COLORS["primary"],
                             fg=COLORS["text_white"],
                             padx=15,
                             pady=5,
                             cursor="hand2",
                             command=lambda: recall_sale())
        recall_btn.pack(side=tk.LEFT, padx=10)
        
        # Delete button
        delete_btn = tk.Button(btn_frame,
                             text="Delete Selected",
                             font=FONTS["regular_bold"],
                             bg=COLORS["danger"],
                             fg=COLORS["text_white"],
                             padx=15,
                             pady=5,
                             cursor="hand2",
                             command=lambda: delete_sale())
        delete_btn.pack(side=tk.LEFT, padx=10)
        
        # Close button
        close_btn = tk.Button(btn_frame,
                            text="Close",
                            font=FONTS["regular"],
                            bg=COLORS["bg_secondary"],
                            fg=COLORS["text_primary"],
                            padx=15,
                            pady=5,
                            cursor="hand2",
                            command=dialog.destroy)
        close_btn.pack(side=tk.RIGHT, padx=10)
        
        def recall_sale():
            selection = suspended_tree.selection()
            if not selection:
                messagebox.showinfo("Select Sale", "Please select a sale to recall.")
                return
            
            # Check if current cart has items
            if self.cart_items:
                if not messagebox.askyesno("Replace Cart", 
                                         "Current cart has items. Replace with suspended sale?"):
                    return
            
            # Get selected sale ID
            sale_id = suspended_tree.item(selection[0], "values")[0]
            
            # Find sale in suspended bills
            sale = next((s for s in self.suspended_bills if s["id"] == sale_id), None)
            if not sale:
                messagebox.showerror("Error", "Selected sale not found.")
                return
            
            # Restore sale
            self.cart_items = sale["items"].copy()
            self.next_item_id = max(item["id"] for item in self.cart_items) + 1
            self.current_customer = sale["customer"].copy()
            self.customer_label.config(text=sale["customer"]["name"])
            self.discount_var.set(sale["discount"])
            self.discount_type_var.set(sale["discount_type"])
            
            # Populate cart treeview
            for item in self.cart_tree.get_children():
                self.cart_tree.delete(item)
                
            for item in self.cart_items:
                self.cart_tree.insert("", "end", values=(
                    item["id"],
                    item["name"],
                    format_currency(item["price"]),
                    item["quantity"],
                    f"{item['discount']}%",
                    format_currency(item["total"])
                ))
            
            # Update totals
            self.update_totals()
            
            # Remove from suspended bills
            self.suspended_bills = [s for s in self.suspended_bills if s["id"] != sale_id]
            
            # Close dialog
            dialog.destroy()
        
        def delete_sale():
            selection = suspended_tree.selection()
            if not selection:
                messagebox.showinfo("Select Sale", "Please select a sale to delete.")
                return
            
            if not messagebox.askyesno("Delete Sale", 
                                     "Are you sure you want to delete this suspended sale?"):
                return
            
            # Get selected sale ID
            sale_id = suspended_tree.item(selection[0], "values")[0]
            
            # Remove from suspended bills
            self.suspended_bills = [s for s in self.suspended_bills if s["id"] != sale_id]
            
            # Remove from treeview
            suspended_tree.delete(selection[0])
    
    def quick_add_product(self):
        """Quick add a new product from sales screen"""
        # Create dialog
        dialog = tk.Toplevel(self)
        dialog.title("Quick Add Product")
        dialog.geometry("450x450")
        dialog.transient(self.master)
        dialog.grab_set()
        
        # Center dialog
        x = self.winfo_x() + (self.winfo_width() // 2) - (450 // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (450 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Dialog content
        frame = tk.Frame(dialog, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(frame, 
               text="Add New Product",
               font=FONTS["subheading"]).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))
        
        # Get categories and vendors from the database
        # Get categories
        categories = []
        query = "SELECT value FROM settings WHERE key = 'product_categories'"
        result = self.controller.db.fetchone(query)
        if result and result[0]:
            categories = result[0].split(',')
        if not categories:
            categories = ["Fertilizers", "Pesticides", "Seeds", "Equipment", "Other"]
        
        # Get vendors
        vendors = []
        query = "SELECT value FROM settings WHERE key = 'vendors'"
        result = self.controller.db.fetchone(query)
        if result and result[0]:
            vendors = result[0].split(',')
        
        # Also get unique vendors from products table
        query = "SELECT DISTINCT vendor FROM products WHERE vendor IS NOT NULL AND vendor != ''"
        results = self.controller.db.fetchall(query)
        for vendor in results:
            if vendor[0] and vendor[0] not in vendors:
                vendors.append(vendor[0])
        
        # Form fields with type information
        fields = [
            {"name": "name", "label": "Product Name:", "required": True, "type": "entry"},
            {"name": "vendor", "label": "Vendor/Brand:", "type": "combobox", "values": vendors},
            {"name": "product_code", "label": "Product Code:", "type": "entry"},
            {"name": "category", "label": "Category:", "type": "combobox", "values": categories},
            {"name": "wholesale_price", "label": "Wholesale Price:", "required": True, "type": "entry"},
            {"name": "selling_price", "label": "Selling Price:", "required": True, "type": "entry"},
            {"name": "quantity", "label": "Initial Quantity:", "required": True, "type": "entry"}
        ]
        
        # Variables to store entry values
        form_vars = {}
        entries = {}
        
        # Create labels and entries
        for i, field in enumerate(fields):
            # Label
            req_mark = "*" if field.get("required", False) else ""
            tk.Label(frame, 
                   text=f"{field['label']}{req_mark}",
                   font=FONTS["regular_bold"]).grid(row=i+1, column=0, sticky="w", pady=10)
            
            # Variable
            var = tk.StringVar()
            form_vars[field["name"]] = var
            
            # Different types of input fields
            if field.get("type") == "combobox":
                # Create combobox with values
                entry = ttk.Combobox(frame, 
                                  textvariable=var,
                                  font=FONTS["regular"],
                                  width=25,
                                  values=field["values"])
                
                # Add an option to create a new value
                values = list(field["values"])
                if "Add new..." not in values:
                    values.append("Add new...")
                entry["values"] = values
                
                # Bind selection event
                entry.bind("<<ComboboxSelected>>", 
                           lambda event, f=field["name"]: self.handle_combobox_selection(event, f, form_vars, entries))
            else:
                # Create regular entry
                entry = tk.Entry(frame, 
                               textvariable=var,
                               font=FONTS["regular"],
                               width=25)
            
            entries[field["name"]] = entry
            entry.grid(row=i+1, column=1, sticky="w", pady=10)
        
        # Required fields note
        tk.Label(frame, 
               text="* Required fields",
               font=FONTS["small_italic"]).grid(row=len(fields)+1, column=0, columnspan=2, sticky="w", pady=(10, 20))
        
        # Buttons frame
        btn_frame = tk.Frame(frame)
        btn_frame.grid(row=len(fields)+2, column=0, columnspan=2)
        
        # Save button
        save_btn = tk.Button(btn_frame,
                           text="Save & Add to Cart",
                           font=FONTS["regular_bold"],
                           bg=COLORS["primary"],
                           fg=COLORS["text_white"],
                           padx=15,
                           pady=5,
                           cursor="hand2",
                           command=lambda: save_product())
        save_btn.pack(side=tk.LEFT, padx=10)
        
        # Cancel button
        cancel_btn = tk.Button(btn_frame,
                             text="Cancel",
                             font=FONTS["regular"],
                             bg=COLORS["bg_secondary"],
                             fg=COLORS["text_primary"],
                             padx=15,
                             pady=5,
                             cursor="hand2",
                             command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
        def save_product():
            # Validate required fields
            for field in fields:
                if field.get("required", False) and not form_vars[field["name"]].get().strip():
                    messagebox.showerror("Required Field", f"{field['label']} is required.")
                    return
            
            try:
                # Parse numeric values
                wholesale_price = parse_currency(form_vars["wholesale_price"].get())
                selling_price = parse_currency(form_vars["selling_price"].get())
                quantity = int(form_vars["quantity"].get())
                
                # Validate
                if wholesale_price <= 0:
                    messagebox.showerror("Invalid Input", "Wholesale price must be greater than zero.")
                    return
                
                if selling_price <= 0:
                    messagebox.showerror("Invalid Input", "Selling price must be greater than zero.")
                    return
                
                if quantity < 0:
                    messagebox.showerror("Invalid Input", "Quantity cannot be negative.")
                    return
                
                # Create product data
                product_data = {
                    "name": form_vars["name"].get().strip(),
                    "vendor": form_vars["vendor"].get().strip(),
                    "product_code": form_vars["product_code"].get().strip(),
                    "category": form_vars["category"].get().strip(),
                    "wholesale_price": float(wholesale_price),
                    "selling_price": float(selling_price),
                    "tax_percentage": 0  # Default tax percentage
                }
                
                # Insert product into database
                product_id = self.controller.db.insert("products", product_data)
                
                if not product_id:
                    messagebox.showerror("Database Error", "Failed to add product.")
                    return
                
                # Add inventory if quantity > 0
                if quantity > 0:
                    inventory_data = {
                        "product_id": product_id,
                        "batch_number": "INIT",
                        "quantity": quantity,
                        "purchase_date": datetime.date.today().strftime("%Y-%m-%d")
                    }
                    
                    self.controller.db.insert("inventory", inventory_data)
                    
                    # Add inventory transaction
                    transaction_data = {
                        "product_id": product_id,
                        "batch_number": "INIT",
                        "quantity": quantity,
                        "transaction_type": "PURCHASE",
                        "notes": "Initial stock"
                    }
                    
                    self.controller.db.insert("inventory_transactions", transaction_data)
                
                # Get batches for the new product
                batches = [(None, quantity, None)] if quantity > 0 else []
                
                # Add to cart
                self.add_product_to_cart(
                    product_id, 
                    product_data["name"], 
                    product_data["selling_price"], 
                    1,  # Default quantity
                    0,  # No discount 
                    batches
                )
                
                # Update totals
                self.update_totals()
                
                # Reload products list
                self.load_products()
                
                # Close dialog
                dialog.destroy()
                
                # Confirm to user
                messagebox.showinfo("Product Added", 
                                  f"Product '{product_data['name']}' has been added and placed in cart.")
                
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter valid numbers for prices and quantity.")
    
    def change_customer(self, add_new=False):
        """Change customer for current sale
        If add_new is True, directly open the add new customer dialog"""
        def load_customers():
            # Clear existing items
            for item in customer_tree.get_children():
                customer_tree.delete(item)
            
            # Get all customers
            query = "SELECT id, name, phone, address FROM customers ORDER BY name"
            customers = self.controller.db.fetchall(query)
            
            # Insert into treeview
            for customer in customers:
                customer_id, name, phone, address = customer
                customer_tree.insert("", "end", values=(
                    customer_id,
                    name,
                    phone or "",
                    address or ""
                ))
        
        def search_customers():
            search_term = search_var.get()
            
            if not search_term:
                # If search is empty, load all customers
                load_customers()
                return
            
            # Clear existing items
            for item in customer_tree.get_children():
                customer_tree.delete(item)
            
            # Search by name or phone
            query = """
                SELECT id, name, phone, address 
                FROM customers 
                WHERE name LIKE ? OR phone LIKE ?
                ORDER BY name
            """
            search_pattern = f"%{search_term}%"
            customers = self.controller.db.fetchall(query, (search_pattern, search_pattern))
            
            # Insert into treeview
            for customer in customers:
                customer_id, name, phone, address = customer
                customer_tree.insert("", "end", values=(
                    customer_id,
                    name,
                    phone or "",
                    address or ""
                ))
        
        def add_new_customer():
            # Create dialog
            customer_dialog = tk.Toplevel(dialog)
            customer_dialog.title("Add New Customer")
            customer_dialog.geometry("400x300")
            customer_dialog.transient(dialog)
            customer_dialog.grab_set()
            
            # Center dialog
            x = dialog.winfo_x() + (dialog.winfo_width() // 2) - (400 // 2)
            y = dialog.winfo_y() + (dialog.winfo_height() // 2) - (300 // 2)
            customer_dialog.geometry(f"+{x}+{y}")
            
            # Dialog content
            cust_frame = tk.Frame(customer_dialog, padx=20, pady=20)
            cust_frame.pack(fill=tk.BOTH, expand=True)
            
            # Title
            tk.Label(cust_frame, 
                   text="Add New Customer",
                   font=FONTS["subheading"]).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))
            
            # Form fields
            fields = [
                {"name": "name", "label": "Customer Name:", "required": True},
                {"name": "phone", "label": "Phone Number:"},
                {"name": "address", "label": "Address:"}
            ]
            
            # Variables to store entry values
            customer_vars = {}
            
            # Create labels and entries
            for i, field in enumerate(fields):
                # Label
                req_mark = "*" if field.get("required", False) else ""
                tk.Label(cust_frame, 
                       text=f"{field['label']}{req_mark}",
                       font=FONTS["regular_bold"]).grid(row=i+1, column=0, sticky="w", pady=10)
                
                # Entry
                var = tk.StringVar()
                customer_vars[field["name"]] = var
                
                if field["name"] == "address":
                    # Multiline text for address
                    entry = tk.Text(cust_frame, 
                                  font=FONTS["regular"],
                                  width=25,
                                  height=3)
                    entry.grid(row=i+1, column=1, sticky="w", pady=10)
                    
                    # Store the text widget instead of StringVar
                    customer_vars[field["name"]] = entry
                else:
                    entry = tk.Entry(cust_frame, 
                                   textvariable=var,
                                   font=FONTS["regular"],
                                   width=25)
                    entry.grid(row=i+1, column=1, sticky="w", pady=10)
            
            # Required fields note
            tk.Label(cust_frame, 
                   text="* Required fields",
                   font=FONTS["small_italic"]).grid(row=len(fields)+1, column=0, columnspan=2, sticky="w", pady=(10, 20))
            
            # Buttons frame
            cust_btn_frame = tk.Frame(cust_frame)
            cust_btn_frame.grid(row=len(fields)+2, column=0, columnspan=2)
            
            # Save button
            save_btn = tk.Button(cust_btn_frame,
                               text="Save Customer",
                               font=FONTS["regular_bold"],
                               bg=COLORS["primary"],
                               fg=COLORS["text_white"],
                               padx=15,
                               pady=5,
                               cursor="hand2",
                               command=lambda: save_customer())
            save_btn.pack(side=tk.LEFT, padx=10)
            
            # Cancel button
            cancel_btn = tk.Button(cust_btn_frame,
                                 text="Cancel",
                                 font=FONTS["regular"],
                                 bg=COLORS["bg_secondary"],
                                 fg=COLORS["text_primary"],
                                 padx=15,
                                 pady=5,
                                 cursor="hand2",
                                 command=customer_dialog.destroy)
            cancel_btn.pack(side=tk.LEFT, padx=10)
            
            def save_customer():
                # Validate required fields
                if not customer_vars["name"].get().strip():
                    messagebox.showerror("Required Field", "Customer Name is required.")
                    return
                
                # Get address from text widget
                address_text = customer_vars["address"].get("1.0", tk.END).strip()
                
                # Create customer data
                customer_data = {
                    "name": customer_vars["name"].get().strip(),
                    "phone": customer_vars["phone"].get().strip(),
                    "address": address_text
                }
                
                # Insert customer into database
                customer_id = self.controller.db.insert("customers", customer_data)
                
                if not customer_id:
                    messagebox.showerror("Database Error", "Failed to add customer.")
                    return
                
                # Close dialog
                customer_dialog.destroy()
                
                # Reload customers and select the new one
                load_customers()
                
                # Find and select the new customer
                for item in customer_tree.get_children():
                    if int(customer_tree.item(item, "values")[0]) == customer_id:
                        customer_tree.selection_set(item)
                        customer_tree.see(item)
                        break
        
        def select_customer():
            selection = customer_tree.selection()
            if not selection:
                messagebox.showinfo("Select Customer", "Please select a customer.")
                return
            
            # Get customer data from treeview
            customer_values = customer_tree.item(selection[0], "values")
            customer_id = int(customer_values[0])
            customer_name = customer_values[1]
            customer_phone = customer_values[2]
            customer_address = customer_values[3]
            
            # Update current customer
            self.current_customer = {
                "id": customer_id,
                "name": customer_name,
                "phone": customer_phone,
                "address": customer_address
            }
            
            # Update customer label
            self.customer_label.config(text=customer_name)
            
            # Close dialog
            dialog.destroy()
        
        def set_default_customer():
            # Set default (Walk-in) customer
            self.current_customer = {
                "id": 1,  # Default to Walk-in Customer
                "name": "Walk-in Customer",
                "phone": "",
                "address": ""
            }
            
            # Update customer label
            self.customer_label.config(text="Walk-in Customer")
            
            # Close dialog
            dialog.destroy()
        
        # Create dialog
        dialog = tk.Toplevel(self)
        dialog.title("Select Customer")
        dialog.geometry("600x500")
        dialog.transient(self.master)
        dialog.grab_set()
        
        # Center dialog
        x = self.winfo_x() + (self.winfo_width() // 2) - (600 // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (500 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Dialog content
        frame = tk.Frame(dialog, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(frame, 
               text="Select Customer",
               font=FONTS["subheading"]).pack(anchor="w", pady=(0, 10))
        
        # Search frame
        search_frame = tk.Frame(frame)
        search_frame.pack(fill=tk.X, pady=10)
        
        # Search entry
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, 
                              textvariable=search_var,
                              font=FONTS["regular"],
                              width=30)
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        search_entry.bind("<Return>", lambda event: search_customers())
        
        # Search button
        search_btn = tk.Button(search_frame,
                             text="Search",
                             font=FONTS["regular"],
                             bg=COLORS["primary"],
                             fg=COLORS["text_white"],
                             padx=10,
                             pady=5,
                             cursor="hand2",
                             command=lambda: search_customers())
        search_btn.pack(side=tk.LEFT)
        
        # Add new customer button
        add_customer_btn = tk.Button(search_frame,
                                   text="Add New",
                                   font=FONTS["regular"],
                                   bg=COLORS["secondary"],
                                   fg=COLORS["text_white"],
                                   padx=10,
                                   pady=5,
                                   cursor="hand2",
                                   command=lambda: add_new_customer())
        add_customer_btn.pack(side=tk.RIGHT)
        
        # Treeview frame
        tree_frame = tk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create treeview for customers
        customer_tree = ttk.Treeview(tree_frame, 
                                   columns=("id", "name", "phone", "address"),
                                   show="headings",
                                   yscrollcommand=scrollbar.set)
        
        # Configure scrollbar
        scrollbar.config(command=customer_tree.yview)
        
        # Define columns
        customer_tree.heading("id", text="ID")
        customer_tree.heading("name", text="Name")
        customer_tree.heading("phone", text="Phone")
        customer_tree.heading("address", text="Address")
        
        # Set column widths
        customer_tree.column("id", width=50)
        customer_tree.column("name", width=150)
        customer_tree.column("phone", width=120)
        customer_tree.column("address", width=230)
        
        customer_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind double-click to select
        customer_tree.bind("<Double-1>", lambda event: select_customer())
        
        # Buttons frame
        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        # Select button
        select_btn = tk.Button(btn_frame,
                             text="Select Customer",
                             font=FONTS["regular_bold"],
                             bg=COLORS["primary"],
                             fg=COLORS["text_white"],
                             padx=15,
                             pady=5,
                             cursor="hand2",
                             command=lambda: select_customer())
        select_btn.pack(side=tk.LEFT, padx=10)
        
        # Default customer button
        default_btn = tk.Button(btn_frame,
                              text="Walk-in Customer",
                              font=FONTS["regular"],
                              bg=COLORS["bg_secondary"],
                              fg=COLORS["text_primary"],
                              padx=15,
                              pady=5,
                              cursor="hand2",
                              command=lambda: set_default_customer())
        default_btn.pack(side=tk.LEFT, padx=10)
        
        # Cancel button
        cancel_btn = tk.Button(btn_frame,
                             text="Cancel",
                             font=FONTS["regular"],
                             bg=COLORS["bg_secondary"],
                             fg=COLORS["text_primary"],
                             padx=15,
                             pady=5,
                             cursor="hand2",
                             command=dialog.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=10)
        
        # Load customers initially
        load_customers()
        
        # If add_new is True, directly open the add customer dialog
        if add_new:
            # Use after to ensure dialog is fully created first
            dialog.after(100, add_new_customer)
    
    def process_payment(self, payment_method):
        """Process payment and finalize sale"""
        if not self.cart_items:
            messagebox.showinfo("Empty Cart", "No items in cart to process.")
            return
        
        # Calculate totals
        subtotal = sum(item["total"] for item in self.cart_items)
        
        # Get discount
        try:
            discount_value = float(self.discount_var.get() or 0)
            discount_type = self.discount_type_var.get()
            
            if discount_type == "amount":
                discount = min(discount_value, subtotal)
            else:  # percentage
                discount_value = min(discount_value, 100)
                discount = subtotal * (discount_value / 100)
        except ValueError:
            discount = 0
        
        # Calculate tax (simplified - 5%)
        taxable_amount = subtotal - discount
        tax = taxable_amount * 0.05  # 5% tax
        
        # Calculate total
        total = taxable_amount + tax
        
        # Different payment processes based on method
        if payment_method == "CASH":
            # Show amount tendered dialog
            amount_tendered = simpledialog.askfloat("Cash Payment", 
                                                  f"Total: {format_currency(total)}\n\nAmount Tendered:",
                                                  minvalue=total,
                                                  initialvalue=total)
            
            if amount_tendered is None:
                return  # User cancelled
            
            # Calculate change
            change = amount_tendered - total
            
            # Show confirmation with change
            if not messagebox.askyesno("Confirm Payment", 
                                     f"Amount Tendered: {format_currency(amount_tendered)}\n"
                                     f"Total: {format_currency(total)}\n"
                                     f"Change: {format_currency(change)}\n\n"
                                     "Complete sale?"):
                return
            
            # Complete sale with cash payment
            self.complete_sale(payment_method, total, 0, 0, total, None)
            
            # Show receipt with change
            messagebox.showinfo("Sale Complete", 
                              f"Sale completed successfully!\n\n"
                              f"Amount Tendered: {format_currency(amount_tendered)}\n"
                              f"Change: {format_currency(change)}")
            
        elif payment_method == "UPI":
            # Create UPI reference dialog
            upi_dialog = tk.Toplevel(self)
            upi_dialog.title("UPI Payment")
            upi_dialog.geometry("400x200")
            upi_dialog.transient(self.master)
            upi_dialog.grab_set()
            
            # Center dialog
            x = self.winfo_x() + (self.winfo_width() // 2) - (400 // 2)
            y = self.winfo_y() + (self.winfo_height() // 2) - (200 // 2)
            upi_dialog.geometry(f"+{x}+{y}")
            
            # Dialog content
            frame = tk.Frame(upi_dialog, padx=20, pady=20)
            frame.pack(fill=tk.BOTH, expand=True)
            
            # Title
            tk.Label(frame, 
                   text="UPI Payment",
                   font=FONTS["subheading"]).pack(anchor="w", pady=(0, 10))
            
            # Amount
            tk.Label(frame, 
                   text=f"Amount: {format_currency(total)}",
                   font=FONTS["regular_bold"]).pack(anchor="w", pady=(0, 15))
            
            # Reference ID
            reference_frame = tk.Frame(frame)
            reference_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(reference_frame, 
                   text="UPI Transaction Reference:",
                   font=FONTS["regular"]).pack(side=tk.LEFT, padx=(0, 10))
            
            upi_reference_var = tk.StringVar()
            reference_entry = tk.Entry(reference_frame, 
                                     textvariable=upi_reference_var,
                                     font=FONTS["regular"],
                                     width=20)
            reference_entry.pack(side=tk.LEFT)
            reference_entry.focus_set()  # Focus on entry
            
            # Buttons frame
            btn_frame = tk.Frame(frame, pady=15)
            btn_frame.pack(fill=tk.X)
            
            # Cancel button
            cancel_btn = tk.Button(btn_frame,
                                 text="Cancel",
                                 font=FONTS["regular"],
                                 bg=COLORS["bg_secondary"],
                                 fg=COLORS["text_primary"],
                                 padx=15,
                                 pady=5,
                                 cursor="hand2",
                                 command=upi_dialog.destroy)
            cancel_btn.pack(side=tk.LEFT, padx=5)
            
            # Proceed button
            proceed_btn = tk.Button(btn_frame,
                                  text="Proceed",
                                  font=FONTS["regular_bold"],
                                  bg=COLORS["primary"],
                                  fg=COLORS["text_white"],
                                  padx=15,
                                  pady=5,
                                  cursor="hand2",
                                  command=lambda: process_upi())
            proceed_btn.pack(side=tk.RIGHT, padx=5)
            
            # Skip button
            skip_btn = tk.Button(btn_frame,
                               text="Skip Reference",
                               font=FONTS["regular"],
                               bg=COLORS["secondary"],
                               fg=COLORS["text_white"],
                               padx=15,
                               pady=5,
                               cursor="hand2",
                               command=lambda: process_upi(skip=True))
            skip_btn.pack(side=tk.RIGHT, padx=5)
            
            def process_upi(skip=False):
                upi_reference = None if skip else upi_reference_var.get().strip()
                
                # Confirm payment
                confirmation_text = f"Total: {format_currency(total)}\n"
                if upi_reference:
                    confirmation_text += f"UPI Reference: {upi_reference}\n\n"
                else:
                    confirmation_text += "No UPI Reference provided.\n\n"
                    
                confirmation_text += "Confirm UPI payment received and complete sale?"
                
                # Close the reference dialog
                upi_dialog.destroy()
                
                if not messagebox.askyesno("Confirm UPI Payment", confirmation_text):
                    return
                
                # Complete sale with UPI payment
                self.complete_sale(payment_method, 0, total, 0, total, upi_reference)
                
                # Show receipt
                receipt_text = f"Sale completed successfully!\n\nPayment Method: UPI\nAmount: {format_currency(total)}"
                if upi_reference:
                    receipt_text += f"\nUPI Reference: {upi_reference}"
                else:
                    receipt_text += "\nNo UPI Reference provided"
                    
                messagebox.showinfo("Sale Complete", receipt_text)
            
        elif payment_method == "SPLIT":
            # Create split payment dialog
            self.show_split_payment_dialog(total)
            
        elif payment_method == "CREDIT":
            # Check if customer is Walk-in
            if self.current_customer["id"] == 1:
                if not messagebox.askyesno("Credit Sale", 
                                         "Credit sale requires a specific customer. Do you want to select a customer?"):
                    return
                
                # Show customer selection
                self.change_customer()
                
                # Check again if customer is still Walk-in
                if self.current_customer["id"] == 1:
                    messagebox.showinfo("Credit Sale", "Credit sale cancelled. No customer selected.")
                    return
            
            # Show confirmation
            if not messagebox.askyesno("Confirm Credit Sale", 
                                     f"Total: {format_currency(total)}\n\n"
                                     f"Customer: {self.current_customer['name']}\n\n"
                                     "This will be recorded as credit/due payment. Continue?"):
                return
            
            # Complete sale with credit
            self.complete_sale(payment_method, 0, 0, total, total, None)
            
            # Show receipt
            messagebox.showinfo("Sale Complete", 
                              f"Sale completed as credit for {self.current_customer['name']}!\n\n"
                              f"Amount: {format_currency(total)}\n\n"
                              "This has been added to the customer's credit balance.")
    
    def show_split_payment_dialog(self, total):
        """Show dialog for split payment"""
        # Create dialog
        dialog = tk.Toplevel(self)
        dialog.title("Split Payment")
        dialog.geometry("400x300")
        dialog.transient(self.master)
        dialog.grab_set()
        
        # Center dialog
        x = self.winfo_x() + (self.winfo_width() // 2) - (400 // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (300 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Dialog content
        frame = tk.Frame(dialog, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(frame, 
               text="Split Payment",
               font=FONTS["subheading"]).pack(anchor="w", pady=(0, 20))
        
        # Total amount
        tk.Label(frame, 
               text=f"Total Amount: {format_currency(total)}",
               font=FONTS["regular_bold"]).pack(anchor="w", pady=5)
        
        # Cash amount
        tk.Label(frame, 
               text="Cash Amount:",
               font=FONTS["regular"]).pack(anchor="w", pady=(10, 5))
        
        cash_var = tk.StringVar(value="0.00")
        cash_entry = tk.Entry(frame, 
                            textvariable=cash_var,
                            font=FONTS["regular"],
                            width=15)
        cash_entry.pack(anchor="w")
        
        # UPI amount
        tk.Label(frame, 
               text="UPI Amount:",
               font=FONTS["regular"]).pack(anchor="w", pady=(10, 5))
        
        upi_var = tk.StringVar(value="0.00")
        upi_entry = tk.Entry(frame, 
                           textvariable=upi_var,
                           font=FONTS["regular"],
                           width=15)
        upi_entry.pack(anchor="w")

        # UPI reference
        tk.Label(frame,
               text="UPI Reference:",
               font=FONTS["regular"]).pack(anchor="w", pady=(10, 5))
        
        upi_reference_var = tk.StringVar()
        upi_reference_entry = tk.Entry(frame,
                                    textvariable=upi_reference_var,
                                    font=FONTS["regular"],
                                    width=15)
        upi_reference_entry.pack(anchor="w")
        
        # Credit amount
        if self.current_customer["id"] != 1:  # Not Walk-in
            tk.Label(frame, 
                   text="Credit Amount:",
                   font=FONTS["regular"]).pack(anchor="w", pady=(10, 5))
            
            credit_var = tk.StringVar(value="0.00")
            credit_entry = tk.Entry(frame, 
                                  textvariable=credit_var,
                                  font=FONTS["regular"],
                                  width=15)
            credit_entry.pack(anchor="w")
        else:
            credit_var = tk.StringVar(value="0.00")
        
        # Total entered - dynamically update
        total_entered_var = tk.StringVar(value=format_currency(0))
        
        tk.Label(frame, 
               text="Total Entered:",
               font=FONTS["regular_bold"]).pack(anchor="w", pady=(20, 5))
        
        total_entered_label = tk.Label(frame, 
                                     textvariable=total_entered_var,
                                     font=FONTS["regular_bold"],
                                     fg=COLORS["primary"])
        total_entered_label.pack(anchor="w")
        
        # Update total function
        def update_total_entered(*args):
            try:
                cash_amount = parse_currency(cash_var.get())
                upi_amount = parse_currency(upi_var.get())
                credit_amount = parse_currency(credit_var.get())
                
                total_entered = cash_amount + upi_amount + credit_amount
                
                # Update color based on match
                if abs(total_entered - total) < 0.01:  # Allow small rounding differences
                    total_entered_label.config(fg=COLORS["success"])
                else:
                    total_entered_label.config(fg=COLORS["primary"] if total_entered < total else COLORS["danger"])
                
                total_entered_var.set(format_currency(total_entered))
            except:
                total_entered_var.set(format_currency(0))
        
        # Bind update to entry changes
        cash_var.trace_add("write", update_total_entered)
        upi_var.trace_add("write", update_total_entered)
        credit_var.trace_add("write", update_total_entered)
        
        # Set initial values to match total
        upi_var.set(format_currency(total).replace("₹", ""))
        update_total_entered()
        
        # Buttons frame
        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Process button
        process_btn = tk.Button(btn_frame,
                              text="Process Payment",
                              font=FONTS["regular_bold"],
                              bg=COLORS["primary"],
                              fg=COLORS["text_white"],
                              padx=15,
                              pady=5,
                              cursor="hand2",
                              command=lambda: process_split())
        process_btn.pack(side=tk.LEFT, padx=10)
        
        # Cancel button
        cancel_btn = tk.Button(btn_frame,
                             text="Cancel",
                             font=FONTS["regular"],
                             bg=COLORS["bg_secondary"],
                             fg=COLORS["text_primary"],
                             padx=15,
                             pady=5,
                             cursor="hand2",
                             command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
        def process_split():
            try:
                cash_amount = parse_currency(cash_var.get())
                upi_amount = parse_currency(upi_var.get())
                credit_amount = parse_currency(credit_var.get())
                upi_reference = upi_reference_var.get().strip() if upi_amount > 0 else None
                
                total_entered = cash_amount + upi_amount + credit_amount
                
                # Validate
                if total_entered < total - 0.01:  # Allow small rounding differences
                    messagebox.showerror("Payment Error", 
                                       f"Total entered ({format_currency(total_entered)}) "
                                       f"is less than required amount ({format_currency(total)}).")
                    return
                
                # Check credit amount for Walk-in customer
                if self.current_customer["id"] == 1 and credit_amount > 0:
                    messagebox.showerror("Credit Error", 
                                       "Cannot apply credit to Walk-in Customer. Please select a specific customer.")
                    return
                
                # Adjust for any overpayment
                if total_entered > total:
                    # Adjust cash amount (assuming any excess is in cash)
                    cash_amount -= (total_entered - total)
                
                # Build confirmation message
                confirmation_text = f"Cash: {format_currency(cash_amount)}\n"
                confirmation_text += f"UPI: {format_currency(upi_amount)}\n"
                if upi_amount > 0 and upi_reference:
                    confirmation_text += f"UPI Reference: {upi_reference}\n"
                confirmation_text += f"Credit: {format_currency(credit_amount)}\n\n"
                confirmation_text += f"Total: {format_currency(total)}\n\n"
                confirmation_text += "Complete sale with split payment?"
                
                # Show confirmation
                if not messagebox.askyesno("Confirm Split Payment", confirmation_text):
                    return
                
                # Close dialog
                dialog.destroy()
                
                # Complete sale with split payment
                self.complete_sale("SPLIT", cash_amount, upi_amount, credit_amount, total, upi_reference)
                
                # Build receipt message
                receipt_text = f"Sale completed successfully!\n\n"
                receipt_text += f"Cash: {format_currency(cash_amount)}\n"
                receipt_text += f"UPI: {format_currency(upi_amount)}\n"
                if upi_amount > 0 and upi_reference:
                    receipt_text += f"UPI Reference: {upi_reference}\n"
                receipt_text += f"Credit: {format_currency(credit_amount)}\n\n"
                receipt_text += f"Total: {format_currency(total)}"
                
                # Show receipt
                messagebox.showinfo("Sale Complete", receipt_text)
                
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter valid amounts.")
    
    def complete_sale(self, payment_method, cash_amount, upi_amount, credit_amount, total_amount, upi_reference=None):
        """Complete the sale and save to database"""
        # Calculate totals
        subtotal = sum(item["total"] for item in self.cart_items)
        
        # Get discount
        try:
            discount_value = float(self.discount_var.get() or 0)
            discount_type = self.discount_type_var.get()
            
            if discount_type == "amount":
                discount = min(discount_value, subtotal)
            else:  # percentage
                discount_value = min(discount_value, 100)
                discount = subtotal * (discount_value / 100)
        except ValueError:
            discount = 0
        
        # Calculate tax (simplified - 5%)
        taxable_amount = subtotal - discount
        tax = taxable_amount * 0.05  # 5% tax
        
        # Generate auto-incrementing invoice number
        prefix = self.controller.config.get("invoice_prefix", "AGT")
        
        # Get the last invoice number from the database
        query = "SELECT invoice_number FROM invoices ORDER BY id DESC LIMIT 1"
        last_invoice = self.controller.db.fetchone(query)
        
        # Extract the numeric part if it exists, otherwise start from 0
        last_number = 0
        if last_invoice and last_invoice[0]:
            # Try to extract the numeric part
            try:
                # If format is like "AGT0001", extract the numeric part
                numeric_part = ''.join(filter(str.isdigit, last_invoice[0]))
                if numeric_part:
                    last_number = int(numeric_part)
            except (ValueError, TypeError):
                last_number = 0
        
        # Generate new invoice number with incrementing number
        new_number = last_number + 1
        date_part = datetime.datetime.now().strftime("%Y%m")
        invoice_number = f"{prefix}{date_part}{new_number:04d}"
        
        # Payment status (PAID or DUE)
        payment_status = "DUE" if payment_method == "CREDIT" else "PAID"
        
        # Convert Decimal values to float to avoid database errors
        def decimal_to_float(value):
            """Convert Decimal to float if needed"""
            if isinstance(value, decimal.Decimal):
                return float(value)
            return value

        # Create invoice data
        invoice_data = {
            "invoice_number": invoice_number,
            "customer_id": self.current_customer["id"],
            "subtotal": decimal_to_float(subtotal),
            "discount_amount": decimal_to_float(discount),
            "tax_amount": decimal_to_float(tax),
            "total_amount": decimal_to_float(total_amount),
            "payment_method": payment_method,
            "payment_status": payment_status,
            "cash_amount": decimal_to_float(cash_amount),
            "upi_amount": decimal_to_float(upi_amount),
            "upi_reference": upi_reference,
            "credit_amount": decimal_to_float(credit_amount),
            "invoice_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Insert invoice into database
        invoice_id = self.controller.db.insert("invoices", invoice_data)
        
        if not invoice_id:
            messagebox.showerror("Database Error", "Failed to create invoice.")
            return False
        
        # Insert invoice items and update inventory
        for item in self.cart_items:
            # Add to invoice_items (converting any Decimal values to float)
            item_data = {
                "invoice_id": invoice_id,
                "product_id": item["product_id"],
                "quantity": decimal_to_float(item["quantity"]),
                "price_per_unit": decimal_to_float(item["price"]),
                "discount_percentage": decimal_to_float(item["discount"]),
                "total_price": decimal_to_float(item["total"])
            }
            
            # If batch is available, use first batch
            if item["batches"] and item["batches"][0][0]:
                item_data["batch_number"] = item["batches"][0][0]
            
            # Insert item
            item_id = self.controller.db.insert("invoice_items", item_data)
            
            if not item_id:
                messagebox.showerror("Database Error", "Failed to save invoice item.")
                # Don't roll back here, as some items might be saved already
                continue
            
            # Update inventory based on available batches
            remaining_qty = item["quantity"]
            
            if item["batches"]:
                for batch in item["batches"]:
                    batch_number, batch_qty, expiry = batch
                    
                    if remaining_qty <= 0:
                        break
                    
                    # Calculate quantity to deduct from this batch
                    deduct_qty = min(remaining_qty, batch_qty)
                    remaining_qty -= deduct_qty
                    
                    # Update inventory
                    if batch_number:  # If batch is specified
                        update_query = """
                            UPDATE inventory 
                            SET quantity = quantity - ? 
                            WHERE product_id = ? AND batch_number = ?
                        """
                        self.controller.db.execute(update_query, (deduct_qty, item["product_id"], batch_number))
                    else:  # Otherwise, just use any batch
                        update_query = """
                            UPDATE inventory 
                            SET quantity = quantity - ? 
                            WHERE product_id = ? AND quantity > 0
                            LIMIT 1
                        """
                        self.controller.db.execute(update_query, (deduct_qty, item["product_id"]))
                    
                    # Add inventory transaction
                    transaction_data = {
                        "product_id": item["product_id"],
                        "batch_number": batch_number if batch_number else "N/A",
                        "quantity": decimal_to_float(deduct_qty),
                        "transaction_type": "SALE",
                        "reference_id": invoice_id,
                        "notes": f"Invoice #{invoice_number}"
                    }
                    
                    self.controller.db.insert("inventory_transactions", transaction_data)
            
            # If no batches specified or remaining quantity, deduct from any available stock
            if remaining_qty > 0:
                update_query = """
                    UPDATE inventory 
                    SET quantity = quantity - ? 
                    WHERE product_id = ? AND quantity > 0
                    LIMIT 1
                """
                self.controller.db.execute(update_query, (remaining_qty, item["product_id"]))
                
                # Add inventory transaction
                transaction_data = {
                    "product_id": item["product_id"],
                    "batch_number": "N/A",
                    "quantity": decimal_to_float(remaining_qty),
                    "transaction_type": "SALE",
                    "reference_id": invoice_id,
                    "notes": f"Invoice #{invoice_number}"
                }
                
                self.controller.db.insert("inventory_transactions", transaction_data)
        
        # Get product HSN codes
        product_hsn_codes = {}
        for item in self.cart_items:
            if "product_id" in item and item["product_id"]:
                # Query to get the HSN code for this product
                query = "SELECT hsn_code FROM products WHERE id = ?"
                hsn_result = self.controller.db.fetchone(query, (item["product_id"],))
                if hsn_result and hsn_result[0]:
                    product_hsn_codes[item["product_id"]] = hsn_result[0]
        
        # Generate invoice
        invoice_template_data = {
            # Shop info
            "shop_name": self.controller.config.get("shop_name", "Agritech Products Shop"),
            "shop_address": self.controller.config.get("shop_address", "Main Road, Maharashtra"),
            "shop_phone": self.controller.config.get("shop_phone", "+91 1234567890"),
            "shop_gst": self.controller.config.get("shop_gst", "27AABCU9603R1ZX"),
            
            # Invoice info
            "invoice_number": invoice_number,
            "date": datetime.datetime.now().strftime("%d-%m-%Y %H:%M"),
            
            # Customer info
            "customer_name": self.current_customer["name"],
            "customer_phone": self.current_customer["phone"],
            "customer_address": self.current_customer["address"],
            
            # Items
            "items": [
                {
                    "name": item["name"],
                    "price": item["price"],
                    "qty": item["quantity"],
                    "discount": item["discount"],
                    "total": item["total"],
                    "hsn_code": product_hsn_codes.get(item.get("product_id", 0), "")
                }
                for item in self.cart_items
            ],
            
            # Totals
            "subtotal": subtotal,
            "discount": discount,
            "tax": tax,
            "total": total_amount,
            
            # Payment
            "payment_method": payment_method,
            "payment_status": payment_status,
            "cash_amount": cash_amount,
            "upi_amount": upi_amount,
            "upi_reference": upi_reference,
            "credit_amount": credit_amount
        }
        
        # Save invoice to file
        invoices_dir = "invoices"
        os.makedirs(invoices_dir, exist_ok=True)
        invoice_path = os.path.join(invoices_dir, f"{invoice_number}.pdf")
        
        # Generate PDF invoice
        result = generate_invoice(invoice_template_data, invoice_path)
        
        if not result:
            print(f"Warning: Failed to generate invoice file for {invoice_number}")
            messagebox.showerror("Invoice Error", "Failed to generate invoice PDF.")
        else:
            # Update invoice record with the file path
            self.controller.db.execute(
                "UPDATE invoices SET file_path = ? WHERE invoice_number = ?",
                (invoice_path, invoice_number)
            )
            
            # Show success message with option to open the invoice
            open_invoice = messagebox.askyesno(
                "Invoice Generated", 
                f"Invoice #{invoice_number} has been generated successfully!\n\n"
                f"Would you like to open the invoice PDF now?", 
                icon=messagebox.INFO
            )
            
            if open_invoice:
                try:
                    # Use os.startfile on Windows, which is the most reliable method
                    if os.name == 'nt':  # Windows
                        os.startfile(invoice_path)
                    else:  # macOS or Linux
                        import subprocess
                        # Try to use the platform's default application
                        subprocess.call(('xdg-open', invoice_path)) if os.name == 'posix' else subprocess.call(('open', invoice_path))
                except Exception as e:
                    messagebox.showinfo(
                        "Invoice Location", 
                        f"The invoice has been saved to:\n{os.path.abspath(invoice_path)}\n\n"
                        "Please open this file to view the invoice."
                    )
        
        # Clear cart
        self.cart_items = []
        self.next_item_id = 1
        
        # Clear treeview
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        # Reset customer to default
        self.current_customer = {
            "id": 1,  # Default to Walk-in Customer
            "name": "Walk-in Customer",
            "phone": "",
            "address": ""
        }
        self.customer_label.config(text="Walk-in Customer")
        
        # Reset discount
        self.discount_var.set("0.00")
        self.discount_type_var.set("amount")
        
        # Update totals
        self.update_totals()
        
        # Reload products (stock may have changed)
        self.load_products()
        
        return True
    
    def show_cart_context_menu(self, event):
        """Show context menu on right-click in cart"""
        # Create context menu
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Edit Item", command=self.edit_cart_item)
        menu.add_command(label="Remove Item", command=self.remove_selected_item)
        
        # Display menu at mouse position
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def show_product_context_menu(self, event):
        """Show context menu on right-click in product list"""
        # Create context menu
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Add to Cart", command=self.add_to_cart)
        menu.add_command(label="Quick Edit", command=self.quick_edit_product)
        
        # Display menu at mouse position
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def remove_selected_item(self):
        """Remove selected item from cart"""
        selection = self.cart_tree.selection()
        if not selection:
            return
        
        # Get item ID from treeview
        item_id = int(self.cart_tree.item(selection[0], "values")[0])
        
        # Remove item from cart_items list
        self.cart_items = [item for item in self.cart_items if item["id"] != item_id]
        
        # Remove item from treeview
        self.cart_tree.delete(selection[0])
        
        # Update totals
        self.update_totals()
    
    def quick_edit_product(self):
        """Quick edit selected product"""
        selection = self.product_tree.selection()
        if not selection:
            return
        
        # Get product data from treeview
        product_values = self.product_tree.item(selection[0], "values")
        product_id = int(product_values[0])
        
        # Create edit dialog
        dialog = tk.Toplevel(self)
        dialog.title("Quick Edit Product")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        x = self.winfo_x() + (self.winfo_width() // 2) - (400 // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (300 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Dialog content
        frame = tk.Frame(dialog, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Load product data
        query = "SELECT * FROM products WHERE id = ?"
        product = self.controller.db.fetchone(query, (product_id,))
        
        if not product:
            messagebox.showerror("Error", "Product not found.")
            dialog.destroy()
            return
        
        # Unpack product data
        product_data = {
            "id": product[0],
            "product_code": product[1],
            "name": product[2],
            "vendor": product[3],
            "hsn_code": product[4],
            "category": product[5],
            "description": product[6],
            "wholesale_price": product[7],
            "selling_price": product[8],
            "tax_percentage": product[9]
        }
        
        # Title
        tk.Label(frame, 
               text=f"Edit: {product_data['name']}",
               font=FONTS["subheading"]).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))
        
        # Form fields
        fields = [
            {"name": "wholesale_price", "label": "Wholesale Price:", "value": product_data["wholesale_price"]},
            {"name": "selling_price", "label": "Selling Price:", "value": product_data["selling_price"]},
            {"name": "tax_percentage", "label": "Tax %:", "value": product_data["tax_percentage"] or 0}
        ]
        
        # Variables to store entry values
        form_vars = {}
        
        # Create labels and entries
        for i, field in enumerate(fields):
            # Label
            tk.Label(frame, 
                   text=field["label"],
                   font=FONTS["regular_bold"]).grid(row=i+1, column=0, sticky="w", pady=10)
            
            # Entry
            var = tk.StringVar(value=str(field["value"]))
            form_vars[field["name"]] = var
            
            entry = tk.Entry(frame, 
                           textvariable=var,
                           font=FONTS["regular"],
                           width=15)
            entry.grid(row=i+1, column=1, sticky="w", pady=10)
        
        # Buttons frame
        btn_frame = tk.Frame(frame)
        btn_frame.grid(row=len(fields)+1, column=0, columnspan=2, pady=20)
        
        # Save button
        save_btn = tk.Button(btn_frame,
                           text="Save Changes",
                           font=FONTS["regular_bold"],
                           bg=COLORS["primary"],
                           fg=COLORS["text_white"],
                           padx=15,
                           pady=5,
                           cursor="hand2",
                           command=lambda: save_product())
        save_btn.pack(side=tk.LEFT, padx=10)
        
        # Cancel button
        cancel_btn = tk.Button(btn_frame,
                             text="Cancel",
                             font=FONTS["regular"],
                             bg=COLORS["bg_secondary"],
                             fg=COLORS["text_primary"],
                             padx=15,
                             pady=5,
                             cursor="hand2",
                             command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
        def save_product():
            try:
                # Get values from entries
                wholesale_price = float(form_vars["wholesale_price"].get())
                selling_price = float(form_vars["selling_price"].get())
                tax_percentage = float(form_vars["tax_percentage"].get())
                
                # Validate
                if wholesale_price <= 0:
                    messagebox.showerror("Invalid Input", "Wholesale price must be greater than zero.")
                    return
                
                if selling_price <= 0:
                    messagebox.showerror("Invalid Input", "Selling price must be greater than zero.")
                    return
                
                if tax_percentage < 0 or tax_percentage > 100:
                    messagebox.showerror("Invalid Input", "Tax percentage must be between 0 and 100.")
                    return
                
                # Update product
                update_data = {
                    "wholesale_price": wholesale_price,
                    "selling_price": selling_price,
                    "tax_percentage": tax_percentage,
                    "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                result = self.controller.db.update("products", update_data, f"id = {product_id}")
                
                if result:
                    # Close dialog
                    dialog.destroy()
                    
                    # Reload products
                    self.load_products()
                    
                    # Confirm to user
                    messagebox.showinfo("Product Updated", 
                                      f"Product '{product_data['name']}' has been updated.")
                else:
                    messagebox.showerror("Database Error", "Failed to update product.")
                
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter valid numbers.")
    
    def handle_key_event(self, event):
        """Handle keyboard events for navigation and actions"""
        # Focus management
        if event.keysym == "Tab":
            # Switch between cart, products, and payment buttons
            if self.current_focus is None or self.current_focus == "products":
                self.current_focus = "cart"
                self.selected_cart_item = 0 if self.cart_tree.get_children() else -1
                if self.selected_cart_item >= 0:
                    self.cart_tree.selection_set(self.cart_tree.get_children()[self.selected_cart_item])
                    self.cart_tree.focus_set()
            elif self.current_focus == "cart":
                self.current_focus = "buttons"
                # Here we'd focus on a button if we track them
            elif self.current_focus == "buttons":
                self.current_focus = "products"
                self.selected_product_item = 0 if self.product_tree.get_children() else -1
                if self.selected_product_item >= 0:
                    self.product_tree.selection_set(self.product_tree.get_children()[self.selected_product_item])
                    self.product_tree.focus_set()
            return "break"  # Prevent default tab behavior
            
        # Navigation within cart
        if self.current_focus == "cart":
            cart_items = self.cart_tree.get_children()
            if not cart_items:
                return
                
            if event.keysym == "Down":
                # Move to next item in cart
                self.selected_cart_item = min(self.selected_cart_item + 1, len(cart_items) - 1)
                self.cart_tree.selection_set(cart_items[self.selected_cart_item])
                self.cart_tree.see(cart_items[self.selected_cart_item])
            elif event.keysym == "Up":
                # Move to previous item in cart
                self.selected_cart_item = max(self.selected_cart_item - 1, 0)
                self.cart_tree.selection_set(cart_items[self.selected_cart_item])
                self.cart_tree.see(cart_items[self.selected_cart_item])
            elif event.keysym == "Return" or event.keysym == "space":
                # Edit selected cart item
                self.edit_cart_item()
            elif event.keysym == "Delete":
                # Remove selected item
                if self.selected_cart_item >= 0:
                    self.remove_selected_item()
        
        # Navigation within products
        elif self.current_focus == "products":
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
                # Add selected product to cart
                self.add_to_cart()
            elif event.keysym == "f" and event.state & 0x4:  # Ctrl+F
                # Focus search box
                self.search_var.set("")
                self.right_panel.focus_set()
        
        # Shortcuts available in any focus area
        if event.keysym == "c" and event.state & 0x4:  # Ctrl+C
            # Change customer
            self.change_customer()
        elif event.keysym == "p" and event.state & 0x4:  # Ctrl+P
            # Cash payment
            self.process_payment("CASH")
        elif event.keysym == "u" and event.state & 0x4:  # Ctrl+U
            # UPI payment
            self.process_payment("UPI")
        elif event.keysym == "s" and event.state & 0x4:  # Ctrl+S
            # Split payment
            self.process_payment("SPLIT")
        elif event.keysym == "x" and event.state & 0x4:  # Ctrl+X
            # Cancel sale
            self.cancel_sale()
        elif event.keysym == "z" and event.state & 0x4:  # Ctrl+Z
            # Suspend sale
            self.suspend_sale()
    
    def handle_combobox_selection(self, event, field_name, form_vars, entries):
        """Handle selection in category or vendor combobox"""
        # Get combobox
        combobox = event.widget
        selection = combobox.get()
        
        # If "Add new..." selected, prompt for new value
        if selection == "Add new...":
            # Create dialog for new value
            prompt_title = f"Add New {field_name.title()}"
            new_value = simpledialog.askstring(prompt_title, f"Enter new {field_name}:")
            
            if new_value and new_value.strip():
                # Update combobox
                current_values = list(combobox["values"])
                # Remove "Add new..." temporarily
                if "Add new..." in current_values:
                    current_values.remove("Add new...")
                    
                # Add the new value
                if new_value not in current_values:
                    current_values.append(new_value)
                    
                # Re-add "Add new..." at the end
                current_values.append("Add new...")
                
                # Update combobox values and select the new value
                combobox["values"] = current_values
                combobox.set(new_value)
                
                # Update the database
                if field_name == "category":
                    # Get current categories from settings
                    query = "SELECT value FROM settings WHERE key = 'product_categories'"
                    result = self.controller.db.fetchone(query)
                    
                    if result and result[0]:
                        category_list = result[0].split(',')
                        if new_value not in category_list:
                            category_list.append(new_value)
                            new_categories = ",".join(category_list)
                            self.controller.db.update("settings", 
                                                   {"value": new_categories}, 
                                                   "key = 'product_categories'")
                    else:
                        # Create setting
                        self.controller.db.insert("settings", {
                            "key": "product_categories",
                            "value": new_value
                        })
                        
                elif field_name == "vendor":
                    # Get current vendors from settings
                    query = "SELECT value FROM settings WHERE key = 'vendors'"
                    result = self.controller.db.fetchone(query)
                    
                    if result and result[0]:
                        vendor_list = result[0].split(',')
                        if new_value not in vendor_list:
                            vendor_list.append(new_value)
                            new_vendors = ",".join(vendor_list)
                            self.controller.db.update("settings", 
                                                   {"value": new_vendors}, 
                                                   "key = 'vendors'")
                    else:
                        # Create setting
                        self.controller.db.insert("settings", {
                            "key": "vendors",
                            "value": new_value
                        })
            else:
                # If cancelled or empty, reset to empty
                combobox.set("")
    
    def on_show(self):
        """Called when frame is shown"""
        # Reload products
        self.load_products()
        
        # Set initial focus 
        self.current_focus = "products"
        self.focus_set()
        
        # Check for suspended bills
        if self.suspended_bills:
            suspended_count = len(self.suspended_bills)
            messagebox.showinfo("Suspended Bills", 
                              f"You have {suspended_count} suspended bill{'s' if suspended_count > 1 else ''} "
                              "that can be recalled from the Suspended Bills button.")