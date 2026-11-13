"""
Master Pipeline Runner for YouTube Video Statistics Analysis.
Executes all stages end-to-end:
  [Step 0] Data Download Check & Verification
  [Step 1] YouTube Data API v3 Ingestion (Optional)
  [Step 2] Processing Engine: PySpark Cluster or High-Speed Standalone Engine
  [Step 3] Analytics & MLlib Model Evaluation
  [Step 4] Matplotlib & Seaborn Visualizations (300 DPI)
  [Step 5] Big Data Performance Tuning & Benchmarks
"""

import sys
import time
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# Initialize environment configuration (Java 17, Hadoop winutils, PySpark worker Python)
from config import config

def check_pyspark_available() -> bool:
    try:
        import pyspark
        return True
    except (ImportError, Exception):
        return False

def print_banner():
    banner = """
    ========================================================================
     YOUTUBE VIDEO STATISTICS BIG DATA PIPELINE (HADOOP + APACHE SPARK)
    ========================================================================
     Storage     : Hadoop HDFS / Local Parquet
     Processing  : Apache Spark (PySpark DataFrame API + Spark SQL)
     ML Engine   : Spark MLlib (Random Forest, Linear Reg, K-Means)
     Analytics   : 8 Multidimensional Data Marts
     Visuals     : Matplotlib & Seaborn High-Resolution Plots (300 DPI)
    ========================================================================
    """
    print(banner)

def run_step(name: str, script_path: Path) -> bool:
    print("\n" + "="*70)
    print(f" STARTING: {name}")
    print(f" Script  : {script_path.name}")
    print("="*70)
    
    t0 = time.time()
    try:
        cmd = [sys.executable, str(script_path)]
        res = subprocess.run(cmd, check=True)
        dt = time.time() - t0
        print(f"[+] Completed: {name} in {dt:.2f} seconds.")
        return True
    except subprocess.CalledProcessError as e:
        dt = time.time() - t0
        print(f"[-] FAILED: {name} after {dt:.2f} seconds (Exit Code: {e.returncode}).")
        return False
    except Exception as ex:
        print(f"[-] Error executing {name}: {ex}")
        return False

def main():
    print_banner()
    total_start = time.time()
    
    has_spark = check_pyspark_available()
    if has_spark:
        print("[+] Apache PySpark runtime detected. Using Distributed Engine.")
        steps = [
            ("Step 0: Verify & Download Raw Data", PROJECT_ROOT / "scripts" / "00_download_data.py"),
            ("Step 1: Optional YouTube Data API v3 Ingestion", PROJECT_ROOT / "scripts" / "01_fetch_youtube_api.py"),
            ("Step 3: PySpark Ingest, Clean & Parquet Export", PROJECT_ROOT / "scripts" / "03_ingest_and_clean.py"),
            ("Step 4: PySpark Feature Engineering", PROJECT_ROOT / "scripts" / "04_feature_engineering.py"),
            ("Step 5: Spark SQL & Analytical Queries", PROJECT_ROOT / "scripts" / "05_spark_sql_analysis.py"),
            ("Step 6: Spark MLlib Regression & Clustering", PROJECT_ROOT / "scripts" / "06_spark_mllib.py"),
            ("Step 7: Matplotlib & Seaborn Visualizations", PROJECT_ROOT / "scripts" / "07_visualize_results.py"),
            ("Step 8: Performance Tuning & Benchmarks", PROJECT_ROOT / "scripts" / "08_benchmark_tuning.py"),
            ("Step 9: Export Frontend Data", PROJECT_ROOT / "scripts" / "export_frontend_data.py"),
        ]
    else:
        print("[*] PySpark is not installed in the local Python environment.")
        print("    Running pipeline via Standalone Engine.")
        print("    (Note: To run in clustered Hadoop/Spark, run 'docker compose up -d' in /docker)")
        steps = [
            ("Step 0: Verify & Download Raw Data", PROJECT_ROOT / "scripts" / "00_download_data.py"),
            ("Step 1: Optional YouTube Data API v3 Ingestion", PROJECT_ROOT / "scripts" / "01_fetch_youtube_api.py"),
            ("Step 2-6: Ingest, Clean, Feature Eng, Analytics & ML", PROJECT_ROOT / "scripts" / "simulate_pipeline.py"),
            ("Step 7: Matplotlib & Seaborn Visualizations", PROJECT_ROOT / "scripts" / "07_visualize_results.py"),
            ("Step 8: Performance Tuning & Benchmarks", PROJECT_ROOT / "scripts" / "08_benchmark_tuning.py"),
            ("Step 9: Export Frontend Data", PROJECT_ROOT / "scripts" / "export_frontend_data.py"),
        ]
        
    successful_steps = 0
    for name, script_path in steps:
        if not script_path.exists():
            print(f"[-] Script not found: {script_path}")
            continue
            
        success = run_step(name, script_path)
        if success:
            successful_steps += 1
        else:
            print(f"[!] Pipeline halted at '{name}'. Please resolve errors above.")
            sys.exit(1)
            
    total_time = time.time() - total_start
    print("\n" + "="*70)
    print(f" ALL PIPELINE STAGES COMPLETED SUCCESSFULLY! ({successful_steps}/{len(steps)})")
    print(f" Total Duration: {total_time:.2f} seconds")
    print(f" Visualizations: {PROJECT_ROOT / 'output' / 'charts'}")
    print(f" Analytical Tables: {PROJECT_ROOT / 'output' / 'tables'}")
    print(f" Benchmark Reports: {PROJECT_ROOT / 'output' / 'reports'}")
    print("="*70)

if __name__ == "__main__":
    main()
