"""
Step 0: Data Acquisition via Kaggle API.
Downloads the Trending YouTube Video Statistics dataset (datasnaek/youtube-new)
and extracts country CSV and JSON files into the data/raw/ directory.
"""

import os
import sys
import zipfile
import subprocess
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.config import RAW_DATA_DIR, KAGGLE_DATASET_ID

def download_via_kaggle_cli() -> bool:
    """Attempts to download the dataset using kaggle CLI."""
    print(f"[*] Attempting to download '{KAGGLE_DATASET_ID}' using Kaggle CLI...")
    try:
        cmd = [
            "kaggle",
            "datasets",
            "download",
            "-d",
            KAGGLE_DATASET_ID,
            "-p",
            str(RAW_DATA_DIR),
            "--unzip",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"[+] Kaggle CLI download completed:\n{res.stdout}")
        return True
    except FileNotFoundError:
        print("[-] 'kaggle' CLI is not found on PATH.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"[-] Kaggle CLI failed: {e.stderr.strip()}")
        return False

def download_via_kaggle_api() -> bool:
    """Attempts to download dataset using Kaggle Python API."""
    print("[*] Attempting to download using 'kaggle' Python library...")
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        api = KaggleApi()
        api.authenticate()
        print(f"[+] Kaggle authentication successful. Downloading '{KAGGLE_DATASET_ID}'...")
        api.dataset_download_files(KAGGLE_DATASET_ID, path=str(RAW_DATA_DIR), unzip=True)
        print(f"[+] Download and extraction to '{RAW_DATA_DIR}' completed!")
        return True
    except Exception as e:
        print(f"[-] Kaggle API download failed: {e}")
        return False

def download_via_kagglehub() -> bool:
    """Attempts to download dataset using official kagglehub Python library."""
    print(f"[*] Attempting to download '{KAGGLE_DATASET_ID}' via kagglehub...")
    try:
        import kagglehub
        import shutil
        cache_dir = kagglehub.dataset_download(KAGGLE_DATASET_ID)
        print(f"[+] Downloaded to cache: {cache_dir}")
        for item in Path(cache_dir).glob("*.*"):
            dest = RAW_DATA_DIR / item.name
            shutil.copy2(item, dest)
        print(f"[+] Successfully copied dataset files to '{RAW_DATA_DIR}'!")
        return True
    except Exception as e:
        print(f"[-] kagglehub download failed: {e}")
        return False

def verify_raw_files() -> bool:
    """Checks whether raw CSV and category JSON files exist in data/raw/."""
    csv_files = list(RAW_DATA_DIR.glob("*videos.csv"))
    json_files = list(RAW_DATA_DIR.glob("*category_id.json"))
    
    print("\n--- Raw Data Verification ---")
    print(f"CSV files found ({len(csv_files)}): {[f.name for f in csv_files]}")
    print(f"JSON files found ({len(json_files)}): {[f.name for f in json_files]}")
    
    if csv_files and json_files:
        print("[+] Raw data is ready for the ingestion pipeline.")
        return True
    else:
        print("[-] Missing required raw files. Please download them or run scripts/generate_sample_data.py.")
        return False

def main():
    print("=" * 60)
    print("YouTube Video Statistics - Step 0: Data Acquisition")
    print("=" * 60)
    
    # Check if raw data already exists
    if verify_raw_files():
        print("[+] Dataset already present in data/raw/. Skipping download.")
        return
        
    # Attempt download
    success = download_via_kagglehub() or download_via_kaggle_api() or download_via_kaggle_cli()
    
    if not success:
        print("\n[!] Automatic Kaggle download could not proceed.")
        print("    Instructions for manual download:")
        print("    1. Go to: https://www.kaggle.com/datasets/datasnaek/youtube-new")
        print("    2. Download the archive and extract all *.csv and *.json files into:")
        print(f"       {RAW_DATA_DIR.resolve()}")
        print("    Alternatively, generate synthetic test data using:")
        print("       python scripts/generate_sample_data.py\n")
        
    verify_raw_files()

if __name__ == "__main__":
    main()

