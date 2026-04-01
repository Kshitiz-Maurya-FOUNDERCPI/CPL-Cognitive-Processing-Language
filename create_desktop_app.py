"""
CPL Desktop App Builder
Creates an icon and launcher for CPL
"""

import os
import struct

def create_simple_icon():
    """Create a simple brain/mind icon for CPL"""
    # Simple 32x32 ICO file with a brain-like design
    # This is a minimal valid ICO file
    
    # ICO Header
    ico_header = struct.pack('<HHH', 0, 1, 1)  # Reserved, Type (1=ICO), Count
    
    # ICO Directory Entry (32x32, 32bpp)
    width, height = 32, 32
    bpp = 32  # bits per pixel
    
    # Create pixel data (32x32 BGRA = 4096 bytes per pixel)
    pixels = []
    for y in range(height):
        for x in range(width):
            # Create a brain-like pattern
            cx, cy = width // 2, height // 2
            dx, dy = x - cx, y - cy
            dist = (dx*dx + dy*dy) ** 0.5
            
            # Brain shape (ellipse with folds)
            in_brain = dist < 14 and abs(dx) < 12
            is_fold = in_brain and (int(dist + x*0.5) % 4 < 2)
            
            if is_fold:
                # Cyan/teal for consciousness
                pixels.extend([255, 217, 0, 255])  # BGRA
            elif in_brain:
                # Dark blue for brain
                pixels.extend([100, 50, 30, 255])  # BGRA
            else:
                # Transparent
                pixels.extend([0, 0, 0, 0])  # BGRA
    
    # AND mask (32x32 / 8 = 128 bytes, all zeros for full opacity)
    and_mask = bytes(128)
    
    pixel_data = bytes(pixels)
    bmp_size = 40 + len(pixel_data) + len(and_mask)
    
    # ICO Directory Entry
    dir_entry = struct.pack('<BBBBHHII',
        width,  # Width
        height,  # Height
        0,  # Color palette
        0,  # Reserved
        1,  # Color planes
        bpp,  # Bits per pixel
        bmp_size,  # Size of image data
        22  # Offset to image data (6 + 16)
    )
    
    # BMP Info Header (40 bytes)
    bmp_header = struct.pack('<IIIHHIIIIII',
        40,  # Header size
        width,  # Width
        height * 2,  # Height (doubled for ICO)
        1,  # Planes
        bpp,  # Bits per pixel
        0,  # Compression
        len(pixel_data) + len(and_mask),  # Image size
        0, 0,  # DPI
        0, 0  # Colors
    )
    
    # Combine all parts
    ico_data = ico_header + dir_entry + bmp_header + pixel_data + and_mask
    
    with open('cpl.ico', 'wb') as f:
        f.write(ico_data)
    
    print("Created cpl.ico")


def create_launcher():
    """Create a CPL launcher batch file"""
    launcher = '''@echo off
title CPL - Cognitive Processing Language
color 0A
echo.
echo  ███████╗ ██████╗██╗  ██╗ ██████╗ 
echo  ██╔════╝██╔════╝██║  ██║██╔═══██╗
echo  █████╗  ╚█████╗ ███████║██║   ██║
echo  ██╔══╝   ╚═══██╗██╔══██║██║   ██║
echo  ███████╗██████╔╝██║  ██║╚██████╔╝
echo  ╚══════╝╚═════╝ ╚═╝  ╚═╝ ╚═════╝ 
echo.
echo  Cognitive Processing Language
echo  Artificial Generative Consciousness
echo.
echo  Starting CPL GUI...
echo.
python cpl_gui.py
pause
'''
    
    with open('Start_CPL.bat', 'w', encoding='utf-8') as f:
        f.write(launcher)
    
    print("Created Start_CPL.bat")


def create_desktop_shortcut():
    """Create PowerShell script to create desktop shortcut"""
    script = '''# CPL Desktop Shortcut Creator
# Run this script as Administrator to create desktop shortcut

$Desktop = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = "$Desktop\\CPL.lnk"
$IconPath = "$PSScriptRoot\\cpl.ico"

# Create WScript Shell
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut($ShortcutPath)

$Shortcut.TargetPath = "$PSScriptRoot\\Start_CPL.bat"
$Shortcut.WorkingDirectory = $PSScriptRoot
$Shortcut.Description = "CPL - Cognitive Processing Language"
$Shortcut.IconLocation = "$PSScriptRoot\\cpl.ico"

$Shortcut.Save()

Write-Host "Shortcut created at: $ShortcutPath"
'''
    
    with open('Create_Shortcut.ps1', 'w', encoding='utf-8') as f:
        f.write(script)
    
    print("Created Create_Shortcut.ps1")


def create_install_script():
    """Create a full installation script"""
    install = '''@echo off
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
copy Start_CPL.bat "%USERPROFILE%\\Desktop\\" >nul 2>&1

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
'''
    
    with open('Install_CPL.bat', 'w', encoding='utf-8') as f:
        f.write(install)
    
    print("Created Install_CPL.bat")


if __name__ == '__main__':
    print("Building CPL Desktop App...")
    create_simple_icon()
    create_launcher()
    create_desktop_shortcut()
    create_install_script()
    print()
    print("Desktop app files created!")
    print("Run Install_CPL.bat to install on desktop")
