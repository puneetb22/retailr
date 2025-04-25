"""
Main dashboard for POS system
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from assets.styles import COLORS, FONTS, STYLES

# Import UI modules (will be loaded when needed)
import ui.product_management as product_management
import ui.sales as sales
import ui.customer_management as customer_management
import ui.reports as reports
import ui.inventory_management as inventory_management
import ui.settings as settings
import ui.backup as backup

class Dashboard(tk.Frame):
    """Main dashboard containing the navigation and content frames"""
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=COLORS["bg_primary"])
        self.controller = controller
        
        # Create layout
        self.create_layout()
        
        # Dictionary to store frames
        self.frames = {}
        
        # Load initial frame
        self.load_module("sales")
    
    def create_layout(self):
        """Create the main dashboard layout"""
        # Top header
        self.header_frame = tk.Frame(self, bg=COLORS["primary"], height=60)
        self.header_frame.pack(side=tk.TOP, fill=tk.X)
        self.header_frame.pack_propagate(False)
        
        # Shop name
        shop_name = self.controller.config.get('shop_name', 'Agritech Products Shop')
        shop_label = tk.Label(self.header_frame, 
                             text=shop_name,
                             font=FONTS["heading_light"],
                             bg=COLORS["primary"],
                             fg=COLORS["text_white"])
        shop_label.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Current date and time
        self.datetime_label = tk.Label(self.header_frame,
                                      text=self.get_current_datetime(),
                                      font=FONTS["regular_light"],
                                      bg=COLORS["primary"],
                                      fg=COLORS["text_white"])
        self.datetime_label.pack(side=tk.RIGHT, padx=15, pady=15)
        self.update_datetime()
        
        # Side navigation
        self.nav_frame = tk.Frame(self, bg=COLORS["bg_secondary"], width=220)
        self.nav_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.nav_frame.pack_propagate(False)
        
        # Create navigation items
        self.create_nav_items()
        
        # Main content area
        self.content_frame = tk.Frame(self, bg=COLORS["bg_primary"])
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Footer
        self.footer_frame = tk.Frame(self, bg=COLORS["bg_secondary"], height=30)
        self.footer_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Version info in footer
        version = self.controller.config.get('version', '1.0.0')
        version_label = tk.Label(self.footer_frame, 
                                text=f"Version {version} | Shopkeeper Mode", 
                                font=FONTS["small"],
                                bg=COLORS["bg_secondary"],
                                fg=COLORS["text_secondary"])
        version_label.pack(side=tk.RIGHT, padx=10, pady=5)
        
    def create_nav_items(self):
        """Create navigation buttons in the sidebar"""
        # Nav title
        nav_title = tk.Label(self.nav_frame, 
                            text="MENU",
                            font=FONTS["nav_title"],
                            bg=COLORS["bg_secondary"],
                            fg=COLORS["text_primary"])
        nav_title.pack(side=tk.TOP, pady=(20, 15), padx=10, anchor="w")
        
        # Nav items with icons
        nav_items = [
            {"name": "sales", "text": "Sales & Checkout", "icon": "🛒"},
            {"name": "products", "text": "Products", "icon": "📦"},
            {"name": "inventory", "text": "Inventory", "icon": "🏷️"},
            {"name": "customers", "text": "Customers", "icon": "👥"},
            {"name": "reports", "text": "Reports", "icon": "📊"},
            {"name": "settings", "text": "Settings", "icon": "⚙️"},
            {"name": "backup", "text": "Backup & Restore", "icon": "💾"}
        ]
        
        # Track selected button for styling
        self.selected_nav = None
        
        # Create buttons
        for item in nav_items:
            btn = tk.Button(self.nav_frame,
                          text=f"{item['icon']} {item['text']}",
                          font=FONTS["nav_item"],
                          bg=COLORS["bg_secondary"],
                          fg=COLORS["text_primary"],
                          bd=0,
                          padx=10,
                          pady=10,
                          anchor="w",
                          width=25,
                          relief=tk.FLAT,
                          activebackground=COLORS["primary_light"],
                          activeforeground=COLORS["text_white"],
                          cursor="hand2",
                          command=lambda i=item["name"]: self.load_module(i))
            btn.pack(side=tk.TOP, padx=0, pady=3, fill=tk.X)
            
            # Store reference to button
            setattr(self, f"btn_{item['name']}", btn)
        
        # Add exit button at bottom
        exit_btn = tk.Button(self.nav_frame,
                           text="🚪 Exit Application",
                           font=FONTS["nav_item"],
                           bg=COLORS["bg_secondary"],
                           fg=COLORS["danger"],
                           bd=0,
                           padx=10,
                           pady=10,
                           anchor="w",
                           width=25,
                           relief=tk.FLAT,
                           activebackground=COLORS["danger"],
                           activeforeground=COLORS["text_white"],
                           cursor="hand2",
                           command=self.controller.exit_application)
        exit_btn.pack(side=tk.BOTTOM, padx=0, pady=20, fill=tk.X)
    
    def load_module(self, module_name):
        """Load the specified module into the content frame"""
        # Update nav button styles
        self.update_nav_selection(module_name)
        
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Load appropriate module frame based on selection
        if module_name == "products":
            frame = product_management.ProductManagementFrame(self.content_frame, self.controller)
        elif module_name == "sales":
            frame = sales.SalesFrame(self.content_frame, self.controller)
        elif module_name == "customers":
            frame = customer_management.CustomerManagementFrame(self.content_frame, self.controller)
        elif module_name == "reports":
            frame = reports.ReportsFrame(self.content_frame, self.controller)
        elif module_name == "inventory":
            frame = inventory_management.InventoryManagementFrame(self.content_frame, self.controller)
        elif module_name == "settings":
            frame = settings.SettingsFrame(self.content_frame, self.controller)
        elif module_name == "backup":
            frame = backup.BackupFrame(self.content_frame, self.controller)
        
        # Pack the frame
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Store reference
        self.frames[module_name] = frame
        
        # Call on_show if method exists
        if hasattr(frame, 'on_show'):
            frame.on_show()
    
    def update_nav_selection(self, selected):
        """Update the styling of navigation buttons"""
        # Reset all buttons
        for item in ["sales", "products", "inventory", "customers", "reports", "settings", "backup"]:
            btn = getattr(self, f"btn_{item}")
            btn.config(bg=COLORS["bg_secondary"], fg=COLORS["text_primary"])
        
        # Highlight selected button
        if hasattr(self, f"btn_{selected}"):
            btn = getattr(self, f"btn_{selected}")
            btn.config(bg=COLORS["primary"], fg=COLORS["text_white"])
    
    def get_current_datetime(self):
        """Get formatted current date and time"""
        now = datetime.datetime.now()
        return now.strftime("%d %b %Y, %I:%M:%S %p")
    
    def update_datetime(self):
        """Update the datetime display"""
        self.datetime_label.config(text=self.get_current_datetime())
        # Update every second
        self.after(1000, self.update_datetime)
        
    def on_show(self):
        """Called when dashboard is shown"""
        # Check for low stock and expired items
        self.check_alerts()
    
    def check_alerts(self):
        """Check for system alerts like low stock, expired items"""
        # Query for alerts
        # This is a simplistic implementation - would be expanded in real app
        
        low_stock_threshold = int(self.controller.config.get('low_stock_threshold', 10))
        
        # Check for low stock items
        query = """
            SELECT COUNT(*) FROM inventory
            JOIN products ON inventory.product_id = products.id
            WHERE inventory.quantity <= ?
        """
        low_stock_count = self.controller.db.fetchone(query, (low_stock_threshold,))[0]
        
        # Check for expiring items (items expiring in 30 days)
        today = datetime.date.today()
        thirty_days_later = today + datetime.timedelta(days=30)
        
        query = """
            SELECT COUNT(*) FROM inventory
            WHERE expiry_date IS NOT NULL 
            AND expiry_date <= ? 
            AND expiry_date >= ?
        """
        expiring_count = self.controller.db.fetchone(query, (thirty_days_later.isoformat(), today.isoformat()))[0]
        
        # Show alert if needed
        if low_stock_count > 0 or expiring_count > 0:
            alert_msg = "System Alerts:\n"
            if low_stock_count > 0:
                alert_msg += f"• {low_stock_count} products with low stock\n"
            if expiring_count > 0:
                alert_msg += f"• {expiring_count} products expiring soon\n"
            
            messagebox.showwarning("Inventory Alerts", alert_msg)
