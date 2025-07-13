@echo off
title BladeFighters - Setup and Run
color 0B

echo.
echo ==========================================
echo    BladeFighters - Setup and Run
echo    Modular Architecture Version (90%%)
echo ==========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=python
    goto :check_pygame
)

python3 --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=python3
    goto :check_pygame
)

py --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=py
    goto :check_pygame
)

echo [ERROR] Python not found!
echo.
echo Please install Python 3.8+ from https://python.org
echo Make sure to check "Add Python to PATH" during installation
echo.
pause
exit /b 1

:check_pygame
echo [INFO] Found Python: %PYTHON_CMD%
echo [INFO] Checking for pygame...

%PYTHON_CMD% -c "import pygame" >nul 2>&1
if %errorlevel% == 0 (
    echo [INFO] Pygame already installed
    goto :run_game
)

echo [WARN] Pygame not found. Installing...
echo.
%PYTHON_CMD% -m pip install pygame
if %errorlevel% == 0 (
    echo [INFO] Pygame installed successfully!
    echo.
) else (
    echo [ERROR] Failed to install pygame
    echo.
    echo Try running as administrator or manually install with:
    echo %PYTHON_CMD% -m pip install pygame
    echo.
    pause
    exit /b 1
)

:run_game
echo [INFO] Starting BladeFighters...
echo.
echo Controls:
echo   Arrow Keys: Move pieces
echo   Z/X: Rotate pieces  
echo   Space: Drop pieces
echo   ESC: Back to menu
echo.
echo Enjoy the modular architecture! :)
echo.
%PYTHON_CMD% main.py

if %errorlevel% == 0 (
    echo.
    echo [INFO] Game ended normally
) else (
    echo.
    echo [ERROR] Game encountered an error (exit code: %errorlevel%)
    echo Check the output above for details
)

echo.
echo Thanks for playing BladeFighters!
echo.
pause 