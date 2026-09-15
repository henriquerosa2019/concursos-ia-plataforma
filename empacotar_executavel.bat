@echo off
chcp 65001 >nul
title Gerador de Executável Standalone - Central de Concursos IA

cd /d "C:\PROJETOS IA\Concursos"

echo ======================================================================
echo   GERANDO EXECUTAVEL COMERCIAL STANDALONE PARA WINDOWS
echo ======================================================================
echo.
python build_standalone_exe.py

echo.
pause
