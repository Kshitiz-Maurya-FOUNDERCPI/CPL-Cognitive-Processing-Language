@echo off
title CPL Installer
color 0A

echo.
echo  ================================================
echo    CPL - Cognitive Processing Language
echo    Desktop App Installer
echo  ================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install requests numpy >nul 2>&1

REM Create icon
echo Creating icon...
python create_icon.py

REM Create launcher
echo Creating launcher...
copy Start_CPL.bat "%USERPROFILE%\Desktop\" >nul 2>&1

REM Create shortcut
echo Creating desktop shortcut...
powershell -ExecutionPolicy Bypass -File Create_Shortcut.ps1

echo.
echo  ================================================
echo    Installation Complete!
echo  ================================================
echo.
echo  CPL has been installed on your desktop:
echo    - Start_CPL.bat (launcher)
echo    - CPL.lnk (shortcut)
echo.
echo  You can also run directly:
echo    python cpl_gui.py
echo.
pause
