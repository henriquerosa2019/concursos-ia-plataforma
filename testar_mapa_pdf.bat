@echo off
title Testador Isolado de Mapas Mentais - Concursos IA
cls
echo ===============================================================================
echo        TESTADOR ISOLADO DE MAPA MENTAL PARA CONCURSOS (NOTEBOOKLM)
echo ===============================================================================
echo.
if "%~1"=="" (
    echo [Instrucao]: Voce pode arrastar um ou varios PDFs sobre este arquivo .bat
    echo              ou digitar/colar o caminho completo do PDF abaixo.
    echo.
    set /p "PDF_INPUT=Arraste o arquivo PDF aqui ou cole o caminho: "
    setlocal enabledelayedexpansion
    set "PDF_INPUT=!PDF_INPUT:"=!"
    echo.
    echo Processando...
    echo.
    python "%~dp0testar_mapa_isolado\testar_mapa.py" "!PDF_INPUT!"
    endlocal
) else (
    echo Processando arquivos recebidos...
    echo.
    python "%~dp0testar_mapa_isolado\testar_mapa.py" %*
)
echo.
echo ===============================================================================
echo Processamento finalizado! Os mapas foram abertos no seu navegador.
echo ===============================================================================
pause
