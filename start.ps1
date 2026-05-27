# Sales Planning — one command: prepare DB, seed masters, start dev server
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "Starting PostgreSQL (docker compose)..." -ForegroundColor Cyan
    docker compose up -d
}

if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") { Copy-Item ".env.example" ".env" }
}

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "First run: creating venv and installing packages..." -ForegroundColor Cyan
    python -m venv .venv
    & ".\.venv\Scripts\pip.exe" install -r requirements\requirements.txt
}

$python = ".\.venv\Scripts\python.exe"
$port = if ($env:DEV_PORT) { $env:DEV_PORT } else { "8004" }

Write-Host "Preparing database and master data..." -ForegroundColor Cyan
& $python manage.py migrate --noinput
& $python manage.py seed_vendor_masters
& $python manage.py seed_erp_data

Write-Host "`nLogin: admin / admin123" -ForegroundColor Green
Write-Host "Parties: http://127.0.0.1:$port/parties/" -ForegroundColor Green
Write-Host "Vendor tab example: http://127.0.0.1:$port/parties/1/roles/1/manage/`n" -ForegroundColor Green

foreach ($p in 8000, [int]$port) {
    netstat -ano | Select-String ":$p\s" | Select-String "LISTENING" | ForEach-Object {
        $procId = ($_.Line -split '\s+')[-1]
        if ($procId -match '^\d+$') { taskkill /PID $procId /F 2>$null | Out-Null }
    }
}

$env:DEV_PORT = $port
& $python -u manage.py runserver --noreload
