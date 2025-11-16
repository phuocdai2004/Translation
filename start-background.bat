@echo off
REM Run server in background with no window
cd /d e:\haystack\backend
set PYTHONPATH=e:\haystack\backend

REM Create a VBScript to run without console window
echo CreateObject("WScript.Shell").Run "python -m uvicorn main:app --host 127.0.0.1 --port 8000", 0, False > run_hidden.vbs

REM Run the VBScript
cscript.exe run_hidden.vbs

REM Clean up
del run_hidden.vbs

echo Server started in background on http://127.0.0.1:8000
