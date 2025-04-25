"""
Settings UI for POS system
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from assets.styles import COLORS, FONTS, STYLES
from utils.config import save_config

class SettingsFrame(tk.Frame):
    """Settings frame for configuring application preferences"""
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=COLORS["bg_primary"])
        self.controller = controller
        
        # Header
        header_frame = tk.Frame(self, bg=COLORS["bg_primary"], pady=10)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        
        title = tk.Label(header_frame, 
                        text="Settings",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"])
        title.pack(side=tk.LEFT, padx=20)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
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
        self.shop_info_tab = tk.Frame(self.notebook, bg=COLORS["bg_primary"])
        self.invoice_tab = tk.Frame(self.notebook, bg=COLORS["bg_primary"])
        self.system_tab = tk.Frame(self.notebook, bg=COLORS["bg_primary"])
        
        self.notebook.add(self.shop_info_tab, text="Shop Information")
        self.notebook.add(self.invoice_tab, text="Invoice Settings")
        self.notebook.add(self.system_tab, text="System Settings")
        
        # Setup tabs
        self.setup_shop_info_tab()
        self.setup_invoice_tab()
        self.setup_system_tab()
    
    def setup_shop_info_tab(self):
        """Setup the shop information tab"""
        # Form frame
        form_frame = tk.Frame(self.shop_info_tab, bg=COLORS["bg_primary"], padx=20, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create form fields
        fields = [
            {"name": "shop_name", "label": "Shop Name:", "default": self.controller.config.get("shop_name", "")},
            {"name": "shop_address", "label": "Address:", "default": self.controller.config.get("shop_address", "")},
            {"name": "shop_phone", "label": "Phone Number:", "default": self.controller.config.get("shop_phone", "")},
            {"name": "shop_gst", "label": "GST Number:", "default": self.controller.config.get("shop_gst", "")}
        ]
        
        # Variables to store entry values
        self.shop_info_vars = {}
        
        # Create labels and entries
        for i, field in enumerate(fields):
            # Label
            label = tk.Label(form_frame, 
                            text=field["label"],
                            font=FONTS["regular_bold"],
                            bg=COLORS["bg_primary"],
                            fg=COLORS["text_primary"])
            label.grid(row=i, column=0, sticky="w", pady=10)
            
            # Entry
            var = tk.StringVar(value=field["default"])
            self.shop_info_vars[field["name"]] = var
            
            entry = tk.Entry(form_frame, 
                           textvariable=var,
                           font=FONTS["regular"],
                           width=40)
            entry.grid(row=i, column=1, sticky="w", pady=10, padx=10)
        
        # Save button
        save_btn = tk.Button(form_frame,
                           text="Save Shop Information",
                           font=FONTS["regular_bold"],
                           bg=COLORS["primary"],
                           fg=COLORS["text_white"],
                           padx=20,
                           pady=8,
                           cursor="hand2",
                           command=self.save_shop_info)
        save_btn.grid(row=len(fields)+1, column=0, columnspan=2, pady=20)
    
    def setup_invoice_tab(self):
        """Setup the invoice settings tab"""
        # Form frame
        form_frame = tk.Frame(self.invoice_tab, bg=COLORS["bg_primary"], padx=20, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create form fields
        fields = [
            {"name": "invoice_prefix", "label": "Invoice Prefix:", "default": self.controller.config.get("invoice_prefix", "")}
        ]
        
        # Variables to store entry values
        self.invoice_vars = {}
        
        # Create labels and entries
        for i, field in enumerate(fields):
            # Label
            label = tk.Label(form_frame, 
                            text=field["label"],
                            font=FONTS["regular_bold"],
                            bg=COLORS["bg_primary"],
                            fg=COLORS["text_primary"])
            label.grid(row=i, column=0, sticky="w", pady=10)
            
            # Entry
            var = tk.StringVar(value=field["default"])
            self.invoice_vars[field["name"]] = var
            
            entry = tk.Entry(form_frame, 
                           textvariable=var,
                           font=FONTS["regular"],
                           width=20)
            entry.grid(row=i, column=1, sticky="w", pady=10, padx=10)
        
        # Invoice template
        template_label = tk.Label(form_frame, 
                               text="Invoice Template:",
                               font=FONTS["regular_bold"],
                               bg=COLORS["bg_primary"],
                               fg=COLORS["text_primary"])
        template_label.grid(row=len(fields), column=0, sticky="w", pady=10)
        
        # Template options
        self.template_var = tk.StringVar(value=self.controller.config.get("invoice_template", "default"))
        templates = ["default", "compact", "detailed"]
        
        template_frame = tk.Frame(form_frame, bg=COLORS["bg_primary"])
        template_frame.grid(row=len(fields), column=1, sticky="w", pady=10, padx=10)
        
        for template in templates:
            rb = tk.Radiobutton(template_frame, 
                              text=template.capitalize(),
                              variable=self.template_var,
                              value=template,
                              font=FONTS["regular"],
                              bg=COLORS["bg_primary"],
                              fg=COLORS["text_primary"],
                              selectcolor=COLORS["bg_primary"])
            rb.pack(side=tk.LEFT, padx=10)
        
        # Save button
        save_btn = tk.Button(form_frame,
                           text="Save Invoice Settings",
                           font=FONTS["regular_bold"],
                           bg=COLORS["primary"],
                           fg=COLORS["text_white"],
                           padx=20,
                           pady=8,
                           cursor="hand2",
                           command=self.save_invoice_settings)
        save_btn.grid(row=len(fields)+2, column=0, columnspan=2, pady=20)
    
    def setup_system_tab(self):
        """Setup the system settings tab"""
        # Form frame
        form_frame = tk.Frame(self.system_tab, bg=COLORS["bg_primary"], padx=20, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create form fields
        fields = [
            {"name": "low_stock_threshold", "label": "Low Stock Threshold:", "default": self.controller.config.get("low_stock_threshold", "10")}
        ]
        
        # Variables to store entry values
        self.system_vars = {}
        
        # Create labels and entries
        for i, field in enumerate(fields):
            # Label
            label = tk.Label(form_frame, 
                            text=field["label"],
                            font=FONTS["regular_bold"],
                            bg=COLORS["bg_primary"],
                            fg=COLORS["text_primary"])
            label.grid(row=i, column=0, sticky="w", pady=10)
            
            # Entry
            var = tk.StringVar(value=field["default"])
            self.system_vars[field["name"]] = var
            
            entry = tk.Entry(form_frame, 
                           textvariable=var,
                           font=FONTS["regular"],
                           width=10)
            entry.grid(row=i, column=1, sticky="w", pady=10, padx=10)
        
        # Version information
        version_frame = tk.Frame(form_frame, bg=COLORS["bg_primary"], pady=20)
        version_frame.grid(row=len(fields)+1, column=0, columnspan=2, sticky="w", pady=10)
        
        version = self.controller.config.get('version', '1.0.0')
        version_label = tk.Label(version_frame, 
                               text=f"Application Version: {version}",
                               font=FONTS["regular_bold"],
                               bg=COLORS["bg_primary"],
                               fg=COLORS["text_primary"])
        version_label.pack(anchor="w")
        
        # Save button
        save_btn = tk.Button(form_frame,
                           text="Save System Settings",
                           font=FONTS["regular_bold"],
                           bg=COLORS["primary"],
                           fg=COLORS["text_white"],
                           padx=20,
                           pady=8,
                           cursor="hand2",
                           command=self.save_system_settings)
        save_btn.grid(row=len(fields)+2, column=0, columnspan=2, pady=20)
    
    def save_shop_info(self):
        """Save shop information settings"""
        # Update config
        for key, var in self.shop_info_vars.items():
            self.controller.config[key] = var.get()
        
        # Save to file
        if save_config(self.controller.config):
            messagebox.showinfo("Settings", "Shop information saved successfully!")
        else:
            messagebox.showerror("Settings Error", "Failed to save shop information.")
    
    def save_invoice_settings(self):
        """Save invoice settings"""
        # Update config
        for key, var in self.invoice_vars.items():
            self.controller.config[key] = var.get()
            
        # Save template
        self.controller.config["invoice_template"] = self.template_var.get()
        
        # Save to file
        if save_config(self.controller.config):
            messagebox.showinfo("Settings", "Invoice settings saved successfully!")
        else:
            messagebox.showerror("Settings Error", "Failed to save invoice settings.")
    
    def save_system_settings(self):
        """Save system settings"""
        # Validate low stock threshold
        try:
            threshold = int(self.system_vars["low_stock_threshold"].get())
            if threshold < 0:
                raise ValueError("Threshold must be positive")
                
            # Update config
            self.controller.config["low_stock_threshold"] = threshold
            
            # Save to file
            if save_config(self.controller.config):
                messagebox.showinfo("Settings", "System settings saved successfully!")
            else:
                messagebox.showerror("Settings Error", "Failed to save system settings.")
                
        except ValueError:
            messagebox.showerror("Invalid Input", "Low stock threshold must be a positive number.")
    
    def on_show(self):
        """Called when frame is shown"""
        # Refresh data from config
        # Shop info
        for key, var in self.shop_info_vars.items():
            var.set(self.controller.config.get(key, ""))
            
        # Invoice settings
        for key, var in self.invoice_vars.items():
            var.set(self.controller.config.get(key, ""))
            
        self.template_var.set(self.controller.config.get("invoice_template", "default"))
        
        # System settings
        for key, var in self.system_vars.items():
            var.set(self.controller.config.get(key, ""))