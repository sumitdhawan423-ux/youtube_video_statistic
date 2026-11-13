"""
Central Configuration Module for YouTube Video Statistics Big Data Pipeline
Handles paths (HDFS vs Local fallback), Spark configurations, and pipeline constants.
"""

import os
import sys
from pathlib import Path

# Add DLL directory for PostgreSQL bundled Python on Windows
PG_PYTHON = r"C:\Program Files\PostgreSQL\18\pgAdmin 4\python"
_DLL_HANDLE = None
if os.path.exists(PG_PYTHON) and hasattr(os, "add_dll_directory"):
    try:
        _DLL_HANDLE = os.add_dll_directory(PG_PYTHON)
        import ctypes  # preload ctypes while DLL directory is active
    except Exception:
        pass

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
CLEAN_DATA_DIR = DATA_DIR / "clean"
OUTPUT_DIR = PROJECT_ROOT / "output"
CHARTS_DIR = OUTPUT_DIR / "charts"
TABLES_DIR = OUTPUT_DIR / "tables"
REPORTS_DIR = OUTPUT_DIR / "reports"

# Ensure local directories exist
for p in [RAW_DATA_DIR, CLEAN_DATA_DIR, CHARTS_DIR, TABLES_DIR, REPORTS_DIR]:
    p.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# Automatic Environment Configuration for Java and Hadoop on Windows
# -----------------------------------------------------------------------------
def get_short_path(path_str: str) -> str:
    """Returns 8.3 short path on Windows to prevent spaces from breaking batch/cmd invocations."""
    if os.name == "nt":
        try:
            import ctypes
            buf = ctypes.create_unicode_buffer(500)
            ctypes.windll.kernel32.GetShortPathNameW(str(path_str), buf, 500)
            return buf.value or str(path_str)
        except Exception:
            return str(path_str)
    return str(path_str)

# Configure PySpark worker Python
_short_py = get_short_path(sys.executable)
os.environ["PYSPARK_PYTHON"] = _short_py
os.environ["PYSPARK_DRIVER_PYTHON"] = _short_py

# Java Runtime Configuration (JDK 17 portable or JRE)
JDK17_LOCAL = PROJECT_ROOT / "jdk-17.0.12+7"
JAVA_DEFAULT = Path(r"C:\Program Files\Java\jre1.8.0_421")

if JDK17_LOCAL.exists():
    _jdk_path = get_short_path(str(JDK17_LOCAL))
    os.environ["JAVA_HOME"] = _jdk_path
    os.environ["PATH"] = str(Path(_jdk_path) / "bin") + os.pathsep + os.environ.get("PATH", "")
elif JAVA_DEFAULT.exists() and "JAVA_HOME" not in os.environ:
    _java_path = get_short_path(str(JAVA_DEFAULT))
    os.environ["JAVA_HOME"] = _java_path
    os.environ["PATH"] = str(Path(_java_path) / "bin") + os.pathsep + os.environ.get("PATH", "")

# Hadoop Winutils Configuration (winutils.exe, hadoop.dll)
HADOOP_LOCAL = PROJECT_ROOT / "hadoop"
if (HADOOP_LOCAL / "bin" / "winutils.exe").exists():
    _hadoop_path = get_short_path(str(HADOOP_LOCAL))
    os.environ["HADOOP_HOME"] = _hadoop_path
    os.environ["PATH"] = str(Path(_hadoop_path) / "bin") + os.pathsep + os.environ.get("PATH", "")

# Hadoop & HDFS Configuration
# Set USE_HDFS = True or set environment variable USE_HDFS=true to read/write from HDFS
USE_HDFS = os.getenv("USE_HDFS", "false").lower() in ("true", "1", "yes")
HDFS_NAMENODE = os.getenv("HDFS_NAMENODE", "hdfs://localhost:9000")

# HDFS Paths
HDFS_BASE_DIR = f"{HDFS_NAMENODE}/youtube"
HDFS_RAW_DIR = f"{HDFS_BASE_DIR}/raw"
HDFS_CLEAN_DIR = f"{HDFS_BASE_DIR}/clean"
HDFS_OUTPUT_DIR = f"{HDFS_BASE_DIR}/output"

# Resolved active paths based on environment
def get_path(storage_type: str) -> str:
    """Returns either local or HDFS path depending on configuration."""
    if USE_HDFS:
        mapping = {
            "raw": HDFS_RAW_DIR,
            "clean": HDFS_CLEAN_DIR,
            "output": HDFS_OUTPUT_DIR,
        }
        return mapping.get(storage_type, HDFS_BASE_DIR)
    else:
        mapping = {
            "raw": str(RAW_DATA_DIR),
            "clean": str(CLEAN_DATA_DIR),
            "output": str(TABLES_DIR),
        }
        return mapping.get(storage_type, str(DATA_DIR))

# Spark Configuration Constants
SPARK_APP_NAME = "YouTube_Statistics_BigData_Analysis"
SPARK_MASTER = os.getenv("SPARK_MASTER", "local[*]")
SPARK_DRIVER_MEMORY = os.getenv("SPARK_DRIVER_MEMORY", "4g")
SPARK_EXECUTOR_MEMORY = os.getenv("SPARK_EXECUTOR_MEMORY", "4g")

# Kaggle Dataset Identifier
KAGGLE_DATASET_ID = "datasnaek/youtube-new"

# Countries in Dataset
COUNTRY_CODES = ["US", "IN", "GB", "CA", "DE", "FR", "JP", "KR", "MX", "RU"]

# YouTube API Configuration (loaded from .env if present)
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

# Machine Learning Constants
RANDOM_SEED = 42
RF_NUM_TREES = 50
RF_MAX_DEPTH = 10
KMEANS_K = 4

