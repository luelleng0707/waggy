# Start Wagtopia PPIE Python demo (API + Streamlit UI)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "[PPIE] Installing Python dependencies..." -ForegroundColor Cyan
py -3 -m pip install -q -r requirements.txt

Write-Host "[PPIE] Starting FastAPI on http://localhost:8000" -ForegroundColor Magenta
Start-Process -NoNewWindow py -ArgumentList "-3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"

Start-Sleep -Seconds 2

Write-Host "[PPIE] Starting Streamlit UI on http://localhost:8501" -ForegroundColor Magenta
py -3 -m streamlit run app/ui/demo_app.py --server.port 8501
