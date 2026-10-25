@echo off
"%~dp0.venv\Scripts\python.exe" -X utf8 "%~dp0scripts\content_editor.py"
if errorlevel 1 pause
