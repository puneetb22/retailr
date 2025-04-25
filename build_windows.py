"""
Build script for Agritech POS System
Creates a Windows executable using PyInstaller
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def clean_build_dirs():
    """Clean build and dist directories"""
    print("Cleaning build directories...")
    
    dirs_to_clean = ["dist", "build"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  Removed {dir_name}/")

def create_logo():
    """Create a basic logo if it doesn't exist"""
    logo_path = Path("assets/logo.png")
    if not logo_path.exists():
        try:
            import tkinter as tk
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a simple logo
            print("Creating logo...")
            img = Image.new('RGBA', (256, 256), color=(78, 115, 223, 255))
            d = ImageDraw.Draw(img)
            
            try:
                # Try to use a nice font if available
                font = ImageFont.truetype("arial.ttf", 64)
            except:
                # Fallback to default font
                font = ImageFont.load_default()
            
            # Draw text
            d.text((128, 128), "POS", fill=(255, 255, 255, 255), font=font, anchor="mm")
            
            # Save the image
            os.makedirs(logo_path.parent, exist_ok=True)
            img.save(logo_path)
            print(f"  Created {logo_path}")
        except Exception as e:
            print(f"  Warning: Could not create logo: {e}")
            # Create an empty file as placeholder
            os.makedirs(logo_path.parent, exist_ok=True)
            with open(logo_path, 'wb') as f:
                f.write(b'')

