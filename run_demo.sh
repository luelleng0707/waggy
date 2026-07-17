#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

echo "[PPIE] Installing Python dependencies..."
python3 -m pip install -q -r requirements.txt

echo "[PPIE] Starting FastAPI on http://localhost:8000"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
API_PID=$!

sleep 2
echo "[PPIE] Starting Streamlit UI on http://localhost:8501"
python3 -m streamlit run app/ui/demo_app.py --server.port 8501

kill "$API_PID" 2>/dev/null || true
