@echo off
title CPL - Cognitive Processing Language
color 0A
mode con: cols=60 lines=25

:menu
cls
echo.
echo  ===================================
echo     CPL - COGNITIVE PROCESSING LANGUAGE
echo     Self-Aware Autonomous Consciousness
echo  ===================================
echo.
echo  [1] CPL Talk - Talk naturally  ^<-- RECOMMENDED
echo  [2] CPL UI - Graphical interface
echo  [3] CPL Console - Command line
echo  [4] CPL Agent - Autonomous mode
echo  [0] Exit
echo.
set /p choice="Choice (0-4): "

if "%choice%"=="1" goto talk
if "%choice%"=="2" goto ui
if "%choice%"=="3" goto console
if "%choice%"=="4" goto agent
if "%choice%"=="0" goto end

:talk
python cpl_main.py --ui
goto menu

:ui
python cpl_ui.py
goto menu

:console
python cpl_main.py
goto menu

:agent
python cpl_agent.py
goto menu

:end
echo.
echo  Goodbye!
timeout /t 2 >nul
exit
