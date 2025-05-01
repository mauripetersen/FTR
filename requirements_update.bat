@echo off
cd .venv\Scripts

echo updating requirements.txt ...

call activate.bat
call pip3 freeze > "../../requirements.txt"
call deactivate.bat

echo Done.
pause
