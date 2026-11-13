@echo off
REM ==============================================================================
REM Master Pipeline Runner Script (Windows Batch)
REM ==============================================================================

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo ========================================================================
echo  YouTube Video Statistics Pipeline Runner (Windows)
echo ========================================================================

REM Add PostgreSQL embedded python to PATH if needed
set "PATH=C:\Program Files\PostgreSQL\18\pgAdmin 4\python;%PATH%"

REM Activate virtual environment if present
if exist ".venv\Scripts\activate.bat" (
    echo [*] Activating virtual environment (.venv)...
    call .venv\Scripts\activate.bat
) else if exist "venv\Scripts\activate.bat" (
    echo [*] Activating virtual environment (venv)...
    call venv\Scripts\activate.bat
)

REM Optional HDFS upload if Hadoop is configured
where hdfs >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [*] Hadoop HDFS detected. Running HDFS setup...
    call scripts\02_hdfs_setup.bat
)

REM Run master Python pipeline
python run_all.py

if %ERRORLEVEL% equ 0 (
    echo.
    echo [+] Pipeline executed successfully!
) else (
    echo.
    echo [-] Pipeline failed. Check console output above.
)

endlocal

