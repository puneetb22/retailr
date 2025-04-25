# Agritech POS System - Developer Guide

This guide is for developers who want to modify or extend the Agritech POS System. 

## Project Structure

The application follows a modular architecture with the following key components:

```
agritech-pos/
├── assets/           # Style definitions, images, and static resources
├── database/         # Database handling and schema definitions
├── docs/             # Documentation files
├── ui/               # User interface modules organized by functionality
├── utils/            # Utility functions and helper classes
├── main.py           # Application entry point
└── build_windows.py  # Build script for creating the Windows executable
```

## Environment Setup

### Development Requirements

- Python 3.8 or newer
- Required packages (see requirements section below)
- SQLite database (included in Python standard library)

### Required Packages

The following Python packages are required for development:

```
matplotlib
pandas
pillow
pyinstaller
xlsxwriter
```

Install them using pip:

```bash
pip install matplotlib pandas pillow pyinstaller xlsxwriter
```

## Module Overview

### Main Application (main.py)

The entry point of the application that initializes the database connection and sets up the tkinter UI.

### Database (database/)

- **db_handler.py**: Database connection manager with methods for common operations
- **schema.py**: Database schema definitions and initial data setup

### User Interface (ui/)

Each module handles a specific functional area of the application:

- **login.py**: Auto-login functionality
- **dashboard.py**: Main application dashboard and navigation
- **sales.py**: Sales and checkout processing
- **product_management.py**: Product inventory management
- **customer_management.py**: Customer database and history
- **inventory_management.py**: Advanced inventory with batch tracking
- **accounting.py**: Financial tracking with P&L and cash flow
- **reports.py**: Business analytics and reporting
- **backup.py**: Data backup and restore functionality
- **cloud_sync.py**: Google Drive synchronization
- **settings.py**: Application configuration

### Utilities (utils/)

- **helpers.py**: General helper functions
- **export.py**: Data export functionality
- **cloud_sync.py**: Cloud synchronization backend

## Database Schema

The application uses SQLite with the following main tables:

- **products**: Product catalog information
- **inventory**: Stock levels and batch tracking
- **customers**: Customer database
- **invoices**: Sales transaction records
- **invoice_items**: Line items for each invoice
- **expenses**: Business expense tracking
- **settings**: Application configuration

## Adding New Features

### Creating a New Module

1. Create a new file in the ui/ directory
2. Import the necessary tkinter components and utility functions
3. Create a class that inherits from tk.Frame
4. Add the new module to the dashboard navigation in ui/dashboard.py

Example:

```python
import tkinter as tk
from tkinter import ttk, messagebox
from assets.styles import COLORS, FONTS, STYLES

class NewFeatureFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=COLORS["bg_primary"])
        self.controller = controller
        
        # Create UI components here
        
    def on_show(self):
        # This is called when the frame is shown
        pass
```

### Extending Database Schema

To add new tables or modify existing ones:

1. Update the schema.py file with your new table definitions
2. Implement any migration logic needed for existing databases
3. Update the relevant UI modules to use the new schema

## Building for Distribution

The project includes a build script (build_windows.py) that packages the application for Windows using PyInstaller.

To build the executable:

1. Make sure PyInstaller is installed (`pip install pyinstaller`)
2. Run the build script: `python build_windows.py`
3. The output will be created in the dist/ directory
4. A ZIP installer will be created as AgritechPOS_Setup.zip

## Troubleshooting Development Issues

### Database Schema Changes

If you make changes to the database schema, you may need to manually handle migration for existing databases. The application doesn't currently have an automated migration system.

### UI Layout Issues

Tkinter layout can be tricky. If you're having issues:

1. Use `pack()` for simple vertical or horizontal layouts
2. Use `grid()` for more complex layouts
3. Don't mix `pack()` and `grid()` in the same container
4. Use `frame.pack_propagate(False)` to maintain a fixed frame size

### PyInstaller Issues

If you encounter issues with PyInstaller:

1. Check that all imports are explicit (PyInstaller can't detect dynamic imports)
2. Add hidden imports in the build script for any modules not detected automatically
3. Ensure all data files are properly specified in the build script

## Contributing

When contributing to the project, please follow these practices:

1. Maintain the modular architecture
2. Follow the existing code style
3. Document new functions and classes
4. Add appropriate error handling
5. Test thoroughly before submitting changes