@echo off
title CPL - Cognitive Processing Language
color 0A
mode con: cols=60 lines=30

:menu
cls
echo.
echo  ╔════════════════════════════════════════════╗
echo  ║   CPL - Cognitive Processing Language      ║
echo  ║   Artificial Generative Consciousness     ║
echo  ╚════════════════════════════════════════════╝
echo.
echo  What would you like to do?
echo.
echo  [1] CPL Assistant - Chat with CPL naturally
echo  [2] CPL GUI - Graphical interface
echo  [3] CPL Console - Command line mode
echo  [4] CPL Agent - Run autonomously
echo  [5] Install Voice Support - Enable voice commands
echo  [0] Exit
echo.
set /p choice="Choice (0-5): "

if "%choice%"=="1" goto assistant
if "%choice%"=="2" goto gui
if "%choice%"=="3" goto console
if "%choice%"=="4" goto agent
if "%choice%"=="5" goto voice_install
if "%choice%"=="0" goto end

:assistant
echo.
echo  Starting CPL Assistant...
python cpl_assistant.py
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

:voice_install
echo.
echo  Installing voice support...
pip install SpeechRecognition pyttsx3 >nul 2>&1
echo.
echo  Voice support installed! Restart CPL to use.
echo.
pause
goto menu

:end
echo.
echo  Goodbye!
timeout /t 2 >nul
exit
