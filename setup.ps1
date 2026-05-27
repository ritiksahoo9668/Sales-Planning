# One-time / fresh setup for Sales Planning ERP
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (Test-Path ".\.venv\Scripts\python.exe") {
    $python = ".\.venv\Scripts\python.exe"
    $pip = ".\.venv\Scripts\pip.exe"
} else {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    python -m venv .venv
    $python = ".\.venv\Scripts\python.exe"
    $pip = ".\.venv\Scripts\pip.exe"
}

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example" -ForegroundColor Green
}

Write-Host "Installing dependencies..." -ForegroundColor Cyan
& $pip install -r requirements\requirements.txt

Write-Host "Running migrations..." -ForegroundColor Cyan
& $python manage.py migrate

Write-Host "Loading vendor masters and sample data..." -ForegroundColor Cyan
& $python manage.py seed_vendor_masters
& $python manage.py seed_erp_data

Write-Host "`nSetup complete. Start the app with:" -ForegroundColor Green
Write-Host "  .\start.ps1" -ForegroundColor Yellow
Write-Host "Then open: http://127.0.0.1:8004/parties/" -ForegroundColor Yellow
Write-Host "Login: admin / admin123`n" -ForegroundColor Yellow
