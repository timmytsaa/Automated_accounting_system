import os
import json
import glob
from datetime import datetime
from PIL import Image
from dotenv import load_dotenv
from base64 import b64encode
from anthropic import Anthropic
import pandas as pd
from excel_manager import ExcelManager

EXTENSION_TO_MEDIA_TYPE = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp",
}

TOOLS = [
    {
        "name": "extract_invoice_data",
        "description": "Extract structured invoice data",
        "input_schema": {
            "type": "object",
            "properties": {
                "invoice_data": {
                    "type": "object",
                    "properties": {
                        "invoice_number": {"type": "string"},
                        "vendor_name": {"type": "string"},
                        "vendor_address": {"type": "string"},
                        "vendor_phone": {"type": "string"},
                        "vendor_email": {"type": "string"},
                        "receiver_name": {"type": "string"},
                        "receiver_address": {"type": "string"},
                        "receiver_phone": {"type": "string"},
                        "receiver_email": {"type": "string"},
                        "invoice_date": {"type": "string"},
                        "due_date": {"type": "string"},
                        "subtotal": {"type": "number"},
                        "tax_amount": {"type": "number"},
                        "total_amount": {"type": "number"},
                        "currency": {"type": "string"},
                        "payment_status": {"type": "string"},
                        "payment_date": {"type": "string"},
                        "category": {"type": "string"},
                        "line_items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "description": {"type": "string"},
                                    "quantity": {"type": "number"},
                                    "unit_price": {"type": "number"},
                                    "total": {"type": "number"}
                                }
                            }
                        }
                    },
                    "required": ["invoice_number", "vendor_name", "total_amount"]
                }
            },
            "required": ["invoice_data"]
        }
    }
]

class InvoiceProcessor:
    def __init__(self, input_folder=None, output_file="invoice_data.xlsx"):
        # Set default input folder to the invoice subdirectory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.input_folder = input_folder or os.path.join(script_dir, "invoice")
        self.output_file = os.path.join(script_dir, output_file)
        self.client = None
        self.processed_data = []
        
        # Initialize Excel manager
        self.excel_manager = ExcelManager(self.output_file)
        
    def initialize_api(self):
        """Initialize Anthropic API client"""
        # Load .env from the same directory as this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        env_path = os.path.join(script_dir, ".env")
        load_dotenv(env_path, override=True)
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        self.client = Anthropic(api_key=api_key)
        
    def encode_image(self, image_path):
        """Encode image to base64"""
        with open(image_path, 'rb') as image_file:
            return b64encode(image_file.read()).decode()
    
    def get_media_type(self, file_path):
        """Get media type from file extension"""
        extension = file_path.split('.')[-1].lower()
        return EXTENSION_TO_MEDIA_TYPE.get(extension, "image/jpeg")
    
    def extract_invoice_data(self, image_path):
        """Extract structured data from invoice image"""
        try:
            encoded_image = self.encode_image(image_path)
            media_type = self.get_media_type(image_path)
            
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.1,
                tools=TOOLS,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": encoded_image
                                }
                            },
                            {
                                "type": "text",
                                "text": "Extract all invoice information including invoice number, vendor details (name, address, phone, email), receiver details (name, address, phone, email), invoice date, due date, amounts, currency, and line items. Set payment_status to 'Pending' by default. Use the extract_invoice_data tool to return structured data."
                            }
                        ]
                    }
                ]
            )
            
            # Extract tool use result
            if message.content and len(message.content) > 0:
                for content in message.content:
                    if content.type == "tool_use" and content.name == "extract_invoice_data":
                        invoice_data = content.input["invoice_data"]
                        # Add metadata
                        invoice_data["processing_date"] = datetime.now().isoformat()
                        invoice_data["source_file"] = os.path.basename(image_path)
                        invoice_data["confidence_score"] = 0.95  # Default confidence
                        return invoice_data
            
            return None
            
        except Exception as e:
            print(f"Error processing {image_path}: {str(e)}")
            return None
    
    def process_all_invoices(self):
        """Process all invoice images in the input folder"""
        if not self.client:
            self.initialize_api()
            
        # Get all image files
        image_patterns = ['*.jpg', '*.jpeg', '*.png', '*.webp']
        image_files = []
        
        for pattern in image_patterns:
            image_files.extend(glob.glob(os.path.join(self.input_folder, pattern)))
            image_files.extend(glob.glob(os.path.join(self.input_folder, pattern.upper())))
        
        print(f"Found {len(image_files)} invoice images to process")
        
        for image_file in image_files:
            print(f"Processing: {image_file}")
            invoice_data = self.extract_invoice_data(image_file)
            
            if invoice_data:
                self.processed_data.append(invoice_data)
                print(f"✓ Successfully processed: {os.path.basename(image_file)}")
            else:
                print(f"✗ Failed to process: {os.path.basename(image_file)}")
    
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
                "Subtotal": invoice.get("subtotal", 0),
                "Tax Amount": invoice.get("tax_amount", 0),
                "Total Amount": invoice.get("total_amount", 0),
                "Currency": invoice.get("currency", "USD"),
                "Payment Status": invoice.get("payment_status", "Pending"),
                "Payment Date": invoice.get("payment_date", ""),
                "Category": invoice.get("category", ""),
                "Processing Date": invoice.get("processing_date", ""),
                "Source File": invoice.get("source_file", ""),
                "Confidence Score": invoice.get("confidence_score", 0)
            }
            
            # Add line items if they exist
            line_items = invoice.get("line_items", [])
            if line_items:
                for item in line_items:
                    row = base_row.copy()
                    row["Item Description"] = item.get("description", "")
                    row["Quantity"] = item.get("quantity", 0)
                    row["Unit Price"] = item.get("unit_price", 0)
                    row["Item Total"] = item.get("total", 0)
                    excel_data.append(row)
            else:
                excel_data.append(base_row)
                
        return excel_data

    def export_to_excel(self, append_mode=True):
        """Export processed data to Excel using ExcelManager"""
        return self.excel_manager.export_to_excel(self.processed_data, append_mode)
    
    def read_excel_data(self):
        """Read existing Excel data using ExcelManager"""
        return self.excel_manager.read_excel_data()
    
    def update_payment_status(self, invoice_number, payment_status, payment_date=None):
        """Update payment status using ExcelManager"""
        return self.excel_manager.update_payment_status(invoice_number, payment_status, payment_date)
    
    def get_invoice_summary(self):
        """Get invoice summary using ExcelManager"""
        return self.excel_manager.get_invoice_summary()
    
    def run(self):
        """Run the complete invoice processing workflow"""
        print("Starting automated invoice processing...")
        self.process_all_invoices()
        self.export_to_excel()
        print(f"Processing complete. {len(self.processed_data)} invoices processed.")

if __name__ == "__main__":
    processor = InvoiceProcessor()
    processor.run()