# SurakshaDrishti AI — Start Camera AI Pipeline
# Runs webcam detection, tracking, event engine, and live frame streaming

Set-Location "E:\Copycat2"

if (Test-Path ".\venv\Scripts\Activate.ps1") {
    . ".\venv\Scripts\Activate.ps1"
}

python pipelines\tracking_pipeline.py