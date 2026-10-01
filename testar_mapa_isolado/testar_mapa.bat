@echo off
title Testador Isolado de Mapa Mental - Concursos IA
cls
echo ===============================================================================
echo        TESTADOR ISOLADO DE MAPA MENTAL PARA CONCURSOS (NOTEBOOKLM)
echo ===============================================================================
echo.
if "%~1"=="" (
    echo Nenhum arquivo PDF foi arrastado.
    echo.
    set /p "PDF_INPUT=Arraste um ou mais PDFs aqui ou digite o caminho: "
    setlocal enabledelayedexpansion
    set "PDF_INPUT=!PDF_INPUT:"=!"
    echo.
    python "%~dp0testar_mapa.py" "!PDF_INPUT!"
    endlocal
) else (
    python "%~dp0testar_mapa.py" %*
)
echo.
echo ===============================================================================
echo Pressione qualquer tecla para encerrar...
pause >nul
