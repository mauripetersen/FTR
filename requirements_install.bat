@echo off
cd .venv\Scripts

echo updating requirements.txt ...
echo.

call activate.bat
call pip3 install -r "../../requirements.txt"
call deactivate.bat

echo.
echo Done.
pause
