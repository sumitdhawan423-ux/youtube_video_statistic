@echo off
REM ==============================================================================
REM Step 2: Hadoop HDFS Setup and Raw Data Ingestion (Windows Batch)
REM Creates directories on HDFS and uploads raw CSVs and Category JSON files.
REM ==============================================================================

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..
set RAW_DATA_DIR=%PROJECT_ROOT%\data\raw

set HDFS_BASE=/youtube
set HDFS_RAW=%HDFS_BASE%/raw
set HDFS_CLEAN=%HDFS_BASE%/clean
set HDFS_OUTPUT=%HDFS_BASE%/output

echo =================================================================
echo  YouTube Big Data Pipeline - Step 2: HDFS Setup & Upload (Windows)
echo =================================================================

where hdfs >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [!] 'hdfs' command not found on PATH.
    echo     PySpark will read directly from local files: %RAW_DATA_DIR%
    echo     If using Hadoop, start HDFS and add Hadoop bin to PATH.
    goto :end
)

echo [*] Creating HDFS directories...
hdfs dfs -mkdir -p %HDFS_RAW%
hdfs dfs -mkdir -p %HDFS_CLEAN%
hdfs dfs -mkdir -p %HDFS_OUTPUT%

echo [*] Uploading raw files from %RAW_DATA_DIR% to HDFS %HDFS_RAW%...
hdfs dfs -put -f "%RAW_DATA_DIR%\*.csv" %HDFS_RAW%/
hdfs dfs -put -f "%RAW_DATA_DIR%\*.json" %HDFS_RAW%/

echo [+] Upload complete! Listing HDFS %HDFS_RAW%:
hdfs dfs -ls %HDFS_RAW%

:end
endlocal

