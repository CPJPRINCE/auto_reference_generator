@echo off
REM Auto Reference Generator Windows Uninstaller
REM This script removes the Auto Reference Generator from the system

setlocal enabledelayedexpansion

echo.
echo ===============================================
echo Auto Reference Generator Uninstallation
echo ===============================================
echo.

REM Define installation directory
set INSTALL_DIR=%LOCALAPPDATA%\Auto Reference Generator
set BIN_DIR=!INSTALL_DIR!\bin

REM Confirm uninstallation
echo This will remove Auto Reference Generator from:
echo !INSTALL_DIR!
echo.
set /p CONFIRM="Are you sure you want to uninstall? (Y/N): "
if /i not "!CONFIRM!"=="Y" (
    echo Uninstallation cancelled
    pause
    exit /b 0
)

REM Remove from PATH
echo Removing from PATH...
%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe -Command "$path = [Environment]::GetEnvironmentVariable('Path', 'User'); $newPath = ($path -split ';' | Where-Object { $_ -ne '%LOCALAPPDATA%\Auto Reference Generator\bin' -and $_ -ne $env:LOCALAPPDATA + '\Auto Reference Generator\bin' }) -join ';'; if ($path -ne $newPath) { [Environment]::SetEnvironmentVariable('Path', $newPath, 'User'); Write-Host 'Removed from PATH' } else { Write-Host 'Not found in PATH' }"

REM Remove installation directory
if exist "!INSTALL_DIR!" (
    echo Removing installation directory...
    rmdir /S /Q "!INSTALL_DIR!"
)

echo.
echo ===============================================
echo Uninstallation Complete!
echo ===============================================
echo.
pause
