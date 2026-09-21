@echo off
title Sistema de Inventario Quimico - Proyecto Chapala (AOS)
cd /d "%~dp0"

echo ==============================================================================
echo       INICIANDO SISTEMA DE INVENTARIO Y REPORTES DIARIOS - AOS
echo ==============================================================================
echo.
echo [1/2] Abriendo navegador en http://127.0.0.1:8000/ ...
start "" http://127.0.0.1:8000/

echo [2/2] Levantando servidor Django con base de datos PostgreSQL...
echo.
echo Para detener el servidor presione Ctrl + C en esta ventana.
echo ==============================================================================
echo.

".\env\Scripts\python.exe" manage.py runserver 127.0.0.1:8000

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Ocurrio un problema al ejecutar el servidor.
    pause
)

