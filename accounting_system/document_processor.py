import os
import time
import glob
import shutil
from datetime import datetime
from pathlib import Path
from PIL import Image
import fitz  # PyMuPDF for PDF processing
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from automated_invoice_processor import InvoiceProcessor

class DocumentProcessor:
    """Enhanced document processor with multi-document capabilities"""
    
    def __init__(self, watch_folder="./watch", processed_folder="./processed", 
                 failed_folder="./failed", output_file="invoice_data.xlsx"):
        self.watch_folder = watch_folder
        self.processed_folder = processed_folder
        self.failed_folder = failed_folder
        self.output_file = output_file
        
        # Create directories if they don't exist
        os.makedirs(watch_folder, exist_ok=True)
        os.makedirs(processed_folder, exist_ok=True)
        os.makedirs(failed_folder, exist_ok=True)
        
        # Initialize invoice processor
        self.invoice_processor = InvoiceProcessor(output_file=output_file)
        
        # Supported file types
        self.supported_image_types = ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff']
        self.supported_pdf_types = ['.pdf']
        self.supported_types = self.supported_image_types + self.supported_pdf_types
        
    def is_supported_file(self, file_path):
        """Check if file is supported"""
        return Path(file_path).suffix.lower() in self.supported_types
    
    def is_pdf(self, file_path):
        """Check if file is PDF"""
        return Path(file_path).suffix.lower() == '.pdf'
    
    def convert_pdf_to_images(self, pdf_path):
        """Convert PDF pages to images"""
        try:
            doc = fitz.open(pdf_path)
            images = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Convert page to image
                mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
                pix = page.get_pixmap(matrix=mat)
                
                # Save as temporary image
                temp_image_path = f"temp_page_{page_num}_{int(time.time())}.png"
                pix.save(temp_image_path)
                images.append(temp_image_path)
            
            doc.close()
            return images
            
        except Exception as e:
            print(f"Error converting PDF {pdf_path}: {e}")
            return []
    
    def process_single_document(self, file_path):
        """Process a single document (image or PDF)"""
        try:
            print(f"Processing document: {os.path.basename(file_path)}")
            
            if self.is_pdf(file_path):
                return self.process_pdf_document(file_path)
            else:
                return self.process_image_document(file_path)
                
        except Exception as e:
            print(f"Error processing document {file_path}: {e}")
            return False
    
    def process_pdf_document(self, pdf_path):
        """Process PDF document"""
        try:
            # Convert PDF to images
            temp_images = self.convert_pdf_to_images(pdf_path)
            
            if not temp_images:
                print(f"Failed to convert PDF: {pdf_path}")
                return False
            
            # Process each page
            processed_data = []
            for i, temp_image in enumerate(temp_images):
                print(f"Processing page {i+1}/{len(temp_images)}")
                
                # Extract data from image
                invoice_data = self.invoice_processor.extract_invoice_data(temp_image)
                
                if invoice_data:
                    # Add page information
                    invoice_data['source_file'] = f"{os.path.basename(pdf_path)}_page_{i+1}"
                    invoice_data['page_number'] = i + 1
                    invoice_data['total_pages'] = len(temp_images)
                    processed_data.append(invoice_data)
                
                # Clean up temp image
                os.remove(temp_image)
            
            # Add processed data to invoice processor
            self.invoice_processor.processed_data.extend(processed_data)
            
            print(f"Successfully processed {len(processed_data)} pages from PDF")
            return len(processed_data) > 0
            
        except Exception as e:
            print(f"Error processing PDF {pdf_path}: {e}")
            return False
    
    def process_image_document(self, image_path):
        """Process image document"""
        try:
            # Extract data from image
            invoice_data = self.invoice_processor.extract_invoice_data(image_path)
            
            if invoice_data:
                self.invoice_processor.processed_data.append(invoice_data)
                print(f"Successfully processed image: {os.path.basename(image_path)}")
                return True
            else:
                print(f"Failed to extract data from: {os.path.basename(image_path)}")
                return False
                
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            return False
    
    def classify_document(self, file_path):
        """Classify document type based on extracted data"""
        try:
            # For now, we'll classify based on content after extraction
            # This could be expanded to use ML classification
            
            # Basic classification rules
            filename = os.path.basename(file_path).lower()
            
            if any(keyword in filename for keyword in ['invoice', '發票', '帳單']):
                return 'invoice'
            elif any(keyword in filename for keyword in ['receipt', '收據', '收據']):
                return 'receipt'
            elif any(keyword in filename for keyword in ['contract', '合約', '契約']):
                return 'contract'
            elif any(keyword in filename for keyword in ['statement', '對帳單']):
                return 'statement'
            else:
                return 'unknown'
                
        except Exception as e:
            print(f"Error classifying document {file_path}: {e}")
            return 'unknown'
    
    def move_processed_file(self, file_path, success=True):
        """Move file to processed or failed folder"""
        try:
            filename = os.path.basename(file_path)
            
            if success:
                # Move to processed folder with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_name = f"{timestamp}_{filename}"
                destination = os.path.join(self.processed_folder, new_name)
            else:
                # Move to failed folder
                destination = os.path.join(self.failed_folder, filename)
            
            shutil.move(file_path, destination)
            print(f"Moved {filename} to {destination}")
            
        except Exception as e:
            print(f"Error moving file {file_path}: {e}")
    
    def process_batch(self, folder_path=None):
        """Process all documents in a folder"""
        if folder_path is None:
            folder_path = self.watch_folder
            
        print(f"Processing batch from folder: {folder_path}")
        
        # Initialize API once
        self.invoice_processor.initialize_api()
        
        # Get all supported files
        all_files = []
        for file_type in self.supported_types:
            pattern = os.path.join(folder_path, f"*{file_type}")
            all_files.extend(glob.glob(pattern))
            # Also check uppercase extensions
            pattern_upper = os.path.join(folder_path, f"*{file_type.upper()}")
            all_files.extend(glob.glob(pattern_upper))
        
        print(f"Found {len(all_files)} documents to process")
        
        processed_count = 0
        failed_count = 0
        
        for file_path in all_files:
            if self.is_supported_file(file_path):
                # Classify document
                doc_type = self.classify_document(file_path)
                print(f"Document type: {doc_type}")
                
                # Process document
                success = self.process_single_document(file_path)
                
                if success:
                    processed_count += 1
                    self.move_processed_file(file_path, success=True)
                else:
                    failed_count += 1
                    self.move_processed_file(file_path, success=False)
        
        # Export to Excel if any documents were processed
        if processed_count > 0:
            self.invoice_processor.export_to_excel()
            print(f"✓ Exported {processed_count} documents to Excel")
        
        print(f"Batch processing complete:")
        print(f"  - Processed: {processed_count} documents")
        print(f"  - Failed: {failed_count} documents")
        
        return processed_count, failed_count
    
    def get_processing_stats(self):
        """Get processing statistics"""
        stats = {
            'watch_folder': self.watch_folder,
            'processed_folder': self.processed_folder,
            'failed_folder': self.failed_folder,
            'supported_types': self.supported_types,
            'pending_files': len([f for f in os.listdir(self.watch_folder) 
                                if self.is_supported_file(os.path.join(self.watch_folder, f))]),
            'processed_files': len(os.listdir(self.processed_folder)),
            'failed_files': len(os.listdir(self.failed_folder))
        }
        return stats

