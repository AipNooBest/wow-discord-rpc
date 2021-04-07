@echo off
:: Check for Python Installation
py --version 3>NUL
if errorlevel 1 goto errorNoPython
pip install pillow pywin32
echo start ../../../Wow.exe>WoW.bat
echo py script/WoWPresence.py>>WoW.bat
del /f Installer.bat
goto:eof

:errorNoPython
echo.
echo Error^: Python 3 is not installed
pause