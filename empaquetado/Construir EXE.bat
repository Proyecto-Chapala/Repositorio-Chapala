@echo off
title Construir CHAPALA.exe (version de prueba)
cd /d "%~dp0"

set PY=..\.venv\Scripts\python.exe
if not exist "%PY%" (
    echo [ERROR] No se encontro el entorno virtual en ..\.venv
    pause
    exit /b 1
)

echo ==============================================================================
echo   [1/6] Verificando el proyecto con Python (base temporal, no toca sus datos)
echo ==============================================================================
"%PY%" chapala_app.py --verificar
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [DETENIDO] El proyecto tiene errores. Corrijalos antes de empaquetar.
    pause
    exit /b 1
)

echo ==============================================================================
echo   [2/6] Instalando PyInstaller en el entorno virtual...
echo ==============================================================================
"%PY%" -m pip install --upgrade pyinstaller
if %ERRORLEVEL% NEQ 0 goto :error

echo ==============================================================================
echo   [3/6] Limpiando construcciones anteriores...
echo ==============================================================================
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo ==============================================================================
echo   [4/6] Construyendo CHAPALA.exe (tarda unos minutos)...
echo ==============================================================================
"%PY%" -m PyInstaller --noconfirm chapala.spec
if %ERRORLEVEL% NEQ 0 goto :error

echo ==============================================================================
echo   [5/6] Verificando el EJECUTABLE construido...
echo ==============================================================================
"dist\CHAPALA\CHAPALA.exe" --verificar
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [DETENIDO] El ejecutable no paso la verificacion. NO se genero el .zip.
    echo Copie los mensajes de arriba y envielos para revisarlos.
    pause
    exit /b 1
)

copy /y "LEEME_PRUEBAS.txt" "dist\CHAPALA\LEEME_PRUEBAS.txt" >nul

echo ==============================================================================
echo   [6/6] Comprimiendo en dist\CHAPALA_Pruebas.zip ...
echo ==============================================================================
powershell -NoProfile -Command "Compress-Archive -Path 'dist\CHAPALA' -DestinationPath 'dist\CHAPALA_Pruebas.zip' -Force"
if %ERRORLEVEL% NEQ 0 goto :error

echo.
echo LISTO. Entregue el archivo:  empaquetado\dist\CHAPALA_Pruebas.zip
echo Para probarlo aqui mismo:     empaquetado\dist\CHAPALA\CHAPALA.exe
pause
exit /b 0

:error
echo.
echo [ERROR] Fallo la construccion. Revise los mensajes de arriba.
pause
exit /b 1