def build_exe():
    """Build the executable using PyInstaller"""
    print("Building executable with PyInstaller...")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--name=AgritechPOS",
        "--windowed",
        "--icon=assets/logo.png",
        "--add-data=assets;assets",
        "--add-data=database;database",
        "--add-data=ui;ui",
        "--add-data=utils;utils", 
        "--add-data=docs;docs",
        # Include hidden imports for new modules
        "--hidden-import=pandas",
        "--hidden-import=matplotlib",
        "--hidden-import=xlsxwriter",
        "--hidden-import=tkinter",
        "--hidden-import=utils.cloud_sync", 
        "--hidden-import=utils.export",
        "--hidden-import=utils.helpers",
        "--hidden-import=ui.accounting",
        "--hidden-import=ui.cloud_sync",
        "main.py"
    ]
    
    # Run PyInstaller
    try:
        subprocess.run(cmd, check=True)
        print("  PyInstaller completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"  Error running PyInstaller: {e}")
        sys.exit(1)

def copy_extra_files():
    """Copy additional files to the dist directory"""
    print("Copying additional files...")
    
    # Create directories
    dist_dir = Path("dist/AgritechPOS")
    os.makedirs(dist_dir / "backups", exist_ok=True)
    os.makedirs(dist_dir / "invoices", exist_ok=True)
    os.makedirs(dist_dir / "exports", exist_ok=True)
    os.makedirs(dist_dir / "logs", exist_ok=True)
    
    # Create empty database file if it doesn't exist yet
    if not os.path.exists("pos_data.db"):
        try:
            import sqlite3
            conn = sqlite3.connect("pos_data.db")
            conn.close()
            print("  Created empty database file")
        except Exception as e:
            print(f"  Error creating database: {e}")
    
    # Copy database if it exists
    if os.path.exists("pos_data.db"):
        try:
            import shutil
            shutil.copy("pos_data.db", dist_dir)
            print("  Copied database file")
        except Exception as e:
            print(f"  Error copying database: {e}")
    
    # Create a README file
    with open(dist_dir / "README.txt", "w") as f:
        f.write("""Agritech POS System
===================

Thank you for installing the Agritech POS System!

This point-of-sale system is designed for agricultural product shops
in Maharashtra to manage inventory, process sales, track customer 
information, and handle accounting needs.

Features:
• Complete offline operation with cloud sync when available
• Sales and checkout with multiple payment methods
• Inventory management with batch tracking
• Customer database with purchase history
• Detailed reporting and analytics
• Accounting with profit & loss statements 
• Google Drive synchronization
• Data backup and recovery

To get started, simply double-click the AgritechPOS.exe file.

For detailed instructions, please see the user manual in the docs folder.
""")
    
    # Create sample product data file
    with open(dist_dir / "sample_products.csv", "w") as f:
        f.write("""product_code,product_name,description,category,unit,wholesale_price,retail_price,stock_quantity,tax_rate
SEED001,Wheat Seeds,High-yield wheat seeds,Seeds,kg,120,150,100,5
SEED002,Rice Seeds,Premium rice seeds,Seeds,kg,140,175,80,5
SEED003,Cotton Seeds,Bt cotton seeds,Seeds,packet,350,400,50,5
FERT001,Urea,Nitrogen fertilizer,Fertilizers,bag,250,300,30,18
FERT002,DAP,Diammonium phosphate,Fertilizers,bag,450,500,25,18
PEST001,Insecticide Spray,General purpose insecticide,Pesticides,bottle,180,220,40,18
PEST002,Fungicide,Anti-fungal spray,Pesticides,bottle,200,250,35,18
TOOL001,Hand Hoe,Steel hand hoe,Tools,piece,300,350,20,12
TOOL002,Sickle,Steel sickle,Tools,piece,120,150,15,12
EQUIP001,Sprayer,Manual backpack sprayer,Equipment,piece,1200,1500,10,18
""")
    
    # Create version information
    with open(dist_dir / "version.txt", "w") as f:
        f.write("Agritech POS System\nVersion: 1.0.0\nRelease Date: April 25, 2025\n")
    
    print("  Created necessary directories and files")

def create_docs():
    """Create documentation files"""
    print("Creating documentation...")
    
    docs_dir = Path("docs")
    os.makedirs(docs_dir, exist_ok=True)
    
    # Check if installation guide exists
    if os.path.exists(docs_dir / "installation_guide.md"):
        # Use existing MD file and create a text version
        try:
            with open(docs_dir / "installation_guide.md", "r") as src:
                content = src.read()
                
            # Create text version
            with open(docs_dir / "installation_guide.txt", "w") as dest:
                dest.write(content)
                
            print("  Using existing installation guide")
        except Exception as e:
            print(f"  Error converting installation guide: {e}")
            # Create a basic guide as fallback
            create_basic_installation_guide(docs_dir)
    else:
        # Create a basic guide
        create_basic_installation_guide(docs_dir)
    
    # Check if user manual exists
    if os.path.exists(docs_dir / "user_manual.md"):
        # Use existing MD file and create a text version
        try:
            with open(docs_dir / "user_manual.md", "r") as src:
                content = src.read()
                
            # Create text version
            with open(docs_dir / "user_manual.txt", "w") as dest:
                dest.write(content)
                
            print("  Using existing user manual")
        except Exception as e:
            print(f"  Error converting user manual: {e}")
            # Create a basic manual as fallback
            create_basic_user_manual(docs_dir)
    else:
        # Create a basic manual
        create_basic_user_manual(docs_dir)
        
def create_basic_installation_guide(docs_dir):
    """Create a basic installation guide if one doesn't exist"""
    with open(docs_dir / "installation_guide.txt", "w") as f:
        f.write("""Agritech POS System - Installation Guide
=======================================

System Requirements:
- Windows 7/8/10/11
- 4GB RAM minimum (8GB recommended)
- 500MB free disk space
- 1366x768 screen resolution or higher

Installation Steps:
1. Extract the AgritechPOS.zip file to a location of your choice
2. Open the extracted folder
3. Double-click AgritechPOS.exe to start the application

First-Time Setup:
1. The database will be created automatically on first run
2. Go to Settings to configure your shop information
3. Add your products through the Product Management screen
4. You're ready to start making sales!

Backup Recommendations:
- The system automatically maintains backups
- Manual backups can be created from the Backup & Restore screen
- We recommend backing up to an external drive periodically
- You can sync backups to Google Drive when internet is available

Troubleshooting:
- If the application won't start, ensure you have extracted all files
- If you encounter database errors, try using the Restore function
- For further assistance, contact support
""")
    print("  Created basic installation guide")

def create_basic_user_manual(docs_dir):
    """Create a basic user manual if one doesn't exist"""
    with open(docs_dir / "user_manual.txt", "w") as f:
        f.write("""Agritech POS System - User Manual
=================================

Quick Start Guide:
-----------------
1. Login: The system auto-logs in as the shopkeeper
2. Dashboard: Navigate using the buttons on the left sidebar
3. Sales: Process transactions by adding items to the cart
4. Products: Manage your inventory and price lists
5. Customers: Track customer information and purchase history
6. Reports: View sales data and analytics
7. Accounting: Track finances and generate profit/loss reports
8. Backup: Regularly backup your database
9. Cloud Sync: Sync data to Google Drive when internet is available

Module Details:
--------------

1. Dashboard
   - Overview of system status
   - Quick access to all modules
   - Shows alerts for low stock and expiring items

2. Sales
   - Add items to cart by double-clicking products
   - Change quantities and apply discounts
   - Select payment method (Cash, UPI, Split, Credit)
   - Suspend sales for later completion
   - Print invoices for customers

3. Product Management
   - Add, edit, and delete products
   - Set prices and tax rates
   - Track inventory levels
   - Manage product batches and expiry dates

4. Customer Management
   - Maintain customer database
   - Track purchase history
   - Manage credit sales
   - View and record payments

5. Reports
   - Sales summary by day, week, month
   - Product-wise sales analysis
   - Payment method breakdown
   - Tax/GST reporting
   - Export reports to Excel

6. Accounting
   - Profit & Loss statements
   - Cash flow management
   - Expense tracking
   - Customer and supplier ledgers

7. Backup & Restore
   - Create database backups
   - Restore from previous backups
   - Export backups to external storage
   - Import backups from external files

8. Cloud Sync
   - Sync backups to Google Drive
   - Background sync when internet is available
   - Manage sync settings

9. Settings
   - Configure shop information
   - Set invoice preferences
   - Adjust system parameters
   - Manage alert thresholds

Keyboard Shortcuts:
------------------
F1 - Help
F5 - Refresh data
Ctrl+S - Save current work
Ctrl+P - Print current view
Esc - Cancel current operation

For additional assistance, refer to the detailed documentation.
""")
    
    print("  Created installation guide and user manual")

def create_installer():
    """Create a zip file for distribution"""
    print("Creating installer package...")
    
    try:
        dist_dir = "dist"
        output_zip = "AgritechPOS_Setup.zip"
        
        # Copy docs to dist directory
        docs_src = Path("docs")
        docs_dest = Path(dist_dir) / "AgritechPOS" / "docs"
        os.makedirs(docs_dest, exist_ok=True)
        
        for file in docs_src.glob("*"):
            shutil.copy(file, docs_dest)
        
        # Create zip archive
        shutil.make_archive("AgritechPOS_Setup", 'zip', dist_dir, "AgritechPOS")
        print(f"  Created {output_zip}")
        
    except Exception as e:
        print(f"  Error creating installer: {e}")

def main():
    """Main build function"""
    print("Building Agritech POS System for Windows...")
    
    # Clean previous builds
    clean_build_dirs()
    
    # Create logo if needed
    create_logo()
    
    # Build executable
    build_exe()
    
    # Copy additional files
    copy_extra_files()
    
    # Create documentation
    create_docs()
    
    # Create installer package
    create_installer()
    
    print("\nBuild completed successfully!")
    print("The installer package is available at: AgritechPOS_Setup.zip")

if __name__ == "__main__":
    main()