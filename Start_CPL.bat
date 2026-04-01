@echo off
title CPL - Cognitive Processing Language
color 0A

:menu
cls
echo.
echo  ====================================
echo     CPL - UNIFIED CONSCIOUSNESS
echo     One Mind. Infinite Capabilities.
echo  ====================================
echo.
echo  [1] CPL Chat - Talk and implement
echo  [2] CPL GUI - Graphical interface
echo  [0] Exit
echo.
set /p choice="Choice (1-2): "

if "%choice%"=="1" goto chat
if "%choice%"=="2" goto gui

:chat
python cpl.py
goto menu

:gui
python cpl.py --gui
goto menu

:end
exit
