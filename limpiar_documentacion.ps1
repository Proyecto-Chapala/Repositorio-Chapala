# ==============================================================================
# Limpieza de la documentacion vieja - Smart Mud (02-oct-2026)
# ------------------------------------------------------------------------------
# Todo lo que borra este script YA esta copiado dentro de docs/ :
#   docs_2/docs/*            -> docs/ (documentos 01-21 actualizados)
#   docs_2/claude/traspaso   -> docs/00_TRASPASO.md
#   docs_2/audio/*           -> docs/fuentes/audios_2026-10-02/
#   docs_2/memoria.md        -> docs/_archivo/claude/memoria_25sep.md
#   docs/ viejos (23-sep)    -> docs/_archivo/docs_23sep/
#   GUIA_DIA_OPERATIVO, etc. -> docs/manuales/
#   notas sueltas de la raiz -> docs/fuentes/notas_cliente/ y docs/_archivo/
# Los temp_*.txt y test_err.py eran salidas de busquedas y pruebas: se borran.
#
# Uso (PowerShell, en la carpeta del proyecto):
#   powershell -ExecutionPolicy Bypass -File .\limpiar_documentacion.ps1
# Despues: git add -A ; git commit -m "Documentacion reorganizada en docs/"
# ==============================================================================

$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot

$necesarios = @('docs\00_TRASPASO.md', 'docs\README.md', 'docs\22_CAMBIOS_02OCT_SMART_MUD.md',
                'docs\_archivo\docs_23sep\README.md', 'docs\fuentes\audios_2026-10-02\audio_1.txt',
                'docs\manuales\GUIA_DIA_OPERATIVO.pdf')
foreach ($n in $necesarios) {
    if (-not (Test-Path -LiteralPath $n)) {
        Write-Host "[DETENIDO] Falta $n. No se borro nada." -ForegroundColor Red
        exit 1
    }
}

$borrar = @(
    'docs_2',
    'docs\API_ENDPOINTS.md',
    'docs\ARQUITECTURA.md',
    'docs\PENDIENTES_Y_DECISIONES.md',
    'docs\GUIA_DIA_OPERATIVO.html',
    'docs\GUIA_DIA_OPERATIVO.pdf',
    'docs\MANUAL_USUARIO.html',
    'docs\convertir_a_pdf.py',
    'docs\inventario',
    'docs\reportes',
    'OBSERVACIONES DE HOY.md',
    'Lista de Posibles Bugs, cosas por revisar.md',
    'Avances del dia de hoy.txt',
    'RESUMEN_AVANCE.txt',
    'temp_cards.txt',
    'temp_mi.txt',
    'temp_rep.txt',
    'temp_spud.txt',
    'test_err.py'
)

foreach ($b in $borrar) {
    if (Test-Path -LiteralPath $b) {
        Remove-Item -LiteralPath $b -Recurse -Force
        Write-Host "Borrado: $b"
    } else {
        Write-Host "No estaba: $b" -ForegroundColor DarkGray
    }
}

Write-Host ""
Write-Host "LISTO. Toda la documentacion esta en docs\ (indice: docs\README.md)." -ForegroundColor Green
Write-Host "No se tocaron: 'Claude outputs', 'proyecto chapala - claude', 'Proyecto CHAPALA.zip' ni los *-1.py (decidir aparte)."
Write-Host "Ahora: git add -A ; git commit -m `"Documentacion reorganizada en docs/`""
