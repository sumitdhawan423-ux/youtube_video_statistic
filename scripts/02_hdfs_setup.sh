#!/usr/bin/env bash
# ==============================================================================
# Step 2: Hadoop HDFS Setup and Raw Data Ingestion
# Creates directories on HDFS and uploads raw CSVs and Category JSON files.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
RAW_DATA_DIR="$PROJECT_ROOT/data/raw"

HDFS_BASE="/youtube"
HDFS_RAW="$HDFS_BASE/raw"
HDFS_CLEAN="$HDFS_BASE/clean"
HDFS_OUTPUT="$HDFS_BASE/output"

echo "================================================================="
echo " YouTube Big Data Pipeline - Step 2: HDFS Setup & Upload"
echo "================================================================="

# Check if hdfs CLI is available
if ! command -v hdfs &> /dev/null; then
    echo "[!] 'hdfs' command not found on PATH."
    echo "    If you are running in standalone/local mode without Hadoop,"
    echo "    PySpark will read directly from the local file system at: $RAW_DATA_DIR"
    echo "    To run with Hadoop, please start HDFS (start-dfs.sh) and ensure Hadoop bin is on PATH."
    exit 0
fi

echo "[*] Creating HDFS directories..."
hdfs dfs -mkdir -p "$HDFS_RAW"
hdfs dfs -mkdir -p "$HDFS_CLEAN"
hdfs dfs -mkdir -p "$HDFS_OUTPUT"

echo "[*] Uploading raw CSV and JSON datasets to HDFS at $HDFS_RAW..."
if [ -d "$RAW_DATA_DIR" ]; then
    hdfs dfs -put -f "$RAW_DATA_DIR"/*.csv "$HDFS_RAW/" || true
    hdfs dfs -put -f "$RAW_DATA_DIR"/*.json "$HDFS_RAW/" || true
else
    echo "[-] Directory $RAW_DATA_DIR does not exist."
    exit 1
fi

echo "[+] Upload complete! Current files in HDFS $HDFS_RAW:"
hdfs dfs -ls "$HDFS_RAW"

