#!/bin/bash
# Enhanced Multi-Document Processing Script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Change to the parent directory (main project directory)
cd "$(dirname "$0")/.."

echo -e "${BLUE}=== Enhanced Multi-Document Processing System ===${NC}"
echo -e "${BLUE}Supports: Images (JPG, PNG, WEBP) + PDFs + Traditional Chinese${NC}\n"

# Check if virtual environment exists
if [ ! -d "venv_new" ]; then
    echo -e "${RED}Error: Virtual environment not found!${NC}"
    echo -e "${YELLOW}Please run setup script first${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo -e "${YELLOW}Please create .env file with your ANTHROPIC_API_KEY${NC}"
    exit 1
fi

# Create multi-document processing folders
echo -e "${BLUE}Setting up multi-document processing folders...${NC}"
mkdir -p watch processed failed invoice

# Show processing mode menu
echo -e "${PURPLE}Choose processing mode:${NC}"
echo -e "1. ${GREEN}Single Folder Processing${NC} (process invoice folder)"
echo -e "2. ${GREEN}Multi-Document Batch${NC} (process watch folder)"
echo -e "3. ${GREEN}Auto-Monitor Mode${NC} (watch for new documents)"
echo -e "4. ${GREEN}Show Statistics${NC} (view processing stats)"
echo ""
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo -e "\n${BLUE}=== Single Folder Processing ===${NC}"
        
        # Count documents in invoice folder
        invoice_count=$(find invoice -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" -o -name "*.webp" -o -name "*.pdf" \) | wc -l)
        echo -e "${BLUE}Found ${invoice_count} documents in invoice folder${NC}"
        
        if [ "$invoice_count" -eq 0 ]; then
            echo -e "${YELLOW}No documents found in invoice folder.${NC}"
            echo -e "${YELLOW}Please add images or PDFs to the invoice folder.${NC}"
            exit 0
        fi
        
        # Run standard processor
        echo -e "${BLUE}Processing documents...${NC}"
        ./venv_new/bin/python accounting_system/automated_invoice_processor.py
        ;;
        
    2)
        echo -e "\n${BLUE}=== Multi-Document Batch Processing ===${NC}"
        
        # Count documents in watch folder
        watch_count=$(find watch -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" -o -name "*.webp" -o -name "*.pdf" \) 2>/dev/null | wc -l)
        echo -e "${BLUE}Found ${watch_count} documents in watch folder${NC}"
        
        if [ "$watch_count" -eq 0 ]; then
            echo -e "${YELLOW}No documents found in watch folder.${NC}"
            echo -e "${YELLOW}Please add images or PDFs to the watch folder.${NC}"
            exit 0
        fi
        
        # Run multi-document processor
        echo -e "${BLUE}Processing batch documents...${NC}"
        ./venv_new/bin/python accounting_system/run_multi_processor.py --mode batch --stats
        ;;
        
    3)
        echo -e "\n${BLUE}=== Auto-Monitor Mode ===${NC}"
        echo -e "${PURPLE}Starting automatic document monitoring...${NC}"
        echo -e "${BLUE}Drop documents into the 'watch' folder and they'll be processed automatically${NC}"
        echo -e "${YELLOW}Press Ctrl+C to stop monitoring${NC}\n"
        
        # Run document watcher
        ./venv_new/bin/python run_multi_processor.py --mode watch
        ;;
        
    4)
        echo -e "\n${BLUE}=== Processing Statistics ===${NC}"
        
        # Run statistics
        ./venv_new/bin/python -c "
from document_processor import DocumentProcessor
processor = DocumentProcessor()
stats = processor.get_processing_stats()
print('📊 Multi-Document Processing Statistics:')
for key, value in stats.items():
    print(f'   {key}: {value}')
"
        
        # Also show invoice summary if available
        if [ -f "invoice_data.xlsx" ]; then
            echo -e "\n${BLUE}Invoice Summary:${NC}"
            ./venv_new/bin/python -c "
from automated_invoice_processor import InvoiceProcessor
processor = InvoiceProcessor()
summary = processor.get_invoice_summary()
if summary:
    print(f'   Total Invoices: {summary[\"total_invoices\"]}')
    print(f'   Total Amount: \${summary[\"total_amount\"]}')
    print(f'   Pending Payments: {summary[\"pending_payments\"]}')
    print(f'   Paid Invoices: {summary[\"paid_invoices\"]}')
    print(f'   Overdue Invoices: {summary[\"overdue_invoices\"]}')
    print(f'   Currencies: {list(summary[\"currencies\"].keys())}')
    print(f'   Vendors: {len(summary[\"vendors\"])} unique vendors')
else:
    print('   No invoice data available')
"
        fi
        exit 0
        ;;
        
    *)
        echo -e "${RED}Invalid choice!${NC}"
        exit 1
        ;;
esac

# Check if processing was successful
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✓ Processing completed successfully!${NC}"
    
    # Check if Excel file was created
    if [ -f "invoice_data.xlsx" ]; then
        echo -e "\n${GREEN}✓ Excel file updated: invoice_data.xlsx${NC}"
        
        # Show folder status
        echo -e "\n${BLUE}Folder Status:${NC}"
        echo -e "   📁 Watch folder: $(find watch -type f 2>/dev/null | wc -l) files"
        echo -e "   ✅ Processed folder: $(find processed -type f 2>/dev/null | wc -l) files"
        echo -e "   ❌ Failed folder: $(find failed -type f 2>/dev/null | wc -l) files"
        
        # Ask if user wants to open the file
        echo -e "\n${YELLOW}Would you like to open the Excel file? (y/n)${NC}"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            if command -v xdg-open > /dev/null; then
                xdg-open invoice_data.xlsx
            elif command -v open > /dev/null; then
                open invoice_data.xlsx
            else
                echo -e "${YELLOW}Please open invoice_data.xlsx manually${NC}"
            fi
        fi
    else
        echo -e "${YELLOW}⚠️  Excel file not found${NC}"
    fi
    
else
    echo -e "\n${RED}✗ Processing failed!${NC}"
    echo -e "${YELLOW}Please check the error messages above.${NC}"
    exit 1
fi

echo -e "\n${GREEN}🎉 Processing complete!${NC}"