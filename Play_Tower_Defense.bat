@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Could not find .venv\Scripts\python.exe
    echo Make sure this launcher stays in the tower_defense folder.
    pause
    exit /b 1
)

if not exist "tower_defense.py" (
    echo Could not find tower_defense.py
    echo Make sure this launcher stays in the tower_defense folder.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" "tower_defense.py"

if errorlevel 1 (
    echo.
    echo The game closed with an error.
    pause
)
