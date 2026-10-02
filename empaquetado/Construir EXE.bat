@echo off
title Construir SmartMud.exe
cd /d "%~dp0"

set PY=..\.venv\Scripts\python.exe
if not exist "%PY%" set PY=..\env\Scripts\python.exe
if not exist "%PY%" (
    echo [ERROR] No se encontro el entorno virtual en ..\.venv ni en ..\env
    pause
    exit /b 1
)

echo ==============================================================================
echo   [1/6] Instalando PyInstaller y el icono de bandeja en el entorno virtual...
echo ==============================================================================
"%PY%" -m pip install --upgrade pyinstaller pystray pillow
if %ERRORLEVEL% NEQ 0 goto :error

echo ==============================================================================
echo   [2/6] Verificando el proyecto con Python (base temporal, no toca sus datos)
echo ==============================================================================
"%PY%" chapala_app.py --verificar
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [DETENIDO] El proyecto tiene errores. Corrijalos antes de empaquetar.
    pause
    exit /b 1
)

echo ==============================================================================
echo   [3/6] Limpiando construcciones anteriores...
echo ==============================================================================
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo ==============================================================================
echo   [4/6] Construyendo SmartMud.exe (tarda unos minutos)...
echo ==============================================================================
"%PY%" -m PyInstaller --noconfirm chapala.spec
if %ERRORLEVEL% NEQ 0 goto :error

echo ==============================================================================
echo   [5/6] Verificando el EJECUTABLE construido...
echo ==============================================================================
rem El .exe no tiene consola: escribe el resultado en un archivo y aqui se muestra.
set VLOG=%~dp0verificacion_exe.log
if exist "%VLOG%" del "%VLOG%"
"dist\SmartMud\SmartMud.exe" --verificar --log "%VLOG%"
set RESULTADO=%ERRORLEVEL%
if exist "%VLOG%" type "%VLOG%"
if %RESULTADO% NEQ 0 (
    echo.
    echo [DETENIDO] El ejecutable no paso la verificacion. NO se genero el .zip.
    echo Envie el archivo empaquetado\verificacion_exe.log para revisarlo.
    pause
    exit /b 1
)

copy /y "LEEME_PRUEBAS.txt" "dist\SmartMud\LEEME_PRUEBAS.txt" >nul

echo ==============================================================================
echo   [6/6] Comprimiendo en dist\SmartMud_Pruebas.zip ...
echo ==============================================================================
powershell -NoProfile -Command "Compress-Archive -Path 'dist\SmartMud' -DestinationPath 'dist\SmartMud_Pruebas.zip' -Force"
if %ERRORLEVEL% NEQ 0 goto :error

echo.
echo LISTO. Entregue el archivo:  empaquetado\dist\SmartMud_Pruebas.zip
echo Para probarlo aqui mismo:     empaquetado\dist\SmartMud\SmartMud.exe
pause
exit /b 0

:error
echo.
echo [ERROR] Fallo la construccion. Revise los mensajes de arriba.
pause
exit /b 1
