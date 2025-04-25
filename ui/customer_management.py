"""
Customer Management UI for POS system
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from assets.styles import COLORS, FONTS, STYLES

class CustomerManagementFrame(tk.Frame):
    """Customer management frame for adding, editing, and viewing customers"""
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=COLORS["bg_primary"])
        self.controller = controller
        
        # Create layout
        self.create_layout()
        
        # Load customers
        self.load_customers()
    
    def create_layout(self):
        """Create the customer management layout"""
        # Header
        header_frame = tk.Frame(self, bg=COLORS["bg_primary"], pady=10)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        
        title = tk.Label(header_frame, 
                        text="Customer Management",
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
        self.search_var.trace("w", lambda name, index, mode: self.search_customers())
        
        search_entry = tk.Entry(search_frame, 
                               textvariable=self.search_var,
                               font=FONTS["regular"],
                               width=30)
        search_entry.pack(side=tk.LEFT)
        
        # Add customer button
        add_btn = tk.Button(search_frame,
                          text="Add New Customer",
                          font=FONTS["regular"],
                          bg=COLORS["primary"],
                          fg=COLORS["text_white"],
                          padx=15,
                          pady=5,
                          cursor="hand2",
                          command=self.add_customer)
        add_btn.pack(side=tk.RIGHT)
        
        # Customers treeview
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
        self.customer_tree = ttk.Treeview(tree_frame, 
                                        columns=("ID", "Name", "Phone", "Address", "Credit", "Created", "Updated"),
                                        show="headings",
                                        yscrollcommand=scrollbar.set)
        
        # Configure scrollbar
        scrollbar.config(command=self.customer_tree.yview)
        
        # Define columns
        self.customer_tree.heading("ID", text="ID")
        self.customer_tree.heading("Name", text="Customer Name")
        self.customer_tree.heading("Phone", text="Phone Number")
        self.customer_tree.heading("Address", text="Address")
        self.customer_tree.heading("Credit", text="Credit Limit")
        self.customer_tree.heading("Created", text="Created Date")
        self.customer_tree.heading("Updated", text="Updated Date")
        
        # Set column widths
        self.customer_tree.column("ID", width=50)
        self.customer_tree.column("Name", width=200)
        self.customer_tree.column("Phone", width=120)
        self.customer_tree.column("Address", width=250)
        self.customer_tree.column("Credit", width=100)
        self.customer_tree.column("Created", width=120)
        self.customer_tree.column("Updated", width=120)
        
        self.customer_tree.pack(fill=tk.BOTH, expand=True)
        
        # Binding for double-click to edit
        self.customer_tree.bind("<Double-1>", self.edit_customer)
        
        # Right-click menu for additional options
        self.context_menu = tk.Menu(self, tearoff=0, bg=COLORS["bg_white"], font=FONTS["small"])
        self.context_menu.add_command(label="Edit Customer", command=self.edit_customer)
        self.context_menu.add_command(label="Delete Customer", command=self.delete_customer)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="View Purchase History", command=self.view_history)
        
        # Bind right-click to show menu
        self.customer_tree.bind("<Button-3>", self.show_context_menu)
        
        # Action buttons frame
        button_frame = tk.Frame(self, bg=COLORS["bg_primary"], pady=10, padx=20)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Delete customer button
        delete_btn = tk.Button(button_frame,
                             text="Delete Customer",
                             font=FONTS["regular"],
                             bg=COLORS["danger"],
                             fg=COLORS["text_white"],
                             padx=15,
                             pady=5,
                             cursor="hand2",
                             command=self.delete_customer)
        delete_btn.pack(side=tk.RIGHT, padx=5)
        
        # Edit customer button
        edit_btn = tk.Button(button_frame,
                           text="Edit Customer",
                           font=FONTS["regular"],
                           bg=COLORS["secondary"],
                           fg=COLORS["text_white"],
                           padx=15,
                           pady=5,
                           cursor="hand2",
                           command=self.edit_customer)
        edit_btn.pack(side=tk.RIGHT, padx=5)
        
        # View history button
        history_btn = tk.Button(button_frame,
                              text="View Purchase History",
                              font=FONTS["regular"],
                              bg=COLORS["primary"],
                              fg=COLORS["text_white"],
                              padx=15,
                              pady=5,
                              cursor="hand2",
                              command=self.view_history)
        history_btn.pack(side=tk.RIGHT, padx=5)
    
    def load_customers(self):
        """Load customers from database into treeview"""
        # Clear current items
        for item in self.customer_tree.get_children():
            self.customer_tree.delete(item)
        
        # Get customers from database
        query = """
            SELECT id, name, phone, address, credit_limit, created_at, updated_at
            FROM customers
            ORDER BY name
        """
        customers = self.controller.db.fetchall(query)
        
        # Insert into treeview
        for customer in customers:
            # Format dates
            created_date = self._format_date(customer[5]) if customer[5] else ""
            updated_date = self._format_date(customer[6]) if customer[6] else ""
            
            # Format credit limit
            credit_limit = f"₹{customer[4]:.2f}" if customer[4] else "₹0.00"
            
            self.customer_tree.insert("", "end", values=(
                customer[0],
                customer[1],
                customer[2] if customer[2] else "",
                customer[3] if customer[3] else "",
                credit_limit,
                created_date,
                updated_date
            ))
    
    def search_customers(self):
        """Search customers based on search term"""
        search_term = self.search_var.get().strip().lower()
        
        # Clear current items
        for item in self.customer_tree.get_children():
            self.customer_tree.delete(item)
        
        if not search_term:
            # If search is empty, load all customers
            self.load_customers()
            return
        
        # Get filtered customers
        query = """
            SELECT id, name, phone, address, credit_limit, created_at, updated_at
            FROM customers
            WHERE LOWER(name) LIKE ? OR 
                  LOWER(phone) LIKE ? OR
                  LOWER(address) LIKE ?
            ORDER BY name
        """
        search_pattern = f"%{search_term}%"
        customers = self.controller.db.fetchall(query, (search_pattern, search_pattern, search_pattern))
        
        # Insert into treeview
        for customer in customers:
            # Format dates
            created_date = self._format_date(customer[5]) if customer[5] else ""
            updated_date = self._format_date(customer[6]) if customer[6] else ""
            
            # Format credit limit
            credit_limit = f"₹{customer[4]:.2f}" if customer[4] else "₹0.00"
            
            self.customer_tree.insert("", "end", values=(
                customer[0],
                customer[1],
                customer[2] if customer[2] else "",
                customer[3] if customer[3] else "",
                credit_limit,
                created_date,
                updated_date
            ))
    
    def add_customer(self):
        """Open dialog to add a new customer"""
        # Create customer dialog
        customer_dialog = tk.Toplevel(self)
        customer_dialog.title("Add New Customer")
        customer_dialog.geometry("500x350")
        customer_dialog.resizable(False, False)
        customer_dialog.configure(bg=COLORS["bg_primary"])
        customer_dialog.grab_set()  # Make window modal
        
        # Center the dialog
        customer_dialog.update_idletasks()
        width = customer_dialog.winfo_width()
        height = customer_dialog.winfo_height()
        x = (customer_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (customer_dialog.winfo_screenheight() // 2) - (height // 2)
        customer_dialog.geometry(f"+{x}+{y}")
        
        # Create form
        title = tk.Label(customer_dialog, 
                        text="Add New Customer",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"])
        title.pack(pady=15)
        
        # Form frame
        form_frame = tk.Frame(customer_dialog, bg=COLORS["bg_primary"], padx=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create form fields
        fields = [
            {"name": "name", "label": "Customer Name:", "required": True},
            {"name": "phone", "label": "Phone Number:", "required": False},
            {"name": "address", "label": "Address:", "required": False},
            {"name": "credit_limit", "label": "Credit Limit (₹):", "required": False}
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
            
            # Default credit limit to 0
            if field["name"] == "credit_limit":
                var.set("0")
            
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
        button_frame = tk.Frame(customer_dialog, bg=COLORS["bg_primary"], pady=15)
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
                             command=customer_dialog.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=20)
        
        # Function to save customer
        def save_customer():
            # Validate required fields
            for field in fields:
                if field["required"] and not entry_vars[field["name"]].get().strip():
                    messagebox.showerror("Error", f"{field['label']} is required.")
                    return
            
            # Validate credit limit is a number
            try:
                credit_limit = float(entry_vars["credit_limit"].get().strip() or 0)
                if credit_limit < 0:
                    messagebox.showerror("Error", "Credit limit cannot be negative.")
                    return
            except ValueError:
                messagebox.showerror("Error", "Credit limit must be a number.")
                return
            
            # Create customer data
            customer_data = {
                "name": entry_vars["name"].get().strip(),
                "phone": entry_vars["phone"].get().strip(),
                "address": entry_vars["address"].get().strip(),
                "credit_limit": credit_limit,
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Insert into database
            customer_id = self.controller.db.insert("customers", customer_data)
            
            if customer_id:
                messagebox.showinfo("Success", "Customer added successfully!")
                customer_dialog.destroy()
                self.load_customers()  # Refresh customer list
            else:
                messagebox.showerror("Error", "Failed to add customer.")
        
        # Save button
        save_btn = tk.Button(button_frame,
                           text="Save Customer",
                           font=FONTS["regular"],
                           bg=COLORS["primary"],
                           fg=COLORS["text_white"],
                           padx=20,
                           pady=5,
                           cursor="hand2",
                           command=save_customer)
        save_btn.pack(side=tk.RIGHT, padx=5)
    
    def edit_customer(self, event=None):
        """Open dialog to edit selected customer"""
        # Get selected item
        selection = self.customer_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a customer to edit.")
            return
        
        # Get customer ID
        customer_id = self.customer_tree.item(selection[0])["values"][0]
        
        # Get customer data
        query = """
            SELECT * FROM customers WHERE id = ?
        """
        customer = self.controller.db.fetchone(query, (customer_id,))
        
        if not customer:
            messagebox.showerror("Error", "Customer not found.")
            return
        
        # Create customer dialog
        customer_dialog = tk.Toplevel(self)
        customer_dialog.title("Edit Customer")
        customer_dialog.geometry("500x350")
        customer_dialog.resizable(False, False)
        customer_dialog.configure(bg=COLORS["bg_primary"])
        customer_dialog.grab_set()  # Make window modal
        
        # Center the dialog
        customer_dialog.update_idletasks()
        width = customer_dialog.winfo_width()
        height = customer_dialog.winfo_height()
        x = (customer_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (customer_dialog.winfo_screenheight() // 2) - (height // 2)
        customer_dialog.geometry(f"+{x}+{y}")
        
        # Create form
        title = tk.Label(customer_dialog, 
                        text="Edit Customer",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"])
        title.pack(pady=15)
        
        # Form frame
        form_frame = tk.Frame(customer_dialog, bg=COLORS["bg_primary"], padx=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Column names for reference
        columns = [description[0] for description in self.controller.db.cursor.description]
        
        # Create form fields
        fields = [
            {"name": "name", "label": "Customer Name:", "required": True},
            {"name": "phone", "label": "Phone Number:", "required": False},
            {"name": "address", "label": "Address:", "required": False},
            {"name": "credit_limit", "label": "Credit Limit (₹):", "required": False}
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
            
            # Set value from customer data
            index = columns.index(field["name"])
            if customer[index] is not None:
                var.set(customer[index])
            
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
        button_frame = tk.Frame(customer_dialog, bg=COLORS["bg_primary"], pady=15)
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
                             command=customer_dialog.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=20)
        
        # Function to update customer
        def update_customer():
            # Validate required fields
            for field in fields:
                if field["required"] and not entry_vars[field["name"]].get().strip():
                    messagebox.showerror("Error", f"{field['label']} is required.")
                    return
            
            # Validate credit limit is a number
            try:
                credit_limit = float(entry_vars["credit_limit"].get().strip() or 0)
                if credit_limit < 0:
                    messagebox.showerror("Error", "Credit limit cannot be negative.")
                    return
            except ValueError:
                messagebox.showerror("Error", "Credit limit must be a number.")
                return
            
            # Create customer data
            customer_data = {
                "name": entry_vars["name"].get().strip(),
                "phone": entry_vars["phone"].get().strip(),
                "address": entry_vars["address"].get().strip(),
                "credit_limit": credit_limit,
                "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Update in database
            updated = self.controller.db.update("customers", customer_data, f"id = {customer_id}")
            
            if updated:
                messagebox.showinfo("Success", "Customer updated successfully!")
                customer_dialog.destroy()
                self.load_customers()  # Refresh customer list
            else:
                messagebox.showerror("Error", "Failed to update customer.")
        
        # Save button
        save_btn = tk.Button(button_frame,
                           text="Update Customer",
                           font=FONTS["regular"],
                           bg=COLORS["primary"],
                           fg=COLORS["text_white"],
                           padx=20,
                           pady=5,
                           cursor="hand2",
                           command=update_customer)
        save_btn.pack(side=tk.RIGHT, padx=5)
    
    def delete_customer(self):
        """Delete selected customer"""
        # Get selected item
        selection = self.customer_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a customer to delete.")
            return
        
        # Get customer ID
        customer_id = self.customer_tree.item(selection[0])["values"][0]
        customer_name = self.customer_tree.item(selection[0])["values"][1]
        
        # Don't allow deleting Walk-in Customer
        if customer_id == 1:
            messagebox.showwarning("Warning", "Cannot delete the default Walk-in Customer.")
            return
        
        # Check if customer has invoices
        query = """
            SELECT COUNT(*) FROM invoices WHERE customer_id = ?
        """
        invoice_count = self.controller.db.fetchone(query, (customer_id,))[0]
        
        if invoice_count > 0:
            messagebox.showwarning("Cannot Delete", 
                                 f"Customer '{customer_name}' has {invoice_count} invoices associated with them.\n\n"
                                 f"Please delete the invoices first or reassign them to another customer.")
            return
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", 
                                 f"Are you sure you want to delete customer '{customer_name}'?"):
            return
        
        # Delete from database
        deleted = self.controller.db.delete("customers", f"id = {customer_id}")
        
        if deleted:
            messagebox.showinfo("Success", "Customer deleted successfully!")
            self.load_customers()  # Refresh customer list
        else:
            messagebox.showerror("Error", "Failed to delete customer.")
    
    def view_history(self):
        """View purchase history for selected customer"""
        # Get selected item
        selection = self.customer_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a customer to view purchase history.")
            return
        
        # Get customer ID
        customer_id = self.customer_tree.item(selection[0])["values"][0]
        customer_name = self.customer_tree.item(selection[0])["values"][1]
        
        # Create history dialog
        history_dialog = tk.Toplevel(self)
        history_dialog.title(f"Purchase History - {customer_name}")
        history_dialog.geometry("800x500")
        history_dialog.configure(bg=COLORS["bg_primary"])
        history_dialog.grab_set()  # Make window modal
        
        # Center the dialog
        history_dialog.update_idletasks()
        width = history_dialog.winfo_width()
        height = history_dialog.winfo_height()
        x = (history_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (history_dialog.winfo_screenheight() // 2) - (height // 2)
        history_dialog.geometry(f"+{x}+{y}")
        
        # Create header
        title = tk.Label(history_dialog, 
                        text=f"Purchase History for {customer_name}",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"])
        title.pack(pady=10)
        
        # Add stats frame
        stats_frame = tk.Frame(history_dialog, bg=COLORS["bg_primary"], padx=20, pady=10)
        stats_frame.pack(fill=tk.X)
        
        # Get purchase statistics
        query = """
            SELECT 
                COUNT(*) as total_invoices, 
                SUM(total_amount) as total_spent,
                SUM(CASE WHEN payment_status = 'CREDIT' THEN credit_amount ELSE 0 END) as total_credit
            FROM invoices
            WHERE customer_id = ?
        """
        stats = self.controller.db.fetchone(query, (customer_id,))
        
        # Stats labels
        total_invoices = stats[0] if stats[0] else 0
        total_spent = stats[1] if stats[1] else 0
        total_credit = stats[2] if stats[2] else 0
        
        # Format stats
        tk.Label(stats_frame, 
                text=f"Total Invoices: {total_invoices}",
                font=FONTS["regular_bold"],
                bg=COLORS["bg_primary"],
                fg=COLORS["text_primary"]).grid(row=0, column=0, padx=20)
        
        tk.Label(stats_frame, 
                text=f"Total Amount: ₹{total_spent:.2f}",
                font=FONTS["regular_bold"],
                bg=COLORS["bg_primary"],
                fg=COLORS["text_primary"]).grid(row=0, column=1, padx=20)
        
        tk.Label(stats_frame, 
                text=f"Credit Balance: ₹{total_credit:.2f}",
                font=FONTS["regular_bold"],
                bg=COLORS["bg_primary"],
                fg=COLORS["text_primary"],
                fg_color=COLORS["danger"] if total_credit > 0 else COLORS["text_primary"]).grid(row=0, column=2, padx=20)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(history_dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
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
        invoices_tab = tk.Frame(notebook, bg=COLORS["bg_primary"])
        credit_tab = tk.Frame(notebook, bg=COLORS["bg_primary"])
        
        notebook.add(invoices_tab, text="All Invoices")
        notebook.add(credit_tab, text="Credit Sales")
        
        # Setup invoices tab
        self._setup_invoices_tab(invoices_tab, customer_id)
        
        # Setup credit tab
        self._setup_credit_tab(credit_tab, customer_id)
        
        # Buttons frame
        button_frame = tk.Frame(history_dialog, bg=COLORS["bg_primary"], pady=10)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10)
        
        # Close button
        close_btn = tk.Button(button_frame,
                            text="Close",
                            font=FONTS["regular"],
                            bg=COLORS["secondary"],
                            fg=COLORS["text_white"],
                            padx=20,
                            pady=5,
                            cursor="hand2",
                            command=history_dialog.destroy)
        close_btn.pack(side=tk.RIGHT, padx=10)
    
    def _setup_invoices_tab(self, parent, customer_id):
        """Setup the invoices tab in purchase history"""
        # Create frame with scrollbar
        tree_frame = tk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create treeview
        invoices_tree = ttk.Treeview(tree_frame, 
                                   columns=("ID", "Invoice", "Date", "Total", "Status", "Method"),
                                   show="headings",
                                   yscrollcommand=scrollbar.set)
        
        # Configure scrollbar
        scrollbar.config(command=invoices_tree.yview)
        
        # Define columns
        invoices_tree.heading("ID", text="ID")
        invoices_tree.heading("Invoice", text="Invoice Number")
        invoices_tree.heading("Date", text="Date")
        invoices_tree.heading("Total", text="Total Amount")
        invoices_tree.heading("Status", text="Payment Status")
        invoices_tree.heading("Method", text="Payment Method")
        
        # Set column widths
        invoices_tree.column("ID", width=50)
        invoices_tree.column("Invoice", width=150)
        invoices_tree.column("Date", width=150)
        invoices_tree.column("Total", width=100)
        invoices_tree.column("Status", width=100)
        invoices_tree.column("Method", width=100)
        
        invoices_tree.pack(fill=tk.BOTH, expand=True)
        
        # Get invoices data
        query = """
            SELECT id, invoice_number, invoice_date, total_amount, payment_status, payment_method
            FROM invoices
            WHERE customer_id = ?
            ORDER BY invoice_date DESC
        """
        invoices = self.controller.db.fetchall(query, (customer_id,))
        
        # Insert into treeview
        for invoice in invoices:
            # Format date
            invoice_date = self._format_date(invoice[2]) if invoice[2] else ""
            
            # Format total
            total = f"₹{invoice[3]:.2f}" if invoice[3] else "₹0.00"
            
            # Set row tags for credit sales
            tags = ("credit",) if invoice[4] == "CREDIT" else ()
            
            invoices_tree.insert("", "end", values=(
                invoice[0],
                invoice[1],
                invoice_date,
                total,
                invoice[4],
                invoice[5]
            ), tags=tags)
        
        # Configure tag for credit sales
        invoices_tree.tag_configure("credit", background=COLORS["danger_light"])
    
    def _setup_credit_tab(self, parent, customer_id):
        """Setup the credit tab in purchase history"""
        # Create frame with scrollbar
        tree_frame = tk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create treeview
        credit_tree = ttk.Treeview(tree_frame, 
                                 columns=("ID", "Invoice", "Date", "Amount", "Status"),
                                 show="headings",
                                 yscrollcommand=scrollbar.set)
        
        # Configure scrollbar
        scrollbar.config(command=credit_tree.yview)
        
        # Define columns
        credit_tree.heading("ID", text="ID")
        credit_tree.heading("Invoice", text="Invoice Number")
        credit_tree.heading("Date", text="Date")
        credit_tree.heading("Amount", text="Credit Amount")
        credit_tree.heading("Status", text="Status")
        
        # Set column widths
        credit_tree.column("ID", width=50)
        credit_tree.column("Invoice", width=150)
        credit_tree.column("Date", width=150)
        credit_tree.column("Amount", width=100)
        credit_tree.column("Status", width=100)
        
        credit_tree.pack(fill=tk.BOTH, expand=True)
        
        # Get credit invoices data
        query = """
            SELECT id, invoice_number, invoice_date, credit_amount, payment_status
            FROM invoices
            WHERE customer_id = ? AND payment_status = 'CREDIT'
            ORDER BY invoice_date DESC
        """
        credit_invoices = self.controller.db.fetchall(query, (customer_id,))
        
        # Insert into treeview
        for invoice in credit_invoices:
            # Format date
            invoice_date = self._format_date(invoice[2]) if invoice[2] else ""
            
            # Format amount
            amount = f"₹{invoice[3]:.2f}" if invoice[3] else "₹0.00"
            
            credit_tree.insert("", "end", values=(
                invoice[0],
                invoice[1],
                invoice_date,
                amount,
                invoice[4]
            ))
        
        # Add payment buttons if there are credit invoices
        if credit_invoices:
            # Payment frame
            payment_frame = tk.Frame(parent, bg=COLORS["bg_primary"], pady=10)
            payment_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10)
            
            # Record payment button
            pay_btn = tk.Button(payment_frame,
                              text="Record Payment",
                              font=FONTS["regular"],
                              bg=COLORS["success"],
                              fg=COLORS["text_white"],
                              padx=15,
                              pady=5,
                              cursor="hand2",
                              command=lambda: self._record_payment(customer_id, credit_tree))
            pay_btn.pack(side=tk.RIGHT, padx=5)
    
    def _record_payment(self, customer_id, credit_tree):
        """Record payment for credit sale"""
        # Get selected invoice
        selection = credit_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select an invoice to record payment.")
            return
        
        # Get invoice details
        invoice_id = credit_tree.item(selection[0])["values"][0]
        invoice_number = credit_tree.item(selection[0])["values"][1]
        amount = credit_tree.item(selection[0])["values"][3]
        
        # Parse amount
        credit_amount = float(amount.replace("₹", ""))
        
        # Create payment dialog
        payment_dialog = tk.Toplevel(self)
        payment_dialog.title("Record Payment")
        payment_dialog.geometry("400x300")
        payment_dialog.resizable(False, False)
        payment_dialog.configure(bg=COLORS["bg_primary"])
        payment_dialog.grab_set()
        
        # Center the dialog
        payment_dialog.update_idletasks()
        width = payment_dialog.winfo_width()
        height = payment_dialog.winfo_height()
        x = (payment_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (payment_dialog.winfo_screenheight() // 2) - (height // 2)
        payment_dialog.geometry(f"+{x}+{y}")
        
        # Create form
        title = tk.Label(payment_dialog, 
                        text=f"Record Payment for Invoice #{invoice_number}",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"],
                        wraplength=380)
        title.pack(pady=10)
        
        # Form frame
        form_frame = tk.Frame(payment_dialog, bg=COLORS["bg_primary"], padx=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Amount due
        due_label = tk.Label(form_frame, 
                           text=f"Amount Due: {amount}",
                           font=FONTS["regular_bold"],
                           bg=COLORS["bg_primary"],
                           fg=COLORS["danger"])
        due_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=10)
        
        # Payment method
        method_label = tk.Label(form_frame, 
                              text="Payment Method:",
                              font=FONTS["regular"],
                              bg=COLORS["bg_primary"],
                              fg=COLORS["text_primary"])
        method_label.grid(row=1, column=0, sticky="w", pady=8)
        
        method_var = tk.StringVar(value="Cash")
        methods = ["Cash", "UPI", "Bank Transfer"]
        
        method_combo = ttk.Combobox(form_frame, 
                                  textvariable=method_var, 
                                  values=methods,
                                  font=FONTS["regular"],
                                  width=15,
                                  state="readonly")
        method_combo.grid(row=1, column=1, sticky="w", pady=8, padx=5)
        
        # Payment amount
        amount_label = tk.Label(form_frame, 
                              text="Payment Amount:",
                              font=FONTS["regular"],
                              bg=COLORS["bg_primary"],
                              fg=COLORS["text_primary"])
        amount_label.grid(row=2, column=0, sticky="w", pady=8)
        
        amount_var = tk.StringVar(value=str(credit_amount))
        amount_entry = tk.Entry(form_frame, 
                              textvariable=amount_var,
                              font=FONTS["regular"],
                              width=15)
        amount_entry.grid(row=2, column=1, sticky="w", pady=8, padx=5)
        
        # Notes
        notes_label = tk.Label(form_frame, 
                             text="Notes:",
                             font=FONTS["regular"],
                             bg=COLORS["bg_primary"],
                             fg=COLORS["text_primary"])
        notes_label.grid(row=3, column=0, sticky="w", pady=8)
        
        notes_var = tk.StringVar()
        notes_entry = tk.Entry(form_frame, 
                             textvariable=notes_var,
                             font=FONTS["regular"],
                             width=30)
        notes_entry.grid(row=3, column=1, sticky="w", pady=8, padx=5)
        
        # Buttons frame
        button_frame = tk.Frame(payment_dialog, bg=COLORS["bg_primary"], pady=10)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10)
        
        # Cancel button
        cancel_btn = tk.Button(button_frame,
                             text="Cancel",
                             font=FONTS["regular"],
                             bg=COLORS["bg_secondary"],
                             fg=COLORS["text_primary"],
                             padx=10,
                             pady=5,
                             cursor="hand2",
                             command=payment_dialog.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        # Function to save payment
        def save_payment():
            try:
                # Validate payment amount
                payment_amount = float(amount_var.get())
                if payment_amount <= 0:
                    messagebox.showerror("Error", "Payment amount must be greater than zero.")
                    return
                
                if payment_amount > credit_amount:
                    messagebox.showerror("Error", "Payment amount cannot exceed the amount due.")
                    return
                
                # Update invoice status
                if payment_amount == credit_amount:
                    # Fully paid
                    payment_status = "PAID"
                    new_credit_amount = 0
                else:
                    # Partially paid
                    payment_status = "PARTIAL"
                    new_credit_amount = credit_amount - payment_amount
                
                # Get payment method
                payment_method = method_var.get()
                
                # Update cash/upi amount based on payment method
                cash_amount = payment_amount if payment_method == "Cash" else 0
                upi_amount = payment_amount if payment_method == "UPI" else 0
                
                # Update invoice data
                invoice_data = {
                    "payment_status": payment_status,
                    "credit_amount": new_credit_amount,
                    "cash_amount": cash_amount,
                    "upi_amount": upi_amount,
                    "notes": notes_var.get().strip(),
                    "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Update in database
                updated = self.controller.db.update("invoices", invoice_data, f"id = {invoice_id}")
                
                if updated:
                    messagebox.showinfo("Success", "Payment recorded successfully!")
                    payment_dialog.destroy()
                    
                    # Refresh the view
                    self.view_history()
                else:
                    messagebox.showerror("Error", "Failed to record payment.")
                
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid payment amount.")
        
        # Save button
        save_btn = tk.Button(button_frame,
                           text="Record Payment",
                           font=FONTS["regular"],
                           bg=COLORS["success"],
                           fg=COLORS["text_white"],
                           padx=10,
                           pady=5,
                           cursor="hand2",
                           command=save_payment)
        save_btn.pack(side=tk.RIGHT, padx=5)
    
    def show_context_menu(self, event):
        """Show context menu on right-click"""
        # Select row under mouse
        iid = self.customer_tree.identify_row(event.y)
        if iid:
            # Select the item
            self.customer_tree.selection_set(iid)
            # Show context menu
            self.context_menu.post(event.x_root, event.y_root)
    
    def _format_date(self, date_str):
        """Format date string for display"""
        try:
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            return date_obj.strftime("%d %b %Y, %I:%M %p")
        except (ValueError, TypeError):
            try:
                # Try parsing just the date part
                date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                return date_obj.strftime("%d %b %Y")
            except (ValueError, TypeError):
                return date_str
    
    def on_show(self):
        """Called when frame is shown"""
        # Refresh customer list
        self.load_customers()
