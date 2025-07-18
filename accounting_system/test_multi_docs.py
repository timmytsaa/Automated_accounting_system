#!/usr/bin/env python3
"""
Test script for multi-document processing
"""

import os
from document_processor import DocumentProcessor

def test_multi_document_processing():
    """Test the multi-document processing system"""
    
    print("=== Multi-Document Processing Test ===\n")
    
    # Initialize processor
    processor = DocumentProcessor(
        watch_folder="./watch",
        processed_folder="./processed",
        failed_folder="./failed",
        output_file="multi_document_test.xlsx"
    )
    
    # Test 1: Check supported file types
    print("1. Testing supported file types:")
    test_files = [
        "invoice.jpg", "receipt.png", "document.pdf", 
        "contract.webp", "statement.txt", "image.bmp"
    ]
    
    for file in test_files:
        supported = processor.is_supported_file(file)
        print(f"   {file}: {'✓' if supported else '✗'}")
    
    # Test 2: Document classification
    print("\n2. Testing document classification:")
    test_docs = [
        "invoice_001.jpg", "receipt_abc.png", "contract_xyz.pdf",
        "發票_123.jpg", "收據_456.png", "statement_789.pdf"
    ]
    
    for doc in test_docs:
        doc_type = processor.classify_document(doc)
        print(f"   {doc}: {doc_type}")
    
    # Test 3: Check directory structure
    print("\n3. Testing directory structure:")
    folders = [processor.watch_folder, processor.processed_folder, processor.failed_folder]
    for folder in folders:
        exists = os.path.exists(folder)
        print(f"   {folder}: {'✓' if exists else '✗'}")
    
    # Test 4: Processing statistics
    print("\n4. Processing statistics:")
    stats = processor.get_processing_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Test 5: Check if watch folder has documents
    print("\n5. Checking for documents in watch folder:")
    if os.path.exists(processor.watch_folder):
        files = os.listdir(processor.watch_folder)
        supported_files = [f for f in files if processor.is_supported_file(f)]
        print(f"   Found {len(supported_files)} supported documents")
        
        if supported_files:
            print("   Files ready for processing:")
            for file in supported_files:
                print(f"     - {file}")
        else:
            print("   No documents found. Add some invoice images or PDFs to ./watch folder")
    
    print("\n=== Test Complete ===")
    print("\nTo test processing:")
    print("1. Add invoice images or PDFs to ./watch folder")
    print("2. Run: python run_multi_processor.py --mode batch")
    print("3. Or run: python run_multi_processor.py --mode watch")

if __name__ == "__main__":
    test_multi_document_processing()