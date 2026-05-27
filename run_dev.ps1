# Start Django dev server on port 8004 with visible request logs (Windows)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$port = if ($env:DEV_PORT) { $env:DEV_PORT } else { "8004" }

if (Test-Path ".\.venv\Scripts\python.exe") {
    $python = ".\.venv\Scripts\python.exe"
} else {
    $python = "python"
}

Write-Host "Stopping old servers on ports 8000 and 8004..." -ForegroundColor Yellow
foreach ($p in 8000, 8004) {
    $lines = netstat -ano | Select-String ":$p\s" | Select-String "LISTENING"
    foreach ($line in $lines) {
        $procId = ($line -split '\s+')[-1]
        if ($procId -match '^\d+$') {
            taskkill /PID $procId /F 2>$null | Out-Null
        }
    }
}

Write-Host "Starting Sales Planning on port $port..." -ForegroundColor Cyan
Write-Host "Open: http://127.0.0.1:$port/parties/" -ForegroundColor Green
Write-Host "Login, then New Partner to create records." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop`n" -ForegroundColor Yellow

# Uses custom runserver (default port from DEV_PORT / 8004)
$env:DEV_PORT = $port
& $python -u manage.py runserver --noreload
