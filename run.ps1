# Shareable PowerShell script to run a Python TUI from a raw GitHub URL without leaving permanent files.
# Usage: 
#   1) Save this script locally, e.g.:  Save-As RunTUI.ps1
#   2) Run it from PowerShell:          .\RunTUI.ps1
#
# NOTE:
#   - Make sure 'python' is on the PATH.
#   - This script will automatically remove the downloaded file once the TUI exits.
#   - If the user has restricted execution policies, they may need to enable 
#     execution for this script (e.g., "Set-ExecutionPolicy Bypass" as Admin).

Param(
    [String]$RawScriptUri = "https://raw.githubusercontent.com/YourUser/YourRepo/main/app.py"
)

Write-Host "Downloading Python TUI from $RawScriptUri" -ForegroundColor Cyan

try {
    $TempFile = Join-Path $env:TEMP "temp_tui_$(Get-Random).py"

    Invoke-WebRequest -Uri $RawScriptUri -OutFile $TempFile -UseBasicParsing

    if (Test-Path $TempFile) {
        Write-Host "Download complete. Running the TUI..." -ForegroundColor Green
        
        # Run Python on the TUI script
        & python $TempFile

        Write-Host "TUI exited. Cleaning up..." -ForegroundColor Yellow
        Remove-Item -Path $TempFile -Force -ErrorAction SilentlyContinue
    }
    else {
        Write-Host "Download failed. The file does not exist after Invoke-WebRequest." -ForegroundColor Red
    }
}
catch {
    Write-Host "Error encountered: $($_.Exception.Message)" -ForegroundColor Red
}
