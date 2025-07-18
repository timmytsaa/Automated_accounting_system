import os
import pandas as pd
from datetime import datetime

# Ensure UTF-8 encoding for Chinese characters
import sys
if sys.version_info[0] >= 3:
    import codecs
    import io
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

class ExcelManager:
    """Handles Excel file operations for invoice data"""
    
    def __init__(self, output_file="invoice_data.xlsx"):
        self.output_file = output_file
        
    def flatten_invoice_data(self, invoice_data_list):
        """Flatten invoice data for Excel export"""
        excel_data = []
        
        for invoice in invoice_data_list:
            base_row = {
                "Invoice Number": invoice.get("invoice_number", ""),
                "Vendor Name": invoice.get("vendor_name", ""),
                "Vendor Address": invoice.get("vendor_address", ""),
                "Vendor Phone": invoice.get("vendor_phone", ""),
                "Vendor Email": invoice.get("vendor_email", ""),
                "Receiver Name": invoice.get("receiver_name", ""),
                "Receiver Address": invoice.get("receiver_address", ""),
                "Receiver Phone": invoice.get("receiver_phone", ""),
                "Receiver Email": invoice.get("receiver_email", ""),
                "Invoice Date": invoice.get("invoice_date", ""),
                "Due Date": invoice.get("due_date", ""),
                "Tax Amount": invoice.get("tax_amount", 0),
                "Total Amount": invoice.get("total_amount", 0),
                "Currency": invoice.get("currency", "USD"),
                "Category": invoice.get("category", ""),
                "Processing Date": invoice.get("processing_date", ""),
                "Source File": invoice.get("source_file", ""),
            }
            
            # Add line items if they exist
            line_items = invoice.get("line_items", [])
            if line_items:
                for item in line_items:
                    row = base_row.copy()
                    row["Item Description"] = item.get("description", "")
                    row["Quantity"] = item.get("quantity", 0)
                    row["Unit Price"] = item.get("unit_price", 0)
                    row["Amount"] = item.get("amount", 0)
                    excel_data.append(row)
            else:
                excel_data.append(base_row)
                
        return excel_data
    
    def export_to_excel(self, invoice_data_list, append_mode=True):
        """Export processed data to Excel, with option to append to existing file"""
        if not invoice_data_list:
            print("No data to export")
            return False
            
        # Flatten data for Excel export
        excel_data = self.flatten_invoice_data(invoice_data_list)
        
        # Create DataFrame with new data
        new_df = pd.DataFrame(excel_data)
        
        # Check if Excel file already exists and append mode is enabled
        if append_mode and os.path.exists(self.output_file):
            try:
                # Read existing data
                existing_df = pd.read_excel(self.output_file)
                
                # Get existing invoice numbers to avoid duplicates
                existing_invoice_numbers = set(existing_df["Invoice Number"].dropna().astype(str))
                
                # Filter out duplicates from new data
                new_df_filtered = new_df[~new_df["Invoice Number"].astype(str).isin(existing_invoice_numbers)]
                
                if len(new_df_filtered) > 0:
                    # Append new data to existing data
                    combined_df = pd.concat([existing_df, new_df_filtered], ignore_index=True)
                    combined_df.to_excel(self.output_file, index=False)
                    print(f"✓ Added {len(new_df_filtered)} new invoices to existing file: {self.output_file}")
                    return True
                else:
                    print("No new invoices to add (all invoices already exist in the file)")
                    return False
                    
            except Exception as e:
                print(f"Error reading existing file, creating new one: {e}")
                new_df.to_excel(self.output_file, index=False)
                print(f"✓ Data exported to new file: {self.output_file}")
                return True
        else:
            # Create new file or overwrite existing
            new_df.to_excel(self.output_file, index=False)
            print(f"✓ Data exported to file: {self.output_file}")
            return True
    
    def read_excel_data(self):
        """Read existing Excel data"""
        if os.path.exists(self.output_file):
            try:
                df = pd.read_excel(self.output_file)
                return df
            except Exception as e:
                print(f"Error reading Excel file: {e}")
                return None
        else:
            print("Excel file does not exist")
            return None
    
    
    def get_invoice_summary(self):
        """Get summary of invoices in the Excel file"""
        df = self.read_excel_data()
        if df is None:
            return None
            
        summary = {
            "total_invoices": len(df),
            "total_amount": df["Total Amount"].sum(),
            "pending_payments": len(df[df["Payment Status"] == "Pending"]),
            "paid_invoices": len(df[df["Payment Status"] == "Paid"]),
            "overdue_invoices": len(df[df["Payment Status"] == "Overdue"]),
            "currencies": df["Currency"].value_counts().to_dict(),
            "vendors": df["Vendor Name"].value_counts().to_dict()
        }
        
        return summary
    
    def filter_invoices(self, filter_criteria):
        """Filter invoices based on criteria"""
        df = self.read_excel_data()
        if df is None:
            return None
            
        filtered_df = df.copy()
        
        # Apply filters
        if "vendor_name" in filter_criteria:
            filtered_df = filtered_df[filtered_df["Vendor Name"].str.contains(filter_criteria["vendor_name"], case=False, na=False)]
        
        if "payment_status" in filter_criteria:
            filtered_df = filtered_df[filtered_df["Payment Status"] == filter_criteria["payment_status"]]
        
        if "date_range" in filter_criteria:
            start_date, end_date = filter_criteria["date_range"]
            filtered_df = filtered_df[(filtered_df["Invoice Date"] >= start_date) & (filtered_df["Invoice Date"] <= end_date)]
        
        if "currency" in filter_criteria:
            filtered_df = filtered_df[filtered_df["Currency"] == filter_criteria["currency"]]
        
        return filtered_df
    
    def export_filtered_data(self, filter_criteria, output_file=None):
        """Export filtered data to a new Excel file"""
        filtered_df = self.filter_invoices(filter_criteria)
        if filtered_df is None or len(filtered_df) == 0:
            print("No data matches the filter criteria")
            return False
        
        if output_file is None:
            output_file = f"filtered_invoices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        filtered_df.to_excel(output_file, index=False)
        print(f"✓ Filtered data exported to: {output_file}")
        return True