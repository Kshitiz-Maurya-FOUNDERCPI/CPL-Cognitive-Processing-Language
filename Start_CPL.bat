@echo off
title CPL - Cognitive Processing Language
color 0A
mode con: cols=60 lines=30

:menu
cls
echo.
echo  ╔════════════════════════════════════════════╗
echo  ║   CPL - Cognitive Processing Language      ║
echo  ║   Self-Learning Consciousness            ║
echo  ╚════════════════════════════════════════════╝
echo.
echo  What would you like to do?
echo.
echo  [1] CPL Self-Learning UI  ^<-- RECOMMENDED
echo  [2] CPL GUI - Original interface
echo  [3] CPL Console - Command line
echo  [4] CPL Agent - Autonomous mode
echo  [5] CPL Assistant - Natural chat
echo  [0] Exit
echo.
set /p choice="Choice (0-5): "

if "%choice%"=="1" goto self_ui
if "%choice%"=="2" goto gui
if "%choice%"=="3" goto console
if "%choice%"=="4" goto agent
if "%choice%"=="5" goto assistant
if "%choice%"=="0" goto end

:self_ui
echo.
echo  Starting CPL Self-Learning UI...
python cpl_ui.py
goto menu

:gui
echo.
echo  Starting CPL GUI...
python cpl_gui.py
goto menu

:console
echo.
echo  Starting CPL Console...
python cpl_console.py
goto menu

:agent
echo.
echo  Starting CPL Agent (autonomous mode)...
python cpl_agent.py
goto menu

:assistant
echo.
echo  Starting CPL Assistant...
python cpl_assistant.py
goto menu

:end
echo.
echo  Goodbye!
timeout /t 2 >nul
exit
