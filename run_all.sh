#!/usr/bin/env bash
# ==============================================================================
# Master Pipeline Runner Script (Bash / Linux / macOS / WSL)
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================================================"
echo " YouTube Video Statistics Pipeline Runner (Bash)"
echo "========================================================================"

# Activate virtualenv if present
if [ -d ".venv" ]; then
    echo "[*] Activating virtual environment (.venv)..."
    source .venv/bin/activate
elif [ -d "venv" ]; then
    echo "[*] Activating virtual environment (venv)..."
    source venv/bin/activate
fi

# Optional Step 2: HDFS upload if Hadoop is detected
if command -v hdfs &> /dev/null; then
    echo "[*] Hadoop HDFS detected. Running HDFS setup..."
    bash scripts/02_hdfs_setup.sh
fi

# Execute Python master pipeline
python run_all.py

