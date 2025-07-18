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

# Ensure UTF-8 encoding for Chinese characters
import sys
if sys.version_info[0] >= 3:
    import codecs
    import io
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

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
                        "tax_amount": {"type": "number"},
                        "total_amount": {"type": "number"},
                        "currency": {"type": "string"},
                        "category": {"type": "string"},
                        "line_items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "description": {"type": "string"},
                                    "quantity": {"type": "number"},
                                    "unit_price": {"type": "number"},
                                    "amount": {"type": "number"}
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
        # Set default input folder to the invoice subdirectory in parent directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        self.input_folder = input_folder or os.path.join(parent_dir, "invoice")
        self.output_file = os.path.join(parent_dir, output_file)
        self.client = None
        self.processed_data = []
        
        # Initialize Excel manager
        self.excel_manager = ExcelManager(self.output_file)
        
    def initialize_api(self):
        """Initialize Anthropic API client"""
        # Load .env from the parent directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        env_path = os.path.join(parent_dir, ".env")
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
                                "text": "Extract all invoice information from this Traditional Chinese invoice including invoice number (發票號碼), vendor details (供應商名稱、地址、電話、電子郵件), receiver details (收件人名稱、地址、電話、電子郵件), invoice date (發票日期), due date (到期日), tax amount (稅額), total amount (總金額), currency (幣別), and line items with description (項目描述), quantity (數量), unit price (單價), and amount (金額). Set payment_status to 'Pending' by default. Use the extract_invoice_data tool to return structured data. Please ensure all extracted text maintains Traditional Chinese characters where applicable."
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
        
        failed_files = []
        
        for image_file in image_files:
            print(f"Processing: {image_file}")
            invoice_data = self.extract_invoice_data(image_file)
            
            if invoice_data:
                self.processed_data.append(invoice_data)
                print(f"✓ Successfully processed: {os.path.basename(image_file)}")
                
                # Move analyzed invoice to analyzed_invoices folder
                self.move_analyzed_invoice(image_file)
            else:
                print(f"✗ Failed to process: {os.path.basename(image_file)}")
                failed_files.append(image_file)
        
        # Retry failed files immediately
        if failed_files:
            print(f"\n🔄 Retrying {len(failed_files)} failed invoices immediately...")
            self.retry_failed_invoices(failed_files)
        else:
            print("\n🎉 All invoices processed successfully on first attempt!")
    
    def countdown_timer(self, seconds):
        """Display countdown timer"""
        import time
        for i in range(seconds, 0, -1):
            print(f"\r⏰ Retrying in {i} seconds...", end="", flush=True)
            time.sleep(1)
        print("\r⏰ Retrying now!" + " " * 20)  # Clear the line
    
    def retry_failed_invoices(self, failed_files):
        """Retry failed invoices with countdown delay"""
        if not failed_files:
            return
            
        # No delay - immediate retry
        print(f"\n🔄 Starting immediate retry for {len(failed_files)} failed invoices...")
        
        print(f"\n🔄 Starting retry for {len(failed_files)} failed invoices...")
        retry_success = 0
        still_failed = []
        
        for image_file in failed_files:
            print(f"Retrying: {os.path.basename(image_file)}")
            invoice_data = self.extract_invoice_data(image_file)
            
            if invoice_data:
                self.processed_data.append(invoice_data)
                print(f"✅ Retry successful: {os.path.basename(image_file)}")
                self.move_analyzed_invoice(image_file)
                retry_success += 1
            else:
                print(f"❌ Retry failed: {os.path.basename(image_file)}")
                still_failed.append(image_file)
        
        # Move permanently failed invoices to failed folder
        if still_failed:
            print(f"\n📁 Moving {len(still_failed)} permanently failed invoices to failed folder...")
            self.move_failed_invoices(still_failed)
        
        print(f"\n📊 Retry Results: {retry_success}/{len(failed_files)} invoices recovered")
    
    def move_failed_invoices(self, failed_files):
        """Move permanently failed invoices to failed folder"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(script_dir)
            failed_dir = os.path.join(parent_dir, "failed")
            
            # Create failed directory if it doesn't exist
            os.makedirs(failed_dir, exist_ok=True)
            
            for image_file in failed_files:
                filename = os.path.basename(image_file)
                destination = os.path.join(failed_dir, filename)
                
                # Move file to failed folder
                import shutil
                shutil.move(image_file, destination)
                print(f"❌ Moved to failed folder: {filename}")
                
        except Exception as e:
            print(f"Warning: Could not move failed files: {e}")
    
    def move_analyzed_invoice(self, image_file):
        """Move successfully analyzed invoice to analyzed_invoices folder"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(script_dir)
            analyzed_dir = os.path.join(parent_dir, "analyzed_invoices")
            
            # Create analyzed_invoices directory if it doesn't exist
            os.makedirs(analyzed_dir, exist_ok=True)
            
            # Get filename and create destination path
            filename = os.path.basename(image_file)
            destination = os.path.join(analyzed_dir, filename)
            
            # Move file to analyzed_invoices folder
            import shutil
            shutil.move(image_file, destination)
            print(f"📁 Moved to analyzed_invoices: {filename}")
            
        except Exception as e:
            print(f"Warning: Could not move file to analyzed_invoices: {e}")
    
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

    def export_to_excel(self, append_mode=True):
        """Export processed data to Excel using ExcelManager"""
        return self.excel_manager.export_to_excel(self.processed_data, append_mode)
    
    def read_excel_data(self):
        """Read existing Excel data using ExcelManager"""
        return self.excel_manager.read_excel_data()
    
    
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