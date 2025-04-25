"""
Accounting UI for POS system
Basic accounting module for profit/loss tracking
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import calendar
from decimal import Decimal

from assets.styles import COLORS, FONTS, STYLES
from utils.helpers import format_currency, parse_currency
from utils.export import export_to_excel

class AccountingFrame(tk.Frame):
    """Accounting frame for basic financial tracking"""
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=COLORS["bg_primary"])
        self.controller = controller
        
        # Header
        header_frame = tk.Frame(self, bg=COLORS["bg_primary"], pady=10)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        
        title = tk.Label(header_frame, 
                        text="Accounting",
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
        self.profit_loss_tab = tk.Frame(self.notebook, bg=COLORS["bg_primary"])
        self.cash_flow_tab = tk.Frame(self.notebook, bg=COLORS["bg_primary"])
        self.expenses_tab = tk.Frame(self.notebook, bg=COLORS["bg_primary"])
        self.ledger_tab = tk.Frame(self.notebook, bg=COLORS["bg_primary"])
        
        self.notebook.add(self.profit_loss_tab, text="Profit & Loss")
        self.notebook.add(self.cash_flow_tab, text="Cash Flow")
        self.notebook.add(self.expenses_tab, text="Expenses")
        self.notebook.add(self.ledger_tab, text="Ledgers")
        
        # Setup tabs
        self.setup_profit_loss_tab()
        self.setup_cash_flow_tab()
        self.setup_expenses_tab()
        self.setup_ledger_tab()
    
    def setup_profit_loss_tab(self):
        """Setup profit & loss tab"""
        # Main container
        container = tk.Frame(self.profit_loss_tab, bg=COLORS["bg_primary"])
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Controls
        left_panel = tk.Frame(container, bg=COLORS["bg_primary"], width=250)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        left_panel.pack_propagate(False)  # Don't shrink
        
        # Right panel - Report
        right_panel = tk.Frame(container, bg=COLORS["bg_white"])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Date range controls
        date_frame = tk.LabelFrame(left_panel, 
                                 text="Date Range",
                                 font=FONTS["regular_bold"],
                                 bg=COLORS["bg_primary"],
                                 fg=COLORS["text_primary"])
        date_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Date range options
        date_ranges = [
            "This Month", 
            "Last Month", 
            "This Quarter", 
            "Last Quarter", 
            "This Year", 
            "Last Year",
            "Custom Range"
        ]
        
        # Create radio buttons for date ranges
        self.pl_date_range_var = tk.StringVar(value="This Month")
        
        for date_range in date_ranges:
            rb = tk.Radiobutton(date_frame, 
                              text=date_range,
                              variable=self.pl_date_range_var,
                              value=date_range,
                              font=FONTS["regular"],
                              bg=COLORS["bg_primary"],
                              fg=COLORS["text_primary"],
                              selectcolor=COLORS["bg_primary"],
                              command=self.toggle_pl_custom_date_range)
            rb.pack(anchor="w", padx=10, pady=2)
        
        # Custom date range frame
        self.pl_custom_date_frame = tk.Frame(date_frame, bg=COLORS["bg_primary"], padx=10)
        
        # Start date
        start_label = tk.Label(self.pl_custom_date_frame, 
                             text="Start Date (YYYY-MM-DD):",
                             font=FONTS["regular"],
                             bg=COLORS["bg_primary"],
                             fg=COLORS["text_primary"])
        start_label.pack(anchor="w", pady=(10, 5))
        
        self.pl_start_date_var = tk.StringVar()
        start_date_entry = tk.Entry(self.pl_custom_date_frame, 
                                  textvariable=self.pl_start_date_var,
                                  font=FONTS["regular"],
                                  width=15)
        start_date_entry.pack(fill=tk.X, pady=(0, 10))
        
        # End date
        end_label = tk.Label(self.pl_custom_date_frame, 
                           text="End Date (YYYY-MM-DD):",
                           font=FONTS["regular"],
                           bg=COLORS["bg_primary"],
                           fg=COLORS["text_primary"])
        end_label.pack(anchor="w", pady=(0, 5))
        
        self.pl_end_date_var = tk.StringVar()
        end_date_entry = tk.Entry(self.pl_custom_date_frame, 
                                textvariable=self.pl_end_date_var,
                                font=FONTS["regular"],
                                width=15)
        end_date_entry.pack(fill=tk.X)
        
        # Generate report button
        generate_btn = tk.Button(left_panel,
                               text="Generate Report",
                               font=FONTS["regular_bold"],
                               bg=COLORS["primary"],
                               fg=COLORS["text_white"],
                               padx=10,
                               pady=5,
                               cursor="hand2",
                               command=self.load_profit_loss)
        generate_btn.pack(padx=10, pady=15)
        
        # Export button
        export_btn = tk.Button(left_panel,
                             text="Export to Excel",
                             font=FONTS["regular"],
                             bg=COLORS["secondary"],
                             fg=COLORS["text_white"],
                             padx=10,
                             pady=5,
                             cursor="hand2",
                             command=self.export_profit_loss)
        export_btn.pack(padx=10, pady=5)
        
        # Initial state - hide custom date frame
        self.toggle_pl_custom_date_range()
        
        # Create scrollable frame for report
        canvas = tk.Canvas(right_panel, bg=COLORS["bg_white"])
        scrollbar = ttk.Scrollbar(right_panel, orient="vertical", command=canvas.yview)
        
        self.pl_report_frame = tk.Frame(canvas, bg=COLORS["bg_white"])
        self.pl_report_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.pl_report_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def toggle_pl_custom_date_range(self):
        """Show/hide custom date range inputs for profit & loss tab"""
        if self.pl_date_range_var.get() == "Custom Range":
            # Set default date range (last 30 days)
            today = datetime.date.today()
            thirty_days_ago = today - datetime.timedelta(days=30)
            
            self.pl_start_date_var.set(thirty_days_ago.strftime("%Y-%m-%d"))
            self.pl_end_date_var.set(today.strftime("%Y-%m-%d"))
            
            # Show custom date frame
            self.pl_custom_date_frame.pack(fill=tk.X, padx=5, pady=5)
        else:
            # Hide custom date frame
            self.pl_custom_date_frame.pack_forget()
    
    def get_pl_date_range(self):
        """Get start and end dates for profit & loss report"""
        date_range = self.pl_date_range_var.get()
        today = datetime.date.today()
        
        if date_range == "This Month":
            start_of_month = today.replace(day=1)
            return start_of_month, today
        
        elif date_range == "Last Month":
            start_of_this_month = today.replace(day=1)
            end_of_last_month = start_of_this_month - datetime.timedelta(days=1)
            start_of_last_month = end_of_last_month.replace(day=1)
            return start_of_last_month, end_of_last_month
        
        elif date_range == "This Quarter":
            current_quarter = (today.month - 1) // 3 + 1
            start_month = (current_quarter - 1) * 3 + 1
            start_of_quarter = today.replace(month=start_month, day=1)
            return start_of_quarter, today
        
        elif date_range == "Last Quarter":
            current_quarter = (today.month - 1) // 3 + 1
            last_quarter = current_quarter - 1
            last_quarter_year = today.year
            
            if last_quarter == 0:
                last_quarter = 4
                last_quarter_year -= 1
                
            start_month = (last_quarter - 1) * 3 + 1
            end_month = start_month + 2
            
            start_of_quarter = datetime.date(last_quarter_year, start_month, 1)
            end_of_quarter = datetime.date(last_quarter_year, end_month, 1)
            end_of_quarter = end_of_quarter.replace(day=calendar.monthrange(end_of_quarter.year, end_of_quarter.month)[1])
            
            return start_of_quarter, end_of_quarter
        
        elif date_range == "This Year":
            start_of_year = today.replace(month=1, day=1)
            return start_of_year, today
        
        elif date_range == "Last Year":
            start_of_last_year = datetime.date(today.year-1, 1, 1)
            end_of_last_year = datetime.date(today.year-1, 12, 31)
            return start_of_last_year, end_of_last_year
        
        elif date_range == "Custom Range":
            try:
                start_date = datetime.datetime.strptime(self.pl_start_date_var.get(), "%Y-%m-%d").date()
                end_date = datetime.datetime.strptime(self.pl_end_date_var.get(), "%Y-%m-%d").date()
                
                # Validate dates
                if start_date > end_date:
                    messagebox.showerror("Date Error", "Start date cannot be after end date.")
                    raise ValueError("Invalid date range")
                
                return start_date, end_date
                
            except ValueError as e:
                if "Invalid date range" not in str(e):
                    messagebox.showerror("Date Error", "Please enter valid dates in YYYY-MM-DD format.")
                # Default to this month on error
                start_of_month = today.replace(day=1)
                return start_of_month, today
        
        # Default fallback
        return today - datetime.timedelta(days=30), today
    
    def load_profit_loss(self):
        """Load and display profit & loss report"""
        # Get date range
        start_date, end_date = self.get_pl_date_range()
        
        # Format dates for SQL query
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        # Clear existing report
        for widget in self.pl_report_frame.winfo_children():
            widget.destroy()
        
        # Add title
        title = tk.Label(self.pl_report_frame,
                       text=f"Profit & Loss Statement",
                       font=FONTS["heading"],
                       bg=COLORS["bg_white"],
                       fg=COLORS["text_primary"])
        title.pack(pady=(20, 5))
        
        # Add date range
        date_label = tk.Label(self.pl_report_frame,
                            text=f"From {start_date_str} to {end_date_str}",
                            font=FONTS["regular_italic"],
                            bg=COLORS["bg_white"],
                            fg=COLORS["text_primary"])
        date_label.pack(pady=(0, 20))
        
        # Get revenue data
        revenue_query = """
            SELECT 
                SUM(total_amount) as total_revenue,
                SUM(discount_amount) as total_discount,
                SUM(tax_amount) as total_tax
            FROM invoices
            WHERE DATE(invoice_date) BETWEEN ? AND ?
        """
        revenue_data = self.controller.db.fetchone(revenue_query, (start_date_str, end_date_str))
        
        # Get cost of goods sold
        cogs_query = """
            SELECT 
                SUM(ii.quantity * p.wholesale_price) as total_cogs
            FROM 
                invoice_items ii
            JOIN 
                invoices i ON ii.invoice_id = i.id
            JOIN 
                products p ON ii.product_id = p.id
            WHERE 
                DATE(i.invoice_date) BETWEEN ? AND ?
        """
        cogs_data = self.controller.db.fetchone(cogs_query, (start_date_str, end_date_str))
        
        # Get expense data
        expense_query = """
            SELECT 
                SUM(amount) as total_expenses
            FROM expenses
            WHERE DATE(expense_date) BETWEEN ? AND ?
        """
        expense_data = self.controller.db.fetchone(expense_query, (start_date_str, end_date_str))
        
        # Extract values (handle None values)
        total_revenue = revenue_data[0] if revenue_data and revenue_data[0] else 0
        total_discount = revenue_data[1] if revenue_data and revenue_data[1] else 0
        total_tax = revenue_data[2] if revenue_data and revenue_data[2] else 0
        total_cogs = cogs_data[0] if cogs_data and cogs_data[0] else 0
        total_expenses = expense_data[0] if expense_data and expense_data[0] else 0
        
        # Calculate net revenue
        net_revenue = total_revenue
        
        # Calculate gross profit
        gross_profit = net_revenue - total_cogs
        
        # Calculate net profit
        net_profit = gross_profit - total_expenses
        
        # Calculate profit margin
        profit_margin = (net_profit / net_revenue * 100) if net_revenue > 0 else 0
        
        # Create report sections
        self.create_pl_section(self.pl_report_frame, "Revenue", [
            {"label": "Gross Revenue", "value": total_revenue},
            {"label": "Tax Collected", "value": total_tax, "indent": True},
            {"label": "Discounts Given", "value": total_discount, "indent": True, "negative": True},
            {"label": "Net Revenue", "value": net_revenue, "bold": True}
        ])
        
        self.create_pl_section(self.pl_report_frame, "Cost of Goods Sold", [
            {"label": "Total Cost of Goods", "value": total_cogs, "negative": True},
            {"label": "Gross Profit", "value": gross_profit, "bold": True}
        ])
        
        self.create_pl_section(self.pl_report_frame, "Operating Expenses", [
            {"label": "Total Expenses", "value": total_expenses, "negative": True}
        ])
        
        self.create_pl_section(self.pl_report_frame, "Net Profit", [
            {"label": "Net Profit", "value": net_profit, "bold": True},
            {"label": "Profit Margin", "value": f"{profit_margin:.2f}%", "is_percent": True}
        ])
        
        # Store for export
        self.pl_report_data = {
            "start_date": start_date_str,
            "end_date": end_date_str,
            "total_revenue": total_revenue,
            "total_discount": total_discount,
            "total_tax": total_tax,
            "net_revenue": net_revenue,
            "total_cogs": total_cogs,
            "gross_profit": gross_profit,
            "total_expenses": total_expenses,
            "net_profit": net_profit,
            "profit_margin": profit_margin
        }
    
    def create_pl_section(self, parent, section_title, items):
        """Create a section in the profit & loss report"""
        section_frame = tk.Frame(parent, bg=COLORS["bg_white"], padx=20, pady=10)
        section_frame.pack(fill=tk.X)
        
        # Add section title
        title = tk.Label(section_frame,
                       text=section_title,
                       font=FONTS["subheading"],
                       bg=COLORS["bg_white"],
                       fg=COLORS["text_primary"])
        title.pack(anchor="w", pady=(0, 10))
        
        # Add section items
        for item in items:
            item_frame = tk.Frame(section_frame, bg=COLORS["bg_white"])
            item_frame.pack(fill=tk.X, pady=2)
            
            # Label
            label_font = FONTS["regular_bold"] if item.get("bold", False) else FONTS["regular"]
            padx = 20 if item.get("indent", False) else 0
            
            label = tk.Label(item_frame,
                           text=item["label"],
                           font=label_font,
                           bg=COLORS["bg_white"],
                           fg=COLORS["text_primary"])
            label.pack(side=tk.LEFT, padx=(padx, 0))
            
            # Value
            if item.get("is_percent", False):
                value_text = item["value"]
            else:
                if item.get("negative", False) and float(item["value"]) > 0:
                    value_text = f"-{format_currency(item['value'])}"
                else:
                    value_text = format_currency(item["value"])
            
            value_color = COLORS["danger"] if item.get("negative", False) else COLORS["text_primary"]
            if item.get("bold", False):
                if float(item["value"]) < 0:
                    value_color = COLORS["danger"]
                else:
                    value_color = COLORS["success"]
            
            value = tk.Label(item_frame,
                           text=value_text,
                           font=label_font,
                           bg=COLORS["bg_white"],
                           fg=value_color)
            value.pack(side=tk.RIGHT)
        
        # Add separator
        separator = ttk.Separator(parent, orient="horizontal")
        separator.pack(fill=tk.X, padx=20, pady=10)
    
    def export_profit_loss(self):
        """Export profit & loss report to Excel"""
        # Check if report has been generated
        if not hasattr(self, 'pl_report_data'):
            messagebox.showinfo("Export", "Please generate a report first.")
            return
        
        # Get date range for filename
        start_date = self.pl_report_data["start_date"]
        end_date = self.pl_report_data["end_date"]
        
        # Prepare data for Excel
        data = {
            "Category": [
                "Gross Revenue",
                "Tax Collected",
                "Discounts Given",
                "Net Revenue",
                "Cost of Goods Sold",
                "Gross Profit",
                "Operating Expenses",
                "Net Profit",
                "Profit Margin (%)"
            ],
            "Amount": [
                self.pl_report_data["total_revenue"],
                self.pl_report_data["total_tax"],
                -self.pl_report_data["total_discount"],
                self.pl_report_data["net_revenue"],
                -self.pl_report_data["total_cogs"],
                self.pl_report_data["gross_profit"],
                -self.pl_report_data["total_expenses"],
                self.pl_report_data["net_profit"],
                self.pl_report_data["profit_margin"]
            ]
        }
        
        import pandas as pd
        df = pd.DataFrame(data)
        
        # Ask user for save location
        import tkinter.filedialog as filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile=f"Profit_Loss_{start_date}_to_{end_date}.xlsx"
        )
        
        if not file_path:
            return
        
        # Export to Excel
        if export_to_excel(df, file_path, "Profit & Loss"):
            messagebox.showinfo("Export", "Report exported successfully.")
        else:
            messagebox.showerror("Export Error", "Failed to export report.")
    
    def setup_cash_flow_tab(self):
        """Setup cash flow tab"""
        # Main container
        container = tk.Frame(self.cash_flow_tab, bg=COLORS["bg_primary"])
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Controls
        left_panel = tk.Frame(container, bg=COLORS["bg_primary"], width=250)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        left_panel.pack_propagate(False)  # Don't shrink
        
        # Right panel - Report
        right_panel = tk.Frame(container, bg=COLORS["bg_white"])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Date range controls
        date_frame = tk.LabelFrame(left_panel, 
                                 text="Date Range",
                                 font=FONTS["regular_bold"],
                                 bg=COLORS["bg_primary"],
                                 fg=COLORS["text_primary"])
        date_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Date range options
        date_ranges = [
            "This Month", 
            "Last Month", 
            "This Quarter", 
            "Custom Range"
        ]
        
        # Create radio buttons for date ranges
        self.cf_date_range_var = tk.StringVar(value="This Month")
        
        for date_range in date_ranges:
            rb = tk.Radiobutton(date_frame, 
                              text=date_range,
                              variable=self.cf_date_range_var,
                              value=date_range,
                              font=FONTS["regular"],
                              bg=COLORS["bg_primary"],
                              fg=COLORS["text_primary"],
                              selectcolor=COLORS["bg_primary"],
                              command=self.toggle_cf_custom_date_range)
            rb.pack(anchor="w", padx=10, pady=2)
        
        # Custom date range frame
        self.cf_custom_date_frame = tk.Frame(date_frame, bg=COLORS["bg_primary"], padx=10)
        
        # Start date
        start_label = tk.Label(self.cf_custom_date_frame, 
                             text="Start Date (YYYY-MM-DD):",
                             font=FONTS["regular"],
                             bg=COLORS["bg_primary"],
                             fg=COLORS["text_primary"])
        start_label.pack(anchor="w", pady=(10, 5))
        
        self.cf_start_date_var = tk.StringVar()
        start_date_entry = tk.Entry(self.cf_custom_date_frame, 
                                  textvariable=self.cf_start_date_var,
                                  font=FONTS["regular"],
                                  width=15)
        start_date_entry.pack(fill=tk.X, pady=(0, 10))
        
        # End date
        end_label = tk.Label(self.cf_custom_date_frame, 
                           text="End Date (YYYY-MM-DD):",
                           font=FONTS["regular"],
                           bg=COLORS["bg_primary"],
                           fg=COLORS["text_primary"])
        end_label.pack(anchor="w", pady=(0, 5))
        
        self.cf_end_date_var = tk.StringVar()
        end_date_entry = tk.Entry(self.cf_custom_date_frame, 
                                textvariable=self.cf_end_date_var,
                                font=FONTS["regular"],
                                width=15)
        end_date_entry.pack(fill=tk.X)
        
        # Generate report button
        generate_btn = tk.Button(left_panel,
                               text="Generate Report",
                               font=FONTS["regular_bold"],
                               bg=COLORS["primary"],
                               fg=COLORS["text_white"],
                               padx=10,
                               pady=5,
                               cursor="hand2",
                               command=self.load_cash_flow)
        generate_btn.pack(padx=10, pady=15)
        
        # Export button
        export_btn = tk.Button(left_panel,
                             text="Export to Excel",
                             font=FONTS["regular"],
                             bg=COLORS["secondary"],
                             fg=COLORS["text_white"],
                             padx=10,
                             pady=5,
                             cursor="hand2",
                             command=self.export_cash_flow)
        export_btn.pack(padx=10, pady=5)
        
        # Initial state - hide custom date frame
        self.toggle_cf_custom_date_range()
        
        # Create scrollable frame for report
        canvas = tk.Canvas(right_panel, bg=COLORS["bg_white"])
        scrollbar = ttk.Scrollbar(right_panel, orient="vertical", command=canvas.yview)
        
        self.cf_report_frame = tk.Frame(canvas, bg=COLORS["bg_white"])
        self.cf_report_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.cf_report_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def toggle_cf_custom_date_range(self):
        """Show/hide custom date range inputs for cash flow tab"""
        if self.cf_date_range_var.get() == "Custom Range":
            # Set default date range (last 30 days)
            today = datetime.date.today()
            thirty_days_ago = today - datetime.timedelta(days=30)
            
            self.cf_start_date_var.set(thirty_days_ago.strftime("%Y-%m-%d"))
            self.cf_end_date_var.set(today.strftime("%Y-%m-%d"))
            
            # Show custom date frame
            self.cf_custom_date_frame.pack(fill=tk.X, padx=5, pady=5)
        else:
            # Hide custom date frame
            self.cf_custom_date_frame.pack_forget()
    
    def get_cf_date_range(self):
        """Get start and end dates for cash flow report"""
        date_range = self.cf_date_range_var.get()
        today = datetime.date.today()
        
        if date_range == "This Month":
            start_of_month = today.replace(day=1)
            return start_of_month, today
        
        elif date_range == "Last Month":
            start_of_this_month = today.replace(day=1)
            end_of_last_month = start_of_this_month - datetime.timedelta(days=1)
            start_of_last_month = end_of_last_month.replace(day=1)
            return start_of_last_month, end_of_last_month
        
        elif date_range == "This Quarter":
            current_quarter = (today.month - 1) // 3 + 1
            start_month = (current_quarter - 1) * 3 + 1
            start_of_quarter = today.replace(month=start_month, day=1)
            return start_of_quarter, today
        
        elif date_range == "Custom Range":
            try:
                start_date = datetime.datetime.strptime(self.cf_start_date_var.get(), "%Y-%m-%d").date()
                end_date = datetime.datetime.strptime(self.cf_end_date_var.get(), "%Y-%m-%d").date()
                
                # Validate dates
                if start_date > end_date:
                    messagebox.showerror("Date Error", "Start date cannot be after end date.")
                    raise ValueError("Invalid date range")
                
                return start_date, end_date
                
            except ValueError as e:
                if "Invalid date range" not in str(e):
                    messagebox.showerror("Date Error", "Please enter valid dates in YYYY-MM-DD format.")
                # Default to this month on error
                start_of_month = today.replace(day=1)
                return start_of_month, today
        
        # Default fallback
        return today - datetime.timedelta(days=30), today
    
    def load_cash_flow(self):
        """Load and display cash flow report"""
        # Get date range
        start_date, end_date = self.get_cf_date_range()
        
        # Format dates for SQL query
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        # Clear existing report
        for widget in self.cf_report_frame.winfo_children():
            widget.destroy()
        
        # Add title
        title = tk.Label(self.cf_report_frame,
                       text=f"Cash Flow Statement",
                       font=FONTS["heading"],
                       bg=COLORS["bg_white"],
                       fg=COLORS["text_primary"])
        title.pack(pady=(20, 5))
        
        # Add date range
        date_label = tk.Label(self.cf_report_frame,
                            text=f"From {start_date_str} to {end_date_str}",
                            font=FONTS["regular_italic"],
                            bg=COLORS["bg_white"],
                            fg=COLORS["text_primary"])
        date_label.pack(pady=(0, 20))
        
        # Get cash inflow data
        cash_inflow_query = """
            SELECT 
                SUM(cash_amount) as cash_sales,
                SUM(upi_amount) as upi_sales,
                COUNT(*) as num_transactions
            FROM invoices
            WHERE 
                DATE(invoice_date) BETWEEN ? AND ? AND
                payment_status = 'PAID'
        """
        cash_inflow_data = self.controller.db.fetchone(cash_inflow_query, (start_date_str, end_date_str))
        
        # Get cash outflow data
        cash_outflow_query = """
            SELECT 
                SUM(amount) as total_expenses,
                COUNT(*) as num_expenses
            FROM expenses
            WHERE DATE(expense_date) BETWEEN ? AND ?
        """
        cash_outflow_data = self.controller.db.fetchone(cash_outflow_query, (start_date_str, end_date_str))
        
        # Extract values (handle None values)
        cash_sales = cash_inflow_data[0] if cash_inflow_data and cash_inflow_data[0] else 0
        upi_sales = cash_inflow_data[1] if cash_inflow_data and cash_inflow_data[1] else 0
        num_transactions = cash_inflow_data[2] if cash_inflow_data and cash_inflow_data[2] else 0
        
        total_expenses = cash_outflow_data[0] if cash_outflow_data and cash_outflow_data[0] else 0
        num_expenses = cash_outflow_data[1] if cash_outflow_data and cash_outflow_data[1] else 0
        
        # Calculate totals
        total_inflow = cash_sales + upi_sales
        net_cash_flow = total_inflow - total_expenses
        
        # Create report sections
        self.create_cf_section(self.cf_report_frame, "Cash Inflows", [
            {"label": "Cash Sales", "value": cash_sales},
            {"label": "UPI Sales", "value": upi_sales},
            {"label": "Total Sales Transactions", "value": num_transactions, "is_count": True},
            {"label": "Total Cash Inflow", "value": total_inflow, "bold": True}
        ])
        
        self.create_cf_section(self.cf_report_frame, "Cash Outflows", [
            {"label": "Total Expenses", "value": total_expenses, "negative": True},
            {"label": "Number of Expenses", "value": num_expenses, "is_count": True},
            {"label": "Total Cash Outflow", "value": total_expenses, "bold": True, "negative": True}
        ])
        
        self.create_cf_section(self.cf_report_frame, "Net Cash Flow", [
            {"label": "Net Cash Flow", "value": net_cash_flow, "bold": True}
        ])
        
        # Store for export
        self.cf_report_data = {
            "start_date": start_date_str,
            "end_date": end_date_str,
            "cash_sales": cash_sales,
            "upi_sales": upi_sales,
            "num_transactions": num_transactions,
            "total_inflow": total_inflow,
            "total_expenses": total_expenses,
            "num_expenses": num_expenses,
            "net_cash_flow": net_cash_flow
        }
    
    def create_cf_section(self, parent, section_title, items):
        """Create a section in the cash flow report"""
        section_frame = tk.Frame(parent, bg=COLORS["bg_white"], padx=20, pady=10)
        section_frame.pack(fill=tk.X)
        
        # Add section title
        title = tk.Label(section_frame,
                       text=section_title,
                       font=FONTS["subheading"],
                       bg=COLORS["bg_white"],
                       fg=COLORS["text_primary"])
        title.pack(anchor="w", pady=(0, 10))
        
        # Add section items
        for item in items:
            item_frame = tk.Frame(section_frame, bg=COLORS["bg_white"])
            item_frame.pack(fill=tk.X, pady=2)
            
            # Label
            label_font = FONTS["regular_bold"] if item.get("bold", False) else FONTS["regular"]
            
            label = tk.Label(item_frame,
                           text=item["label"],
                           font=label_font,
                           bg=COLORS["bg_white"],
                           fg=COLORS["text_primary"])
            label.pack(side=tk.LEFT)
            
            # Value
            if item.get("is_count", False):
                value_text = str(int(item["value"]))
            else:
                if item.get("negative", False) and float(item["value"]) > 0:
                    value_text = f"-{format_currency(item['value'])}"
                else:
                    value_text = format_currency(item["value"])
            
            value_color = COLORS["danger"] if item.get("negative", False) else COLORS["text_primary"]
            if item.get("bold", False):
                if float(item["value"]) < 0:
                    value_color = COLORS["danger"]
                elif float(item["value"]) > 0:
                    value_color = COLORS["success"]
            
            value = tk.Label(item_frame,
                           text=value_text,
                           font=label_font,
                           bg=COLORS["bg_white"],
                           fg=value_color)
            value.pack(side=tk.RIGHT)
        
        # Add separator
        separator = ttk.Separator(parent, orient="horizontal")
        separator.pack(fill=tk.X, padx=20, pady=10)
    
    def export_cash_flow(self):
        """Export cash flow report to Excel"""
        # Check if report has been generated
        if not hasattr(self, 'cf_report_data'):
            messagebox.showinfo("Export", "Please generate a report first.")
            return
        
        # Get date range for filename
        start_date = self.cf_report_data["start_date"]
        end_date = self.cf_report_data["end_date"]
        
        # Prepare data for Excel
        data = {
            "Category": [
                "Cash Sales",
                "UPI Sales",
                "Total Sales Transactions",
                "Total Cash Inflow",
                "Total Expenses",
                "Number of Expenses",
                "Total Cash Outflow",
                "Net Cash Flow"
            ],
            "Amount": [
                self.cf_report_data["cash_sales"],
                self.cf_report_data["upi_sales"],
                self.cf_report_data["num_transactions"],
                self.cf_report_data["total_inflow"],
                -self.cf_report_data["total_expenses"],
                self.cf_report_data["num_expenses"],
                -self.cf_report_data["total_expenses"],
                self.cf_report_data["net_cash_flow"]
            ]
        }
        
        import pandas as pd
        df = pd.DataFrame(data)
        
        # Ask user for save location
        import tkinter.filedialog as filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile=f"Cash_Flow_{start_date}_to_{end_date}.xlsx"
        )
        
        if not file_path:
            return
        
        # Export to Excel
        if export_to_excel(df, file_path, "Cash Flow"):
            messagebox.showinfo("Export", "Report exported successfully.")
        else:
            messagebox.showerror("Export Error", "Failed to export report.")
    
    def setup_expenses_tab(self):
        """Setup expenses management tab"""
        # Main container with two frames side by side
        main_container = tk.Frame(self.expenses_tab, bg=COLORS["bg_primary"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Expense list
        left_panel = tk.Frame(main_container, bg=COLORS["bg_primary"])
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Right panel - Add/Edit expense
        right_panel = tk.Frame(main_container, bg=COLORS["bg_secondary"], width=300)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        right_panel.pack_propagate(False)  # Don't shrink
        
        # Setup expenses list
        self.setup_expense_list(left_panel)
        
        # Setup expense form
        self.setup_expense_form(right_panel)
    
    def setup_expense_list(self, parent):
        """Setup the expense list panel"""
        # Top controls frame
        controls_frame = tk.Frame(parent, bg=COLORS["bg_primary"])
        controls_frame.pack(fill=tk.X, pady=5)
        
        # Title
        title = tk.Label(controls_frame, 
                       text="Expenses",
                       font=FONTS["subheading"],
                       bg=COLORS["bg_primary"],
                       fg=COLORS["text_primary"])
        title.pack(side=tk.LEFT, padx=10)
        
        # Search field
        search_frame = tk.Frame(controls_frame, bg=COLORS["bg_primary"])
        search_frame.pack(side=tk.RIGHT, padx=10)
        
        tk.Label(search_frame, 
               text="Search:",
               font=FONTS["regular"],
               bg=COLORS["bg_primary"],
               fg=COLORS["text_primary"]).pack(side=tk.LEFT, padx=(0, 5))
        
        self.expense_search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, 
                              textvariable=self.expense_search_var,
                              font=FONTS["regular"],
                              width=20)
        search_entry.pack(side=tk.LEFT, padx=(0, 5))
        search_entry.bind("<Return>", lambda event: self.search_expenses())
        
        search_btn = tk.Button(search_frame,
                             text="Search",
                             font=FONTS["regular"],
                             bg=COLORS["primary"],
                             fg=COLORS["text_white"],
                             padx=5,
                             pady=2,
                             cursor="hand2",
                             command=self.search_expenses)
        search_btn.pack(side=tk.LEFT)
        
        # Treeview frame
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
        
        # Create treeview for expenses
        self.expense_tree = ttk.Treeview(tree_frame, 
                                      columns=("id", "date", "category", "amount", "description"),
                                      show="headings",
                                      yscrollcommand=scrollbar.set)
        
        # Configure scrollbar
        scrollbar.config(command=self.expense_tree.yview)
        
        # Define columns
        self.expense_tree.heading("id", text="ID")
        self.expense_tree.heading("date", text="Date")
        self.expense_tree.heading("category", text="Category")
        self.expense_tree.heading("amount", text="Amount")
        self.expense_tree.heading("description", text="Description")
        
        # Set column widths
        self.expense_tree.column("id", width=50)
        self.expense_tree.column("date", width=100)
        self.expense_tree.column("category", width=150)
        self.expense_tree.column("amount", width=100)
        self.expense_tree.column("description", width=300)
        
        self.expense_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind double-click to edit
        self.expense_tree.bind("<Double-1>", self.edit_expense)
        # Bind right-click for context menu
        self.expense_tree.bind("<Button-3>", self.show_expense_context_menu)
        
        # Bottom controls frame
        bottom_frame = tk.Frame(parent, bg=COLORS["bg_primary"], pady=5)
        bottom_frame.pack(fill=tk.X)
        
        # Add expense button
        add_btn = tk.Button(bottom_frame,
                          text="Add New Expense",
                          font=FONTS["regular_bold"],
                          bg=COLORS["primary"],
                          fg=COLORS["text_white"],
                          padx=15,
                          pady=5,
                          cursor="hand2",
                          command=self.add_expense)
        add_btn.pack(side=tk.LEFT, padx=10)
        
        # Delete expense button
        delete_btn = tk.Button(bottom_frame,
                             text="Delete Expense",
                             font=FONTS["regular_bold"],
                             bg=COLORS["danger"],
                             fg=COLORS["text_white"],
                             padx=15,
                             pady=5,
                             cursor="hand2",
                             command=self.delete_expense)
        delete_btn.pack(side=tk.LEFT, padx=10)
        
        # Export button
        export_btn = tk.Button(bottom_frame,
                             text="Export to Excel",
                             font=FONTS["regular"],
                             bg=COLORS["secondary"],
                             fg=COLORS["text_white"],
                             padx=15,
                             pady=5,
                             cursor="hand2",
                             command=self.export_expenses)
        export_btn.pack(side=tk.RIGHT, padx=10)
    
    def setup_expense_form(self, parent):
        """Setup the expense form panel"""
        # Title
        title = tk.Label(parent, 
                       text="Expense Details",
                       font=FONTS["subheading"],
                       bg=COLORS["bg_secondary"],
                       fg=COLORS["text_primary"])
        title.pack(pady=(20, 10))
        
        # Form frame
        form_frame = tk.Frame(parent, bg=COLORS["bg_secondary"], padx=20, pady=10)
        form_frame.pack(fill=tk.X)
        
        # Date
        tk.Label(form_frame, 
               text="Date:",
               font=FONTS["regular_bold"],
               bg=COLORS["bg_secondary"],
               fg=COLORS["text_primary"]).grid(row=0, column=0, sticky="w", pady=10)
        
        self.expense_date_var = tk.StringVar(value=datetime.date.today().strftime("%Y-%m-%d"))
        date_entry = tk.Entry(form_frame, 
                            textvariable=self.expense_date_var,
                            font=FONTS["regular"],
                            width=15)
        date_entry.grid(row=0, column=1, sticky="w", pady=10)
        
        # Category
        tk.Label(form_frame, 
               text="Category:",
               font=FONTS["regular_bold"],
               bg=COLORS["bg_secondary"],
               fg=COLORS["text_primary"]).grid(row=1, column=0, sticky="w", pady=10)
        
        # Get categories from database or use defaults
        expense_categories = self.get_expense_categories()
        
        self.expense_category_var = tk.StringVar()
        category_combo = ttk.Combobox(form_frame, 
                                     textvariable=self.expense_category_var,
                                     values=expense_categories,
                                     font=FONTS["regular"],
                                     width=20)
        category_combo.grid(row=1, column=1, sticky="w", pady=10)
        
        # Amount
        tk.Label(form_frame, 
               text="Amount:",
               font=FONTS["regular_bold"],
               bg=COLORS["bg_secondary"],
               fg=COLORS["text_primary"]).grid(row=2, column=0, sticky="w", pady=10)
        
        self.expense_amount_var = tk.StringVar()
        amount_entry = tk.Entry(form_frame, 
                              textvariable=self.expense_amount_var,
                              font=FONTS["regular"],
                              width=15)
        amount_entry.grid(row=2, column=1, sticky="w", pady=10)
        
        # Description
        tk.Label(form_frame, 
               text="Description:",
               font=FONTS["regular_bold"],
               bg=COLORS["bg_secondary"],
               fg=COLORS["text_primary"]).grid(row=3, column=0, sticky="w", pady=10)
        
        self.expense_description_var = tk.StringVar()
        description_entry = tk.Entry(form_frame, 
                                   textvariable=self.expense_description_var,
                                   font=FONTS["regular"],
                                   width=25)
        description_entry.grid(row=3, column=1, sticky="w", pady=10)
        
        # Buttons frame
        btn_frame = tk.Frame(parent, bg=COLORS["bg_secondary"], pady=20)
        btn_frame.pack()
        
        # Save button
        self.save_expense_btn = tk.Button(btn_frame,
                                      text="Save Expense",
                                      font=FONTS["regular_bold"],
                                      bg=COLORS["primary"],
                                      fg=COLORS["text_white"],
                                      padx=15,
                                      pady=5,
                                      cursor="hand2",
                                      command=self.save_expense)
        self.save_expense_btn.pack(side=tk.LEFT, padx=5)
        
        # Cancel button
        self.cancel_expense_btn = tk.Button(btn_frame,
                                         text="Cancel",
                                         font=FONTS["regular"],
                                         bg=COLORS["bg_white"],
                                         fg=COLORS["text_primary"],
                                         padx=15,
                                         pady=5,
                                         cursor="hand2",
                                         command=self.reset_expense_form)
        self.cancel_expense_btn.pack(side=tk.LEFT, padx=5)
        
        # Store the expense ID for editing (None for new expense)
        self.current_expense_id = None
    
    def get_expense_categories(self):
        """Get list of expense categories from database"""
        # First, get categories from existing expenses
        query = """
            SELECT DISTINCT category 
            FROM expenses 
            ORDER BY category
        """
        categories = [row[0] for row in self.controller.db.fetchall(query) if row[0]]
        
        # Add default categories if not enough
        default_categories = [
            "Rent", 
            "Utilities", 
            "Salaries", 
            "Supplies", 
            "Maintenance", 
            "Transport",
            "Marketing",
            "Miscellaneous"
        ]
        
        for category in default_categories:
            if category not in categories:
                categories.append(category)
        
        return categories
    
    def load_expenses(self):
        """Load expenses into the treeview"""
        # Clear existing items
        for item in self.expense_tree.get_children():
            self.expense_tree.delete(item)
        
        # Get expenses from database
        query = """
            SELECT 
                id,
                expense_date,
                category,
                amount,
                description
            FROM 
                expenses
            ORDER BY 
                expense_date DESC
        """
        expenses = self.controller.db.fetchall(query)
        
        # Insert into treeview
        for expense in expenses:
            expense_id, date_str, category, amount, description = expense
            
            # Format date
            try:
                date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                date_formatted = date_obj.strftime("%Y-%m-%d")
            except:
                date_formatted = date_str
            
            self.expense_tree.insert("", "end", values=(
                expense_id,
                date_formatted,
                category,
                format_currency(amount),
                description or ""
            ))
    
    def search_expenses(self):
        """Search expenses based on search term"""
        search_term = self.expense_search_var.get().strip()
        
        if not search_term:
            # If search is empty, load all expenses
            self.load_expenses()
            return
        
        # Clear existing items
        for item in self.expense_tree.get_children():
            self.expense_tree.delete(item)
        
        # Search expenses
        query = """
            SELECT 
                id,
                expense_date,
                category,
                amount,
                description
            FROM 
                expenses
            WHERE 
                category LIKE ? OR
                description LIKE ?
            ORDER BY 
                expense_date DESC
        """
        search_pattern = f"%{search_term}%"
        expenses = self.controller.db.fetchall(query, (search_pattern, search_pattern))
        
        # Insert into treeview
        for expense in expenses:
            expense_id, date_str, category, amount, description = expense
            
            # Format date
            try:
                date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                date_formatted = date_obj.strftime("%Y-%m-%d")
            except:
                date_formatted = date_str
            
            self.expense_tree.insert("", "end", values=(
                expense_id,
                date_formatted,
                category,
                format_currency(amount),
                description or ""
            ))
    
    def add_expense(self):
        """Prepare form for adding a new expense"""
        # Reset form
        self.reset_expense_form()
        
        # Set current expense ID to None (new expense)
        self.current_expense_id = None
        
        # Update button text
        self.save_expense_btn.config(text="Add Expense")
    
    def edit_expense(self, event=None):
        """Load selected expense for editing"""
        selection = self.expense_tree.selection()
        if not selection:
            return
        
        # Get expense data
        expense_values = self.expense_tree.item(selection[0], "values")
        expense_id = expense_values[0]
        
        # Get expense details from database
        query = """
            SELECT 
                expense_date,
                category,
                amount,
                description
            FROM 
                expenses
            WHERE 
                id = ?
        """
        expense = self.controller.db.fetchone(query, (expense_id,))
        
        if not expense:
            messagebox.showerror("Error", "Expense not found.")
            return
        
        # Set form values
        self.expense_date_var.set(expense[0])
        self.expense_category_var.set(expense[1])
        self.expense_amount_var.set(str(expense[2]))
        self.expense_description_var.set(expense[3] or "")
        
        # Set current expense ID
        self.current_expense_id = expense_id
        
        # Update button text
        self.save_expense_btn.config(text="Update Expense")
    
    def save_expense(self):
        """Save or update expense"""
        try:
            # Validate date
            date_str = self.expense_date_var.get().strip()
            try:
                date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                date_str = date_obj.strftime("%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Invalid Date", "Please enter a valid date in YYYY-MM-DD format.")
                return
            
            # Validate category
            category = self.expense_category_var.get().strip()
            if not category:
                messagebox.showerror("Required Field", "Category is required.")
                return
            
            # Validate amount
            amount_str = self.expense_amount_var.get().strip()
            try:
                amount = parse_currency(amount_str)
                if amount <= 0:
                    messagebox.showerror("Invalid Amount", "Amount must be greater than zero.")
                    return
            except ValueError:
                messagebox.showerror("Invalid Amount", "Please enter a valid amount.")
                return
            
            # Get description
            description = self.expense_description_var.get().strip()
            
            # Prepare expense data
            expense_data = {
                "expense_date": date_str,
                "category": category,
                "amount": amount,
                "description": description
            }
            
            if self.current_expense_id is None:
                # Add new expense
                expense_data["created_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                result = self.controller.db.insert("expenses", expense_data)
                
                if result:
                    messagebox.showinfo("Success", "Expense added successfully.")
                else:
                    messagebox.showerror("Error", "Failed to add expense.")
                    return
            else:
                # Update existing expense
                result = self.controller.db.update("expenses", expense_data, f"id = {self.current_expense_id}")
                
                if result:
                    messagebox.showinfo("Success", "Expense updated successfully.")
                else:
                    messagebox.showerror("Error", "Failed to update expense.")
                    return
            
            # Reset form
            self.reset_expense_form()
            
            # Reload expenses
            self.load_expenses()
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
    
    def delete_expense(self):
        """Delete selected expense"""
        selection = self.expense_tree.selection()
        if not selection:
            messagebox.showinfo("Select Expense", "Please select an expense to delete.")
            return
        
        # Get expense ID
        expense_id = self.expense_tree.item(selection[0], "values")[0]
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this expense?"):
            return
        
        # Delete expense
        result = self.controller.db.delete("expenses", f"id = {expense_id}")
        
        if result:
            messagebox.showinfo("Success", "Expense deleted successfully.")
            
            # Reset form if the deleted expense was being edited
            if self.current_expense_id == expense_id:
                self.reset_expense_form()
                
            # Reload expenses
            self.load_expenses()
        else:
            messagebox.showerror("Error", "Failed to delete expense.")
    
    def reset_expense_form(self):
        """Reset expense form to default values"""
        self.expense_date_var.set(datetime.date.today().strftime("%Y-%m-%d"))
        self.expense_category_var.set("")
        self.expense_amount_var.set("")
        self.expense_description_var.set("")
        
        # Reset current expense ID
        self.current_expense_id = None
        
        # Update button text
        self.save_expense_btn.config(text="Save Expense")
    
    def show_expense_context_menu(self, event):
        """Show context menu for expense treeview"""
        # Create context menu
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Edit Expense", command=self.edit_expense)
        menu.add_command(label="Delete Expense", command=self.delete_expense)
        
        # Display menu at mouse position
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def export_expenses(self):
        """Export expenses to Excel"""
        # Get all expenses
        query = """
            SELECT 
                id,
                expense_date,
                category,
                amount,
                description,
                created_at
            FROM 
                expenses
            ORDER BY 
                expense_date DESC
        """
        expenses = self.controller.db.fetchall(query)
        
        if not expenses:
            messagebox.showinfo("Export", "No expenses to export.")
            return
        
        # Prepare data for Excel
        data = {
            "ID": [],
            "Date": [],
            "Category": [],
            "Amount": [],
            "Description": [],
            "Created At": []
        }
        
        for expense in expenses:
            data["ID"].append(expense[0])
            data["Date"].append(expense[1])
            data["Category"].append(expense[2])
            data["Amount"].append(expense[3])
            data["Description"].append(expense[4] or "")
            data["Created At"].append(expense[5])
        
        import pandas as pd
        df = pd.DataFrame(data)
        
        # Ask user for save location
        import tkinter.filedialog as filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile="Expenses_Report.xlsx"
        )
        
        if not file_path:
            return
        
        # Export to Excel
        if export_to_excel(df, file_path, "Expenses"):
            messagebox.showinfo("Export", "Expenses exported successfully.")
        else:
            messagebox.showerror("Export Error", "Failed to export expenses.")
    
    def setup_ledger_tab(self):
        """Setup customer/supplier ledger tab"""
        # Main container
        container = tk.Frame(self.ledger_tab, bg=COLORS["bg_primary"])
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Top controls frame
        controls_frame = tk.Frame(container, bg=COLORS["bg_primary"])
        controls_frame.pack(fill=tk.X, pady=5)
        
        # Label
        tk.Label(controls_frame, 
               text="Select Ledger Type:",
               font=FONTS["regular_bold"],
               bg=COLORS["bg_primary"],
               fg=COLORS["text_primary"]).pack(side=tk.LEFT, padx=10)
        
        # Ledger type selection
        self.ledger_type_var = tk.StringVar(value="customer")
        
        customer_rb = tk.Radiobutton(controls_frame, 
                                   text="Customer Ledger",
                                   variable=self.ledger_type_var,
                                   value="customer",
                                   font=FONTS["regular"],
                                   bg=COLORS["bg_primary"],
                                   fg=COLORS["text_primary"],
                                   selectcolor=COLORS["bg_primary"],
                                   command=self.load_ledger_entities)
        customer_rb.pack(side=tk.LEFT, padx=10)
        
        supplier_rb = tk.Radiobutton(controls_frame, 
                                   text="Supplier Ledger",
                                   variable=self.ledger_type_var,
                                   value="supplier",
                                   font=FONTS["regular"],
                                   bg=COLORS["bg_primary"],
                                   fg=COLORS["text_primary"],
                                   selectcolor=COLORS["bg_primary"],
                                   command=self.load_ledger_entities)
        supplier_rb.pack(side=tk.LEFT, padx=10)
        
        # Entity selection frame
        entity_frame = tk.Frame(container, bg=COLORS["bg_primary"], pady=10)
        entity_frame.pack(fill=tk.X)
        
        tk.Label(entity_frame, 
               text="Select Entity:",
               font=FONTS["regular_bold"],
               bg=COLORS["bg_primary"],
               fg=COLORS["text_primary"]).pack(side=tk.LEFT, padx=10)
        
        # Entity dropdown
        self.entity_var = tk.StringVar()
        self.entity_dropdown = ttk.Combobox(entity_frame, 
                                          textvariable=self.entity_var,
                                          font=FONTS["regular"],
                                          width=30,
                                          state="readonly")
        self.entity_dropdown.pack(side=tk.LEFT, padx=10)
        
        # Load button
        load_btn = tk.Button(entity_frame,
                           text="Load Ledger",
                           font=FONTS["regular"],
                           bg=COLORS["primary"],
                           fg=COLORS["text_white"],
                           padx=10,
                           pady=2,
                           cursor="hand2",
                           command=self.load_ledger)
        load_btn.pack(side=tk.LEFT, padx=10)
        
        # Date range frame
        date_frame = tk.Frame(container, bg=COLORS["bg_primary"], pady=5)
        date_frame.pack(fill=tk.X)
        
        tk.Label(date_frame, 
               text="Date Range:",
               font=FONTS["regular_bold"],
               bg=COLORS["bg_primary"],
               fg=COLORS["text_primary"]).pack(side=tk.LEFT, padx=10)
        
        # Start date
        tk.Label(date_frame, 
               text="From:",
               font=FONTS["regular"],
               bg=COLORS["bg_primary"],
               fg=COLORS["text_primary"]).pack(side=tk.LEFT, padx=(10, 5))
        
        self.ledger_start_date_var = tk.StringVar()
        # Set default to 3 months ago
        start_date = datetime.date.today().replace(day=1) - datetime.timedelta(days=90)
        self.ledger_start_date_var.set(start_date.strftime("%Y-%m-%d"))
        
        start_date_entry = tk.Entry(date_frame, 
                                  textvariable=self.ledger_start_date_var,
                                  font=FONTS["regular"],
                                  width=12)
        start_date_entry.pack(side=tk.LEFT)
        
        # End date
        tk.Label(date_frame, 
               text="To:",
               font=FONTS["regular"],
               bg=COLORS["bg_primary"],
               fg=COLORS["text_primary"]).pack(side=tk.LEFT, padx=(10, 5))
        
        self.ledger_end_date_var = tk.StringVar(value=datetime.date.today().strftime("%Y-%m-%d"))
        end_date_entry = tk.Entry(date_frame, 
                                textvariable=self.ledger_end_date_var,
                                font=FONTS["regular"],
                                width=12)
        end_date_entry.pack(side=tk.LEFT)
        
        # Ledger treeview frame
        tree_frame = tk.Frame(container)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create treeview for ledger
        self.ledger_tree = ttk.Treeview(tree_frame, 
                                     columns=("date", "ref", "description", "debit", "credit", "balance"),
                                     show="headings",
                                     yscrollcommand=scrollbar.set)
        
        # Configure scrollbar
        scrollbar.config(command=self.ledger_tree.yview)
        
        # Define columns
        self.ledger_tree.heading("date", text="Date")
        self.ledger_tree.heading("ref", text="Reference")
        self.ledger_tree.heading("description", text="Description")
        self.ledger_tree.heading("debit", text="Debit")
        self.ledger_tree.heading("credit", text="Credit")
        self.ledger_tree.heading("balance", text="Balance")
        
        # Set column widths
        self.ledger_tree.column("date", width=100)
        self.ledger_tree.column("ref", width=100)
        self.ledger_tree.column("description", width=300)
        self.ledger_tree.column("debit", width=100)
        self.ledger_tree.column("credit", width=100)
        self.ledger_tree.column("balance", width=100)
        
        self.ledger_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bottom controls frame
        bottom_frame = tk.Frame(container, bg=COLORS["bg_primary"], pady=10)
        bottom_frame.pack(fill=tk.X)
        
        # Summary frame
        summary_frame = tk.Frame(bottom_frame, bg=COLORS["bg_primary"])
        summary_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Label(summary_frame, 
               text="Total Debit:",
               font=FONTS["regular_bold"],
               bg=COLORS["bg_primary"],
               fg=COLORS["text_primary"]).grid(row=0, column=0, sticky="w", padx=5)
        
        self.total_debit_label = tk.Label(summary_frame, 
                                        text="₹0.00",
                                        font=FONTS["regular"],
                                        bg=COLORS["bg_primary"],
                                        fg=COLORS["text_primary"])
        self.total_debit_label.grid(row=0, column=1, sticky="w", padx=5)
        
        tk.Label(summary_frame, 
               text="Total Credit:",
               font=FONTS["regular_bold"],
               bg=COLORS["bg_primary"],
               fg=COLORS["text_primary"]).grid(row=1, column=0, sticky="w", padx=5)
        
        self.total_credit_label = tk.Label(summary_frame, 
                                         text="₹0.00",
                                         font=FONTS["regular"],
                                         bg=COLORS["bg_primary"],
                                         fg=COLORS["text_primary"])
        self.total_credit_label.grid(row=1, column=1, sticky="w", padx=5)
        
        tk.Label(summary_frame, 
               text="Current Balance:",
               font=FONTS["regular_bold"],
               bg=COLORS["bg_primary"],
               fg=COLORS["text_primary"]).grid(row=2, column=0, sticky="w", padx=5)
        
        self.current_balance_label = tk.Label(summary_frame, 
                                           text="₹0.00",
                                           font=FONTS["regular_bold"],
                                           bg=COLORS["bg_primary"],
                                           fg=COLORS["text_primary"])
        self.current_balance_label.grid(row=2, column=1, sticky="w", padx=5)
        
        # Export button
        export_btn = tk.Button(bottom_frame,
                             text="Export to Excel",
                             font=FONTS["regular"],
                             bg=COLORS["secondary"],
                             fg=COLORS["text_white"],
                             padx=15,
                             pady=5,
                             cursor="hand2",
                             command=self.export_ledger)
        export_btn.pack(side=tk.RIGHT, padx=10)
        
        # Load initial data
        self.load_ledger_entities()
    
    def load_ledger_entities(self):
        """Load entities (customers or suppliers) into dropdown"""
        ledger_type = self.ledger_type_var.get()
        
        if ledger_type == "customer":
            # Load customers
            query = "SELECT id, name FROM customers ORDER BY name"
            entities = self.controller.db.fetchall(query)
            
            # Format for dropdown
            entity_list = [f"{name} (ID: {id})" for id, name in entities]
            
            # Update dropdown
            self.entity_dropdown["values"] = entity_list
            
            if entity_list:
                self.entity_dropdown.current(0)
        else:
            # Load suppliers (placeholder - in real app, would load from suppliers table)
            # For demo, we'll use a static list
            self.entity_dropdown["values"] = [
                "Agricultural Supplier Ltd. (Demo)", 
                "Farm Equipment Inc. (Demo)", 
                "Pesticide Products Co. (Demo)"
            ]
            self.entity_dropdown.current(0)
    
    def load_ledger(self):
        """Load ledger for selected entity"""
        entity = self.entity_var.get()
        if not entity:
            messagebox.showinfo("Select Entity", "Please select an entity.")
            return
        
        # Clear existing items
        for item in self.ledger_tree.get_children():
            self.ledger_tree.delete(item)
        
        # Get entity ID if customer
        entity_id = None
        if self.ledger_type_var.get() == "customer":
            try:
                # Extract ID from dropdown text (ID: X)
                entity_id = int(entity.split("(ID: ")[1].split(")")[0])
            except:
                # If parsing fails, show error
                messagebox.showerror("Error", "Invalid entity selection.")
                return
        
        # Get date range
        try:
            start_date = datetime.datetime.strptime(self.ledger_start_date_var.get(), "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(self.ledger_end_date_var.get(), "%Y-%m-%d").date()
            
            # Validate dates
            if start_date > end_date:
                messagebox.showerror("Date Error", "Start date cannot be after end date.")
                return
                
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")
            
        except ValueError:
            messagebox.showerror("Date Error", "Please enter valid dates in YYYY-MM-DD format.")
            return
        
        # Load ledger data based on type
        if self.ledger_type_var.get() == "customer":
            self.load_customer_ledger(entity_id, start_date_str, end_date_str)
        else:
            self.load_supplier_ledger(entity, start_date_str, end_date_str)
    
    def load_customer_ledger(self, customer_id, start_date, end_date):
        """Load customer ledger data"""
        # Get opening balance (all transactions before start date)
        opening_balance_query = """
            SELECT 
                SUM(CASE WHEN payment_status = 'PAID' THEN 0 ELSE credit_amount END) as opening_balance 
            FROM 
                invoices 
            WHERE 
                customer_id = ? AND 
                DATE(invoice_date) < ?
        """
        opening_balance_data = self.controller.db.fetchone(opening_balance_query, (customer_id, start_date))
        opening_balance = opening_balance_data[0] if opening_balance_data and opening_balance_data[0] else 0
        
        # Add opening balance row
        self.ledger_tree.insert("", "end", values=(
            start_date,
            "",
            "Opening Balance",
            "",
            "",
            format_currency(opening_balance)
        ))
        
        # Get ledger transactions
        transactions_query = """
            SELECT 
                DATE(invoice_date) as date,
                invoice_number as reference,
                CASE 
                    WHEN payment_status = 'PAID' THEN 'Payment received'
                    ELSE 'Invoice generated' 
                END as description,
                0 as debit,
                credit_amount as credit
            FROM 
                invoices 
            WHERE 
                customer_id = ? AND 
                DATE(invoice_date) BETWEEN ? AND ? AND
                credit_amount > 0
            
            UNION ALL
            
            -- Add payments made by customer
            SELECT 
                DATE(transaction_date) as date,
                reference_id as reference,
                'Payment received' as description,
                amount as debit,
                0 as credit
            FROM 
                credit_payments
            WHERE 
                customer_id = ? AND 
                DATE(transaction_date) BETWEEN ? AND ?
            
            ORDER BY 
                date, reference
        """
        
        # For demo, we'll simplify by using only invoices since credit_payments table might not exist
        transactions_query = """
            SELECT 
                DATE(invoice_date) as date,
                invoice_number as reference,
                'Invoice generated' as description,
                0 as debit,
                credit_amount as credit
            FROM 
                invoices 
            WHERE 
                customer_id = ? AND 
                DATE(invoice_date) BETWEEN ? AND ? AND
                credit_amount > 0
            ORDER BY 
                date, reference
        """
        
        transactions = self.controller.db.fetchall(transactions_query, (customer_id, start_date, end_date))
        
        # Initialize running balance and totals
        balance = opening_balance
        total_debit = 0
        total_credit = 0
        
        # Add transactions to treeview
        for date, reference, description, debit, credit in transactions:
            # Update running balance
            balance = balance - debit + credit
            
            # Update totals
            total_debit += debit
            total_credit += credit
            
            # Add to treeview
            self.ledger_tree.insert("", "end", values=(
                date,
                reference,
                description,
                format_currency(debit) if debit else "",
                format_currency(credit) if credit else "",
                format_currency(balance)
            ))
        
        # Add closing balance row
        self.ledger_tree.insert("", "end", values=(
            end_date,
            "",
            "Closing Balance",
            "",
            "",
            format_currency(balance)
        ))
        
        # Update summary labels
        self.total_debit_label.config(text=format_currency(total_debit))
        self.total_credit_label.config(text=format_currency(total_credit))
        self.current_balance_label.config(text=format_currency(balance))
        
        # Set color for balance
        if balance > 0:
            self.current_balance_label.config(fg=COLORS["danger"])
        else:
            self.current_balance_label.config(fg=COLORS["text_primary"])
        
        # Store for export
        self.ledger_data = {
            "entity": self.entity_var.get(),
            "type": "Customer",
            "start_date": start_date,
            "end_date": end_date,
            "opening_balance": opening_balance,
            "transactions": transactions,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "closing_balance": balance
        }
    
    def load_supplier_ledger(self, supplier_name, start_date, end_date):
        """Load supplier ledger data (demo/placeholder)"""
        # This is a placeholder - in a real app, would load from database
        
        # Demo data
        from random import randint, choice
        import string
        
        # Generate a random reference number
        def random_ref():
            return ''.join(choice(string.ascii_uppercase) for _ in range(2)) + str(randint(1000, 9999))
        
        # Parse dates
        start = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
        
        # Generate demo transactions
        transactions = []
        current_date = start
        
        # Opening balance transaction
        opening_balance = randint(10000, 50000)
        
        # Add opening balance row
        self.ledger_tree.insert("", "end", values=(
            start_date,
            "",
            "Opening Balance",
            "",
            "",
            format_currency(opening_balance)
        ))
        
        # Initialize running balance and totals
        balance = opening_balance
        total_debit = 0
        total_credit = 0
        
        # Generate some random transactions
        while current_date <= end:
            # Skip some days
            if randint(0, 3) > 0:
                current_date += datetime.timedelta(days=randint(1, 7))
                continue
                
            if current_date > end:
                break
                
            # Decide transaction type
            if randint(0, 1) == 0:
                # Purchase (credit)
                amount = randint(1000, 10000)
                debit = 0
                credit = amount
                description = "Goods Purchased"
            else:
                # Payment (debit)
                amount = randint(1000, min(balance, 15000))
                debit = amount
                credit = 0
                description = "Payment Made"
                
            # Update running balance
            balance = balance - debit + credit
            
            # Update totals
            total_debit += debit
            total_credit += credit
            
            # Add to treeview
            self.ledger_tree.insert("", "end", values=(
                current_date.strftime("%Y-%m-%d"),
                random_ref(),
                description,
                format_currency(debit) if debit else "",
                format_currency(credit) if credit else "",
                format_currency(balance)
            ))
            
            transactions.append((
                current_date.strftime("%Y-%m-%d"),
                random_ref(),
                description,
                debit,
                credit
            ))
            
            # Move to next date
            current_date += datetime.timedelta(days=randint(1, 7))
        
        # Add closing balance row
        self.ledger_tree.insert("", "end", values=(
            end_date,
            "",
            "Closing Balance",
            "",
            "",
            format_currency(balance)
        ))
        
        # Update summary labels
        self.total_debit_label.config(text=format_currency(total_debit))
        self.total_credit_label.config(text=format_currency(total_credit))
        self.current_balance_label.config(text=format_currency(balance))
        
        # Set color for balance
        if balance > 0:
            self.current_balance_label.config(fg=COLORS["danger"])
        else:
            self.current_balance_label.config(fg=COLORS["text_primary"])
        
        # Store for export
        self.ledger_data = {
            "entity": supplier_name,
            "type": "Supplier",
            "start_date": start_date,
            "end_date": end_date,
            "opening_balance": opening_balance,
            "transactions": transactions,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "closing_balance": balance
        }
    
    def export_ledger(self):
        """Export ledger to Excel"""
        # Check if ledger has been loaded
        if not hasattr(self, 'ledger_data'):
            messagebox.showinfo("Export", "Please load a ledger first.")
            return
        
        # Prepare data for Excel
        data = {
            "Date": [],
            "Reference": [],
            "Description": [],
            "Debit": [],
            "Credit": [],
            "Balance": []
        }
        
        # Add opening balance row
        data["Date"].append(self.ledger_data["start_date"])
        data["Reference"].append("")
        data["Description"].append("Opening Balance")
        data["Debit"].append("")
        data["Credit"].append("")
        data["Balance"].append(self.ledger_data["opening_balance"])
        
        # Add transaction rows
        balance = self.ledger_data["opening_balance"]
        for transaction in self.ledger_data["transactions"]:
            date, reference, description, debit, credit = transaction
            balance = balance - debit + credit
            
            data["Date"].append(date)
            data["Reference"].append(reference)
            data["Description"].append(description)
            data["Debit"].append(debit if debit else "")
            data["Credit"].append(credit if credit else "")
            data["Balance"].append(balance)
        
        # Add closing balance row
        data["Date"].append(self.ledger_data["end_date"])
        data["Reference"].append("")
        data["Description"].append("Closing Balance")
        data["Debit"].append("")
        data["Credit"].append("")
        data["Balance"].append(self.ledger_data["closing_balance"])
        
        import pandas as pd
        df = pd.DataFrame(data)
        
        # Create filename
        entity_name = self.ledger_data["entity"].split("(")[0].strip()
        filename = f"{self.ledger_data['type']}_{entity_name}_Ledger.xlsx"
        
        # Ask user for save location
        import tkinter.filedialog as filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile=filename
        )
        
        if not file_path:
            return
        
        # Export to Excel
        if export_to_excel(df, file_path, f"{self.ledger_data['type']} Ledger"):
            messagebox.showinfo("Export", "Ledger exported successfully.")
        else:
            messagebox.showerror("Export Error", "Failed to export ledger.")
    
    def on_show(self):
        """Called when frame is shown"""
        # Update data in active tab
        current_tab = self.notebook.index(self.notebook.select())
        
        if current_tab == 0:  # Profit & Loss
            self.load_profit_loss()
        elif current_tab == 1:  # Cash Flow
            self.load_cash_flow()
        elif current_tab == 2:  # Expenses
            self.load_expenses()
        elif current_tab == 3:  # Ledgers
            self.load_ledger_entities()