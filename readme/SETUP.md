# Setup Guide for Automated Invoice Processing System

## Quick Start

### 1. Get Your Anthropic API Key
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Create an account or log in
3. Navigate to API Keys
4. Create a new API key
5. Copy the key (starts with `sk-ant-`)

### 2. Initial Setup
```bash
# Create virtual environment
python3 -m venv venv_new

# Activate virtual environment
source venv_new/bin/activate  # Linux/Mac
# OR
venv_new\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure API Key
Create a `.env` file in the root directory:
```
ANTHROPIC_API_KEY=sk-ant-your-actual-api-key-here
```

### 4. Test the System
```bash
# Make shell script executable (Linux/Mac)
chmod +x bin/run_processor.sh

# Run the system
./bin/run_processor.sh
```

## For Windows Users

### Using Windows Batch Script
```batch
# Run the batch script
bin\run_processor.bat
```

### Using PowerShell
```powershell
# Activate virtual environment
venv_new\Scripts\Activate.ps1

# Run Python script directly
python accounting_system\automated_invoice_processor.py
```

## Folder Structure Setup

The system automatically creates these folders:
- `invoice/` - Place your invoices here
- `analyzed_invoices/` - Successfully processed invoices
- `failed/` - Failed invoices for manual review
- `watch/` - For batch processing mode

## First Use

1. **Add invoices** to the `invoice/` folder
2. **Run the shell script**: `./bin/run_processor.sh`
3. **Choose option 1** for single folder processing
4. **Check results** in `invoice_data.xlsx`

## Troubleshooting

### Common Issues

**"Virtual environment not found"**
```bash
python3 -m venv venv_new
source venv_new/bin/activate
```

**"ANTHROPIC_API_KEY not found"**
- Check your `.env` file exists
- Ensure API key is correct
- No spaces around the `=` sign

**"No invoices processed"**
- Ensure invoices are real (not templates)
- Check file formats: JPG, PNG, WEBP, PDF
- Try with different invoice files

**"Permission denied"**
```bash
chmod +x bin/run_processor.sh
```

### API Key Issues

If you see authentication errors:
1. Verify your API key is valid
2. Check your Anthropic account has credits
3. Ensure no extra spaces in the `.env` file

### File Processing Issues

**Templates or examples will fail** - this is normal behavior:
- The system correctly rejects invoice templates
- Use real invoices with actual data
- Failed invoices are moved to `failed/` folder

## Performance Tips

- **Batch processing**: Use multiple invoices at once
- **File formats**: JPG/PNG work best
- **File size**: Smaller files process faster
- **Network**: Stable internet connection recommended

## Support

Check the main README.md for detailed documentation and troubleshooting steps.