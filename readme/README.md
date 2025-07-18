# Automated Invoice Processing System

An AI-powered invoice processing system that automatically extracts data from invoices and exports to Excel, designed for accounting professionals.

## Features

- **AI-Powered OCR**: Uses Claude AI to extract invoice data with high accuracy
- **Multi-Format Support**: Processes JPG, PNG, WEBP images and PDF documents
- **Traditional Chinese Support**: Fully compatible with Traditional Chinese invoices
- **Excel Export**: Automatically exports structured data to Excel spreadsheets
- **Automatic File Organization**: 
  - Successful invoices → `analyzed_invoices/` folder
  - Failed invoices → `failed/` folder for manual review
- **Batch Processing**: Process multiple invoices at once
- **Intelligent Retry**: Automatically retries failed invoices
- **Shell Script Interface**: Easy-to-use command-line interface

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd accounting_system
   ```

2. **Set up Python virtual environment**:
   ```bash
   python3 -m venv venv_new
   source venv_new/bin/activate  # On Windows: venv_new\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API key**:
   Create a `.env` file in the root directory:
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

## Usage

### Method 1: Shell Script (Recommended)
```bash
./bin/run_processor.sh
```

Choose from 4 processing modes:
1. **Single Folder Processing** - Process invoices in `invoice/` folder
2. **Multi-Document Batch** - Process documents in `watch/` folder
3. **Auto-Monitor Mode** - Watch for new documents automatically
4. **Show Statistics** - View processing statistics

### Method 2: Direct Python Execution
```bash
source venv_new/bin/activate
python3 accounting_system/automated_invoice_processor.py
```

## Project Structure

```
accounting_system/
├── accounting_system/          # Core Python modules
│   ├── automated_invoice_processor.py  # Main invoice processing
│   ├── excel_manager.py               # Excel operations
│   ├── document_processor.py          # Multi-document processing
│   └── run_multi_processor.py         # Batch processing
├── bin/                        # Executable scripts
│   ├── run_processor.sh               # Linux/Mac shell script
│   └── run_processor.bat             # Windows batch script
├── invoice/                    # Input folder for invoices
├── analyzed_invoices/          # Successfully processed invoices
├── failed/                     # Failed invoices for manual review
├── processed/                  # Legacy processed files
├── .env                        # API key configuration
├── requirements.txt            # Python dependencies
└── invoice_data.xlsx          # Output Excel file
```

## Data Fields Extracted

The system extracts the following information from invoices:

- **Invoice Details**: Invoice number, date, due date
- **Vendor Information**: Name, address, phone, email
- **Receiver Information**: Name, address, phone, email
- **Financial Data**: Tax amount, total amount, currency
- **Line Items**: Description, quantity, unit price, amount
- **Processing Metadata**: Processing date, source file

## Supported File Types

- **Images**: JPG, JPEG, PNG, WEBP
- **Documents**: PDF (multi-page supported)
- **Languages**: English, Traditional Chinese

## Error Handling

The system includes comprehensive error handling:

- **Automatic Retry**: Failed invoices are retried immediately
- **File Organization**: Failed invoices are moved to `failed/` folder
- **Error Messages**: Clear feedback on processing issues
- **Template Detection**: Automatically rejects invoice templates

## Requirements

- Python 3.7+
- Anthropic API key
- Internet connection for AI processing

## Dependencies

See `requirements.txt` for full list:
- anthropic
- python-dotenv
- pillow
- pandas
- openpyxl
- PyMuPDF
- watchdog

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is designed for accounting professionals and small businesses to automate invoice processing workflows.

## Support

For issues or questions, please check the error messages and ensure:
- Valid Anthropic API key in `.env` file
- Proper file formats (not templates or corrupted files)
- Internet connection for AI processing