# Agritech POS System - Installation Guide

This guide will walk you through the process of installing and setting up the Agritech POS System on a Windows computer.

## System Requirements

Before installation, make sure your computer meets these minimum requirements:

- **Operating System**: Windows 7, 8, 10, or 11
- **Processor**: 1 GHz or faster processor
- **Memory**: 4 GB RAM minimum (8 GB recommended)
- **Disk Space**: At least 500 MB of free disk space
- **Display**: 1366 x 768 screen resolution or higher
- **Printer**: Optional, for printing invoices and reports

## Installation Steps

### Method 1: Standard Installation (Recommended)

1. **Download the Installation Package**
   - Locate the `AgritechPOS_Setup.zip` file provided to you
   - Save it to a location on your computer where you can easily find it (e.g., Desktop)

2. **Extract the Files**
   - Right-click on the zip file
   - Select "Extract All..."
   - Choose a destination folder or use the default suggestion
   - Click "Extract"

3. **Run the Application**
   - Open the extracted folder
   - Double-click on `AgritechPOS.exe` to start the application
   - On first run, the application will create a new database and other necessary files

4. **Create a Shortcut (Optional)**
   - Right-click on `AgritechPOS.exe`
   - Select "Create shortcut"
   - Move the shortcut to your desktop or taskbar for easy access

### Method 2: Portable Installation

If you want to run the application from a USB drive or without installing:

1. **Extract to Portable Location**
   - Extract the `AgritechPOS_Setup.zip` to a USB drive or folder of your choice
   - Make sure the location is writable (the application needs to create and update its database file)

2. **Run Directly**
   - Navigate to the extracted folder
   - Double-click on `AgritechPOS.exe` to start

3. **Important Note**
   - The database will be created in the same folder as the application
   - Make regular backups if using the portable option

## First-Time Setup

When you first start the application, follow these steps to configure it:

1. **Auto-Login**
   - The system will automatically log you in as the shopkeeper
   - No additional authentication is required for this version

2. **Configure Shop Information**
   - Go to Settings (⚙️ icon in the menu)
   - Enter your shop details:
     - Shop name
     - Address
     - Contact information
     - GST number (if applicable)
   - This information will appear on invoices and reports

3. **Set System Preferences**
   - Still in Settings, configure:
     - Invoice numbering format
     - Default tax rates
     - Low stock alert thresholds
     - Backup reminder frequency

4. **Add Products**
   - Navigate to the Products module
   - Add your initial inventory of products, including:
     - Product name, code, and description
     - Purchase and selling prices
     - Initial stock quantity
     - Categories (if needed)

5. **Create Your First Backup**
   - Go to the Backup & Restore module
   - Click "Create New Backup"
   - This creates a baseline backup that you can restore to if needed

## Updating the Software

To update to a newer version of the Agritech POS System:

1. **Backup Your Data**
   - Create a backup using the built-in Backup & Restore function
   - Additionally, copy your `pos_data.db` file to a safe location as a precaution

2. **Install New Version**
   - Extract the new version to a different folder than your current installation
   - Copy your `pos_data.db` file from the old installation to the new folder
   - Start the new version of the application

## Troubleshooting Installation Issues

### Application Doesn't Start

- **Check Extracted Files**: Make sure all files were properly extracted
- **Windows Defender/Antivirus**: Temporarily disable or add an exception for the application
- **Administrator Rights**: Try running the application as Administrator
- **Missing DLLs**: Ensure you have the latest Visual C++ Redistributable installed from Microsoft

### Database Creation Fails

- **Disk Permissions**: Ensure you have write permissions to the folder
- **Disk Space**: Verify you have sufficient free disk space
- **Corrupt ZIP File**: Try re-downloading the installation package

### Graphics or Display Issues

- **Screen Resolution**: Set your display to at least 1366 x 768 resolution
- **Display Scaling**: Try setting Windows display scaling to 100%
- **Update Graphics Drivers**: Ensure your graphics drivers are up to date

## Getting Help

If you encounter problems during installation or setup:

- **Email Support**: support@agritech.example.com
- **Phone Support**: +91 1234567890
- **Business Hours**: Monday to Saturday, 9 AM to 6 PM IST