class DocumentWatcher(FileSystemEventHandler):
    """File system watcher for automatic document processing"""
    
    def __init__(self, document_processor):
        self.document_processor = document_processor
        self.processing_delay = 2  # seconds to wait before processing
        
    def on_created(self, event):
        """Handle file creation events"""
        if not event.is_directory:
            file_path = event.src_path
            
            if self.document_processor.is_supported_file(file_path):
                print(f"New document detected: {os.path.basename(file_path)}")
                
                # Wait a bit to ensure file is fully written
                time.sleep(self.processing_delay)
                
                # Process the document
                self.document_processor.invoice_processor.initialize_api()
                success = self.document_processor.process_single_document(file_path)
                
                if success:
                    self.document_processor.invoice_processor.export_to_excel()
                    self.document_processor.move_processed_file(file_path, success=True)
                    print(f"✓ Auto-processed: {os.path.basename(file_path)}")
                else:
                    self.document_processor.move_processed_file(file_path, success=False)
                    print(f"✗ Auto-processing failed: {os.path.basename(file_path)}")

def start_document_watcher(watch_folder="./watch", output_file="invoice_data.xlsx"):
    """Start automatic document watching"""
    processor = DocumentProcessor(watch_folder=watch_folder, output_file=output_file)
    event_handler = DocumentWatcher(processor)
    observer = Observer()
    observer.schedule(event_handler, watch_folder, recursive=False)
    observer.start()
    
    print(f"🔍 Document watcher started")
    print(f"📁 Watching folder: {watch_folder}")
    print(f"📊 Output file: {output_file}")
    print("Press Ctrl+C to stop...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n🛑 Document watcher stopped")
    
    observer.join()

if __name__ == "__main__":
    # Example usage
    processor = DocumentProcessor()
    
    # Process batch
    processed, failed = processor.process_batch()
    
    # Show stats
    stats = processor.get_processing_stats()
    print("\n📊 Processing Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")