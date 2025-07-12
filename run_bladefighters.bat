@echo off
title BladeFighters - Puzzle Fighting Game
color 0A

echo.
echo ==========================================
echo    BladeFighters - Puzzle Fighting Game
echo    Modular Architecture Version (90%%)
echo ==========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo [INFO] Python found, starting game...
    echo.
    python main.py
    goto :end
)

:: Try python3 if python didn't work
python3 --version >nul 2>&1
if %errorlevel% == 0 (
    echo [INFO] Python3 found, starting game...
    echo.
    python3 main.py
    goto :end
)

:: Try py launcher if neither worked
py --version >nul 2>&1
if %errorlevel% == 0 (
    echo [INFO] Python launcher found, starting game...
    echo.
    py main.py
    goto :end
)

:: If no Python found
echo [ERROR] Python not found!
echo.
echo Please install Python 3.8+ from https://python.org
echo Make sure to check "Add Python to PATH" during installation
echo.
echo Required packages:
echo   - pygame
echo.
echo After installing Python, run:
echo   pip install pygame
echo.
pause
goto :end

:end
echo.
echo Game ended. Thanks for playing BladeFighters!
echo.
pause 