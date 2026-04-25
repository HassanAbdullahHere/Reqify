@echo off
start "Reqify" cmd /k "cd /d %~dp0 && uv run main.py"