"""
load_via_kagglehub.py - Download and load Kaggle's "datasnaek/youtube-new" dataset.

This script uses the official kagglehub Python library to:
1. Dynamically load specific dataset files into pandas DataFrames.
2. Download and populate data/raw/ with the full real Kaggle trending data.

Usage:
  python scripts/load_via_kagglehub.py --file USvideos.csv
  python scripts/load_via_kagglehub.py --file INvideos.csv --rows 10
  python scripts/load_via_kagglehub.py --download-all
"""

import os
import sys
import argparse
from pathlib import Path

# Add project root and .venv site-packages to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
VENV_PACKAGES = PROJECT_ROOT / ".venv" / "Lib" / "site-packages"
if VENV_PACKAGES.exists() and str(VENV_PACKAGES) not in sys.path:
    sys.path.insert(0, str(VENV_PACKAGES))

# Ensure Windows finds PostgreSQL's bundled Python runtime DLLs if applicable
pg_python = r"C:\Program Files\PostgreSQL\18\pgAdmin 4\python"
if os.path.exists(pg_python) and hasattr(os, "add_dll_directory"):
    try:
        os.add_dll_directory(pg_python)
    except Exception:
        pass

import kagglehub
from kagglehub import KaggleDatasetAdapter


DATASET_HANDLE = "datasnaek/youtube-new"


def load_dataset_file(file_path: str = "USvideos.csv", nrows: int = None, **pandas_kwargs):
    """
    Load a single file from the Kaggle dataset into a pandas DataFrame.
    
    Args:
        file_path: Relative file path in dataset (e.g. 'USvideos.csv', 'INvideos.csv')
        nrows: Optional number of rows to preview
        pandas_kwargs: Additional arguments for pd.read_csv
    """
    kwargs = {"encoding_errors": "replace"}
    if nrows:
        kwargs["nrows"] = nrows
    kwargs.update(pandas_kwargs)

    print(f"\n[KaggleHub] Loading '{file_path}' from '{DATASET_HANDLE}'...")
    df = kagglehub.load_dataset(
        KaggleDatasetAdapter.PANDAS,
        DATASET_HANDLE,
        file_path,
        pandas_kwargs=kwargs
    )
    return df


def download_full_dataset(destination_dir: str = None):
    """
    Downloads the entire Kaggle dataset to the local cache and copies
    the files into destination_dir (default: data/raw/).
    """
    if destination_dir is None:
        destination_dir = PROJECT_ROOT / "data" / "raw"
    destination_dir = Path(destination_dir)
    destination_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[KaggleHub] Downloading complete dataset '{DATASET_HANDLE}'...")
    cache_path = kagglehub.dataset_download(DATASET_HANDLE)
    print(f"[KaggleHub] Cached at: {cache_path}")

    import shutil
    files = list(Path(cache_path).glob("*.*"))
    print(f"[KaggleHub] Found {len(files)} files. Copying to {destination_dir}...")
    for f in files:
        target = destination_dir / f.name
        shutil.copy2(f, target)
        size_mb = target.stat().st_size / (1024 * 1024)
        print(f"  -> Copied {f.name} ({size_mb:.2f} MB)")

    print(f"\n[KaggleHub] Complete! All files are now in {destination_dir}")
    return cache_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="KaggleHub YouTube Dataset Loader")
    parser.add_argument("--file", type=str, default="USvideos.csv", help="File to load (e.g. USvideos.csv)")
    parser.add_argument("--rows", type=int, default=5, help="Number of rows to preview (default: 5)")
    parser.add_argument("--download-all", action="store_true", help="Download all dataset files to data/raw/")
    args = parser.parse_args()

    if args.download_all:
        download_full_dataset()
    else:
        df = load_dataset_file(file_path=args.file, nrows=args.rows)
        print(f"\n[SUCCESS] Loaded {len(df)} records from {args.file}!")
        print("\nColumns:")
        print(list(df.columns))
        print("\nFirst 5 records:")
        print(df.head())

