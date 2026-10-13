@echo off
cd /d "%~dp0"
python -c "import PIL" >nul 2>&1
if errorlevel 1 (
    echo Installing bot dependencies...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Dependency installation failed.
        pause
        exit /b 1
    )
)
python bot.py
pause