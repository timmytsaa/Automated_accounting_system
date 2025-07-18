#!/bin/bash
# Automated Invoice Processing Script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Change to the script directory
cd "$(dirname "$0")"

echo -e "${BLUE}=== Automated Invoice Processing System ===${NC}"
echo -e "${BLUE}Starting invoice processing...${NC}\n"

# Check if virtual environment exists
if [ ! -d "venv_new" ]; then
    echo -e "${RED}Error: Virtual environment not found!${NC}"
    echo -e "${YELLOW}Please run: python3 -m venv venv_new && venv_new/bin/pip install -r requirements.txt${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo -e "${YELLOW}Please create .env file with your ANTHROPIC_API_KEY${NC}"
    exit 1
fi

# Check if invoice folder exists
if [ ! -d "invoice" ]; then
    echo -e "${YELLOW}Warning: invoice folder not found. Creating it...${NC}"
    mkdir -p invoice
fi

# Count invoice images
invoice_count=$(find invoice -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" -o -name "*.webp" \) | wc -l)
echo -e "${BLUE}Found ${invoice_count} invoice images to process${NC}"

if [ "$invoice_count" -eq 0 ]; then
    echo -e "${YELLOW}No invoice images found in the invoice folder.${NC}"
    echo -e "${YELLOW}Please add .jpg, .png, or .webp files to the invoice folder.${NC}"
    exit 0
fi

# Run the processor
echo -e "${BLUE}Processing invoices...${NC}"
./venv_new/bin/python automated_invoice_processor.py

# Check if processing was successful
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✓ Invoice processing completed successfully!${NC}"
    
    # Display summary
    echo -e "\n${BLUE}Getting invoice summary...${NC}"
    ./venv_new/bin/python -c "
from automated_invoice_processor import InvoiceProcessor
processor = InvoiceProcessor()
summary = processor.get_invoice_summary()
if summary:
    print(f'📊 Invoice Summary:')
    print(f'   Total Invoices: {summary[\"total_invoices\"]}')
    print(f'   Total Amount: \${summary[\"total_amount\"]}')
    print(f'   Pending Payments: {summary[\"pending_payments\"]}')
    print(f'   Paid Invoices: {summary[\"paid_invoices\"]}')
    print(f'   Overdue Invoices: {summary[\"overdue_invoices\"]}')
    print(f'   Currencies: {list(summary[\"currencies\"].keys())}')
    print(f'   Vendors: {len(summary[\"vendors\"])} unique vendors')
else:
    print('⚠️  Could not generate summary')
"
    
    # Check if Excel file was created
    if [ -f "invoice_data.xlsx" ]; then
        echo -e "\n${GREEN}✓ Excel file created: invoice_data.xlsx${NC}"
        
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
    echo -e "\n${RED}✗ Invoice processing failed!${NC}"
    echo -e "${YELLOW}Please check the error messages above.${NC}"
    exit 1
fi

echo -e "\n${GREEN}🎉 Processing complete!${NC}"