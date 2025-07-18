#!/usr/bin/env python3
"""
Multi-Document Processing Runner
Supports batch processing and automatic monitoring
"""

import sys
import os
import argparse
from document_processor import DocumentProcessor, start_document_watcher

def main():
    parser = argparse.ArgumentParser(description='Multi-Document Invoice Processor')
    parser.add_argument('--mode', choices=['batch', 'watch'], default='batch',
                       help='Processing mode: batch or watch')
    parser.add_argument('--watch-folder', default='./watch',
                       help='Folder to watch for new documents')
    parser.add_argument('--output', default='invoice_data.xlsx',
                       help='Output Excel file')
    parser.add_argument('--stats', action='store_true',
                       help='Show processing statistics')
    
    args = parser.parse_args()
    
    if args.mode == 'batch':
        print("🔄 Starting batch processing...")
        processor = DocumentProcessor(
            watch_folder=args.watch_folder,
            output_file=args.output
        )
        
        # Process all documents in watch folder
        processed, failed = processor.process_batch()
        
        if args.stats:
            stats = processor.get_processing_stats()
            print("\n📊 Processing Statistics:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
        
        print(f"\n✅ Batch processing complete: {processed} processed, {failed} failed")
        
    elif args.mode == 'watch':
        print("👁️  Starting document watcher...")
        start_document_watcher(args.watch_folder, args.output)

if __name__ == "__main__":
    main()