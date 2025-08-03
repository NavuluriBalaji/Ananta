@echo off
REM Windows Batch Script to Run GPT Engineer Safely
REM This script sets up proper encoding and runs GPT Engineer

REM Set UTF-8 encoding
chcp 65001 > nul

REM Set Python environment variables
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
set PYTHONLEGACYWINDOWSSTDIO=0

REM Set model to avoid gRPC issues (use OpenAI instead of Gemini)
set MODEL_NAME=gemini-2.0-flash

REM Load environment variables if .env exists
if exist .env (
    for /f "usebackq tokens=1,2 delims==" %%i in (.env) do (
        if not "%%i"=="" if not "%%j"=="" (
            set %%i=%%j
        )
    )
)

REM Run GPT Engineer with the provided arguments
if "%1"=="" (
    echo Usage: run_safe.bat ^<project_path^> [additional_arguments]
    echo Example: run_safe.bat projects\my-project
    pause
    exit /b 1
)

echo Running GPT Engineer with UTF-8 encoding...
echo Project path: %1

REM Run with OpenAI model to avoid gRPC issues
python -m gpt_engineer.applications.cli.main %1 --model gemini-2.0-flash %2 %3 %4 %5 %6 %7 %8 %9

pause
