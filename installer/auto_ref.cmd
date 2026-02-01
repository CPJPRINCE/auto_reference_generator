@echo off
REM Auto Reference Generator Wrapper Script
REM This script sets up the environment and runs the auto_ref executable

setlocal enabledelayedexpansion

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"

REM Run the executable with all passed arguments
"%SCRIPT_DIR%auto_ref.exe" %*

REM Exit with the same code as the executable
exit /b %errorlevel%
