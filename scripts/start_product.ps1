$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
$frontend = Join-Path $projectRoot "frontend"
$logDirectory = Join-Path $projectRoot "inspection_store\logs"
$env:PYTHONPATH = Join-Path $projectRoot "src"

if (-not (Test-Path -LiteralPath $python)) {
    throw "Python environment not found. Follow the setup steps in README.md first."
}
if (-not (Test-Path -LiteralPath (Join-Path $frontend "node_modules"))) {
    throw "Frontend dependencies not found. Run npm install in the frontend directory."
}

New-Item -ItemType Directory -Force -Path $logDirectory | Out-Null
$backend = Start-Process -FilePath $python `
    -ArgumentList "-m", "uvicorn", "fabric_inspection.product.api:create_app", "--factory", "--host", "127.0.0.1", "--port", "8000" `
    -WorkingDirectory $projectRoot `
    -RedirectStandardOutput (Join-Path $logDirectory "backend.stdout.log") `
    -RedirectStandardError (Join-Path $logDirectory "backend.stderr.log") `
    -WindowStyle Hidden -PassThru
$npm = (Get-Command npm.cmd).Source
$ui = Start-Process -FilePath $npm `
    -ArgumentList "run", "dev" `
    -WorkingDirectory $frontend `
    -RedirectStandardOutput (Join-Path $logDirectory "frontend.stdout.log") `
    -RedirectStandardError (Join-Path $logDirectory "frontend.stderr.log") `
    -WindowStyle Hidden -PassThru

Start-Sleep -Seconds 2
Write-Host "RAW-FABRID Quality Inspection is running." -ForegroundColor Green
Write-Host "Product UI: http://127.0.0.1:5173"
Write-Host "API docs:   http://127.0.0.1:8000/docs"
Write-Host "Backend PID: $($backend.Id) | Frontend PID: $($ui.Id)"
Write-Host "Logs: $logDirectory"
