# SurakshaDrishti AI - Professional Backend Launcher
# Purpose: Run backend cleanly for demo without messy raw logs.
# This file only controls terminal display. It does not change backend logic.

Clear-Host

$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

$ProjectRoot = "E:\Copycat2"
$BackendUrl = "http://127.0.0.1:8000"
$LogDir = Join-Path $ProjectRoot "logs"
$StdoutLog = Join-Path $LogDir "backend_stdout.log"
$StderrLog = Join-Path $LogDir "backend_stderr.log"

if (!(Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir | Out-Null
}

function Show-Header {
    Write-Host ""
    Write-Host "==============================================================" -ForegroundColor Cyan
    Write-Host "              SurakshaDrishti AI Backend Server              " -ForegroundColor Green
    Write-Host "==============================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Backend URL : $BackendUrl" -ForegroundColor Yellow
    Write-Host "API Docs    : $BackendUrl/docs" -ForegroundColor Yellow
    Write-Host "Health      : $BackendUrl/health" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Mode        : Professional Demo Mode" -ForegroundColor Gray
    Write-Host "Logs        : logs\backend_stdout.log / logs\backend_stderr.log" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Press Ctrl + C to stop backend cleanly." -ForegroundColor Gray
    Write-Host ""
    Write-Host "--------------------------------------------------------------" -ForegroundColor DarkGray
}

function Show-Status {
    param(
        [string]$Label,
        [string]$Message,
        [string]$Color = "White"
    )

    Write-Host "  " -NoNewline
    Write-Host $Label.PadRight(12) -NoNewline -ForegroundColor $Color
    Write-Host " | " -NoNewline -ForegroundColor DarkGray
    Write-Host $Message -ForegroundColor $Color
}

function Test-Url {
    param(
        [string]$Label,
        [string]$Url,
        [string]$SuccessMessage
    )

    try {
        Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5 | Out-Null
        Show-Status "[OK]" $SuccessMessage "Green"
        return $true
    }
    catch {
        Show-Status "[FAIL]" "$Label failed: $Url" "Red"
        return $false
    }
}

Show-Header

# Stop old backend if port 8000 is already occupied
$oldProcesses = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue |
    Where-Object { $_.State -eq "Listen" } |
    Select-Object -ExpandProperty OwningProcess -Unique

if ($oldProcesses) {
    Show-Status "[INFO]" "Stopping old backend process on port 8000..." "Yellow"

    foreach ($processId in $oldProcesses) {
        Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
    }

    Start-Sleep -Seconds 2
}

try {
    Show-Status "[BOOT]" "Starting FastAPI backend..." "Yellow"

    $backendProcess = Start-Process `
        -FilePath "python" `
        -ArgumentList "-m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --log-level warning" `
        -WorkingDirectory $ProjectRoot `
        -RedirectStandardOutput $StdoutLog `
        -RedirectStandardError $StderrLog `
        -PassThru `
        -WindowStyle Hidden

    Start-Sleep -Seconds 4

    if ($backendProcess.HasExited) {
        Show-Status "[ERROR]" "Backend stopped immediately. Check logs\backend_stderr.log" "Red"
        exit 1
    }

    Show-Status "[OK]" "Backend process started successfully" "Green"
    Write-Host ""

    Show-Status "[CHECK]" "Running endpoint verification..." "Cyan"

    $healthOk = Test-Url "Health" "$BackendUrl/health" "Health API online"
    $docsOk = Test-Url "Docs" "$BackendUrl/docs" "API documentation available"
    $csvOk = Test-Url "CSV Export" "$BackendUrl/reports/events/csv?limit=100" "CSV export working"
    $jsonOk = Test-Url "JSON Export" "$BackendUrl/reports/events/json?limit=100" "JSON export working"
    $dailyOk = Test-Url "Daily Report" "$BackendUrl/reports/daily?limit=100" "Daily report working"

    Write-Host ""
    Write-Host "--------------------------------------------------------------" -ForegroundColor DarkGray

    if ($healthOk -and $docsOk -and $csvOk -and $jsonOk -and $dailyOk) {
        Show-Status "[READY]" "Backend is ready for final demo" "Green"
    }
    else {
        Show-Status "[WARN]" "Backend started, but some checks failed. Review URLs/logs." "Yellow"
    }

    Write-Host "--------------------------------------------------------------" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "Keep this terminal open while presenting." -ForegroundColor Gray
    Write-Host "Open dashboard/frontend in another terminal." -ForegroundColor Gray
    Write-Host ""

    while (-not $backendProcess.HasExited) {
        Start-Sleep -Seconds 1
        $backendProcess.Refresh()
    }
}
catch {
    Show-Status "[ERROR]" "Backend launcher interrupted or failed." "Red"
}
finally {
    if ($backendProcess -and -not $backendProcess.HasExited) {
        Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
    }

    Write-Host ""
    Write-Host "==============================================================" -ForegroundColor Cyan
    Write-Host "          SurakshaDrishti AI Backend Stopped Cleanly         " -ForegroundColor Green
    Write-Host "==============================================================" -ForegroundColor Cyan
    Write-Host ""
}