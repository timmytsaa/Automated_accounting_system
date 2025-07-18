# Automated Invoice Processing System

An AI-powered invoice processing system that extracts structured data from invoice images using Claude AI and exports to Excel for accounting purposes.

## Features

- 🤖 **AI-Powered Extraction**: Uses Claude AI to extract comprehensive invoice data
- 📊 **Excel Export**: Generates structured Excel files with all invoice details
- 💰 **Payment Tracking**: Manage payment status and due dates
- 🔍 **Data Filtering**: Filter and export specific invoice data
- 📈 **Reporting**: Generate comprehensive invoice summaries
- 🔄 **Append Mode**: Add new invoices without overwriting existing data

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/invoice-processing-system.git
cd invoice-processing-system

# Create virtual environment
python3 -m venv venv_new
source venv_new/bin/activate  # On Windows: venv_new\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment file
cp .env.example .env

# Edit .env file and add your Anthropic API key
# Get your API key from: https://console.anthropic.com/
```

### 3. Usage

```bash
# Add invoice images to the invoice folder
cp your_invoices/*.jpg invoice/

# Run the automated processor
./run_processor.sh
```

## Data Structure

The system extracts the following information from invoices:

### Basic Information
- Invoice Number
- Vendor Name, Address, Phone, Email
- Receiver Name, Address, Phone, Email
- Invoice Date and Due Date

### Financial Details
- Subtotal, Tax Amount, Total Amount
- Currency Type
- Payment Status and Payment Date
- Line Items with descriptions, quantities, and prices

### Metadata
- Processing Date
- Source File Name
- Confidence Score

## Excel Output

The system generates Excel files with comprehensive invoice data:

| Invoice Number | Vendor Name | Vendor Address | ... | Total Amount | Currency | Payment Status |
|---------------|-------------|----------------|-----|--------------|----------|----------------|
| INV-001       | ABC Corp    | 123 Main St    | ... | $1,080.00    | USD      | Pending        |

## Advanced Usage

### Python API

```python
from automated_invoice_processor import InvoiceProcessor

# Initialize processor
processor = InvoiceProcessor()

# Process invoices
processor.initialize_api()
processor.process_all_invoices()
processor.export_to_excel()

# Get summary
summary = processor.get_invoice_summary()
print(f"Total invoices: {summary['total_invoices']}")

# Update payment status
processor.update_payment_status("INV-001", "Paid", "2024-01-15")
```

### Payment Management

```python
# Update multiple payment statuses
invoices = [
    ("INV-001", "Paid", "2024-01-15"),
    ("INV-002", "Overdue", None),
    ("INV-003", "Pending", None)
]

for invoice_num, status, date in invoices:
    processor.update_payment_status(invoice_num, status, date)
```

### Data Filtering and Export

```python
# Filter by payment status
processor.excel_manager.export_filtered_data(
    {"payment_status": "Paid"}, 
    "paid_invoices.xlsx"
)

# Filter by vendor
processor.excel_manager.export_filtered_data(
    {"vendor_name": "ABC Corp"}, 
    "abc_corp_invoices.xlsx"
)
```

## File Structure

```
invoice-processing-system/
├── automated_invoice_processor.py  # Main processor
├── excel_manager.py               # Excel operations
├── run_processor.sh               # Automated runner
├── requirements.txt               # Dependencies
├── .env.example                   # Environment template
├── invoice/                       # Input folder
│   └── .gitkeep                   # Folder placeholder
├── README.md                      # Documentation
└── .gitignore                     # Git ignore rules
```

## Requirements

- Python 3.8+
- Anthropic API key
- Virtual environment (recommended)

## Dependencies

- anthropic>=0.7.0
- python-dotenv>=0.19.0
- pillow>=9.0.0
- pandas>=1.3.0
- openpyxl>=3.0.0

## Security

- Never commit `.env` files with API keys
- Invoice images and Excel files are ignored by git
- Use environment variables for sensitive data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the existing issues
2. Create a new issue with detailed description
3. Include error messages and steps to reproduce

## Changelog

### v1.0.0
- Initial release with AI-powered invoice extraction
- Excel export functionality
- Payment tracking system
- Data filtering and reporting
- Automated processing script