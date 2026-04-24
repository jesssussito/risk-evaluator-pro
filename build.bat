@echo off
:: build.bat — Genera el ejecutable con PyInstaller.
:: Uso: doble clic o ejecutar desde CMD/PowerShell

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo =================================================
echo   Risk Evaluator Pro -- Build
echo =================================================

:: 1. Verificar PyInstaller
where pyinstaller >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] pyinstaller no encontrado en PATH.
    echo         Instalalo con: pip install pyinstaller
    echo =================================================
    echo.
    pause
    exit /b 1
)

:: 2. Limpiar artefactos anteriores
echo.
echo [1/3] Limpiando build\ y dist\...
if exist build\ rmdir /s /q build\
if exist dist\  rmdir /s /q dist\
echo       Hecho.

:: 3. Ejecutar PyInstaller
echo.
echo [2/3] Ejecutando PyInstaller (main.spec)...
echo -------------------------------------------------
pyinstaller main.spec
if errorlevel 1 (
    echo -------------------------------------------------
    echo.
    echo [ERROR] PyInstaller fallo. Revisa los mensajes anteriores.
    echo =================================================
    echo.
    pause
    exit /b 1
)

echo -------------------------------------------------
echo.
echo [3/3] Build completado con exito.
echo.
echo   Ejecutable: dist\main.exe
echo =================================================
echo.
pause
