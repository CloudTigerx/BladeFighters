@echo off
echo Running Modularized Puzzle Game...

set PYTHON_PATH=%LOCALAPPDATA%\Programs\Python\Python310\python.exe

if not exist "%PYTHON_PATH%" (
    echo Python is not found at expected location: %PYTHON_PATH%
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    goto :end
)

"%PYTHON_PATH%" main.py
:end
pause 