@echo off
echo Starting GPT Engineer GUI...
echo.

:: Set UTF-8 encoding
chcp 65001 > nul

:: Set Python environment variables for UTF-8 support
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
set PYTHONLEGACYWINDOWSSTDIO=0

:: Run the GUI
python gpt_engineer_gui.py

:: Keep window open if there's an error
if %ERRORLEVEL% neq 0 (
    echo.
    echo Error occurred. Press any key to exit...
    pause > nul
)
