@echo off
REM Enhanced Multi-Document Processing Script for Windows
color 0B
echo.
echo ==========================================
echo   Enhanced Multi-Document Processing System
echo   Supports: Images + PDFs + Traditional Chinese
echo ==========================================
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

REM Create multi-document processing folders
echo Setting up multi-document processing folders...
if not exist "watch" mkdir watch
if not exist "processed" mkdir processed
if not exist "failed" mkdir failed
if not exist "invoice" mkdir invoice
echo.

REM Show processing mode menu
echo Choose processing mode:
echo 1. Single Folder Processing (process invoice folder)
echo 2. Multi-Document Batch (process watch folder)
echo 3. Auto-Monitor Mode (watch for new documents)
echo 4. Show Statistics (view processing stats)
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto single_folder
if "%choice%"=="2" goto multi_batch
if "%choice%"=="3" goto auto_monitor
if "%choice%"=="4" goto show_stats
echo [ERROR] Invalid choice!
pause
exit /b 1

:single_folder
echo.
echo === Single Folder Processing ===
echo.

REM Count documents in invoice folder
set /a count=0
for %%f in (invoice\*.jpg invoice\*.jpeg invoice\*.png invoice\*.webp invoice\*.pdf) do set /a count+=1

echo Found %count% documents in invoice folder
echo.

if %count%==0 (
    echo [WARNING] No documents found in invoice folder.
    echo Please add images or PDFs to the invoice folder.
    echo.
    pause
    exit /b 0
)

REM Run standard processor
echo Processing documents...
echo.
venv_new\Scripts\python.exe automated_invoice_processor.py
goto process_complete

:multi_batch
echo.
echo === Multi-Document Batch Processing ===
echo.

REM Count documents in watch folder
set /a count=0
for %%f in (watch\*.jpg watch\*.jpeg watch\*.png watch\*.webp watch\*.pdf) do set /a count+=1

echo Found %count% documents in watch folder
echo.

if %count%==0 (
    echo [WARNING] No documents found in watch folder.
    echo Please add images or PDFs to the watch folder.
    echo.
    pause
    exit /b 0
)

REM Run multi-document processor
echo Processing batch documents...
echo.
venv_new\Scripts\python.exe run_multi_processor.py --mode batch --stats
goto process_complete

:auto_monitor
echo.
echo === Auto-Monitor Mode ===
echo.
echo Starting automatic document monitoring...
echo Drop documents into the 'watch' folder and they'll be processed automatically
echo Press Ctrl+C to stop monitoring
echo.

REM Run document watcher
venv_new\Scripts\python.exe run_multi_processor.py --mode watch
goto end

:show_stats
echo.
echo === Processing Statistics ===
echo.

REM Run statistics
venv_new\Scripts\python.exe -c "from document_processor import DocumentProcessor; processor = DocumentProcessor(); stats = processor.get_processing_stats(); print('📊 Multi-Document Processing Statistics:'); [print(f'   {key}: {value}') for key, value in stats.items()]"

REM Also show invoice summary if available
if exist "invoice_data.xlsx" (
    echo.
    echo Invoice Summary:
    venv_new\Scripts\python.exe -c "from automated_invoice_processor import InvoiceProcessor; processor = InvoiceProcessor(); summary = processor.get_invoice_summary(); print(f'   Total Invoices: {summary[\"total_invoices\"]}') if summary else print('   No invoice data available')"
)
echo.
pause
exit /b 0

:process_complete
if %errorlevel%==0 (
    echo.
    echo [SUCCESS] Processing completed successfully!
    echo.
    
    if exist "invoice_data.xlsx" (
        echo [SUCCESS] Excel file updated: invoice_data.xlsx
        echo.
        
        REM Show folder status
        echo Folder Status:
        for /f %%i in ('dir /b watch 2^>nul ^| find /c /v ""') do echo    Watch folder: %%i files
        for /f %%i in ('dir /b processed 2^>nul ^| find /c /v ""') do echo    Processed folder: %%i files
        for /f %%i in ('dir /b failed 2^>nul ^| find /c /v ""') do echo    Failed folder: %%i files
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
    echo [ERROR] Processing failed!
    echo Please check the error messages above.
    pause
    exit /b 1
)

:end
echo.
echo 🎉 Processing complete!
echo.
pause