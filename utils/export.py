"""
Export utilities for POS system
Handles exporting data to external formats like Excel
"""

import pandas as pd
import os

def export_to_excel(dataframe, filename, sheet_name='Sheet1'):
    """
    Export pandas DataFrame to Excel file
    
    Args:
        dataframe: Pandas DataFrame to export
        filename: Target filename (full path)
        sheet_name: Name of sheet in Excel file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Make sure directories exist
        os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
        
        # Create Excel writer
        writer = pd.ExcelWriter(filename, engine='xlsxwriter')
        
        # Convert dataframe to Excel
        dataframe.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Get workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]
        
        # Add formatting
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4e73df',
            'font_color': 'white',
            'border': 1
        })
        
        # Format headers
        for col_num, value in enumerate(dataframe.columns.values):
            worksheet.write(0, col_num, value, header_format)
            
        # Auto-fit columns
        for i, col in enumerate(dataframe.columns):
            column_width = max(dataframe[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, column_width)
        
        # Save workbook
        writer.close()
        
        return True
    except Exception as e:
        print(f"Export error: {e}")
        return False