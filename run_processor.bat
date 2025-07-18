@echo off
REM Automated Invoice Processing Script for Windows
color 0B
echo.
echo ==========================================
echo    Automated Invoice Processing System
echo ==========================================
echo.
echo Starting invoice processing...
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv_new" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup_windows.bat first
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo [ERROR] .env file not found!
    echo Please create .env file with your ANTHROPIC_API_KEY
    echo You can copy .env.example to .env and edit it
    pause
    exit /b 1
)

REM Check if invoice folder exists
if not exist "invoice" (
    echo [WARNING] invoice folder not found. Creating it...
    mkdir invoice
)

REM Count invoice images
set /a count=0
for %%f in (invoice\*.jpg invoice\*.jpeg invoice\*.png invoice\*.webp) do set /a count+=1

echo Found %count% invoice images to process
echo.

if %count%==0 (
    echo [WARNING] No invoice images found in the invoice folder.
    echo Please add .jpg, .png, or .webp files to the invoice folder.
    echo.
    pause
    exit /b 0
)

REM Run the processor
echo Processing invoices...
echo.
venv_new\Scripts\python.exe automated_invoice_processor.py

if %errorlevel%==0 (
    echo.
    echo [SUCCESS] Invoice processing completed successfully!
    echo.
    
    REM Display summary
    echo Getting invoice summary...
    echo.
    venv_new\Scripts\python.exe -c "from automated_invoice_processor import InvoiceProcessor; processor = InvoiceProcessor(); summary = processor.get_invoice_summary(); print(f'📊 Invoice Summary:'); print(f'   Total Invoices: {summary[\"total_invoices\"]}'); print(f'   Total Amount: ${summary[\"total_amount\"]}'); print(f'   Pending Payments: {summary[\"pending_payments\"]}'); print(f'   Paid Invoices: {summary[\"paid_invoices\"]}'); print(f'   Overdue Invoices: {summary[\"overdue_invoices\"]}'); print(f'   Currencies: {list(summary[\"currencies\"].keys())}'); print(f'   Vendors: {len(summary[\"vendors\"])} unique vendors')"
    
    echo.
    if exist "invoice_data.xlsx" (
        echo [SUCCESS] Excel file created: invoice_data.xlsx
        echo.
        set /p choice="Would you like to open the Excel file? (y/n): "
        if /i "%choice%"=="y" (
            start "" "invoice_data.xlsx"
        )
    ) else (
        echo [WARNING] Excel file not found
    )
    
) else (
    echo.
    echo [ERROR] Invoice processing failed!
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo 🎉 Processing complete!
echo.
pause