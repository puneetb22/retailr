"""
Export utilities for POS system
Functions for exporting data to Excel and other formats
"""

import os
import datetime
import xlsxwriter

def export_to_excel(data_frame, file_path, sheet_name="Sheet1"):
    """
    Export a pandas DataFrame to Excel
    
    Args:
        data_frame: Pandas DataFrame to export
        file_path: Path to save the Excel file
        sheet_name: Name of the worksheet
        
    Returns:
        True if export was successful, False otherwise
    """
    try:
        # Create a writer
        writer = data_frame.to_excel(file_path, sheet_name=sheet_name, index=False, engine='xlsxwriter')
        
        # Close the Pandas Excel writer and output the Excel file
        if hasattr(writer, 'close'):
            writer.close()
            
        return True
    except Exception as e:
        print(f"Error exporting to Excel: {e}")
        return False
        
def export_data_to_excel(data, columns, file_path, sheet_name="Sheet1"):
    """
    Export data directly to Excel without pandas
    
    Args:
        data: List of data rows to export
        columns: List of column names
        file_path: Path to save the Excel file
        sheet_name: Name of the worksheet
        
    Returns:
        True if export was successful, False otherwise
    """
    try:
        # Create a workbook and add a worksheet
        workbook = xlsxwriter.Workbook(file_path)
        worksheet = workbook.add_worksheet(sheet_name)
        
        # Add a header format
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D3D3D3',
            'border': 1
        })
        
        # Write the headers
        for col_num, column in enumerate(columns):
            worksheet.write(0, col_num, column, header_format)
        
        # Write the data
        for row_num, row in enumerate(data):
            for col_num, cell_value in enumerate(row):
                worksheet.write(row_num + 1, col_num, cell_value)
                
        # Auto-adjust column width
        for col_num, column in enumerate(columns):
            worksheet.set_column(col_num, col_num, max(len(column) + 2, 12))
        
        workbook.close()
        return True
        
    except Exception as e:
        print(f"Error exporting to Excel: {e}")
        return False

def export_query_to_excel(db, query, params, file_path, sheet_name="Sheet1", column_names=None):
    """
    Export SQL query results directly to Excel
    
    Args:
        db: Database handler object
        query: SQL query to execute
        params: Parameters for the query
        file_path: Path to save the Excel file
        sheet_name: Name of the worksheet
        column_names: Optional list of column names (if None, first row used as headers)
        
    Returns:
        True if export was successful, False otherwise
    """
    try:
        # Execute query and get results
        results = db.fetchall(query, params)
        
        if not results:
            print("No data to export")
            return False
            
        # Get column names from cursor description if not provided
        if column_names is None:
            # For SQLite, need to get column names from cursor description
            # This implementation might need to be adjusted based on your db_handler
            cursor_description = db.execute(query, params).description
            column_names = [desc[0] for desc in cursor_description]
        
        # Create a workbook and add a worksheet
        workbook = xlsxwriter.Workbook(file_path)
        worksheet = workbook.add_worksheet(sheet_name)
        
        # Add a header format
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D3D3D3',
            'border': 1
        })
        
        # Write the headers
        for col_num, column in enumerate(column_names):
            worksheet.write(0, col_num, column, header_format)
        
        # Write the data
        for row_num, row in enumerate(results):
            for col_num, cell_value in enumerate(row):
                worksheet.write(row_num + 1, col_num, cell_value)
                
        # Auto-adjust column width
        for col_num, column in enumerate(column_names):
            worksheet.set_column(col_num, col_num, max(len(column) + 2, 12))
        
        workbook.close()
        return True
        
    except Exception as e:
        print(f"Error exporting to Excel: {e}")
        return False