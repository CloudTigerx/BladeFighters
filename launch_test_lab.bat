@echo off
cls
color 0A
title Blade Fighters - Test Laboratory

echo.
echo    ========================================================
echo                  BLADE FIGHTERS TEST LABORATORY
echo    ========================================================
echo.
echo    Starting Test Laboratory...
echo    Please wait while we initialize the testing environment.
echo.
echo    RECOMMENDED WORKFLOW:
echo    1. Select "Blank Scene (Recommended)"
echo    2. Press G to add Grid System
echo    3. Perfect the grid rendering
echo    4. Press P to add Piece System
echo    5. Continue building incrementally
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo    ERROR: Python is not installed or not in PATH
    echo    Please install Python and make sure it's in your PATH
    echo.
    pause
    exit /b 1
)

REM Check if pygame is available
echo    Checking dependencies...
python -c "import pygame" >nul 2>&1
if errorlevel 1 (
    echo    ERROR: pygame is not installed
    echo    Installing pygame...
    pip install pygame
    if errorlevel 1 (
        echo    ERROR: Failed to install pygame
        echo    Please install pygame manually: pip install pygame
        echo.
        pause
        exit /b 1
    )
)

REM Navigate to test laboratory directory
cd /d "%~dp0test_laboratory"
if errorlevel 1 (
    echo    ERROR: test_laboratory directory not found
    echo    Please make sure you're running this from the correct directory
    echo.
    pause
    exit /b 1
)

echo    Dependencies OK! Launching Test Laboratory...
echo.

REM Launch the test laboratory
python run_tests.py

REM Check if the program exited normally
if errorlevel 1 (
    echo.
    echo    Test Laboratory exited with an error.
) else (
    echo.
    echo    Test Laboratory closed normally.
)

echo.
echo    Thanks for using the Test Laboratory!
pause 