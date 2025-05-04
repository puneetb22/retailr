"""
Settings UI for POS system
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from assets.styles import COLORS, FONTS, STYLES, set_theme
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
                 foreground=[("selected", COLORS["primary_light"])])
        
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
        # Use Canvas and Scrollbar for scrollable content
        shop_canvas = tk.Canvas(self.shop_info_tab, bg=COLORS["bg_primary"])
        scrollbar = ttk.Scrollbar(self.shop_info_tab, orient=tk.VERTICAL, command=shop_canvas.yview)
        shop_canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        shop_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Form frame inside canvas
        form_frame = tk.Frame(shop_canvas, bg=COLORS["bg_primary"], padx=20, pady=20)
        form_frame_window = shop_canvas.create_window((0, 0), window=form_frame, anchor=tk.NW)
        
        # Configure canvas scroll area
        def on_frame_configure(event):
            shop_canvas.configure(scrollregion=shop_canvas.bbox("all"))
        form_frame.bind("<Configure>", on_frame_configure)
        
        # Basic Info Section
        basic_info_frame = tk.LabelFrame(form_frame, text="Basic Shop Information", bg=COLORS["bg_primary"], fg=COLORS["text_primary"], font=FONTS["regular_bold"], padx=10, pady=10)
        basic_info_frame.pack(fill=tk.X, pady=10)
        
        # Create basic form fields
        basic_fields = [
            {"name": "shop_name", "label": "Shop Name:", "default": self.controller.config.get("shop_name", "")},
            {"name": "shop_address", "label": "Address:", "default": self.controller.config.get("shop_address", "")},
            {"name": "shop_phone", "label": "Phone Number:", "default": self.controller.config.get("shop_phone", "")},
            {"name": "shop_email", "label": "Email:", "default": self.controller.config.get("shop_email", "")},
            {"name": "shop_gst", "label": "GST Number:", "default": self.controller.config.get("shop_gst", "")}
        ]
        
        # Variables to store entry values
        self.shop_info_vars = {}
        
        # Create labels and entries for basic fields
        for i, field in enumerate(basic_fields):
            # Label
            label = tk.Label(basic_info_frame, 
                           text=field["label"],
                           font=FONTS["regular_bold"],
                           bg=COLORS["bg_primary"],
                           fg=COLORS["text_primary"])
            label.grid(row=i, column=0, sticky="w", pady=5)
            
            # Entry
            var = tk.StringVar(value=field["default"])
            self.shop_info_vars[field["name"]] = var
            
            entry = tk.Entry(basic_info_frame, 
                          textvariable=var,
                          font=FONTS["regular"],
                          width=40)
            entry.grid(row=i, column=1, sticky="w", pady=5, padx=10)
            
        # State Information Section
        state_info_frame = tk.LabelFrame(form_frame, text="State Information", bg=COLORS["bg_primary"], fg=COLORS["text_primary"], font=FONTS["regular_bold"], padx=10, pady=10)
        state_info_frame.pack(fill=tk.X, pady=10)
        
        # Create state info fields
        state_fields = [
            {"name": "state_name", "label": "State Name:", "default": self.controller.config.get("state_name", "Maharashtra")},
            {"name": "state_code", "label": "State Code:", "default": self.controller.config.get("state_code", "27")}
        ]
        
        # Create labels and entries for state fields
        for i, field in enumerate(state_fields):
            # Label
            label = tk.Label(state_info_frame, 
                           text=field["label"],
                           font=FONTS["regular_bold"],
                           bg=COLORS["bg_primary"],
                           fg=COLORS["text_primary"])
            label.grid(row=i, column=0, sticky="w", pady=5)
            
            # Entry
            var = tk.StringVar(value=field["default"])
            self.shop_info_vars[field["name"]] = var
            
            entry = tk.Entry(state_info_frame, 
                          textvariable=var,
                          font=FONTS["regular"],
                          width=40)
            entry.grid(row=i, column=1, sticky="w", pady=5, padx=10)
        
        # License Information Section
        license_info_frame = tk.LabelFrame(form_frame, text="License Information", bg=COLORS["bg_primary"], fg=COLORS["text_primary"], font=FONTS["regular_bold"], padx=10, pady=10)
        license_info_frame.pack(fill=tk.X, pady=10)
        
        # Create license info fields
        license_fields = [
            {"name": "shop_laid_no", "label": "LAID Number:", "default": self.controller.config.get("shop_laid_no", "")},
            {"name": "shop_lcsd_no", "label": "LCSD Number:", "default": self.controller.config.get("shop_lcsd_no", "")},
            {"name": "shop_lfrd_no", "label": "LFRD Number:", "default": self.controller.config.get("shop_lfrd_no", "")}
        ]
        
        # Create labels and entries for license fields
        for i, field in enumerate(license_fields):
            # Label
            label = tk.Label(license_info_frame, 
                           text=field["label"],
                           font=FONTS["regular_bold"],
                           bg=COLORS["bg_primary"],
                           fg=COLORS["text_primary"])
            label.grid(row=i, column=0, sticky="w", pady=5)
            
            # Entry
            var = tk.StringVar(value=field["default"])
            self.shop_info_vars[field["name"]] = var
            
            entry = tk.Entry(license_info_frame, 
                          textvariable=var,
                          font=FONTS["regular"],
                          width=40)
            entry.grid(row=i, column=1, sticky="w", pady=5, padx=10)
            
        # Terms & Conditions Section
        terms_frame = tk.LabelFrame(form_frame, text="Invoice Terms & Conditions", bg=COLORS["bg_primary"], fg=COLORS["text_primary"], font=FONTS["regular_bold"], padx=10, pady=10)
        terms_frame.pack(fill=tk.X, pady=10)
        
        # Label
        terms_label = tk.Label(terms_frame, 
                             text="Terms & Conditions:",
                             font=FONTS["regular_bold"],
                             bg=COLORS["bg_primary"],
                             fg=COLORS["text_primary"])
        terms_label.grid(row=0, column=0, sticky="w", pady=5)
        
        # Create a Text widget for multiline text
        terms_text = tk.Text(terms_frame, font=FONTS["regular"], width=40, height=4)
        terms_text.grid(row=0, column=1, sticky="w", pady=5, padx=10)
        
        # Insert default text
        default_terms = self.controller.config.get("terms_conditions", "Goods once sold cannot be returned. Payment due within 30 days.")
        terms_text.insert(tk.END, default_terms)
        
        # Store the text widget reference
        self.terms_text = terms_text
        
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
        save_btn.pack(pady=20)
    
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
        templates = ["default", "compact", "detailed", "shop_bill"]
        
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
        
        # Theme settings
        theme_label = tk.Label(form_frame, 
                              text="Application Theme:",
                              font=FONTS["regular_bold"],
                              bg=COLORS["bg_primary"],
                              fg=COLORS["text_primary"])
        theme_label.grid(row=len(fields), column=0, sticky="w", pady=10)
        
        # Theme options
        self.theme_var = tk.StringVar(value=self.controller.config.get("app_theme", "light"))
        
        theme_frame = tk.Frame(form_frame, bg=COLORS["bg_primary"])
        theme_frame.grid(row=len(fields), column=1, sticky="w", pady=10, padx=10)
        
        # Light theme radio button
        light_rb = tk.Radiobutton(theme_frame, 
                                text="Light Theme",
                                variable=self.theme_var,
                                value="light",
                                font=FONTS["regular"],
                                bg=COLORS["bg_primary"],
                                fg=COLORS["text_primary"],
                                selectcolor=COLORS["bg_primary"],
                                command=self.apply_theme)
        light_rb.pack(side=tk.LEFT, padx=10)
        
        # Dark theme radio button
        dark_rb = tk.Radiobutton(theme_frame, 
                               text="Dark Theme",
                               variable=self.theme_var,
                               value="dark",
                               font=FONTS["regular"],
                               bg=COLORS["bg_primary"],
                               fg=COLORS["text_primary"],
                               selectcolor=COLORS["bg_primary"],
                               command=self.apply_theme)
        dark_rb.pack(side=tk.LEFT, padx=10)
        
        # Add keyboard shortcuts button
        shortcuts_btn = tk.Button(form_frame,
                                text="View Keyboard Shortcuts",
                                font=FONTS["regular"],
                                bg=COLORS["primary_light"],
                                fg=COLORS["text_white"],
                                padx=10,
                                pady=5,
                                cursor="hand2",
                                command=self.show_keyboard_shortcuts)
        shortcuts_btn.grid(row=len(fields)+1, column=0, columnspan=2, pady=10, sticky="w")
        
        # Version information
        version_frame = tk.Frame(form_frame, bg=COLORS["bg_primary"], pady=10)
        version_frame.grid(row=len(fields)+2, column=0, columnspan=2, sticky="w", pady=10)
        
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
        save_btn.grid(row=len(fields)+3, column=0, columnspan=2, pady=20)
    
    def save_shop_info(self):
        """Save shop information settings"""
        # Update config
        for key, var in self.shop_info_vars.items():
            self.controller.config[key] = var.get()
        
        # Make sure specific shop_bill template fields are properly stored with correct keys
        # Map license field keys to the expected field names in invoice_generator
        field_mapping = {
            "shop_laid_no": "laid_no",
            "shop_lcsd_no": "lcsd_no", 
            "shop_lfrd_no": "lfrd_no"
        }
        
        # Map fields to expected keys to ensure compatibility with invoice_generator.py
        for ui_key, config_key in field_mapping.items():
            if ui_key in self.shop_info_vars:
                self.controller.config[config_key] = self.shop_info_vars[ui_key].get()
        
        # Save terms and conditions from text widget
        terms_content = self.terms_text.get("1.0", tk.END).strip()
        self.controller.config["terms_conditions"] = terms_content
        
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
            
            # Update theme setting
            self.controller.config["app_theme"] = self.theme_var.get()
            
            # Save to file
            if save_config(self.controller.config):
                messagebox.showinfo("Settings", "System settings saved successfully!")
            else:
                messagebox.showerror("Settings Error", "Failed to save system settings.")
                
        except ValueError:
            messagebox.showerror("Invalid Input", "Low stock threshold must be a positive number.")
    
    def apply_theme(self):
        """Apply the selected theme"""
        theme = self.theme_var.get()
        # Save theme setting to config
        self.controller.config["app_theme"] = theme
        # Apply the theme
        set_theme(theme)
        messagebox.showinfo("Theme Changed", f"The {theme.capitalize()} theme has been applied. Some components may require restarting the application to fully update.")
        
    def show_keyboard_shortcuts(self):
        """Display keyboard shortcuts help"""
        shortcuts_window = tk.Toplevel(self)
        shortcuts_window.title("Keyboard Shortcuts")
        shortcuts_window.geometry("600x500")
        shortcuts_window.resizable(False, False)
        shortcuts_window.configure(bg=COLORS["bg_primary"])
        
        # Create content
        tk.Label(shortcuts_window, 
               text="Keyboard Shortcuts",
               font=FONTS["heading"],
               bg=COLORS["bg_primary"],
               fg=COLORS["text_primary"]).pack(pady=15)
        
        # Create scrollable frame
        canvas = tk.Canvas(shortcuts_window, bg=COLORS["bg_primary"], highlightthickness=0)
        scrollbar = tk.Scrollbar(shortcuts_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS["bg_primary"])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Navigation shortcuts
        self.add_shortcut_section(scrollable_frame, "Navigation", [
            ("↑/↓", "Navigate between items in lists"),
            ("Tab", "Switch focus between different areas"),
            ("Left/Right", "Navigate between menu items"),
            ("Esc", "Exit the application (with confirmation)")
        ])
        
        # Dashboard shortcuts
        self.add_shortcut_section(scrollable_frame, "Dashboard", [
            ("Arrow Keys", "Navigate between menu items"),
            ("Enter", "Select menu item")
        ])
        
        # Sales shortcuts
        self.add_shortcut_section(scrollable_frame, "Sales Screen", [
            ("Ctrl+C", "Change customer"),
            ("Ctrl+P", "Process cash payment"),
            ("Ctrl+U", "Process UPI payment"),
            ("Ctrl+S", "Process split payment"),
            ("Ctrl+X", "Cancel sale"),
            ("Ctrl+Z", "Suspend sale"),
            ("Ctrl+F", "Focus on search field"),
            ("Enter", "Add selected product / Edit cart item"),
            ("Delete", "Remove item from cart"),
            ("Ctrl+Shift+P", "Focus product list"),
            ("Ctrl+Shift+C", "Focus cart")
        ])
        
        # Products shortcuts
        self.add_shortcut_section(scrollable_frame, "Product Management", [
            ("Ctrl+N", "Add new product"),
            ("Ctrl+E", "Edit selected product"),
            ("Ctrl+D", "Delete selected product"),
            ("Ctrl+S", "Add stock to product"),
            ("Ctrl+F", "Focus on search field"),
            ("Enter", "Edit selected product"),
            ("Delete", "Delete selected product")
        ])
        
        # Customer shortcuts
        self.add_shortcut_section(scrollable_frame, "Customer Management", [
            ("Ctrl+N", "Add new customer"),
            ("Ctrl+E", "Edit selected customer"),
            ("Ctrl+D", "Delete selected customer"),
            ("Ctrl+H", "View purchase history"),
            ("Ctrl+F", "Focus on search field"),
            ("Enter", "Edit selected customer"),
            ("Delete", "Delete selected customer")
        ])
        
        # Button at bottom
        button_frame = tk.Frame(shortcuts_window, bg=COLORS["bg_primary"], pady=10)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        close_btn = tk.Button(button_frame,
                           text="Close",
                           font=FONTS["regular_bold"],
                           bg=COLORS["primary"],
                           fg=COLORS["text_white"],
                           padx=20,
                           pady=5,
                           cursor="hand2",
                           command=shortcuts_window.destroy)
        close_btn.pack(pady=10)
        
        # Center window on screen
        shortcuts_window.update_idletasks()
        width = shortcuts_window.winfo_width()
        height = shortcuts_window.winfo_height()
        x = (shortcuts_window.winfo_screenwidth() // 2) - (width // 2)
        y = (shortcuts_window.winfo_screenheight() // 2) - (height // 2)
        shortcuts_window.geometry(f"+{x}+{y}")
        
    def add_shortcut_section(self, parent, title, shortcuts):
        """Add a section of shortcuts to the help window"""
        # Section title
        section_frame = tk.Frame(parent, bg=COLORS["bg_primary"], pady=5)
        section_frame.pack(fill=tk.X, pady=5)
        
        section_title = tk.Label(section_frame,
                               text=title,
                               font=FONTS["subheading"],
                               bg=COLORS["primary"],
                               fg=COLORS["text_white"],
                               padx=10,
                               pady=5)
        section_title.pack(fill=tk.X)
        
        # Shortcuts
        for shortcut, description in shortcuts:
            shortcut_frame = tk.Frame(parent, bg=COLORS["bg_primary"])
            shortcut_frame.pack(fill=tk.X, padx=10)
            
            shortcut_key = tk.Label(shortcut_frame,
                                  text=shortcut,
                                  font=FONTS["regular_bold"],
                                  bg=COLORS["bg_primary"],
                                  fg=COLORS["text_primary"],
                                  width=15,
                                  anchor="w")
            shortcut_key.pack(side=tk.LEFT, padx=10, pady=3)
            
            shortcut_desc = tk.Label(shortcut_frame,
                                   text=description,
                                   font=FONTS["regular"],
                                   bg=COLORS["bg_primary"],
                                   fg=COLORS["text_primary"],
                                   anchor="w")
            shortcut_desc.pack(side=tk.LEFT, padx=10, pady=3, fill=tk.X, expand=True)
                
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
            
        # Theme settings
        self.theme_var.set(self.controller.config.get("app_theme", "light"))